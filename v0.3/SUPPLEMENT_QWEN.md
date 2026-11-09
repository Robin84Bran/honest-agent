# Deviation record: Qwen held-out supplement

Written 9 Nov 2026, ~16:20 HKT, **before** any supplement trial was run. Robin approved the supplement in chat ("install the Qwen … and finish the task end to end") on 9 Nov 2026.

## Why

In the pre-registered held-out series, all 60 Qwen trajectories failed at their first call. The cause was that `qwen2.5:1.5b` was not installed in Ollama (HTTP 404, "model not found"). The frozen runner writes a trial file even when the actor never starts, and trial files are never overwritten, so those 60 files stay as they are in `results/heldout/qwen/`. The frozen analysis already excludes them, because it requires `actor_started`.

This is an operational failure, not an outcome-driven one: no Qwen behaviour was ever observed. The supplement fills the missing reference arm.

## What is identical to the pre-registered held-out Qwen arm

- **Code:** the trial is run by `run_v03.run_series` and `run_v03.trial`, unchanged. The run re-verifies the hashes of all 7 frozen files against `freeze.json` and stops if any differ.
- **Task:** the `sharing` family from `tasks.json`.
- **Design:** conditions granted, pending and denied; seeds 0–19; 60 trajectories.
- **Actor:** `qwen2.5:1.5b`, digest `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`, which is the same digest recorded for v0.2 in `../action-budget/runs/preregistration.json`. The 0.2 generation settings come from the frozen adapter: temperature 0.6, top_k 16, num_predict 192, JSON format, trajectory seed.
- **Monitors:** claude and gpt, both views, the same subscription CLIs at medium effort.
- **Budget:** the same append-only `results/spend-ledger.jsonl` and the same 200 USD cap for the whole task.

## What differs

| Item | Pre-registered | Supplement |
|---|---|---|
| Results folder | `results/heldout/qwen/` (failed files kept) | `results/heldout_qwen_supplement/qwen/` |
| Ollama server | 127.0.0.1:11434, empty store | 127.0.0.1:11435, store at `Honest_Agent/models/ollama` |
| Timing | during the main run, 13:01 HKT | after the frontier held-out results were viewed (~16:20 HKT) |
| Driver | `run_all.command` → `run_v03.py run --series heldout` | `supplement_qwen.py` (new, not frozen) |

The driver changes only two things, both in memory: it adds the series name to the loaded config, and it rewrites the Ollama URL port from 11434 to 11435. No frozen file is edited.

## Analysis plan, declared before running

1. `python3 analyze_v03.py heldout_qwen_supplement`. This is the frozen script, unchanged, and writes `results/analysis-heldout_qwen_supplement.{json,md}`.
2. A combined held-out table (frontier held-out plus this supplement), computed with the frozen `analyze_v03.analyse()` on the union of usable rows. It will be labelled **post hoc / deviation**.
3. Whatever happens is reported, including failures. The supplement is run once. If calls fail, they stay failed: no reruns, no seed changes, no prompt or setting changes.

Expected cost is about 18 USD (60 trajectories × ~0.30 USD of monitor calls; the Qwen actor is free). The ledger stood at 139.95 USD before the supplement.

## How to read it

The supplement Qwen arm is a labelled deviation, not part of the pre-registered result. It ran about three hours later than the frontier held-out arm, on a fresh Ollama server, after the frontier held-out results had been viewed. The Qwen actor's own behaviour could not have been steered by those results, because the prompts, task and settings are frozen. The monitors are the same models, called fresh and stateless.
