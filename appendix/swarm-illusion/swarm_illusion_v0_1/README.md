# The Swarm Illusion v0.1

**Scripted simulation baseline.** Does extra worker capacity improve completion while permitting an incorrect intermediate result to travel farther or escape an audit? This offline Python experiment measures that trade-off in a synthetic inventory workflow. It contains no empirical LLM measurements. It uses only the Python standard library and runs without accounts or network access.

## Reproduce the first run

From the extracted project directory, using Python 3.9 or later (tested with 3.9.6), run

```sh
python3 -m unittest discover -s tests -v
python3 run.py --seed 20261108 --per-level 100 --out replay
diff -r data replay/data
diff -r results replay/results
```

The first command runs six tests. The second runs 1,800 trials over 300 paired tasks. On macOS/Linux the two diff commands produce no output for an identical replay. To explore a different seed, pass another integer and a fresh output directory.

## First-run measurements

Each row covers the same 300 tasks. Completion counts every submitted total. Correct counts only submissions that match the ledger. Spread counts tasks in which a later node consumed an already incorrect output. Recall uses every faulty trace, including partial traces. Missed finals counts incorrect submissions that received no alert.

|Ticks|Workers|Completed|Correct|Wrong final|Spread|Monitor recall|False positives / clean|Abstained|Missed finals|
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|10|1|200|105|95|112|149/149|0/151|0|0|
|10|2|300|119|181|159|149/181|0/119|141|32|
|10|4|300|112|188|165|146/188|0/112|150|42|
|13|1|300|140|160|146|160/160|0/140|0|0|
|13|2|300|119|181|159|149/181|0/119|141|32|
|13|4|300|112|188|165|146/188|0/112|150|42|

At 10 ticks, the single worker ran out of time on every hard task. Four workers submitted 100 more totals and delivered seven more correct answers. Some of the extra spread under that deadline reflects the extra work finished. At 13 ticks, all configurations executed the same nodes. Moving from one worker to four then raised spread from 146 to 165 tasks and reduced correct submissions from 140 to 112. The two-worker configuration produced seven more correct totals than four workers in both profiles.

All 42 unflagged wrong four-worker submissions received an abstention. None received a clean verdict. If a downstream system holds abstentions for review, these are unresolved cases. If it accepts every submission without an alert, those 42 errors pass through. The simulator records verdicts without implementing either downstream policy.

## Experiment design

- **Dataset and independent truth.** Each difficulty has 100 inventories with two, three, or four bins and two quantity records per bin. Workers transcribe each record, add each bin, and combine bin totals, requiring 7, 10, or 13 actions. The oracle computes each expected value directly from the original records before simulation, including a separate direct sum for the final total. The simulator never receives the ledger.
- **Controlled comparisons.** All configurations receive identical tasks, a team-wide limit of 13 actions, and the same deadline within each profile. A worker performs at most one ready action per tick. Parents must finish in an earlier tick. Workers own nodes by their position in the ordered workflow modulo team size. Parallel capacity grows with headcount. Actual work consumed is recorded, so the deadline comparison can be distinguished from the equal-work relaxed comparison.
- **Paired randomness.** SHA-256 maps seed, task ID, node or edge, and event type to a reproducible draw. A node has the same local fault opportunity across configurations. Each local arithmetic/transcription fault adds one with probability 7%. Each cross-worker delivery independently adds one with probability 4%, and omits its receipt with probability 40%. Same-worker deliveries preserve values and receipts. These chosen rates model a mechanism and have no empirical calibration. Positive-only errors cannot cancel.
- **Delegation chains.** Each trace records every node's assigned worker, tick, output, dependencies, source and destination workers, actual delivered values, and simulated fault flags. Starting at total, follow each edge's from field to its producing node to reconstruct every dependency chain. For an incomplete trace, start at its last completed nodes. This models fixed assignments and handoffs. It does not model autonomous delegation, dialogue, or worker specialization.
- **Monitor.** The public view exposes outputs, parent identifiers and receipted input values. The monitor checks source transcription, arithmetic when all operands are visible, and whether visible deliveries equal producer statements. Any contradiction yields an alert, otherwise any absent receipt yields abstention, otherwise clear. A partial trace can earn a clear verdict on the actions observed. The monitor sees neither oracle answers nor injected fault flags.

## Metrics and interpretation

A trace is faulty if any produced node differs from its ledger entry. A propagated edge requires a wrong producer output and a delivered value that is still wrong. A newly corrupted delivery from a correct producer first counts as an introduced fault. Wrong and correct finals exclude incomplete tasks. Correct yield divides correct submissions by assigned tasks. Wrong per completed divides wrong submissions by completed tasks.

Recall is alerts on faulty traces divided by all faulty traces. False-positive rate is alerts on clean traces divided by all clean traces. Abstention rate uses all assigned tasks. Unflagged wrong finals includes clears and abstentions, which the trace records distinguish. An undefined rate is an empty CSV cell. The monitor's exact checks and the scripted fault model explain the observed zero false positives. A monitor allowed to recompute the whole inventory could detect every wrong final here. Concealment is relative to the specified receipt audit.

The six configurations reuse tasks and draws. The 1,800 trials are paired observations from one seed, with only one task family. Headcount changes both scheduling and the number of exposed handoffs. Extra handoffs carry a fault cost by construction. These measurements quantify the consequences of those assumptions and cannot establish the behavior of real agent teams.

## Files

- dataset.py generates public tasks and oracle answers. data/tasks.jsonl and data/ledger.json contain the first-run fixtures.
- simulator.py implements the scheduler, handoff model, public trace projection, and monitor.
- run.py scores against the ledger and writes the trial records and summaries.
- results/settings.json records the first-run settings. results/summary.csv includes counts and rates for each difficulty and the pooled tasks. results/traces.jsonl contains one complete record per trial, including the monitor verdict and scores.
- tests/test_swarm.py covers oracle agreement, resource limits, dependency order, receipt visibility, propagation, abstentions, pairing, replay, and partial submissions.
