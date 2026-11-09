import datetime
import itertools
import json
from pathlib import Path
import platform
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'reference/src'))
from providers import Provider, ollama
from trial import digest, save, trial

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def main():
    freeze = json.loads((ROOT/'reference/experiments/deployment-freeze.json').read_text())
    for p in (ROOT/'reference/src').glob('*.*'):
        assert digest(p) == freeze['sha256']['src/'+p.name]
    tasks = ROOT/'reference/experiments/tasks.json'
    assert digest(tasks) == freeze['sha256']['experiments/tasks.json']
    task = json.loads(tasks.read_text())['deployment']
    model = freeze['run']['model']
    provider = Provider(SimpleNamespace(model=model,provider='ollama'))
    assert provider.identity == freeze['model_digest']
    assert ollama('/api/version')['version'] == freeze['ollama_version']
    out=ROOT/'runs'
    out.mkdir(exist_ok=False)
    orders=list(itertools.permutations([4,8,12]))
    schedule=[(s,b) for s in range(20) for b in orders[s%6]]
    show=ollama('/api/show',{'model':model})
    save(out/'model.json',show)
    save(out/'preregistration.json',dict(timestamp=now(),schedule=schedule,
         file_sha256={str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'protocol.md',ROOT/'execute.py',ROOT/'trial.py',ROOT/'audit.json', *sorted((ROOT/'reference').rglob('*.*'))]},
         model_sha256=digest(out/'model.json'),model_digest=provider.identity,
         platform=platform.platform(),python=sys.version,runtime=freeze['ollama_version'],options=freeze['generation']))
    for seed,budget in schedule:
        row=trial(provider,task,seed,budget)
        save(out/f's{seed:02d}-b{budget}.json',row)
        if not row['actor_started'] or any('raw' not in c for c in row['calls']):
            raise RuntimeError('Provider unavailable; partial evidence retained.')
    save(out/'manifest.json',dict(finished=now(),sha256={p.name:digest(p) for p in sorted(out.glob('*.json'))}))

if __name__ == '__main__':
    main()
