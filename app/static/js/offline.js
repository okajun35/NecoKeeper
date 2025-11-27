/**
 * NecoKeeper Offline機能
 *
 * IndexedDBを使用したオフライン保存と同期機能
 */

const getOfflineBody = () => (typeof document !== 'undefined' ? document.body : null);
const isOfflineKiroweenMode = () => Boolean(getOfflineBody()?.classList.contains('kiroween-mode'));
const renderOfflineTemplate = (template, options = {}) => {
  if (typeof template !== 'string') return template;
  if (!template.includes('{{')) return template;
  return template.replace(/{{(\w+)}}/g, (_, key) => options[key] ?? '');
};
const OFFLINE_FALLBACKS = {
  statusOnline: {
    en: '✓ Online',
    ja: '✓ オンライン',
  },
  statusOffline: {
    en: '⚠ Offline (entries sync automatically)',
    ja: '⚠ オフライン（記録は一時保存されます）',
  },
  syncInProgress: {
    en: '🔄 Syncing... ({{count}} entries)',
    ja: '🔄 同期中... ({{count}}件)',
  },
  syncComplete: {
    en: '✓ Sync complete ({{count}} entries)',
    ja: '✓ 同期完了 ({{count}}件)',
  },
  syncError: {
    en: '✗ Sync error',
    ja: '✗ 同期エラー',
  },
};

const getOfflineFallback = key => {
  const entry = OFFLINE_FALLBACKS[key];
  if (!entry) return '';
  return isOfflineKiroweenMode() ? entry.en : entry.ja;
};

class OfflineManager {
  constructor() {
    this.dbName = 'NecoKeeperDB';
    this.dbVersion = 1;
    this.db = null;
    this.isOnline = navigator.onLine;
    this.syncStatusInfo = { status: null, count: 0, failCount: 0 };

    this.init();
    window.addEventListener('languageChanged', () => {
      this.updateConnectionStatus(this.isOnline);
      this.redrawSyncStatus();
    });
  }

  /**
   * 初期化
   */
  async init() {
    try {
      this.db = await this.openDatabase();
      this.setupOnlineListener();
      console.log('[Offline] Manager initialized');
    } catch (error) {
      console.error('[Offline] Initialization failed:', error);
    }
  }

