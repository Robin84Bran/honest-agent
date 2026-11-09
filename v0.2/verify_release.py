"""Release-only helper, added 9 Nov 2026 when v0.2 was published. It is not part of v0.2's evidence.

One v0.2 file had a local path redacted for publication: action-budget/runs/model.json. Its Modelfile line
"FROM <path>/blobs/sha256-1837..." pointed into the author's local Ollama store. Because analyze.py checks
that file's SHA-256 against runs/manifest.json, the unchanged analyze.py stops on this copy by design.

This script runs the unchanged action-budget/analyze.py. It accepts model.json only if the file's hash
equals the published redacted hash below; in that case it reports the original hash in its place. Every
other hash, the full sandbox replay and all statistics are checked exactly as analyze.py does. Finally it
confirms that the regenerated statistics equal the published analysis.json.

Run from the repository root:  python3 -B v0.2/verify_release.py
"""
import json
import sys
from pathlib import Path

AB = Path(__file__).resolve().parent / "action-budget"
REDACTED = {  # file -> (hash of the published redacted copy, original hash recorded in runs/manifest.json)
    AB / "runs" / "model.json": ("a3ac28f71951da51ce4ef851c0bfdc62a772921f4e08666d27d3f2bf4bed0779",
                                 "b7e15e896c3cbbc2f14300d0276d3b9936a8d548e5639e889cca2c045fd79ac9"),
}

sys.path.insert(0, str(AB))
import analyze  # noqa: E402  (unchanged v0.2 code)

_real_digest = analyze.digest


def digest(path):
    h = _real_digest(path)
    expected = REDACTED.get(Path(path).resolve())
    if expected and h == expected[0]:
        return expected[1]
    return h


analyze.digest = digest
result = analyze.analyze()
published = json.loads((AB / "analysis.json").read_text())
assert json.loads(json.dumps(result)) == published, "regenerated statistics differ from analysis.json"
print("v0.2 action-budget: hashes verified (model.json via its published redacted hash), "
      "all 60 trajectories replayed, statistics equal analysis.json.")
