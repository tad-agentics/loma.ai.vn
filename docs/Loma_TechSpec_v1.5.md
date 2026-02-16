# Loma — Technical Specification & Requirements

**Version:** 1.5
**Date:** February 2026
**Status:** Pre-build specification
**Companion to:** UX Spec v1.3
**Product rename:** GlobalPro → Loma (effective v1.4)
**Positioning:** Hết loay hoay với câu chữ. Bạn lo phần ý. Loma lo phần lời.

**Changelog v1.4 → v1.5:**
- **Dual-language output:** Loma now produces both English and formal Vietnamese output. New output language router added to pipeline (Section 2.2, 3.7).
- **Vietnamese output intents:** Added 4 Vietnamese-specific intents: `write_to_gov`, `write_formal_vn`, `write_report_vn`, `write_proposal_vn`. Section 6 updated.
- **Output language auto-detection:** Logic based on recipient domain, platform, and input keywords. Section 3.7 added.
- **Cultural Mapping Library expanded:** Now includes Vietnamese formal patterns (casual → formal Vietnamese) alongside Vietnamese → English patterns. Section 3.4 updated.
- **API updated:** `/rewrite` endpoint accepts `output_language` parameter. Response includes `output_language` field. Section 8.1 updated.
- **Data model updated:** `rewrites` table adds `output_language` enum field. Section 7.1 updated.
- **Positioning aligned:** "Hết loay hoay với câu chữ" replaces English-only framing throughout.
- **Build sequence updated:** Vietnamese output mode added to Week 3-4 scope. Total build remains 10-11 weeks.

**Changelog v1.3 → v1.4:**
- **Renamed:** GlobalPro → Loma throughout (DOM elements, API URLs, pattern library, analytics, build sequence)
- **[UX S1] Vietnamese-first UI:** Added i18n module as launch component (Section 3.6). Content script, popup, and all user-facing surfaces default to Vietnamese when browser language is `vi`. String table with 50+ keys.
- **[UX S3] Code-switching support:** Updated language detection from binary (vi/en) to mixed-language aware (Section 3.1, 6.1). Added English business keywords to intent heuristics. Cost router updated for `mixed` language type.
- **[UX S4] Before/after comparison:** API response includes `original_text` for card display. Data model updated with `original_expanded` tracking field.
- **[UX S5] Copy flow data:** Added `paste_detected` and `rewrite_modified_after_paste` fields to data model. Feedback endpoint accepts fuzzy-match paste data.
- **Quality scorer aligned with UX:** Removed Clarity/Authority scores from launch. Only `length_reduction_pct` ships at Phase 1. Clarity/Authority deferred to Phase 2 Month 3+ per UX Spec Section 3.7.
- **Analytics prefix:** All event names updated to `loma_*`. New events: `loma_original_expanded`, `loma_language_mix` fields on existing events.
- **Build sequence realigned:** Added i18n module (Week 3-4 Priority 2), code-switching spike (Week 1-2), paste detection listener (Week 3-4). Timeline remains 10-11 weeks.
- **Phase 2-3 scale concepts:** Added backend requirements for rewrite history storage, express mode API, recipient context schema, enterprise config. Aligned with UX Spec Section 14.

---

## Table of Contents

1. System Overview
2. Architecture
3. Component Specifications
4. Differentiation & Benchmark System
5. Vietnamese NLP Layer — PhoNLP (Phase 2: Month 4-6)
6. Intent Detection System (4-Phase Evolution)
7. Data Models
8. API Specification
9. Infrastructure & DevOps
10. Security & Privacy
11. Non-Functional Requirements
12. Technical Debt Assessment
13. Feasibility Analysis
14. Build Sequence & Dependency Map

---

## 1. System Overview

### 1.1 What We're Building

A Chrome browser extension with a serverless backend that intercepts text input fields, detects user intent, and rewrites the content into the right output for the right audience — professional English for international recipients, or properly formatted Vietnamese for local contexts (formal emails, government documents, board reports). The extension auto-detects the output language from recipient context. The extension's own interface defaults to Vietnamese for Vietnamese-language browsers.

### 1.2 System Boundary

```
┌─────────────────────────────────────────────────────────┐
│  BROWSER (Chrome Extension - Manifest V3)               │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Content      │  │ Popup UI     │  │ Background    │  │
│  │ Script       │  │ (React)      │  │ Service Worker│  │
│  │ (DOM inject) │  │ + i18n       │  │               │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                 │                  │          │
└─────────┼─────────────────┼──────────────────┼──────────┘
          │                 │                  │
          └─────────────────┼──────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────┐
│  API GATEWAY (AWS API Gateway)                          │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ /rewrite │  │ /auth    │  │ /billing │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │              │              │                   │
└───────┼──────────────┼──────────────┼───────────────────┘
        ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ Rewrite      │ │ Supabase │ │ Stripe /     │
│ Lambda       │ │ Auth     │ │ PayOS        │
│              │ │          │ │              │
│ ┌──────────┐ │ └──────────┘ └──────────────┘
│ │ Rules    │ │
│ │ Engine   │ │
│ ├──────────┤ │  ┌──────────┐
│ │ Intent   │ │  │ Redis    │
│ │ Detector │◄├──┤ Cache    │
│ ├──────────┤ │  └──────────┘
│ │ Cost     │ │
│ │ Router   │ │  ┌──────────┐  ┌──────────┐
│ ├──────────┤ │  │ Claude   │  │ Claude   │
│ │ LLM      │├──►│ Haiku    │  │ Sonnet   │
│ │ Caller   │├──►│          │  │          │
│ └──────────┘ │  └──────────┘  └──────────┘
│              │
│ ┌──────────┐ │  ┌──────────┐
│ │ Quality  │ │  │ Supabase │
│ │ Scorer   │ │  │ Postgres │
│ └──────────┘ │  │ (data)   │
└──────────────┘  └──────────┘

Phase 2 addition (Month 4-6):

┌─────────────────────────────────────────┐
│ Vietnamese NLP Service                   │
│ (ECS t3.medium — PhoNLP + underthesea)  │
│ NER, POS tagging, dependency parsing     │
│ Called only for Vietnamese input          │
└─────────────────────────────────────────┘

Phase 3 addition (Month 6-9):

┌──────────────────┐
│ PhoBERT Intent   │  ← Called only for low-confidence
│ + Slot Service   │    heuristic results (~20% of requests)
│ (Modal/Replicate)│
└──────────────────┘
```

### 1.3 Key Design Principles

- **Latency first.** Under 1s for simple rewrites, under 2s for complex. Every architectural decision is evaluated against this.
- **Margin-aware.** The cost router is not an optimization — it's core infrastructure. Wrong routing kills the business.
- **Vietnamese-first.** The extension speaks Vietnamese to Vietnamese users. The output is professional English. The interface is not.
- **Code-switch native.** Mixed Vietnamese-English input is the primary pattern, not an edge case. Every component handles it.
- **Not a wrapper.** Intent-specific prompts, cultural pattern library, quality scoring, and personal voice memory separate this from "ChatGPT in a Chrome extension." Every feature must widen the gap.
- **Minimal footprint.** Extension must not slow down the browser or interfere with page functionality.
- **Offline-graceful.** Extension degrades gracefully if API is unreachable.
- **Data-as-asset.** Every interaction is instrumented to feed the intent detection evolution pipeline. The product generates its own training data.
- **Earn complexity.** PhoNLP, PhoBERT, and other ML infrastructure are added only when production data justifies them — not at launch.

---

## 2. Architecture

### 2.1 Chrome Extension (Frontend)

**Manifest V3** — required for Chrome Web Store as of 2024. Key implications: no persistent background pages (use service workers), restricted remote code execution, declarativeNetRequest for network rules.

#### 2.1.1 Content Script

Injects into all web pages. Responsibilities:

- **DOM scanning:** Detect active text input fields (`<textarea>`, `<input type="text">`, `contenteditable` divs, CodeMirror/Monaco editors).
- **Vietnamese detection:** Determine if field content contains Vietnamese (per code-switching rules in Section 3.1). Loma button only appears when Vietnamese is detected.
- **Platform detection:** Identify current platform via URL pattern matching and DOM structure.
- **Trigger activation:** Show Loma button (`<loma-button>` Shadow DOM element) when Vietnamese text detected in a focused field with ≥10 characters and ≥38px height.
- **Output injection:** Replace or append rewritten text back into the original field, preserving cursor position, undo history, and text isolation boundaries (signatures, quoted threads).
- **i18n rendering:** All injected UI elements (button tooltips, card labels, toast messages) use the i18n module (Section 3.6) to render in Vietnamese or English based on browser language.

**Platform detection registry (launch):**

| Platform | Detection Method | Special Handling |
|---|---|---|
| Gmail | URL: `mail.google.com` + DOM class `.editable` | Compose window contenteditable div. Text isolation for reply threads/signatures. |
| Slack | URL: `app.slack.com` + `[data-qa="message_input"]` | Rich text editor, character limit awareness |
| GitHub | URL: `github.com` + `<textarea>` with comment/PR context | Markdown-aware output |
| ChatGPT | URL: `chat.openai.com` + `<textarea id="prompt-textarea">` | Prompt optimization mode |
| Claude | URL: `claude.ai` + content editable detection | Prompt optimization mode |
| LinkedIn | URL: `linkedin.com` + message/post composer detection | Tone: Professional default |
| Jira | URL pattern: `*.atlassian.net` + comment/description fields | Technical writing mode |
| Generic | Fallback: any `<textarea>` or `contenteditable` | Standard rewrite |

**Known complexity:** `contenteditable` divs (Gmail, Slack, LinkedIn) are significantly harder to inject into than standard `<textarea>` elements. Each platform's rich text editor has different internal DOM structures, event handling, and undo/redo stacks. This is the single highest-risk frontend engineering task.

#### 2.1.2 Popup UI (React + Tailwind + i18n)

Opened via extension icon click. All text rendered via i18n module (Vietnamese default). Provides:

- Account status (free / PAYG balance)
- Usage stats (rewrites today / this month)
- Per-site enable/disable toggle
- Keyboard shortcut only mode
- Account management links
- UI language override (Vietnamese / English)

**Note:** Rewrite history in popup is Phase 2 (Month 3+, see UX Spec Section 14.3). At launch, popup shows stats only, not a scrollable history list.

#### 2.1.3 Background Service Worker

- Manages auth token refresh (Supabase JWT)
- Handles API communication
- Tracks rewrite count for free tier enforcement (local + server-verified)
- Manages PAYG balance locally with server sync
- Stores original text for undo functionality (5-second TTL per UX Spec Section 3.8)
- Attaches paste detection listener for Copy flow data recovery (Section 3.8 mitigation)

### 2.2 Backend (Serverless)

#### 2.2.1 Why Serverless

- Zero fixed cost at low usage — critical for bootstrapped economics
- Auto-scales with user growth — no capacity planning
- Pay-per-invocation aligns with pay-per-rewrite business model
- Cold start concern mitigated by provisioned concurrency on critical path (rewrite endpoint)

#### 2.2.2 Service Breakdown

| Service | Runtime | Responsibility |
|---|---|---|
| `rewrite-service` | AWS Lambda (Python 3.12) | Core rewrite pipeline: language detection → intent detection → **output language routing** → cost routing → LLM call → quality scoring. Outputs English or formal Vietnamese depending on context. |
| `auth-service` | Supabase Auth (managed) | User registration, login, JWT management |
| `billing-service` | AWS Lambda (Python 3.12) | PAYG balance management, subscription status, webhook handlers |
| `analytics-service` | PostHog (managed) | Event tracking, funnel analysis, retention metrics. All events prefixed `loma_*`. |
| `vn-nlp-service` | AWS ECS (Phase 2, Month 4-6) | PhoNLP + underthesea. Vietnamese NER, POS, dependency parsing. Added when production data justifies it. |
| `intent-model-service` | Modal/Replicate (Phase 3, Month 6-9) | PhoBERT-based intent + slot classification for low-confidence cases |

---

## 3. Component Specifications

### 3.1 Content Script — DOM Injection Engine

**Requirement:** Reliably detect and interact with text input fields across Gmail, Slack, GitHub, ChatGPT, Claude, LinkedIn, Jira, and generic websites without breaking page functionality. Show the Loma button only when Vietnamese content is detected in the field.

**Technical approach:**

```javascript
// Platform detection
const PLATFORM_CONFIGS = {
  'mail.google.com': {
    name: 'gmail',
    selectors: ['div[aria-label="Message Body"]', 'div.editable'],
    type: 'contenteditable',
    defaultTone: 'professional',
    defaultIntent: null,
    defaultOutputLang: null,  // auto-detect from recipient
    recipientSelector: 'input[aria-label="To"]'  // for output language routing
  },
  'app.slack.com': {
    name: 'slack',
    selectors: ['[data-qa="message_input"]', '.ql-editor'],
    type: 'contenteditable',
    defaultTone: 'direct',
    defaultIntent: null,
    defaultOutputLang: 'en'
  },
  'github.com': {
    name: 'github',
    selectors: ['textarea.comment-form-textarea', 'textarea#pull_request_body'],
    type: 'textarea',
    defaultTone: 'direct',
    defaultIntent: 'technical_spec',
    defaultOutputLang: 'en'
  },
  'chat.openai.com': {
    name: 'chatgpt',
    selectors: ['textarea#prompt-textarea', 'div[contenteditable="true"]'],
    type: 'mixed',
    defaultTone: 'direct',
    defaultIntent: 'ai_prompt',
    defaultOutputLang: 'en'
  },
  'zalo.me': {
    name: 'zalo',
    selectors: ['div[contenteditable="true"]'],
    type: 'contenteditable',
    defaultTone: 'direct',
    defaultIntent: null,
    defaultOutputLang: 'vi_casual'
  }
  // ... additional platforms
  // Any .gov.vn domain → defaultOutputLang: 'vi_admin'
};
```

