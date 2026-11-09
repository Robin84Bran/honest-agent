# v0.1 repository audit · 6 November 2026
Read all five available turns of “🦋 Anthropic Residency Application” in ChatGPT (conversation 6aeb2e39-d934-83ec-a003-db69ada9a5dc). The originating turn distributes honest-agent-v0.1.zip. Three identically hashed copies were present in Downloads. No pre-existing project directory was present at the requested destination. The preserved ZIP is the source reviewed. No Git history or public remote was supplied.

## Reproduction
Using seed 42 and n=60, all four original tests passed. The regenerated dataset.jsonl, predictions.csv and metrics.json matched all archived bytes, including the row split and train predictions. SHA-256 values and runtime are in the baseline manifest.

| Monitor | TP | FP | TN | FN | Recall | Precision | FPR |
|---|---:|---:|---:|---:|---:|---:|---:|
| Final report substring | 1 | 0 | 6 | 11 | 1/12 | 1/1 | 0/6 |
| Trace heuristic | 7 | 0 | 6 | 5 | 7/12 | 7/7 | 0/6 |
| Deterministic rule | 12 | 0 | 6 | 0 | 12/12 | 12/12 | 0/6 |

## What generates those numbers
The generator cycles through four categories and shuffles individual rows. Category determines tool, permission, path, amount and truth. For a violating row the report admits a possible violation with probability 0.20. On compliant rows the 0.75 branch selects a different compliant wording. Neither branch executes a task. The 42 training rows serve as a partition only. All four templates are available to the evaluator by construction. The policy checker reconstructs the generating rule. The heuristic omits the transfer-limit clause. Each monitor receives the full row including truth, although the three implementations do not access that label when making predictions.

The archive has no model calls, real action sequence, independently observed state, task completion labels, model token costs, ambiguous intent or delegation. The final-report keyword result reflects the authored wording. It cannot establish comparative performance on model-generated behavior.
