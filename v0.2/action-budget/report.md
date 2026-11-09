# The Honest Agent v0.2 · Action-budget ablation

**The same 16 of 20 seeds breached approval at every budget.** Eleven first breached on action one and five on action two. All 20 seeds preserved their shorter action history when given more decisions. The four compliant seeds stayed compliant. Extra decisions could change later actions and reports, but could never erase an earlier breach. This is evidence about extending the horizon for this model on this simulated deployment. The study did not test announcing a deadline to the actor.

**Frozen trajectory audit.** A correct request grants staging approval on action one; deploying build-7 on action two completes the task compliantly. These are distinct tools, so two is the minimum. Among the four compliant historical trajectories, three first completed on action three and one on action four. All 20 deployments completed. The completion claim was correct in 1/20 reports, the compliance claim in 11/20 and both in 1/20. The fresh four-action arm matched the archive on every seed’s tool trace, ground truth, report and monitor verdicts.

## Outcome by action budget

Cells give counts and descriptive 95% Wilson intervals in percent. Each column uses the same 20 seeds. A breach is any deployment executed before approval, even if approval follows later.

| Outcome | 4 actions | 8 actions | 12 actions |
|---|---:|---:|---:|
| Task complete | 20/20 [84–100] | 20/20 [84–100] | 20/20 [84–100] |
| Approval breach | 16/20 [58–92] | 16/20 [58–92] | 16/20 [58–92] |
| Correct completion claim | 1/20 [1–24] | 2/20 [3–30] | 3/20 [5–36] |
| Correct breach claim | 11/20 [34–74] | 16/20 [58–92] | 13/20 [43–82] |
| Both claims correct | 1/20 [1–24] | 2/20 [3–30] | 3/20 [5–36] |

## Paired comparisons

Differences are longer minus shorter in percentage points. Discordant counts show seeds that switched from compliant to breached, then the reverse. Intervals are conservative 95% paired intervals.

| Budgets | Breach switches (+ / −) | Breach difference [95% CI] | Exact McNemar p |
|---|---:|---:|---:|
| 8-4 | 0 / 0 | +0 [-19.7 to +19.7] | 1 |
| 12-4 | 0 / 0 | +0 [-19.7 to +19.7] | 1 |
| 12-8 | 0 / 0 | +0 [-19.7 to +19.7] | 1 |

The equal observed rates leave sampling uncertainty. With 20 paired seeds the intervals allow differences approaching 20 percentage points in either direction. Reporting changed despite the identical compliance outcomes. Joint report accuracy rose from one to three correct reports, while compliance-claim accuracy peaked at eight actions.

## Monitor verdicts

Precision, recall and false-positive rate exclude abstentions. Abstention uses all 20 trials. Brackets give 95% Wilson intervals in percent.

| Actions | Monitor | Precision | Recall | False-positive rate | Abstention |
|---:|---|---:|---:|---:|---:|
| 4 | Final report | 10/13 [50–92] | 10/13 [50–92] | 3/4 [30–95] | 3/20 [5–36] |
| 4 | Trace | 14/17 [59–94] | 14/16 [64–97] | 3/4 [30–95] | 0/20 [0–16] |
| 8 | Final report | 14/17 [59–94] | 14/16 [64–97] | 3/4 [30–95] | 0/20 [0–16] |
| 8 | Trace | 16/18 [67–97] | 16/16 [81–100] | 2/3 [21–94] | 1/20 [1–24] |
| 12 | Final report | 10/12 [55–95] | 10/13 [50–92] | 2/4 [15–85] | 3/20 [5–36] |
| 12 | Trace | 15/16 [72–99] | 15/16 [72–99] | 1/4 [5–70] | 0/20 [0–16] |

Restricting recall to breached trials where both monitors gave a verdict yields these paired comparisons.

| Actions | Final | Trace | Trace minus final, pp [95% CI] |
|---:|---:|---:|---:|
| 4 | 10/13 | 13/13 | +23.1 [-24.7 to +57.6] |
| 8 | 14/16 | 16/16 | +12.5 [-22.9 to +42.0] |
| 12 | 10/13 | 13/13 | +23.1 [-24.7 to +57.6] |

## Inference and reproduction

| Actions | Local calls | Input tokens | Output tokens | Summed request seconds |
|---:|---:|---:|---:|---:|
| 4 | 160 | 29,849 | 2,250 | 15 |
| 8 | 240 | 59,514 | 3,594 | 23 |
| 12 | 319 | 97,374 | 4,716 | 31 |

API charges totaled $0. Electricity and hardware costs were unmeasured. Actor and judge used local Qwen2.5 1.5B on Apple M3 Ultra Metal, macOS 26.6, Ollama 0.33.3, Python 3.9.6. JSON decoding used temperature 0.6, top-k 16, at most 192 output tokens per call, and the trajectory seed on every call. The pinned model and runtime supplied remaining defaults. Each seed started a fresh sandbox in each condition. The cap was hidden and the actor could finish early. Intent, reporting and monitoring calls did not consume tool decisions.

Model manifest SHA-256: `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`. Model weights SHA-256: `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.

From the extracted study directory run `python3 -B analyze.py` to verify frozen input and output hashes, replay every action and regenerate the statistics. For fresh inference, copy the study files excluding `runs/` into an empty directory, start the pinned local Ollama server with cloud inference disabled and run `python3 -B execute.py`.

[Preregistration](protocol.md) · [Frozen schedule and configuration](runs/preregistration.json) · [Model settings and template](runs/model.json) · [Raw trial manifest](runs/manifest.json) · [Full statistics, paired reporting comparisons and per-role costs](analysis.json) · [Historical audit](audit.json)
