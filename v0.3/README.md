# Honest Agent v0.3: how to run

Read `PROTOCOL.md` first. Everything in this folder is new; nothing outside it is changed or overwritten.

| File | Purpose |
|---|---|
| `PROTOCOL.md` | Approved design (not yet frozen) |
| `config.json` | Models, effort, prices, 200 USD cap, seeds, fallback rule |
| `tasks.json` | Three task families, including the new held-out `sharing` task |
| `sandbox_v03.py` | 0.2 simulator plus granted / pending / denied approval |
| `providers_api.py` | Anthropic, OpenAI and local Ollama adapters (standard library only) |
| `run_v03.py` | Runner with budget guard, no-overwrite rule and freeze check |
| `analyze_v03.py` | Frozen analysis: tables in `results/analysis-<series>.md` |
| `test_v03.py` | 12 offline tests with a fake model (no network, no cost) |

## Run everything (on the Mac)

```sh
bash v0.3/run_all.command
```

Uses your existing Claude and ChatGPT subscription sign-ins; no API keys needed. It runs tests, preflight, calibration, the health gate, projection, freeze, replication, held-out and analysis, and stops by itself at any failed gate. The log goes to `results/run_all-<time>.log`. Rerunning is safe.

The manual steps below are kept for reference (API-key transport).

## Steps (on the Mac, in Terminal)

```sh
cd v0.3
python3 test_v03.py                      # must end with OK

# 1. Edit config.json: fill prices_usd_per_million_tokens.gpt input/output
#    from OpenAI's pricing page. The runner refuses to start while they are null.

# 2. Keys for this Terminal session only (never written to any file):
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...

# 3. Calibration: 30 trajectories, roughly 3-10 USD.
python3 run_v03.py run --series calibration

# 4. Cost projection. Send this output to Claude before freezing.
python3 run_v03.py project

# 5. Freeze. Use 10 if project printed "fallback_triggered": true.
python3 run_v03.py freeze --replication-seeds 20

# 6. Main runs, once each. Held-out also needs `ollama serve` running for the Qwen arm.
python3 run_v03.py run --series replication
python3 run_v03.py run --series heldout

# 7. Analysis.
python3 analyze_v03.py
```

If a run is interrupted, rerun the same command: finished trials are skipped, never overwritten. If the cap would be exceeded, the runner stops with BUDGET_STOP and writes `results/STOP-<series>.json`.

If the first calibration call fails with a model-not-found error, correct the model ID in `config.json` and rerun; no results exist yet at that point.
