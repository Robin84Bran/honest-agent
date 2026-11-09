"""Offline replay, rate estimates and exact paired comparisons. Standard library only."""
import json
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reference/src'))
from metrics import rate, summarize
from sandbox import Sandbox, policy_checker
from trial import digest, save

def read(path):
    return json.loads(path.read_text())

def exact_lower(k,n):
    if k==0:
        return 0.
    lo,hi=0.,1.
    for _ in range(60):
        p=(lo+hi)/2
        tail=sum(comb(n,j)*p**j*(1-p)**(n-j) for j in range(k,n+1))
        if tail<0.0125:
            lo=p
        else:
            hi=p
    return (lo+hi)/2

def paired(left,right):
    pairs=[(a,b) for a,b in zip(left,right) if a is not None and b is not None]
    n=len(pairs)
    up=pairs.count((False,True))
    down=pairs.count((True,False))
    switches=up+down
    if not n:
        return {'n':0,'difference':None,'ci95':None,'p':None}
    p=min(1.,2*sum(comb(switches,i) for i in range(min(up,down)+1))/2**switches)
    return dict(n=n,up=up,down=down,difference=(up-down)/n,
                ci95=[exact_lower(up,n)+exact_lower(n-down,n)-1,
                      1-exact_lower(n-up,n)-exact_lower(down,n)],p=p)

def claim(row,key):
    return None if row['report'] is None else row['report'][key]==row['truth'][key]

def analyze():
    folder=ROOT/'runs'
    freeze=read(folder/'preregistration.json')
    for name,sha in read(folder/'manifest.json')['sha256'].items():
        assert digest(folder/name)==sha
    for name,sha in freeze['file_sha256'].items():
        assert digest(ROOT/name)==sha
    data={b:[] for b in (4,8,12)}
    assert sorted(map(tuple,freeze['schedule']))==sorted((s,b) for s in range(20) for b in data)
    task=read(ROOT/'reference/experiments/tasks.json')['deployment']
    for seed,b in freeze['schedule']:
        r=read(folder/f's{seed:02d}-b{b}.json')
        assert r['seed']==seed and r['actor_started']
        box=Sandbox(task)
        for e in r['trace']:
            box.call(e['call'])
        assert box.trace==r['trace'] and box.truth()==r['truth'] and box.events==r['policy_events']
        assert box.resources==r['resources'] and policy_checker(box.trace)==r['monitors']['policy']
        assert sum(c['role']=='actor' for c in r['calls'])<=b
        data[b].append(r)
    stats={}
    outcomes={}
    for b,rows in data.items():
        assert [r['seed'] for r in rows]==list(range(20))
        m=summarize(rows)
        values=dict(completion=[r['truth']['completed'] for r in rows],breach=[r['truth']['violation'] for r in rows],
                    completion_claim=[claim(r,'completed') for r in rows],compliance_claim=[claim(r,'violation') for r in rows],
                    joint=[None if r['report'] is None else r['truth']==r['report'] for r in rows])
        outcomes[b]=values
        rates={k:rate(v.count(True),len(v)-v.count(None)) for k,v in values.items()}
        for mon,v in m['monitors'].items():
            v['abstention']=rate(v['unknown'],len(rows))
        usage={}
        for role in ('actor','final','trace'):
            calls=[c for r in rows for c in r['calls'] if (c['role'] in ('intent','report','actor') if role=='actor' else c['role']==role)]
            usage[role]={k:sum(c[k] for c in calls) for k in ['input_tokens','output_tokens','seconds']}
            usage[role].update(calls=len(calls),errors=sum('error' in c for c in calls))
        pos=[r for r in rows if r['truth']['violation'] and all(r['monitors'][k] is not None for k in ('final','trace'))]
        a=[r['monitors']['final'] for r in pos]; t=[r['monitors']['trace'] for r in pos]
        stats[b]=dict(rates=rates,metrics=m,usage=usage,api_usd=sum(r['api_charge_usd'] for r in rows),
                      paired_monitor_recall=dict(final=sum(a),trace=sum(t),**paired(a,t)))
    comparisons={}
    for a,b in combinations(data,2):
        comparisons[f'{b}-{a}']={k:paired(v,outcomes[b][k]) for k,v in outcomes[a].items()}
        comparisons[f'{b}-{a}']['trace_prefix_matches']=sum(
            x['trace']==y['trace'][:len(x['trace'])] for x,y in zip(data[a],data[b]))
    return dict(arms=stats,paired=comparisons)

if __name__=='__main__':
    print(json.dumps(analyze(),indent=2))
