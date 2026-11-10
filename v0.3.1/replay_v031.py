"""Pre-registered replay verification for protocol 0.3.1 (PROTOCOL.md section 8).

Re-sends every saved actor call (intent, actions, report) in the given series through the same Ollama adapter,
with its saved prompt and seed, and checks the response text is identical. The Claude monitor's verdicts are not
replayed. Needs the project Ollama server from config.json running, with the pinned digests.
Usage: python3 replay_v031.py [series ...]   (default: deployment sharing) -> results/replay-<series>.json
"""
import json
import sys
from pathlib import Path

from providers_api import build

BASE = Path(__file__).resolve().parent


def replay(series, base=BASE):
    cfg = json.loads((base / "config.json").read_text())
    providers = {}
    calls = same = trials = trials_same = 0
    diffs = []
    for f in sorted((base / "results" / series).glob("*/*/trial-*.json")):
        t = json.loads(f.read_text())
        if cfg["models"][t["actor"]]["provider"] != "ollama":
            continue
        if t["actor"] not in providers:
            providers[t["actor"]] = build(t["actor"], cfg["models"][t["actor"]])  # checks the pinned digest
        trials += 1
        ok = True
        for c in t["calls"]:
            if c["model"] != t["actor"] or "raw" not in c:
                continue
            calls += 1
            if providers[t["actor"]].generate(c["prompt"], c["seed"])["text"] == c["raw"]:
                same += 1
            else:
                ok = False
                diffs.append("%s %s" % (f.relative_to(base / "results" / series).as_posix(), c["role"]))
        trials_same += ok
    out = {"series": series, "actor_calls": calls, "identical": same, "trials": trials,
           "trials_fully_identical": trials_same, "differences": diffs}
    (base / "results" / ("replay-%s.json" % series)).write_text(json.dumps(out, indent=2) + "\n")
    return out


if __name__ == "__main__":
    for s in sys.argv[1:] or ["deployment", "sharing"]:
        print(json.dumps(replay(s), indent=2))
