import csv
from pathlib import Path
import tempfile
import unittest

from run import run


class SweepTests(unittest.TestCase):
    def test_controls_pairing_and_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            run(Path(tmp), 9, 2, 2)
            with (Path(tmp) / 'pooled.csv').open() as f:
                rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 96)
        seen = {}
        for row in rows:
            n = lambda k: int(row[k])
            self.assertEqual(n('tasks'), 12)
            self.assertEqual(sum(n('seeds_' + s) for s in ('win','tie','loss')), 2)
            self.assertEqual(n('gained_vs_one') - n('lost_vs_one'), n('delta_vs_one'))
            if row['local_rate'] == '0':
                self.assertEqual(n('faulty') + n('abstain') + n('fp'), 0)
                expected = 8 if (n('ticks'), n('agents')) == (10, 1) else 12
                self.assertEqual(n('correct'), expected)
            key = tuple(row[k] for k in ('local_rate','corruption','ticks','agents'))
            seen.setdefault(key, n('correct'))
            self.assertEqual(seen[key], n('correct'))
            if n('ticks') == 13:
                self.assertEqual(n('actions'), 120)
                self.assertLessEqual(n('delta_vs_one'), 0)
