"""Release-only helper (not part of the frozen study). In the public repository this folder is
appendix/obedient-rebel/v0.2.2, and the Honest Agent v0.3.1 code it imports sits at the repository root, not in the
sibling ../../Honest_Agent/v0.3.1 folder the frozen scripts expect on the original machine. This helper puts whichever
copy exists on the import path, re-checks the frozen hashes that don't depend on that location, rebuilds the analysis
and the post hoc output in memory, and compares them with the saved files. It writes nothing.
Run from this folder: python3 -B verify_release.py
"""
import hashlib
import io
import json
import runpy
import sys
from contextlib import redirect_stdout
from pathlib import Path

BASE = Path(__file__).resolve().parent
candidates = [BASE.parent.parent / "Honest_Agent" / "v0.3.1", BASE.parents[2] / "v0.3.1"]
src = next(p for p in candidates if (p / "analyze_v031.py").exists())
sys.path.insert(0, str(src))

freeze = json.loads((BASE / "freeze.json").read_text())
for name, digest in freeze["sha256"].items():
    assert hashlib.sha256((BASE / name).read_bytes()).hexdigest() == digest, name
for name, digest in freeze["source_sha256"].items():
    assert hashlib.sha256((src / name).read_bytes()).hexdigest() == digest, "v0.3.1/" + name
cfg = json.loads((BASE / "config.json").read_text())
runs = sorted((BASE / cfg["source"]).resolve().glob("*.json"))
lines = ["%s  %s" % (hashlib.sha256(p.read_bytes()).hexdigest(), p.name) for p in runs]
assert hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest() == freeze["source_runs_sha256"], "source runs"
print("frozen files, imported code and %d source runs match freeze.json" % len(runs))

import analyze_v022 as av  # noqa: E402
res = av.analyse(*av.load_rows(BASE))
assert json.dumps(res, indent=2) + "\n" == (BASE / "results" / "analysis.json").read_text(), "analysis.json"
assert av.markdown(res) == (BASE / "results" / "analysis.md").read_text(), "analysis.md"
print("analysis.json and analysis.md rebuild byte for byte")

saved = (BASE / "results" / "posthoc-report-pattern.json").read_text()
real_write = Path.write_text
captured = {}
Path.write_text = lambda self, text, *a, **k: captured.__setitem__(self.name, text)
try:
    with redirect_stdout(io.StringIO()):
        runpy.run_path(str(BASE / "posthoc_report_pattern.py"), run_name="__main__")
finally:
    Path.write_text = real_write
assert captured["posthoc-report-pattern.json"] == saved, "posthoc-report-pattern.json"
print("posthoc-report-pattern.json rebuilds byte for byte")
