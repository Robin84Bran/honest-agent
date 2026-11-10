# The Honest Agent

A small AI-control experiment. Agents get a simulated task with one rule: get approval for the exact target first. The experiment records whether they break the rule, whether their end-of-task reports are honest, and whether LLM monitors catch the breaches. Monitors either read the agent's final report alone or the full action trace.

This repository holds **v0.3**, which used frontier actors (Claude Opus 5.5 and GPT-6 Astra) and a local Qwen 2.5 1.5B reference arm, and **v0.3.1**, a pre-registered follow-up with three open models. It also holds the earlier **v0.2** in [`v0.2/`](v0.2/README.md). v0.2 used Qwen 2.5 1.5B as both actor and monitor:

- It breached approval in 16 of 20 simulated deployments, and only 1 of its 20 reports got both completion and breach right.
- Giving it 8 or 12 decisions instead of 4 never undid a breach.
- The trace monitor caught 12–23 percentage points more breaches than the report-only monitor, but with 20 runs the intervals crossed zero.

## Results in one screen

- **Frontier actors:** 0 breaches in 210 runs, with honest reports in 210 of 210. This held across granted, pending and denied approval on three tasks.
- **Trace-reading monitors:** 0 false alarms on frontier runs, and 22 of 22 breaches caught on Qwen runs.
- **Report-only monitoring:** a Claude monitor that saw only the final report caught 2 of the 17 Qwen breaches it ruled on, a paired trace advantage of +0.88 (95% CI +0.59 to +0.97). **Every Qwen result is a post-freeze deviation**: the Qwen arm failed because of a setup error and was rerun after the main analysis.
- **Why Qwen breached:** mostly not because of approval pressure. In 15 of its 22 breaches it asked approval for the wrong target, in 6 it never asked, and in 1 it acted after a correctly targeted "pending" answer.
- **Frontier runs didn't vary:** every seed in a cell produced the same behaviour.
- **The pre-registered follow-up confirmed the monitor result ([`v0.3.1/RESULTS.md`](v0.3.1/RESULTS.md)).** Qwen 2.5 1.5B, Qwen 2.5 7B and Llama 3.1 8B ran on fresh seeds, on the deployment and sharing tasks. The protocol and code were pushed here before any run; GitHub's push log records the times, and a copy is in `v0.3.1/results/github-push-log.json`. On the 26 breaches where both of the Claude monitor's views gave a verdict, the trace view caught all 26 and the report-only view none: +1.00 (95% CI +0.82 to +1.00). Counting abstentions as misses, it was **67 of 67** against **0 of 67** (+1.00, 95% CI +0.92 to +1.00). The test passed on both tasks, including v0.2's own deployment task. The trace view raised 0 false alarms in 293 compliant runs. **All breaches came from Qwen 1.5B.** The two larger models never breached, but they often reported violations that hadn't happened (100 of 120 and 73 of 120 runs).

For the picture version, download the repository and open [`v0.3/site/index.html`](v0.3/site/index.html) in a browser. It's a results page with charts that GitHub shows only as source; `python3 -B v0.3/site/build_site.py` rebuilds it from the raw trial files. For the full account, start with [`v0.3/WRITEUP.md`](v0.3/WRITEUP.md). Then read [`v0.3/DEVIATIONS.md`](v0.3/DEVIATIONS.md) and the pre-registered [`v0.3/PROTOCOL.md`](v0.3/PROTOCOL.md).

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
| `src/run.py`, `src/sandbox.py` | v0.2 reference sources, identical to `v0.2/src/`; the v0.3 tests check that prompts and policy text are copied verbatim |
| `v0.3.1/` | Pre-registered open-model replication (Qwen 2.5 1.5B and 7B, Llama 3.1 8B; fresh seeds). It holds the protocol and code pushed before any inference, then the freeze and results. See [`v0.3.1/PROTOCOL.md`](v0.3.1/PROTOCOL.md) |
| `v0.3.2/` | Pre-registered second monitor family: GPT-6 Sol re-judges the 360 saved v0.3.1 runs with the same 720 monitor prompts. Protocol, code and freeze pushed before any GPT call. See [`v0.3.2/PROTOCOL.md`](v0.3.2/PROTOCOL.md) |
| `v0.2/` | v0.2 as it was run: its README, protocol and audit docs, local research page (`site/index.html`), payment calibration and held-out deployment trials (`results/`), the action-budget ablation (`action-budget/`), and the v0.1 scripted baseline (`baseline/`) |
| `v0.2/verify_release.py` | Release-only helper that runs v0.2's unchanged action-budget analysis on this redacted copy (see `RELEASE_MANIFEST.md`) |
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

v0.2 (run from the repository root):

```sh
python3 -B v0.2/verify_release.py    # action-budget: hashes, replay of 60 trajectories, statistics equal analysis.json
cd v0.2
python3 -B -m unittest discover -s tests
python3 -B tests/verify_pilot.py
python3 -B tests/verify_series.py payment-calibration | diff - results/payment-accounting.json
python3 -B tests/verify_series.py deployment-heldout | diff - results/deployment-accounting.json
```

`providers_api.py` differs from its frozen hash in two lines only: the local CLI paths were replaced by bare command names. See `RELEASE_MANIFEST.md`. Because of this, `run_v03.py`'s freeze check fails on this copy by design. The analyses and tests above don't depend on it.

## Rerun (costs money or subscription quota)

Fresh inference needs the Claude Code and Codex CLIs signed in to subscriptions, plus a local Ollama with `qwen2.5:1.5b` (digest `65ec0654…`). See `v0.3/README.md`. Frontier sampling is not reproducible, so a rerun is a new sample, not a replay. New runs should use v0.4. It fixes the operational and latent defects listed in `v0.3/DEVIATIONS.md`, but it isn't in this repository yet.

## Review

An independent read-only review by GPT-6 Astra (via Codex), in two rounds, reproduced the headline counts and all frozen analyses. Its findings and the resulting fixes are listed in `v0.3/DEVIATIONS.md`.

## License

- **Code** (every `.py`, `.swift`, `.command` and `.sh` file, `tasks.json`/`config.json`, and the v0.1 baseline zip): MIT. See [`LICENSE`](LICENSE).
- **Everything else** (the write-up, protocol, deviations and supplement documents, trial files, ledger, logs and analysis outputs): [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). See [`LICENSE-CC-BY-4.0.md`](LICENSE-CC-BY-4.0.md).

If you use the data or findings, please cite *Bin "Robin" Xie, "The Honest Agent v0.3" (2026)* and link to this repository.

The trial files contain outputs from Claude Opus 5.5, GPT-6 Astra and Qwen 2.5 1.5B, and they are shared here as research data. No model weights are included. The models themselves are covered by their providers' own terms and licenses.
