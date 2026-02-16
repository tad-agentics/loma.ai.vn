/**
 * Loma — background service worker (Manifest V3).
 * Handles API base URL, auth token refresh (Phase 2), and rewrite count (Phase 2).
 */
chrome.runtime.onInstalled.addListener((details) => {
  chrome.storage.local.get(['loma_api_base'], (data) => {
    if (!data.loma_api_base) {
      chrome.storage.local.set({ loma_api_base: 'http://localhost:3000' });
    }
  });
  if (details.reason === 'install') {
    chrome.tabs.create({ url: chrome.runtime.getURL('welcome.html') });
  }
});

const STORAGE_KEYS = {
  api_base: 'loma_api_base',
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

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'GET_API_BASE') {
    chrome.storage.local.get([STORAGE_KEYS.api_base], (data) => {
      sendResponse({ apiBase: data[STORAGE_KEYS.api_base] || 'http://localhost:3000' });
    });
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
});
