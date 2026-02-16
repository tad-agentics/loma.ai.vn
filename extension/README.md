# Loma Chrome Extension

Manifest V3 extension. Shows a Loma button in text fields when Vietnamese is detected; on click, sends text to the rewrite API and replaces the field with the result.

## Setup

1. **Backend**: Run the local API server so the extension can call the rewrite API:
   ```bash
   cd backend && pip install -r requirements.txt && python server.py
   ```
   Server runs at `http://127.0.0.1:3000`. Put `ANTHROPIC_API_KEY` in `backend/.env` for real rewrites.

2. **API URL**: The extension uses `chrome.storage.local.loma_api_base` (default `http://localhost:3000`). Change it in the popup if your server uses another port or host.

3. **Load unpacked**: Chrome → Extensions → Load unpacked → select the `extension` folder.

4. **Test**: Open `extension/test_page.html` in Chrome (or any page with a textarea). Type 10+ characters of Vietnamese; the Loma button appears. Click it to rewrite.

## Structure

- `manifest.json` — Manifest V3, content scripts, background service worker, popup, tabs (FTUX)
- `background.js` — Service worker; API base, stats; on install opens `welcome.html`
- `content/detection.js` — `containsVietnamese()`, `computeLanguageMix()`, `getPlatform()`, `getOutputLanguage(cb)`, `setOutputLanguageForDomain()`, `detectGrammarly()`
- `content/loma-button.js` — `<loma-button>` (Shadow DOM); `grammarly-offset` attribute when Grammarly present
- `content/result-card.js` — Result card: intent badge (14 intents), loading by intent, quality (Ngắn hơn X% / Đầy đủ hơn / Đúng format hành chính), [Dùng] [Sao chép] [Đổi giọng] with tone selector (4 EN + 3 VN formality + [English] [Tiếng Việt])
- `content/text-isolation.js` — Gmail boundaries; replaceUserText
- `content/content.js` — Scans fields, injects button, calls API with `output_language`, `tone`; onToneChange stores per-domain and re-requests
- `_locales/vi`, `_locales/en` — Full i18n (UX Spec 1.4): intents, loading, tone, quality, FTUX
- `popup/` — Popup with API URL, stats, per-site toggle
- `welcome.html` + `welcome.js` — FTUX tab on first install (both EN and VN output examples)

## Flow

1. Content script scans for text fields; `containsVietnamese(text)` and height ≥38px → show `<loma-button>`. If Grammarly detected, button offset 44px left.
2. `getOutputLanguage(cb)` reads per-domain preference or .gov.vn → vi_admin; payload includes `output_language`, `tone`.
3. User clicks → POST `/api/v1/rewrite` → result card shows intent badge, rewrite, quality, [Dùng] [Sao chép] [Đổi giọng].
4. [Đổi giọng] opens tone/language selector; choice is stored per domain and rewrite is re-requested with new tone/output_language.
5. [Dùng] replaces field (with text isolation on Gmail); 5s undo toast.
