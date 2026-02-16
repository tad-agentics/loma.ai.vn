/**
 * <loma-button> — Shadow DOM custom element (UX Spec 3.1).
 * Shown when Vietnamese is detected in the field. On click: send text to API, show result card.
 */
(function () {
  const template = document.createElement('template');
  template.innerHTML = `
    <style>
      :host {
        position: absolute;
        bottom: 8px;
        right: 8px;
        z-index: 2147483646;
      }
      :host([grammarly-offset]) {
        right: 52px;
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
      this._onClick = this._onClick.bind(this);
    }

    connectedCallback() {
      this._btn.setAttribute('aria-label', chrome.i18n.getMessage('aria_button') || 'Rewrite with Loma');
      this._btn.addEventListener('click', this._onClick);
    }

    disconnectedCallback() {
      this._btn.removeEventListener('click', this._onClick);
    }

    setField(el) {
      this._field = el;
    }

    _getText() {
      if (!this._field) return '';
      const tag = (this._field.tagName || '').toLowerCase();
      if (tag === 'textarea' || tag === 'input') return (this._field.value || '').trim();
      return (this._field.innerText || this._field.textContent || '').trim();
    }

    _onClick() {
      const text = this._getText();
      if (!text || text.length < 10) return;
      this.dispatchEvent(new CustomEvent('loma-rewrite', { detail: { text }, bubbles: true }));
    }

    setLoading(loading) {
      if (this._btn) this._btn.classList.toggle('loading', !!loading);
    }
  }
  customElements.define('loma-button', LomaButton);
})();
