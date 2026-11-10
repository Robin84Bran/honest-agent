"""Paired parameter sweep for The Swarm Illusion v0.2."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from dataset import generate
from scoring import score, summarize
from simulator import monitor, public_view, simulate

CORRUPTION = (0, .02, .04, .08, .16)
OMISSION = (0, .4, .8)
CONDITIONS = [(0, 0, 0)] + [(.07, c, o) for c in CORRUPTION for o in OMISSION]
KEYS = ('local_rate', 'corruption', 'omission', 'ticks', 'agents')


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def run(out, first_seed, seeds, per_level):
    out.mkdir(parents=True, exist_ok=True)
    pooled = defaultdict(Counter)
    seed_rows = []
    signs = defaultdict(Counter)
    for seed in range(first_seed, first_seed + seeds):
        tasks, ledger = generate(seed, per_level)
        for local, corrupt, omit in CONDITIONS:
            for ticks in (10, 13):
                for agents in (1, 2, 4):
                    key = local, corrupt, omit, ticks, agents
                    counts = Counter()
                    correct_ids = set()
                    for task in tasks:
                        trace = simulate(task, seed, agents, ticks, 13, local, corrupt, omit)
                        verdict = monitor(task, public_view(trace))
                        result = score(trace, ledger[task['id']], verdict)
                        counts.update(result)
                        if result['correct']:
                            correct_ids.add(task['id'])
                    if agents == 1:
                        solo_ids = correct_ids
                    counts['gained_vs_one'] = len(correct_ids - solo_ids)
                    counts['lost_vs_one'] = len(solo_ids - correct_ids)
                    delta = len(correct_ids) - len(solo_ids)
                    counts['delta_vs_one'] = delta
                    signs[key]['win' if delta > 0 else 'loss' if delta < 0 else 'tie'] += 1
                    pooled[key].update(counts)
                    seed_rows.append(dict(seed=seed, **dict(zip(KEYS, key)), **summarize(counts)))
    rows = [dict(**dict(zip(KEYS, key)), **summarize(counts),
                 **{f'seeds_{s}': signs[key][s] for s in ('win', 'tie', 'loss')})
            for key, counts in pooled.items()]
    write_csv(out / 'pooled.csv', rows)
    write_csv(out / 'per_seed.csv', seed_rows)
    settings = dict(version='0.2', first_seed=first_seed, seeds=seeds, per_level=per_level,
                    conditions=CONDITIONS, condition_order=KEYS[:3], ticks=[10,13],
                    agents=[1,2,4], max_team_actions=13)
    (out / 'settings.json').write_text(json.dumps(settings, indent=2) + '\n')
    print(f'{len(rows)} pooled cells, {len(seed_rows)} seed cells, '
          f'{sum(r["tasks"] for r in rows):,} task runs')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first-seed', type=int, default=20261108)
    parser.add_argument('--seeds', type=int, default=8)
    parser.add_argument('--per-level', type=int, default=30)
    parser.add_argument('--out', type=Path, default=Path('replay'))
    args = parser.parse_args()
    if min(args.seeds, args.per_level) < 1:
        parser.error('seeds and per-level must be positive')
    run(args.out, args.first_seed, args.seeds, args.per_level)
