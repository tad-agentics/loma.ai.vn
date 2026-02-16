/**
 * Loma result card — viewport-fixed overlay (UX Spec 3.4, v1.3).
 * Intent badge (14 intents), loading microcopy, "Show original", quality (Ngắn hơn X% or Đầy đủ hơn/Đúng format hành chính), [Dùng] [Sao chép] [Đổi giọng].
 */
(function () {
  const t = (key) => chrome.i18n.getMessage(key) || key;

  // Backend intent name → i18n message key (UX Spec 1.4)
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
  const QUICKPICK_INTENTS = [
    { key: 'ask_payment', i18n: 'intent_payment' }, { key: 'follow_up', i18n: 'intent_followup' }, { key: 'say_no', i18n: 'intent_decline' },
    { key: 'request_senior', i18n: 'intent_request' }, { key: 'cold_outreach', i18n: 'intent_cold_outreach' }, { key: 'give_feedback', i18n: 'intent_feedback' },
    { key: 'disagree', i18n: 'intent_disagree' }, { key: 'escalate', i18n: 'intent_escalate' }, { key: 'apologize', i18n: 'intent_apologize' },
    { key: 'ai_prompt', i18n: 'intent_ai_prompt' }, { key: 'write_to_gov', i18n: 'intent_gov_doc' },
    { key: 'write_formal_vn', i18n: 'intent_formal_vn' }, { key: 'write_report_vn', i18n: 'intent_report_vn' }, { key: 'write_proposal_vn', i18n: 'intent_proposal_vn' },
  ];

  function createCard() {
    const host = document.createElement('div');
    host.id = 'loma-result-card-host';
    host.style.cssText = 'position:fixed;inset:0;z-index:2147483647;display:none;align-items:center;justify-content:center;background:rgba(0,0,0,0.4);';
    document.body.appendChild(host);

    const root = host.attachShadow({ mode: 'open' });
    root.innerHTML = `
      <style>
        .backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; }
        .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); width: 420px; max-width: 90vw; max-height: 360px; display: flex; flex-direction: column; }
        .card-head { padding: 12px 16px; border-bottom: 1px solid #e5e7eb; font-weight: 600; color: #111; font-size: 14px; }
        .card-body { padding: 16px; overflow-y: auto; flex: 1; min-height: 0; }
        .card-foot { padding: 12px 16px; border-top: 1px solid #e5e7eb; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .skeleton-badge { height: 24px; width: 180px; border-radius: 9999px; margin-bottom: 12px; }
        .skeleton-line { height: 14px; border-radius: 4px; margin-bottom: 8px; }
        .skeleton-line.short { width: 60%; }
        .shimmer { background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%); background-size: 200% 100%; animation: loma-shimmer 1.2s ease-in-out infinite; }
        @keyframes loma-shimmer { to { background-position: 200% 0; } }
        @media (prefers-reduced-motion: reduce) { .shimmer { animation: none; background: #e5e7eb; } }
        .loading-microcopy { font-size: 14px; color: #6b7280; margin-bottom: 12px; }
        .text-block { white-space: pre-wrap; word-break: break-word; margin-bottom: 12px; line-height: 1.5; color: #374151; font-size: 14px; }
        .orig-block { font-size: 12px; color: #6b7280; margin-bottom: 12px; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
        .toggle { background: none; border: none; color: #0d9488; cursor: pointer; font-size: 13px; padding: 4px 0; margin-bottom: 8px; }
        .toggle:hover { text-decoration: underline; }
        .toggle:focus-visible { outline: 2px solid #0d9488; outline-offset: 2px; }
        .meta { font-size: 12px; color: #6b7280; margin-bottom: 12px; }
        .quickpick { margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb; }
        .quickpick-title { font-size: 13px; font-weight: 500; color: #374151; margin-bottom: 8px; }
        .quickpick-btns { display: flex; flex-wrap: wrap; gap: 6px; }
        .btn-quickpick { padding: 6px 12px; border-radius: 6px; border: 1px solid #d1d5db; background: #fff; font-size: 12px; cursor: pointer; color: #374151; }
        .btn-quickpick:hover { background: #f3f4f6; }
        .btn-quickpick:focus-visible { outline: 2px solid #0d9488; outline-offset: 2px; }
        .btn { padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer; font-size: 14px; font-weight: 500; }
        .btn:focus-visible { outline: 2px solid #0d9488; outline-offset: 2px; }
        .btn-use { background: #0d9488; color: #fff; }
        .btn-use:hover { background: #0f766e; }
        .btn-copy { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }
        .btn-copy:hover { background: #e5e7eb; }
        .btn-disabled { opacity: 0.5; pointer-events: none; }
        .btn-tone { background: none; color: #0d9488; border: none; cursor: pointer; font-size: 13px; padding: 8px 0; }
        .btn-tone:hover { text-decoration: underline; }
        .tone-popover { position: absolute; bottom: 100%; left: 0; margin-bottom: 4px; background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.12); padding: 10px; min-width: 200px; z-index: 10; }
        .tone-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
        .tone-row:last-child { margin-bottom: 0; }
        .tone-lang-row { border-top: 1px solid #e5e7eb; padding-top: 8px; margin-top: 4px; }
        .tone-btn { padding: 4px 10px; border-radius: 6px; border: 1px solid #d1d5db; background: #fff; font-size: 12px; cursor: pointer; color: #374151; }
        .tone-btn:hover { background: #f3f4f6; }
        .toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #111; color: #fff; padding: 10px 20px; border-radius: 8px; font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); opacity: 0; transition: opacity 0.2s; pointer-events: none; }
        .toast.show { opacity: 1; }
      </style>
      <div class="backdrop" id="backdrop">
        <div class="card" id="card">
          <div class="card-head" id="head">Loma</div>
          <div class="card-body" id="body"></div>
          <div class="card-foot" id="foot" style="display:none;"></div>
        </div>
      </div>
      <div class="toast" id="toast"></div>
    `;

    const body = root.getElementById('body');
    const foot = root.getElementById('foot');
    const backdrop = root.getElementById('backdrop');
    const toastEl = root.getElementById('toast');

    let state = 'hidden'; // 'hidden' | 'loading' | 'result'
    let currentData = null;
    let callbacks = null;

    function hide() {
      host.style.display = 'none';
      state = 'hidden';
      currentData = null;
      callbacks = null;
      removeEscapeListener();
    }

    function onEscape(e) {
      if (e.key === 'Escape') hide();
    }
    function addEscapeListener() {
      removeEscapeListener();
      document.addEventListener('keydown', onEscape);
    }
    function removeEscapeListener() {
      document.removeEventListener('keydown', onEscape);
    }

    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) hide();
    });

    function showLoading(detectedIntent) {
      state = 'loading';
      host.style.display = 'flex';
      const loadKey = (INTENT_TO_LOADING[detectedIntent] || 'loading_generic');
      const loadMsg = t(loadKey);
      body.innerHTML = `
        <div class="skeleton-badge shimmer"></div>
        <div class="loading-microcopy">${loadMsg}</div>
        <div class="skeleton-line shimmer" style="width:100%"></div>
        <div class="skeleton-line shimmer short"></div>
        <div class="skeleton-line shimmer" style="width:85%"></div>
      `;
      foot.style.display = 'flex';
      foot.innerHTML = '<button type="button" class="btn btn-use btn-disabled" disabled>'+t('btn_use')+'</button><button type="button" class="btn btn-copy btn-disabled" disabled>'+t('btn_copy')+'</button>';
      addEscapeListener();
    }

    function showToast(message) {
      toastEl.textContent = message;
      toastEl.classList.add('show');
      setTimeout(() => toastEl.classList.remove('show'), 2000);
    }

    function showResult(data, cbs) {
      state = 'result';
      currentData = data;
      callbacks = cbs || {};
      const output = (data.output_text || '').trim();
      const original = (data.original_text || data.input_text || '').trim();
      const pct = data.scores && data.scores.length_reduction_pct != null ? data.scores.length_reduction_pct : null;
      const outputLang = data.output_language || 'en';

      const headEl = root.getElementById('head');
      const intentLabel = t(INTENT_TO_I18N[data.detected_intent] || 'intent_other');
      headEl.textContent = intentLabel;

      const showOrigId = 'loma-show-orig';
      let showingOriginal = false;
      const toggleLabel = () => (showingOriginal ? t('hide_original') : t('show_original'));

      const toggleBtn = document.createElement('button');
      toggleBtn.type = 'button';
      toggleBtn.className = 'toggle';
      toggleBtn.id = showOrigId;
      toggleBtn.textContent = toggleLabel();
      toggleBtn.addEventListener('click', () => {
        showingOriginal = !showingOriginal;
        toggleBtn.textContent = toggleLabel();
        origBlock.style.display = showingOriginal ? 'block' : 'none';
      });

      const textBlock = document.createElement('div');
      textBlock.className = 'text-block';
      textBlock.textContent = output;

      const origBlock = document.createElement('div');
      origBlock.className = 'orig-block';
      origBlock.style.display = 'none';
      origBlock.textContent = original;

      const meta = document.createElement('div');
      meta.className = 'meta';
      if (outputLang === 'vi_admin') meta.textContent = t('quality_format_admin');
      else if (outputLang && outputLang.startsWith('vi_') && pct != null && pct < 0) meta.textContent = t('quality_more_complete');
      else if (pct != null) meta.textContent = chrome.i18n.getMessage('quality_shorter', [String(Math.round(pct))]) || ('Ngắn hơn ' + Math.round(pct) + '%');
      else meta.textContent = '';

      body.innerHTML = '';
      body.appendChild(textBlock);
      body.appendChild(toggleBtn);
      body.appendChild(origBlock);
      body.appendChild(meta);

      const confidence = data.intent_confidence != null ? data.intent_confidence : 1;
      const showQuickPick = (confidence < 0.5 || (data.detected_intent === 'general' && confidence < 0.7)) && typeof callbacks.onIntentPick === 'function';
      if (showQuickPick) {
        const qp = document.createElement('div');
        qp.className = 'quickpick';
        qp.innerHTML = '<div class="quickpick-title">' + t('quickpick_title') + '</div>';
        const qpBtns = document.createElement('div');
        qpBtns.className = 'quickpick-btns';
        QUICKPICK_INTENTS.slice(0, 3).forEach(({ key, i18n }) => {
          const b = document.createElement('button');
          b.type = 'button';
          b.className = 'btn-quickpick';
          b.textContent = t(i18n);
          b.addEventListener('click', () => callbacks.onIntentPick(key));
          qpBtns.appendChild(b);
        });
        const otherBtn = document.createElement('button');
        otherBtn.type = 'button';
        otherBtn.className = 'btn-quickpick';
        otherBtn.textContent = t('intent_other');
        otherBtn.addEventListener('click', () => { /* keep current result */ });
        qpBtns.appendChild(otherBtn);
        qp.appendChild(qpBtns);
        body.appendChild(qp);
      }

      const btnUse = document.createElement('button');
      btnUse.type = 'button';
      btnUse.className = 'btn btn-use';
      btnUse.textContent = t('btn_use');
      btnUse.addEventListener('click', () => {
        if (typeof callbacks.onUse === 'function') callbacks.onUse();
        hide();
      });

      const btnCopy = document.createElement('button');
      btnCopy.type = 'button';
      btnCopy.className = 'btn btn-copy';
      btnCopy.textContent = t('btn_copy');
      btnCopy.addEventListener('click', () => {
        if (output && navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(output).then(() => showToast(t('copied_toast')));
        }
        if (typeof callbacks.onCopy === 'function') callbacks.onCopy();
      });

      const footEl = root.getElementById('foot');
      const toneWrap = document.createElement('div');
      toneWrap.style.position = 'relative';
      const btnTone = document.createElement('button');
      btnTone.type = 'button';
      btnTone.className = 'btn-tone';
      btnTone.textContent = t('btn_tone');
      btnTone.addEventListener('click', (e) => {
        e.stopPropagation();
        const pop = root.getElementById('loma-tone-popover');
        if (pop) { pop.remove(); return; }
        const popover = document.createElement('div');
        popover.id = 'loma-tone-popover';
        popover.className = 'tone-popover';
        const enTones = [{ tone: 'direct', i18n: 'tone_direct' }, { tone: 'softer', i18n: 'tone_softer' }, { tone: 'shorter', i18n: 'tone_shorter' }, { tone: 'formal', i18n: 'tone_formal' }];
        const vnTones = [{ tone: 'vi_casual', i18n: 'tone_vn_casual' }, { tone: 'vi_formal', i18n: 'tone_vn_formal' }, { tone: 'vi_admin', i18n: 'tone_vn_admin' }];
        const row1 = document.createElement('div');
        row1.className = 'tone-row';
        enTones.forEach(({ tone, i18n }) => {
          const b = document.createElement('button');
          b.type = 'button';
          b.className = 'tone-btn';
          b.textContent = t(i18n);
          b.addEventListener('click', () => { if (typeof callbacks.onToneChange === 'function') callbacks.onToneChange(tone, 'en'); popover.remove(); });
          row1.appendChild(b);
        });
        const row2 = document.createElement('div');
        row2.className = 'tone-row';
        vnTones.forEach(({ tone, i18n }) => {
          const b = document.createElement('button');
          b.type = 'button';
          b.className = 'tone-btn';
          b.textContent = t(i18n);
          b.addEventListener('click', () => { if (typeof callbacks.onToneChange === 'function') callbacks.onToneChange(tone, tone); popover.remove(); });
          row2.appendChild(b);
        });
        const langRow = document.createElement('div');
        langRow.className = 'tone-row tone-lang-row';
        const enLang = document.createElement('button');
        enLang.type = 'button';
        enLang.className = 'tone-btn';
        enLang.textContent = t('tone_lang_en');
        enLang.addEventListener('click', () => { if (typeof callbacks.onToneChange === 'function') callbacks.onToneChange('professional', 'en'); popover.remove(); });
        const viLang = document.createElement('button');
        viLang.type = 'button';
        viLang.className = 'tone-btn';
        viLang.textContent = t('tone_lang_vi');
        viLang.addEventListener('click', () => { if (typeof callbacks.onToneChange === 'function') callbacks.onToneChange('vi_formal', 'vi_formal'); popover.remove(); });
        langRow.appendChild(enLang);
        langRow.appendChild(viLang);
        popover.appendChild(row1);
        popover.appendChild(row2);
        popover.appendChild(langRow);
        toneWrap.appendChild(popover);
        document.addEventListener('click', function closePopover() {
          if (!popover.contains(document.activeElement)) { popover.remove(); document.removeEventListener('click', closePopover); }
        }, 0);
      });
      toneWrap.appendChild(btnTone);

      footEl.innerHTML = '';
      footEl.appendChild(btnUse);
      footEl.appendChild(btnCopy);
      footEl.appendChild(toneWrap);
      footEl.style.display = 'flex';
      addEscapeListener();
    }

    return {
      showLoading,
      showResult,
      hide,
      get state() { return state; },
    };
  }

  let singleton = null;
  window.getLomaResultCard = function () {
    if (!singleton) singleton = createCard();
    return singleton;
  };
})();
