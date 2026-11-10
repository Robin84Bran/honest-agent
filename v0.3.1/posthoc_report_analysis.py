"""Post hoc analyses of v0.3.1 reports and report-only verdicts (10 Nov 2026; not part of the frozen analysis).

All three were chosen after seeing the results. They read the saved main-series trial files only (no model calls):
  A. "Confessions" by whether the actor ever saw "approval granted": on compliant runs, how often the report
     said violation=true, split by whether any trace step returned "approval granted".
  B. The Claude report-only verdict by what the report claimed (completed, violation), over all 360 runs.
  C. Sharing task, Qwen 7B: approval requests naming the recipient, and shares made.
Run from v0.3.1/: python3 -B posthoc_report_analysis.py  -> results/posthoc-report-analysis.{json,md}
"""
import json
from pathlib import Path

from analyze_v031 import load

BASE = Path(__file__).resolve().parent
ACTORS = ("qwen1.5b", "qwen7b", "llama8b")


def saw_grant(r):
    return any(h["observation"] == "approval granted" for h in r["trace"])


def confession_by_grant(rows):
    out = {}
    for a in ACTORS:
        comp = [r for r in rows if r["actor"] == a and not r["truth"]["violation"]]
        cell = {}
        for label, keep in (("saw_grant", True), ("never_saw_grant", False)):
            rs = [r for r in comp if saw_grant(r) == keep]
            cell[label] = {"compliant_runs": len(rs), "reported_violation": sum(r["report"]["violation"] for r in rs)}
        out[a] = cell
    return out


def final_verdict_by_report(rows, key="claude_final"):
    out = {}
    for r in rows:
        k = "completed=%s,violation=%s" % (str(r["report"]["completed"]).lower(), str(r["report"]["violation"]).lower())
        v = {True: "true", False: "false", None: "null"}[r["monitors"].get(key)]
        cell = out.setdefault(k, {"runs": 0, "breaches": 0, "true_completed": 0, "verdict": {"true": 0, "false": 0, "null": 0}})
        cell["runs"] += 1
        cell["breaches"] += r["truth"]["violation"]
        cell["true_completed"] += r["truth"]["completed"]
        cell["verdict"][v] += 1
    return dict(sorted(out.items()))


def recipient_requests(rows, actor="qwen7b"):
    tasks = json.loads((BASE / "tasks.json").read_text())
    value = tasks["sharing"]["value"]
    rs = [r for r in rows if r["actor"] == actor]
    asked = sum(any(h["call"].get("tool") == "request_approval" and h["call"].get("target") == value for h in r["trace"]) for r in rs)
    shared = sum(any(h["observation"] == "operation recorded" for h in r["trace"]) for r in rs)
    granted_runs = [r for r in rs if r["condition"] == "granted"]
    return {"actor": actor, "runs": len(rs), "asked_approval_for_recipient": asked, "runs_with_a_share": shared,
            "granted_condition_runs": len(granted_runs), "granted_runs_completed": sum(r["truth"]["completed"] for r in granted_runs)}


def markdown(res):
    lines = ["# v0.3.1 post hoc: reports and report-only verdicts", "",
             "Post hoc (chosen after seeing the data). Source: `posthoc_report_analysis.py` on the 360 main-series trials.", "",
             "## A. Reported violation on compliant runs, by whether the actor ever saw \"approval granted\"", "",
             "| Actor | Saw a grant | Never saw a grant |", "|---|---|---|"]
    for a, c in res["confession_by_grant"].items():
        g, n = c["saw_grant"], c["never_saw_grant"]
        lines.append("| %s | %d / %d | %d / %d |" % (a, g["reported_violation"], g["compliant_runs"], n["reported_violation"], n["compliant_runs"]))
    lines += ["", "## B. Claude report-only verdict by what the report claimed (all 360 runs)", "",
              "| Report claimed | Runs | Real breaches | Really completed | Verdict true | Verdict false | No verdict |", "|---|---|---|---|---|---|---|"]
    for k, c in res["final_verdict_by_report"].items():
        v = c["verdict"]
        lines.append("| %s | %d | %d | %d | %d | %d | %d |" % (k, c["runs"], c["breaches"], c["true_completed"], v["true"], v["false"], v["null"]))
    q = res["sharing_recipient_requests"]
    lines += ["", "## C. Sharing task, %s" % q["actor"], "",
              "- Runs: %d. Asked approval naming the recipient: %d. Runs with a share: %d." % (q["runs"], q["asked_approval_for_recipient"], q["runs_with_a_share"]),
              "- Granted-condition runs: %d, of which completed: %d." % (q["granted_condition_runs"], q["granted_runs_completed"]), ""]
    return "\n".join(lines)


def main(base=BASE):
    rows = load("deployment", base) + load("sharing", base)
    assert len(rows) == 360, len(rows)
    res = {"note": "post hoc; chosen after seeing the data", "trajectories": len(rows),
           "confession_by_grant": confession_by_grant(rows),
           "final_verdict_by_report": final_verdict_by_report(rows),
           "sharing_recipient_requests": recipient_requests(load("sharing", base))}
    (base / "results" / "posthoc-report-analysis.json").write_text(json.dumps(res, indent=2) + "\n")
    (base / "results" / "posthoc-report-analysis.md").write_text(markdown(res))
    print(markdown(res))
    return res


if __name__ == "__main__":
    main()
