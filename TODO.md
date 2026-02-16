# Loma — To-dos (from plan)

Status as of last implementation. Aligned with UX Spec v1.3, Tech Spec v1.5, OnePager.

---

## Build steps

| ID | Step | Status |
|----|------|--------|
| step-1 | Foundation: UX Spec v1.3 + Tech Spec v1.5 in repo | ✅ Done |
| step-2-prompts | LLM prompt playbook → backend `prompts/` | ✅ Done |
| step-2-patterns | Cultural pattern library v0.1 (110 patterns) | ✅ Done |
| step-2-benchmark | Benchmark suite 50 scenarios; run Loma vs ChatGPT, gate ≥40/50 | ⏳ Pending: run full benchmark with `ANTHROPIC_API_KEY` |
| step-3 | Extension UI: button loading, card skeleton, 420px, Escape, focus | ✅ Done |
| step-4 | Billing readiness: lock PAYG, free trial, regions, payment methods | ⏳ Pending |
| step-5 | Launch: landing copy, store listing, Privacy Policy, ToS | ⏳ Pending |

---

## Spec updates (v1.3 / v1.5)

| ID | Item | Status |
|----|------|--------|
| output-lang | Output language routing (client + API, per-domain storage) | ✅ Done |
| vn-intents | Backend: 4 VN intents + công văn template engine | ✅ Done |
| tone-selector-vn | Tone selector: VN formality + [English] [Tiếng Việt]; per-domain | ✅ Done |
| i18n-ftux-quality | i18n (14 intents, tone_*, loading_*_vn, quality VN); FTUX welcome | ✅ Done |
| checkpoint-c-grammarly | Grammarly coexistence: detect + offset 44px left | ✅ Done |

---

## Checkpoints (phase gates)

| Checkpoint | Phase | Pass when | Status |
|------------|--------|-----------|--------|
| **A** | Rewrite engine | Engine working; benchmark Loma wins >80%; text isolation ≥18/20; code-switch intent >65% | ⏳ Pending: run full 50 benchmark ≥40/50 |
| **B** | Extension textarea | i18n through t(), Vietnamese default; 50 beta users | ⏳ Pending: 50 beta users |
| **C** | Gmail | Contenteditable + text isolation; Grammarly verified | ✅ Implemented |
| **D** | Billing | 10 users willing to pay | ⏳ Pending |
| **E** | Launch | Store submission; loma_* events; landing live | ⏳ Pending |

---

## Next actions

1. **Run benchmark:** `cd backend && python run_benchmark.py` (set `ANTHROPIC_API_KEY` in `.env`). Gate: Loma wins ≥40/50.
2. **Billing:** Lock pricing (PAYG, Pro), free trial (5 rewrites), payment methods; then implement.
3. **Launch:** Landing page (Vi + En), store listing, Privacy Policy, ToS at loma.app.

---

*Source: plan (UX v1.3, Tech v1.5). Do not edit the plan file; update this TODO as work completes.*
