/**
 * Loma — background service worker (Manifest V3).
 * Handles: API base URL, auth token, rewrite counts, site toggles,
 * keyboard shortcut command, analytics relay, UI language.
 */

const DEFAULT_API_BASE = 'https://api.loma.app';

chrome.runtime.onInstalled.addListener((details) => {
  chrome.storage.local.get(['loma_api_base'], (data) => {
    if (!data.loma_api_base) {
      chrome.storage.local.set({ loma_api_base: DEFAULT_API_BASE });
    }
  });
  if (details.reason === 'install') {
    chrome.tabs.create({ url: chrome.runtime.getURL('welcome.html') });
  }
});

const STORAGE_KEYS = {
  api_base: 'loma_api_base',
  auth_token: 'loma_auth_token',
  user_id: 'loma_user_id',
  user_email: 'loma_user_email',
  subscription_tier: 'loma_subscription_tier',
  payg_balance: 'loma_payg_balance',
  rewrites_today: 'loma_rewrites_today',
  rewrites_month: 'loma_rewrites_month',
  last_date: 'loma_last_date',
  site_disabled: 'loma_site_disabled',
  ui_lang: 'loma_ui_lang',
};

function resetDailyIfNeeded(data) {
  const today = new Date().toDateString();
  if (data[STORAGE_KEYS.last_date] !== today) {
    data[STORAGE_KEYS.rewrites_today] = 0;
    data[STORAGE_KEYS.last_date] = today;
  }
  return data;
}

