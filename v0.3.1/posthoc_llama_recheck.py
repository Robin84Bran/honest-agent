"""Post hoc, post-review check (10 Nov 2026; not part of the frozen analysis).

The pre-registered replay found 3 mismatched actor calls, all Llama 3.1 8B report calls. This script re-sends
each of those three calls 3 more times, with the saved prompt and seed through the same adapter, and saves every
raw response with its parsed claims. These are NEW responses generated after the review. They are not the
responses seen in the earlier informal re-check, which were not saved.
Needs the project Ollama server from config.json. Run from v0.3.1/: python3 -B posthoc_llama_recheck.py
-> results/posthoc-llama-recheck.json
"""
import json
from pathlib import Path

from providers_api import build, extract_json

BASE = Path(__file__).resolve().parent
CALLS = ["deployment/llama8b/granted/trial-33.json", "sharing/llama8b/denied/trial-31.json", "sharing/llama8b/pending/trial-37.json"]


def claims(text):
    try:
        j = extract_json(text)
        return {"completed": j.get("completed"), "violation": j.get("violation")}
    except ValueError:
        return None


cfg = json.loads((BASE / "config.json").read_text())
llama = build("llama8b", cfg["models"]["llama8b"])
out = []
for rel in CALLS:
    t = json.loads((BASE / "results" / rel).read_text())
    c = next(x for x in t["calls"] if x["role"] == "report")
    reps = [llama.generate(c["prompt"], c["seed"])["text"] for _ in range(3)]
    out.append({"trial": rel, "role": "report", "seed": c["seed"],
                "saved": {"raw": c["raw"], "claims": claims(c["raw"]), "scored_report": t["report"]},
                "rechecks": [{"raw": r, "claims": claims(r), "identical_to_saved": r == c["raw"]} for r in reps]})
(BASE / "results" / "posthoc-llama-recheck.json").write_text(json.dumps(out, indent=2) + "\n")
for o in out:
    print(o["trial"], "saved", o["saved"]["claims"], "| rechecks", [(r["claims"], r["identical_to_saved"]) for r in o["rechecks"]])
