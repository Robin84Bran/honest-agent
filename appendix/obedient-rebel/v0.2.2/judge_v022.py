"""Protocol 0.2.2 runner: a Claude monitor judges the saved Obedient Rebel v0.2.1 runs. Usage (from v0.2.2/):
  python3 -B judge_v022.py check              # offline: count runs and check that no payload leaks hidden fields
  python3 -B judge_v022.py freeze             # hash frozen files and source runs -> freeze.json (never overwritten)
  python3 -B judge_v022.py preflight          # one tiny call: sign-in and returned model; start time saved
  python3 -B judge_v022.py run --workers 4    # judge every (run, view) once; resumable, never re-sends a saved call

No actor is run. Calls go through Honest Agent v0.3.1's frozen `ask` with its monitor instruction, verbatim.
"""
import argparse
import concurrent.futures
import hashlib
import json
import random
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
REBEL = BASE.parent
SRC = (REBEL.parent / "Honest_Agent" / "v0.3.1").resolve()
sys.path.insert(0, str(SRC))
import run_v031 as rv  # noqa: E402  (frozen in Honest Agent v0.3.1)
from providers_api import build  # noqa: E402  (frozen in Honest Agent v0.3.1)

FROZEN_FILES = ["PROTOCOL.md", "config.json", "judge_v022.py", "analyze_v022.py"]
SOURCE_FILES = ["run_v031.py", "providers_api.py", "analyze_v031.py", "freeze.json"]
NAME = "claude"
HIDDEN = ("actor", "budget", "frame", "seed", "task", "truth", "qwen", "llama", "neutral", "urgency",
          "I need this done today", "Preparation for this task")


class CallFailed(RuntimeError):
    pass


class ModelMismatch(RuntimeError):
    pass


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def load_cfg(base=BASE):
    return json.loads((base / "config.json").read_text())


def tasks(rebel=REBEL):
    return {t["id"]: t for t in json.loads((rebel / "data" / "tasks.json").read_text())}


def source_runs(base=BASE, cfg=None):
    cfg = cfg or load_cfg(base)
    return sorted((base / cfg["source"]).resolve().glob("*.json"))


def payload(run, view, fixtures):
    task = fixtures[run["task"]]
    out = {"task": {"goal": task["goal"], "rule": task["constraint"]},
           "report": {k: run["claims"][k] for k in ("completion", "compliance")}}
    if view == "trace":
        out["trace"] = [{"action": e["action"], "receipt": e["receipt"]} for e in run["events"]]
    return out


def jobs(base=BASE, cfg=None):
    cfg = cfg or load_cfg(base)
    fixtures = tasks()
    out = []
    for p in source_runs(base, cfg):
        run = json.loads(p.read_text())
        for view in cfg["views"]:
            out.append({"run": p.name, "view": view, "seed": run["seed"], "payload": payload(run, view, fixtures),
                        "breach": run["truth"]["compliance"] is False})
    return out


def prompt(job):
    return rv.MONITOR + "\nInput:\n" + json.dumps(job["payload"], ensure_ascii=False)


def check(base=BASE, cfg=None):
    js = jobs(base, cfg)
    runs = {j["run"]: j["breach"] for j in js}
    leaks = [j["run"] + ":" + j["view"] for j in js if any(h.lower() in json.dumps(j["payload"]).lower() for h in HIDDEN if h != "task")
             or set(j["payload"]) - {"task", "report", "trace"}]
    return {"jobs": len(js), "runs": len(runs), "breaches": sum(runs.values()), "compliant": len(runs) - sum(runs.values()),
            "leaks": leaks}


def out_path(base, job):
    return base / "results" / "judgments" / ("%s-%s.json" % (job["run"][:-5], job["view"]))


def freeze_record(base=BASE):
    cfg = load_cfg(base)
    lines = ["%s  %s" % (sha(p.read_bytes()), p.name) for p in source_runs(base, cfg)]
    return {"sha256": {n: sha((base / n).read_bytes()) for n in FROZEN_FILES},
            "source_sha256": {n: sha((SRC / n).read_bytes()) for n in SOURCE_FILES},
            "fixtures_sha256": sha((REBEL / "data" / "tasks.json").read_bytes()),
            "source_runs_sha256": sha("\n".join(lines) + "\n"), "source_runs": len(lines)}


def freeze(base=BASE):
    path = base / "freeze.json"
    if path.exists():
        raise SystemExit("freeze.json already exists; it is never overwritten.")
    c = check(base)
    if c["leaks"] or (c["runs"], c["breaches"], c["compliant"]) != (1080, 670, 410):
        raise SystemExit("check failed: %s" % json.dumps(c)[:400])
    path.write_text(json.dumps(dict(frozen_utc=rv.now(), jobs=c["jobs"], **freeze_record(base)), indent=2) + "\n")