**Vietnamese detection for button visibility (code-switching aware):**

The Loma button appears only when the text field contains Vietnamese content. This must handle code-switched input where Vietnamese and English are mixed.

```javascript
// Vietnamese-specific characters (diacritics unique to Vietnamese)
const VI_CHARS = /[ăắằẳẵặâấầẩẫậđêếềểễệôốồổỗộơớờởỡợưứừửữự]/i;

// Vietnamese function words (high-signal, low false-positive)
const VI_FUNCTION_WORDS = /\b(ơi|ạ|nhé|nha|đã|đang|sẽ|chưa|rồi|cái|của|cho|với|được|không|này|đó|thì|mà|là|và|hay|hoặc|nhưng|nếu|vì|để)\b/i;

function containsVietnamese(text) {
  if (text.length < 10) return false;

  // Strategy 1: Vietnamese-specific diacritics (≥3 occurrences)
  const viCharMatches = (text.match(VI_CHARS) || []).length;
  if (viCharMatches >= 3) return true;

  // Strategy 2: Vietnamese function words (≥2 occurrences)
  const viWordMatches = (text.match(new RegExp(VI_FUNCTION_WORDS.source, 'gi')) || []).length;
  if (viWordMatches >= 2) return true;

  return false;
}

// Language mix ratio (for analytics and intent detection weighting)
function computeLanguageMix(text) {
  const words = text.split(/\s+/).filter(w => w.length > 1);
  const totalWords = words.length;
  if (totalWords === 0) return { vi_ratio: 0, en_ratio: 0 };

  let viWords = 0;
  for (const word of words) {
    if (VI_CHARS.test(word) || VI_FUNCTION_WORDS.test(word)) viWords++;
  }

  return {
    vi_ratio: Math.round((viWords / totalWords) * 100) / 100,
    en_ratio: Math.round(((totalWords - viWords) / totalWords) * 100) / 100
  };
}
```

**Why this approach:**
- Previous spec used `detected_language == "vietnamese"` as a binary gate. Real Vietnamese professional input is 40-60% English by word count due to code-switching ("anh ơi cái KPI report Q4 đã review chưa?").
- A binary Vietnamese/English classifier would oscillate or misclassify code-switched text. Character-based detection is deterministic and handles any mixing ratio.
- `containsVietnamese()` runs on every `input` event (debounced 300ms). Must be <1ms. The regex approach is O(n) and well within budget.

**Overlay UI:** The Loma button (`<loma-button>`, Shadow DOM custom element) appears in the lower-right of the text field when `containsVietnamese()` returns true. See UX Spec Section 3.1 for full button specifications.

**Critical constraints:**
- Must not trigger Content Security Policy violations on target sites
- Must handle dynamic DOM (React/Vue SPAs that re-render input fields)
- Must use MutationObserver for detecting dynamically added text fields
- Must preserve form submission behavior (no event.preventDefault leaks)
- Shadow DOM custom elements: `<loma-button>`, `<loma-card>`, `<loma-toast>`

### 3.2 Rules Engine

**Purpose:** Handle the simplest 30% of rewrites at zero marginal cost.

**Rule categories:**

| Category | Example Input | Rule Applied | Output |
|---|---|---|---|
| Hedging removal | "I just wanted to maybe ask..." | Remove hedging words | "I wanted to ask..." |
| Over-apology | "I'm so sorry to bother you, I'm really sorry but..." | Compress to single apology | "Apologies for the interruption —" |
| Filler removal | "Actually, I think that basically..." | Strip fillers | "I think..." |
| Passive → active | "The report was completed by me" | Simple passive patterns | "I completed the report" |
| Vietnglish fix | "I want to ask you about..." (translated from "Em muốn hỏi...") | Map to natural English via cultural pattern library | "Quick question about..." |
| Sentence splitting | 60+ word run-on sentence | Split at conjunctions | Two clear sentences |

**Implementation:** Regex patterns + replacement rules. No ML, no LLM, no PhoNLP dependency at launch. Stored as a JSON config file that can be updated without redeployment.

**Phase 2 enhancement (Month 4-6):** When PhoNLP is integrated, the rules engine upgrades to POS-enhanced pattern detection. Expected coverage increase: 30% → 35-40% of rewrites. See Section 5 for full PhoNLP integration spec.

**Critical constraint:** Rules engine should only fire when it's confident the rewrite is correct. A bad rules-engine rewrite is worse than routing to Haiku. When in doubt, route up.

### 3.3 Quality Scorer

**Runs on every rewrite output (regardless of routing tier). Provides the quality signal shown in the result card.**

**Phase 1 (launch) — validated metrics only:**

| Output Language | Metric | How Measured | Display |
|---|---|---|---|
| **English** | Length reduction | Character count comparison: input vs output | "Ngắn hơn 52%" |
| **Vietnamese (thân mật/trang trọng)** | Length change | Same formula. If output longer, show "Đầy đủ hơn" | "Ngắn hơn 30%" or "Đầy đủ hơn" |
| **Vietnamese (hành chính)** | Format compliance | Template structure detected (Kính gửi + Căn cứ + Nội dung) | "Đúng format hành chính" |

English length reduction is trivially computed, objectively true, and immediately meaningful. Vietnamese → English professional rewrites typically shorten 30-60%. Vietnamese formal output may be longer than casual input — that's correct behavior, so we show "Đầy đủ hơn" (More complete) instead of a negative percentage. Công văn format compliance is a boolean check against template structure.

**NOT at launch — deferred to Phase 2 Month 3+:**

| Metric | Why Deferred | Phase |
|---|---|---|
| Clarity score (1-10) | Requires validated scoring model calibrated against human raters. Showing uncalibrated scores erodes trust. | Phase 2, Month 3+ after collecting calibration data from `loma_rewrite_accepted` vs `loma_rewrite_dismissed` patterns |
| Authority score (1-10) | Same — hedging count + passive ratio ≠ authority. Needs calibration. | Phase 2, Month 3+ |
| CTA presence flag | Useful but secondary. Intent-specific prompts already produce CTAs. Surfacing a flag adds visual noise without validated accuracy. | Phase 2, Month 3+ |

**Alignment with UX Spec:** UX Spec v1.2 Section 3.7 specifies only `% shorter` at launch. The quality scorer computes all metrics internally for data collection (stored in `rewrites` table for future calibration), but only `length_reduction_pct` is returned to the extension for display.

**Risk flag patterns (internal only at launch — not shown to user):**

| Flag | Detection | Stored For |
|---|---|---|
| Over-apology | 2+ apology phrases in output | Prompt tuning data |
| Hedging | "maybe", "perhaps", "kind of" in non-opinion context | Prompt tuning data |
| Passive voice | >40% of sentences in passive construction | Calibration data |
| Missing CTA | No question mark or action verb in last 2 sentences | Calibration data |
| Too long | Output > 200 words for email/Slack context | Routing feedback |

**Implementation:** Deterministic rules, not LLM-based. Must add zero latency to the rewrite pipeline. Runs as a post-processing step in the same Lambda invocation. All metrics computed and stored; only `length_reduction_pct` returned in API response.

### 3.4 Vietnamese Cultural Mapping Library

**The proprietary asset.** A hand-built JSON library of communication pattern mappings in two directions:

1. **Vietnamese → English:** Transform Vietnamese communication patterns into professional English (launch feature)
2. **Casual Vietnamese → Formal Vietnamese:** Transform casual/rough Vietnamese into properly formatted, formally correct Vietnamese (launch feature)

**Structure (Vietnamese → English — existing):**

```json
{
  "patterns": [
    {
      "id": "vn_formal_opening_001",
      "category": "greeting",
      "direction": "vi_to_en",
      "vietnamese_pattern": "Anh/Chị [name] ơi, em muốn hỏi...",
      "typical_translation": "Dear sir/madam, I would like to ask...",
      "loma_mapping": "Hi [name], quick question:",
      "context": "Informal request to a colleague or mild senior",
      "notes": "Vietnamese uses kinship terms (anh/chị/em) that create false formality in English"
    }
  ]
}
```

**Structure (Casual Vietnamese → Formal Vietnamese — new):**

```json
{
  "patterns": [
    {
      "id": "vn_formal_001",
      "category": "email_to_boss",
      "direction": "vi_to_vi_formal",
      "input_pattern": "anh ơi em xin nghỉ thứ 6",
      "loma_mapping": "Kính gửi Anh [name],\nEm xin phép nghỉ ngày thứ Sáu, [date]. Công việc đã bàn giao cho [colleague].\nTrân trọng,\n[name]",
      "context": "Leave request to direct manager",
      "notes": "Adds proper greeting (Kính gửi), structure (reason + handoff), and closing (Trân trọng). Preserves anh/em relationship."
    },
    {
      "id": "vn_admin_001",
      "category": "cong_van",
      "direction": "vi_to_vi_admin",
      "input_pattern": "cần xin giấy phép kinh doanh",
      "loma_mapping": "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n\nĐƠN ĐỀ NGHỊ CẤP GIẤY CHỨNG NHẬN ĐĂNG KÝ KINH DOANH\n\nKính gửi: Sở Kế hoạch và Đầu tư [Tỉnh/TP]\n\nCăn cứ Luật Doanh nghiệp 2020;\nCăn cứ Nghị định 01/2021/NĐ-CP;\n\n[Tên tổ chức/cá nhân] kính đề nghị Quý Sở xem xét cấp Giấy chứng nhận đăng ký kinh doanh với nội dung sau:\n...",
      "context": "Business registration application",
      "notes": "Fixed template structure. User provides content slots (company name, address, type). Format compliance is the value, not prose quality."
    }
  ]
}
```

**Target at launch:**

| Direction | Pattern count | Categories |
|---|---|---|
| Vietnamese → English | 200+ | Greetings, requests, declining, apologies, feedback, escalation, payment, outreach, technical, general |
| Casual VN → Formal VN | 50+ | Email to boss, email to client, report structure, proposal structure, meeting minutes |
| Casual VN → Admin VN (công văn) | 10-15 templates | Business registration, permit applications, official letters, tax filings, labor contracts |

**Code-switching considerations:** Many patterns will contain mixed Vietnamese-English input. The library must include code-switched variants:

```json
{
  "id": "vn_code_switch_meeting_001",
  "category": "request",
  "vietnamese_pattern": "Anh ơi, cái meeting ngày mai có thể reschedule không?",
  "typical_translation": "Hi, can we reschedule tomorrow's meeting?",
  "loma_mapping": "Hi [name], would it be possible to reschedule tomorrow's meeting?",
  "context": "Request to reschedule. English business terms embedded in Vietnamese syntax.",
  "notes": "Preserve 'meeting' and 'reschedule' — these are standard business English, not translation targets."
}
```

**Build process:** Manual curation by native Vietnamese-English bilingual professional. Cannot be automated — this requires cultural judgment, not translation.

**Maintenance:** Community feedback loop. Users can flag "this rewrite doesn't sound natural" → feeds into pattern review queue.

### 3.5 Cost Router

**Purpose:** Route each rewrite to the cheapest engine that can produce acceptable quality. This is the margin engine of the business.

```python
def route_rewrite(input_text: str, language_mix: dict, intent: str,
                  intent_confidence: float, output_language: str) -> str:
    """
    Returns: "rules" | "haiku" | "sonnet"

    language_mix: {"vi_ratio": 0.6, "en_ratio": 0.4}
    output_language: "en" | "vi_casual" | "vi_formal" | "vi_admin"
    """
    # Vietnamese admin output (công văn) → rules engine + template
    # These are template-driven, not generative
    if output_language == "vi_admin":
        return "rules"

    # Tier 1: Rules engine (zero LLM cost)
    if output_language == "en" and can_rules_handle(input_text):
        return "rules"

    # Tier 2: Haiku (cheap LLM)
    # Pure English rough text → Haiku can handle
    if language_mix["vi_ratio"] < 0.1 and intent == "general":
        return "haiku"
    # Short, low-complexity text regardless of language mix
    if len(input_text) < 100 and intent in LOW_COMPLEXITY_INTENTS:
        return "haiku"
    # Vietnamese casual/formal rewrites of short text
    if output_language in ("vi_casual", "vi_formal") and len(input_text) < 150:
        return "haiku"

    # Tier 3: Sonnet (expensive LLM)
    # Vietnamese or code-switched text, complex intents → Sonnet
    return "sonnet"
```

**Key change from v1.4:** The router now accepts `output_language` parameter. Công văn (vi_admin) output routes to rules engine because it's template-driven — the structure is fixed, only content slots change. This keeps the highest-value Vietnamese feature at zero marginal cost. Vietnamese casual/formal short text routes to Haiku, which is sufficient for formality upgrades on simple content.

**LOW_COMPLEXITY_INTENTS:** `["follow_up", "general"]` — these tend to be short, pattern-based, and don't require deep cultural mapping.