// Keyboard shortcut handler (Ctrl+Shift+. / Cmd+Shift+.)
chrome.commands.onCommand.addListener((command) => {
  if (command === 'trigger-rewrite') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, { type: 'TRIGGER_REWRITE' });
      }
    });
  }
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'GET_API_BASE') {
    chrome.storage.local.get([STORAGE_KEYS.api_base], (data) => {
      sendResponse({ apiBase: data[STORAGE_KEYS.api_base] || DEFAULT_API_BASE });
    });
    return true;
  }

  if (msg.type === 'GET_AUTH') {
    chrome.storage.local.get([
      STORAGE_KEYS.auth_token, STORAGE_KEYS.user_id, STORAGE_KEYS.user_email,
      STORAGE_KEYS.subscription_tier, STORAGE_KEYS.payg_balance,
    ], (data) => {
      sendResponse({
        token: data[STORAGE_KEYS.auth_token] || null,
        userId: data[STORAGE_KEYS.user_id] || null,
        email: data[STORAGE_KEYS.user_email] || null,
        tier: data[STORAGE_KEYS.subscription_tier] || 'free',
        paygBalance: data[STORAGE_KEYS.payg_balance] || 0,
      });
    });
    return true;
  }

  if (msg.type === 'SET_AUTH') {
    const updates = {};
    if (msg.token !== undefined) updates[STORAGE_KEYS.auth_token] = msg.token;
    if (msg.userId !== undefined) updates[STORAGE_KEYS.user_id] = msg.userId;
    if (msg.email !== undefined) updates[STORAGE_KEYS.user_email] = msg.email;
    if (msg.tier !== undefined) updates[STORAGE_KEYS.subscription_tier] = msg.tier;
    if (msg.paygBalance !== undefined) updates[STORAGE_KEYS.payg_balance] = msg.paygBalance;
    chrome.storage.local.set(updates);
    sendResponse({ ok: true });
    return true;
  }

  if (msg.type === 'LOGOUT') {
    chrome.storage.local.remove([
      STORAGE_KEYS.auth_token, STORAGE_KEYS.user_id, STORAGE_KEYS.user_email,
      STORAGE_KEYS.subscription_tier, STORAGE_KEYS.payg_balance,
    ]);
    sendResponse({ ok: true });
    return true;
  }

  if (msg.type === 'GET_STATS') {
    chrome.storage.local.get([STORAGE_KEYS.rewrites_today, STORAGE_KEYS.rewrites_month, STORAGE_KEYS.last_date], (data) => {
      const updated = resetDailyIfNeeded(data);
      if (updated[STORAGE_KEYS.last_date] !== data[STORAGE_KEYS.last_date]) {
        chrome.storage.local.set({ [STORAGE_KEYS.last_date]: updated[STORAGE_KEYS.last_date], [STORAGE_KEYS.rewrites_today]: 0 });
      }
      sendResponse({
        rewrites_today: updated[STORAGE_KEYS.rewrites_today] || 0,
        rewrites_month: updated[STORAGE_KEYS.rewrites_month] || 0,
      });
    });
    return true;
  }

  if (msg.type === 'INCREMENT_REWRITES') {
    chrome.storage.local.get([STORAGE_KEYS.rewrites_today, STORAGE_KEYS.rewrites_month, STORAGE_KEYS.last_date], (data) => {
      const updated = resetDailyIfNeeded(data);
      updated[STORAGE_KEYS.rewrites_today] = (updated[STORAGE_KEYS.rewrites_today] || 0) + 1;
      updated[STORAGE_KEYS.rewrites_month] = (updated[STORAGE_KEYS.rewrites_month] || 0) + 1;
      chrome.storage.local.set({
        [STORAGE_KEYS.rewrites_today]: updated[STORAGE_KEYS.rewrites_today],
        [STORAGE_KEYS.rewrites_month]: updated[STORAGE_KEYS.rewrites_month],
        [STORAGE_KEYS.last_date]: updated[STORAGE_KEYS.last_date],
      });
      sendResponse({ ok: true });
    });
    return true;
  }

  if (msg.type === 'GET_SITE_ENABLED') {
    const host = msg.host || '';
    chrome.storage.local.get([STORAGE_KEYS.site_disabled], (data) => {
      const list = data[STORAGE_KEYS.site_disabled] || [];
      sendResponse({ enabled: !list.includes(host) });
    });
    return true;
  }

  if (msg.type === 'SET_SITE_ENABLED') {
    const host = msg.host || '';
    const enabled = msg.enabled !== false;
    chrome.storage.local.get([STORAGE_KEYS.site_disabled], (data) => {
      let list = data[STORAGE_KEYS.site_disabled] || [];
      if (enabled) list = list.filter((h) => h !== host);
      else if (!list.includes(host)) list.push(host);
      chrome.storage.local.set({ [STORAGE_KEYS.site_disabled]: list });
      sendResponse({ ok: true });
    });
    return true;
  }

  if (msg.type === 'GET_UI_LANG') {
    chrome.storage.local.get([STORAGE_KEYS.ui_lang], (data) => {
      sendResponse({ lang: data[STORAGE_KEYS.ui_lang] || 'vi' });
    });
    return true;
  }

  if (msg.type === 'SET_UI_LANG') {
    chrome.storage.local.set({ [STORAGE_KEYS.ui_lang]: msg.lang || 'vi' });
    sendResponse({ ok: true });
    return true;
  }

  // Relay analytics events to backend
  if (msg.type === 'TRACK_EVENT') {
    chrome.storage.local.get([STORAGE_KEYS.api_base, STORAGE_KEYS.auth_token], (data) => {
      const apiBase = (data[STORAGE_KEYS.api_base] || DEFAULT_API_BASE).replace(/\/$/, '');
      const headers = { 'Content-Type': 'application/json' };
      if (data[STORAGE_KEYS.auth_token]) {
        headers['Authorization'] = 'Bearer ' + data[STORAGE_KEYS.auth_token];
      }
      fetch(apiBase + '/api/v1/events', {
        method: 'POST',
        headers,
        body: JSON.stringify({ event_name: msg.eventName, event_data: msg.eventData || {} }),
      }).catch(() => {});
    });
    sendResponse({ ok: true });
    return true;
  }
});
