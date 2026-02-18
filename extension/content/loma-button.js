/**
 * <loma-button> — Shadow DOM custom element (UX Spec 3.1).
 * Shown when Vietnamese is detected in the field. On click: send text to API, show result card.
 *
 * Positioned with position:fixed on document.body so it is never clipped by
 * Gmail/Outlook overflow:hidden containers. Call reposition() or let the
 * built-in listeners keep it anchored to the bottom-right of its field.
 */
(function () {
  const template = document.createElement('template');
  template.innerHTML = `
    <style>
      :host {
        position: fixed;
        z-index: 2147483646;
        pointer-events: auto;
      }
      button {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        border: none;
        background: #0d9488;
        color: white;
        cursor: pointer;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: background 0.15s ease, transform 0.15s ease, box-shadow 0.2s ease;
      }
      button:hover { background: #0f766e; }
      button:active { transform: scale(0.96); }
      button:focus-visible { outline: 2px solid #0d9488; outline-offset: 2px; }
      button.loading {
        box-shadow: 0 2px 12px rgba(13,148,136,0.35);
        pointer-events: none;
      }
      @media (prefers-reduced-motion: reduce) {
        button.loading { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
      }
    </style>
    <button type="button" aria-label="">L</button>
  `;

  class LomaButton extends HTMLElement {
    static get is() { return 'loma-button'; }
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
      this.shadowRoot.appendChild(template.content.cloneNode(true));
      this._btn = this.shadowRoot.querySelector('button');
      this._field = null;
      this._grammarlyOffset = false;
      this._onClick = this._onClick.bind(this);
      this._reposition = this.reposition.bind(this);
      this._rafId = null;
    }

    connectedCallback() {
      this._btn.setAttribute('aria-label', chrome.i18n.getMessage('aria_button') || 'Rewrite with Loma');
      this._btn.addEventListener('click', this._onClick);
      window.addEventListener('scroll', this._reposition, true);
      window.addEventListener('resize', this._reposition);
      this.reposition();
    }

    disconnectedCallback() {
      this._btn.removeEventListener('click', this._onClick);
      window.removeEventListener('scroll', this._reposition, true);
      window.removeEventListener('resize', this._reposition);
      if (this._rafId) cancelAnimationFrame(this._rafId);
    }

    setField(el) {
      this._field = el;
      this.reposition();
    }

    /** Re-anchor to the bottom-right corner of the associated field. */
    reposition() {
      if (this._rafId) cancelAnimationFrame(this._rafId);
      this._rafId = requestAnimationFrame(() => {
        if (!this._field) return;
        const rect = this._field.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) {
          // Field is hidden — hide ourselves too
          this.style.display = 'none';
          return;
        }
        this.style.display = '';
        const rightOffset = this._grammarlyOffset ? 52 : 8;
        this.style.top = (rect.bottom - 8 - 36) + 'px';   // 8px from bottom, 36px button height
        this.style.left = (rect.right - rightOffset - 36) + 'px';
      });
    }

    setGrammarlyOffset(offset) {
      this._grammarlyOffset = !!offset;
      this.reposition();
    }

    _getText() {
      if (!this._field) return '';
      const tag = (this._field.tagName || '').toLowerCase();
      if (tag === 'textarea' || tag === 'input') return (this._field.value || '').trim();
      return (this._field.innerText || this._field.textContent || '').trim();
    }

    _onClick() {
      const text = this._getText();
      if (!text || text.length < 5) return;
      this.dispatchEvent(new CustomEvent('loma-rewrite', { detail: { text }, bubbles: true }));
    }

    setLoading(loading) {
      if (this._btn) this._btn.classList.toggle('loading', !!loading);
    }
  }
  if (typeof customElements !== 'undefined' && !customElements.get('loma-button')) {
    customElements.define('loma-button', LomaButton);
  }
})();