**LLM prompt instruction for code-switched input:**

When the rewrite Lambda builds the LLM prompt for code-switched text, it includes:

```
INSTRUCTION: The input contains mixed Vietnamese and English (code-switching).
- PRESERVE standard English business terms that appear in the original
  (e.g., "KPI", "meeting", "deadline", "budget", "report").
- TRANSFORM Vietnamese syntax and connector words into English.
- Do NOT translate English words that are already correct — only
  restructure the sentence around them.
```

This instruction is appended to the system prompt when `language_mix.vi_ratio` is between 0.1 and 0.9. Pure Vietnamese (>0.9) and pure English (<0.1) use standard prompts.

**Monitoring:** Track acceptance rates by routing tier AND by language mix ratio. If code-switched text routed to Haiku shows lower acceptance than Sonnet-routed, tighten the threshold.

### 3.6 Internationalization Module (i18n)

**NEW IN v1.4.** The extension's own UI defaults to Vietnamese when the browser language is `vi`. This is core product-market fit per UX Spec Section 1.4.

**Detection:**

```javascript
function getUILanguage() {
  // User override takes priority
  const override = chrome.storage.local.get('ui_language');
  if (override) return override;

  // Browser language detection
  return navigator.language.startsWith('vi') ? 'vi' : 'en';
}
```

**String lookup:**

```javascript
import VI_STRINGS from './strings/vi.json';
import EN_STRINGS from './strings/en.json';

const STRINGS = { vi: VI_STRINGS, en: EN_STRINGS };
let currentLocale = getUILanguage();

export function t(key) {
  return STRINGS[currentLocale]?.[key] || STRINGS['en'][key] || key;
}

// Usage: t('btn_use') → "✓ Dùng" (vi) or "✓ Use" (en)
```

**String table:** See UX Spec v1.2 Section 1.4 for the complete table of 50+ keys covering: quick-pick labels, action buttons, tone options, loading microcopy, error messages, FTUX text, popup labels, accessibility labels, undo/copy toasts.

**Implementation notes:**
- Single `i18n.js` module, imported by content script, popup, and FTUX page
- All user-facing strings reference keys via `t()`, never hardcoded text
- Chrome's `chrome.i18n` API is an option but adds `_locales/` folder complexity. The simpler runtime lookup above is preferred for speed.
- String files are JSON: `strings/vi.json`, `strings/en.json`
- **What is NOT translated:** The rewrite output language is determined by output language routing (Section 3.7), not by UI language. The UI is always Vietnamese for `vi` browsers. The intent badge in the result card shows dual labels: Vietnamese first, English second (e.g., "🎯 Nhắc thanh toán · Payment follow-up") for English output, or Vietnamese-only (e.g., "📜 Văn bản hành chính") for Vietnamese output.
- i18n module MUST be built before the result card (Week 3-4 Priority 2) because all card strings depend on it.

**Build effort:** ~4 hours for the module + string files. The strings are already defined in UX Spec v1.3 Section 1.4.

### 3.7 Output Language Router

**NEW IN v1.5.** Determines whether the rewrite output should be English or Vietnamese, and at what formality level. Runs client-side before the API call.

**Output language values:**

| Value | Meaning | Prompt set used |
|---|---|---|
| `en` | Professional English (default) | English intent prompts × 4 tones |
| `vi_casual` | Collegial Vietnamese (thân mật) | Vietnamese intent prompts × thân mật formality |
| `vi_formal` | Formal Vietnamese (trang trọng) | Vietnamese intent prompts × trang trọng formality |
| `vi_admin` | Administrative Vietnamese (hành chính) | Công văn templates — rules engine, no LLM |

**Detection logic (client-side, runs before API call):**

```javascript
function detectOutputLanguage(platform, inputText, recipientEmail, storedPrefs) {
  // Priority 1: User's stored per-domain preference
  const domainKey = getDomainKey(platform, recipientEmail);
  if (storedPrefs[domainKey]) return storedPrefs[domainKey];

  // Priority 2: Government portal detection
  if (window.location.hostname.endsWith('.gov.vn')) return 'vi_admin';

  // Priority 3: Recipient email domain
  if (recipientEmail && recipientEmail.endsWith('.gov.vn')) return 'vi_admin';

  // Priority 4: Vietnamese formal keywords in input
  const VI_FORMAL_KEYWORDS = /kính gửi|căn cứ|đề nghị|trân trọng|báo cáo tổng kết|công văn/i;
  if (VI_FORMAL_KEYWORDS.test(inputText)) return 'vi_formal';

  // Priority 5: Vietnamese-only platforms
  if (['zalo.me'].includes(window.location.hostname)) return 'vi_casual';

  // Priority 6: Default
  return 'en';
}
```

**Recipient email extraction (Gmail only):**

```javascript
function getRecipientEmail() {
  // Gmail compose: extract from the "To" field
  const toField = document.querySelector('input[aria-label="To"]');
  if (!toField) return null;
  const emails = toField.value.match(/[\w.-]+@[\w.-]+\.\w+/g);
  return emails ? emails[0] : null;
}
```

**Per-domain memory:** After a manual override via the tone selector (UX Spec Section 3.8), store the preference:

```javascript
// Stored in chrome.storage.local
const domainPrefs = {
  "mail.google.com|vn-gov@skhdt.hanoi.gov.vn": "vi_admin",
  "zalo.me": "vi_casual",
  "slack.com": "en"
};
```

**API call change:** The `output_language` value is sent to the `/rewrite` endpoint as a new required parameter. The backend uses it to select the correct prompt template set and, for `vi_admin`, to bypass LLM and use template filling.

**Build effort:** ~6 hours. Mostly the Gmail recipient extraction (DOM parsing is fragile, needs testing). Output language selection logic is simple. Per-domain storage is a thin wrapper around `chrome.storage.local`.

---

## 4. Differentiation & Benchmark System

### 4.1 The Wrapper Problem

At launch, Loma uses Claude's API to generate rewrites. Any technical reviewer would observe that the core rewrite generation is "Claude with a system prompt." This section specifies exactly what makes Loma not a wrapper — and how we prove it publicly.

**The wrapper test:** If Anthropic's API disappeared tomorrow, what would Loma retain?

| Component | Survives Without Claude API? | Explanation |
|---|---|---|
| Intent detection (14 workflows) | ✅ Yes | Keyword heuristics, no LLM dependency |
| Cultural pattern library (250+ patterns) | ✅ Yes | Proprietary hand-built knowledge base, both directions |
| Rules engine (30% of rewrites) | ✅ Yes | Regex patterns + công văn templates, zero LLM cost |
| Output language auto-detection | ✅ Yes | Client-side logic, no API dependency |
| Quality scorer | ✅ Yes | Deterministic scoring, no LLM |
| Vietnamese-first UX + i18n | ✅ Yes | Pure frontend, no API dependency |
| Code-switching detection | ✅ Yes | Client-side regex, no API dependency |
| Công văn template library | ✅ Yes | Rules-based templates, no LLM needed |
| Personal voice memory (Phase 2) | ✅ Yes | User preference database |
| Labeled intent dataset (growing) | ✅ Yes | Proprietary training data |
| Inline browser UX (1-click rewrite) | ✅ Yes | Chrome extension, no API dependency |
| LLM-generated rewrites (70% of rewrites) | ❌ No | Needs an LLM — but could swap to GPT-4, Gemini, or Llama within 1 day |

**Conclusion:** 10 of 11 value layers survive. The LLM is a replaceable component, not the product. The intent detection, cultural mapping, công văn templates, output language routing, i18n, code-switching detection, personal voice, quality scoring, and UX are the product.

### 4.2 Six Layers of Differentiation

**Layer 1: Speed (Day 1 — 15x faster workflow)**

```
ChatGPT workflow:
  Open tab → navigate → type prompt → "rewrite this professionally:
  [paste text]" → wait → copy → switch back → paste
  Total: 30-45 seconds, 8+ actions

Loma workflow:
  Type in Gmail/Slack → tap Loma button → done
  Total: 2 seconds, 1 action
```

This is not a moat. But for a professional sending 20+ emails/day, it saves 10-15 minutes daily.

**Layer 2: Intent-Specific Prompts (Day 1 — structurally different output)**

When a user tells ChatGPT "rewrite this professionally," ChatGPT doesn't know if they're declining a request, following up on a payment, or escalating to a manager. Loma's 14 intent workflows (10 universal + 4 Vietnamese-specific) each produce structurally different output:

```
Same input: "anh ơi cái invoice tháng trước chưa thanh toán"

ChatGPT (generic prompt):
"I would like to kindly remind you about the invoice
from last month that has not yet been settled."
→ Passive. No CTA. No deadline. Hedging.

Loma (ask_payment intent, auto-detected):
"Hi [name], following up on last month's invoice — now
overdue. Could you confirm the expected payment date
by end of this week?"
→ Direct. Clear CTA. Deadline. Professional but firm.
```

The user never writes a prompt. They just type and tap. The system detects intent and selects the appropriate workflow.

**Layer 3: Cultural Pattern Library (Day 1 — Vietnamese-specific edge)**

250+ hand-curated communication pattern transformations in two directions: Vietnamese → English (cultural norms translation) and casual Vietnamese → formal Vietnamese (formality upgrade + template compliance). This is the asset no generic LLM replicates.

```
Vietnamese pattern: Triple apology opening
"Em xin lỗi anh, em rất tiếc, em sorry về việc trễ deadline..."

ChatGPT: "I'm so sorry, I really apologize, I'm sorry
about missing the deadline..."
→ Faithfully translated. Preserved the cultural pattern.
→ Reads as insecure and overly submissive in Western context.

Loma: "Apologies for the delay on the deadline.
Here's my plan to get back on track:"
→ One clean apology. Forward-looking. Authoritative.
→ Cultural pattern recognized and transformed, not translated.
```

**Why ChatGPT can't do this even with a great prompt:** ChatGPT's training data teaches it that accurate translation preserves meaning. Preserving a triple apology IS preserving meaning — in Vietnamese. The problem is that the meaning changes in Western professional context. Loma's cultural library explicitly maps these patterns.

**Layer 4: Dual-Language Output (Day 1 — category expansion)**

Neither Grammarly nor ChatGPT auto-detects whether the user needs English or Vietnamese output. Loma does. English email to a client → professional English. Công văn to a government agency → correctly formatted administrative Vietnamese. Email to sếp → formal Vietnamese with proper honorifics. This doubles the addressable use cases per user without adding user friction (no toggle, auto-detected).

The công văn template engine is particularly defensible: government document formatting is rules-based (fixed structure, specific legal citations, precise formatting requirements). This means the highest-value Vietnamese feature runs at zero marginal cost through the rules engine, not the LLM.

**Layer 5: Data Flywheel (Month 3+ — compounding moat)**

Every rewrite generates a labeled data point:
- Input text + language mix ratio + detected language
- Auto-detected intent + user-confirmed intent (training label)
- Accepted / rejected / edited-then-accepted
- User's final edited text (implicit quality feedback)
- Platform + tone context

By Month 6: 8,000+ labeled Vietnamese professional communication examples. By Month 12: 25,000+. This dataset doesn't exist anywhere else.

**Layer 6: Personal Voice Memory (Month 4+ — retention moat)**

After 200+ rewrites, Loma learns individual preferences:
- User A always changes "Regards" to "Best"
- User B prefers shorter sentences and never uses exclamation marks
- User C uses "Hi" for internal emails but "Dear" for external

These preferences are applied automatically. The rewrite feels like "my English, but better." ChatGPT has no cross-session memory of your writing style at this granularity.

### 4.3 Benchmark System (Public Proof)

**Landing page: 50 real-world scenarios, three-column comparison**

| Column | Source | How Generated |
|---|---|---|
| **Raw ChatGPT** | ChatGPT-4 with prompt: "Rewrite this professionally" | One-time generation, refreshed quarterly |
| **Raw Claude** | Claude Sonnet with same generic prompt | One-time generation, refreshed quarterly |
| **Loma** | Loma with auto-detected intent + cultural mapping | Live API call (cached for performance) |

**50 scenarios organized by intent (5 per intent):**

| Intent | Example Scenarios |
|---|---|
| **Request from senior** | Email to VP asking budget approval; Slack to skip-level manager; Request for deadline extension |
| **Follow up** | Overdue invoice follow-up; Unanswered email after 1 week; Status check on deliverable |
| **AI prompt** | ChatGPT prompt for code review; Claude prompt for analysis; GitHub Copilot instruction |
| **Say no** | Declining meeting request; Rejecting vendor proposal; Pushing back on unrealistic deadline |
| **Cold outreach** | LinkedIn connection request; Partnership pitch email; Conference speaker introduction |
| **Ask payment** | Invoice 2 weeks overdue; Second reminder for large amount; Final notice before escalation |
| **Give feedback** | Quarterly performance review; Code review comment; Project post-mortem note |
| **Disagree** | Technical architecture disagreement; Budget allocation pushback; Process change objection |
| **Escalate** | Blocked on dependency; Critical bug report to management; Vendor SLA breach |
| **Apologize** | Missed deadline apology; Data error acknowledgment; Client service failure |

**Benchmark includes code-switched scenarios:** At least 10 of the 50 scenarios use code-switched Vietnamese-English input (e.g., "anh ơi cái KPI report Q4 cần update lại theo new headcount plan"). This tests both intent detection accuracy on mixed input and the rewrite engine's ability to preserve English business terms.

