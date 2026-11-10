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


