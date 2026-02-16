/**
 * Popup — Vietnamese-first: auth status, balance, rewrites today/month,
 * per-site toggle, UI language, keyboard shortcut hint.
 */
(function () {
  const t = (key) => chrome.i18n.getMessage(key) || key;

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function applyLocale() {
    setText('title', t('ext_name'));
    setText('lbl-today', t('popup_rewrites_today'));
    setText('lbl-month', t('popup_rewrites_month'));
    setText('lbl-site', t('popup_site_toggle'));
    setText('lbl-lang', t('popup_lang'));
    setText('lbl-api', t('popup_api'));
  }

  applyLocale();

  // API base
  chrome.storage.local.get(['loma_api_base'], (data) => {
    setText('api-base', data.loma_api_base || 'https://api.loma.app');
  });

  // Stats
  chrome.runtime.sendMessage({ type: 'GET_STATS' }, (res) => {
    if (res) {
      setText('rewrites-today', String(res.rewrites_today || 0));
      setText('rewrites-month', String(res.rewrites_month || 0));
    }
  });

  // Auth state
  chrome.runtime.sendMessage({ type: 'GET_AUTH' }, (res) => {
    if (res && res.email) {
      document.getElementById('auth-info').style.display = 'block';
      document.getElementById('auth-anon').style.display = 'none';
      setText('user-email', res.email);
      const badge = document.getElementById('tier-badge');
      const tier = res.tier || 'free';
      badge.textContent = tier === 'pro' ? 'Pro' : tier === 'payg' ? 'PAYG' : 'Free';
      badge.className = 'tier-badge tier-' + tier;
      if (tier === 'pro') {
        setText('balance', 'Unlimited');
      } else if (tier === 'payg') {
        setText('balance', (res.paygBalance || 0) + ' còn lại');
      } else {
        setText('balance', '5/ngày miễn phí');
      }
    } else {
      document.getElementById('auth-info').style.display = 'none';
      document.getElementById('auth-anon').style.display = 'block';
      setText('balance', '5/ngày miễn phí');
    }
  });

  // Logout
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      chrome.runtime.sendMessage({ type: 'LOGOUT' }, () => {
        document.getElementById('auth-info').style.display = 'none';
        document.getElementById('auth-anon').style.display = 'block';
        setText('balance', '5/ngày miễn phí');
      });
    });
  }

  // Site toggle
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

  // Language selector
  chrome.runtime.sendMessage({ type: 'GET_UI_LANG' }, (res) => {
    const sel = document.getElementById('lang-select');
    if (sel && res && res.lang) sel.value = res.lang;
  });

  const langSel = document.getElementById('lang-select');
  if (langSel) {
    langSel.addEventListener('change', (e) => {
      const lang = e.target.value;
      chrome.runtime.sendMessage({ type: 'SET_UI_LANG', lang }, () => {
        applyLocale();
      });
    });
  }
})();
