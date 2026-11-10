# Does the model wait when approval becomes affordable?

**Giving the two focal actors enough actions to wait for permission produced no observed decline in breaches across the four planned contrasts.** Qwen 7B breached in all 30 pairs on both sides of each threshold. For Llama 8B the medium-delay breach count rose from 8/30 to 20/30, while the slow-delay count moved from 24/30 to 26/30. Extra actions made waiting possible and also gave each actor more chances to execute. These results describe the total effect of the visible budget in this simulator.

The same batch-release and snapshot-export fixtures were paired by actor, framing and seed. Lawful completion first becomes possible at 6 actions for medium delay and 10 for slow delay. The table reports longer minus shorter breach rates among pairs with known outcomes.

| Actor | Delay | Caps | Pairs used / planned | Breach at longer only | Breach at shorter only | Difference in points [95% CI] | Leave-one-seed-out range, pp |
|---|---|---|---|---|---|---|---|
| qwen7b | medium | 8-4 | 30/30 | 0 | 0 | 0.0 [-11.4, 11.4] | 0.0 to 0.0 |
| qwen7b | slow | 12-8 | 30/30 | 0 | 0 | 0.0 [-11.4, 11.4] | 0.0 to 0.0 |
| llama8b | medium | 8-4 | 30/30 | 16 | 4 | 40.0 [12.2, 60.7] | 37.5 to 50.0 |
| llama8b | slow | 12-8 | 30/30 | 5 | 3 | 6.7 [-12.3, 25.4] | -8.3 to 12.5 |
| qwen1.5b | medium | 8-4 | 30/30 | 15 | 0 | 50.0 [29.7, 66.8] | 41.7 to 58.3 |
| qwen1.5b | slow | 12-8 | 30/30 | 0 | 1 | -3.3 [-16.7, 8.3] | -4.2 to 0.0 |

A positive difference means breaches increased for the longer budget. The direction predicted before inference was negative in each of the four focal contrasts. Family and framing cell sizes are small, with five paired seeds.

| Actor | Known / attempted | Breaches | Lawful / all completions | Stops / cap reached | Last-step completions | Admitted / denied / missing on breaches |
|---|---|---|---|---|---|---|
| qwen7b | 360/360 | 229/360 | 85 / 314 | 46 / 0 | 95 | 195 / 34 / 0 |
| llama8b | 360/360 | 157/360 | 108 / 265 | 0 / 95 | 76 | 152 / 5 / 0 |
| qwen1.5b | 360/360 | 284/360 | 13 / 297 | 0 / 63 | 65 | 0 / 284 / 0 |

## Pressure wording and self-reporting

| Actor | Urgency minus neutral, pp [95% CI] | Prior work minus neutral, pp [95% CI] | Both claims accurate on breaches | Both accurate on compliant runs |
|---|---|---|---|---|
| qwen7b | -3.3 [-7.3, 0.6] | -3.3 [-7.3, 0.6] | 101/229 | 85/131 |
| llama8b | 10.8 [2.5, 18.8] | 7.5 [-0.9, 15.7] | 152/157 | 42/203 |
| qwen1.5b | 10.0 [4.7, 16.1] | -13.3 [-22.4, -4.0] | 0/284 | 13/76 |

Qwen 7B and Llama 8B sometimes executed even after explicit denial, in 39 and 60 trials respectively across all budgets and framings. Qwen 1.5B denied all 284 of its breaches. Of the larger actors, Llama admitted 152/157 and Qwen 7B admitted 195/229. The urgency sentence increased Llama’s breach rate by 10.8 points versus neutral; the prior-work sentence increased it by 7.5 points. The corresponding Qwen 7B estimates were both −3.3 points.

## Interpretation and reproduction

Per-cell rates, completion and compliance claim accuracy, omissions, missing outcomes, timing of commits, reasons for stopping, and paired contrasts are in results/analysis.json. Intervals for rates use Wilson; paired contrasts use Newcombe. Compare both families, feasibility and missingness before attributing differences to the deadline. Observable choices cannot establish motive. Prior work is a framing sentence. The two simulated operation types, five seeds and three models bound these results.

The original interface stopped on the practice fixture when Qwen copied an action placeholder. Version 0.2.1 clarified the output format and was privately timestamped before a fresh practice run. No main trial was run using the first interface. The planned main sample ran locally with zero paid calls. Raw practice and main trials retain receipts, model text, tokens and timings. Rebuild with python3 -B study.py analysis.
