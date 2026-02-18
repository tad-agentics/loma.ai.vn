/**
 * Content script: find text fields, show Loma button when Vietnamese detected,
 * handle rewrite request (call API, show result).
 * Now includes: auth headers, keyboard shortcut, analytics, better error handling.
 */
(function () {
  const DEBOUNCE_MS = 300;
  const UNDO_TTL_MS = 5000;
  const FALLBACK_SCAN_MS = 3000;
  let debounceTimer = null;
  let undoState = null;
  let undoTimer = null;
  const buttons = new WeakMap();
  let lastFocusedField = null;
  let siteEnabled = true; // cached; assume enabled until background says otherwise

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
      if (text && text.length >= 5 && containsVietnamese(text)) {
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
        const lomaPlatform = typeof getPlatform === 'function' ? getPlatform() : 'generic';
        if (typeof LomaTextIsolation !== 'undefined' && LomaTextIsolation.replaceUserText) {
          LomaTextIsolation.replaceUserText(undoState.field, undoState.originalText, lomaPlatform);
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
    const lomaPlatform = typeof getPlatform === 'function' ? getPlatform() : 'generic';
    if (typeof LomaTextIsolation !== 'undefined' && LomaTextIsolation.extractUserTextFromElement) {
      const out = LomaTextIsolation.extractUserTextFromElement(field, lomaPlatform);
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
    const shouldShow = height >= minHeight && text.length >= 5 && containsVietnamese(text);
    let btn = buttons.get(field);
    if (shouldShow && !btn) {
      btn = document.createElement('loma-button');
      if (typeof btn.setField !== 'function') return; // custom element not registered
      btn.setField(field);
      if (typeof detectGrammarly === 'function' && detectGrammarly(field)) btn.setGrammarlyOffset(true);
      btn.addEventListener('loma-rewrite', () => onRewrite(field, getFieldText(field)));
      // Always append to document.body with position:fixed so the button is
      // never clipped by Gmail/Outlook overflow:hidden containers.
      document.body.appendChild(btn);
      buttons.set(field, btn);
    } else if (!shouldShow && btn) {
      btn.remove();
      buttons.delete(field);
    }
  }

  function doRewrite(field, text, intentOverride, toneOverride, outputLanguageOverride, refinementInstruction) {
    const card = typeof getLomaResultCard === 'function' ? getLomaResultCard() : null;
    const lomaBtn = buttons.get(field);
    if (lomaBtn && lomaBtn.setLoading) lomaBtn.setLoading(true);
    if (card) {
      card.setAnchorField(field);
      card.showLoading(intentOverride || null, field);
    }

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
      if (refinementInstruction) payload.refinement_instruction = refinementInstruction;

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
                      const lomaPlatform = typeof getPlatform === 'function' ? getPlatform() : 'generic';
                      if (typeof LomaTextIsolation !== 'undefined' && LomaTextIsolation.replaceUserText) {
                        LomaTextIsolation.replaceUserText(field, out, lomaPlatform);
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
                  onRefine: (instruction) => {
                    trackEvent('loma_refine', { instruction_length: instruction.length });
                    doRewrite(field, text, intentOverride, toneOverride, outputLanguageOverride, instruction);
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

  /**
   * Refresh cached site-enabled flag from background. Non-blocking — scan()
   * uses the cached value so it never stalls when the MV3 service worker is
   * inactive. Also removes Loma buttons immediately when disabled.
   */
  function refreshSiteEnabled() {
    const host = window.location.hostname || '';
    try {
      chrome.runtime.sendMessage({ type: 'GET_SITE_ENABLED', host }, (res) => {
        if (chrome.runtime.lastError) return;
        const enabled = !(res && res.enabled === false);
        if (!enabled && siteEnabled) {
          // Transition to disabled — remove all buttons
          document.querySelectorAll('loma-button').forEach((el) => el.remove());
        }
        siteEnabled = enabled;
      });
    } catch (_) { /* service worker unreachable — keep cached value */ }
  }

  function scan() {
    if (!siteEnabled) return;
    const textareas = document.querySelectorAll('textarea');
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"]');
    const fields = [...textareas, ...inputs];
    // Platforms that use contenteditable compose fields
    const platform = typeof getPlatform === 'function' ? getPlatform() : 'generic';
    if (['gmail', 'outlook', 'teams', 'google_docs', 'notion', 'jira', 'slack'].indexOf(platform) !== -1) {
      // Use broad selector — Gmail may use contenteditable="" or "plaintext-only",
      // not just "true". Filter with isContentEditable to catch all variants.
      const contenteditables = document.querySelectorAll('[contenteditable]:not([contenteditable="false"]), [role="textbox"]');
      contenteditables.forEach((el) => {
        if (el.isContentEditable && el.offsetHeight >= 38 && el.offsetParent !== null) fields.push(el);
      });
    }
    fields.forEach((el) => showOrHideButton(el));
  }

  function debouncedScan() {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(scan, DEBOUNCE_MS);
  }

  document.addEventListener('input', debouncedScan);
  document.addEventListener('change', debouncedScan);
  document.addEventListener('keyup', debouncedScan);
  // Gmail (and similar SPAs) create compose fields dynamically — rescan on focus
  document.addEventListener('focusin', debouncedScan);

  // Observe DOM for dynamically-added compose fields AND attribute changes
  // (Gmail may add a div first, then set contenteditable later).
  const mo = new MutationObserver((mutations) => {
    for (const m of mutations) {
      if (m.type === 'attributes') {
        debouncedScan();
        return;
      }
      for (const node of m.addedNodes) {
        if (node.nodeType === 1 &&
            (node.isContentEditable ||
             (node.querySelector && node.querySelector('[contenteditable]')))) {
          debouncedScan();
          return;
        }
      }
    }
  });
  mo.observe(document.body || document.documentElement, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['contenteditable', 'role'],
  });

  // Refresh site-enabled cache & run initial scan
  refreshSiteEnabled();
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) refreshSiteEnabled();
  });

  // Periodic fallback scan — catches cases where events are missed
  // (e.g. paste via context menu, autofill, drag-and-drop)
  setInterval(() => {
    if (!document.hidden) scan();
  }, FALLBACK_SCAN_MS);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scan);
  } else {
    scan();
  }
})();