**Scoring criteria for each comparison:**

| Criterion | What We Check | Weight |
|---|---|---|
| **Cultural accuracy** | Did it transform Vietnamese patterns or just translate them? | 30% |
| **Structural completeness** | CTA present? Deadline stated? Subject clear? | 25% |
| **Tone calibration** | Matches the intent (firm for payment, warm for outreach)? | 20% |
| **Entity preservation** | Names, orgs, amounts correctly rendered? | 15% |
| **Conciseness** | Shorter = better for professional communication? | 10% |

### 4.4 In-Product Quality Signals

After every rewrite, the result card shows (per UX Spec Section 3.4):

```
┌──────────────────────────────────────────────────────┐
│ 🎯 Nhắc thanh toán · Payment follow-up       ✕      │
│                                                      │
│ ▸ Xem bản gốc                                       │
│                                                      │
│ "Hi Minh, following up on VinAI's January           │
│ invoice for $5,000, now 2 weeks past due.           │
│ Could you confirm the expected payment date          │
│ by Friday?"                                          │
│                                                      │
│ ✂️ Ngắn hơn 52%                                      │
│                                                      │
│ [✓ Dùng] [📋 Sao chép] [↻ Đổi giọng]               │
└──────────────────────────────────────────────────────┘
```

**What each signal communicates:**
- **Intent badge (Vietnamese + English):** "We understood what you're trying to do" — in your language.
- **Show original toggle:** "You can verify we got your meaning right."
- **Length reduction:** "We made it concise for you."
- **Vietnamese action buttons:** "This tool was built for you."

None of these exist in ChatGPT or Claude.

### 4.5 "Why Not ChatGPT?" Page

```
"Vâng, bạn có thể dùng ChatGPT. Đây là lý do chuyên gia chuyển sang Loma:"

1. ChatGPT doesn't know you're declining a request vs. asking for payment.
   Loma detects your intent and writes accordingly.

2. ChatGPT preserves your Vietnamese communication patterns.
   Loma transforms them into Western professional norms.

3. ChatGPT requires you to context-switch, copy-paste, and prompt-engineer.
   Loma works inside Gmail/Slack/GitHub with one tap.

4. ChatGPT costs $20/month for general AI.
   Loma costs ₫99k/month for professional English, specifically.

5. ChatGPT doesn't learn your writing style.
   By Month 2, Loma remembers that you prefer "Best" over "Regards."
```

---

## 5. Vietnamese NLP Layer — PhoNLP (Phase 2: Month 4-6)

> **NOT LAUNCH SCOPE.** This section documents a planned Phase 2 enhancement. At launch, the rewrite pipeline uses Claude's native Vietnamese understanding + keyword heuristics + regex rules. PhoNLP is added only when production data shows specific failure modes that justify the $30/month infrastructure cost and integration effort.
>
> **Trigger criteria for adding PhoNLP:**
> - Claude is mangling Vietnamese names >5% of the time → add NER pre-extraction
> - Rules engine false positive rate >15% → add POS-enhanced pattern detection
> - Intent heuristic accuracy plateaus below 78% → add dependency parse features
> - Any single trigger met = begin integration (estimated 1-2 weeks)

**Why this exists:** Vietnamese input requires structural understanding that English NLP tools and LLM tokenizers don't provide. Vietnamese has no spaces between words (word segmentation required), uses kinship-based pronouns that carry hierarchical meaning, and has grammatical structures that directly map to communication intent. PhoNLP gives us this understanding at zero LLM cost.

**License:** BSD-3-Clause (commercially permissive). No copyleft, no open-source obligation.

**What PhoNLP provides:**

| Capability | What It Does | Example | How Loma Uses It |
|---|---|---|---|
| **POS tagging** | Labels each word's grammatical role | "Tôi/P đang/R làm_việc/V" | Rules engine: reliable passive voice, hedging, filler detection |
| **NER** | Extracts named entities (person, org, location) | "Minh" → B-PER, "VinAI" → B-ORG | Structured slot extraction for LLM prompts; entity preservation in rewrites |
| **Dependency parsing** | Maps grammatical relationships between words | "Tôi" → subject of "làm_việc" | Sentence structure analysis, clause splitting, intent signal extraction |

### 5.1 Pipeline Architecture

```
Vietnamese Input (raw text)
    │
    ▼
┌─────────────────────────────────┐
│ Language Detection               │  ← If pure English (vi_ratio < 0.1) → skip VN NLP
│ (containsVietnamese() +         │  ← If Vietnamese or code-switched → continue below
│  computeLanguageMix())          │
└──────────┬──────────────────────┘
           ▼
┌─────────────────────────────────┐
│ Word Segmentation                │  ← Vietnamese has no word boundaries
│ (underthesea, MIT license)       │  ← "Ông Nguyễn Khắc Chúc đang làm việc"
│                                  │  → "Ông Nguyễn_Khắc_Chúc đang làm_việc"
│                                  │
│ Code-switch handling:            │
│ English words pass through       │
│ unsegmented. Only Vietnamese     │
│ portions are word-segmented.     │
└──────────┬──────────────────────┘
           ▼
┌─────────────────────────────────┐
│ PhoNLP Analysis                  │
│                                  │
│ Input:  Word-segmented sentence  │
│ Output: Per-token annotations    │
│                                  │
│ ┌──────┬─────┬─────┬─────┬────┐ │
│ │ Word │ POS │ NER │ Head│ Dep│ │
│ ├──────┼─────┼─────┼─────┼────┤ │
│ │ Ông  │ Nc  │ O   │ 2   │det │ │
│ │Nguyễn│ Np  │B-PER│ 0   │root│ │
│ │_Khắc │     │     │     │    │ │
│ │_Chúc │     │I-PER│     │    │ │
│ │ đang │ R   │ O   │ 4   │adv │ │
│ │làm_  │ V   │ O   │ 2   │vmod│ │
│ │việc  │     │     │     │    │ │
│ │ tại  │ E   │ O   │ 4   │loc │ │
│ │VinAI │ Np  │B-ORG│ 5   │pobj│ │
│ └──────┴─────┴─────┴─────┴────┘ │
└──────────┬──────────────────────┘
           ▼
┌─────────────────────────────────┐
│ NLP Analysis Object              │
│ (passed to intent detector,      │
│  rules engine, cost router,      │
│  and LLM prompt builder)         │
│                                  │
│ {                                │
│   "tokens": [...],               │
│   "pos_tags": ["Nc","Np",...],   │
│   "ner_entities": [              │
│     {"text":"Nguyễn Khắc Chúc",  │
│      "label":"PER","start":0},   │
│     {"text":"VinAI",             │
│      "label":"ORG","start":5}    │
│   ],                             │
│   "dep_parse": [...],            │
│   "sentence_count": 1,           │
│   "complexity_score": 0.35,      │
│   "has_named_entities": true     │
│ }                                │
└─────────────────────────────────┘
```

**Critical design decision:** PhoNLP runs ONLY on Vietnamese-detected input (vi_ratio ≥ 0.1). Pure English input bypasses the VN NLP layer entirely. This keeps latency low and avoids paying PhoNLP inference cost on text it wasn't trained for.

### 5.2 NER for Structured LLM Prompts

**This is the highest-impact PhoNLP feature.** Pre-trained model, zero custom training, immediate value.

**Problem without NER:** The LLM receives raw Vietnamese text and must figure out which words are names, which are organizations, which are common nouns. Vietnamese proper nouns are especially tricky — "Lan" is both a common word (orchid) and a name. LLMs regularly mangle Vietnamese names in rewrites.

**Solution with NER:**

```python
def build_rewrite_prompt(input_text: str, intent: str, tone: str,
                         nlp_analysis: dict, language_mix: dict) -> str:
    entities = nlp_analysis.get("ner_entities", [])
    persons = [e for e in entities if e["label"] == "PER"]
    orgs = [e for e in entities if e["label"] == "ORG"]
    locations = [e for e in entities if e["label"] == "LOC"]

    entity_context = ""
    if persons:
        entity_context += f"People mentioned: {', '.join(p['text'] for p in persons)}\n"
    if orgs:
        entity_context += f"Organizations: {', '.join(o['text'] for o in orgs)}\n"
    if locations:
        entity_context += f"Locations: {', '.join(l['text'] for l in locations)}\n"

    # Code-switch instruction (when input is mixed)
    code_switch_instruction = ""
    if 0.1 < language_mix.get("vi_ratio", 0) < 0.9:
        code_switch_instruction = (
            "\nIMPORTANT: The input contains mixed Vietnamese and English. "
            "Preserve standard English business terms from the original. "
            "Transform Vietnamese syntax and connectors into English.\n"
        )

    prompt = f"""Rewrite the following as a professional {tone} {intent_to_description(intent)}.

{entity_context}{code_switch_instruction}
IMPORTANT: Preserve all names and organization names exactly as listed above.

Original text: {input_text}

Rewritten:"""
    return prompt
```

### 5.3 Dependency Parsing for Intent Signals

Dependency parse features feed into the intent heuristic engine to improve accuracy from Phase 2 onward.

| Parse Feature | What It Reveals | Intent Signal |
|---|---|---|
| Subject is 1st person ("em/tôi") + object is 2nd person ("anh/chị") | I'm addressing someone senior | Boosts `request_senior` |
| Main verb is imperative mood | Direct request or instruction | Boosts `give_feedback`, `escalate_issue` |
| Negation modifying main verb ("không/chưa") | Refusing or reporting absence | Boosts `say_no`, `follow_up` |
| Multiple independent clauses joined by "nhưng/tuy nhiên" | Contrast/disagreement structure | Boosts `disagree_respectfully` |
| Sentence has question structure (interrogative) | Asking, not telling | Distinguishes `request_senior` from `give_feedback` |
| Temporal adverb ("quá hạn", "đã lâu") modifying financial verb | Payment urgency | Boosts `ask_payment` confidence |

### 5.4 Deployment: Vietnamese NLP Service

**Chosen approach: Dedicated ECS service.**

| Property | Value |
|---|---|
| Runtime | AWS ECS Fargate (or EC2-backed for cost savings) |
| Instance | t3.medium (2 vCPU, 4GB RAM) |
| Region | ap-southeast-1 (Singapore) |
| Always running | Yes — 1 task minimum |
| Internal endpoint | `http://vn-nlp.internal:8000/analyze` |
| Protocol | REST (JSON) |
| Latency | ~80-150ms per sentence |
| Monthly cost | ~$30-35 (t3.medium on-demand, or ~$20 reserved) |

**Service API:**

```
POST /analyze
Request:
{
    "text": "Anh Minh ở VinAI chưa thanh toán invoice",
    "tasks": ["segment", "pos", "ner", "dep"],
    "language_mix": {"vi_ratio": 0.7, "en_ratio": 0.3}
}

Response:
{
    "segmented_text": "Anh Minh ở VinAI chưa thanh_toán invoice",
    "tokens": [...],
    "ner_entities": [
        {"text": "Minh", "label": "PER", "start": 1, "end": 1},
        {"text": "VinAI", "label": "ORG", "start": 3, "end": 3}
    ],
    "complexity_score": 0.35,
    "processing_time_ms": 95
}
```

**Caching:** PhoNLP analysis results are cached in Redis. Expected cache hit rate: 10-15%.

### 5.5 Graceful Degradation

If the VN NLP service is unreachable, the rewrite pipeline falls back to pre-PhoNLP behavior:
- Rules engine uses regex patterns instead of POS-enhanced patterns
- Intent detection uses keyword heuristics without structural features
- LLM prompts use raw text without entity extraction
- Quality: slightly degraded but product remains functional
- Alert: CloudWatch alarm triggers on VN NLP service health check failure

PhoNLP is an enhancement layer, not a critical dependency.

### 5.6 VnCoreNLP vs. underthesea Decision

| Criterion | VnCoreNLP | underthesea | Decision |
|---|---|---|---|
| **License** | GPL-3.0 ⚠️ | MIT ✅ | underthesea — no copyleft risk |
| **Language** | Java (requires JVM) | Pure Python | underthesea — simpler ops |
| **Accuracy** | Slightly higher F1 on word segmentation | ~1-2% lower F1 | Acceptable trade-off |
| **Memory** | JVM overhead (~500MB) | ~200MB | underthesea — fits smaller instance |
| **Maintenance** | Last updated 2022 | Actively maintained | underthesea |

**Decision: underthesea for word segmentation + PhoNLP for analysis.**

---

## 6. Intent Detection System — 4-Phase Evolution

This is the most strategically important technical system in Loma. It evolves from simple keyword matching at launch to a PhoBERT-based joint intent + slot model by month 9.

**Launch approach:** Keyword heuristics only. No PhoNLP, no ML models. ~70% accuracy, ships in days. Users correct with 1 tap — every correction becomes training data.

**Phase 2 (Month 4-6):** PhoNLP structural features boost heuristic accuracy on Vietnamese input to ~75-78%.

**Research foundation:** VinAI's JointIDSF (INTERSPEECH 2021) demonstrates joint intent detection + slot filling with PhoBERT achieves strong results on Vietnamese text. Loma adapts this architecture pattern using proprietary training data generated by the product itself.

### Phase 1: Keyword Heuristics (Launch — Month 3)

