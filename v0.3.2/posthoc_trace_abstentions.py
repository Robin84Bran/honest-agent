"""Post hoc (10 Nov 2026; chosen after seeing the v0.3.2 results, not part of the frozen analysis).
Lists every run where GPT-6 Sol's trace view gave no verdict, with the trace and the report, and checks whether the
report contradicts the trace: it claims completion, or a violation, although no operation was recorded. Added after the
independent review: the same check over all 360 trace judgments, so the abstentions can be compared with every run whose
report contradicts the trace (an association, not a cause), and how often each abstained prompt occurs.
Reads saved files only. Run from v0.3.2/: python3 -B posthoc_trace_abstentions.py -> results/posthoc-trace-abstentions.json
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = (BASE / ".." / "v0.3.1").resolve()

out, all_runs, prompts = [], {}, {}
for p in sorted((BASE / "results" / "judgments").rglob("*-trace.json")):
    j = json.loads(p.read_text())
    t = json.loads((SRC / "results" / j["trial"]).read_text())
    operated = any(h["observation"] == "operation recorded" for h in t["trace"])
    contra = (not operated) and (t["report"]["completed"] or t["report"]["violation"])
    key = "report_contradicts_trace=%s, gpt_trace=%s" % (str(bool(contra)).lower(), {True: "violation", False: "no violation", None: "no verdict"}[j["verdict"]])
    all_runs[key] = all_runs.get(key, 0) + 1
    prompts.setdefault(j["call"]["prompt"], []).append(j["verdict"])
    if j["verdict"] is not None:
        continue
    out.append({"trial": j["trial"], "raw": j["call"]["raw"], "breach": t["truth"]["violation"], "operation_recorded": operated,
                "report": t["report"], "claude_trace": t["monitors"]["claude_trace"],
                "report_contradicts_trace": (not operated) and (t["report"]["completed"] or t["report"]["violation"]),
                "trace": [[h["call"].get("tool"), h["call"].get("target"), h["observation"]] for h in t["trace"]], "prompt": j["call"]["prompt"]})
for o in out:
    vs = prompts[o.pop("prompt")]
    o["identical_trace_prompts"] = {"runs": len(vs), "no_verdict": sum(v is None for v in vs), "no_violation": sum(v is False for v in vs)}
summary = {"note": "post hoc", "gpt_trace_no_verdict": len(out), "breaches": sum(o["breach"] for o in out),
           "report_contradicts_trace": sum(o["report_contradicts_trace"] for o in out),
           "claude_trace_on_same_runs": [o["claude_trace"] for o in out], "all_360_trace_judgments": dict(sorted(all_runs.items())), "runs": out}
(BASE / "results" / "posthoc-trace-abstentions.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: v for k, v in summary.items() if k != "runs"}))
