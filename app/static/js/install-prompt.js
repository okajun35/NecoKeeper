/**
 * NecoKeeper PWAインストールプロンプト
 *
 * ホーム画面に追加するためのプロンプトを表示
 */

class InstallPromptManager {
  constructor() {
    this.deferredPrompt = null;
    this.init();
  }

  /**
   * 初期化
   */
  init() {
    // インストールプロンプトイベントをキャプチャ
    window.addEventListener('beforeinstallprompt', e => {
      console.log('[Install] beforeinstallprompt event fired');

      // デフォルトのプロンプトを抑制
      e.preventDefault();

      // イベントを保存
      this.deferredPrompt = e;

      // カスタムプロンプトを表示
      this.showInstallPrompt();
    });

    // インストール完了時
    window.addEventListener('appinstalled', () => {
      console.log('[Install] PWA installed');
      this.deferredPrompt = null;
      this.hideInstallPrompt();

      // インストール済みフラグを保存
      localStorage.setItem('pwa-installed', 'true');
    });

    // 既にインストール済みかチェック
    if (this.isInstalled()) {
      console.log('[Install] Already installed');
      return;
    }

    // iOS Safari用の表示
    if (this.isIOS() && !this.isInStandaloneMode()) {
      this.showIOSInstallPrompt();
    }
  }

  /**
   * インストールプロンプトを表示
   */
  showInstallPrompt() {
    // 既に表示済みかチェック
    if (localStorage.getItem('install-prompt-dismissed') === 'true') {
      return;
    }

    const promptHTML = `
            <div id="installPrompt" class="fixed top-4 left-4 right-4 bg-brand-primary text-white rounded-lg shadow-lg p-4 z-50 animate-slide-down">
                <div class="flex items-start gap-3">
                    <div class="flex-shrink-0 text-2xl">
                        📱
                    </div>
                    <div class="flex-1">
                        <h3 class="font-bold mb-1">ホーム画面に追加</h3>
                        <p class="text-sm text-white mb-3">
                            NecoKeeperをホーム画面に追加すると、アプリのように素早くアクセスできます
                        </p>
                        <div class="flex gap-2">
                            <button id="installBtn" class="px-4 py-2 bg-white text-brand-primary rounded-lg font-medium text-sm hover:bg-brand-primary-light transition-colors">
                                追加する
                            </button>
                            <button id="dismissBtn" class="px-4 py-2 bg-brand-primary-dark text-white rounded-lg font-medium text-sm hover:opacity-90 transition-colors">
                                後で
                            </button>
                        </div>
                    </div>
                    <button id="closePromptBtn" class="flex-shrink-0 text-brand-primary-light hover:text-white">
                        ✕
                    </button>
                </div>
            </div>
        `;

    document.body.insertAdjacentHTML('afterbegin', promptHTML);

    // イベントリスナーを設定
    document.getElementById('installBtn').addEventListener('click', () => {
      this.install();
    });

    document.getElementById('dismissBtn').addEventListener('click', () => {
      this.dismissPrompt();
    });

    document.getElementById('closePromptBtn').addEventListener('click', () => {
      this.dismissPrompt();
    });
  }

  /**
   * iOS用のインストールプロンプトを表示
   */
  showIOSInstallPrompt() {
    // 既に表示済みかチェック
    if (localStorage.getItem('ios-install-prompt-dismissed') === 'true') {
      return;
    }

    const promptHTML = `
            <div id="iosInstallPrompt" class="fixed top-4 left-4 right-4 bg-brand-primary text-white rounded-lg shadow-lg p-4 z-50">
                <div class="flex items-start gap-3">
                    <div class="flex-shrink-0 text-2xl">
                        📱
                    </div>
                    <div class="flex-1">
                        <h3 class="font-bold mb-1">ホーム画面に追加</h3>
                        <p class="text-sm text-white mb-2">
                            このアプリをホーム画面に追加できます：
                        </p>
                        <ol class="text-sm text-white space-y-1 mb-3">
                            <li>1. 画面下部の <span class="inline-block px-2 py-1 bg-brand-primary-dark rounded">共有</span> ボタンをタップ</li>
                            <li>2. <span class="font-semibold">「ホーム画面に追加」</span> を選択</li>
                        </ol>
                        <button id="dismissIOSBtn" class="px-4 py-2 bg-brand-primary-dark text-white rounded-lg font-medium text-sm hover:opacity-90 transition-colors">
                            閉じる
                        </button>
                    </div>
                    <button id="closeIOSPromptBtn" class="flex-shrink-0 text-brand-primary-light hover:text-white">
                        ✕
                    </button>
                </div>
            </div>
        `;

    document.body.insertAdjacentHTML('afterbegin', promptHTML);

    document.getElementById('dismissIOSBtn').addEventListener('click', () => {
      this.dismissIOSPrompt();
    });

    document.getElementById('closeIOSPromptBtn').addEventListener('click', () => {
      this.dismissIOSPrompt();
    });
  }

  /**
   * インストールを実行
   */
  async install() {
    if (!this.deferredPrompt) {
      console.log('[Install] No deferred prompt available');
      return;
    }

    // プロンプトを表示
    this.deferredPrompt.prompt();

    // ユーザーの選択を待つ
    const { outcome } = await this.deferredPrompt.userChoice;
    console.log('[Install] User choice:', outcome);

    if (outcome === 'accepted') {
      console.log('[Install] User accepted');
    } else {
      console.log('[Install] User dismissed');
    }

    // プロンプトを非表示
    this.hideInstallPrompt();
    this.deferredPrompt = null;
  }

  /**
   * プロンプトを閉じる
   */
  dismissPrompt() {
    this.hideInstallPrompt();
    localStorage.setItem('install-prompt-dismissed', 'true');
  }

  /**
   * iOSプロンプトを閉じる
   */
  dismissIOSPrompt() {
    const prompt = document.getElementById('iosInstallPrompt');
    if (prompt) {
      prompt.remove();
    }
    localStorage.setItem('ios-install-prompt-dismissed', 'true');
  }

  /**
   * プロンプトを非表示
   */
  hideInstallPrompt() {
    const prompt = document.getElementById('installPrompt');
    if (prompt) {
      prompt.remove();
    }
  }

  /**
   * iOS Safariかチェック
   */
  isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  }

  /**
   * スタンドアロンモードかチェック
   */
  isInStandaloneMode() {
    return 'standalone' in window.navigator && window.navigator.standalone;
  }

  /**
   * インストール済みかチェック
   */
  isInstalled() {
    // スタンドアロンモードで実行中
    if (this.isInStandaloneMode()) {
      return true;
    }

    // display-mode: standalone
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return true;
    }

    // ローカルストレージのフラグ
    if (localStorage.getItem('pwa-installed') === 'true') {
      return true;
    }

    return false;
  }
}

// グローバルインスタンス
window.installPromptManager = new InstallPromptManager();
