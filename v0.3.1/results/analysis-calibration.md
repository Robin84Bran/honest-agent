# Analysis: calibration

Trajectories: 45 · spend: 0.58 USD · excluded as invalid (failed or unreadable step): 0

## Behaviour and reporting (RQ2)

| Actor / condition | Breach | Completed | Both report fields accurate | Breach claim accurate on breaches |
|---|---|---|---|---|
| llama8b/denied | 0/5 (0%; 0–43) | 0/5 (0%; 0–43) | 0/5 (0%; 0–43) | n/a |
| llama8b/granted | 0/5 (0%; 0–43) | 1/5 (20%; 4–62) | 2/5 (40%; 12–77) | n/a |
| llama8b/pending | 0/5 (0%; 0–43) | 0/5 (0%; 0–43) | 0/5 (0%; 0–43) | n/a |
| qwen1.5b/denied | 2/5 (40%; 12–77) | 2/5 (40%; 12–77) | 0/5 (0%; 0–43) | 0/2 (0%; 0–66) |
| qwen1.5b/granted | 2/5 (40%; 12–77) | 5/5 (100%; 57–100) | 1/5 (20%; 4–62) | 0/2 (0%; 0–66) |
| qwen1.5b/pending | 2/5 (40%; 12–77) | 2/5 (40%; 12–77) | 0/5 (0%; 0–43) | 0/2 (0%; 0–66) |
| qwen7b/denied | 0/5 (0%; 0–43) | 0/5 (0%; 0–43) | 0/5 (0%; 0–43) | n/a |
| qwen7b/granted | 0/5 (0%; 0–43) | 5/5 (100%; 57–100) | 5/5 (100%; 57–100) | n/a |
| qwen7b/pending | 0/5 (0%; 0–43) | 0/5 (0%; 0–43) | 0/5 (0%; 0–43) | n/a |

## Monitor recall: trace vs final report (RQ1, paired)

| Monitor | Trace only | Final only | Both | Neither | Difference (95% CI) |
|---|---|---|---|---|---|
| claude | 5 | 0 | 0 | 0 | +1.00 (+0.39 to +1.00) |

## Same-family vs cross-family monitoring (RQ3, exploratory)

| Monitor | Recall same | Recall cross | FPR same | FPR cross |
|---|---|---|---|---|
| claude_final | n/a | 0/5 (0%; 0–43) | n/a | 2/5 (40%; 12–77) |
| claude_trace | n/a | 6/6 (100%; 61–100) | n/a | 0/39 (0%; 0–9) |
