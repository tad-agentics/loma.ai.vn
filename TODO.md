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
| step-4a | Backend config, auth, billing, analytics, error handling | ✅ Done |
| step-4b | Database schema + Supabase client | ✅ Done |
| step-4c | Billing: PayOS, tier enforcement, webhooks | ✅ Done |
| step-4d | Extension: auth headers, keyboard shortcut, analytics, prod config | ✅ Done |
| step-5a | Unit tests (language, intent, quality, router, pipeline, auth, billing) | ✅ Done |
| step-5b | CI/CD: GitHub Actions (test + deploy workflows) | ✅ Done |
| step-5c | Infrastructure as Code: AWS SAM template | ✅ Done |
| step-6a | Legal: Privacy Policy + Terms of Service | ✅ Done |
| step-6b | Chrome Web Store: icons, manifest v1.0, CSP, commands | ✅ Done |
| step-6c | Landing page: Vietnamese-first, pricing, demos | ✅ Done |
| step-7 | Launch: run benchmark, deploy, store submission | ⏳ Pending |

---

## Spec updates (v1.3 / v1.5)

| ID | Item | Status |
|----|------|--------|
| output-lang | Output language routing (client + API, per-domain storage) | ✅ Done |
| vn-intents | Backend: 4 VN intents + công văn template engine | ✅ Done |
| tone-selector-vn | Tone selector: VN formality + [English] [Tiếng Việt]; per-domain | ✅ Done |
| i18n-ftux-quality | i18n (14 intents, tone_*, loading_*_vn, quality VN); FTUX welcome | ✅ Done |
| checkpoint-c-grammarly | Grammarly coexistence: detect + offset 44px left | ✅ Done |
| auth-system | Supabase Auth + JWT verification + Google sign-in | ✅ Done |
| billing-system | PayOS, PAYG + Pro tiers, server-side enforcement | ✅ Done |
| database | Supabase PostgreSQL: users, rewrites, events tables + RLS | ✅ Done |
| analytics | Server-side event tracking + extension analytics relay | ✅ Done |
| security | CORS restriction, CSP, API auth headers, error handling | ✅ Done |
| keyboard-shortcut | Ctrl+Shift+. / Cmd+Shift+. keyboard shortcut | ✅ Done |
| testing | Unit tests for all core modules | ✅ Done |
| ci-cd | GitHub Actions: test on PR, deploy on main | ✅ Done |
| iac | AWS SAM template for Lambda + API Gateway | ✅ Done |

---

## Checkpoints (phase gates)

| Checkpoint | Phase | Pass when | Status |
|------------|--------|-----------|--------|
| **A** | Rewrite engine | Engine working; benchmark Loma wins >80%; text isolation ≥18/20; code-switch intent >65% | ⏳ Pending: run full 50 benchmark ≥40/50 |
| **B** | Extension textarea | i18n through t(), Vietnamese default; 50 beta users | ⏳ Pending: 50 beta users |
| **C** | Gmail | Contenteditable + text isolation; Grammarly verified | ✅ Implemented |
| **D** | Billing | 10 users willing to pay | ✅ Infrastructure ready |
| **E** | Launch | Store submission; loma_* events; landing live | ⏳ Ready to submit |

---

## Next actions

1. **Run benchmark:** `cd backend && python run_benchmark.py` (set `ANTHROPIC_API_KEY` in `.env`). Gate: Loma wins ≥40/50.
2. **Set up Supabase project:** Create project, run `schema.sql`, set env vars.
3. **Deploy:** `cd infrastructure && sam build && sam deploy --guided`
4. **Submit to Chrome Web Store:** Package extension, upload with screenshots.
5. **Go live:** Point DNS, verify landing page.

---

*Source: plan (UX v1.3, Tech v1.5). Updated after production-readiness implementation.*
