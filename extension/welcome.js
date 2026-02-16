/**
 * FTUX welcome page (UX Spec 5.1). Uses i18n when available.
 */
(function () {
  const isVi = typeof chrome !== 'undefined' && chrome.i18n && chrome.i18n.getUILanguage && chrome.i18n.getUILanguage().startsWith('vi');
  const t = function (key) {
    if (typeof chrome !== 'undefined' && chrome.i18n) return chrome.i18n.getMessage(key) || key;
    return key;
  };

  document.getElementById('screen1').textContent = t('ftux_screen1');
  document.getElementById('screen2').textContent = t('ftux_screen2');
  document.getElementById('screen3').textContent = t('ftux_screen3');
  const cta = document.getElementById('cta');
  cta.textContent = isVi ? 'Bắt đầu dùng Loma' : 'Get started with Loma';
  cta.addEventListener('click', function (e) {
    e.preventDefault();
    if (typeof chrome !== 'undefined' && chrome.tabs) chrome.tabs.getCurrent((tab) => { if (tab && tab.id) chrome.tabs.remove(tab.id); });
    else window.close();
  });
})();
