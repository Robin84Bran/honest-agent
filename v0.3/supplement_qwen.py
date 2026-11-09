"""Qwen held-out supplement (labelled deviation; see SUPPLEMENT_QWEN.md).

Runs the frozen run_v03.run_series unchanged for one extra series, `heldout_qwen_supplement`
(sharing family, qwen actor, seeds 0-19, all three conditions), against a project-local Ollama
server on 127.0.0.1:11435. Only two in-memory changes: the series entry is added to the loaded
config, and the Ollama URL port is rewritten 11434 -> 11435. No frozen file is edited; run_series
re-verifies freeze.json hashes before running and never overwrites a trial file.

Usage: python3 supplement_qwen.py [--workers 3]
"""
import argparse
import json
import sys
import urllib.request

import providers_api
import run_v03

SERIES = "heldout_qwen_supplement"
PORT_FROM, PORT_TO = "127.0.0.1:11434", "127.0.0.1:11435"
EXPECTED_DIGEST = "65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b"  # v0.2 qwen2.5:1.5b

_orig_post = providers_api._post
_orig_load = run_v03.load


def _post(url, headers, body, timeout):
    return _orig_post(url.replace(PORT_FROM, PORT_TO), headers, body, timeout)


def _load(base):
    cfg, tasks = _orig_load(base)
    held = cfg["series"]["heldout"]
    cfg["series"][SERIES] = {"family": held["family"], "actors": ["qwen"], "seeds": list(held["seeds"])}
    return cfg, tasks


def check_model():
    with urllib.request.urlopen("http://%s/api/tags" % PORT_TO, timeout=10) as r:
        models = json.loads(r.read().decode())["models"]
    found = {m["name"]: m["digest"] for m in models}
    if found.get("qwen2.5:1.5b") != EXPECTED_DIGEST:
        raise SystemExit("qwen2.5:1.5b with digest %s not found on %s: %s" % (EXPECTED_DIGEST, PORT_TO, found))


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    a = p.parse_args(argv)
    check_model()
    providers_api._post = _post
    run_v03.load = _load
    return run_v03.run_series(SERIES, workers=a.workers)


if __name__ == "__main__":
    sys.exit(main())
