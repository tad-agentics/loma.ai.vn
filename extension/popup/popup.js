/**
 * Popup — Vietnamese-first: auth status, balance, rewrites today/month,
 * per-site toggle, UI language, keyboard shortcut hint.
 *
 * Language switching uses a runtime translation map because chrome.i18n is
 * compile-time only and cannot be changed after the extension is loaded.
 */
(function () {
  // Runtime translations for popup-only keys (both languages)
  const STRINGS = {
    vi: {
      ext_name: 'Loma',
      popup_rewrites_today: 'Hôm nay',
      popup_rewrites_month: 'Tháng này',
      popup_site_toggle: 'Bật Loma trên trang này',
      popup_lang: 'Giao diện',
      popup_api: 'API',
      popup_balance_free: '5/ngày miễn phí',
      popup_remaining: 'còn lại',
      popup_anon: '5 lượt miễn phí / ngày',
      popup_signout: 'Đăng xuất',
    },
    en: {
      ext_name: 'Loma',
      popup_rewrites_today: 'Today',
      popup_rewrites_month: 'This month',
      popup_site_toggle: 'Enable Loma on this site',
      popup_lang: 'UI language',
      popup_api: 'API',
      popup_balance_free: '5/day free',
      popup_remaining: 'remaining',
      popup_anon: '5 free rewrites / day',
      popup_signout: 'Sign out',
    },
  };

  let currentLang = 'vi';

  function t(key) {
    return (STRINGS[currentLang] && STRINGS[currentLang][key]) || (STRINGS.vi[key]) || key;
  }

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
    // Update anon label if visible
    const authAnon = document.getElementById('auth-anon');
    if (authAnon && authAnon.style.display !== 'none') {
      authAnon.querySelector('.label').textContent = t('popup_anon');
    }
    // Update sign-out button
    setText('btn-logout', t('popup_signout'));
  }

  // Load saved language preference, then apply
  chrome.runtime.sendMessage({ type: 'GET_UI_LANG' }, (res) => {
    if (res && res.lang) currentLang = res.lang;
    applyLocale();
    const sel = document.getElementById('lang-select');
    if (sel) sel.value = currentLang;
  });

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
        setText('balance', (res.paygBalance || 0) + ' ' + t('popup_remaining'));
      } else {
        setText('balance', t('popup_balance_free'));
      }
    } else {
      document.getElementById('auth-info').style.display = 'none';
      document.getElementById('auth-anon').style.display = 'block';
      setText('balance', t('popup_balance_free'));
    }
  });

  // Logout
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      chrome.runtime.sendMessage({ type: 'LOGOUT' }, () => {
        document.getElementById('auth-info').style.display = 'none';
        document.getElementById('auth-anon').style.display = 'block';
        setText('balance', t('popup_balance_free'));
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
  const langSel = document.getElementById('lang-select');
  if (langSel) {
    langSel.addEventListener('change', (e) => {
      const lang = e.target.value;
      currentLang = lang;
      chrome.runtime.sendMessage({ type: 'SET_UI_LANG', lang }, () => {
        applyLocale();
      });
    });
  }
})();
