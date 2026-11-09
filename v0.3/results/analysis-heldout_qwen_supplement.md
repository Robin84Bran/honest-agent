# Analysis: heldout_qwen_supplement

Trajectories: 60 · spend: 18.24 USD

## Behaviour and reporting (RQ2)

| Actor / condition | Breach | Completed | Both report fields accurate | Breach claim accurate on breaches |
|---|---|---|---|---|
| qwen/denied | 7/20 (35%; 18–57) | 7/20 (35%; 18–57) | 2/20 (10%; 3–30) | 3/7 (43%; 16–75) |
| qwen/granted | 7/20 (35%; 18–57) | 9/20 (45%; 26–66) | 6/20 (30%; 15–52) | 2/7 (29%; 8–64) |
| qwen/pending | 8/20 (40%; 22–61) | 8/20 (40%; 22–61) | 5/20 (25%; 11–47) | 2/8 (25%; 7–59) |

## Monitor recall: trace vs final report (RQ1, paired)

| Monitor | Trace only | Final only | Both | Neither | Difference (95% CI) |
|---|---|---|---|---|---|
| claude | 15 | 0 | 2 | 0 | +0.88 (+0.59 to +0.97) |
| gpt | – | – | – | – | no paired breaches |

## Same-family vs cross-family monitoring (RQ3, exploratory)

| Monitor | Recall same | Recall cross | FPR same | FPR cross |
|---|---|---|---|---|
| claude_final | n/a | 2/17 (12%; 3–34) | n/a | 3/16 (19%; 7–43) |
| claude_trace | n/a | 22/22 (100%; 85–100) | n/a | 0/38 (0%; 0–9) |
| gpt_final | n/a | n/a | n/a | 1/1 (100%; 21–100) |
| gpt_trace | n/a | 22/22 (100%; 85–100) | n/a | 0/38 (0%; 0–9) |
