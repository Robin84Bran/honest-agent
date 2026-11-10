"""Post hoc (10 Nov 2026; chosen after seeing the v0.2.2 results, not part of the frozen analysis).
1. The report-only verdict by what the report claimed (completion, compliance), on breaches and on compliant runs.
2. The trace view's false alarms: their receipts and claims, and how many compliant runs carried the same claim.
Reads saved files only. Run from v0.2.2/: python3 -B posthoc_report_pattern.py -> results/posthoc-report-pattern.json
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = (BASE / json.loads((BASE / "config.json").read_text())["source"]).resolve()
LABEL = {True: "violation", False: "no violation", None: "no verdict"}

table, false_alarms, compliant_claims = {}, [], {}
for p in sorted(SRC.glob("*.json")):
    run = json.loads(p.read_text())
    v = {view: json.loads((BASE / "results" / "judgments" / ("%s-%s.json" % (p.stem, view))).read_text())["verdict"] for view in ("final", "trace")}
    breach = run["truth"]["compliance"] is False
    claim = "completion=%s, compliance=%s" % (str(run["claims"]["completion"]).lower(), str(run["claims"]["compliance"]).lower())
    cell = table.setdefault("breach" if breach else "compliant", {}).setdefault(claim, {"runs": 0, **{x: 0 for x in LABEL.values()}})
    cell["runs"] += 1
    cell[LABEL[v["final"]]] += 1
    if not breach:
        compliant_claims[claim] = compliant_claims.get(claim, 0) + 1
        if v["trace"] is True:
            false_alarms.append({"run": p.stem, "actor": run["actor"], "claims": run["claims"],
                                 "receipts": [e["receipt"] for e in run["events"]], "committed": any(e["receipt"] == "committed" for e in run["events"])})
out = {"note": "post hoc", "report_only_by_claim": table, "trace_false_alarms": len(false_alarms),
       "compliant_runs_by_claim": compliant_claims, "false_alarm_runs": false_alarms}
(BASE / "results" / "posthoc-report-pattern.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "false_alarm_runs"}, indent=2))
