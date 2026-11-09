"""Verify recorded bytes and independently replay every observed tool call."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from sandbox import Sandbox, policy_checker
from metrics import summarize

folder = ROOT/"results/pilot"
manifest = json.loads((folder/"manifest.json").read_text())
for base, key in [(ROOT,"source_sha256"), (folder,"output_sha256")]:
    for name, expected in manifest[key].items():
        assert hashlib.sha256((base/name).read_bytes()).hexdigest() == expected, name
tasks = json.loads((ROOT/"experiments/tasks.json").read_text())
rows = []
for path in sorted(folder.glob("trial-*.json")):
    row = json.loads(path.read_text())
    box = Sandbox(tasks[manifest["config"]["family"]])
    for entry in row["trace"]:
        box.call(entry["call"])
    assert box.trace == row["trace"] and box.events == row["policy_events"]
    assert box.resources == row["resources"] and box.truth() == row["truth"]
    assert policy_checker(box.trace) == row["monitors"]["policy"]
    rows.append(row)
assert rows and summarize(rows) == json.loads((folder/"metrics.json").read_text())
print("Verified manifest hashes, sandbox replay and aggregate metrics.")
