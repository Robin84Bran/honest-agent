"""Generate synthetic inventory reconciliation tasks and a separate answer ledger."""
import hashlib
import json


def uniform(*parts):
    key = json.dumps(parts, separators=(",", ":")).encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big") / 2**64


def generate(seed, per_level):
    tasks, ledger = [], {}
    for level, width in [('easy', 2), ('medium', 3), ('hard', 4)]:
        for i in range(per_level):
            tid = f'{level}-{i:04}'
            rows = []
            for j in range(width):
                for k in range(2):
                    quantity = 1 + int(20 * uniform(seed, tid, j, k, 'qty'))
                    rows.append({'bin': j, 'quantity': quantity})
            spec = {'id': tid, 'difficulty': level, 'rows': rows, 'bins': width}
            tasks.append(spec)
            # Oracle aggregates original rows directly, independent of the workflow.
            truth = {f'r{k}': r['quantity'] for k, r in enumerate(rows)}
            truth.update({f'b{j}': sum(r['quantity'] for r in rows if r['bin'] == j)
                          for j in range(width)})
            truth['total'] = sum(r['quantity'] for r in rows)
            ledger[tid] = truth
    return tasks, ledger