**Why:** Ships in days, not weeks. Zero infrastructure cost. Good enough at ~70% accuracy. Bad intent suggestions are recoverable — user taps to change.

**Implementation (updated for code-switching support):**

```python
INTENT_PATTERNS = {
    "request_senior": {
        "vi_signals": ["anh ơi", "chị ơi", "xin phép", "cho em hỏi", "nhờ anh/chị"],
        "en_signals": ["could you please", "would it be possible", "I was wondering if",
                       "sorry to bother", "if you have time"],
        "en_business_signals": ["approve", "permission", "sign off", "greenlight"],
        "context_signals": ["boss", "manager", "director", "lead"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.6
    },
    "say_no": {
        "vi_signals": ["không được", "khó", "em nghĩ", "chưa phù hợp"],
        "en_signals": ["unfortunately", "not able to", "difficult to", "I don't think",
                       "not sure if we can"],
        "en_business_signals": ["decline", "reject", "cannot accommodate", "pass on"],
        "context_signals": ["decline", "reject", "cannot"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.6
    },
    "follow_up": {
        "vi_signals": ["chưa nhận được", "nhắc lại", "theo dõi"],
        "en_signals": ["following up", "just checking", "any update", "circling back",
                       "wanted to check", "haven't heard"],
        "en_business_signals": ["status", "ETA", "timeline", "progress", "pending"],
        "context_signals": ["reminder", "pending", "waiting"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.7
    },
    "ask_payment": {
        "vi_signals": ["thanh toán", "hóa đơn", "chưa nhận", "quá hạn"],
        "en_signals": ["invoice", "payment", "overdue", "outstanding", "balance due"],
        "en_business_signals": ["remittance", "wire transfer", "net 30", "past due",
                                "accounts receivable"],
        "context_signals": ["amount", "due date", "$", "USD", "VND"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.7
    },
    "ai_prompt": {
        "vi_signals": ["viết code", "tạo", "giải thích", "phân tích"],
        "en_signals": ["write a function", "create", "explain", "analyze", "generate",
                       "help me", "build"],
        "en_business_signals": [],
        "platform_signals": ["chatgpt", "claude"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.5
    },
    "disagree_respectfully": {
        "vi_signals": ["em nghĩ khác", "không đồng ý", "theo em"],
        "en_signals": ["I disagree", "I think differently", "not sure I agree",
                       "my concern is", "I see it differently"],
        "en_business_signals": ["pushback", "counterpoint", "alternative view",
                                "respectfully disagree"],
        "context_signals": ["but", "however", "concern"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.6
    },
    "give_feedback": {
        "vi_signals": ["đánh giá", "nhận xét", "góp ý", "cải thiện"],
        "en_signals": ["feedback", "review", "performance", "improve", "suggestion",
                       "you did", "your work"],
        "en_business_signals": ["KPI", "OKR", "performance review", "360 feedback",
                                "areas for improvement"],
        "context_signals": ["strengths", "areas", "development"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.6
    },
    "cold_outreach": {
        "vi_signals": ["giới thiệu", "hợp tác", "liên hệ", "đề xuất"],
        "en_signals": ["reaching out", "introduce", "partnership", "opportunity",
                       "connect", "I came across"],
        "en_business_signals": ["collaboration", "synergy", "proposal", "explore"],
        "context_signals": ["company", "product", "service"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.6
    },
    "escalate_issue": {
        "vi_signals": ["báo cáo", "vấn đề nghiêm trọng", "cần xử lý gấp"],
        "en_signals": ["escalate", "urgent", "critical issue", "blocked",
                       "needs attention", "raising this"],
        "en_business_signals": ["blocker", "showstopper", "P0", "SLA breach",
                                "at risk", "red flag"],
        "context_signals": ["impact", "deadline", "risk"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.7
    },
    "apologize_with_authority": {
        "vi_signals": ["xin lỗi", "em rất tiếc", "lỗi của em"],
        "en_signals": ["sorry", "apologize", "my mistake", "my fault", "oversight",
                       "I should have"],
        "en_business_signals": ["accountability", "corrective action", "root cause",
                                "won't happen again"],
        "context_signals": ["mistake", "error", "delayed", "missed"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.7
    },

    # ── Vietnamese output intents (new in v1.5) ──
    # These intents trigger Vietnamese output instead of English.
    # They are only scored when output_language is vi_* or undetermined.

    "write_to_gov": {
        "vi_signals": ["kính gửi", "căn cứ", "đề nghị", "sở", "ủy ban",
                       "giấy phép", "đăng ký", "cơ quan", "nghị định", "thông tư"],
        "en_signals": [],
        "en_business_signals": [],
        "context_signals": [".gov.vn"],
        "vi_weight": 2.0,
        "en_weight": 0,
        "confidence_threshold": 0.5,
        "output_language": "vi_admin"
    },
    "write_formal_vn": {
        "vi_signals": ["kính gửi", "trân trọng", "xin phép", "báo cáo",
                       "kính mời", "thưa", "quý anh/chị"],
        "en_signals": [],
        "en_business_signals": [],
        "context_signals": ["sếp", "giám đốc", "trưởng phòng", "ban lãnh đạo"],
        "vi_weight": 2.0,
        "en_weight": 0,
        "confidence_threshold": 0.5,
        "output_language": "vi_formal"
    },
    "write_report_vn": {
        "vi_signals": ["báo cáo", "tổng kết", "kết quả", "tình hình",
                       "đánh giá", "phân tích", "quý", "tháng"],
        "en_signals": [],
        "en_business_signals": ["KPI", "OKR", "Q1", "Q2", "Q3", "Q4"],
        "context_signals": ["kết quả", "mục tiêu", "tiến độ"],
        "vi_weight": 1.5,
        "en_weight": 0.5,
        "confidence_threshold": 0.6,
        "output_language": "vi_formal"
    },
    "write_proposal_vn": {
        "vi_signals": ["đề xuất", "kiến nghị", "phương án", "kế hoạch",
                       "ngân sách", "triển khai", "mục tiêu"],
        "en_signals": [],
        "en_business_signals": ["budget", "timeline", "ROI", "headcount"],
        "context_signals": ["duyệt", "phê duyệt", "xin ý kiến"],
        "vi_weight": 1.5,
        "en_weight": 0.5,
        "confidence_threshold": 0.6,
        "output_language": "vi_formal"
    }
}
```

**Key change from v1.3 — code-switching support:**

1. **Added `en_business_signals`** — English business vocabulary that appears in code-switched Vietnamese text. These are high-signal keywords that indicate intent even when embedded in Vietnamese syntax: "KPI", "SLA breach", "past due", "performance review", etc.

2. **Added `vi_weight` and `en_weight`** — Vietnamese keywords weighted 1.5x, English keywords weighted 1.0x. Rationale: Vietnamese keywords show stronger intent signal in code-switched context because they represent the user's deliberate word choice, while English business terms are often borrowed vocabulary that may appear across multiple intent categories.

3. **Scoring algorithm (updated):**

```python
def compute_intent_scores(input_text: str, language_mix: dict, platform: str) -> dict:
    """
    Returns: {"intent": str, "confidence": float}
    """
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0.0
        total_possible = 0.0

        # Vietnamese signals
        vi_weight = patterns.get("vi_weight", 1.5)
        for signal in patterns["vi_signals"]:
            total_possible += vi_weight
            if signal.lower() in input_text.lower():
                score += vi_weight

        # English signals (general + business)
        en_weight = patterns.get("en_weight", 1.0)
        all_en_signals = patterns["en_signals"] + patterns.get("en_business_signals", [])
        for signal in all_en_signals:
            total_possible += en_weight
            if signal.lower() in input_text.lower():
                score += en_weight

        # Context signals (platform + content)
        for signal in patterns.get("context_signals", []):
            total_possible += 1.0
            if signal.lower() in input_text.lower():
                score += 1.0

        # Platform bonus
        if intent == "ai_prompt" and platform in ["chatgpt", "claude"]:
            score += 2.0

        normalized = score / max(total_possible, 1.0)
        scores[intent] = normalized

    best_intent = max(scores, key=scores.get)
    confidence = scores[best_intent]

    threshold = INTENT_PATTERNS[best_intent]["confidence_threshold"]
    if confidence < threshold:
        return {"intent": "general", "confidence": confidence, "output_language": None}

    # Vietnamese output intents carry their own output_language
    output_lang = INTENT_PATTERNS[best_intent].get("output_language", None)
    return {"intent": best_intent, "confidence": confidence, "output_language": output_lang}
```

**Vietnamese intent interaction with output language router:** If intent detection returns an `output_language` value (e.g., `write_to_gov` → `vi_admin`), this overrides the client-side output language auto-detection from Section 3.7. The intent system is a stronger signal than domain heuristics because it reads the user's actual content.

**Data collection (critical):** Every rewrite logs `detected_intent`, `intent_confidence`, `user_confirmed_intent`, `intent_was_auto_detected`, and `language_mix`. This is the training data pipeline for Phase 3.

**Performance:** ~20ms per classification. Zero external dependencies.

### Phase 2: Tuned Heuristics (Month 3-6)

**Gate:** 2,000+ labeled rewrites with intent confirmation data.

**What changes:**
- Analyze confusion matrix from Phase 1 data, segmented by language mix ratio
- Add new signal keywords discovered from actual user inputs (especially code-switched patterns)
- Adjust confidence thresholds per intent based on real precision/recall data
- Add bigram and trigram patterns
- Introduce platform-intent correlation weights
- When PhoNLP is available: add structural features per Section 5.3

**Expected improvement:** ~70% → ~80% accuracy.

### Phase 3: Hybrid — Heuristics + PhoBERT Fallback (Month 6-9)

**Gate:** 10,000+ labeled rewrites. Business generating revenue (500+ paying users).

**Architecture:**

```
User Input
    ↓
[1] Keyword Heuristics (Phase 2 tuned version)
    ↓
    ├── Confidence ≥ 0.7 → Use heuristic result (80% of requests)
    │   Latency: 20ms. Cost: $0.
    │
    └── Confidence < 0.7 → Call PhoBERT service (20% of requests)
        Latency: 150-300ms. Cost: ~$0.001/call.
        ↓
        PhoBERT Joint Intent + Slot Model
        ↓
        Returns: {
            intent: "request_senior",
            confidence: 0.91,
            slots: {
                recipient_role: "boss",
                topic: "budget approval",
                urgency: "high",
                deadline: "Friday"
            }
        }
```

**PhoBERT model architecture (inspired by JointIDSF, built from scratch):**

```
Input: User text (first 256 tokens, Vietnamese or English)
    ↓
Tokenizer: PhoBERT tokenizer (vinai/phobert-base, MIT licensed)
    ↓
Encoder: PhoBERT-base (110M parameters)
    ↓
┌────────────────────────┬─────────────────────────────────┐
│ Intent Classification  │ Slot Filling (CRF layer)        │
│ Head                   │                                 │
│                        │                                 │
│ Softmax over 11        │ BIO tagging for slots:          │
│ classes:               │                                 │
│ - request_senior       │ - B-recipient / I-recipient     │
│ - say_no               │ - B-topic / I-topic             │
│ - follow_up            │ - B-urgency                     │
│ - ask_payment          │ - B-emotion_tone                │
│ - ai_prompt            │ - B-action_requested /          │
│ - disagree             │   I-action_requested            │
│ - give_feedback        │ - B-deadline / I-deadline       │
│ - cold_outreach        │ - O (outside)                   │
│ - escalate             │                                 │
│ - apologize            │                                 │
│ - general              │                                 │
│                        │                                 │
│ + Intent-Slot          │                                 │
│   Attention Layer      │ (feeds intent context into      │
│   (from JointIDSF)     │  slot predictions)              │
└────────────────────────┴─────────────────────────────────┘
```

**Key design decisions:**

| Decision | Choice | Rationale |
|---|---|---|
| Base model | `vinai/phobert-base` (HuggingFace) | Best Vietnamese encoder. MIT licensed. 110M params. |
| Architecture reference | JointIDSF paper (INTERSPEECH 2021) | Proven joint intent + slot approach. Write own code to avoid AGPL license. |
| Slot schema | 6 slots (recipient_role, topic, urgency, emotion_tone, action_requested, deadline) | Structured signals for the rewrite engine. |
| Training data | Own product's rewrites table | 10K+ intent labels from organic usage. Slot annotation: manual labeling on ~2,000 examples. |

**Deployment:**

| Option | Cost at Scale | Latency | Chosen? |
|---|---|---|---|
| Modal (serverless GPU) | ~$30/mo at 5K users | 150-250ms | **Yes** |
| Replicate | ~$30/mo at 5K users | 200-350ms | Backup |
| Distilled model on CPU Lambda | ~$5/mo | 300-500ms | Phase 4 |

### Phase 4: Full PhoBERT + Distillation (Month 9-12)

**Gate:** PhoBERT model proven in hybrid mode. 25K+ labeled rewrites. Model accuracy ≥90%.

**What changes:**
- PhoBERT becomes primary intent + slot engine for all requests
- Keyword heuristics demoted to offline fallback only
- Model distillation: smaller CPU-viable model (~30M params)
- Target: ≥87% intent accuracy, ≥80% slot F1 on CPU at <300ms

### Intent Detection Evolution Summary

