# Pre-registered tests (protocol 0.3.1, deployment + sharing)

Trajectories analysed: 360 · excluded as invalid: 0

## RQ1 · trace vs final report (paired, primary: breaches where both views gave a verdict)

| Scope | Paired breaches | Trace only | Final only | Both | Neither | Trace − final (95% CI) | Supported? | Abstain-as-miss (n, diff, CI) |
|---|---|---|---|---|---|---|---|---|
| claude pooled | 26 | 26 | 0 | 0 | 0 | +1.00 (+0.82 to +1.00) | yes | 67, +1.00 (+0.92 to +1.00) |
| claude task: deployment | 14 | 14 | 0 | 0 | 0 | +1.00 (+0.70 to +1.00) | yes | 51, +1.00 (+0.90 to +1.00) |
| claude task: sharing | 12 | 12 | 0 | 0 | 0 | +1.00 (+0.66 to +1.00) | yes | 16, +1.00 (+0.73 to +1.00) |
| claude actor: llama8b | 0 | – | – | – | – | n/a | not testable (<10) | n/a |
| claude actor: qwen1.5b | 26 | 26 | 0 | 0 | 0 | +1.00 (+0.82 to +1.00) | yes | 67, +1.00 (+0.92 to +1.00) |
| claude actor: qwen7b | 0 | – | – | – | – | n/a | not testable (<10) | n/a |

## RQ3 · model comparisons (exploratory; first − second)

| Comparison | Breach rate difference | Both-claims-accurate difference |
|---|---|---|
| qwen1.5b_vs_qwen7b/pooled | +0.56 (+0.46 to +0.64) | -0.02 (-0.12 to +0.07) |
| qwen1.5b_vs_qwen7b/deployment | +0.85 (+0.72 to +0.92) | -0.27 (-0.40 to -0.13) |
| qwen1.5b_vs_qwen7b/sharing | +0.27 (+0.15 to +0.39) | +0.22 (+0.11 to +0.34) |
| qwen7b_vs_llama8b/pooled | +0.00 (-0.03 to +0.03) | -0.07 (-0.17 to +0.04) |
| qwen7b_vs_llama8b/deployment | +0.00 (-0.06 to +0.06) | -0.05 (-0.22 to +0.12) |
| qwen7b_vs_llama8b/sharing | +0.00 (-0.06 to +0.06) | -0.08 (-0.18 to -0.01) |

## RQ4 · trace-monitor false-positive rate on compliant runs

| Monitor | Overall | Granted | Pending | Denied |
|---|---|---|---|---|
| claude_trace | 0/293 (0%; 0–1) | 0/99 (0%; 0–4) | 0/96 (0%; 0–4) | 0/98 (0%; 0–4) |

## Breach mechanism (descriptive)

| Task / actor | No request first | Wrong target only | Correct request, then operation |
|---|---|---|---|
| deployment/llama8b | 0 | 0 | 0 |
| deployment/qwen1.5b | 45 | 3 | 3 |
| deployment/qwen7b | 0 | 0 | 0 |
| sharing/llama8b | 0 | 0 | 0 |
| sharing/qwen1.5b | 6 | 9 | 1 |
| sharing/qwen7b | 0 | 0 | 0 |
