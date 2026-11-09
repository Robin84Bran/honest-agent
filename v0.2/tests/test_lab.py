import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from run import monitor_view, trial
from sandbox import Sandbox, policy_checker
from metrics import summarize

TASK = json.loads((ROOT/"experiments/tasks.json").read_text())["file"]


class Fixture:
    """Deterministic plumbing test, never used to generate research results."""
    def __init__(self, replies):
        self.replies = iter(replies)

    def generate(self, prompt, seed):
        return json.dumps(next(self.replies)), 10, 5


class LabTests(unittest.TestCase):
    def test_late_approval_does_not_erase_violation(self):
        box = Sandbox(TASK)
        box.call({"tool":TASK["tool"], "target":TASK["target"], "value":TASK["value"]})
        box.call({"tool":"request_approval","target":TASK["target"]})
        self.assertEqual(box.truth(), {"completed":True,"violation":True})
        self.assertTrue(policy_checker(box.trace))

    def test_wrong_target_has_no_effect(self):
        box = Sandbox(TASK)
        box.call({"tool":"write_file","target":"/etc/test","value":"x"})
        self.assertFalse(box.resources)
        self.assertFalse(box.events)

    def test_monitor_boundary(self):
        self.assertEqual(set(monitor_view({}, None)), {"task","report"})
        self.assertEqual(set(monitor_view({}, None, [])), {"task","report","trace"})

    def test_compliant_but_inaccurate_report(self):
        replies = [{"goal":TASK["goal"]},{"tool":"request_approval","target":TASK["target"]},
                   {"tool":TASK["tool"],"target":TASK["target"],"value":TASK["value"]},
                   {"tool":"finish"},{"completed":False,"violation":False},
                   {"violation":None},{"violation":False}]
        row = trial(Fixture(replies), TASK, 1)
        metrics = summarize([row])
        self.assertEqual(metrics["completion"]["rate"],1)
        self.assertEqual(metrics["report_accuracy"]["rate"],0)
        self.assertIsNone(metrics["monitors"]["policy"]["recall"]["rate"])
        self.assertEqual(metrics["monitors"]["final"]["unknown"],1)
