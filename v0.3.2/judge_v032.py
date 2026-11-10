"""Protocol 0.3.2 runner: GPT-6 Sol re-judges the saved v0.3.1 monitor prompts. Usage (from v0.3.2/):
  python3 -B judge_v032.py check              # offline: rebuild all 720 prompts and compare them with the saved ones
  python3 -B judge_v032.py freeze             # hash frozen files and source trials -> freeze.json (never overwritten)
  python3 -B judge_v032.py preflight          # one tiny call: sign-in, and the model and effort Codex actually ran
  python3 -B judge_v032.py run --workers 4    # judge every (trial, view) once; resumable, never re-sends a saved call

No actor is run. Each job is one saved v0.3.1 Claude monitor call: the same instruction and the same input, byte for
byte, sent to GPT-6 Sol through v0.3.1's frozen `ask` (retries, budget and JSON parsing unchanged).
"""
import argparse
import concurrent.futures
import hashlib
import json
import random
import sys
import threading
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = (BASE / ".." / "v0.3.1").resolve()
sys.path.insert(0, str(SRC))
import run_v031 as rv  # noqa: E402  (frozen in v0.3.1)
from providers_api import build  # noqa: E402  (frozen in v0.3.1)

FROZEN_FILES = ["PROTOCOL.md", "config.json", "judge_v032.py", "analyze_v032.py"]
SOURCE_FILES = ["run_v031.py", "providers_api.py", "analyze_v031.py", "sandbox_v031.py", "freeze.json"]
NAME = "gpt"


class CallFailed(RuntimeError):
    pass


class ModelMismatch(RuntimeError):
    pass


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def load_cfg(base=BASE):
    return json.loads((base / "config.json").read_text())


def source_trials(src=SRC, series=("deployment", "sharing")):
    return sorted(p for s in series for p in (src / "results" / s).glob("*/*/trial-*.json"))


def jobs(src=SRC, cfg=None):
    """One job per analysed v0.3.1 trial and view, holding the saved Claude monitor prompt split into its parts."""
    cfg = cfg or load_cfg()
    out = []
    for p in source_trials(src, cfg["source_series"]):
        t = json.loads(p.read_text())
        if not (t.get("actor_started") and t.get("truth") is not None and not t.get("invalid")):
            continue
        for view in cfg["views"]:
            call = next(c for c in t["calls"] if c["role"] == "monitor_claude_%s" % view)
            instruction, payload = call["prompt"].split("\nInput:\n", 1)
            out.append({"trial": p.relative_to(src / "results").as_posix(), "view": view, "seed": call["seed"],
                        "instruction": instruction, "payload": json.loads(payload), "saved_prompt": call["prompt"]})
    return out


def rebuilt(job):
    return rv.MONITOR + "\nInput:\n" + json.dumps(job["payload"], ensure_ascii=False)


def check(src=SRC, cfg=None):
    """Offline integrity check: every saved prompt is v0.3.1's monitor instruction plus a payload that round-trips."""
    js = jobs(src, cfg)
    bad = [j["trial"] + ":" + j["view"] for j in js if j["instruction"] != rv.MONITOR or rebuilt(j) != j["saved_prompt"]
           or (("trace" in j["payload"]) != (j["view"] == "trace"))]
    return {"jobs": len(js), "trials": len({j["trial"] for j in js}), "mismatches": bad}


def out_path(base, job):
    rel = Path(job["trial"])
    return base / "results" / "judgments" / rel.parent / ("%s-%s.json" % (rel.stem, job["view"]))


def source_digest(src=SRC, cfg=None):
    cfg = cfg or load_cfg()
    lines = ["%s  %s" % (sha(p.read_bytes()), p.relative_to(src).as_posix()) for p in source_trials(src, cfg["source_series"])]
    return sha("\n".join(lines) + "\n"), len(lines)


def freeze_record(base=BASE, src=SRC):
    cfg = load_cfg(base)
    trials_sha, n = source_digest(src, cfg)
    return {"sha256": {n_: sha((base / n_).read_bytes()) for n_ in FROZEN_FILES},
            "source_sha256": {n_: sha((src / n_).read_bytes()) for n_ in SOURCE_FILES},
            "source_trials_sha256": trials_sha, "source_trial_files": n}


def freeze(base=BASE, src=SRC):
    path = base / "freeze.json"
    if path.exists():
        raise SystemExit("freeze.json already exists; it is never overwritten.")
    c = check(src, load_cfg(base))
    if c["mismatches"] or c["jobs"] != 720:
        raise SystemExit("prompt check failed: %s" % json.dumps(c)[:500])
    record = dict(frozen_utc=rv.now(), jobs=c["jobs"], **freeze_record(base, src))
    path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


