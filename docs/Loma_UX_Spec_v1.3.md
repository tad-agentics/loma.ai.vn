# Loma — UX Specification

**Version:** 1.3
**Date:** February 2026
**Companion to:** Tech Spec v1.5
**Purpose:** Every interaction design decision that drives the Chrome extension engineering.
**Product rename:** GlobalPro → Loma (effective v1.2)
**Positioning:** Hết loay hoay với câu chữ. Bạn lo phần ý. Loma lo phần lời.

**Changelog v1.2 → v1.3:**
- **Dual-language output:** Loma now produces both English and formal Vietnamese output. Auto-detects output language based on recipient context. Sections 1.1, 1.4, 3.4, 3.5, 3.8 updated.
- **Vietnamese formality levels:** Tone selector expanded with 3 Vietnamese formality levels (thân mật / trang trọng / hành chính) alongside existing 4 English tones. Section 3.8 updated.
- **New Vietnamese intents:** Added `write_to_gov`, `write_formal_vn`, `write_report_vn`, `write_proposal_vn` for Vietnamese output contexts. Section 3.5 updated.
- **Output language routing:** New Section 2.6 — auto-detection logic based on recipient domain, platform, and input language. No manual toggle.
- **FTUX updated:** Onboarding screens now demo both English and Vietnamese output. Section 5.1 updated.
- **Positioning updated:** "Hết loay hoay với câu chữ. Bạn lo phần ý. Loma lo phần lời." replaces English-only positioning throughout.
- **String table expanded:** New keys for Vietnamese output mode, formality levels, and updated FTUX copy.

**Changelog v1.1 → v1.2:**
- **Renamed:** GlobalPro → Loma throughout (button, events, DOM elements, FTUX, popup)
- **[S1] Vietnamese-first UI:** All extension UI defaults to Vietnamese when browser language is `vi`. New Section 1.4 with full string table.
- **[S3] Code-switching support:** Mixed Vietnamese-English input recognized as primary input pattern. New Section 2.5 with detection, preservation, and intent heuristic implications.
- **[S4] Before/after comparison:** "Show original" toggle added to result card. Section 3.4 updated.
- **[S5] Copy flow data gap:** Acknowledged with mitigation strategy in Section 4.3 and analytics.
- **Scale architecture:** Added Section 14 (Phase 2-3 Scale Concepts) covering: recipient context, express mode, rewrite history, enterprise, visible flywheel, and viral mechanics.

**Previous changelog (v1.0 → v1.1):** Fixed text isolation for Gmail threads (P0), replaced Clarity/Authority scores with validated-only metrics (P0), marked confidence split as hypothesis (P0), fixed card positioning to viewport-fixed (P1), replaced [Edit] with [Copy] at launch (P1), added post-install onboarding tab (P1), fixed keyboard shortcut conflict (P1), added extension popup spec (P2), moved Grammarly analysis to appendix, capped quick-pick at 3 options, removed mobile responsive section, added free-trial auth decision, added 5-second undo toast for [Use] action (P1), added ARIA live regions (P1), fixed teal contrast for small text, specified visible focus indicators for Shadow DOM, added FTUX exit feedback, added contextual microcopy during loading state, added intent frequency bias to Phase 2 roadmap.

---

## 1. Interaction Model

### 1.1 Core Mental Model: "One Button, Full Transform"

Grammarly's mental model: "Your writing has errors. We'll show you each one."
Loma's mental model: **"You've written something. We'll produce the version your recipient needs to hear."**

This is not a correction tool. It's a transformation tool. English email to a client? Loma produces native-level English. Công văn to a government agency? Loma produces correctly formatted formal Vietnamese. The UX should feel like having a senior colleague rewrite your draft — not a teacher marking your errors.

```
User writes something → taps ONE button → gets the right version 
in the right language for the right audience → uses it

That's the entire product in one sentence.
```

**Output language auto-detection:** Loma determines the output language from recipient context (see Section 2.6). The user never picks a language mode. They just write.

### 1.2 The Three States

At any moment, Loma's UI is in exactly one of three states:

```
STATE 1: DORMANT
   The Loma button is visible but idle.
   User hasn't triggered a rewrite.
   Visual: Small, unobtrusive icon.

STATE 2: ACTIVE
   User tapped the button. Rewrite is processing.
   Visual: Button pulses/animates. Result card appears.

STATE 3: RESULT
   Rewrite is complete. User decides: use, copy, or dismiss.
   Visual: Result card with full rewrite + quality signal.
```

No other states. No "scanning your text" spinner. No "3 errors found" badge. No ambient underlines. The extension is either waiting, working, or showing a result.

### 1.3 What We Deliberately Do NOT Build

These are informed by Grammarly's 16-year evolution (see Appendix A for full competitive analysis).

