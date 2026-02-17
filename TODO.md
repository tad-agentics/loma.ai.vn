# Loma — Production Readiness TODO

Status as of 2026-02-17. Post-audit checklist for production launch.
Aligned with UX Spec v1.3, Tech Spec v1.5, OnePager.

---

## Completed Build Steps

All foundational build steps are done:

- Foundation: UX Spec v1.3 + Tech Spec v1.5
- LLM prompt playbook (15 intents, cultural_context, 4 tones each)
- Cultural pattern library v0.1 (110 patterns, few-shot injection)
- Extension UI: button, card, i18n, keyboard shortcut, Grammarly coexistence
- Backend: config, auth, billing, analytics, error handling
- Database schema + Supabase client + RLS
- Billing: PayOS, PAYG + Pro tiers, webhooks
- Unit tests: 148 passing (language, intent, quality, router, pipeline, auth, billing)
- CI/CD: GitHub Actions (test + deploy workflows)
- Infrastructure as Code: AWS SAM template
- Legal: Privacy Policy + Terms of Service
- Chrome Web Store: icons, manifest v1.0, CSP, commands
- Landing page: Vietnamese-first, pricing, demos
- Platform support: Gmail, Outlook, Teams, Google Docs, Slack, Jira, Notion, GitHub, LinkedIn, ChatGPT, Claude
- Vietnamese output intents: write_to_gov, write_formal_vn, write_report_vn, write_proposal_vn

---

## P0 — Blocks Launch

### Backend: Input Validation & Security

- [ ] **Handler input validation**: Validate `intent_override` against known INTENT_PATTERNS keys; validate `platform` against known platform list; validate `tone` against allowed enum (`professional`, `direct`, `warm`, `formal`). Return 400 for invalid values instead of passing unchecked to LLM.
- [ ] **PayOS webhook signature enforcement**: Currently logs mismatch but returns 200. Must return 401 on signature mismatch to prevent forged webhook calls crediting accounts.
- [ ] **PAYG balance atomicity**: Credit deduction in `payment.py` must use a Supabase transaction (or Postgres function) to prevent race conditions where concurrent requests overspend balance.
- [ ] **Security headers**: Add `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security` to all API responses.

### Backend: Test Coverage (~100+ tests needed)

Current coverage: `test_intent.py`, `test_router.py`, `test_pipeline.py`, `test_quality.py`, `test_language.py`, `test_auth.py`, `test_billing.py` (148 tests). Missing:

- [ ] **test_handler.py**: Request parsing, input validation, error responses, CORS, 429 rate limit responses, auth token extraction, all endpoint paths.
- [ ] **test_llm.py**: Retry logic, timeout handling, API error responses, token counting, model selection, prompt truncation.
- [ ] **test_rules_engine.py**: All rule categories, edge cases, vi_admin formatting, entity preservation in rules output.
- [ ] **test_payment.py**: PayOS webhook processing, signature validation, PAYG balance operations, tier transitions, concurrent deduction safety.
- [ ] **test_db.py**: Supabase client operations, connection handling, RLS behavior, error recovery.
- [ ] **test_prompt_assembly.py**: System prompt construction for all 15 intents × 4 tones, cultural example injection, platform override merging, code-switch modifier, output language injection.
- [ ] **test_analytics.py**: Event tracking, event schema validation, batch operations.

### Extension: Auth & Store Readiness

- [ ] **Supabase config in background.js**: Pre-populate `SUPABASE_URL` and `SUPABASE_ANON_KEY` in the `onInstalled` handler so auth works immediately after install without manual config.
- [ ] **Chrome Web Store screenshots**: Create 1280×800 screenshots showing Loma in action on Gmail, Slack, and Outlook. Required for store submission.
- [ ] **Chrome Web Store description**: Write Vietnamese + English store listing (short description, detailed description, category).

### Legal & Compliance

- [ ] **Host privacy/terms at loma.app**: Privacy Policy and Terms of Service must be accessible at live URLs (e.g., `loma.app/privacy`, `loma.app/terms`). Required by Chrome Web Store policy.

---

## P1 — Should Fix Before Launch

### Backend: Reliability

- [ ] **LLM retry tuning**: Increase `MAX_RETRIES` from 1 to 3 in `llm.py`. Increase `REQUEST_TIMEOUT_S` from 15s to 20s. Anthropic API can have transient failures; 1 retry is insufficient.
- [ ] **Anonymous rate limiting**: Enforce per-IP rate limits for unauthenticated users. Currently only tier-based limits exist; anonymous users have no throttle.
- [ ] **Unicode normalization in quality.py**: Entity comparison (`entity_preserved_pct`) should normalize Unicode (NFC) before comparing Vietnamese names to handle diacritic variations.
- [ ] **Logging for missing prompt files**: Add `logger.warning()` in `prompt_assembly.py` when an intent has no matching JSON file, instead of silently falling back to `general.json`.
- [ ] **Pin dependency versions**: `requirements.txt` should use exact versions (`anthropic==0.x.y`) instead of ranges to prevent unexpected breaks in production.

### Infrastructure

- [ ] **CloudWatch monitoring & alerts**: Add CloudWatch alarms in SAM template for: Lambda errors > 5/min, API Gateway 5xx > 1%, Lambda duration p99 > 10s, DLQ messages > 0.
- [ ] **Missing SAM env vars**: Add `FREE_REWRITES_PER_DAY`, `LOG_LEVEL`, `PAYOS_CLIENT_ID`, `PAYOS_API_KEY`, `PAYOS_CHECKSUM_KEY` to SAM template environment variables.
- [ ] **Lambda reserved concurrency**: Set reserved concurrency limit (e.g., 50) to prevent runaway scaling and unexpected Anthropic API costs.

### Benchmark

- [ ] **Run full benchmark**: `cd backend && python run_benchmark.py` with `ANTHROPIC_API_KEY`. Gate: Loma wins ≥40/50 scenarios. Current cultural pattern improvements should boost score.
- [ ] **Re-benchmark after P0 fixes**: Run again after handler validation and prompt assembly test fixes to confirm no regressions.

---

## P2 — Recommended Before Scale

- [ ] **Redis caching layer**: Cache intent detection results and frequently-used prompt assemblies to reduce Lambda cold-start latency and LLM calls for repeated inputs.
- [ ] **Benchmark comparison page**: Add a `/benchmark` page to the landing site showing Loma vs. ChatGPT/generic AI scores with real examples.
- [ ] **X-Ray tracing**: Enable AWS X-Ray in SAM template for end-to-end request tracing and latency debugging.
- [ ] **Separate dev/prod dependencies**: Split `requirements.txt` into `requirements.txt` (production) and `requirements-dev.txt` (pytest, linting, benchmark tools).
- [ ] **Error tracking integration**: Add Sentry or similar error tracking for both backend (Lambda) and extension (content script errors).
- [ ] **Extension E2E tests**: Puppeteer/Playwright tests for the extension on Gmail, Outlook, and Slack to catch DOM selector breakage.

---

## Launch Sequence

Once P0 items are complete:

1. Run benchmark (gate ≥40/50)
2. Set up Supabase project: create project, run `schema.sql`, set env vars
3. Deploy backend: `cd infrastructure && sam build && sam deploy --guided`
4. Verify API endpoints and webhook signatures
5. Package extension, upload to Chrome Web Store with screenshots
6. Point DNS, verify landing page and legal pages
7. Monitor CloudWatch for first 48 hours

---

*Source: Production audit (2026-02-17). Covers extension, backend, infrastructure, and compliance.*