def verify_freeze(base=BASE, src=SRC):
    path = base / "freeze.json"
    if not path.exists():
        raise SystemExit("freeze.json missing: freeze and push before any GPT call.")
    saved, now_ = json.loads(path.read_text()), freeze_record(base, src)
    for k in ("sha256", "source_sha256", "source_trials_sha256", "source_trial_files"):
        if saved[k] != now_[k]:
            raise SystemExit("Frozen input changed since freeze: %s" % k)
    return saved


def budget_for(base, cfg):
    rv.check_prices(cfg, [NAME])
    return rv.Budget(base / "results" / "spend-ledger.jsonl", cfg["cap_usd"], {NAME: cfg["prices_usd_per_million_tokens"][NAME]})


def model_ok(item, cfg):
    m = cfg["models"][NAME]
    return item.get("returned_model") == m["model"] and item.get("returned_effort") == m["effort"]


def preflight(base=BASE, factory=build):
    """One tiny call with no experimental data. Passes only if the session log shows the configured model and effort."""
    cfg = load_cfg(base)
    budget = budget_for(base, cfg)
    log = []
    answer = rv.ask(factory(NAME, cfg["models"][NAME]), "preflight", 'Return {"ok":true} only.', {}, 0, log, budget,
                    cfg["models"][NAME]["max_tokens"])
    item = log[-1]
    report = {"ok": answer.get("ok") is True and model_ok(item, cfg), "returned_model": item.get("returned_model"),
              "returned_effort": item.get("returned_effort"), "error": item.get("error"), "usd": item.get("usd")}
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 3


def judge_one(job, provider, budget, cfg, base):
    """Send one saved prompt. Writes the judgment file exactly once. Raises CallFailed (no file) if no response came back
    after all retries, and ModelMismatch (file written, excluded from analysis) if Codex ran another model or effort."""
    f = out_path(base, job)
    if f.exists():
        return None
    if rebuilt(job) != job["saved_prompt"]:
        raise SystemExit("prompt mismatch for %s %s" % (job["trial"], job["view"]))
    log = []
    answer = rv.ask(provider, "monitor_gpt_%s" % job["view"], rv.MONITOR, job["payload"], job["seed"], log, budget,
                    cfg["models"][NAME]["max_tokens"])
    item = log[-1]
    assert item["prompt"] == job["saved_prompt"]
    if "raw" not in item:
        raise CallFailed("%s %s: %s" % (job["trial"], job["view"], item.get("error")))
    verdict = answer["violation"] if type(answer.get("violation")) is bool else None
    rec = {"trial": job["trial"], "view": job["view"], "verdict": verdict, "model_verified": model_ok(item, cfg),
           "prompt_sha256": sha(item["prompt"]), "call": item, "finished_utc": rv.now()}
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("x") as fh:
        fh.write(json.dumps(rec, indent=2, ensure_ascii=False))
    if not rec["model_verified"]:
        raise ModelMismatch("%s %s: model %s effort %s" % (job["trial"], job["view"], item.get("returned_model"), item.get("returned_effort")))
    return rec


def run(base=BASE, src=SRC, factory=build, workers=None):
    verify_freeze(base, src)
    cfg = load_cfg(base)
    budget = budget_for(base, cfg)
    provider = factory(NAME, cfg["models"][NAME])
    todo = jobs(src, cfg)
    random.Random(cfg["order_seed"]).shuffle(todo)
    todo = [j for j in todo if not out_path(base, j).exists()]
    stop, lock, done = threading.Event(), threading.Lock(), [0]

    def work(job):
        if stop.is_set():
            return
        try:
            judge_one(job, provider, budget, cfg, base)
        except (rv.BudgetStop, CallFailed, ModelMismatch):
            stop.set()  # at once, so no worker starts another call; calls already in flight finish and are saved
            raise
        with lock:
            done[0] += 1
            if done[0] % 20 == 0 or done[0] == len(todo):
                print("judged %d of %d this run  spent %.2f USD" % (done[0], len(todo), budget.spent), flush=True)

    status = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers or cfg["workers"]) as pool:
        futures = [pool.submit(work, j) for j in todo]
        for fut in concurrent.futures.as_completed(futures):
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
        return 0 if not c["mismatches"] and c["jobs"] == 720 else 1
    if a.command == "freeze":
        freeze()
        return 0
    if a.command == "preflight":
        return preflight()
    return run(workers=a.workers)


if __name__ == "__main__":
    sys.exit(main())
