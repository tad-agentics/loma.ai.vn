/**
 * Loma result card — Grammarly-style inline card anchored to the text field.
 * Positioned with position:fixed near the bottom of the active field.
 * Intent badge, tone tabs, diff-highlighted suggestion, accept/copy/dismiss,
 * and a refinement input ("Ask for a change").
 */
(function () {
  const t = (key) => chrome.i18n.getMessage(key) || key;

  const INTENT_TO_I18N = {
    ask_payment: 'intent_payment', follow_up: 'intent_followup', say_no: 'intent_decline',
    request_senior: 'intent_request', cold_outreach: 'intent_cold_outreach', give_feedback: 'intent_feedback',
    disagree: 'intent_disagree', escalate: 'intent_escalate', apologize: 'intent_apologize',
    ai_prompt: 'intent_ai_prompt', general: 'intent_other',
    write_to_gov: 'intent_gov_doc', write_formal_vn: 'intent_formal_vn', write_report_vn: 'intent_report_vn', write_proposal_vn: 'intent_proposal_vn',
  };
  const INTENT_TO_LOADING = {
    ask_payment: 'loading_payment', follow_up: 'loading_followup', say_no: 'loading_decline',
    request_senior: 'loading_request', cold_outreach: 'loading_outreach', give_feedback: 'loading_feedback',
    disagree: 'loading_disagree', escalate: 'loading_escalate', apologize: 'loading_apologize',
    ai_prompt: 'loading_ai_prompt', general: 'loading_generic',
    write_to_gov: 'loading_gov_doc', write_formal_vn: 'loading_formal_vn', write_report_vn: 'loading_report_vn', write_proposal_vn: 'loading_proposal_vn',
  };

  /** Simple word-level diff: returns HTML with <ins>/<del> tags. */
  function diffWords(original, rewritten) {
    const a = original.split(/(\s+)/);
    const b = rewritten.split(/(\s+)/);
    // LCS-based diff for word tokens
    const m = a.length, n = b.length;
    const dp = Array.from({ length: m + 1 }, () => new Uint16Array(n + 1));
    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        dp[i][j] = a[i - 1] === b[j - 1] ? dp[i - 1][j - 1] + 1 : Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }
    const parts = [];
    let i = m, j = n;
    while (i > 0 || j > 0) {
      if (i > 0 && j > 0 && a[i - 1] === b[j - 1]) {
        parts.push({ type: 'same', text: a[i - 1] });
        i--; j--;
      } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
        parts.push({ type: 'ins', text: b[j - 1] });
        j--;
      } else {
        parts.push({ type: 'del', text: a[i - 1] });
        i--;
      }
    }
    parts.reverse();
    // Merge consecutive same-type tokens
    let html = '';
    for (const p of parts) {
      const escaped = p.text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      if (p.type === 'ins') html += '<ins>' + escaped + '</ins>';
      else if (p.type === 'del') html += '<del>' + escaped + '</del>';
      else html += escaped;
    }
    return html;
  }

  function createCard() {
    const host = document.createElement('div');
    host.id = 'loma-result-card-host';
    host.style.cssText = 'position:fixed;z-index:2147483647;display:none;';
    document.body.appendChild(host);

    const root = host.attachShadow({ mode: 'open' });
    root.innerHTML = `
      <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :host { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; line-height: 1.5; color: #1f2937; }

        .card {
          background: #fff;
          border: 1px solid #e5e7eb;
          border-radius: 10px;
          box-shadow: 0 8px 30px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
          width: 440px;
          max-width: 92vw;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        /* Header */
        .header {
          background: #111827;
          color: #f9fafb;
          padding: 10px 14px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 12px;
          font-weight: 500;
        }
        .header-left { display: flex; align-items: center; gap: 6px; }
        .header-logo { font-weight: 700; font-size: 13px; color: #5eead4; }
        .header-dot { color: #6b7280; }
        .header-intent { color: #d1d5db; }
        .btn-close {
          background: none; border: none; color: #9ca3af; cursor: pointer;
          font-size: 16px; line-height: 1; padding: 2px 4px; border-radius: 4px;
        }
        .btn-close:hover { color: #f9fafb; background: rgba(255,255,255,0.1); }

        /* Tone tabs */
        .tabs {
          display: flex;
          border-bottom: 1px solid #e5e7eb;
          padding: 0 14px;
          gap: 0;
          overflow-x: auto;
        }
        .tab {
          padding: 9px 14px;
          font-size: 13px;
          color: #6b7280;
          background: none;
          border: none;
          border-bottom: 2px solid transparent;
          cursor: pointer;
          white-space: nowrap;
          transition: color 0.15s, border-color 0.15s;
        }
        .tab:hover { color: #111827; }
        .tab.active { color: #0d9488; border-bottom-color: #0d9488; font-weight: 600; }

        /* Body / suggestion area */
        .body { padding: 14px; flex: 1; min-height: 0; overflow-y: auto; max-height: 220px; }

        .suggestion {
          border-left: 3px solid #0d9488;
          padding: 10px 12px;
          background: #f0fdfa;
          border-radius: 0 6px 6px 0;
          margin-bottom: 10px;
        }
        .suggestion-label { font-size: 12px; color: #0d9488; font-weight: 600; margin-bottom: 6px; }
        .suggestion-text {
          white-space: pre-wrap; word-break: break-word;
          font-size: 14px; line-height: 1.6; color: #1f2937;
        }
        .suggestion-text ins {
          text-decoration: none;
          background: #bbf7d0;
          color: #14532d;
          padding: 0 1px;
          border-radius: 2px;
        }
        .suggestion-text del {
          background: #fecaca;
          color: #991b1b;
          text-decoration: line-through;
          opacity: 0.7;
          padding: 0 1px;
          border-radius: 2px;
        }

        .meta { font-size: 12px; color: #6b7280; }

        /* Loading skeleton */
        .skeleton { padding: 14px; }
        .skeleton-badge { height: 14px; width: 140px; border-radius: 4px; margin-bottom: 10px; }
        .skeleton-line { height: 14px; border-radius: 4px; margin-bottom: 8px; }
        .skeleton-line.short { width: 60%; }
        .shimmer {
          background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
          background-size: 200% 100%;
          animation: loma-shimmer 1.2s ease-in-out infinite;
        }
        @keyframes loma-shimmer { to { background-position: 200% 0; } }
        @media (prefers-reduced-motion: reduce) { .shimmer { animation: none; background: #e5e7eb; } }
        .loading-microcopy { font-size: 13px; color: #6b7280; margin-bottom: 12px; }

        /* Footer actions */
        .footer {
          padding: 10px 14px;
          border-top: 1px solid #e5e7eb;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .btn-accept {
          background: #0d9488; color: #fff; border: none; border-radius: 6px;
          padding: 7px 18px; font-size: 13px; font-weight: 600; cursor: pointer;
          transition: background 0.15s;
        }
        .btn-accept:hover { background: #0f766e; }
        .btn-accept:disabled { opacity: 0.4; cursor: default; }
        .btn-icon {
          background: none; border: 1px solid #e5e7eb; border-radius: 6px;
          width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
          cursor: pointer; color: #6b7280; font-size: 14px; transition: background 0.15s;
        }
        .btn-icon:hover { background: #f3f4f6; color: #111827; }
        .btn-icon:disabled { opacity: 0.4; cursor: default; }
        .footer-spacer { flex: 1; }

        /* Refinement input */
        .refine {
          padding: 8px 14px;
          border-top: 1px solid #e5e7eb;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .refine-input {
          flex: 1;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          padding: 7px 10px;
          font-size: 13px;
          color: #374151;
          outline: none;
          background: #f9fafb;
          transition: border-color 0.15s;
        }
        .refine-input::placeholder { color: #9ca3af; }
        .refine-input:focus { border-color: #0d9488; background: #fff; }
        .btn-send {
          background: #0d9488; border: none; border-radius: 6px;
          width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
          cursor: pointer; color: #fff; font-size: 14px;
          transition: background 0.15s;
        }
        .btn-send:hover { background: #0f766e; }

        /* Toast */
        .toast {
          position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
          background: #111; color: #fff; padding: 8px 18px; border-radius: 8px;
          font-size: 13px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          opacity: 0; transition: opacity 0.2s; pointer-events: none;
        }
        .toast.show { opacity: 1; }
      </style>
      <div class="card" id="card">
        <div class="header" id="header">
          <div class="header-left">
            <span class="header-logo">Loma</span>
            <span class="header-dot">·</span>
            <span class="header-intent" id="header-intent">Rewrite</span>
          </div>
          <button class="btn-close" id="btn-close" type="button" aria-label="Close">✕</button>
        </div>
        <div class="tabs" id="tabs"></div>
        <div class="body" id="body"></div>
        <div class="footer" id="footer" style="display:none"></div>
        <div class="refine" id="refine" style="display:none">
          <input class="refine-input" id="refine-input" type="text" placeholder="" />
          <button class="btn-send" id="btn-send" type="button" aria-label="Send">➜</button>
        </div>
      </div>
      <div class="toast" id="toast"></div>
    `;

    const card = root.getElementById('card');
    const headerIntent = root.getElementById('header-intent');
    const tabsEl = root.getElementById('tabs');
    const body = root.getElementById('body');
    const footer = root.getElementById('footer');
    const refineWrap = root.getElementById('refine');
    const refineInput = root.getElementById('refine-input');
    const btnSend = root.getElementById('btn-send');
    const btnClose = root.getElementById('btn-close');
    const toastEl = root.getElementById('toast');

    let state = 'hidden';
    let currentData = null;
    let callbacks = null;
    let anchorField = null;
    let _rafId = null;

    const TONE_TABS = [
      { tone: 'professional', i18n: 'tone_direct', label: 'Professional' },
      { tone: 'softer', i18n: 'tone_softer', label: 'Softer' },
      { tone: 'formal', i18n: 'tone_formal', label: 'Formal' },
      { tone: 'shorter', i18n: 'tone_shorter', label: 'Shorter' },
    ];
    let activeTone = 'professional';

    function hide() {
      host.style.display = 'none';
      state = 'hidden';
      currentData = null;
      callbacks = null;
      anchorField = null;
      removeEscapeListener();
      removePositionListeners();
    }

    function onEscape(e) { if (e.key === 'Escape') hide(); }
    function addEscapeListener() { removeEscapeListener(); document.addEventListener('keydown', onEscape); }
    function removeEscapeListener() { document.removeEventListener('keydown', onEscape); }

    btnClose.addEventListener('click', hide);

    // Close when clicking outside the card
    function onDocClick(e) {
      if (state === 'hidden') return;
      if (host.contains(e.target)) return;
      // Check shadow DOM
      const path = e.composedPath ? e.composedPath() : [];
      if (path.includes(host)) return;
      hide();
    }
    document.addEventListener('mousedown', onDocClick, true);

    /** Position the card below (or above) the anchor field. */
    function reposition() {
      if (_rafId) cancelAnimationFrame(_rafId);
      _rafId = requestAnimationFrame(() => {
        if (!anchorField) return;
        const rect = anchorField.getBoundingClientRect();
        const cardHeight = card.offsetHeight || 300;
        const cardWidth = card.offsetWidth || 440;
        const margin = 8;
        const spaceBelow = window.innerHeight - rect.bottom;
        const spaceAbove = rect.top;

        let top, left;
        if (spaceBelow >= cardHeight + margin || spaceBelow >= spaceAbove) {
          top = rect.bottom + margin;
        } else {
          top = rect.top - cardHeight - margin;
        }
        // Clamp vertical
        top = Math.max(margin, Math.min(top, window.innerHeight - cardHeight - margin));

        // Align left edge with field, clamp to viewport
        left = rect.left;
        left = Math.max(margin, Math.min(left, window.innerWidth - cardWidth - margin));

        host.style.top = top + 'px';
        host.style.left = left + 'px';
      });
    }

    function addPositionListeners() {
      window.addEventListener('scroll', reposition, true);
      window.addEventListener('resize', reposition);
    }
    function removePositionListeners() {
      window.removeEventListener('scroll', reposition, true);
      window.removeEventListener('resize', reposition);
      if (_rafId) cancelAnimationFrame(_rafId);
    }

    function showToast(message) {
      toastEl.textContent = message;
      toastEl.classList.add('show');
      setTimeout(() => toastEl.classList.remove('show'), 2000);
    }

    function renderTabs(onTabClick) {
      tabsEl.innerHTML = '';
      TONE_TABS.forEach(({ tone, i18n }) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'tab' + (tone === activeTone ? ' active' : '');
        btn.textContent = t(i18n);
        btn.addEventListener('click', () => {
          activeTone = tone;
          if (typeof onTabClick === 'function') onTabClick(tone);
        });
        tabsEl.appendChild(btn);
      });
    }

    function showLoading(detectedIntent, field) {
      state = 'loading';
      anchorField = field || anchorField;
      host.style.display = 'block';
      addPositionListeners();
      reposition();

      headerIntent.textContent = t(INTENT_TO_I18N[detectedIntent] || 'intent_other').replace(/^[^\w\s]+\s*/, '');
      const loadMsg = t(INTENT_TO_LOADING[detectedIntent] || 'loading_generic');

      renderTabs(null);
      body.innerHTML = `
        <div class="skeleton">
          <div class="loading-microcopy">${loadMsg.replace(/&/g,'&amp;').replace(/</g,'&lt;')}</div>
          <div class="skeleton-line shimmer" style="width:100%"></div>
          <div class="skeleton-line shimmer short"></div>
          <div class="skeleton-line shimmer" style="width:85%"></div>
        </div>
      `;
      footer.style.display = 'flex';
      footer.innerHTML = '<button class="btn-accept" disabled type="button">' + t('btn_use').replace(/^[✓\s]+/, '✓ ') + '</button>';
      refineWrap.style.display = 'none';
      addEscapeListener();
    }

    function showResult(data, cbs) {
      state = 'result';
      currentData = data;
      callbacks = cbs || {};
      const output = (data.output_text || '').trim();
      const original = (data.original_text || data.input_text || '').trim();
      const pct = data.scores && data.scores.length_reduction_pct != null ? data.scores.length_reduction_pct : null;
      const outputLang = data.output_language || 'en';

      host.style.display = 'block';
      reposition();

      // Header intent
      headerIntent.textContent = t(INTENT_TO_I18N[data.detected_intent] || 'intent_other').replace(/^[^\w\s]+\s*/, '');

      // Tabs with live tone switching
      renderTabs((tone) => {
        if (typeof callbacks.onToneChange === 'function') {
          const lang = tone.startsWith('vi_') ? tone : outputLang;
          callbacks.onToneChange(tone, lang);
        }
      });

      // Suggestion body
      const html = diffWords(original, output);
      body.innerHTML = '';
      const suggestion = document.createElement('div');
      suggestion.className = 'suggestion';

      // Label
      const label = document.createElement('div');
      label.className = 'suggestion-label';
      label.textContent = t(INTENT_TO_I18N[data.detected_intent] || 'intent_other').replace(/^[^\w\s]+\s*/, '');
      suggestion.appendChild(label);

      // Diff text
      const textEl = document.createElement('div');
      textEl.className = 'suggestion-text';
      textEl.innerHTML = html;
      suggestion.appendChild(textEl);
      body.appendChild(suggestion);

      // Quality meta
      if (pct != null || outputLang === 'vi_admin') {
        const meta = document.createElement('div');
        meta.className = 'meta';
        if (outputLang === 'vi_admin') meta.textContent = t('quality_format_admin');
        else if (outputLang && outputLang.startsWith('vi_') && pct < 0) meta.textContent = t('quality_more_complete');
        else meta.textContent = chrome.i18n.getMessage('quality_shorter', [String(Math.round(pct))]) || (Math.round(pct) + '% shorter');
        body.appendChild(meta);
      }

      // Footer: Accept + Copy + Dismiss
      footer.innerHTML = '';
      footer.style.display = 'flex';

      const btnAccept = document.createElement('button');
      btnAccept.type = 'button';
      btnAccept.className = 'btn-accept';
      btnAccept.textContent = t('btn_use').replace(/^[✓\s]+/, '✓ ');
      btnAccept.addEventListener('click', () => {
        if (typeof callbacks.onUse === 'function') callbacks.onUse();
        hide();
      });

      const btnCopy = document.createElement('button');
      btnCopy.type = 'button';
      btnCopy.className = 'btn-icon';
      btnCopy.innerHTML = '📋';
      btnCopy.title = t('btn_copy');
      btnCopy.addEventListener('click', () => {
        if (output && navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(output).then(() => showToast(t('copied_toast')));
        }
        if (typeof callbacks.onCopy === 'function') callbacks.onCopy();
      });

      const spacer = document.createElement('div');
      spacer.className = 'footer-spacer';

      const btnDismiss = document.createElement('button');
      btnDismiss.type = 'button';
      btnDismiss.className = 'btn-icon';
      btnDismiss.innerHTML = '✕';
      btnDismiss.title = 'Dismiss';
      btnDismiss.addEventListener('click', hide);

      footer.appendChild(btnAccept);
      footer.appendChild(btnCopy);
      footer.appendChild(spacer);
      footer.appendChild(btnDismiss);

      // Refinement input
      refineWrap.style.display = 'flex';
      refineInput.placeholder = t('refine_placeholder') || 'Ask for a change...';
      refineInput.value = '';

      function sendRefinement() {
        const curInput = root.getElementById('refine-input');
        const instruction = curInput ? curInput.value.trim() : '';
        if (!instruction) return;
        if (curInput) curInput.value = '';
        if (typeof callbacks.onRefine === 'function') callbacks.onRefine(instruction);
      }
      // Remove old listeners by cloning and update persistent refs
      const newSend = btnSend.cloneNode(true);
      btnSend.replaceWith(newSend);
      newSend.addEventListener('click', sendRefinement);
      const newInput = refineInput.cloneNode(true);
      refineInput.replaceWith(newInput);
      newInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); sendRefinement(); } });

      addEscapeListener();
    }

    return {
      showLoading,
      showResult,
      hide,
      setAnchorField(field) { anchorField = field; reposition(); },
      get state() { return state; },
    };
  }

  let singleton = null;
  window.getLomaResultCard = function () {
    if (!singleton) singleton = createCard();
    return singleton;
  };
})();