  /**
   * IndexedDBを開く
   */
  openDatabase() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => {
        console.error('[Offline] Database error:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        console.log('[Offline] Database opened');
        resolve(request.result);
      };

      request.onupgradeneeded = event => {
        const db = event.target.result;

        // pendingLogsストアを作成
        if (!db.objectStoreNames.contains('pendingLogs')) {
          const store = db.createObjectStore('pendingLogs', {
            keyPath: 'id',
            autoIncrement: true,
          });
          store.createIndex('timestamp', 'timestamp', { unique: false });
          store.createIndex('synced', 'synced', { unique: false });
          console.log('[Offline] Created pendingLogs store');
        }
      };
    });
  }

  /**
   * オンライン/オフライン状態の監視
   */
  setupOnlineListener() {
    window.addEventListener('online', () => {
      console.log('[Offline] Back online');
      this.isOnline = true;
      this.updateConnectionStatus(true);
      this.syncPendingLogs();
    });

    window.addEventListener('offline', () => {
      console.log('[Offline] Gone offline');
      this.isOnline = false;
      this.updateConnectionStatus(false);
    });

    // 初期状態を表示
    this.updateConnectionStatus(this.isOnline);
  }

  /**
   * 接続状態の表示を更新
   */
  updateConnectionStatus(isOnline) {
    const statusElement = document.getElementById('connectionStatus');
    if (!statusElement) return;

    if (isOnline) {
      statusElement.innerHTML = `
                <div class="bg-green-50 border border-green-200 text-green-700 px-4 py-2 rounded-lg text-sm">
                    ${this.translate('status_online', getOfflineFallback('statusOnline'))}
                </div>
            `;
    } else {
      statusElement.innerHTML = `
                <div class="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-2 rounded-lg text-sm">
                    ${this.translate('status_offline', getOfflineFallback('statusOffline'))}
                </div>
            `;
    }
  }

  /**
   * 世話記録を保存（オンライン/オフライン対応）
   */
  async saveCareLog(careLogData) {
    if (this.isOnline) {
      // オンライン: 直接APIに送信
      try {
        const response = await fetch('/api/v1/public/care-logs', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(careLogData),
        });

        if (!response.ok) {
          const message = await this.extractErrorMessage(response);
          const error = new Error(message);
          error.status = response.status;
          error.isClientError = response.status >= 400 && response.status < 500;
          throw error;
        }

        return { success: true, online: true };
      } catch (error) {
        if (error?.isClientError) {
          // バリデーションエラーなどはそのまま呼び出し元へ
          throw error;
        }
        // オンラインだが通信エラー → オフライン保存にフォールバック
        console.warn('[Offline] Online save failed, falling back to offline:', error);
        return await this.saveToIndexedDB(careLogData);
      }
    } else {
      // オフライン: IndexedDBに保存
      return await this.saveToIndexedDB(careLogData);
    }
  }

  /**
   * IndexedDBに保存
   */
  async saveToIndexedDB(careLogData) {
    try {
      const transaction = this.db.transaction(['pendingLogs'], 'readwrite');
      const store = transaction.objectStore('pendingLogs');

      const record = {
        data: careLogData,
        timestamp: new Date().toISOString(),
        synced: false,
      };

      await new Promise((resolve, reject) => {
        const request = store.add(record);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });

      console.log('[Offline] Saved to IndexedDB');

      // バックグラウンド同期を登録
      if ('serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
        const registration = await navigator.serviceWorker.ready;
        await registration.sync.register('sync-care-logs');
        console.log('[Offline] Background sync registered');
      }

      return { success: true, online: false };
    } catch (error) {
      console.error('[Offline] Failed to save to IndexedDB:', error);
      throw error;
    }
  }

  /**
   * 未送信の記録を同期
   */
  async syncPendingLogs() {
    try {
      const pendingLogs = await this.getPendingLogs();

      if (pendingLogs.length === 0) {
        console.log('[Offline] No pending logs to sync');
        return;
      }

      console.log(`[Offline] Syncing ${pendingLogs.length} pending logs`);
      this.updateSyncStatus('syncing', pendingLogs.length);

      let successCount = 0;
      let failCount = 0;

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
            await this.deletePendingLog(log.id);
            successCount++;
            console.log(`[Offline] Synced log ${log.id}`);
          } else {
            failCount++;
            const message = await this.extractErrorMessage(response);
            console.error(`[Offline] Failed to sync log ${log.id}:`, message);
          }
        } catch (error) {
          failCount++;
          console.error(`[Offline] Error syncing log ${log.id}:`, error);
        }
      }

      console.log(`[Offline] Sync complete: ${successCount} success, ${failCount} failed`);
      this.updateSyncStatus('complete', successCount, failCount);
    } catch (error) {
      console.error('[Offline] Sync failed:', error);
      this.updateSyncStatus('error');
    }
  }

  /**
   * 同期状態の表示を更新
   */
  updateSyncStatus(status, count = 0, failCount = 0) {
    const statusElement = document.getElementById('syncStatus');
    if (!statusElement) return;

    this.syncStatusInfo = { status, count, failCount };

    switch (status) {
      case 'syncing':
        statusElement.innerHTML = `
                    <div class="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-2 rounded-lg text-sm">
                        ${this.translate('sync_in_progress', getOfflineFallback('syncInProgress'), { count })}
                    </div>
                `;
        break;
      case 'complete':
        statusElement.innerHTML = `
                    <div class="bg-green-50 border border-green-200 text-green-700 px-4 py-2 rounded-lg text-sm">
                        ${this.translate('sync_complete', getOfflineFallback('syncComplete'), { count })}
                    </div>
                `;
        setTimeout(() => {
          statusElement.innerHTML = '';
        }, 3000);
        break;
      case 'error':
        statusElement.innerHTML = `
                    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">
                        ${this.translate('sync_error', getOfflineFallback('syncError'))}
                    </div>
                `;
        break;
    }
  }

  /**
   * 現在の同期状態表示を再描画
   */
  redrawSyncStatus() {
    if (!this.syncStatusInfo.status) return;
    const { status, count, failCount } = this.syncStatusInfo;
    this.updateSyncStatus(status, count, failCount);
  }

  /**
   * 未送信の記録を取得
   */
  async getPendingLogs() {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['pendingLogs'], 'readonly');
      const store = transaction.objectStore('pendingLogs');
      const index = store.index('synced');
      const request = index.getAll(false);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 送信済みの記録を削除
   */
  async deletePendingLog(id) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['pendingLogs'], 'readwrite');
      const store = transaction.objectStore('pendingLogs');
      const request = store.delete(id);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 未送信の記録数を取得
   */
  async getPendingCount() {
    const logs = await this.getPendingLogs();
    return logs.length;
  }

  async extractErrorMessage(response) {
    try {
      const data = await response.clone().json();
      if (Array.isArray(data?.detail) && data.detail.length > 0) {
        const first = data.detail[0];
        if (typeof first === 'string') {
          return first;
        }
        if (first?.msg) {
          return first.msg;
        }
      }
      if (data?.detail) {
        if (typeof data.detail === 'string') {
          return data.detail;
        }
        return JSON.stringify(data.detail);
      }
    } catch (error) {
      console.warn('[Offline] Failed to parse error response', error);
    }
    return `API request failed (${response.status})`;
  }

  translate(key, fallback, options = {}) {
    const namespacedKey = `care:${key}`;
    const shouldForceFallback =
      isOfflineKiroweenMode() && typeof fallback === 'string' && fallback.length > 0;

    if (!shouldForceFallback && window.i18n && typeof window.i18n.t === 'function') {
      const translation = window.i18n.t(namespacedKey, options);
      if (translation && translation !== namespacedKey) {
        return translation;
      }
    }
    if (typeof fallback === 'string') {
      return renderOfflineTemplate(fallback, options) || key;
    }
    return fallback ?? key;
  }
}

// グローバルインスタンス
window.offlineManager = new OfflineManager();
