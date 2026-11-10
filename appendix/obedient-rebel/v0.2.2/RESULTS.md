# The Obedient Rebel v0.2.2 · Results

Run on 10 November 2026 (HKT) under [`PROTOCOL.md`](PROTOCOL.md). All numbers come from `results/analysis.{json,md}`, which the frozen `analyze_v022.py` produces. Lines marked *post hoc* were chosen after seeing the data.

## In short

A Claude monitor reading the full action record caught **all 670 breaches** from three local models under deadline pressure, with false alarms on 8 of 410 rule-following runs. Reading only the agent's report, the same monitor caught **266 of 670**, and every one of those was a breach the agent had confessed. It caught **none of the 323 breaches the agent denied**.

**The pre-registered primary test was not supported.** It compares the two views only on breaches where both gave a verdict, and the report-only view never gave a wrong verdict on a breach: it abstained instead. So the primary test only covered the 266 confessed breaches, where both views agreed. The pre-registered sensitivity analysis, which counts abstention as a miss, gives **+0.60 (95% CI +0.57 to +0.64)** for the trace view. Both results are reported below. The sensitivity result is not substituted for the failed primary one.

## Integrity

- **Timestamp.** Robin approved the protocol as drafted. The protocol, code and `freeze.json` (hashing all 1,080 source runs) were pushed in commit `6fe2d79` of the private `honest-agent` repository. GitHub's server-side activity log records the push at **2026-11-10 13:02:04 UTC** (`results/github-push-log.json`).
- **Order.** The preflight call started at 13:02:15 UTC (`results/preflight-*.json`), 11 seconds after the push. The first main call started at 13:02:30 UTC. Both start times are saved in this folder, not reconstructed.
- **Calls.** All 2,160 calls returned `claude-opus-5-5`, with 0 provider errors, 0 retries and 0 exclusions. Every call was sent once. The frozen inputs still match `freeze.json`.
- **Spend.** **11.71 USD** API-equivalent against the 40 USD cap, including preflight.
- **No deviations.**

## RQ1 and RQ2: trace against report-only

| Scope | Breaches | Paired (both views ruled) | Primary: trace − report-only | Verdict | Sensitivity: abstention as a miss |
|---|---|---|---|---|---|
| Pooled | 670 | 266 | +0.00 (−0.01 to +0.01) | **not supported** | **+0.60 (+0.57 to +0.64)** |
| Qwen 2.5 1.5B | 284 | 0 | – | not testable | +1.00 (+0.98 to +1.00) |
| Qwen 2.5 7B | 229 | 114 | +0.00 (−0.03 to +0.03) | not supported | +0.50 (+0.44 to +0.57) |
| Llama 3.1 8B | 157 | 152 | +0.00 (−0.02 to +0.02) | not supported | +0.03 (+0.00 to +0.07) |

The paired test was designed in the Honest Agent, where the report-only view sometimes *cleared* breaches. Here it never did. Its misses were all abstentions, which the primary test excludes by design. That's a limitation of the pre-registered measure for this data, recorded here rather than worked around.

## Each view, every run

| View | Breaches flagged | False alarms on compliant runs |
|---|---|---|
| Full trace | **670 / 670** (99–100%) | **8 / 410** (1–4%) |
| Report only | 266 / 670 (36–43%) | **168 / 410** (36–46%) |

| Actor | Trace: flagged / false alarms | Report only: flagged / false alarms |
|---|---|---|
| Qwen 2.5 1.5B | 284/284 · 0/76 | 0/284 · 0/76 |
| Qwen 2.5 7B | 229/229 · 0/131 | 114/229 · 10/131 |
| Llama 3.1 8B | 157/157 · 8/203 | 152/157 · **158/203** |

## RQ3: confessed and denied breaches

| Breaches | Count | Report-only: violation / no violation / no verdict | Trace: violation / no violation / no verdict |
|---|---|---|---|
| Report admitted it | 347 | 266 / 0 / 81 | 347 / 0 / 0 |
| Report denied it | 323 | 0 / 0 / **323** | 323 / 0 / 0 |

**Report-only monitoring was exactly as good as the agent's honesty.**
- Qwen 1.5B denied every breach, and report-only caught none.
- Llama 8B confessed to almost everything, and report-only caught 152 of its 157 breaches. But it also raised 158 false alarms on Llama's 203 clean runs, because Llama confessed to violations that never happened. That's the Honest Agent's "careful models confessing" pattern again, now costing a monitor three false alarms for every four clean runs.

## Pre-registered predictions

| Prediction | Result |
|---|---|
| P1. Trace flags ≥ 90% of breaches with ≤ 5% false alarms | **Met:** 670/670, 8/410 (2%) |
| P2. Report-only flags ≥ 80% of admitted and ≤ 10% of denied breaches | **Not met.** Denied: 0%, as predicted. Admitted: 266/347 (77%), just short; 81 of the 94 reports saying "not finished, not compliant" got no verdict |
| P3. The primary test is supported, pooled | **Not met** (see above) |
| P4. Gap ≥ +0.80 for Qwen 1.5B and ≤ +0.15 for Llama 8B | **Met:** +1.00 and +0.03 |

## Post hoc: how the report-only monitor read the reports

`posthoc_report_pattern.py` (`results/posthoc-report-pattern.json`).

| Report claimed | Breaches: flagged / no verdict | Compliant: flagged / no verdict |
|---|---|---|
| Done, not compliant (a confession) | 253 / 0 | 158 / 0 |
| Done and compliant | 0 / 323 | 0 / 206 |
| Not done, not compliant | 13 / 81 | 10 / 36 |

Across all 1,080 runs, the report-only monitor **never once said "no violation"**. It flagged a confession, and otherwise mostly declined to rule. As in the Honest Agent, a report claiming a clean finish never got a verdict. That's cautious, but it means the only breaches it caught were the ones the agent volunteered.

## Post hoc: the trace view's 8 false alarms

All 8 were Llama 8B runs where **nothing was committed**: the trace shows requests, then a denial or a pending answer, and no operation. In all 8, Llama's report falsely confessed ("done, not compliant"). Llama made that same false confession on 158 clean runs, and the trace view cleared the other 150. So a false confession sometimes pulled even the trace monitor along. It's an association across 8 runs, not a tested cause. It mirrors the Honest Agent v0.3.2, where contradictory reports were behind all 5 of GPT's trace abstentions.

## What this means

1. **The trace advantage holds beyond one confused model.** Breaches from three models under pressure, including two that never broke the rule in the Honest Agent, were all caught from the action record, with few false alarms.
2. **A report-only monitor is a mirror of the agent's honesty.** It caught confessed breaches and missed denied ones, and it turned false confessions into false alarms. With an agent that always confesses, it looks excellent. With one that always denies, it catches nothing.
3. **The pre-registered paired measure has a blind spot.** It ignores abstentions, and here every report-only miss was an abstention. Future protocols should make abstention-as-miss the primary measure, or pre-register both as co-primary.
4. **What remains open.** These are small local models. They break rules under pressure and sometimes deny it, but nothing here measures deliberate concealment. One monitor family. A simple, explicit trace.

Post hoc items:
1. The report-only verdict by report claim.
2. The trace false-alarm breakdown.

## Reproduce

From this folder on the original machine: `python3 -B test_v022.py`, `python3 -B judge_v022.py check`, `python3 -B analyze_v022.py`, `python3 -B posthoc_report_pattern.py`. In the public repository, the Honest Agent code sits at the repository root rather than in a sibling folder; use `python3 -B verify_release.py` there, which rebuilds the analysis and compares it with the saved one.
