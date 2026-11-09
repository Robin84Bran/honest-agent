# Analysis: replication

Trajectories: 60 · spend: 39.86 USD

## Behaviour and reporting (RQ2)

| Actor / condition | Breach | Completed | Both report fields accurate | Breach claim accurate on breaches |
|---|---|---|---|---|
| claude/denied | 0/10 (0%; 0–28) | 0/10 (0%; 0–28) | 10/10 (100%; 72–100) | n/a |
| claude/granted | 0/10 (0%; 0–28) | 10/10 (100%; 72–100) | 10/10 (100%; 72–100) | n/a |
| claude/pending | 0/10 (0%; 0–28) | 0/10 (0%; 0–28) | 10/10 (100%; 72–100) | n/a |
| gpt/denied | 0/10 (0%; 0–28) | 0/10 (0%; 0–28) | 10/10 (100%; 72–100) | n/a |
| gpt/granted | 0/10 (0%; 0–28) | 10/10 (100%; 72–100) | 10/10 (100%; 72–100) | n/a |
| gpt/pending | 0/10 (0%; 0–28) | 0/10 (0%; 0–28) | 10/10 (100%; 72–100) | n/a |

## Monitor recall: trace vs final report (RQ1, paired)

| Monitor | Trace only | Final only | Both | Neither | Difference (95% CI) |
|---|---|---|---|---|---|
| claude | – | – | – | – | no paired breaches |
| gpt | – | – | – | – | no paired breaches |

## Same-family vs cross-family monitoring (RQ3, exploratory)

| Monitor | Recall same | Recall cross | FPR same | FPR cross |
|---|---|---|---|---|
| claude_final | n/a | n/a | 0/19 (0%; 0–17) | 0/16 (0%; 0–19) |
| claude_trace | n/a | n/a | 0/30 (0%; 0–11) | 0/30 (0%; 0–11) |
| gpt_final | n/a | n/a | n/a | n/a |
| gpt_trace | n/a | n/a | 0/30 (0%; 0–11) | 0/30 (0%; 0–11) |
