/**
 * モバイルメニュー JavaScript
 * Context7参照: /websites/v3_tailwindcss (Benchmark Score: 96.5)
 */

document.addEventListener('DOMContentLoaded', () => {
  const menuButton = document.getElementById('mobile-menu-button');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('mobile-overlay');

  if (!menuButton || !sidebar || !overlay) return;

  // メニューを開く
  function openMenu() {
    sidebar.classList.remove('-translate-x-full');
    overlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // スクロール防止
  }

  // メニューを閉じる
  function closeMenu() {
    sidebar.classList.add('-translate-x-full');
    overlay.classList.add('hidden');
    document.body.style.overflow = ''; // スクロール復元
  }

  // メニューボタンクリック
  menuButton.addEventListener('click', () => {
    if (sidebar.classList.contains('-translate-x-full')) {
      openMenu();
    } else {
      closeMenu();
    }
  });

  // オーバーレイクリック
  overlay.addEventListener('click', closeMenu);

  // ナビゲーションリンククリック時にメニューを閉じる（モバイルのみ）
  const navLinks = sidebar.querySelectorAll('a');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth < 1024) {
        // lg breakpoint未満
        closeMenu();
      }
    });
  });

  // ウィンドウリサイズ時の処理
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (window.innerWidth >= 1024) {
        // lg breakpoint以上ではオーバーレイを非表示
        overlay.classList.add('hidden');
        document.body.style.overflow = '';
      }
    }, 250);
  });
});
