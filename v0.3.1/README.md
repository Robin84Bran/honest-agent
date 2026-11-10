# Honest Agent v0.3.1 · Open-model ladder

A pre-registered replication of v0.3's monitor result with three local open models (Qwen 2.5 1.5B, Qwen 2.5 7B and Llama 3.1 8B) on fresh seeds, on v0.2's deployment task and v0.3's sharing task. The monitor is Claude, reading either the final report or the full trace, alongside the deterministic policy checker. Design and pass/fail rules: [`PROTOCOL.md`](PROTOCOL.md).

## Files

| File | What it is |
|---|---|
| `PROTOCOL.md` | Approved protocol, frozen with the code |
| `config.json`, `tasks.json` | Models with pinned digests, series, seeds and cap. Tasks are byte-identical to v0.3 |
| `sandbox_v031.py`, `providers_api.py` | Sandbox (v0.3, renamed) and model adapters (v0.4 fixes) |
| `run_v031.py` | Runner: preflight, series, per-actor health gate, projection, freeze |
| `analyze_v031.py` | Frozen analysis. `results/analysis-main.md` holds the pre-registered tests |
| `replay_v031.py` | Pre-registered replay check of every actor call |
| `test_v031.py` | Offline tests: no network, no cost |
| `freeze.json` | SHA-256 of every frozen file, written after calibration |

## Run

```sh
cp local.env.example local.env       # set HONEST_AGENT_CLAUDE_BIN if `claude` isn't on PATH
set -a; . ./local.env; set +a
OLLAMA_NO_CLOUD=1 OLLAMA_HOST=127.0.0.1:11435 OLLAMA_MODELS=<model store> ollama serve &
python3 -B test_v031.py
python3 -B run_v031.py preflight
python3 -B run_v031.py run --series calibration --workers 3
python3 -B run_v031.py health
python3 -B run_v031.py project
python3 -B run_v031.py freeze --deployment-seeds 20     # or 10 if the projection triggers the fallback
python3 -B run_v031.py run --series deployment --workers 3
python3 -B run_v031.py run --series sharing --workers 3
python3 -B analyze_v031.py
python3 -B replay_v031.py
```

The Ollama models must match the digests in `config.json`. Preflight and the adapter refuse to run otherwise.