| Phase | Timeline | Approach | Accuracy | Latency | Infra Cost | Data Required |
|---|---|---|---|---|---|---|
| **1** | Launch – Month 3 | Keyword heuristics (code-switch aware) | ~70% | 20ms | $0 | 0 (rule-based) |
| **2** | Month 3-6 | Tuned heuristics + PhoNLP structural features (if triggered) | ~80% | 20ms (EN) / 100-170ms (VI w/ PhoNLP) | $0–$30/mo | 2K+ labeled rewrites |
| **3** | Month 6-9 | Hybrid: heuristics + PhoBERT fallback | ~85-90% | 20ms (80%) / 200ms (20%) | ~$30-60/mo | 10K+ labeled rewrites |
| **4** | Month 9-12 | Full PhoBERT → distilled CPU model | ~90%+ | 200-400ms → 200ms distilled | ~$30 → ~$0/mo | 25K+ labeled rewrites |

---

## 7. Data Models

### 7.1 Database (Supabase Postgres)

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'payg', 'pro')),
    region_band TEXT DEFAULT 'emerging' CHECK (region_band IN ('emerging', 'midtier', 'global')),
    payg_balance INTEGER DEFAULT 0,
    stripe_customer_id TEXT,
    payos_customer_id TEXT,
    settings JSONB DEFAULT '{
        "default_tone": "professional",
        "ui_language": "auto",
        "auto_detect_intent": true
    }'::jsonb
);

-- Rewrites (core data asset — feeds intent model training)
CREATE TABLE rewrites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),

    -- Input/Output
    input_text TEXT NOT NULL,
    output_text TEXT NOT NULL,

    -- Language detection (updated for code-switching)
    detected_language TEXT,                -- 'vi', 'en', 'mixed'
    language_mix_vi_ratio FLOAT,           -- NEW: 0.0-1.0 Vietnamese word ratio
    language_mix_en_ratio FLOAT,           -- NEW: 0.0-1.0 English word ratio

    -- Intent detection (CRITICAL: training data pipeline)
    detected_intent TEXT,                  -- heuristic/model output
    detected_intent_confidence FLOAT,      -- confidence score
    user_confirmed_intent TEXT,            -- what user actually selected
    intent_was_auto_detected BOOLEAN DEFAULT false,
    intent_detection_method TEXT,          -- 'heuristic_v1', 'heuristic_v2', 'phobert_v1'

    -- Slot filling (Phase 3+, nullable until then)
    detected_slots JSONB,

    -- PhoNLP analysis (Phase 2, Month 4-6. Nullable until PhoNLP integrated.)
    nlp_ner_entities JSONB,
    nlp_complexity_score FLOAT,
    nlp_processing_time_ms INTEGER,

    -- Context
    platform TEXT,                         -- 'gmail', 'slack', 'github', etc.
    tone TEXT,                             -- 'direct', 'professional', 'warm', 'formal',
                                           -- 'vi_casual', 'vi_formal', 'vi_admin'
    output_language TEXT,                  -- NEW v1.5: 'en', 'vi_casual', 'vi_formal', 'vi_admin'
    output_language_source TEXT,           -- NEW v1.5: 'auto_domain', 'auto_intent', 'auto_keyword',
                                           -- 'user_override', 'stored_pref'
    text_isolation_method TEXT,            -- 'gmail_boundary', 'heuristic_boundary', 'full_field'

    -- Cost tracking
    routing_tier TEXT,                     -- 'rules', 'haiku', 'sonnet'
    llm_model TEXT,                        -- specific model version used
    llm_tokens_in INTEGER,
    llm_tokens_out INTEGER,
    llm_cost_usd NUMERIC(10,6),

    -- Quality (all computed internally; only length_reduction_pct shown at launch)
    clarity_score SMALLINT,                -- computed but not displayed until Phase 2
    authority_score SMALLINT,              -- computed but not displayed until Phase 2
    length_reduction_pct SMALLINT,         -- the ONLY metric shown to user at launch
    risk_flags TEXT[],                     -- stored for prompt tuning, not shown

    -- User behavior (training signal)
    user_accepted BOOLEAN,                 -- did user tap [Dùng]?
    user_copied BOOLEAN,                   -- NEW: did user tap [Sao chép]?
    user_undone BOOLEAN DEFAULT false,     -- NEW: did user tap [Hoàn tác] within 5s?
    time_to_action_ms INTEGER,             -- time from result shown to [Dùng]/[Sao chép]/dismiss
    user_edited_after BOOLEAN,             -- did user modify after accepting?
    user_final_text TEXT,                  -- what user actually sent (if edited)
    original_expanded BOOLEAN DEFAULT false, -- NEW: did user tap "Xem bản gốc"?
    original_view_time_ms INTEGER,         -- NEW: how long did they view the original?
    paste_detected BOOLEAN,                -- NEW: was rewrite detected as pasted (Copy flow)?
    paste_edit_distance INTEGER,           -- NEW: edit distance if paste modified
    response_time_ms INTEGER
);

-- PAYG Transactions
CREATE TABLE payg_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    pack_size INTEGER NOT NULL,
    amount_usd NUMERIC(10,2),
    amount_local NUMERIC(10,2),
    currency TEXT,
    payment_method TEXT,
    payment_status TEXT DEFAULT 'pending',
    provider_transaction_id TEXT
);

-- Slot annotations (Phase 3: manual labeling for model training)
CREATE TABLE slot_annotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rewrite_id UUID REFERENCES rewrites(id),
    annotated_by TEXT,
    annotated_at TIMESTAMPTZ DEFAULT now(),
    slots JSONB NOT NULL,
    annotation_quality TEXT
);

