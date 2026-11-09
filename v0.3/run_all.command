#!/bin/bash
# Honest Agent v0.3: full run, end to end. Start with:  bash run_all.command   (or double-click in Finder)
# Stops on its own at any failed gate. Safe to rerun: finished trials are skipped, never overwritten.
set -u
cd "$(dirname "$0")"
mkdir -p results
LOG="results/run_all-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1
caffeinate -i -w $$ &
echo "== Honest Agent v0.3 started $(date)"

echo "== 1/8 offline tests"
python3 test_v03.py || { echo "STOP: offline tests failed"; exit 1; }

echo "== 2/8 preflight: one tiny call per model (login + model ID)"
python3 run_v03.py preflight || { echo "STOP: preflight failed. Check model IDs in config.json and the subscription logins."; exit 1; }

echo "== 3/8 calibration (30 trajectories, payment family)"
python3 run_v03.py run --series calibration --workers 6

echo "== 4/8 health gate (provider/parse errors only, not outcomes)"
python3 run_v03.py health || { echo "STOP: too many provider/parse errors in calibration. Nothing frozen. Send this log to Claude."; exit 1; }

echo "== 5/8 cost projection and pre-registered fallback"
python3 run_v03.py project > results/projection.json && cat results/projection.json
SEEDS=$(python3 -c 'import json;print(json.load(open("results/projection.json"))["recommended_replication_seeds"])')

echo "== 6/8 freeze (replication seeds: $SEEDS)"
[ -f freeze.json ] || python3 run_v03.py freeze --replication-seeds "$SEEDS" || { echo "STOP: freeze failed"; exit 1; }

echo "== 7/8 main runs: replication, then held-out"
python3 run_v03.py run --series replication --workers 6
if ! curl -s http://127.0.0.1:11434/api/tags >/dev/null; then
  echo "starting local ollama for the Qwen reference arm"
  (OLLAMA_NO_CLOUD=1 OLLAMA_HOST=127.0.0.1:11434 ollama serve > results/ollama.log 2>&1 &)
  sleep 8
fi
ollama list | grep -q "qwen2.5:1.5b" || echo "WARNING: qwen2.5:1.5b not installed; Qwen held-out calls will be recorded as failed."
python3 run_v03.py run --series heldout --workers 6

echo "== 8/8 frozen analysis"
python3 analyze_v03.py
echo "== DONE $(date). Tell Claude: the run is finished."
