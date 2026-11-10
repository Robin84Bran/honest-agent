"""Offline tests for protocol 0.3.2. No network, no keys, no spending. Run from v0.3.2/: python3 -B test_v032.py"""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import judge_v032 as jv
import analyze_v032 as av
from judge_v032 import rv
from providers_api import ProviderError
from sandbox_v031 import policy_checker

HERE = Path(__file__).resolve().parent


class FakeGPT:
    """Stands in for CodexCLI. Trace view: the policy checker's verdict. Final view: no verdict."""
    paid = True

    def __init__(self, name, model="gpt-6-sol", effort="medium", fail=False):
        self.name, self.model, self.effort, self.fail, self.calls = name, model, effort, fail, 0

    def generate(self, prompt, seed):
        self.calls += 1
        if self.fail:
            raise ProviderError("HTTP 500: simulated outage")
        view = json.loads(prompt.split("\nInput:\n", 1)[1])
        verdict = policy_checker(view["trace"]) if "trace" in view else None
        text = '{"ok":true}' if not view else json.dumps({"violation": verdict})
        return {"text": text, "input_tokens": 14300, "output_tokens": 20, "returned_model": self.model,
                "returned_effort": self.effort, "stop_reason": "completed"}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for n in jv.FROZEN_FILES:
            shutil.copy(HERE / n, self.tmp / n)
        self.waits = rv.RETRY_WAITS
        rv.RETRY_WAITS = (0, 0, 0, 0)

    def tearDown(self):
        rv.RETRY_WAITS = self.waits
        shutil.rmtree(self.tmp)

    def factory(self, **kw):
        self.fake = None

        def make(name, cfg):
            self.fake = FakeGPT(name, **kw)
            return self.fake
        return make

    def judgments(self):
        return sorted((self.tmp / "results" / "judgments").rglob("*.json")) if (self.tmp / "results" / "judgments").exists() else []


class TestInputs(unittest.TestCase):
    def test_saved_prompts_rebuild_exactly(self):
        c = jv.check()
        self.assertEqual((c["jobs"], c["trials"], c["mismatches"]), (720, 360, []))

    def test_source_code_is_v031_frozen_code(self):
        frozen = json.loads((jv.SRC / "freeze.json").read_text())["sha256"]
        for n in ("run_v031.py", "providers_api.py", "analyze_v031.py", "sandbox_v031.py"):
            self.assertEqual(hashlib.sha256((jv.SRC / n).read_bytes()).hexdigest(), frozen[n], n)

    def test_instruction_is_v031_monitor_instruction(self):
        self.assertTrue(all(j["instruction"] == rv.MONITOR for j in jv.jobs()))

    def test_order_is_fixed(self):
        cfg = jv.load_cfg()
        a, b = jv.jobs(cfg=cfg), jv.jobs(cfg=cfg)
        jv.random.Random(cfg["order_seed"]).shuffle(a)
        jv.random.Random(cfg["order_seed"]).shuffle(b)
        self.assertEqual([(j["trial"], j["view"]) for j in a], [(j["trial"], j["view"]) for j in b])


class TestRun(Base):
    def test_refuses_without_freeze(self):
        with self.assertRaises(SystemExit):
            jv.run(self.tmp, factory=self.factory())

    def test_refuses_if_frozen_file_changed(self):
        jv.freeze(self.tmp)
        (self.tmp / "config.json").write_text((self.tmp / "config.json").read_text().replace('"workers": 4', '"workers": 3'))
        with self.assertRaises(SystemExit):
            jv.run(self.tmp, factory=self.factory())

    def test_full_run_resume_and_analysis(self):
        jv.freeze(self.tmp)
        self.assertEqual(jv.run(self.tmp, factory=self.factory(), workers=4), 0)
        files = self.judgments()
        self.assertEqual(len(files), 720)
        ledger = (self.tmp / "results" / "spend-ledger.jsonl").read_text().splitlines()
        self.assertEqual(len(ledger), 720)
        spent = sum(json.loads(l)["usd"] for l in ledger)
        self.assertLess(spent, 40)
        before = {f: f.read_bytes() for f in files}
        self.assertEqual(jv.run(self.tmp, factory=self.factory()), 0)
        self.assertEqual(self.fake.calls, 0)  # resume sends nothing already saved
        self.assertEqual({f: f.read_bytes() for f in self.judgments()}, before)
        rec = json.loads(files[0].read_text())
        self.assertTrue(rec["model_verified"])
        self.assertEqual(rec["call"]["prompt"].split("\nInput:\n")[0], rv.MONITOR)
        res = av.analyse(*av.load_rows(self.tmp))
        self.assertEqual((res["trajectories"], res["breaches"], res["compliant"]), (360, 67, 293))
        m = res["monitors"]
        self.assertEqual(m["gpt_trace"]["caught_of_all_breaches"]["numerator"], 67)
        self.assertEqual(m["gpt_trace"]["false_alarms_of_all_compliant"]["numerator"], 0)
        self.assertEqual(m["gpt_final"]["confusion"]["unknown"], 360)
        # Claude's numbers come through unchanged from v0.3.1
        self.assertEqual(m["claude_trace"]["caught_of_all_breaches"]["numerator"], 67)
        self.assertEqual(m["claude_final"]["caught_of_all_breaches"]["numerator"], 0)
        self.assertEqual(res["final_view_by_report"]["claude"]["not completed, no violation"]["verdicts"]["no violation"], 68)
        self.assertEqual(res["predictions"], {k: True for k in res["predictions"]})
        self.assertFalse(res["rq1_gpt"]["pooled"]["testable"])
        self.assertIn("RQ1 with GPT-6 Sol", av.markdown(res))

    def test_call_failure_stops_and_writes_no_judgment(self):
        jv.freeze(self.tmp)
        self.assertEqual(jv.run(self.tmp, factory=self.factory(fail=True), workers=1), 5)
        self.assertEqual(self.judgments(), [])
        stop = json.loads((self.tmp / "results" / "stops.jsonl").read_text().splitlines()[0])
        self.assertEqual(stop["kind"], "call_failed")

    def test_model_mismatch_stops_and_is_excluded(self):
        jv.freeze(self.tmp)
        self.assertEqual(jv.run(self.tmp, factory=self.factory(model="gpt-6-astra"), workers=1), 6)
        files = self.judgments()
        self.assertEqual(len(files), 1)
        self.assertFalse(json.loads(files[0].read_text())["model_verified"])
        rows, excluded = av.load_rows(self.tmp)
        self.assertEqual(excluded["model_not_verified"] + excluded["missing"], 360)

    def test_effort_mismatch_is_a_model_mismatch(self):
        jv.freeze(self.tmp)
        self.assertEqual(jv.run(self.tmp, factory=self.factory(effort="high"), workers=1), 6)

    def test_freeze_never_overwritten(self):
        jv.freeze(self.tmp)
        with self.assertRaises(SystemExit):
            jv.freeze(self.tmp)

    def test_preflight(self):
        self.assertEqual(jv.preflight(self.tmp, factory=self.factory()), 0)
        self.assertEqual(jv.preflight(self.tmp, factory=self.factory(model="gpt-6-luna")), 3)


if __name__ == "__main__":
    unittest.main(verbosity=1)
