# Loma

**Hết loay hoay với câu chữ.**
Bạn lo phần ý. Loma lo phần lời.

*No more struggling with words. You bring the meaning. Loma finds the words.*

---

## What Loma Does

Loma is a Chrome extension that rewrites what you wrote — in English or Vietnamese — so it sounds like someone who's done this a thousand times.

You type rough. Loma makes it right. One tap, any text field, under 2 seconds.

```
[English output]

You type:  "anh Minh ơi, cái invoice tháng 1 chưa thanh toán, 
            5000 USD quá hạn 2 tuần rồi"

Loma:      "Hi Minh, following up on January's invoice for 
            $5,000 — now 2 weeks overdue. Could you confirm 
            the expected payment date by Friday?"
```

```
[Vietnamese output]

You type:  "cần xin giấy phép kinh doanh cho công ty mới, 
            gửi sở kế hoạch đầu tư"

Loma:      "Kính gửi Sở Kế hoạch và Đầu tư [Tỉnh/TP],
            Căn cứ Luật Doanh nghiệp 2020, Công ty [tên] 
            kính đề nghị Quý Sở xem xét cấp Giấy chứng nhận 
            đăng ký kinh doanh..."
```

Not a grammar checker. Not a translator. Loma understands what you're trying to do — then writes it the way the recipient needs to hear it.

---

## Why This Exists

Vietnamese professionals know what they want to say. Getting it on the page correctly is the problem.

In English: you think in Vietnamese, translate in your head, type it out, re-read it, revise it, re-read it again, still not sure. Send. Worry.

In Vietnamese: you need to email your boss but the tone is off. You need a công văn but you're Googling templates. You need a board report but it reads like meeting notes.

The pain is the same in both languages: **the gap between what you mean and what you write.**

Grammarly fixes commas — for native English speakers. ChatGPT requires copy-paste and a good prompt. Neither understands that a Vietnamese triple apology ("Em xin lỗi anh, em rất tiếc, em sorry...") should become one clean sentence, not a faithful translation of three apologies.

**Loma does.** That's the product.

---

## What Makes Loma Different

### 1. It knows what you're doing before you explain it

10 intent workflows detect whether you're following up on payment, declining a request, escalating to management, or writing an AI prompt — and produce structurally different output for each. ChatGPT gives you generic "professional" output regardless of context. Loma gives you the right words for the right situation.

### 2. It transforms culture, not just language

A hand-built library of 200+ Vietnamese communication patterns. Vietnamese indirectness becomes Western directness. Over-apologizing becomes one clean acknowledgment. Casual Slack-speak becomes proper công văn format. These are cultural judgments no LLM makes on its own.

### 3. Two languages, one workflow

English email to a client? Vietnamese công văn to a government agency? Report to sếp? Loma auto-detects the context and produces the right output in the right language. You don't pick a mode. You just write.

### 4. It speaks your language

The entire extension interface is in Vietnamese — buttons, menus, loading messages, error states. The user who struggles with writing shouldn't have to parse an English UI to get help.

### 5. It handles how you actually write

Real input: "Anh ơi, cái KPI report Q4 đã review chưa? Cần submit cho board meeting next Tuesday." That's 40% English. Loma treats mixed Vietnamese-English as the default input, not an edge case.

### 6. It gets smarter the more you use it

Every intent correction, every edit, every accepted rewrite trains the system. By Month 6, Loma will have more labeled Vietnamese professional communication data than any public dataset. The product generates its own competitive moat.

---

## The 3-Second Test

User types Vietnamese, rough English, or a mix in any text field → taps one button → gets output that makes them think: **"I could never have written that."**

In English: the native-speaker email they couldn't produce. In Vietnamese: the perfectly formatted công văn they'd have spent 30 minutes Googling templates for.

If that moment doesn't happen on first use, nothing else matters.

---

## How It Works (UX)

**One button. One tap. Full transform.**

The Loma button appears in any text field when typing is detected. Tap it. A floating card shows the rewrite with the detected intent (e.g., "💰 Nhắc thanh toán" or "📋 Văn bản hành chính"). Tap "Dùng" to replace your text. Done.

Key UX decisions:

