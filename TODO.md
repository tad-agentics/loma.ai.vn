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
- Unit tests: 283 passing (all modules covered)
- CI/CD: GitHub Actions (test + deploy workflows)
- Infrastructure as Code: AWS SAM template (with CloudWatch alarms, reserved concurrency)
- Legal: Privacy Policy + Terms of Service
- Chrome Web Store: icons, manifest v1.0, CSP, commands, store listing text
- Landing page: Vietnamese-first, pricing, demos
- Platform support: Gmail, Outlook, Teams, Google Docs, Slack, Jira, Notion, GitHub, LinkedIn, ChatGPT, Claude
- Vietnamese output intents: write_to_gov, write_formal_vn, write_report_vn, write_proposal_vn
- Handler input validation (intent, platform, tone enum)
- PayOS webhook signature enforcement (401 on mismatch)
- PAYG balance atomicity (Postgres RPC function)
- Security headers (X-Content-Type-Options, X-Frame-Options, HSTS)
- LLM retry tuning (3 retries, 20s timeout)
- Anonymous IP-based rate limiting
- Unicode normalization in entity comparison
- Logging for missing prompt files
- Pinned dependency versions
- Separate dev/prod dependencies

---

## P0 — Blocks Launch (requires your input)

### Extension: Auth & Store Readiness

- [ ] **Supabase config in background.js**: Pre-populate `SUPABASE_URL` and `SUPABASE_ANON_KEY` in the `onInstalled` handler. *Needs: your Supabase project credentials.*
- [ ] **Chrome Web Store screenshots**: Create 1280x800 screenshots showing Loma in action on Gmail, Slack, and Outlook. *Needs: running instance with real UI.*

### Legal & Compliance

- [ ] **Host privacy/terms at loma.app**: Privacy Policy and Terms of Service must be accessible at live URLs. *Needs: DNS + hosting setup.*

### Benchmark

- [ ] **Run full benchmark**: `cd backend && python run_benchmark.py` with `ANTHROPIC_API_KEY`. Gate: Loma wins >=40/50. *Needs: your API key.*

---

## P2 — Recommended Before Scale

- [ ] **Redis caching layer**: Cache intent detection results and frequently-used prompt assemblies.
- [ ] **Benchmark comparison page**: Add a `/benchmark` page to the landing site.
- [ ] **X-Ray tracing**: Enable AWS X-Ray in SAM template.
- [ ] **Error tracking integration**: Add Sentry or similar for backend + extension.
- [ ] **Extension E2E tests**: Puppeteer/Playwright tests for the extension on Gmail, Outlook, and Slack.

---

## Launch Sequence

Once remaining P0 items are complete:

1. Run benchmark (gate >=40/50)
2. Set up Supabase project: create project, run `schema.sql`, set env vars
3. Deploy backend: `cd infrastructure && sam build && sam deploy --guided`
4. Verify API endpoints and webhook signatures
5. Package extension, upload to Chrome Web Store with screenshots
6. Point DNS, verify landing page and legal pages
7. Monitor CloudWatch for first 48 hours

---

*Source: Production audit (2026-02-17). Updated after implementation sprint.*
