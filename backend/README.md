# Loma Rewrite Backend

Phase 1 rewrite engine: language detection → intent heuristics → cost router → rules or Claude LLM → quality scorer.

## Layout

- **`loma/`** — Pipeline: `language`, `intent`, `router`, `rules_engine`, `quality`, `prompt_assembly`, `llm`, `pipeline`
- **`prompts/`** — JSON: `system_persona.json`, `intents/*.json`, `modifiers/*.json` (from Loma Prompt Playbook v1)
- **`handler.py`** — Lambda entry for `POST /api/v1/rewrite`
- **`run_local.py`** — Local test script (CLI)
- **`server.py`** — Local HTTP server for the extension (`POST /api/v1/rewrite`)

## Run locally (CLI)

```bash
cd backend
pip install -r requirements.txt
# optional: set ANTHROPIC_API_KEY or use backend/.env

python run_local.py "Anh ơi, em muốn nhờ anh xem giúp em cái báo cáo Q4 được không ạ?" gmail
python run_local.py "Kính gửi Sở, căn cứ nghị định đề nghị cấp giấy phép" generic professional vi_admin
```

Optional args: `[platform] [tone] [output_language]`. Output language can be `en`, `vi_casual`, `vi_formal`, `vi_admin`.

## Run API server (for extension)

Start the server so the Chrome extension can call the rewrite API (default `http://localhost:3000`):

```bash
cd backend
pip install -r requirements.txt
python server.py
```

Then load the extension (Chrome → Extensions → Load unpacked → `extension/`). Open any page with a text field (e.g. `extension/test_page.html` in the repo, or Gmail, GitHub), type Vietnamese (10+ chars); the Loma button appears. Click it to rewrite. Ensure `ANTHROPIC_API_KEY` is in `backend/.env` for real LLM responses.

## Spikes (Checkpoint A)

**Code-switch spike** — Intent accuracy on code-switched benchmark scenarios (gate: >65%):

```bash
python3 run_codeswitch_spike.py
```

**Text isolation spike** — User-text extraction from 20 scenarios (gate: ≥18/20):

```bash
python3 run_isolation_spike.py
```

Scenarios: `docs/Loma_TextIsolation_Spike_Scenarios.json`. Logic: `loma/text_isolation.py`.

## Run benchmark (50 scenarios)

Gate: Loma must win ≥40/50 vs generic ChatGPT (see `docs/Loma_Benchmark_v1.json`).

```bash
cd backend
pip install -r requirements.txt   # anthropic + python-dotenv (key loaded from backend/.env)
python3 run_benchmark.py                    # run all 50
python3 run_benchmark.py --limit 5          # first 5 only
python3 run_benchmark.py -o ../docs/Loma_Benchmark_v1_results.json  # write results
```

If `ANTHROPIC_API_KEY` is in `backend/.env`, it is loaded automatically. Use the same Python environment where `anthropic` is installed so the benchmark calls the real API (otherwise you get placeholder output).

Each scenario is updated with `loma_output`, `loma_detected_intent`, `loma_routing_tier`, `loma_response_time_ms`. Compare with `expected_output_qualities` and score per rubric (cultural_accuracy, structural_completeness, tone_calibration, entity_preservation, conciseness) to compute winner per scenario. **Gate:** Loma wins ≥40/50 before committing to extension build. Without `ANTHROPIC_API_KEY`, the pipeline returns placeholder or errors; set the key to run full benchmark.

## Deploy (Lambda)

Package `backend/` (handler.py, loma/, prompts/) and set Lambda handler to `handler.handler`. Environment: `ANTHROPIC_API_KEY`. Runtime: Python 3.12.

## API request/response

See `docs/Loma_TechSpec_v1.5.md` Section 8.1 — `POST /api/v1/rewrite`. Request: `input_text`, `platform`, `tone`, `language_mix?`, `intent?`, `output_language?` (en | vi_casual | vi_formal | vi_admin), `output_language_source?`. Response: `output_text`, `original_text`, `detected_intent`, `intent_confidence`, `routing_tier`, `scores.length_reduction_pct`, `output_language`, `output_language_source`, etc. Four Vietnamese-output intents: `write_to_gov`, `write_formal_vn`, `write_report_vn`, `write_proposal_vn`. Công văn (vi_admin) uses rules-based template, zero LLM.
