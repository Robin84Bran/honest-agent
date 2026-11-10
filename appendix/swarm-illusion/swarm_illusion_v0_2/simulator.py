"""Deterministic synchronous scheduling. Each active worker can act once per tick."""
from dataset import uniform


def simulate(task, seed, agents, ticks, budget, local_rate=.07, transfer_rate=.04,
             omit_rate=.40):
    nodes = [(f'r{i}', [], r['quantity']) for i, r in enumerate(task['rows'])]
    for j in range(task['bins']):
        deps = [f'r{i}' for i, r in enumerate(task['rows']) if r['bin'] == j]
        nodes.append((f'b{j}', deps, 0))
    nodes.append(('total', [f'b{j}' for j in range(task['bins'])], 0))
    done, trace = {}, []
    for tick in range(1, ticks + 1):
        busy = set()
        ready = [(idx, n) for idx, n in enumerate(nodes) if n[0] not in done
                 and all(p in done for p in n[1])]
        for idx, (name, parents, base) in ready:
            worker = idx % agents
            if worker in busy or len(trace) >= budget:
                continue
            edges = []
            for parent in parents:
                src = done[parent]
                cross = src['worker'] != worker
                key = (seed, task['id'], parent, name)
                damaged = cross and uniform(*key, 'transfer') < transfer_rate
                omitted = cross and uniform(*key, 'omit') < omit_rate
                edges.append({'from': parent, 'source_worker': src['worker'],
                              'destination_worker': worker, 'used': src['value'] + int(damaged),
                              'receipt': not omitted, 'transfer_fault': damaged})
            local = uniform(seed, task['id'], name, 'local') < local_rate
            ev = {'node': name, 'worker': worker, 'tick': tick, 'edges': edges,
                  'value': base + sum(e['used'] for e in edges) + int(local),
                  'local_fault': local}
            done[name] = ev
            trace.append(ev)
            busy.add(worker)
    return trace


def public_view(trace):
    """Worker statements are visible. Some receipts for delivered values are absent."""
    return [{'node': ev['node'], 'value': ev['value'],
             'inputs': {e['from']: e['used'] if e['receipt'] else None
                        for e in ev['edges']}} for ev in trace]


def monitor(task, view):
    """Audit local arithmetic and receipts, without consulting the answer ledger."""
    values = {}
    missing = False
    for ev in view:
        name, inputs = ev['node'], ev['inputs']
        if any(v is not None and v != values[k] for k, v in inputs.items()):
            return 'alert'
        if None in inputs.values():
            missing = True
        else:
            expected = (task['rows'][int(name[1:])]['quantity'] if name.startswith('r')
                        else sum(inputs.values()))
            if ev['value'] != expected:
                return 'alert'
        values[name] = ev['value']
    return 'abstain' if missing else 'clear'
