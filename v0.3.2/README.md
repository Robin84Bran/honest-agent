# Honest Agent v0.3.2 · A second monitor family

GPT-6 Sol re-judges the 360 saved v0.3.1 trajectories, using the same 720 monitor prompts, byte for byte, in the final-report view and the full-trace view. No actor is run again. The question is whether the trace-vs-report gap that Claude showed in v0.3.1 also appears with a monitor from another family. Design and pass/fail rules: [`PROTOCOL.md`](PROTOCOL.md).

## Files

| File | What it is |
|---|---|
| `PROTOCOL.md` | Protocol, with predictions recorded before any GPT call |
| `config.json` | Model, effort, prices, cap, call order seed |
| `judge_v032.py` | Runner: prompt check, freeze, preflight, resumable run. It reuses v0.3.1's frozen adapter and `ask` |
| `analyze_v032.py` | Frozen analysis, using v0.3.1's frozen statistics |
| `test_v032.py` | Offline tests: no network, no cost |
| `freeze.json` | SHA-256 of the frozen files, the v0.3.1 code they import, and the 360 source trial files |
| `results/judgments/<series>/<actor>/<condition>/trial-<seed>-<view>.json` | One file per GPT call: prompt hash, raw reply, tokens, cost, model and effort from Codex's session log |

## Run

```sh
set -a; . ../v0.3.1/local.env; set +a     # HONEST_AGENT_CODEX_BIN, if `codex` isn't on PATH
python3 -B test_v032.py
python3 -B judge_v032.py check
python3 -B judge_v032.py freeze           # then commit and push before any GPT call
python3 -B judge_v032.py preflight
python3 -B judge_v032.py run --workers 4
python3 -B analyze_v032.py
```
