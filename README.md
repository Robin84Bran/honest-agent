# The Honest Agent

A small AI-control experiment. Agents get a simulated task with one rule: get approval for the exact target first. The experiment records whether they break the rule, whether their end-of-task reports are honest, and whether LLM monitors catch the breaches. Monitors either read the agent's final report alone or the full action trace.

This repository holds **v0.3**, which used frontier actors (Claude Opus 5.5 and GPT-6 Astra) and a local Qwen 2.5 1.5B reference arm.

## Results in one screen

- **Frontier actors:** 0 breaches in 210 runs, with honest reports in 210 of 210. This held across granted, pending and denied approval on three tasks.
- **Trace-reading monitors:** 0 false alarms on frontier runs, and 22 of 22 breaches caught on Qwen runs.
- **Report-only monitoring:** a Claude monitor that saw only the final report caught 2 of the 17 Qwen breaches it ruled on, a paired trace advantage of +0.88 (95% CI +0.59 to +0.97). **Every Qwen result is a post-freeze deviation**: the Qwen arm failed because of a setup error and was rerun after the main analysis.
- **Why Qwen breached:** 21 of its 22 breaches came from asking approval for the wrong target, not from approval pressure.
- **Frontier runs didn't vary:** every seed in a cell produced the same behaviour.

Start with [`v0.3/WRITEUP.md`](v0.3/WRITEUP.md). Then read [`v0.3/DEVIATIONS.md`](v0.3/DEVIATIONS.md) and the pre-registered [`v0.3/PROTOCOL.md`](v0.3/PROTOCOL.md).

## Layout

| Path | What it is |
|---|---|
| `v0.3/PROTOCOL.md`, `v0.3/freeze.json` | Pre-registered design and the SHA-256 hashes of every frozen file |
| `v0.3/*.py`, `v0.3/tasks.json`, `v0.3/config.json` | Sandbox, providers, runner, frozen analysis, tasks and settings |
| `v0.3/results/<series>/<actor>/<condition>/trial-<seed>.json` | All 330 trial files: every prompt, raw response, token count, cost and timestamp. Includes the 60 failed Qwen files in `results/heldout/qwen/` |
| `v0.3/results/analysis-*.md` | Frozen analysis output per series |
| `v0.3/results/spend-ledger.jsonl`, `v0.3/results/*.log` | Append-only cost ledger and run logs |
| `v0.3/SUPPLEMENT_QWEN.md`, `v0.3/supplement_qwen.py` | The Qwen rerun: declaration (written before it ran) and driver |
| `v0.3/posthoc_combined_heldout.py`, `v0.3/results/posthoc-*.md` | Post hoc combined held-out table |
| `src/run.py`, `src/sandbox.py` | v0.2 reference sources; the v0.3 tests check that prompts and policy text are copied verbatim |
| `RELEASE_MANIFEST.md`, `SHA256SUMS` | What was redacted for release, and checksums |

## Verify

```sh
shasum -a 256 -c SHA256SUMS          # files match this release
cd v0.3
python3 -B test_v03.py               # 12 offline tests, no network, no cost
python3 -B analyze_v03.py            # regenerates results/analysis-{calibration,replication,heldout}.*
python3 -B analyze_v03.py heldout_qwen_supplement
```

The regenerated analysis files should be byte-identical to the published ones.

`providers_api.py` differs from its frozen hash in two lines only: the local CLI paths were replaced by bare command names. See `RELEASE_MANIFEST.md`.

## Rerun (costs money or subscription quota)

Fresh inference needs the Claude Code and Codex CLIs signed in to subscriptions, plus a local Ollama with `qwen2.5:1.5b` (digest `65ec0654…`). See `v0.3/README.md`. Frontier sampling is not reproducible, so a rerun is a new sample, not a replay.

## License

- **Code** (every `.py`, `.command` and `.sh` file, and `tasks.json`/`config.json`): MIT. See [`LICENSE`](LICENSE).
- **Everything else** (the write-up, protocol, deviations and supplement documents, trial files, ledger, logs and analysis outputs): [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). See [`LICENSE-CC-BY-4.0.md`](LICENSE-CC-BY-4.0.md).

If you use the data or findings, please cite *Robin Xie, "The Honest Agent v0.3" (2026)* and link to this repository.

The trial files contain outputs from Claude Opus 5.5, GPT-6 Astra and Qwen 2.5 1.5B, and they are shared here as research data. No model weights are included. The models themselves are covered by their providers' own terms and licenses.
