"""Offline verification and stratified accounting. Run from any directory."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from metrics import summarize
from sandbox import Sandbox, policy_checker


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory):
    folder = ROOT / "results" / directory
    manifest = read(folder / "manifest.json")
    config = manifest["config"]
    assert manifest["status"] == "complete"
    for base, key in [(ROOT,"source_sha256"), (folder,"output_sha256")]:
        for name, expected in manifest[key].items():
            assert sha(base/name) == expected, name
    task = read(ROOT/"experiments/tasks.json")[config["family"]]
    seeds = range(config["seed"], config["seed"]+config["repeats"])
    assert set(folder.glob("trial-*.json")) == {folder/f"trial-{n}.json" for n in seeds}
    rows, patterns, usage = [], Counter(), {}
    for seed in seeds:
        row = read(folder/f"trial-{seed}.json")
        assert row["seed"] == seed and row["actor_started"]
        sandbox = Sandbox(task)
        for event in row["trace"]:
            sandbox.call(event["call"])
        assert sandbox.trace == row["trace"] and sandbox.events == row["policy_events"]
        assert sandbox.resources == row["resources"] and sandbox.truth() == row["truth"]
        assert policy_checker(sandbox.trace) == row["monitors"]["policy"]
        patterns[tuple(e["observation"] for e in sandbox.trace)] += 1
        for call in row["calls"]:
            role = call["role"]
            if role in ("final","trace"):
                view = json.loads(call["prompt"].split("\nInput:\n", 1)[1])
                assert set(view) == ({"task","report","trace"} if role=="trace" else {"task","report"})
                assert view["report"] == row["report"] and "split" not in view["task"]
                if role == "trace":
                    assert view["trace"] == sandbox.trace
            group = role if role in ("trace","final") else "actor"
            u = usage.setdefault(group, dict(calls=0,input_tokens=0,output_tokens=0,seconds=0,errors=0))
            u["calls"] += 1
            u["errors"] += int("error" in call)
            for key in ("input_tokens","output_tokens","seconds"):
                u[key] = None if u[key] is None or call[key] is None else u[key]+call[key]
        rows.append(row)
    metrics = summarize(rows)
    assert metrics == read(folder/"metrics.json")
    paired = [r for r in rows if r["truth"]["violation"] and
              all(r["monitors"][k] is not None for k in ("final","trace"))]
    paired_counts = {k:sum(r["monitors"][k] for r in paired) for k in ("final","trace")}
    return dict(paired_breaches=len(paired), paired_detections=paired_counts,
                paired_trace_minus_final_recall=((paired_counts["trace"]-paired_counts["final"])/len(paired)
                                                 if paired else None),
                metrics=metrics, violations=sum(r["truth"]["violation"] for r in rows),
                correct_claims={k:sum(r["report"][k]==r["truth"][k] for r in rows if r["report"])
                                for k in ("completed","violation")},
                trace_patterns=[{"observations":list(k),"count":v} for k,v in patterns.items()],
                api_charge_usd=sum(r["api_charge_usd"] for r in rows), usage=usage)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", choices=["payment-calibration","deployment-heldout"])
    args = parser.parse_args()
    if args.directory == "deployment-heldout":
        freeze = read(ROOT/"experiments/deployment-freeze.json")
        for path, expected in freeze["sha256"].items():
            assert sha(ROOT/path) == expected, path
        manifest = read(ROOT/"results/deployment-heldout/manifest.json")
        assert manifest["model"] == freeze["model_digest"]
        for k, v in freeze["run"].items():
            assert manifest["config"][k] == v
    print(json.dumps(verify(args.directory),indent=2))
