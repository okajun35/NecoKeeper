/**
 * NecoKeeper Service Worker
 *
 * PWA機能を提供するService Worker。
 * オフラインキャッシュ、バックグラウンド同期を実装。
 */

const CACHE_VERSION = 'necokeeper-v1';
const CACHE_NAMES = {
    static: `${CACHE_VERSION}-static`,
    dynamic: `${CACHE_VERSION}-dynamic`,
    api: `${CACHE_VERSION}-api`,
};

// キャッシュするリソース
const STATIC_RESOURCES = [
    '/public/care-form',
    '/static/manifest.json',
    'https://cdn.tailwindcss.com',
];

// インストール時の処理
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');

    event.waitUntil(
        caches.open(CACHE_NAMES.static)
            .then((cache) => {
                console.log('[SW] Caching static resources');
                return cache.addAll(STATIC_RESOURCES);
            })
            .then(() => {
                console.log('[SW] Installation complete');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('[SW] Installation failed:', error);
            })
    );
});

// アクティベーション時の処理
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');

    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                // 古いキャッシュを削除
                return Promise.all(
                    cacheNames
                        .filter((cacheName) => {
                            return cacheName.startsWith('necokeeper-') &&
                                   !Object.values(CACHE_NAMES).includes(cacheName);
                        })
                        .map((cacheName) => {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        })
                );
            })
            .then(() => {
                console.log('[SW] Activation complete');
                return self.clients.claim();
            })
    );
});

// フェッチ時の処理
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // API リクエストの処理（Network First戦略）
    if (url.pathname.startsWith('/api/v1/public/')) {
        event.respondWith(
            networkFirstStrategy(request, CACHE_NAMES.api)
        );
        return;
    }

    // 静的リソースの処理（Cache First戦略）
    if (request.method === 'GET') {
        event.respondWith(
            cacheFirstStrategy(request, CACHE_NAMES.dynamic)
        );
        return;
    }

    // POST リクエストなどはネットワークのみ
    event.respondWith(fetch(request));
});

/**
 * Cache First戦略
 * キャッシュを優先し、なければネットワークから取得
 */
async function cacheFirstStrategy(request, cacheName) {
    try {
        // キャッシュを確認
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        // ネットワークから取得
        const networkResponse = await fetch(request);

        // 成功したレスポンスをキャッシュ
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.error('[SW] Cache First failed:', error);

        // オフライン時のフォールバック
        if (request.destination === 'document') {
            const cache = await caches.open(CACHE_NAMES.static);
            return cache.match('/public/care-form');
        }

        throw error;
    }
}

/**
 * Network First戦略
 * ネットワークを優先し、失敗したらキャッシュから取得
 */
async function networkFirstStrategy(request, cacheName) {
    try {
        // ネットワークから取得を試みる
        const networkResponse = await fetch(request);

        // 成功したレスポンスをキャッシュ
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.log('[SW] Network failed, trying cache:', request.url);

        // キャッシュから取得
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        throw error;
    }
}

// バックグラウンド同期（オフライン時のPOSTリクエスト保存）
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync:', event.tag);

    if (event.tag === 'sync-care-logs') {
        event.waitUntil(syncCareLog());
    }
});

/**
 * 保存された世話記録を同期
 */
async function syncCareLogs() {
    try {
        // IndexedDBから未送信の記録を取得
        const db = await openDatabase();
        const pendingLogs = await getPendingLogs(db);

        console.log('[SW] Syncing', pendingLogs.length, 'care logs');

        // 各記録を送信
        for (const log of pendingLogs) {
            try {
                const response = await fetch('/api/v1/public/care-logs', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(log.data),
                });

                if (response.ok) {
                    // 送信成功したら削除
                    await deletePendingLog(db, log.id);
                    console.log('[SW] Synced log:', log.id);
                }
            } catch (error) {
                console.error('[SW] Failed to sync log:', log.id, error);
            }
        }

        console.log('[SW] Sync complete');
    } catch (error) {
        console.error('[SW] Sync failed:', error);
        throw error;
    }
}

/**
 * IndexedDBを開く
 */
function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('NecoKeeperDB', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('pendingLogs')) {
                db.createObjectStore('pendingLogs', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

/**
 * 未送信の記録を取得
 */
function getPendingLogs(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['pendingLogs'], 'readonly');
        const store = transaction.objectStore('pendingLogs');
        const request = store.getAll();

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

/**
 * 送信済みの記録を削除
 */
function deletePendingLog(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['pendingLogs'], 'readwrite');
        const store = transaction.objectStore('pendingLogs');
        const request = store.delete(id);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}

console.log('[SW] Service Worker loaded');