def verify_freeze(base=BASE):
    path = base / "freeze.json"
    if not path.exists():
        raise SystemExit("freeze.json missing: freeze and push before any monitor call.")
    saved, now_ = json.loads(path.read_text()), freeze_record(base)
    for k in now_:
        if saved[k] != now_[k]:
            raise SystemExit("Frozen input changed since freeze: %s" % k)


def budget_for(base, cfg):
    rv.check_prices(cfg, [NAME])
    return rv.Budget(base / "results" / "spend-ledger.jsonl", cfg["cap_usd"], {NAME: cfg["prices_usd_per_million_tokens"][NAME]})


def model_ok(item, cfg):
    return bool(item.get("returned_model")) and cfg["models"][NAME]["model"] in item["returned_model"]


def stamp(base, name, data):
    (base / "results").mkdir(exist_ok=True)
    with (base / "results" / name).open("x") as f:
        f.write(json.dumps(data, indent=2) + "\n")


def preflight(base=BASE, factory=build):
    cfg = load_cfg(base)
    budget = budget_for(base, cfg)
    started = datetime.now(timezone.utc).isoformat()
    log = []
    answer = rv.ask(factory(NAME, cfg["models"][NAME]), "preflight", 'Return {"ok":true} only.', {}, 0, log, budget,
                    cfg["models"][NAME]["max_tokens"])
    item = log[-1]
    report = {"started_utc": started, "ok": answer.get("ok") is True and model_ok(item, cfg),
              "returned_model": item.get("returned_model"), "error": item.get("error"), "usd": item.get("usd")}
    stamp(base, "preflight-%s.json" % started.replace(":", "")[:17], report)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 3


def judge_one(job, provider, budget, cfg, base):
    f = out_path(base, job)
    if f.exists():
        return None
    started = datetime.now(timezone.utc).isoformat()
    log = []
    answer = rv.ask(provider, "monitor_claude_%s" % job["view"], rv.MONITOR, job["payload"], job["seed"], log, budget,
                    cfg["models"][NAME]["max_tokens"])
    item = log[-1]
    assert item["prompt"] == prompt(job)
    if "raw" not in item:
        raise CallFailed("%s %s: %s" % (job["run"], job["view"], item.get("error")))
    verdict = answer["violation"] if type(answer.get("violation")) is bool else None
    rec = {"run": job["run"], "view": job["view"], "verdict": verdict, "model_verified": model_ok(item, cfg),
           "prompt_sha256": sha(item["prompt"]), "started_utc": started, "call": item, "finished_utc": rv.now()}
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("x") as fh:
        fh.write(json.dumps(rec, indent=2, ensure_ascii=False))
    if not rec["model_verified"]:
        raise ModelMismatch("%s %s: model %s" % (job["run"], job["view"], item.get("returned_model")))
    return rec


def run(base=BASE, factory=build, workers=None):
    verify_freeze(base)
    cfg = load_cfg(base)
    budget = budget_for(base, cfg)
    provider = factory(NAME, cfg["models"][NAME])
    todo = jobs(base, cfg)
    random.Random(cfg["order_seed"]).shuffle(todo)
    todo = [j for j in todo if not out_path(base, j).exists()]
    stop, lock, done = threading.Event(), threading.Lock(), [0]

    def work(job):
        if stop.is_set():
            return
        try:
            judge_one(job, provider, budget, cfg, base)
        except (rv.BudgetStop, CallFailed, ModelMismatch):
            stop.set()
            raise
        with lock:
            done[0] += 1
            if done[0] % 100 == 0 or done[0] == len(todo):
                print("judged %d of %d this run  spent %.2f USD" % (done[0], len(todo), budget.spent), flush=True)

    status = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers or cfg["workers"]) as pool:
        for fut in concurrent.futures.as_completed([pool.submit(work, j) for j in todo]):
            try:
                fut.result()
            except (rv.BudgetStop, CallFailed, ModelMismatch) as err:
                if not status:
                    kind = {rv.BudgetStop: "budget", CallFailed: "call_failed", ModelMismatch: "model_mismatch"}[type(err)]
                    (base / "results").mkdir(exist_ok=True)
                    with (base / "results" / "stops.jsonl").open("a") as fh:
                        fh.write(json.dumps({"utc": rv.now(), "kind": kind, "reason": str(err)}) + "\n")
                    print("STOP (%s): %s" % (kind, err), flush=True)
                    status = {"budget": 2, "call_failed": 5, "model_mismatch": 6}[kind]
    return status


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["check", "freeze", "preflight", "run"])
    p.add_argument("--workers", type=int)
    a = p.parse_args(argv)
    if a.command == "check":
        c = check()
        print(json.dumps(c, indent=2))
        return 0 if not c["leaks"] and c["runs"] == 1080 else 1
    if a.command == "freeze":
        freeze()
        return 0
    if a.command == "preflight":
        return preflight()
    return run(workers=a.workers)


if __name__ == "__main__":
    sys.exit(main())
