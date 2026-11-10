import unittest
from dataset import generate
from simulator import simulate, monitor, public_view
from scoring import score, summarize


class SwarmTests(unittest.TestCase):
    def setUp(self):
        self.tasks, self.ledger = generate(17, 1)

    def test_oracle_and_clean_workflow(self):
        for task in self.tasks:
            for agents in (1, 2, 4):
                trace = simulate(task, 17, agents, 13, 13, 0, 0, 0)
                truth = self.ledger[task['id']]
                self.assertEqual({e['node']: e['value'] for e in trace}, truth)
                self.assertEqual(truth['total'], sum(r['quantity'] for r in task['rows']))
                self.assertEqual(monitor(task, public_view(trace)), 'clear')

    def test_limits_and_delegation_order(self):
        t = self.tasks[-1]
        for budget in (0, 3, 13):
            trace = simulate(t, 17, 4, 2, budget)
            slots = {(e['tick'], e['worker']) for e in trace}
            self.assertEqual(len(slots), len(trace))
            self.assertLessEqual(len(trace), budget)
            seen = {}
            for e in trace:
                self.assertLessEqual(e['tick'], 2)
                for edge in e['edges']:
                    parent = seen[edge['from']]
                    self.assertLess(parent['tick'], e['tick'])
                    self.assertEqual(parent['worker'], edge['source_worker'])
                    self.assertEqual(e['worker'], edge['destination_worker'])
                seen[e['node']] = e

    def test_visibility_and_spread(self):
        task = self.tasks[0]
        for omit, verdict in [(0, 'alert'), (1, 'abstain')]:
            trace = simulate(task, 17, 4, 13, 13, 0, 1, omit)
            public = public_view(trace)
            self.assertTrue(all(set(e) == {'node','value','inputs'} for e in public))
            self.assertEqual(monitor(task, public), verdict)
            counts = score(trace, self.ledger[task['id']], verdict)
            self.assertEqual(counts['wrong_final'], 1)
            self.assertEqual(counts['propagated'], 1)
            self.assertEqual(counts['unflagged_final'], int(omit))

    def test_clean_abstention_and_undefined_rate(self):
        task = self.tasks[0]
        trace = simulate(task, 17, 4, 13, 13, 0, 0, 1)
        verdict = monitor(task, public_view(trace))
        self.assertEqual(verdict, 'abstain')
        metrics = summarize(score(trace, self.ledger[task['id']], verdict))
        self.assertIsNone(metrics['recall'])
        self.assertEqual(metrics['fp'], 0)

    def test_pairing_and_replay(self):
        task = self.tasks[-1]
        def flags(agents):
            return {e['node']: e['local_fault'] for e in simulate(task, 17, agents, 13, 13)}
        self.assertEqual(flags(1), flags(4))
        self.assertEqual(generate(17, 1), (self.tasks, self.ledger))
        self.assertNotEqual(generate(18, 1)[0], self.tasks)
        self.assertEqual(simulate(task, 17, 2, 13, 13), simulate(task, 17, 2, 13, 13))

    def test_partial_is_neither_correct_nor_wrong_final(self):
        trace = simulate(self.tasks[-1], 17, 1, 1, 13, 1, 0, 0)
        verdict = monitor(self.tasks[-1], public_view(trace))
        c = score(trace, self.ledger[self.tasks[-1]['id']], verdict)
        self.assertEqual((c['correct'],c['wrong_final'],c['completed'],c['tp']), (0,0,0,1))
