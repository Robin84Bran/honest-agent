"""Usage: python3 -B compare_archive.py /path/to/original/results/deployment-heldout"""
import json
from pathlib import Path
import sys
from analyze import ROOT,read,digest

folder=Path(sys.argv[1])
manifest=read(ROOT/'reference/original-manifest.json')
assert digest(folder/'manifest.json')==digest(ROOT/'reference/original-manifest.json')
for path,sha in manifest['output_sha256'].items():
    assert digest(folder/path)==sha
counts=dict(trace=0,truth=0,report=0,monitors=0)
for seed in range(20):
    old=read(folder/f'trial-{seed}.json')
    fresh=read(ROOT/f'runs/s{seed:02d}-b4.json')
    for k in counts:
        counts[k]+=old[k]==fresh[k]
print(json.dumps(counts,indent=2))
