"""Post hoc replay check for the Qwen supplement (run 10 Nov 2026; not in analyze_v03.py).

Re-sends every saved Qwen call in results/heldout_qwen_supplement/ through the frozen v0.3 Ollama adapter, with its
saved prompt and seed, and checks the response text is identical. Like supplement_qwen.py, it changes only the
Ollama port in memory (11434 -> 11435). It needs a local Ollama 0.33.3 server on 127.0.0.1:11435 holding
qwen2.5:1.5b with digest 65ec0654... It is free and local; Claude and GPT monitor verdicts are not replayed.

Run from v0.3/:  python3 -B posthoc_replay_qwen.py   -> writes results/posthoc-qwen-replay.json
"""
import json
from pathlib import Path

import providers_api as pa

BASE = Path(__file__).resolve().parent
_orig = pa._post
pa._post = lambda url, h, b, t: _orig(url.replace("127.0.0.1:11434", "127.0.0.1:11435"), h, b, t)

tags = json.loads(__import__("urllib.request").request.urlopen("http://127.0.0.1:11435/api/tags", timeout=10).read())
digest = next(m["digest"] for m in tags["models"] if m["name"] == "qwen2.5:1.5b")
assert digest.startswith("65ec06548149"), digest

q = pa.build("qwen", json.loads((BASE / "config.json").read_text())["models"]["qwen"])
calls = same = trials = trials_same = 0
diffs = []
for f in sorted((BASE / "results/heldout_qwen_supplement/qwen").glob("*/trial-*.json")):
    t = json.loads(f.read_text())
    trials += 1
    ok = True
    for c in t["calls"]:
        if c["model"] != "qwen":
            continue
        calls += 1
        if q.generate(c["prompt"], c["seed"])["text"] == c["raw"]:
            same += 1
        else:
            ok = False
            diffs.append("%s/%s %s" % (f.parent.name, f.name, c["role"]))
    trials_same += ok
out = {"model_digest": digest, "qwen_calls": calls, "identical": same, "trials": trials,
       "trials_fully_identical": trials_same, "differences": diffs}
(BASE / "results" / "posthoc-qwen-replay.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
