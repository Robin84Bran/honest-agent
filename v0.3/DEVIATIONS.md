# Deviations, protocol inconsistencies and post hoc analyses

Protocol 0.3, recorded 9 Nov 2026. The frozen files listed in `freeze.json` are unchanged; their SHA-256 hashes were re-verified after every run.

## D1. Qwen held-out arm rerun after the freeze (deviation)

- **What happened.** In the pre-registered held-out series, `qwen2.5:1.5b` was not installed in Ollama. `run_all.command` printed a warning and continued. All 60 Qwen trajectories failed at their first call (HTTP 404, "model not found"), at about 13:01 HKT.
- **Why the failures are permanent.** The frozen runner writes a trial file even when the actor never starts, and trial files are never overwritten. The 60 files stay in `results/heldout/qwen/`, and the frozen analysis excludes them (`actor_started: false`).
- **What was done.** With Robin's approval, the model was installed into a project-local store. Its digest, `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`, is identical to v0.2's. The arm was then run once as a new series, `heldout_qwen_supplement` (16:17–16:30 HKT).
  - The run used the frozen `run_v03.run_series` and `trial` unchanged, via `supplement_qwen.py`.
  - The driver makes two in-memory changes only: it adds the series name, and it moves the Ollama port from 11434 to 11435.
  - `SUPPLEMENT_QWEN.md` was written before the run and declares the analysis. Its own "~16:20" timestamp is wrong; see D4.
- **Why it matters.** The supplement ran after the frontier held-out results had been viewed. Every Qwen result, including the only RQ1 figure, is a deviation, not a pre-registered result.
- **Outcome.** 60/60 trajectories started, with 0 provider or parse errors. Analyses:
  - `results/analysis-heldout_qwen_supplement.md` (frozen script, unchanged)
  - `results/posthoc-heldout-combined.md` (frozen functions applied to the union; post hoc)

## D2. Retry schedule: protocol text is inconsistent (no effect on results)

PROTOCOL.md says two different things:

- **§6:** "Retries wait 10, 60 and 180 seconds."
- **§10:** "up to two retries (5 s, 20 s)."

The code follows §6 (`RETRY_WAITS = (0, 10, 60, 180)`). No call in any series needed a retry: every call had `attempts == 1`. So the inconsistency did not affect any result.

## D3. GPT model ID in trial files comes from the config (verified post hoc)

- **The problem.** The Codex CLI adapter (`providers_api.CodexCLI`) sets `returned_model` from `config.json` instead of reading it from Codex's output. So the `gpt-6-astra` in trial files and in `freeze.json` echoes the configuration and is not independent evidence. The Claude and Qwen IDs do come from the providers' own responses.
- **Post hoc check.** Codex writes a local session log for every `codex exec` run, and each log records the model and reasoning effort of the turn. I counted the experiment's sessions in the run window (9 Nov 12:22–16:31 HKT; originator `codex_exec`; temporary working directory). There are **1,067 sessions, all `gpt-6-astra` at `medium` effort**, exactly matching the 1,067 GPT rows in `results/spend-ledger.jsonl`.
- **Limit of the check.** The session log is Codex's client-side record of the model it requested. It is not a model ID returned by the server.
- **Not verifiable from this repository.** The session logs stay private because they contain local paths and unrelated work, so this is the author's own check. v0.4 records the session-log model with every call.

## D4. Timestamp in `SUPPLEMENT_QWEN.md` is wrong (record correction)

`SUPPLEMENT_QWEN.md` says it was "Written 9 Nov 2026, ~16:20 HKT, **before** any supplement trial was run". The ordering is right, but the time is a wrong estimate. Local file metadata (creation time, never modified afterwards) gives:

| File | Created (HKT) |
|---|---|
| `SUPPLEMENT_QWEN.md` | 16:16:51 |
| `supplement_qwen.py` | 16:16:52 |
| `results/supplement_qwen-20261109-161727.log` (run start) | 16:17:27 |

So the declaration was written 36 seconds before the run started. That evidence comes from the author's file system, which outside readers can't inspect; git history starts later. `SUPPLEMENT_QWEN.md` is left unedited, so that it stays the record as written.