| Pattern | Why We Skip It |
|---|---|
| **Real-time grammar underlines** | Not our product. We don't check grammar — we transform communication. Underlines = "you made mistakes." Loma = "let me write this for you." |
| **Multiple icons in text field** (Grammarly's G + lightbulb + pencil) | Confusing. We have ONE purpose. ONE button. ONE flow. |
| **Prompt text input for rewrite** | Our users can't articulate what they want in English. The whole point is that the system knows. Intent detection replaces prompting. |
| **Error counting / per-word suggestions** | We're not counting errors or fixing words. We're producing a complete rewrite. The mental model is "transform" not "fix." |
| **Agentic side panel** (Grammarly Go/Superhuman) | Feature bloat. Not our product at launch. |

### 1.4 Vietnamese-First UI Language

**The extension's own interface defaults to Vietnamese when the browser language is `vi`.** This is core product-market fit, not internationalization.

The target user is a Vietnamese professional who can't write professional English. Many of these users also can't read English UI fluently. Every English label in the extension adds cognitive load to the exact people we're trying to reduce cognitive load for. A Vietnamese-first product with an English-only interface is a contradiction.

**Detection:** `navigator.language.startsWith('vi')` → Vietnamese UI. All other languages → English UI. User can override in popup settings.

**String table (Phase 1 — all user-facing strings):**

| Key | Vietnamese (default for `vi`) | English (fallback) |
|---|---|---|
| `quickpick_title` | Bạn muốn làm gì? | What are you trying to do? |
| `intent_payment` | 💰 Nhắc thanh toán | 💰 Ask payment |
| `intent_followup` | 🔄 Theo dõi | 🔄 Follow up |
| `intent_decline` | 🚫 Từ chối | 🚫 Decline |
| `intent_request` | 📋 Yêu cầu | 📋 Request |
| `intent_cold_outreach` | 🤝 Giới thiệu | 🤝 Cold outreach |
| `intent_feedback` | 💬 Góp ý | 💬 Give feedback |
| `intent_disagree` | ⚡ Không đồng ý | ⚡ Disagree |
| `intent_escalate` | 🔺 Chuyển cấp trên | 🔺 Escalate |
| `intent_apologize` | 🙏 Xin lỗi | 🙏 Apologize |
| `intent_ai_prompt` | 🤖 Prompt AI | 🤖 AI prompt |
| `intent_gov_doc` | 📜 Văn bản hành chính | 📜 Government document |
| `intent_formal_vn` | 📝 Email trang trọng | 📝 Formal Vietnamese |
| `intent_report_vn` | 📊 Báo cáo | 📊 Report |
| `intent_proposal_vn` | 💼 Đề xuất | 💼 Proposal |
| `intent_other` | Khác... | Other... |
| `btn_use` | ✓ Dùng | ✓ Use |
| `btn_copy` | 📋 Sao chép | 📋 Copy |
| `btn_tone` | ↻ Đổi giọng | ↻ Different tone |
| `tone_direct` | Trực tiếp hơn | More direct |
| `tone_softer` | Nhẹ nhàng hơn | Softer |
| `tone_shorter` | Ngắn gọn hơn | Shorter |
| `tone_formal` | Trang trọng hơn | More formal |
| `tone_vn_casual` | Thân mật | Collegial |
| `tone_vn_formal` | Trang trọng | Formal |
| `tone_vn_admin` | Hành chính | Administrative |
| `undo_toast` | ✓ Đã thay văn bản | ✓ Text replaced |
| `undo_btn` | Hoàn tác | Undo |
| `copied_toast` | Đã sao chép! | Copied! |
| `show_original` | Xem bản gốc | Show original |
| `hide_original` | Ẩn bản gốc | Hide original |
| `loading_generic` | Đang viết lại... | Rewriting... |
| `loading_payment` | Đang viết nhắc thanh toán... | Rewriting as a payment follow-up... |
| `loading_followup` | Đang viết theo dõi chuyên nghiệp... | Writing a professional follow-up... |
| `loading_decline` | Đang soạn từ chối lịch sự... | Drafting a polite decline... |
| `loading_outreach` | Đang soạn giới thiệu chuyên nghiệp... | Crafting a professional introduction... |
| `loading_feedback` | Đang viết góp ý xây dựng... | Framing constructive feedback... |
| `loading_disagree` | Đang diễn đạt không đồng ý... | Expressing disagreement professionally... |
| `loading_escalate` | Đang viết chuyển cấp trên... | Writing an escalation with context... |
| `loading_apologize` | Đang soạn lời xin lỗi... | Drafting a sincere apology... |
| `loading_ai_prompt` | Đang tinh chỉnh prompt... | Refining your prompt... |
| `loading_request` | Đang viết yêu cầu rõ ràng... | Making this respectful and clear... |
| `loading_gov_doc` | Đang soạn văn bản hành chính... | Formatting as official document... |
| `loading_formal_vn` | Đang viết lại trang trọng hơn... | Rewriting in formal Vietnamese... |
| `loading_report_vn` | Đang soạn báo cáo... | Structuring your report... |
| `loading_proposal_vn` | Đang soạn đề xuất... | Drafting your proposal... |
| `error_timeout` | Lâu hơn bình thường... | Taking longer than usual... |
| `error_failed` | Có lỗi xảy ra. | Something went wrong. |
| `error_retry` | Thử lại | Try again |
| `error_offline` | Không có kết nối mạng. | No internet connection. |
| `error_too_long` | Đang viết lại 2000 ký tự đầu. | Rewriting the first 2000 characters. |
| `trial_exhausted` | Bạn đã dùng hết lượt miễn phí. | You've used your free rewrites. |
| `trial_add_credit` | Nạp tiền | Add credit |
| `trial_signin_prompt` | Đăng nhập Google để lưu kết quả | Sign in with Google to save your rewrites |
| `trial_signin_more` | Đăng nhập để nhận thêm 5 lượt miễn phí. | Sign in to get 5 more free rewrites. |
| `ftux_screen1` | Hết loay hoay với câu chữ. | No more struggling with words. |
| `ftux_screen2` | Tiếng Anh hay tiếng Việt — một nút, đúng giọng. | English or Vietnamese — one button, right voice. |
| `ftux_screen3` | Thử ngay — 5 lượt viết lại miễn phí | Try it now — 5 free rewrites |
| `ftux_tooltip` | Viết xong rồi bấm vào đây | Write something, then tap here |
| `ftux_exit_q` | Điều gì khiến bạn dừng lại? | What stopped you? |
| `ftux_exit_browsing` | Chỉ xem thử | Just browsing |
| `ftux_exit_notneed` | Không phải thứ tôi cần | Not what I need |
| `ftux_exit_later` | Để sau | I'll try later |
| `popup_enable` | Bật trên trang này | Enable on this site |
| `popup_show_btn` | Hiện nút Loma | Show Loma button |
| `popup_kbd_only` | Chỉ dùng phím tắt | Keyboard shortcut only |
| `popup_manage` | Quản lý tài khoản | Manage account |
| `popup_signout` | Đăng xuất | Sign out |
| `popup_rewrites_today` | Lượt viết hôm nay | Rewrites today |
| `popup_rewrites_month` | Lượt viết tháng này | Rewrites this month |
| `popup_remaining` | còn lại | remaining |
| `isolation_notice` | Đã viết lại toàn bộ tin nhắn. Chọn văn bản cụ thể để viết lại một phần. | We rewrote your full message. Select specific text to rewrite just a portion. |
| `quality_shorter` | Ngắn hơn {n}% | {n}% shorter |
| `aria_button` | Viết lại với Loma | Rewrite with Loma |
| `aria_card` | Kết quả viết lại | Rewrite result |
| `aria_quickpick` | Chọn mục đích tin nhắn | Choose the intent of your message |

**Implementation:** Single `i18n.js` module. All user-facing strings reference keys, never hardcoded text. Chrome's `chrome.i18n` API can be used, but a simpler approach is a runtime lookup: `const t = (key) => strings[locale][key] || strings['en'][key]`.

**What is NOT translated:** The rewrite output language is determined by recipient context (see Section 2.6), not by the UI language. The UI is always Vietnamese for `vi` browsers. The output may be English or formal Vietnamese depending on context. The intent badge in the result card shows the intent name in both languages: "💰 Nhắc thanh toán · Payment follow-up" (English output) or "📜 Văn bản hành chính · Government document" (Vietnamese output).

---

## 2. Text Isolation Strategy

**This is the hardest UX problem in the spec.** The product assumes "user writes in a text field → Loma rewrites the content." But real text fields are messy:

### 2.1 The Problem

Gmail compose with a reply thread (our #1 use case, estimated 50%+ of all rewrites):

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  anh Minh ơi, invoice tháng 1 chưa thanh toán  │ ← User's new text (REWRITE THIS)
│                                                 │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│                                                 │
│  Best regards,                                  │ ← Signature (DON'T TOUCH)
│  Duc Nguyen | Product Manager                   │
│                                                 │
│  On Feb 10, Minh wrote:                         │ ← Quoted thread (DON'T TOUCH)
│  > Thanks for the update. Can you send...       │
│  > the invoice details when ready?              │
│                                                 │
└─────────────────────────────────────────────────┘
```

If Loma rewrites the entire field, it nukes the signature, quoted thread, and any inline images. This breaks the #1 use case.

### 2.2 The Solution: Smart Boundary Detection

Loma must identify what the user actually wrote vs. what was already in the field. Detection strategy, in priority order:

**Strategy A: Gmail-specific boundary detection (covers ~60% of rewrites)**

Gmail inserts specific DOM markers for reply threads and signatures:

```javascript
// Gmail quoted reply: <div class="gmail_quote"> or <blockquote>
// Gmail signature: <div class="gmail_signature"> or the -- marker
// Forwarded content: "---------- Forwarded message ----------"

function extractUserText(composeElement) {
  const clone = composeElement.cloneNode(true);

  // Remove known boundary elements
  clone.querySelectorAll('.gmail_quote, blockquote, .gmail_signature').forEach(el => el.remove());

  // Remove everything after "-- " signature marker (plain text)
  const text = clone.textContent;
  const sigIndex = text.indexOf('\n-- \n');
  if (sigIndex > -1) return text.substring(0, sigIndex).trim();

  return text.trim();
}
```

**Strategy B: Generic heuristic boundary detection (covers remaining ~40%)**

For non-Gmail platforms or when Gmail markers aren't found:

```
1. Find the first occurrence of any of these patterns:
   - ">" at start of line (quoted text)
   - "On [date], [name] wrote:" 
   - "---------- Forwarded message ----------"
   - "From: " followed by email header patterns
   - "---" or "-- " (signature markers)
   - "Best regards," / "Sincerely," / "Thanks," followed by a name

2. Everything ABOVE the first boundary = user text (rewrite this)
3. Everything AT and BELOW the boundary = preserve untouched
```

**Strategy C: Fallback — full field rewrite**

For simple textareas (GitHub comment, Slack message, generic form fields) with no reply thread or signature patterns detected: rewrite the entire field content. This is the correct behavior for these simpler cases.

### 2.3 How [✓ Use] Works With Boundaries

When the user taps [Use], the replacement logic differs by field type:

| Field Type | Replacement Logic |
|---|---|
| **Gmail compose (reply)** | Replace only the user-text portion above the boundary. Preserve signature, quoted thread, and all DOM structure below. |
| **Gmail compose (new)** | Replace everything above the signature (if present). Preserve signature. |
| **Simple textarea** | Replace `.value` entirely. |
| **Generic contenteditable** | Replace `textContent` up to first detected boundary. If no boundary, replace all. |

**Implementation note:** For contenteditable fields, we must preserve DOM nodes (images, formatting, links) in the preserved section. The replacement targets only the text nodes in the user-written portion, not the entire `innerHTML`. This requires Range-based replacement, not full content swap.

### 2.4 Validation Requirement (Week 1-2 Spike)

Before building the full result card, **the text isolation logic must be tested against 20 real-world scenarios:**

- Gmail reply (short thread, long thread, nested replies)
- Gmail forward
- Gmail new message with signature
- Gmail new message without signature
- Slack message (no boundaries expected)
- GitHub PR comment (no boundaries expected)
- LinkedIn message
- Generic form textarea

**Gate:** Text isolation correctly extracts user-written text in ≥18/20 test cases. If it fails, the fallback is requiring text selection (user highlights what they want rewritten before tapping Loma). This is less magical but safe.

### 2.5 Code-Switching: Mixed Vietnamese-English Input

**This is the primary input pattern, not an edge case.** Vietnamese professionals under 40 code-switch constantly:

```
"Anh Minh ơi, cái KPI report Q4 đã review chưa? 
Cần submit cho board meeting next Tuesday. 
Budget projection cần update lại theo new headcount plan."
```

This message is ~40% English by word count. This is how the target market actually writes. The spec must handle this as the dominant case.

**Language detection:** The Loma button should appear when the text field contains **any Vietnamese content** — not "Vietnamese OR English" as separate categories. Detection rule: if ≥3 Vietnamese-specific characters (ă, ơ, ư, đ, ê, ô, á, à, ả, ã, ạ, etc.) or ≥2 Vietnamese function words (ơi, ạ, nhé, nha, đã, đang, sẽ, chưa, rồi, cái, của, cho, với) appear in the text, treat as Vietnamese-containing input. This fires the Loma button even for heavily code-switched text.

**Intent detection with code-switched input:** The heuristic intent detector (Tech Spec v1.3) uses Vietnamese keywords for intent classification. Code-switched text may dilute Vietnamese keyword density. Mitigation:

```
1. Run intent keywords against the full text (Vietnamese + English words)
2. Add English business equivalents to the keyword lists:
   - "invoice", "payment", "overdue" → payment follow-up
   - "deadline", "submit", "due" → follow-up
   - "sorry", "apologize", "mistake" → apologize
   - "feedback", "review", "comments" → give feedback
3. Confidence scoring weights Vietnamese keywords higher (1.5x)
   than English keywords (1.0x), because Vietnamese keywords
   show stronger intent signal in code-switched context
```

**Rewrite engine behavior with code-switched input:** The LLM prompt must instruct:

1. **Preserve standard English business terms** that appear in the original: "KPI report", "board meeting", "budget projection", "headcount plan" should carry through to the English rewrite as-is.
2. **Transform Vietnamese syntax and connector words** into English: "cần submit cho" → "needs to be submitted for", "đã review chưa" → "has this been reviewed".
3. **Do not translate English words that are already correct** — only restructure the sentence around them.

**Analytics:** Add `detected_language_mix` field to `loma_button_tapped` event: `{vietnamese_ratio: 0.6, english_ratio: 0.4}`. Track intent detection accuracy segmented by language mix ratio. If accuracy drops below 60% for texts with >40% English, the keyword lists need expansion.

### 2.6 Output Language Auto-Detection

**Loma determines the output language automatically. No manual toggle.**

The user should never think about which language they want the output in. Loma infers it from context. This keeps the "one button, one tap" mental model intact.

**Detection priority (first match wins):**

| Priority | Signal | Output | How detected |
|---|---|---|---|
| 1 | User explicitly selected a Vietnamese formality level (thân mật / trang trọng / hành chính) | Vietnamese | Tone selector state |
| 2 | User explicitly selected an English tone (direct / professional / warm / formal) | English | Tone selector state |
| 3 | Platform is a Vietnamese government portal (`.gov.vn` domain) | Vietnamese (hành chính) | `window.location.hostname` |
| 4 | Recipient email domain is `.gov.vn` | Vietnamese (hành chính) | Gmail compose DOM — recipient field parsing |
| 5 | Vietnamese formal keywords detected in input (`kính gửi`, `căn cứ`, `đề nghị`, `báo cáo`, `trân trọng`) | Vietnamese (trang trọng) | Keyword match in input text |
| 6 | Platform is a Vietnamese-only tool (Zalo Web, internal `.vn` corporate tools) | Vietnamese (thân mật) | `window.location.hostname` |
| 7 | Default | English | — |

**Key principle:** English output is the default. Vietnamese output only triggers when there's strong contextual evidence the recipient expects Vietnamese. This avoids surprising users who adopted Loma for English output.

**Recovery path:** If auto-detection is wrong, the tone selector (Đổi giọng) in the result card shows both English tones and Vietnamese formality levels. User taps the correct one. The system stores this per-domain preference for future rewrites.

**Per-domain memory:** After a manual override, store the preference in `chrome.storage.local`:

```json
{
  "domain_output_lang": {
    "mail.google.com/recipient:vn-gov@skhdt.hanoi.gov.vn": "vi_admin",
    "zalo.me": "vi_casual",
    "slack.com": "en"
  }
}
```

**UX behavior when Vietnamese output is detected:**

- Loading message changes: "Đang soạn văn bản hành chính..." instead of "Đang viết lại..."
- Intent badge shows Vietnamese intent: "📜 Văn bản hành chính" instead of "💰 Nhắc thanh toán · Payment follow-up"
- Tone selector shows Vietnamese formality levels instead of English tones
- Before/after toggle still works — shows original casual Vietnamese vs. formal Vietnamese output
- Quality signal still shows length change (formal Vietnamese is typically longer than casual input, so this may show "Đầy đủ hơn +40%" instead of "Ngắn hơn 52%")

---

## 3. Component Specifications

### 3.1 The Loma Button (Primary Entry Point)

Floating Loma icon in the lower-right corner of supported text fields. Shows nothing but the icon. Only appears when the text field has content and Vietnamese language is detected (per Section 2.5 rules).

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  [user's text input area]                       │
│                                                 │
│  anh ơi cái invoice tháng trước chưa thanh toán │
│                                                 │
│                                        [Loma]   │ ← lower-right corner
│                                                 │
└─────────────────────────────────────────────────┘
```

**Loma Button specifications:**

| Property | Value | Rationale |
|---|---|---|
| **Size** | 28×28px (icon area), 36×36px (click target) | Matches Grammarly's sizing convention. Users expect this scale. |
| **Position** | Lower-right corner, 8px inset from edge | Same convention as Grammarly — users know to look here. |
| **Color (dormant)** | Deep teal (#0D9488) | Must be distinguishable from Grammarly's green (#15C39A). |
| **Color (active)** | Pulsing glow animation (300ms period) | Indicates "working." |
| **Visibility trigger** | Appears when: (a) text field contains Vietnamese (per Section 2.5 detection) AND (b) field has >10 characters AND (c) field is focused AND (d) field height ≥38px | Don't show on empty fields, pure-English fields, or tiny inputs. 38px minimum follows Grammarly's proven threshold. |
| **Hide trigger** | Disappears when: (a) field loses focus AND result card is not showing, OR (b) user dismisses via card ✕ | Don't linger when user moves away. |
| **Z-index** | 999999 within Shadow DOM stacking context | Conservative value. Shadow DOM isolation prevents conflicts with other extensions. |
| **Implementation** | Shadow DOM custom element (`<loma-button>`), positioned absolute relative to text field | Shadow DOM for style isolation. Position tracked via IntersectionObserver. |

**What the button does NOT show:** No error count, no ambient animation while user types, no badge or tooltip until clicked, no secondary icons.

### 3.2 Grammarly Coexistence

Many target users will have Grammarly installed. The Loma button MUST NOT overlap the Grammarly G button.

**Detection approach:**

```javascript
function detectGrammarly(textField) {
  const parent = textField.closest('[data-gramm]') || textField.parentElement;
  const grammarlyEl = document.querySelector('grammarly-extension, grammarly-desktop-integration');
  const hasGrammAttr = textField.hasAttribute('data-gramm') || textField.hasAttribute('data-gramm_editor');
  const nearbyBtn = parent?.querySelector('[class*="grammarly"], grammarly-btn');
  return !!(grammarlyEl || hasGrammAttr || nearbyBtn);
}
```

**If Grammarly detected:** Offset Loma button 44px to the left (`right: 52px` instead of `right: 8px`).

**⚠️ SPIKE ITEM (Week 3):** This detection logic MUST be tested on Gmail, Slack, Google Docs, GitHub, and LinkedIn with Grammarly active. Budget 4 hours for hands-on debugging. The above code is a starting hypothesis, not a solved problem.

### 3.3 Button Placement by Platform

| Platform | Text Field Type | Button Position | Special Notes |
|---|---|---|---|
| **Gmail compose** | contenteditable div | Lower-right of compose body, above send bar | Must handle fullscreen, popout, and inline compose modes. |
| **Slack message** | contenteditable div | Lower-right of message input | Input is narrow. If field width <250px, position button above the field instead of inside it. |
| **GitHub textarea** | Standard textarea | Lower-right corner, 8px inset | Standard implementation. |
| **LinkedIn message** | contenteditable div | Lower-right of message compose | Similar to Gmail handling. |
| **Generic textarea** | Standard textarea | Lower-right corner, 8px inset | Default fallback for unrecognized sites. |

### 3.4 The Result Card (Primary Output Surface)

Floating result card appears AFTER user taps the Loma button. Card shows the complete rewrite with intent badge, before/after comparison, quality signal, and action buttons.

```
┌──────────────────────────────────────────────────────┐
│  🎯 Nhắc thanh toán · Payment follow-up    ✕        │ ← Intent badge (Vietnamese + English)
│ ─────────────────────────────────────────────────────│
│                                                      │
│  ▸ Xem bản gốc                                      │ ← Collapsed by default (tap to expand)
│                                                      │
│  Hi Minh, following up on VinAI's January invoice    │
│  for $5,000 — now 2 weeks overdue. Could you         │
│  confirm the expected payment date by Friday?         │
│                                                      │
│ ─────────────────────────────────────────────────────│
│  ✂️ Ngắn hơn 52%                                     │ ← Quality signal (Vietnamese UI)
│                                                      │
│  ┌──────────┐  ┌────────────┐  ┌───────────────┐    │
│  │  ✓ Dùng  │  │ 📋 Sao chép │  │ ↻ Đổi giọng  │    │ ← Action row (Vietnamese)
│  └──────────┘  └────────────┘  └───────────────┘    │
└──────────────────────────────────────────────────────┘
```

**When "▸ Xem bản gốc" (Show original) is expanded:**

```
┌──────────────────────────────────────────────────────┐
│  🎯 Nhắc thanh toán · Payment follow-up    ✕        │
│ ─────────────────────────────────────────────────────│
│                                                      │
│  ▾ Ẩn bản gốc                                       │
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │
│  │ anh Minh ơi, invoice tháng 1 chưa thanh toán, │  │ ← Original text (muted, 12px, #6B7280)
│  │ 5000 USD quá hạn 2 tuần                        │  │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  │
│                                                      │
│  Hi Minh, following up on VinAI's January invoice    │ ← Rewrite (normal text)
│  for $5,000 — now 2 weeks overdue. Could you         │
│  confirm the expected payment date by Friday?         │
│                                                      │
│ ─────────────────────────────────────────────────────│
│  ✂️ Ngắn hơn 52%                                     │
│                                                      │
│  ┌──────────┐  ┌────────────┐  ┌───────────────┐    │
│  │  ✓ Dùng  │  │ 📋 Sao chép │  │ ↻ Đổi giọng  │    │
│  └──────────┘  └────────────┘  └───────────────┘    │
└──────────────────────────────────────────────────────┘
```

**Before/after comparison design decisions:**

- **Collapsed by default.** Most users (>70%) will trust the rewrite and tap [Use] without checking the original. Expanding by default adds visual noise for the common case. Collapsed state is a single text link — near-zero visual cost.
- **Original shown in muted style.** Smaller font (12px), gray text (#6B7280), dashed border container. Visually subordinate to the rewrite. The rewrite is the hero; the original is reference.
- **Not a diff.** We don't highlight word-level changes because the transform is too dramatic — Vietnamese to English isn't a "diff," it's a complete restructuring. Side-by-side or word-level diff would be confusing. Stacked (original above, rewrite below) is the right pattern.
- **Learning value.** Over time, users who expand "Show original" learn English patterns. "Ah, 'quá hạn 2 tuần' becomes 'now 2 weeks overdue' — I'll remember that." This creates sticky retention that pure substitution tools don't.
- **Analytics:** `original_expanded` event with `{time_spent_viewing_ms}`. If >40% of users expand on >50% of rewrites, consider making it default-expanded in Phase 2.

**Card specifications:**

| Property | Value | Rationale |
|---|---|---|
| **Width** | 420px | Wide enough for a full email paragraph without awkward wrapping. |
| **Max height** | 360px (increased from 320px to accommodate comparison), scrollable | Room for original + rewrite when expanded. |
| **Position** | `position: fixed`, viewport-anchored near the Loma button | **NOT anchored to the text field.** Fixed positioning ensures the card is always visible regardless of field or page scroll state. |
| **Shadow** | `0 8px 24px rgba(0,0,0,0.12)` | Elevated, clear separation from background. |
| **Corner radius** | 12px | Modern, approachable. |
| **Background** | White (#FFFFFF) with 1px border (#E5E7EB) | Clean, high-contrast. |
| **Typography** | System font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`. Body 14px, meta 12px. | Matches host platform's native font. |
| **Entry animation** | Fade in + slide up 8px, 200ms ease-out | Feels connected to the button. |
| **Dismiss** | ✕ button, click outside card, Escape key | Three ways to dismiss = no trapped feeling. |
| **Implementation** | Shadow DOM custom element (`<loma-card>`), `position: fixed` | Completely isolated from page styles. |

**Scroll behavior:** Because the card is viewport-fixed, page scrolling does NOT move the card. If the Loma button scrolls out of view, the card remains visible until dismissed.

### 3.5 Intent Badge

The intent badge is the single most important UX element differentiating Loma from Grammarly. It says: "We understood what you're trying to do."

```
┌─────────────────────────────────────────────────┐
│  🎯 Nhắc thanh toán · Payment follow-up   [▾]  │
└─────────────────────────────────────────────────┘
```

- Shows **both Vietnamese label and English label** separated by a centered dot. Vietnamese first (user's language), English second (teaches terminology).
- Auto-detected intent shown as a colored pill badge
- Tappable to reveal dropdown of all intents (labels in Vietnamese with English subtitle)
- **14 total intents:** 10 universal intents (work for both English and Vietnamese output) + 4 Vietnamese-specific intents (only appear when Vietnamese output is detected)
- If user changes intent → re-triggers rewrite with new intent (logs `intent_user_corrected`)
- Color-coded by intent category (soft background, dark text):

```
Universal intents (English or Vietnamese output):
Nhắc thanh toán:      bg #D1FAE5, text #065F46
Yêu cầu:             bg #DBEAFE, text #1E40AF
Theo dõi:             bg #FEF3C7, text #92400E
Từ chối:              bg #FEE2E2, text #991B1B
Giới thiệu:           bg #E0E7FF, text #3730A3
Góp ý:                bg #FCE7F3, text #9D174D
Không đồng ý:         bg #FFF7ED, text #9A3412
Chuyển cấp trên:      bg #FEF2F2, text #7F1D1D
Xin lỗi:              bg #F0FDF4, text #166534
Prompt AI:            bg #F5F3FF, text #5B21B6

Vietnamese output intents (only shown when Vietnamese output detected):
Văn bản hành chính:   bg #FEF9C3, text #854D0E
Email trang trọng:    bg #ECFDF5, text #065F46
Báo cáo:              bg #EFF6FF, text #1E40AF
Đề xuất:              bg #FDF4FF, text #6B21A8
```

### 3.6 Quick-Pick Card (Low-Confidence Intent)

**HYPOTHESIS:** We estimate ~70% of rewrites will auto-detect with high confidence and ~30% will trigger quick-pick. These numbers are unvalidated. The UX must work well even if the split is 50/50 or 40/60. Quick-pick is NOT a degraded fallback — it's a first-class path.

When intent confidence is below threshold (initially 70%, tunable):

```
┌──────────────────────────────────────────────────────┐
│  Bạn muốn làm gì?                             ✕     │
│                                                      │
│  ┌──────────────────┐  ┌───────────────────┐         │
│  │ 💰 Nhắc thanh toán │  │ 🔄 Theo dõi      │         │ ← Exactly 3 options
│  └──────────────────┘  └───────────────────┘         │
│  ┌──────────────────┐  ┌───────────────────┐         │
│  │ 🚫 Từ chối       │  │ Khác...           │         │
│  └──────────────────┘  └───────────────────┘         │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Design rules:**
- Show **exactly 3** suggested intents ranked by heuristic confidence score. Never 2, never 4+.
- Fourth slot is always "Khác..." (Other) which expands to the full list of 10.
- One tap → quick-pick transitions to skeleton → result streams in.
- Quick-pick card uses the same viewport-fixed positioning as the result card.

### 3.7 Quality Signal

Below the rewrite text, a single validated metric:

```
English output:    ✂️ Ngắn hơn 52%
Vietnamese output: 📐 Đầy đủ hơn · Đúng format hành chính
```

**What we show at launch:**

| Output language | Metric | Computation | Why |
|---|---|---|---|
| **English** | **% shorter** | `(1 - output_chars / input_chars) × 100` | Vietnamese → English rewrites typically shorten 30-60%. Meaningful quality signal. |
| **Vietnamese (thân mật/trang trọng)** | **% shorter** or **Đầy đủ hơn** | Same formula. If output is longer, show "Đầy đủ hơn" (More complete) instead of negative %. | Formal Vietnamese is often longer than casual input — that's the point. |
| **Vietnamese (hành chính)** | **Đúng format hành chính** | Static badge when công văn template is applied | Users care about format compliance, not length. |

**What we do NOT show at launch:** Clarity score, Authority score, Overall score. These require validated scoring models we don't have. Showing unreliable scores erodes trust. Defer to Phase 2 (Month 3+) after calibration data.

### 3.8 Action Buttons

Three primary actions, always visible at the bottom of the result card. **All labels use Vietnamese UI by default (per Section 1.4).**

**[✓ Dùng]** — Primary action. Large, brand-colored (#0D9488), prominent.
- Replaces user-written text in the field with the rewrite (respecting text isolation boundaries from Section 2)
- For textarea: `.value` replacement (store previous value in memory)
- For contenteditable with boundaries: Range-based replacement of user-text portion only, preserving all DOM nodes below the boundary (store previous DOM fragment in memory)
- Logs: `rewrite_accepted` event
- Card dismisses. Brief green highlight on the replaced text in the field (500ms fade) to confirm what changed.
- **Undo toast (5 seconds):** After replacement, a small toast appears at the bottom of the viewport:
  ```
  ┌──────────────────────────────────────────────┐
  │  ✓ Đã thay văn bản              [Hoàn tác]   │
  └──────────────────────────────────────────────┘
  ```
  Tapping [Hoàn tác] restores the original text from memory. Toast auto-dismisses after 5 seconds, at which point the previous text is cleared from memory. Logs: `rewrite_undone` if triggered.

**[📋 Sao chép]** — Secondary action. Outlined, neutral.
- Copies rewrite text to clipboard
- Shows brief "Đã sao chép!" confirmation (1s)
- Card stays open
- Logs: `rewrite_copied` event
- **Why Copy instead of Edit:** Editing a multi-sentence paragraph inside a 420px floating card is a cramped, bad experience. Users who need to modify the rewrite are better served by copying, pasting into the native field, and editing there.

**⚠️ Copy flow data gap (acknowledged):** After the user copies and pastes, we lose visibility into what they edit. The [Use] path has clean before/after data. The Copy path is partially blind.

Mitigation: After `rewrite_copied` fires, attach a one-time `input` event listener to the text field. If the field content changes within 30 seconds and contains ≥60% overlap with the copied rewrite (fuzzy match), snapshot the final text and log `rewrite_modified_after_paste` with edit distance. This is imperfect — it won't catch cross-field or cross-app pastes — but it recovers signal for the ~70% of Copy users who paste into the same field. Accept that Copy path generates weaker training data than [Use] path.

**[↻ Đổi giọng]** — Tertiary action. Text link style.
- Opens a compact tone selector. Options depend on the current output language:

  **English output (default):**
  ```
  [Trực tiếp hơn] [Nhẹ nhàng hơn] [Ngắn gọn hơn] [Trang trọng hơn]
  ```

  **Vietnamese output:**
  ```
  [Thân mật] [Trang trọng] [Hành chính]
  ```

  **Language switch row (always visible, below tone options):**
  ```
  ─────────────────────────────────
  [🇬🇧 English] [🇻🇳 Tiếng Việt]
  ```
  Tapping a language option switches output language AND shows the appropriate tone options. This is the manual override for auto-detection (Section 2.6). The selected language is stored as a per-domain preference.

- Selecting any option re-triggers the rewrite with the same intent but adjusted tone/language parameter
- One-tap action, NOT a text input.
- Maximum 4 tone options per language + 2 language options. No free-text prompt field.

### 3.9 The Loading State

The 1-2 second wait between button tap and result is the most critical UX moment.

**Timeline breakdown:**

```
0ms:     User taps Loma button
         → Card appears INSTANTLY (skeleton layout, viewport-fixed)
         → Button transitions to "active" state (pulsing glow)

~50ms:   Intent detection completes (heuristic, local, no network)
         → Intent badge fills in with a 300ms transition
         → If low confidence: skeleton card replaced by quick-pick card
         → 300ms transition ensures the badge is perceptible

~100ms:  If rules engine can handle it (no LLM needed):
         → Full rewrite appears. Done in <200ms total.
         → Quality signal calculates and appears.

100-800ms:  Haiku path — streaming response (typing animation)
100-1800ms: Sonnet path — streaming response
```

**Skeleton card (shown at 0ms):**

```
┌──────────────────────────────────────────────────────┐
│  [░░░░░░░░░░░░░░░░]                       ✕         │ ← Badge placeholder (shimmer)
│ ─────────────────────────────────────────────────────│
│                                                      │
│  Đang viết nhắc thanh toán...                        │ ← Contextual microcopy (Vietnamese, after intent)
│                                                      │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░                          │ ← Text placeholder (shimmer)
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                     │
│                                                      │
│ ─────────────────────────────────────────────────────│
│  ░░░░░░░░░░                                          │
│                                                      │
│  ┌──────────┐  ┌────────────┐  ┌───────────────┐    │ ← Buttons visible but disabled
│  │  ✓ Dùng  │  │ 📋 Sao chép │  │ ↻ Đổi giọng  │    │
│  └──────────┘  └────────────┘  └───────────────┘    │
└──────────────────────────────────────────────────────┘
```

**Contextual microcopy during loading:** Once intent resolves (~50ms), the shimmer body shows Vietnamese text describing what Loma is doing. Microcopy from the string table (Section 1.4), mapped by intent:

```javascript
// Uses the i18n string table — Vietnamese by default
const loadingText = t(`loading_${detectedIntent}`);
// e.g. "Đang viết nhắc thanh toán..." or "Đang soạn từ chối lịch sự..."
```

Shimmer animation on remaining placeholder blocks. Buttons disabled (50% opacity) until rewrite completes. Intent badge placeholder resolves at ~50ms with a smooth 300ms transition.

---

## 4. Flows

### 4.1 Primary Flow: Happy Path (High-Confidence Intent)

**HYPOTHESIS: This path handles ~70% of rewrites. Validate in Week 1-2 beta.** If actual high-confidence rate is below 50%, re-evaluate quick-pick as the default path.

```
1.  User focuses on Gmail compose window (reply to a thread)
2.  User types: "anh Minh ơi, invoice tháng 1 chưa thanh toán, 5000 USD quá hạn 2 tuần"
    (Below: signature + quoted thread from Minh's previous email)
3.  Vietnamese detected in text → Loma button appears in lower-right
4.  User taps Loma button
5.  Text isolation extracts user-written portion (above signature/thread)
6.  Skeleton card appears instantly (viewport-fixed, near Loma button)
7.  Intent badge resolves: "🎯 Nhắc thanh toán · Payment follow-up" (~50ms, 300ms transition)
8.  Microcopy: "Đang viết nhắc thanh toán..."
9.  Rewrite streams in word by word (~800ms Haiku / ~1500ms Sonnet)
10. Quality signal appears: "✂️ Ngắn hơn 52%"
11. User taps [✓ Dùng]
12. User-written portion replaced. Signature + quoted thread untouched.
13. Card dismisses. Undo toast appears. Replaced text highlights green (500ms).
14. User reviews and sends.

Total time from button tap to ready-to-send: 2-4 seconds
```

### 4.2 Secondary Flow: Low-Confidence Intent

```
1-5. Same as above
6.   Quick-pick card appears (viewport-fixed):
     "Bạn muốn làm gì?"
     [💰 Nhắc thanh toán] [🔄 Theo dõi] [🚫 Từ chối] [Khác...]
7.   User taps "💰 Nhắc thanh toán"
8.   Quick-pick transitions to skeleton card → result streams in
9-14. Same as happy path

Total time: 4-6 seconds (one extra tap)
```

### 4.3 Copy Flow

```
1-10. Same as happy path
11.   User reads rewrite, wants to modify before using
12.   User taps [📋 Sao chép]
13.   "Đã sao chép!" confirmation appears (1s)
14.   User clicks into the text field, selects their text, pastes
15.   User edits the pasted text directly in the native field
16.   Card auto-dismisses when user starts typing in the field

Data logged: rewrite_copied event. Field listener attached for 30s
to detect paste + modification (see Section 3.8 mitigation).
⚠️ Known limitation: Copy path generates weaker training data than
[Use] path. Cross-app pastes and no-paste cases are invisible.
[Use] remains the primary training data source.
```

### 4.4 Keyboard Shortcut Flow

```
1.  User types in text field
2.  User presses Cmd+Shift+. (Mac) / Ctrl+Shift+. (Windows)
3.  Same as tapping Loma button → skeleton card appears
4.  Tab to cycle between [Dùng] [Sao chép] [Đổi giọng]
5.  Enter to confirm selection
6.  Escape to dismiss
```

**Why Cmd+Shift+. instead of Cmd+Shift+G:** Cmd+Shift+G is "Find Previous" in all major browsers. Cmd+Shift+. is uncontested in Chrome. Registered as a configurable shortcut in the Manifest V3 `commands` section.

### 4.5 Text Selection Flow (Phase 2, Month 4)

NOT at launch. After launch, add: select specific text → Loma button appears near selection → rewrite only the selected portion. This is the escape hatch for cases where text isolation fails or the user wants to rewrite a specific paragraph.

---

## 5. First-Time User Experience (FTUX)

### 5.1 Post-Install Onboarding Tab

Immediately after installation, Loma opens a new browser tab with a **live interactive demo.** All text in Vietnamese (browser language `vi`) or English (fallback).

```
Step 1: Install from Chrome Web Store
   → Extension icon appears in toolbar
   → NEW TAB opens automatically: loma.app/welcome

Step 2: Welcome tab — hero message
   → "Hết loay hoay với câu chữ."
   → "Bạn lo phần ý. Loma lo phần lời."
   → [Xem thử →]

Step 3: English demo — fake email compose interface
   → Pre-filled with a Vietnamese sample message (payment follow-up)
   → Loma button visible in the compose area
   → Instructional overlay: "Bấm nút Loma để xem kết quả ↓"
   → User taps → full rewrite flow plays out → English output
   → Badge: "💰 Nhắc thanh toán · Payment follow-up"
   → "Tiếng Anh — nghe như người bản xứ viết."

Step 4: Vietnamese demo — second example auto-queued
   → Pre-filled with a casual Vietnamese request to boss
   → User taps → formal Vietnamese output
   → Badge: "📝 Email trang trọng"
   → "Tiếng Việt cũng vậy — đúng giọng, đúng lúc."

Step 5: CTA
   → [Bắt đầu dùng Loma →] → closes tab
   → [Thử ví dụ khác] → cycles through 3 more demo scenarios

Step 6: First real usage
   → User navigates to Gmail/Slack/any text field
   → First time only: subtle tooltip near Loma button (auto-dismisses after 5s)
   → "Viết xong rồi bấm vào đây"
   → First 5 real rewrites use Sonnet regardless of routing
```

**If user closes onboarding tab early:**
- Lightweight exit prompt: "Điều gì khiến bạn dừng lại?" with 3 options: [Chỉ xem thử] [Không phải thứ tôi cần] [Để sau]
- Optional — user can close without answering.
- Logged as `ftux_exited_early` event.

### 5.2 Free Trial & Auth Model

| Aspect | Decision | Rationale |
|---|---|---|
| **Trial type** | 5 free rewrites. Google OAuth required after rewrite #1 (non-blocking banner). | Pure "no signup" is unenforceable. Lightweight OAuth after seeing value is low-friction. |
| **Auth flow** | After first successful rewrite, bottom of result card shows: "Đăng nhập Google để lưu kết quả" | Not a gate — user can dismiss and use remaining 4 free rewrites. |
| **Model for free rewrites** | Always Sonnet (best quality) | First impression matters. 5 × Sonnet ≈ $0.075. |
| **After 5 rewrites (signed in)** | "Bạn đã dùng hết lượt miễn phí." + [Nạp tiền] | PAYG flow begins. |
| **After 5 rewrites (not signed in)** | "Đăng nhập để nhận thêm 5 lượt miễn phí." | Total free: 10 rewrites if they sign in after #5. |

---

## 6. Extension Popup (Settings & Account)

Clicking the Loma icon in Chrome's toolbar opens a popup. All text Vietnamese by default.

### 6.1 Popup Layout

```
┌──────────────────────────────────┐
│  [Loma logo]  Loma          [⚙️] │
│ ────────────────────────────────│
│                                  │
│  duc.nguyen@gmail.com            │
│  ₫47,200 còn lại                │
│  [Nạp tiền]                     │
│                                  │
│ ────────────────────────────────│
│  Lượt viết hôm nay: 12          │
│  Lượt viết tháng này: 187       │
│                                  │
│ ────────────────────────────────│
│  ☑ Bật trên trang này            │
│  ☑ Hiện nút Loma                │
│  ☐ Chỉ dùng phím tắt            │
│                                  │
│ ────────────────────────────────│
│  [Quản lý tài khoản] [Đăng xuất]│
└──────────────────────────────────┘
```

**Popup specifications:**
- Width: 320px (Chrome popup standard)
- Sections: Identity + balance, usage stats, per-site toggle, account links
- "Bật trên trang này" lets users disable Loma on specific domains
- "Chỉ dùng phím tắt" hides the floating Loma button
- "Nạp tiền" links to the PAYG payment flow

### 6.2 Settings Page (⚙️)

Opens in a new tab (`loma.app/settings`). Phase 2 build item. Contains:
- Default intent preference (auto-detect vs. always ask)
- Preferred tone default
- Site blacklist management
- Keyboard shortcut customization
- UI language override (Vietnamese / English)
- Data & privacy (export data, delete account)
- Billing history

---

## 7. Visual Design

### 7.1 Design Language

| Element | Specification | Rationale |
|---|---|---|
| **Brand color** | Deep teal (#0D9488) | Distinct from Grammarly green (#15C39A), Gmail blue, Slack purple. |
| **Card background** | White (#FFFFFF) with 1px border (#E5E7EB) | Platform-native card language. |
| **Typography** | System font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` | Matches host platform. Never impose a custom font. |
| **Icons** | Minimal, line-style, 1.5px stroke | Don't compete with platform icons. |
| **Animation** | Functional only. 200ms transitions, ease-out. | Movement = state change, not decoration. |
| **Shadows** | Dormant: `0 2px 8px rgba(0,0,0,0.08)`. Active card: `0 8px 24px rgba(0,0,0,0.12)`. | Clear elevation hierarchy. |

### 7.2 Color Palette

```
Primary:          #0D9488 (deep teal)
Primary hover:    #0F766E
Primary light:    #CCFBF1 (teal tint, badge backgrounds)

Neutral:
  Text:           #1F2937
  Secondary:      #6B7280
  Border:         #E5E7EB
  Background:     #FFFFFF

Semantic:
  Success:        #10B981 (text replacement highlight)
  Warning:        #F59E0B (low confidence indicator)

Intent badge colors: See Section 3.5
```

### 7.3 Dark Mode

Phase 2 item. Detect via `prefers-color-scheme: dark`. Invert card background to #1F2937, text to #F9FAFB, borders to #374151.

### 7.4 Responsive Behavior (Desktop Only)

**Note:** Chrome extensions (Manifest V3) do not run on mobile Chrome. All specs are desktop-only.

| Text Field Size | Loma Button | Result Card |
|---|---|---|
| **Large** (>500px wide, >100px tall) | Standard 36px, standard position | Standard 420px card, viewport-fixed |
| **Medium** (200-500px wide) | Standard 36px, standard position | Card width = min(420px, viewport width - 32px) |
| **Small** (100-200px wide, 38-100px tall) | Smaller 28px icon, tighter 4px inset | Standard card, viewport-fixed |
| **Tiny** (<100px wide or <38px tall) | **Don't inject.** | N/A |

---

## 8. Accessibility

| Requirement | Implementation |
|---|---|
| **Keyboard navigation** | All elements focusable via Tab. Enter/Space to activate. Escape to dismiss card. Arrow keys navigate intent dropdown and tone selector. |
| **Screen reader** | Loma button: `aria-label` uses i18n string `aria_button` ("Viết lại với Loma" / "Rewrite with Loma"). Result card: `role="dialog"`, `aria-labelledby` referencing intent badge text. Quick-pick card: `role="dialog"`, `aria-label` uses i18n string `aria_quickpick`. |
| **ARIA live regions** | Result card body (`<div aria-live="polite">`) announces state transitions: skeleton → loading microcopy, intent resolved → intent label, streaming complete → full rewrite text read aloud, quality signal. |
| **Focus management** | When card opens, focus moves to card. Tab cycles within card (intent badge → show original toggle → rewrite text → Dùng → Sao chép → Đổi giọng → dismiss ✕). Escape returns focus to text field. Focus trapped within card while open. |
| **Visible focus indicators** | All interactive elements show a 2px solid #0D9488 outline with 2px offset on `:focus-visible`. Shadow DOM suppresses default browser focus rings, so custom ones are mandatory. |
| **Color contrast** | All text meets WCAG AA. Primary teal #0D9488 on white = 4.53:1 — passes AA for 16px+ text. For 12px meta text, use **#0F766E** (5.4:1) or #4B5563 (7.1:1). Intent badge text colors all exceed 4.5:1 against their backgrounds. |
| **Reduced motion** | Respect `prefers-reduced-motion: reduce`. Replace shimmer with static gray blocks. Replace slide-up with instant appearance. Replace streaming typing with instant full-text. Pulse → static color change. |
| **Font scaling** | Card text uses `rem` units. Body: 0.875rem (14px default). Meta: 0.75rem (12px default). Card max-height scales proportionally. |

---

## 9. Error States

All error strings use Vietnamese UI by default (per Section 1.4).

| Error | User Sees | Recovery |
|---|---|---|
| **API timeout** (>5s) | Card body: "Lâu hơn bình thường..." with spinner | Auto-retry once. If retry fails: "Không thể viết lại. Kiểm tra kết nối." + [Thử lại]. |
| **API error** (500) | Card body: "Có lỗi xảy ra." + [Thử lại] | One-tap retry. If persistent: "Dịch vụ tạm gián đoạn. Thử lại sau vài phút." |
| **No Vietnamese detected** | Button doesn't appear | N/A — button requires Vietnamese content per Section 2.5. |
| **Text too long** (>2000 chars extracted) | Card shows: "Đang viết lại 2000 ký tự đầu." | Truncate with notice. |
| **Rate limited** | "Bạn đã dùng hết lượt miễn phí." + [Nạp tiền] | Clear path to payment. |
| **Offline** | Button gray/dimmed. Tap shows: "Không có kết nối mạng." | Auto-retry on navigator.onLine. |
| **Text isolation failed** | Full-field rewrite with notice: "Đã viết lại toàn bộ tin nhắn. Chọn văn bản cụ thể để viết lại một phần." | Transparent. Teaches text-selection flow (Phase 2). |

---

## 10. Analytics Events

Every interaction generates training data. All event names use `loma_` prefix.

| Event | Payload | Purpose |
|---|---|---|
| `loma_button_shown` | `{platform, field_type, text_length, detected_language_mix, grammarly_present}` | Where and when. `detected_language_mix: {vi_ratio, en_ratio}` tracks code-switching prevalence. |
| `loma_button_tapped` | `{platform, text_length, language_mix, text_isolation_method}` | Activation rate. Isolation strategy used. |
| `loma_intent_auto_detected` | `{intent, confidence, text_hash, language_mix}` | Accuracy baseline, segmented by code-switching ratio. |
| `loma_intent_quickpick_shown` | `{suggested_intents[], confidence_scores[]}` | How often low-confidence triggers. Validates the 70/30 hypothesis. |
| `loma_intent_user_corrected` | `{auto_intent, selected_intent, was_quickpick}` | Training labels. Most valuable signal. |
| `loma_rewrite_generated` | `{intent, routing_tier, latency_ms, input_length, output_length}` | Engine performance. |
| `loma_rewrite_accepted` | `{intent, time_to_accept_ms}` | Quick accept = good rewrite. |
| `loma_rewrite_copied` | `{intent, time_to_copy_ms}` | Copy vs. direct use pattern. |
| `loma_rewrite_modified_after_paste` | `{intent, edit_distance, original_rewrite_text, final_text}` | **Stores actual text** (user consents via ToS). Imperfect signal — only captures same-field pastes within 30s window. |
| `loma_rewrite_dismissed` | `{intent, time_to_dismiss_ms}` | Quick dismiss = bad rewrite. |
| `loma_rewrite_undone` | `{intent, time_to_undo_ms}` | If >10%, replacement logic unreliable. |
| `loma_original_expanded` | `{intent, time_spent_viewing_ms}` | Comparison usage. If >40% expand regularly, consider default-expanded. |
| `loma_tone_change_requested` | `{intent, tone_selected}` | Tone demand patterns. |
| `loma_text_isolation_result` | `{method, boundary_type, chars_extracted, chars_preserved}` | Isolation reliability. |
| `loma_ftux_completed` | `{screens_viewed, time_spent, signed_up}` | Onboarding effectiveness. |
| `loma_ftux_exited_early` | `{screen_reached, time_spent, exit_feedback?}` | Activation funnel diagnostics. |
| `loma_error_shown` | `{error_type, platform}` | Reliability monitoring. |

**Critical flywheel signals:**
- `loma_intent_user_corrected` → direct training label for intent detection model
- `loma_rewrite_modified_after_paste` → shows what the engine should have produced (weaker signal from Copy path — accepted limitation)
- `loma_rewrite_dismissed` with `time_to_dismiss_ms < 2000` → flag for review
- `loma_text_isolation_result` → monitors the #1 architectural risk
- `loma_intent_auto_detected` segmented by `language_mix` → monitors code-switching accuracy

---

## 11. What NOT to Build at Launch

| Feature | Why Skip | When to Add |
|---|---|---|
| **In-card editing** | Cramped 420px card. Copy + paste into native field is better. | Phase 2, only if data demands |
| **Text selection rewrite** | Full-field + isolation covers 90%. Selection adds DOM complexity. | Phase 2, Month 4 |
| **Clarity/Authority scores** | Needs validated scoring model. | Phase 2, Month 3+ |
| **Real-time suggestions** | That's Grammarly's product. | Probably never |
| **Side panel / sidebar** | Too much screen real estate. | Only if data demands |
| **Dark mode** | Not launch-blocking. | Phase 2, Month 3-4 |
| **Full settings page** | Popup covers essentials. | Phase 2, Month 2-3 |
| **Intent frequency bias** | Need ≥20 rewrites per user for meaningful data. | Phase 2, Month 3. Local storage frequency counter. |
| **Context menu** | Discoverable but slow. | Phase 2, easy add |
| **Document mode** (paragraph-level control) | Architectural shift for long-form. | Phase 3 (see Section 14.1) |
| **Express mode** (no card, auto-accept) | Needs earned trust (50+ rewrites). | Phase 2 (see Section 14.2) |
| **Rewrite history** | Requires storage architecture. | Phase 2 (see Section 14.3) |
| **Recipient context** | Adds interaction complexity. | Phase 2 concept (see Section 14.4) |

---

## 12. Implementation Priority

```
WEEK 1-2 (Rewrite Engine — per Tech Spec v1.3):
   Build engine. ALSO: spike text isolation AND code-switching detection.
   
   SPIKE A: Text isolation validation
   - Implement boundary detection for Gmail (Strategy A)
   - Implement generic heuristic (Strategy B)
   - Test against 20 real-world scenarios
   - GATE: ≥18/20 correct extraction
   - If fails: plan text-selection as primary trigger
   - Budget: 8 hours, parallel with engine build

   SPIKE B: Code-switching language detection
   - Implement Vietnamese character/word detection (Section 2.5)
   - Test against 30 real messages from target users
   - Measure: does button appear for all code-switched messages?
   - Measure: does intent detection accuracy hold above 65% for
     messages with >40% English word ratio?
   - Budget: 4 hours

WEEK 3-4 (Chrome Extension Build):

   Priority 1: Loma Button + Shadow DOM
   - Detect text fields (textarea + contenteditable)
   - Inject button via Shadow DOM custom element (<loma-button>)
   - Position tracking with IntersectionObserver
   - Vietnamese language detection trigger (Section 2.5)
   - Grammarly coexistence (SPIKE: 4 hours hands-on testing)
   - Minimum field size enforcement (38px)
   - Text isolation integration
   
   Priority 2: i18n module
   - String table (Section 1.4) with Vietnamese default
   - Browser language detection
   - t() function for all user-facing strings
   - MUST be built before result card (all card strings use i18n)
   
   Priority 3: Result Card (viewport-fixed)
   - Skeleton loading with Vietnamese microcopy
   - Intent badge (Vietnamese + English dual label)
   - Streaming text display
   - "Show original" comparison toggle
   - Quality signal (% shorter, Vietnamese label)
   - [✓ Dùng] → boundary-respecting replacement + undo toast
   - [📋 Sao chép] → clipboard + paste detection listener
   
   Priority 4: Quick-Pick Card
   - 3 suggested intents (Vietnamese labels) + "Khác..."
   - Transition to result card after selection
   
   Priority 5: Tone selector
   - 4 fixed options (Vietnamese labels)
   - Re-trigger rewrite with tone parameter

WEEK 5 (Platform specifics + FTUX):

   Priority 6: Platform-specific positioning
   - Gmail compose (3 modes)
   - Slack message input
   - GitHub textarea
   - Generic fallback
   
   Priority 7: FTUX
   - Post-install onboarding tab (Vietnamese) with live demo
   - First-time tooltip on Loma button
   - Google OAuth prompt (non-blocking)
   - Free trial counter (5 rewrites)
   - Exit feedback prompt

   Priority 8: Extension popup
   - Vietnamese UI
   - Account info + balance
   - Usage stats
   - Per-site enable/disable toggle

   Priority 9: Keyboard shortcut + error states
   - Cmd+Shift+. / Ctrl+Shift+.
   - Tab navigation within card
   - All error states (Vietnamese strings)
```

---

## 13. Success Metrics

| Metric | Target | Measurement | Notes |
|---|---|---|---|
| **Button-to-result (p50)** | <1.5s | Loma tap → full rewrite visible | |
| **Button-to-result (p95)** | <3s | Includes Sonnet path | |
| **Text isolation accuracy** | ≥90% | Correct extraction / total Gmail rewrites | If below 80%, accelerate text-selection flow. |
| **Code-switch detection rate** | >95% | Vietnamese detected / total code-switched inputs | New metric. If Loma button fails to appear for mixed text, core use case breaks. |
| **Intent accuracy on mixed input** | >65% | Correct auto-detect / total code-switched rewrites | Segmented by language mix ratio. Track weekly. |
| **Activation rate** | >30% | Users who see button AND tap ≥1 | |
| **FTUX completion** | >60% | Users who complete onboarding demo tab | |
| **First rewrite → signup** | >40% | Google OAuth after first rewrite | |
| **Accept rate** | >60% | [Dùng] taps / total rewrites shown | |
| **Undo rate** | <10% | [Hoàn tác] taps / [Dùng] taps | If above 10%, investigate immediately. |
| **Copy rate** | 15-25% | [Sao chép] taps / total rewrites shown | If >30%, users may distrust [Dùng] replacement. |
| **Original expanded rate** | Monitor | [Xem bản gốc] taps / total rewrites | No target — learning. If >40% regularly, default-expand in Phase 2. |
| **Dismiss rate** | <20% | Dismissed without Dùng or Sao chép / total | |
| **Intent correction rate** | <30% | Users who change auto-detected intent | Trending down = model improving. |
| **Quick-pick trigger rate** | Monitor | Times quick-pick shown / total rewrites | If >50%, adjust confidence threshold. |
| **Time to accept** | <3s median | Result shown → [Dùng] or [Sao chép] tapped | |
| **Platform reliability** | >95% | Loma button successfully injects | |
| **Vietnamese output share** | Monitor | Vietnamese output rewrites / total rewrites | Expect 15-25% at launch. If <5%, auto-detection may be too conservative. |
| **Output language override rate** | <15% | Manual language switch via Đổi giọng / total rewrites | If >15%, auto-detection logic needs tuning. |
| **Vietnamese accept rate** | >55% | [Dùng] taps / Vietnamese output rewrites shown | May be lower than English initially — formal Vietnamese is harder to get right. |

---

## 14. Phase 2-3 Scale Concepts

This section outlines the UX architecture needed to serve 1M users with UX as a moat. None of these are built at launch. They are documented here to ensure the Phase 1 architecture doesn't paint us into a corner and to establish the strategic product direction.

### 14.1 Document Mode (Phase 3)

**Problem:** The current "one button, full transform" model assumes the entire text has one intent. This works for 1-3 sentence messages. It breaks for multi-paragraph content (status updates, proposals, performance reviews) where a single message contains multiple intents — informational paragraphs, requests, escalations — all interleaved.

**Concept:** When extracted text exceeds ~500 characters or contains 3+ paragraphs, offer a "Document mode" that shows paragraph-level intent detection and allows per-paragraph accept/reject:

```
┌──────────────────────────────────────────────────────┐
│  📄 Chế độ tài liệu (3 đoạn)                  ✕     │
│ ─────────────────────────────────────────────────────│
│                                                      │
│  ¶1  🔄 Cập nhật                        [✓] [✕]     │
│  "The Q4 review has been completed..."               │
│                                                      │
│  ¶2  📋 Yêu cầu                         [✓] [✕]     │
│  "Could you share the budget numbers..."             │
│                                                      │
│  ¶3  🔺 Chuyển cấp trên                  [✓] [✕]     │
│  "This needs escalation to VP level..."              │
│                                                      │
│ ─────────────────────────────────────────────────────│
│  [✓ Dùng tất cả]   [📋 Sao chép tất cả]             │
└──────────────────────────────────────────────────────┘
```

**Why Phase 3:** Requires multi-intent detection (significant NLP work), paragraph segmentation, partial replacement logic, and a substantially different card UI. Rushing this at launch would compromise the core single-intent experience.

**Phase 1 prep:** The text isolation architecture already segments content. The analytics pipeline already captures input length distribution. Monitor: what % of rewrites involve >500 characters? If >20% by Month 4, accelerate Document Mode.

### 14.2 Express Mode for Power Users (Phase 2, Month 4+)

**Problem:** A user with 500+ rewrites doesn't need to see the result card. They trust Loma. The card is 3 seconds of overhead per rewrite, multiplied by 20 rewrites/day = 1 minute/day of unnecessary review.

**Concept:** Toggle in popup settings: "Chế độ nhanh" (Express Mode). When enabled:

```
Cmd+Shift+. → text replaced instantly → undo toast appears
No card. No review. One keystroke, done.
```

**Safeguards:**
- Only available after 50+ accepted rewrites (earned trust)
- Automatically disabled if undo rate exceeds 15% (quality failsafe)
- Undo toast extended to 8 seconds in express mode (longer safety window)
- Always shows undo toast — never fully silent replacement

**Why Phase 2:** Requires enough user base to validate threshold (50 rewrites) and enough quality data to ensure undo rate stays low. Premature express mode with bad rewrite quality would destroy trust.

### 14.3 Rewrite History (Phase 2, Month 3+)

**Problem:** After 100 rewrites, users have no record of what Loma produced. No audit trail, no learning review, no way to find a specific past rewrite.

**Concept:** Accessible via popup → "Lịch sử viết lại" (Rewrite history):

```
┌─────────────────────────────────────────────────┐
│  Lịch sử viết lại                    [🔍]      │
│ ───────────────────────────────────────────────│
│                                                 │
│  Hôm nay                                       │
│  10:32  Gmail  🎯 Nhắc thanh toán               │
│  "Following up on VinAI's January invoice..."   │
│                                                 │
│  09:15  Slack  🔄 Theo dõi                      │
│  "Hi team, any updates on the Q4 report..."     │
│                                                 │
│  Hôm qua                                       │
│  16:40  Gmail  🚫 Từ chối                       │
│  "Thank you for the offer, but..."              │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Storage:** Local extension storage (IndexedDB) with optional cloud sync after auth. Stores: timestamp, platform, intent, original text (first 100 chars), rewrite text (first 200 chars), accepted/copied/dismissed.

**Learning value:** Users can review their Vietnamese → English patterns. "Ah, that's how Loma translates 'chưa thanh toán' — 'overdue.'" This transforms Loma from a tool into a teacher, deepening retention.

**Enterprise value (Phase 3):** Audit trail of AI-generated content. Required for compliance-sensitive organizations. History export as CSV.

### 14.4 Recipient Context (Phase 2, Month 4+)

**Problem:** "Payment follow-up to a vendor" vs. "to the CEO" require very different tones. Vietnamese business culture has strong hierarchical registers. The current intent × tone matrix misses the recipient dimension.

**Concept:** When quick-pick fires, add an optional second row:

```
Bạn muốn làm gì?
[💰 Nhắc thanh toán] [🔄 Theo dõi] [🚫 Từ chối] [Khác...]

Viết cho ai?  (optional — tap to skip)
[👔 Cấp trên] [🤝 Đồng nghiệp] [📋 Cấp dưới] [🏢 Bên ngoài]
```

**Phase 2+ approach:** Don't add this UI at launch. Instead:
1. Collect tone correction data (which tones users request after auto-detect)
2. Analyze if corrections correlate with recipient domain or email thread history
3. If pattern emerges (>30% of tone changes are seniority-driven), add recipient context
4. Long-term: infer from Gmail recipient metadata (title from email signature, domain for external)

### 14.5 Visible Flywheel — Making Switching Costs Tangible (Phase 2-3)

**Problem:** User #1 and user #1000 see the exact same UX. There's no visible accumulation of value. Zero switching cost — if a competitor launches tomorrow, users can switch with no loss.

**The moat requires users to see and feel the compounding value:**

| Surface | What User Sees | When |
|---|---|---|
| **Accuracy indicator in popup** | "Độ chính xác: 94% (dựa trên 187 lượt)" (Accuracy: 94% based on 187 rewrites) | Phase 2, after intent frequency bias ships |
| **Learned preferences badge** | "Loma đã học 12 cụm từ ưa thích của bạn" (Loma has learned 12 of your preferred phrases) | Phase 3, after style adaptation ships |
| **Monthly writing insights** | Email digest: "Tháng này: 187 lượt viết lại, tiết kiệm ~3 giờ. Phong cách phổ biến nhất: Trực tiếp." (This month: 187 rewrites, saved ~3 hours. Most common style: Direct.) | Phase 2, Month 4 |
| **"Your Loma" data export** | Downloadable profile of learned preferences, terminology, accuracy history | Phase 3 (creates lock-in AND satisfies GDPR portability) |

**The strategic principle:** Every piece of personalization data should have a user-visible manifestation. If Loma learned something about you, you should know it. This transforms invisible ML improvements into tangible switching costs.

### 14.6 Viral & Referral Mechanics (Phase 2, Month 3+)

**Problem:** At 1M users, organic growth matters more than paid acquisition. Vietnamese professional networks are tight and word-of-mouth driven. The product has zero viral mechanics.

**Concept:**

**Referral program:**
- After 10th rewrite, one-time prompt (non-blocking, bottom of result card): "Biết ai cần viết email tiếng Anh? Giới thiệu bạn bè, nhận 5 lượt miễn phí." (Know someone who needs English emails? Refer a friend, get 5 free rewrites.)
- Unique referral link with tracking
- Referrer gets 5 free rewrites per successful referral (capped at 50/month)
- Referred user gets 10 free rewrites instead of 5

**Organic sharing signal:**
- If a recipient replies to a Loma-rewritten email with positive language ("clear", "professional", "well-written"), detect via thread monitoring and surface: "Người nhận đánh giá cao email của bạn ✓" (Your recipient appreciated your email). Reinforces value, creates shareable moment.
- Phase 3. Requires Gmail thread access and sentiment detection. Privacy-sensitive — must be opt-in.

**What we do NOT do:** No "Powered by Loma" watermark or signature. No forced sharing gates. No gamification leaderboards. Growth must feel organic and professional, not gamified.

### 14.7 Enterprise & Team Deployment (Phase 3)

**Problem:** At scale, enterprise accounts drive disproportionate revenue. The current spec has zero enterprise concepts.

**Phase 3 requirements (not built now, but architecture must not preclude):**

- **Chrome Enterprise policy deployment:** Admin pushes Loma via Google Workspace admin console. Extension pre-configured with company settings.
- **Shared terminology dictionary:** Company-specific terms preserved across all team members' rewrites (e.g., internal project names, product terminology).
- **Tone policies:** Admin sets default tone for external communications (e.g., "all client emails must use formal tone"). Individual users can override for internal.
- **Centralized billing:** Team/department accounts with usage allocation.
- **Usage dashboard:** Manager sees aggregate team usage (not individual content) — rewrites/day, acceptance rate, top intents.
- **SSO/SAML:** Required for enterprise auth.

**Phase 1 prep that enables this path:**
- User auth already via Google OAuth (compatible with Google Workspace SSO)
- Analytics events already capture all needed aggregate metrics
- i18n module can be extended to company-specific string overrides
- Intent + tone architecture can accept policy defaults as configuration

---

## Appendix A: Grammarly Competitive Analysis

*Moved from Section 1 of v1.0. Reference material for product and engineering context.*

### A.1 Grammarly's UX Architecture (Current State, Feb 2026)

```
Layer 1: Floating G button (lower-right corner of every text field)
   → Shows error count as you type
   → Click opens full suggestion list as floating card

Layer 2: Inline underlines (rendered OUTSIDE the text field via overlay)
   → Uses Range.getClientRects() API for position tracking

Layer 3: Green lightbulb icon (next to G button)
   → Entry point for generative AI (compose, rewrite, ideate, reply)

Layer 4: Paragraph-level rewrites (select text → pencil icon)
   → Auto-suggests rewrite on text selection

Layer 5: Superhuman Go (side panel, slides from right edge)
   → Context-aware AI assistant, launched Oct 2025
```

### A.2 Key Technical Decisions Grammarly Made

| Decision | Why | Source |
|---|---|---|
| **Shadow DOM for all injected UI** | Style isolation from host page CSS. | Engineering blog |
| **Underlines as overlays, NOT DOM modifications** | Early versions broke websites. Now uses position-tracked overlay divs. | "Making Grammarly Feel Native" blog |
| **Minimum 38px text field height** | Don't inject into tiny inputs. | Support docs |
| **IntersectionObserver for position tracking** | MutationObserver too expensive. | Engineering blog |
| **Floating card, NOT sidebar** | Sidebar breaks narrow layouts. | Support docs |

### A.3 What Grammarly Gets Right (We Steal These)

1. **Zero-friction entry point.** Button appears automatically on focus.
2. **Progressive disclosure.** Simple → detailed, layered.
3. **One-click acceptance.** Under 2 seconds.
4. **Platform-native feel.** "Extension only works if it feels native."
5. **Shadow DOM isolation.** After years of DOM-conflict bugs.

### A.4 What Grammarly Gets Wrong (We Avoid These)

1. **Too many entry points.** Five competing patterns.
2. **Generative AI bolted on.** Lightbulb added 14 years after core product.
3. **Prompt paradigm wrong for our users.** Assumes English articulation ability.
4. **No intent awareness.** Rewrites generically.
5. **Button overlaps content.** Acknowledged in Grammarly support docs.

---

*This specification should be read alongside Tech Spec v1.3. The UX spec defines what the user sees and does. The tech spec defines how it works underneath.*

*Loma UX Specification v1.2 — February 2026*
