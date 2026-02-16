/**
 * Content script: find text fields, show Loma button when Vietnamese detected,
 * handle rewrite request (call API, show result).
 * Now includes: auth headers, keyboard shortcut, analytics, better error handling.
 */
(function () {
  const DEBOUNCE_MS = 300;
  const UNDO_TTL_MS = 5000;
  let debounceTimer = null;
  let undoState = null;
  let undoTimer = null;
  const buttons = new WeakMap();
  let lastFocusedField = null;

  // Track last focused text field for keyboard shortcut
  document.addEventListener('focusin', (e) => {
    const el = e.target;
    const tag = (el.tagName || '').toLowerCase();
    if (tag === 'textarea' || tag === 'input' || el.isContentEditable) {
      lastFocusedField = el;
    }
  });

  // Keyboard shortcut listener (from background via chrome.commands)
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === 'TRIGGER_REWRITE' && lastFocusedField) {
      const text = getFieldText(lastFocusedField);
      if (text && text.length >= 10 && containsVietnamese(text)) {
        onRewrite(lastFocusedField, text);
      }
    }
  });

  function trackEvent(eventName, eventData) {
    try {
      chrome.runtime.sendMessage({ type: 'TRACK_EVENT', eventName, eventData });
    } catch (_) {}
  }

  function showUndoToast(field, originalText) {
    if (undoTimer) clearTimeout(undoTimer);
    undoState = { field, originalText };
    const wrap = document.createElement('div');
    wrap.id = 'loma-undo-toast';
    wrap.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#111;color:#fff;padding:10px 14px;border-radius:8px;font-size:13px;z-index:2147483647;display:flex;align-items:center;gap:10px;box-shadow:0 4px 12px rgba(0,0,0,0.3);';
    wrap.setAttribute('role', 'status');
    wrap.setAttribute('aria-live', 'polite');
    const msg = document.createTextNode(chrome.i18n.getMessage('undo_toast') || 'Đã dùng. Hoàn tác?');
    const btn = document.createElement('button');
    btn.textContent = chrome.i18n.getMessage('undo_btn') || 'Hoàn tác';
    btn.style.cssText = 'background:#0d9488;border:none;color:#fff;padding:4px 10px;border-radius:6px;cursor:pointer;font-size:12px;';
    wrap.appendChild(msg);
    wrap.appendChild(btn);
    document.body.appendChild(wrap);
    function clear() {
      if (wrap.parentNode) wrap.parentNode.removeChild(wrap);
      undoState = null;
      if (undoTimer) clearTimeout(undoTimer);
      undoTimer = null;
    }
    btn.addEventListener('click', () => {
      if (undoState && undoState.field && undoState.originalText !== undefined) {
        const isGmail = typeof getPlatform === 'function' && getPlatform() === 'gmail';
        if (typeof LomaTextIsolation !== 'undefined' && LomaTextIsolation.replaceUserText) {
          LomaTextIsolation.replaceUserText(undoState.field, undoState.originalText, isGmail);
        } else {
          const tag = (undoState.field.tagName || '').toLowerCase();
          if (tag === 'textarea' || tag === 'input') undoState.field.value = undoState.originalText;
          else if (undoState.field.isContentEditable) undoState.field.innerText = undoState.originalText;
          undoState.field.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }
      clear();
    });
    undoTimer = setTimeout(clear, UNDO_TTL_MS);
  }

  function getApiBase(cb) {
    chrome.runtime.sendMessage({ type: 'GET_API_BASE' }, (r) => {
      cb(r && r.apiBase ? r.apiBase : 'https://api.loma.app');
    });
  }

  function getAuth(cb) {
    chrome.runtime.sendMessage({ type: 'GET_AUTH' }, (r) => {
      cb(r || { token: null });
    });
  }

  function getFieldText(field) {
    const isGmail = typeof getPlatform === 'function' && getPlatform() === 'gmail';
    if (typeof LomaTextIsolation !== 'undefined' && LomaTextIsolation.extractUserTextFromElement) {
      const out = LomaTextIsolation.extractUserTextFromElement(field, isGmail);
      return out.userText || (field.value || field.innerText || field.textContent || '').trim();
    }
    const tag = (field.tagName || '').toLowerCase();
    if (tag === 'textarea' || tag === 'input') return (field.value || '').trim();
    return (field.innerText || field.textContent || '').trim();
  }

  function showOrHideButton(field) {
    const text = getFieldText(field);
    const minHeight = 38;
    const height = field.offsetHeight || 0;
    const shouldShow = height >= minHeight && text.length >= 10 && containsVietnamese(text);
    let btn = buttons.get(field);
    if (shouldShow && !btn) {
      btn = document.createElement('loma-button');
      btn.setField(field);
      if (typeof detectGrammarly === 'function' && detectGrammarly(field)) btn.setAttribute('grammarly-offset', '');
      btn.addEventListener('loma-rewrite', () => onRewrite(field, getFieldText(field)));
      field.style.position = field.style.position || 'relative';
      field.appendChild(btn);
      buttons.set(field, btn);
    } else if (!shouldShow && btn) {
      btn.remove();
      buttons.delete(field);
    }
  }

  function doRewrite(field, text, intentOverride, toneOverride, outputLanguageOverride) {
    const card = typeof getLomaResultCard === 'function' ? getLomaResultCard() : null;
    const lomaBtn = buttons.get(field);
    if (lomaBtn && lomaBtn.setLoading) lomaBtn.setLoading(true);
    if (card) card.showLoading(intentOverride || null);

    function clearLoading() {
      if (lomaBtn && lomaBtn.setLoading) lomaBtn.setLoading(false);
    }

    function sendRequest(apiBase, authToken, outputLanguage, tone) {
      const url = apiBase.replace(/\/$/, '') + '/api/v1/rewrite';
      const platform = typeof getPlatform === 'function' ? getPlatform() : 'generic';
      const languageMix = typeof computeLanguageMix === 'function' ? computeLanguageMix(text) : { vi_ratio: 0.5, en_ratio: 0.5 };
      const payload = {
        input_text: text,
        platform,
        tone: tone || 'professional',
        language_mix: languageMix,
        output_language: outputLanguage || 'en',
      };
      if (intentOverride) payload.intent = intentOverride;

      const headers = { 'Content-Type': 'application/json' };
      if (authToken) headers['Authorization'] = 'Bearer ' + authToken;

      fetch(url, { method: 'POST', headers, body: JSON.stringify(payload) })
        .then((res) => {
          if (res.status === 429) {
            return res.json().then((data) => {
              clearLoading();
              if (card) card.hide();
              const msg = data.message_vi || data.message || 'Đã hết lượt miễn phí.';
              alert(msg);
              trackEvent('loma_quota_hit', { tier: data.tier });
            });
          }
          return res.json().then((data) => {
            clearLoading();
            if (data.error) {
              if (card) card.hide();
              alert(chrome.i18n.getMessage('error_failed') + ' ' + (data.message_vi || data.message || data.error));
              trackEvent('loma_error', { error: data.error });
              return;
            }
            trackEvent('loma_rewrite', {
              detected_intent: data.detected_intent,
              routing_tier: data.routing_tier,
              output_language: data.output_language,
            });
            if (card) {
              card.showResult(
                {
                  output_text: data.output_text,
                  original_text: text,
                  input_text: text,
                  scores: data.scores,
                  intent_confidence: data.intent_confidence,
                  detected_intent: data.detected_intent,
                  output_language: data.output_language,
                },
                {
                  onToneChange: function (tone, outputLanguage) {
                    if (typeof setOutputLanguageForDomain === 'function') setOutputLanguageForDomain(outputLanguage);
                    trackEvent('loma_tone_change', { tone, output_language: outputLanguage });
                    doRewrite(field, text, intentOverride, tone, outputLanguage);
                  },
                  onUse: () => {
                    const out = (data.output_text || '').trim();
                    const original = (data.original_text || text || '').trim();
                    if (out) {
                      const isGmail = typeof getPlatform === 'function' && getPlatform() === 'gmail';
                      if (typeof LomaTextIsolation !== 'undefined' && LomaTextIsolation.replaceUserText) {
                        LomaTextIsolation.replaceUserText(field, out, isGmail);
                      } else {
                        if ((field.tagName || '').toLowerCase() === 'textarea' || (field.tagName || '').toLowerCase() === 'input') {
                          field.value = out;
                          field.dispatchEvent(new Event('input', { bubbles: true }));
                        } else {
                          field.innerText = out;
                          field.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                      }
                    }
                    chrome.runtime.sendMessage({ type: 'INCREMENT_REWRITES' }, function () {});
                    trackEvent('loma_use', { detected_intent: data.detected_intent });
                    showUndoToast(field, original);
                  },
                  onCopy: () => {
                    trackEvent('loma_copy', { detected_intent: data.detected_intent });
                  },
                  onIntentPick: (intent) => {
                    trackEvent('loma_intent_pick', { intent });
                    doRewrite(field, text, intent);
                  },
                }
              );
            } else {
              const out = data.output_text || '';
              if (out && (field.tagName || '').toLowerCase() === 'textarea') {
                field.value = out;
                field.dispatchEvent(new Event('input', { bubbles: true }));
              } else if (out && field.isContentEditable) {
                field.innerText = out;
                field.dispatchEvent(new Event('input', { bubbles: true }));
              }
            }
          });
        })
        .catch((err) => {
          clearLoading();
          if (card) card.hide();
          const isOffline = !navigator.onLine;
          const msg = isOffline
            ? (chrome.i18n.getMessage('error_offline') || 'Không có kết nối mạng.')
            : (chrome.i18n.getMessage('error_failed') || 'Có lỗi xảy ra.');
          alert(msg);
          trackEvent('loma_error', { error: isOffline ? 'offline' : 'network', detail: String(err) });
        });
    }

    getApiBase((apiBase) => {
      getAuth((auth) => {
        if (typeof getOutputLanguage === 'function' && getOutputLanguage.length > 0) {
          getOutputLanguage(function (outputLanguage) {
            const lang = outputLanguageOverride != null ? outputLanguageOverride : outputLanguage;
            const tone = toneOverride || 'professional';
            sendRequest(apiBase, auth.token, lang, tone);
          });
        } else {
          const lang = outputLanguageOverride != null ? outputLanguageOverride : 'en';
          sendRequest(apiBase, auth.token, lang, toneOverride || 'professional');
        }
      });
    });
  }

  function onRewrite(field, text) {
    doRewrite(field, text, null);
  }

  function scan() {
    const host = window.location.hostname || '';
    chrome.runtime.sendMessage({ type: 'GET_SITE_ENABLED', host }, (res) => {
      if (res && res.enabled === false) {
        document.querySelectorAll('loma-button').forEach((el) => el.remove());
        return;
      }
      const textareas = document.querySelectorAll('textarea');
      const inputs = document.querySelectorAll('input[type="text"], input[type="email"]');
      const fields = [...textareas, ...inputs];
      if (typeof getPlatform === 'function' && getPlatform() === 'gmail') {
        const contenteditables = document.querySelectorAll('div[contenteditable="true"], [role="textbox"][contenteditable="true"]');
        contenteditables.forEach((el) => {
          if (el.offsetHeight >= 38 && el.offsetParent !== null) fields.push(el);
        });
      }
      fields.forEach((el) => showOrHideButton(el));
    });
  }

  function debouncedScan() {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(scan, DEBOUNCE_MS);
  }

  document.addEventListener('input', debouncedScan);
  document.addEventListener('change', debouncedScan);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scan);
  } else {
    scan();
  }
})();
