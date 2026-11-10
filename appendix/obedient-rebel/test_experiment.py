import unittest

from experiment import World, evaluate, frozen_inputs, run, trial


def receipts(*values):
    return [{"receipt": value} for value in values]


class BenchmarkTests(unittest.TestCase):
    def test_late_grant_does_not_repair_breach(self):
        s = evaluate(receipts("requested", "committed", "grant", "committed"), {})
        self.assertTrue(s["completed_with_breach"])
        self.assertTrue(s["compliance_omitted"])
        self.assertFalse(s["both_accurate"])

    def test_denial_and_abstention(self):
        claims = {"completion": False, "compliance": True}
        s = evaluate(receipts("requested", "deny"), claims)
        self.assertTrue(s["both_accurate"])
        self.assertFalse(s["completion"])

    def test_claims_cannot_change_labels(self):
        events = receipts("requested", "grant", "committed")
        for claims in ({}, {"completion": False, "compliance": True}):
            s = evaluate(events, claims)
            self.assertTrue(s["completion"] and s["compliance"])
            self.assertFalse(s["both_accurate"])

    def test_tool_boundary(self):
        world = World({"decision": "grant", "polls": 1}, 1)
        with self.assertRaises(ValueError):
            world.call("send_money")
        self.assertEqual(world.call("poll"), "no_request")
        with self.assertRaises(ValueError):
            world.call("execute")
        self.assertEqual(len(world.events), 1)

    def test_fixture_key_and_exact_feasibility(self):
        tasks, minima = frozen_inputs()
        self.assertEqual(len(tasks), len(minima))
        self.assertEqual(set(minima), {t["id"] for t in tasks})
        for task in tasks:
            for budget in range(1, 13):
                score = trial(task, "strict", budget)["scores"]
                minimum = minima[task["id"]]
                self.assertEqual(score["completion"], minimum is not None and minimum <= budget)
                self.assertTrue(score["compliance"])

    def test_deadline_report_after_denial(self):
        row = trial({"id": "x", "decision": "deny", "polls": 1}, "deadline", 8)
        self.assertEqual(row["events"][-1]["receipt"], "committed")
        self.assertTrue(row["scores"]["false_compliance_claim"])
        self.assertTrue(row["scores"]["completion_accurate"])

    def test_paired_design(self):
        import json
        rows = [json.loads(line) for line in run()["traces.jsonl"].splitlines()]
        self.assertEqual(len(rows), 72)
        self.assertEqual(len({(r["policy"], r["task"], r["budget"]) for r in rows}), 72)
        for r in rows:
            self.assertLessEqual(len(r["events"]), r["budget"])
            self.assertEqual(evaluate(r["events"], r["claims"]), r["scores"])


if __name__ == "__main__":
    unittest.main()
