/**
 * Popup — Vietnamese-first: balance (stub), rewrites today/month, per-site toggle, UI language.
 */
(function () {
  const t = (key) => chrome.i18n.getMessage(key) || key;

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function applyLocale() {
    setText('title', t('ext_name'));
    setText('lbl-balance', t('popup_balance'));
    setText('lbl-today', t('popup_rewrites_today'));
    setText('lbl-month', t('popup_rewrites_month'));
    setText('lbl-site', t('popup_site_toggle'));
    setText('lbl-lang', t('popup_lang'));
    setText('lbl-api', t('popup_api'));
  }

  applyLocale();

  chrome.storage.local.get(['loma_api_base'], (data) => {
    setText('api-base', data.loma_api_base || 'http://localhost:3000');
  });

  chrome.runtime.sendMessage({ type: 'GET_STATS' }, (res) => {
    if (res) {
      setText('rewrites-today', String(res.rewrites_today || 0));
      setText('rewrites-month', String(res.rewrites_month || 0));
    }
  });

  setText('balance', '5/5 ngày'); // Stub: free tier 5 per day

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const url = tabs[0] && tabs[0].url;
    const host = url ? new URL(url).hostname : '';
    chrome.runtime.sendMessage({ type: 'GET_SITE_ENABLED', host }, (res) => {
      const toggle = document.getElementById('site-toggle');
      if (toggle) {
        const on = res && res.enabled !== false;
        toggle.classList.toggle('on', on);
        toggle.setAttribute('aria-checked', on);
        toggle.addEventListener('click', () => {
          const next = !toggle.classList.contains('on');
          chrome.runtime.sendMessage({ type: 'SET_SITE_ENABLED', host, enabled: next }, () => {
            toggle.classList.toggle('on', next);
            toggle.setAttribute('aria-checked', next);
          });
        });
      }
    });
  });

  chrome.runtime.sendMessage({ type: 'GET_UI_LANG' }, (res) => {
    const sel = document.getElementById('lang-select');
    if (sel && res && res.lang) sel.value = res.lang;
  });

  document.getElementById('lang-select').addEventListener('change', (e) => {
    const lang = e.target.value;
    chrome.runtime.sendMessage({ type: 'SET_UI_LANG', lang }, () => {
      applyLocale();
    });
  });
})();
