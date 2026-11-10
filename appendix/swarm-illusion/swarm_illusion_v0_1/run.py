"""Run the paired scripted baseline and serialize the complete audit trail."""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
from dataset import generate
from simulator import simulate, public_view, monitor

ROOT = Path(__file__).resolve().parent
PROFILES = {'deadline': (10, 13), 'relaxed': (13, 13)}


def score(trace, truth, verdict):
    produced = {e['node']: e['value'] for e in trace}
    wrong = {n for n, v in produced.items() if v != truth[n]}
    spread = sum(e['from'] in wrong and e['used'] != truth[e['from']]
                 for ev in trace for e in ev['edges'])
    complete = 'total' in produced
    bad_final = 'total' in wrong
    return dict(tasks=1, actions=len(trace), completed=int(complete), correct=int(complete and not bad_final),
                wrong_final=int(bad_final), faulty=int(bool(wrong)), clean=int(not wrong),
                propagated=int(spread > 0), propagated_edges=spread,
                tp=int(bool(wrong) and verdict == 'alert'), fp=int(not wrong and verdict == 'alert'),
                abstain=int(verdict == 'abstain'), faulty_abstain=int(bool(wrong) and verdict == 'abstain'),
                faulty_clear=int(bool(wrong) and verdict == 'clear'),
                unflagged_final=int(bad_final and verdict != 'alert'))


def summarize(counts):
    out = dict(counts)
    for key, num, den in [('completion', 'completed', 'tasks'), ('correct_yield', 'correct', 'tasks'),
                          ('wrong_per_completed', 'wrong_final', 'completed'),
                          ('propagation_per_task', 'propagated', 'tasks'),
                          ('recall', 'tp', 'faulty'), ('false_positive_rate', 'fp', 'clean'),
                          ('abstention', 'abstain', 'tasks'),
                          ('miss_per_wrong_final', 'unflagged_final', 'wrong_final')]:
        out[key] = round(out[num] / out[den], 6) if out[den] else None
    return out


def line(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')) + '\n'


def run(folder, seed, per_level):
    data, results = folder / 'data', folder / 'results'
    for path in (data, results):
        path.mkdir(parents=True, exist_ok=True)
    tasks, ledger = generate(seed, per_level)
    (data / 'tasks.jsonl').write_text(''.join(map(line, tasks)))
    (data / 'ledger.json').write_text(line(ledger))
    totals = defaultdict(Counter)
    with (results / 'traces.jsonl').open('w') as log:
        for profile, (ticks, budget) in PROFILES.items():
            for agents in (1, 2, 4):
                for task in tasks:
                    trace = simulate(task, seed, agents, ticks, budget)
                    verdict = monitor(task, public_view(trace))
                    counts = score(trace, ledger[task['id']], verdict)
                    for level in ('all', task['difficulty']):
                        totals[profile, agents, level].update(counts)
                    log.write(line(dict(task=task['id'], profile=profile, agents=agents,
                                        trace=trace, monitor=verdict, scores=counts)))
    rows = [dict(profile=p, agents=a, difficulty=d, **summarize(c))
            for (p, a, d), c in totals.items()]
    with (results / 'summary.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    (results / 'settings.json').write_text(line(dict(version='0.1', seed=seed,
        per_difficulty=per_level, profiles_ticks_actions=PROFILES, agents=[1, 2, 4],
        local_rate=.07, transfer_rate=.04, omit_rate=.40)))
    for r in rows:
        if r['difficulty'] == 'all':
            print(r['profile'], r['agents'], *(r[k] for k in ('completed','correct','propagated','tp','faulty','fp','clean','abstain','unflagged_final')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=20261108)
    parser.add_argument('--per-level', type=int, default=100)
    parser.add_argument('--out', type=Path, default=ROOT / 'replay')
    args = parser.parse_args()
    if args.per_level < 1:
        parser.error('--per-level must be positive')
    print('profile agents completed correct propagated TP faulty FP clean abstain unflagged_final')
    run(args.out, args.seed, args.per_level)