## Latent defects found in review (no effect on v0.3 results)

These are bugs in frozen code. Neither one affected any v0.3 trajectory. Both are fixed in v0.4.

- **L1. The budget cap was an estimate, not a hard limit.** `Budget.reserve` (`run_v03.py`) checks the balance but doesn't hold money aside, so parallel workers can all pass the same check before any of them is charged. Its worst-case estimate counts the visible prompt only, not the ~14K hidden Codex harness tokens. Neither CLI adapter can cap output length. Realised spend was 158.33 USD against the 200 USD cap.
- **L2. A failed step after the actor started could be scored as compliant.** In `trial` (`run_v03.py`), if an action call fails or can't be parsed after the intent call succeeded, the loop stops, a report is still requested, and the trajectory is analysed as a normal one: no breach, and possibly an "accurate" report. I checked all 270 started trajectories: none has a failed call (every actor and report call has a raw response), none has an unparseable action, and none has an unparseable report.

## Independent review

After the run, GPT-6 Astra reviewed a fresh clone of the release through Codex. The review ran in a read-only sandbox with web, plugins and computer use switched off, in two rounds: a review, then one follow-up on Claude's verdicts. It reproduced the headline counts and all four frozen analyses, and it found the following:

- L1, L2 and D4 above.
- The fact that D3's check can't be verified from this repository.
- Wording that claimed more than the evidence shows. These were corrected in `WRITEUP.md` and the repository `README.md`:
  - same- and cross-family false-alarm rates;
  - the breakdown of Qwen's breaches (15 wrong-target, 6 no request, 1 after a correct pending request);
  - "confusion, not intent", which the data can't establish;
  - "97% harness": GPT calls were 97% of spend, the harness about 94%;
  - "the hashes still match", which is false for the public copy;
  - v0.2 data and v0.4 code, which weren't in this repository at the time of the review. v0.2 was added afterwards, in `../v0.2/`.

No reported number changed.

## Release note: redactions in the public copy (not a deviation)

The public copy is redacted so it does not reveal local paths. Two classes of file changed: four documentation and log files that are not frozen, and one frozen file. The private originals are unchanged, and `RELEASE_MANIFEST.md` lists every redaction with the original and redacted SHA-256.

- **Not frozen:** `README.md` and `results/ollama.log` have their local paths redacted. `HANDOFF.md` (an internal agent prompt) and `results/EXECUTIVE_SUMMARY.md` (an internal briefing) are left out.
- **Frozen:** in `providers_api.py`, the two lines holding absolute local CLI paths (`CODEX = …`, `CLAUDE = …`) are replaced by bare command names. Nothing else in the file changes, so its hash in the public copy differs from `freeze.json` for that reason alone. As a result, `run_v03.py`'s freeze check fails on the public copy by design. The original lines held machine-specific paths, so restoring them elsewhere wouldn't reproduce the hash either. The historical freeze is left as it is, and reruns should use the separately versioned v0.4 code.

## Things that were pre-registered and happened as planned (not deviations)

- **Sample-size fallback.** The post-calibration projection was 197.85 USD, above 90% of the 200 USD cap. Replication therefore ran seeds 0–9, so the pre-registered total became 270 trajectories, not 330.
- **Timing of the freeze.** `run_all.command` created `freeze.json` automatically after the projection, before replication or held-out started.

## Post hoc analyses (not in `analyze_v03.py`)

Every analysis below is descriptive and was chosen after seeing the data:

1. Breach and false-positive rates pooled across series.
2. Resource use per role (calls, USD, latency, tokens).
3. Distinct action sequences per cell: frontier cells had 1 each; Qwen cells had 8–10.
4. Frontier action patterns by condition (number of approval requests before stopping).
5. How Qwen's breaches happened (wrong-target request, no request, or correct request then breach).
6. Breakdown of monitor abstentions in the final-report view, by condition and by whether the report claimed completion.
7. The combined held-out table (`posthoc-heldout-combined.md`), declared in `SUPPLEMENT_QWEN.md` before the supplement ran, but still post hoc relative to the protocol.
8. The Codex session-log check in D3.
9. The scan of all started trajectories for failed or unparseable calls in L2.