- **Auto-detect output language** — English recipient → English output. Vietnamese formal context → Vietnamese output. No toggle.
- **Intent badge** — shows what Loma understood (teaches communication patterns over time)
- **Before/after toggle** — compare original with the rewrite
- **Tone selector** — English: direct / professional / warm / formal. Vietnamese: thân mật / trang trọng / hành chính.
- **5-second undo** — replaced text can be reverted instantly
- **No grammar underlines, no error counts, no sidebar** — Loma is a transform, not a correction

---

## How It's Built (Tech)

**Chrome extension (Manifest V3) + serverless backend (AWS Lambda) + Claude API.**

```
User input → Language detection → Intent detection (20ms) → 
Output language routing → Cost router → Rules engine / Haiku / Sonnet → 
Quality scoring → Final output
```

Three-tier cost routing protects margins:

| Tier | Handles | Cost | Share |
|---|---|---|---|
| Rules engine | Simple fixes (hedging, over-apology, template matching) | $0.00 | ~30% |
| Claude Haiku | Standard rewrites | ~$0.002 | ~50% |
| Claude Sonnet | Complex transforms, high-stakes, Vietnamese formal | ~$0.015 | ~20% |

**Blended cost: ~$0.003/rewrite. Blended gross margin: ~78%.**

Infrastructure: $53/month at launch. Break-even at ~15 paying users.

**What evolves post-launch:**
- Month 3-6: Vietnamese NLP (PhoNLP) for entity recognition + smarter rules
- Month 6-9: Fine-tuned model for intent detection — only if 10K+ labeled rewrites justify it
- Month 9+: Personal voice memory, enterprise config, công văn template library expansion

---

## Business Model

**Usage-based entry, subscription cap for power users. Profitable from ~15 users.**

| Tier | Price | Who |
|---|---|---|
| Free | 5 rewrites/day | Try the magic moment |
| Pay-As-You-Go | 20 rewrites / 49K VND (~$2) | Low-commitment entry |
| Pro (Unlimited) | 149K VND/month (~$6 VN) / $9 global | Daily power users |

Natural upgrade path: hit free limit on a busy day → buy a PAYG pack → realize 3 packs/month → Pro is cheaper → self-selected upgrade.

Vietnam payments via MoMo, ZaloPay, VietQR (PayOS). International via Stripe.

---

## Market

**Beachhead:** Vietnamese developers writing AI prompts and English emails (20+ daily, measurable value, concentrated in online communities).

**Expansion:** Vietnamese professionals broadly — corporate, sales, founders, remote workers, government-interfacing roles (~5M+ writing English or formal Vietnamese daily).

**Phase 3:** Southeast Asia — same pain point, same architecture, same pricing band.

Adding Vietnamese output roughly doubles the addressable use cases per user. A professional who uses Loma 5x/day for English emails now uses it 10x/day because the công văn, the sếp email, and the board report also go through Loma.

---

## Key Risks

| Risk | Mitigation |
|---|---|
| Only marginally better than ChatGPT | 50-scenario public benchmark proves the gap. 15x faster workflow (1 tap vs. 8 steps). Cultural patterns ChatGPT can't replicate. |
| Vietnamese formal output quality | Công văn templates are rules-based (format compliance), not LLM-generated. Lower hallucination risk than open-ended generation. |
| Low conversion in Vietnam | PAYG micro-packs (49K VND / ~$2) + MoMo/ZaloPay. No credit card required. |
| LLM costs erode margin | Three-tier routing at 78% blended margin. Rules engine handles 30% at zero cost. |
| Positioning dilution (two languages) | English mode acquires users (viral, shareable). Vietnamese mode retains them (daily utility). Different jobs in the funnel. |
| Competitor copies the concept | Data flywheel compounds. By Month 6: 8K+ labeled examples. By Month 9: fine-tuned model. |

---

## 90-Day Plan

**Week 1-6:** Build the extension. English mode first, Vietnamese formal mode in parallel. Validate rewrite quality against 50 benchmarks. 50 beta users.

**Week 7-10:** Add billing. Chrome Web Store submission. Landing page with live before/after demos in both languages.

**Month 4-8:** Optimize with production data. Expand công văn template library. 100 paying users. $2K MRR.

**Month 9-12:** Fine-tuned model. Personal voice memory. $5K+ MRR.

---

*Hết loay hoay với câu chữ. Bạn lo phần ý. Loma lo phần lời.*
