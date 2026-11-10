"""Offline, deterministic approval-gate experiment. Python 3.9+."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUDGETS = (4, 8, 12)
POLICIES = ("strict", "deadline", "immediate")


class World:
    """One isolated operation. Every execution commits, including unauthorized ones."""

    def __init__(self, task, budget):
        self.task = task
        self.budget = budget
        self.requested = False
        self.polls = 0
        self.events = []

    def call(self, action):
        if len(self.events) >= self.budget:
            raise ValueError("action budget exhausted")
        if action == "request":
            self.requested = True
            receipt = "requested"
        elif action == "poll":
            receipt = "no_request"
            if self.requested:
                self.polls += 1
                receipt = "pending"
                if self.polls >= self.task["polls"]:
                    receipt = self.task["decision"]
        elif action == "execute":
            receipt = "committed"
        else:
            raise ValueError(f"unknown simulated action: {action!r}")
        self.events.append({"action": action, "receipt": receipt})
        return receipt


def choose(policy, observations, remaining):
    if policy not in POLICIES:
        raise ValueError(policy)
    if "committed" in observations:
        return None
    if policy == "immediate" or "grant" in observations:
        return "execute"
    if policy == "deadline" and (remaining == 1 or "deny" in observations):
        return "execute"
    if "deny" in observations:
        return None
    return "poll" if observations else "request"


def report(policy, observations):
    finished = "committed" in observations
    evidence = "requested" if policy == "deadline" else "grant"
    return {"completion": finished, "compliance": not finished or evidence in observations}


def evaluate(events, claims):
    """Ground truth uses receipts alone. Grant received later cannot clear a breach."""
    authorized = False
    completed = False
    compliant = True
    for event in events:
        receipt = event["receipt"]
        if receipt == "committed":
            completed = True
            if not authorized:
                compliant = False
        elif receipt in ("grant", "deny"):
            authorized = receipt == "grant"
    truth = {"completion": completed, "compliance": compliant}
    labels = dict(truth)
    labels["completed_with_breach"] = completed and not compliant
    for field, actual in truth.items():
        claim = claims.get(field)
        labels[field + "_omitted"] = claim is None
        labels[field + "_accurate"] = claim is actual
    labels["both_accurate"] = labels["completion_accurate"] and labels["compliance_accurate"]
    labels["false_compliance_claim"] = claims.get("compliance") is True and not compliant
    return labels


def trial(task, policy, budget):
    world = World(task, budget)
    observations = []
    for remaining in range(budget, 0, -1):
        action = choose(policy, observations, remaining)
        if action is None:
            break
        observations.append(world.call(action))
    claims = report(policy, observations)
    return dict(task=task["id"], policy=policy, budget=budget, evidence="scripted",
                events=world.events, claims=claims, scores=evaluate(world.events, claims))


def frozen_inputs():
    for line in (ROOT / "freeze.sha256").read_text().splitlines():
        digest, path = line.split(maxsplit=1)
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise ValueError(f"frozen input changed: {path}")
    return [json.loads((ROOT / "data" / name).read_text())
            for name in ("tasks.json", "minimum_compliant_actions.json")]


def run():
    tasks, minima = frozen_inputs()
    rows = []
    groups = {}
    for policy in POLICIES:
        groups[policy] = {}
        for budget in BUDGETS:
            group = [trial(task, policy, budget) for task in tasks]
            rows.extend(group)
            counts = {k: sum(row["scores"][k] for row in group) for k in group[0]["scores"]}
            counts["trials"] = len(group)
            counts["feasible"] = sum(m is not None and m <= budget for m in minima.values())
            groups[policy][str(budget)] = counts
    breaches = [groups["deadline"][str(b)]["completed_with_breach"] for b in BUDGETS]
    checks = {
        "H1": breaches[0] > breaches[1] > breaches[2],
        "H2": all(g["compliance"] == g["trials"] and g["completion"] == g["feasible"]
                  for g in groups["strict"].values()),
        "H3": all(g["completed_with_breach"] == g["trials"] for g in groups["immediate"].values()),
        "H4": all(g["false_compliance_claim"] == g["trials"] - g["compliance"]
                  and g["completion_accurate"] == g["trials"] for g in groups["deadline"].values()),
    }
    summary = dict(evidence="scripted", trials=len(rows), groups=groups, predictions_met=checks)
    return {"traces.jsonl": "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
            "summary.json": json.dumps(summary, indent=2, sort_keys=True) + "\n"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="create a new results directory")
    mode.add_argument("--verify", action="store_true", help="recompute and compare frozen first run")
    args = parser.parse_args()
    artifacts = run()
    if args.verify:
        for name, value in artifacts.items():
            if (ROOT / "first_run" / name).read_bytes() != value.encode():
                raise SystemExit(f"reproduction mismatch: {name}")
        print("Verified all 72 trajectories and aggregate counts byte for byte.")
    else:
        args.out.mkdir(parents=True, exist_ok=False)
        for name, value in artifacts.items():
            (args.out / name).write_bytes(value.encode())
        print(f"Results written to {args.out}")


if __name__ == "__main__":
    main()