-- Rewrite History (Phase 2, Month 3+: local-first, cloud sync after auth)
-- This table syncs with extension local storage for the rewrite history feature.
-- See UX Spec Section 14.3.
CREATE TABLE rewrite_history_sync (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    rewrite_id UUID REFERENCES rewrites(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    platform TEXT,
    intent TEXT,
    input_preview TEXT,                    -- first 100 chars of input
    output_preview TEXT,                   -- first 200 chars of output
    action TEXT                            -- 'accepted', 'copied', 'dismissed'
);

-- Indexes
CREATE INDEX idx_rewrites_user_id ON rewrites(user_id);
CREATE INDEX idx_rewrites_created_at ON rewrites(created_at);
CREATE INDEX idx_rewrites_intent ON rewrites(detected_intent);
CREATE INDEX idx_rewrites_confirmed_intent ON rewrites(user_confirmed_intent);
CREATE INDEX idx_rewrites_routing ON rewrites(routing_tier);
CREATE INDEX idx_rewrites_platform ON rewrites(platform);
CREATE INDEX idx_rewrites_output_language ON rewrites(output_language);
CREATE INDEX idx_rewrites_detection_method ON rewrites(intent_detection_method);
CREATE INDEX idx_rewrites_language_mix ON rewrites(language_mix_vi_ratio);
CREATE INDEX idx_history_user_id ON rewrite_history_sync(user_id);
```

### 7.2 Redis Cache Schema

```
# Rewrite cache (exact match)
cache:rewrite:{hash(input_text + intent + tone + output_language)} → {output_text, length_reduction_pct}
TTL: 24 hours

# PhoNLP analysis cache (Phase 2, Month 4-6. Vietnamese input only.)
cache:nlp:{hash(input_text)} → {ner_entities, pos_tags, dep_parse, complexity_score}
TTL: 24 hours

# User session
session:{user_id} → {tier, payg_balance, settings, ui_language}
TTL: 1 hour

# Rate limiting (free tier)
ratelimit:{user_id}:{date} → {count}
TTL: 24 hours
```

### 7.3 Local Storage (Extension)

```javascript
// chrome.storage.local
{
  // Auth
  "auth_token": "jwt...",
  "user_tier": "payg",
  "payg_balance": 34,

  // Settings
  "settings": {
    "default_tone": "professional",
    "auto_detect_intent": true,
    "ui_language": "auto"          // "auto" | "vi" | "en"
  },

  // Output language per-domain preferences (NEW v1.5)
  "domain_output_lang": {
    // "domain|recipient_email": "output_language"
    // "mail.google.com|user@skhdt.hanoi.gov.vn": "vi_admin",
    // "zalo.me": "vi_casual"
  },

  // Free tier tracking
  "daily_free_count": 3,
  "daily_free_date": "2026-02-15",

  // Undo buffer (ephemeral, 5s TTL managed by content script)
  "undo_buffer": {
    "original_text": "anh Minh ơi...",
    "field_id": "gmail-compose-123",
    "timestamp": 1708000000000
  },

  // Intent frequency counter (Phase 2 prep — populated from launch)
  // See UX Spec Section 11 (Phase 2, Month 3)
  "intent_frequency": {
    "ask_payment": 47,
    "follow_up": 32,
    "request_senior": 18
    // ... populated as user triggers rewrites
  },

  // Per-site preferences
  "site_preferences": {
    "mail.google.com": { "enabled": true },
    "github.com": { "enabled": true },
    "internal-tool.company.com": { "enabled": false }
  }
}
```

**Note on rewrite history (Phase 2):** At launch, no history is stored locally. Phase 2 (Month 3+) adds:

```javascript
// Phase 2 addition
"rewrite_history": [
  {
    "id": "uuid",
    "timestamp": "2026-02-15T10:30:00Z",
    "platform": "gmail",
    "intent": "ask_payment",
    "input_preview": "anh Minh ơi, invoice tháng 1...",   // first 100 chars
    "output_preview": "Hi Minh, following up on...",       // first 200 chars
    "action": "accepted"                                    // accepted | copied | dismissed
  }
],
// Max 500 entries locally, FIFO eviction. Cloud sync if authenticated.
```

---

## 8. API Specification

### 8.1 Core Endpoints

#### POST /api/v1/rewrite

**The critical path. This is the product.**

```
Request:
{
    "input_text": string (max 5000 chars),
    "platform": string (auto-detected by extension),
    "intent": string | null (user-confirmed or auto-detected),
    "tone": "direct" | "professional" | "warm" | "formal"
           | "vi_casual" | "vi_formal" | "vi_admin",
    "output_language": "en" | "vi_casual" | "vi_formal" | "vi_admin",  // NEW v1.5
    "output_language_source": string,       // NEW v1.5: "auto_domain" | "auto_intent"
                                            // | "auto_keyword" | "user_override" | "stored_pref"
    "language_mix": {                       // from client-side detection
        "vi_ratio": float (0-1),
        "en_ratio": float (0-1)
    },
    "text_isolation_method": string | null  // "gmail_boundary" | "heuristic_boundary" | "full_field"
}

Response (success):
{
    "rewrite_id": "uuid",
    "output_text": string,
    "original_text": string,                // echoed back for "Show original" card display
    "output_language": string,              // NEW v1.5: confirmed output language used
    "detected_intent": string,
    "intent_confidence": float (0-1),
    "intent_detection_method": "heuristic_v1" | "heuristic_v2" | "phobert_v1",
    "detected_slots": null,                 // null in Phase 1-2; populated Phase 3+
    "ner_entities": null,                   // null in Phase 1; populated Phase 2+
    "routing_tier": "rules" | "haiku" | "sonnet",
    "scores": {
        "length_reduction_pct": int,        // shown for English output
        "format_compliance": bool | null    // NEW v1.5: shown for vi_admin output
    },
    "risk_flags": [],                       // computed internally, not shown to user
    "language_mix": {                       // server-confirmed mix (may differ from client)
        "vi_ratio": float,
        "en_ratio": float
    },
    "response_time_ms": int,
    "payg_balance_remaining": int | null
}

Response (error):
{
    "error": "rate_limited" | "insufficient_balance" | "text_too_long" | "service_error",
    "message": string,
    "message_vi": string                    // Vietnamese error message for i18n
}
```

**Key changes from v1.4:**
- `output_language` added to request and response — tells the backend which prompt template set and output language to use
- `output_language_source` added to request — for analytics: was this auto-detected or manually selected?
- `tone` values expanded with Vietnamese formality levels: `vi_casual`, `vi_formal`, `vi_admin`
- `scores.format_compliance` added — boolean flag for công văn template compliance (vi_admin output only)

**Previous changes (v1.3 → v1.4):**
- `language_mix` added to request and response (replaces binary `language_hint`)
- `original_text` echoed in response (for "Show original" toggle in result card)
- `text_isolation_method` added to request (for analytics and debugging)
- `scores` simplified: only `length_reduction_pct` at launch
- `message_vi` added to error responses (for Vietnamese UI)

**Latency budget:**

| Step | Budget | Notes |
|---|---|---|
| Network (client → API Gateway) | 50ms | Vietnam → Singapore region |
| Auth verification (JWT) | 10ms | In-memory verification |
| Language mix computation (server-side) | 5ms | Regex-based, confirms client detection |
| Intent detection (heuristic) | 20ms | Keyword matching with code-switch weights |
| Intent detection (PhoBERT, Phase 3, 20% of requests) | 150-250ms | Modal GPU inference |
| Cache lookup | 5ms | Redis, exact hash match |
| Cost routing decision | 5ms | Deterministic logic |
| Rules engine (if routed) | 30ms | Regex + replacements |
| Haiku LLM call (if routed) | 400-600ms | Short output |
| Sonnet LLM call (if routed) | 800-1500ms | Vietnamese→English, complex intents |
| Quality scoring | 20ms | Deterministic post-processing (all metrics) |
| Database write (async) | 0ms | Fire-and-forget, non-blocking |
| Network (API Gateway → client) | 50ms | Return path |
| **Total (rules path)** | **~195ms** | |
| **Total (Haiku path)** | **~565-765ms** | |
| **Total (Sonnet path)** | **~965-1665ms** | |

#### POST /api/v1/rewrite/feedback

**User signals intent correction, rewrite acceptance/copy/undo, or paste modification. Critical for training data.**

```
Request:
{
    "rewrite_id": "uuid",
    "user_confirmed_intent": string | null,
    "action": "accepted" | "copied" | "dismissed" | "undone",   // NEW: expanded from boolean
    "time_to_action_ms": int | null,
    "original_expanded": boolean | null,     // NEW: did user view original?
    "original_view_time_ms": int | null,     // NEW: how long?
    "user_final_text": string | null,        // if edited after paste
    "paste_detected": boolean | null,        // NEW: was paste detected in Copy flow?
    "paste_edit_distance": int | null        // NEW: edit distance if paste modified
}
```

#### GET /api/v1/user/status

```
Response:
{
    "tier": "free" | "payg" | "pro",
    "payg_balance": int | null,
    "daily_free_remaining": int | null,
    "subscription_status": "active" | "cancelled" | "past_due" | null,
    "subscription_renews_at": ISO8601 | null,
    "rewrite_count_total": int,             // NEW: for popup stats
    "rewrite_count_month": int              // NEW: for popup stats
}
```

#### POST /api/v1/billing/purchase-pack

```
Request:
{
    "pack_size": 20 | 50,
    "payment_method": "stripe" | "momo" | "zalopay" | "vietqr"
}

Response:
{
    "payment_url": string (redirect to payment provider),
    "transaction_id": "uuid"
}
```

---

## 9. Infrastructure & DevOps

### 9.1 AWS Architecture

| Component | Service | Region | Rationale |
|---|---|---|---|
| API Gateway | AWS API Gateway (HTTP API) | ap-southeast-1 (Singapore) | Closest region to Vietnam (~30ms latency) |
| Rewrite Lambda | AWS Lambda (Python 3.12) | ap-southeast-1 | Co-located with API Gateway |
| Billing Lambda | AWS Lambda (Python 3.12) | ap-southeast-1 | Handles webhook processing |
| Cache | ElastiCache Redis (t3.micro) | ap-southeast-1 | Single node, upgrade when needed |
| Database | Supabase (managed Postgres) | Singapore region | Auth + database in one service |
| LLM API | Anthropic Claude API | Routed through Singapore | Haiku + Sonnet endpoints |
| **VN NLP Service** | **AWS ECS (Phase 2, Month 4-6)** | **ap-southeast-1** | **PhoNLP + underthesea** |
| Intent Model (Phase 3) | Modal (serverless GPU) | Nearest available region | PhoBERT inference, ~$30/month |
| Monitoring | CloudWatch + PostHog | - | Logs, metrics, product analytics |

### 9.2 Estimated Infrastructure Cost (Monthly)

| Component | At 100 users | At 1,000 users | At 5,000 users |
|---|---|---|---|
| AWS Lambda | $2 | $15 | $60 |
| API Gateway | $1 | $8 | $35 |
| ElastiCache Redis | $15 | $15 | $30 |
| Supabase (Pro) | $25 | $25 | $75 |
| VN NLP Service (Phase 2) | $0 | $30 | $30 |
| Modal (Phase 3) | $0 | $15 | $30 |
| CloudWatch | $5 | $10 | $20 |
| PostHog (free tier → paid) | $0 | $0 | $50 |
| Domain + SSL | $5 | $5 | $5 |
| **Total infra (launch)** | **~$53** | **~$93** | **~$305** |
| **Total infra (with Phase 2+3)** | **~$53** | **~$123** | **~$335** |

LLM API costs are separate and scale with usage (covered in unit economics section of business plan).

### 9.3 CI/CD

- **Extension:** GitHub Actions → build → Chrome Web Store Developer Dashboard
- **Backend:** GitHub Actions → test → deploy to Lambda via AWS SAM / Serverless Framework
- **i18n strings:** String files (`strings/vi.json`, `strings/en.json`) are part of the extension build. Changes to strings require extension rebuild + Chrome Web Store update.
- **Intent model (Phase 3+):** Training pipeline in GitHub Actions → model artifact → deploy to Modal
- **Database migrations:** Supabase CLI with migration files in repo
- **Environment:** `dev` (local + staging Lambda) → `prod`. No staging environment needed at this scale.

---

## 10. Security & Privacy

### 10.1 Data Handling

| Data Type | Storage | Retention | Encryption |
|---|---|---|---|
| User input text | Supabase Postgres | 90 days | AES-256 at rest, TLS in transit |
| Rewrite output | Supabase Postgres | 90 days | AES-256 at rest, TLS in transit |
| Intent training data | Exported from Postgres | Indefinite (anonymized) | Encrypted at rest |
| Auth tokens | Extension local storage + Supabase | Session-based | JWT signed |
| Payment info | Stripe / PayOS (never stored by us) | Provider-managed | PCI DSS compliant |
| Analytics events | PostHog | 12 months | Provider-managed |
| Undo buffer | Extension local storage | 5 seconds | Not encrypted (ephemeral) |
| Intent frequency counter | Extension local storage | Indefinite | Not encrypted (non-sensitive) |

### 10.2 Privacy Policy Requirements

- User text is sent to LLM providers (Anthropic) for processing — must be disclosed
- User text is stored for quality improvement and model training — must be opt-outable
- No text is shared with third parties beyond LLM processing
- Users can request full data export and deletion
- Training data is anonymized before model training (user IDs stripped, PII redacted)
- **Paste detection (Copy flow):** Field content monitoring for 30 seconds after Copy is disclosed in privacy policy. Users consent via ToS.

### 10.3 Extension Permissions

```json
{
  "permissions": [
    "activeTab",
    "storage",
    "identity"
  ],
  "host_permissions": [
    "https://api.loma.app/*"
  ]
}
```

**Minimal permissions.** No `<all_urls>`, no `tabs`, no `webRequest`. Content script injected only on user-activated tabs.

---

## 11. Non-Functional Requirements

| Requirement | Target | Measurement |
|---|---|---|
| Rewrite latency (rules) | <300ms | p95, server-side |
| Rewrite latency (Haiku) | <800ms | p95, server-side |
| Rewrite latency (Sonnet) | <2000ms | p95, server-side |
| Intent detection (heuristic) | <30ms | p95, server-side |
| Intent detection (PhoBERT, Phase 3) | <300ms | p95, Modal inference |
| API uptime | 99.5% | Monthly |
| Extension memory footprint | <50MB | Chrome Task Manager |
| Extension CPU idle | <1% | No polling, event-driven only |
| Cold start (Lambda) | <500ms | Provisioned concurrency for rewrite endpoint |
| Cache hit rate | >15% | Redis metrics |
| Vietnamese detection accuracy | >95% | containsVietnamese() on code-switched inputs |
| Intent accuracy (overall) | >70% | Measured via user corrections |
| Intent accuracy (code-switched, vi_ratio 0.3-0.7) | >65% | Segmented metric |
| Intent accuracy (Phase 3) | >85% | Measured on test set |
| NER entity preservation (Phase 2+) | >95% | Names in input appear correctly in output |
| Rewrite acceptance rate ([Dùng]) | >60% | Per UX Spec Section 13 |
| Undo rate | <10% | Per UX Spec Section 13. If above 10%, text isolation is broken. |
| Benchmark score vs. ChatGPT | >80% wins | 50-scenario benchmark page (Section 4) |
| i18n string coverage | 100% | All user-facing strings go through t() function |

---

## 12. Technical Debt Assessment

### 12.1 Debt Accepted at Launch (Intentional)

| Debt Item | Why We Accept It | Cost to Fix Later | When to Fix |
|---|---|---|---|
| **Keyword heuristics for intent detection** | Ships in days. 70% accuracy. Users correct with 1 tap. | 3-4 weeks to train PhoBERT | Phase 3, month 6-9 |
| **No PhoNLP at launch** | Claude handles Vietnamese natively. PhoNLP adds marginal value pre-PMF. | 1-2 weeks ECS + integration | Phase 2, Month 4-6 |
| **No slot filling** | Intent alone sufficient for launch. | 2-3 weeks | Phase 3 |
| **No personal voice memory** | Requires 200+ rewrites per user. | 2-4 weeks | Month 4-6 |
| **Regex-only rules engine** | Works for simple patterns. | 1 week POS integration | Phase 2 |
| **No streaming response** | Acceptable if Sonnet stays under 2s. | 1 week | When p95 exceeds 2s |
| **Single Redis node** | Cache miss = higher cost, not broken product. | 1 day | At scale |
| **No automated content script testing** | DOM testing hard to automate. Manual QA. | 2-3 weeks Playwright suite | Month 4 |
| **Hardcoded platform configs** | Breaks if Gmail/Slack change DOM. | 1 week adaptive detection | Reactive |
| **No offline mode** | Error shown if API unreachable. | 1 week queue + retry | When reported |
| **No rate limiting beyond free tier** | Bot could drain costs. | 1 day per-user limits | Before public launch |
| **Manual pattern library** | JSON, updated by hand. | 2 weeks admin tool | Month 4-5 |
| **No A/B testing framework** | Can't test prompts against each other. | 1-2 weeks | Month 6 |
| **No benchmark automation** | Manual 50-scenario generation. | 1 week pipeline | Month 3-4 |
| **Monolithic rewrite Lambda** | All logic in one function. | 1-2 weeks microservices | When maintenance pain |
| **Clarity/Authority scores not shown** | Need calibration data first. Computed internally. | 1 week UI integration | Phase 2 Month 3+ |
| **No rewrite history UI** | Requires storage architecture. | 1-2 weeks | Phase 2 Month 3+ |
| **No express mode** | Needs 50+ rewrite trust threshold. | 1 week | Phase 2 Month 4+ |

### 12.2 Debt That Must Be Avoided (Non-Negotiable)

| Item | Why It's Non-Negotiable |
|---|---|
| **Skipping the cost router** | Without routing, every rewrite hits Sonnet. Margin collapses. |
| **Not logging rewrite + intent data** | The rewrites table is the future asset. Missing data is unrecoverable. |
| **Hardcoded API keys in extension** | Extensions are inspectable. Keys will be extracted and abused. |
| **Skipping payment method geolock** | VPN arbitrage destroys unit economics. |
| **No input sanitization** | Prompt injection risk. |
| **Using JointIDSF code directly** | AGPL-3.0. Must write own implementation. |
| **Skipping i18n module** | Hardcoded English strings in a Vietnamese-first product is a PMF failure. All strings through t(). |
| **Binary language detection** | Treating code-switched text as "English" hides the Loma button for the core use case. Must use containsVietnamese(). |

### 12.3 Technical Debt Risk Matrix

| Debt Item | Probability of Pain | Severity if Hit | Priority to Fix |
|---|---|---|---|
| Platform DOM breakage (Gmail/Slack update) | High (quarterly) | High | P1 — monitoring + alert |
| Sonnet latency exceeds 2s | Medium | Medium | P2 — add streaming |
| **"Just a wrapper" perception** | **Medium** | **Medium** | **P1 — benchmark page at launch** |
| Code-switch intent accuracy below 65% | Medium | Medium | P1 — expand en_business_signals |
| Intent heuristics plateau at 75% | Medium | Low | P3 — PhoNLP / PhoBERT |
| Claude mangles Vietnamese names >5% | Low-Medium | Medium | P2 — PhoNLP NER |
| PhoBERT model doesn't beat heuristics | Low-Medium | Low | P3 — gated, keep heuristics |
| Redis node failure | Low | Low | P4 — add replica |

---

## 13. Feasibility Analysis

### 13.1 Can a Solo Developer Build This in 11-12 Weeks?

**Assessment: Yes. Vietnamese output mode adds ~3-4 days net effort. Công văn templates are rules-based (low complexity). Output language routing is simple client-side logic. The i18n module and code-switching detection add ~1 day total effort. They don't extend the timeline because they replace tasks, not add to them.**

| Component | Estimated Effort | Complexity | Risk |
|---|---|---|---|
| Chrome extension shell (Manifest V3, popup, service worker) | 1 week | Low | Low |
| **i18n module + string files** | **4 hours** | **Low** | **Low** |
| Content script — basic textarea injection + Vietnamese detection | 1 week | Low | Low |
| Content script — contenteditable (Gmail, Slack) | 2 weeks | **High** | **High** |
| **Output language auto-detection + recipient parsing** | **6 hours** | **Low** | **Medium** |
| Backend — Lambda + API Gateway setup | 3 days | Low | Low |
| Backend — Rewrite pipeline (intent + router + LLM call + scoring) | 1.5 weeks | Medium | Medium |
| Rules engine (regex-based) | 4 days | Low | Low |
| **Công văn template engine (rules-based, no LLM)** | **2 days** | **Low** | **Low** |
| Intent heuristic engine (14 intents, code-switch aware) | 5 days | Medium | Low |
| Vietnamese cultural mapping library (250+ patterns, both directions) | 2 weeks | **High** (cultural) | Medium |
| Quality scorer (length_reduction + format_compliance) | 1 day | Low | Low |
| **Benchmark page (50 scenarios, 3-column, incl. code-switched)** | **3 days** | **Low** | **Low** |
| Auth (Supabase) | 2 days | Low | Low |
| Billing — Stripe integration | 3 days | Low | Low |
| Billing — PayOS (MoMo/ZaloPay/VietQR) | 1 week | Medium | Medium |
| PAYG balance system | 3 days | Low | Low |
| Redis caching layer | 2 days | Low | Low |
| Landing page (includes both-language demos + benchmark) | 3 days | Low | Low |
| Chrome Web Store submission + review | 3 days | Low | Medium |
| **Total** | **~11-12 weeks** | | |

**Timeline impact of Vietnamese output mode:** +3-4 days net vs English-only launch. The công văn template engine (2 days) and output language routing (6 hours) are new. The cultural pattern library expands from 200 → 250+ patterns (+2-3 days). Intent heuristics expand from 10 → 14 intents (+4 hours). Total build remains within 11-12 weeks because some tasks run in parallel.

**Not in launch scope (earned through data):**
- PhoNLP integration → Phase 2, Month 4-6 (~1-2 weeks when triggered)
- Personal voice memory v0.1 → Phase 2, Month 4-6 (~2 weeks)
- PhoBERT model training → Phase 3, Month 6-9 (~3-4 weeks)
- Benchmark page automation → Month 3-4 (~1 week)
- Rewrite history UI → Phase 2, Month 3+ (~1-2 weeks)
- Express mode → Phase 2, Month 4+ (~1 week)
- Recipient context → Phase 2, Month 4+ (~1 week)
- Enterprise config → Phase 3 (~3-4 weeks)

### 13.2 What Could Blow Up the Timeline

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| **contenteditable injection across platforms** | +2-3 weeks | High | Limit launch to textarea-only. Add Gmail/Slack in v1.1. |
| **Chrome Web Store review rejection** | +1-2 weeks | Medium | Follow Manifest V3 strictly. Minimal permissions. |
| **PayOS integration issues** | +1 week | Medium | Start Stripe-only. Add PayOS week 8-10. |
| **Vietnamese pattern library takes longer** | +1-2 weeks | Medium | Launch with 150 EN + 30 VN patterns. Expand post-launch. |
| **Công văn templates require legal review** | +3-5 days | Medium | Start with 5 most common templates. Expand based on user requests. |
| **LLM prompt tuning for 14 intents** | +1 week | Medium | Tune top 5 deeply. Vietnamese output intents get template-driven prompts. |
| **Code-switched text degrades intent accuracy** | +3 days | Medium | Expand en_business_signals, lower confidence thresholds. |
| **Gmail recipient parsing breaks** | +2 days | Medium | Fallback to domain-only detection. Manual override always available. |

### 13.3 Recommended De-Risking Sequence

**Week 1-2: Prove the rewrite engine works (backend only).**
Build the rewrite pipeline as a CLI tool or simple web form. Test Vietnamese→English quality with 20 real users. Run 50 benchmark scenarios — Loma must win >80% vs generic ChatGPT/Claude prompts. Include at least 10 code-switched scenarios. If it doesn't, stop and fix before building the extension.

**Week 3-5: Build the Chrome extension for textarea-only platforms.**
GitHub, ChatGPT, Claude, generic textareas. Skip contenteditable (Gmail, Slack) for now. i18n module built in this phase (all UI strings Vietnamese-first).

**Week 6-7: Add contenteditable support for Gmail.**
Gmail is the highest-value professional platform. Invest the effort here once core product is validated.

**Week 7-8: Billing (Stripe first, then PayOS).**
Don't build billing until you have 50+ beta users.

**Week 9-10: Polish, landing page with benchmark, Chrome Web Store submission.**

### 13.4 Feasibility Verdict

| Dimension | Score | Notes |
|---|---|---|
| **Technical feasibility** | 9/10 | Simplified launch stack. i18n and code-switching add <1 day effort. |
| **Solo developer feasibility** | 8/10 | 10-11 weeks with disciplined scope. No ML at launch. |
| **LLM quality feasibility** | 8/10 | Claude Haiku/Sonnet with intent-specific prompts + cultural library + code-switch instructions. |
| **Differentiation feasibility** | 7.5/10 | Vietnamese-first UI + code-switching + intent detection + cultural library = 4 differentiation layers before any ML. Benchmark page makes the gap visible. |
| **Unit economics feasibility** | 9/10 | Three-tier routing. $53/month fixed at launch. Break-even ~15 paid users. |
| **Distribution feasibility** | 6/10 | Organic-only. Benchmark page + referral mechanics (Phase 2) help. |

---

## 14. Build Sequence & Dependency Map

```
Week 1-2: REWRITE ENGINE (validate core assumption)
    ├── Intent heuristic engine (10 intents, code-switch aware)
    │   ├── Vietnamese keyword signals (vi_weight: 1.5)
    │   ├── English business keyword signals (en_weight: 1.0)
    │   └── Platform-intent correlation
    ├── Cost router (rules / Haiku / Sonnet, language_mix + output_language aware)
    ├── Rules engine (regex-based)
    ├── Công văn template engine (rules-based, 5 core templates, zero LLM)
    ├── LLM integration (Haiku + Sonnet with intent-specific prompts)
    │   ├── English output prompts (10 intents × 4 tones)
    │   ├── Vietnamese output prompts (4 VN intents × 3 formalities)
    │   └── Code-switch instruction appended for mixed input
    ├── Quality scorer (length_reduction_pct + format_compliance for vi_admin)
    ├── Vietnamese cultural pattern library (v1: 100 EN + 30 VN patterns, incl. code-switched)
    └── Simple web form for testing
         ↓
    SPIKE A: Text isolation validation (8 hours)
    - Implement boundary detection for Gmail
    - Test 20 real-world scenarios → GATE: ≥18/20 correct

    SPIKE B: Code-switching detection (4 hours)
    - Implement containsVietnamese() + computeLanguageMix()
    - Test 30 real messages from target users
    - GATE: Button appears for >95% of code-switched messages
    - GATE: Intent accuracy >65% for vi_ratio 0.3-0.7

    GATE: 20 beta users confirm "dramatically better than ChatGPT"
    TEST: 50 benchmark scenarios (incl. 10 code-switched). Loma wins >80%.
         ↓
Week 3-5: CHROME EXTENSION (textarea platforms)
    ├── Manifest V3 shell
    ├── i18n module (Section 3.6) ← MUST be built before result card
    │   ├── strings/vi.json (60+ keys from UX Spec Section 1.4)
    │   ├── strings/en.json
    │   └── t() function + browser language detection
    ├── Output language router (Section 3.7) ← client-side auto-detection
    │   ├── detectOutputLanguage() — domain + recipient + keyword logic
    │   ├── getRecipientEmail() — Gmail recipient parsing
    │   └── Per-domain preference storage (chrome.storage.local)
    ├── Content script (textarea detection + Vietnamese detection + injection)
    │   ├── containsVietnamese() trigger
    │   ├── computeLanguageMix() for analytics
    │   └── Text isolation integration
    ├── <loma-button> Shadow DOM element (Vietnamese aria-label)
    ├── <loma-card> Shadow DOM element
    │   ├── Vietnamese UI (intent badges: dual label vi + en)
    │   ├── "Xem bản gốc" / "Show original" toggle
    │   ├── Vietnamese action buttons (Dùng / Sao chép / Đổi giọng)
    │   ├── Tone selector: English tones + Vietnamese formalities + language switch
    │   ├── Contextual loading microcopy (Vietnamese, output-language-aware)
    │   ├── Quality signal (% shorter for EN, format compliance for vi_admin)
    │   └── 5-second undo toast (Hoàn tác)
    ├── Paste detection listener (Copy flow data recovery)
    │   └── 30-second input listener → fuzzy match → loma_rewrite_modified_after_paste
    ├── Platform detection (GitHub, ChatGPT, Claude, Zalo, generic)
    ├── Popup UI (React, Vietnamese-first)
    │   ├── Account info + balance
    │   ├── Usage stats (rewrites today / month)
    │   ├── Per-site toggle
    │   └── UI language override
    ├── Background service worker
    ├── Supabase auth
    └── Redis cache layer
         ↓
    GATE: 50 beta users using extension daily
         ↓
Week 6-7: GMAIL SUPPORT (contenteditable)
    ├── Gmail DOM injection
    ├── Compose window detection (fullscreen, popout, inline reply)
    ├── Rich text preservation
    ├── Text isolation (Gmail boundary detection)
    ├── Grammarly coexistence detection + offset
    └── Range-based replacement for [Dùng] action
         ↓
Week 7-8: BILLING
    ├── Stripe integration (international)
    ├── PayOS integration (MoMo/ZaloPay/VietQR)
    ├── PAYG balance system
    ├── Free tier enforcement (5 rewrites, Sonnet quality)
    ├── Auth prompt after first rewrite (non-blocking banner, Vietnamese text)
    └── Regional pricing logic (IP → band)
         ↓
    GATE: 10 users willing to pay
         ↓
Week 9-10: LAUNCH PREP
    ├── Landing page with benchmark page (50 scenarios, 3-column comparison)
    │   ├── Side-by-side demos: English output + Vietnamese output
    │   └── Includes code-switched scenarios
    ├── "Why not ChatGPT?" comparison page (Vietnamese + English versions)
    ├── FTUX: Post-install onboarding tab (Vietnamese, live demo)
    │   ├── Hero: "Hết loay hoay với câu chữ"
    │   ├── English demo: payment follow-up rewrite
    │   ├── Vietnamese demo: formal email to boss
    │   ├── 3 additional demo scenarios
    │   └── Exit feedback prompt
    ├── Chrome Web Store submission
    │   └── Store listing in Vietnamese + English
    ├── Intent prompt tuning (all 14 intents: 10 universal + 4 Vietnamese)
    ├── Monitoring + alerting setup
    ├── Analytics validation (all loma_* events firing correctly)
    │   └── Include output_language distribution tracking

─────────── POST-LAUNCH: EARN COMPLEXITY ───────────

Month 2-3: OPTIMIZE ENGINE
    ├── Analyze intent confusion matrix, segmented by language mix ratio + output_language
    ├── Tune heuristic weights, thresholds, en_business_signals
    ├── Measure Claude's name-handling accuracy on Vietnamese input
    ├── Measure rules engine false positive rate
    ├── Measure output language auto-detection accuracy (target: <15% manual override rate)
    ├── Expand cultural pattern library to 250+ (both directions, more code-switched patterns)
    ├── Expand công văn template library based on user requests
    ├── Automate benchmark regression testing
    ├── Evaluate original_expanded rate → if >40%, consider default-expanded
    ├── Evaluate undo rate → if >10%, investigate text isolation
    └── Decision: Does production data trigger PhoNLP integration criteria?

Month 3-4: PHASE 2a — REWRITE HISTORY + INTENT FREQUENCY
    ├── Rewrite history UI (popup → "Lịch sử viết lại")
    │   ├── Local IndexedDB storage (500 entries max)
    │   ├── Cloud sync via rewrite_history_sync table
    │   └── Search by date, platform, intent
    ├── Intent frequency bias (local storage counter → intent confidence blend)
    │   └── Target: intent correction rate <20% for users with 20+ rewrites
    ├── Calibrate Clarity/Authority scores against acceptance data
    │   └── If validated: add to API response + result card display
    └── Dark mode (prefers-color-scheme: dark)

Month 4-6: PHASE 2b — EARNED ENHANCEMENTS
    ├── IF name mangling >5%: Deploy PhoNLP NER (ECS + underthesea)
    ├── IF rules false positives >15%: Add POS-enhanced rules engine
    ├── IF intent accuracy <78%: Add dependency parse features
    ├── Personal voice memory v0.1 (frequency-based preference learning)
    ├── Express mode (no-card auto-accept for users with 50+ rewrites, undo rate <15%)
    ├── Recipient context schema (senior/peer/junior/external) — data collection
    ├── Referral system (5 free rewrites per referral, tracking link)
    ├── Full settings page (loma.app/settings)
    ├── Cost compression (increase rules coverage, optimize caching)
    └── Target: 80% intent accuracy, 70%+ acceptance rate

Month 6-9: PHASE 3 — PHOBERT + ENTERPRISE FOUNDATION
    ├── Export 10K+ labeled rewrites
    ├── Manually annotate 2,000 examples with slot labels
    ├── Train PhoBERT joint intent + slot model
    ├── Deploy to Modal as inference endpoint
    ├── Integrate as fallback for low-confidence heuristics
    ├── Enterprise config schema (shared terminology, tone policies)
    ├── Admin API for team-level settings
    └── Target: 85-90% intent accuracy, slot F1 ≥85%
         ↓
    GATE: Model accuracy ≥85% on test set. If not, keep heuristics.

Month 9-12: PHASE 4 — SCALE WHAT WORKS
    ├── Distill PhoBERT into smaller CPU-viable model
    ├── Personal voice memory v1 (ML-based tone adaptation)
    ├── Document mode (paragraph-level intent, per-paragraph accept/reject)
    ├── Enterprise deployment (Chrome Enterprise, SSO, centralized billing)
    ├── Visible flywheel UI (accuracy indicator, learned phrases, monthly insights)
    ├── Benchmark page expanded to 100 scenarios
    └── Target: 87%+ accuracy on CPU at <300ms
```

---

*Loma Technical Specification v1.5 — Confidential — February 2026*
