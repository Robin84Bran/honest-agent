# The Swarm Illusion v0.2

**Scripted simulation baseline.** In the eight-seed run, extra workers produced more correct totals when a deadline prevented the solo worker from finishing hard tasks and handoffs were sufficiently reliable. Once the solo worker had time to finish, extra workers never increased correct yield in this model.

## Reproduce

Extract the ZIP, enter the project directory, and run with Python 3.9+ (standard library only).

```sh
python3 -m unittest discover -s tests -v
python3 run.py --out replay
diff -r results replay
```

The default sweep regenerates the packaged CSVs. To extend it, change the seed range or sample size, for example with `python3 run.py --first-seed 900 --seeds 20 --per-level 50 --out extended`. Choose a separate output folder to retain earlier results.

## Design

Each seed generates 30 inventories in each of three difficulties. A workflow reads records, adds bin subtotals, and submits a grand total. The difficulties require 7, 10 and 13 actions. The oracle sums the original data independently. Each configuration receives the same inventories and paired draws for corresponding node/edge faults. The eight seeds start at 20261108. Each cell evaluates 720 tasks. There are 69,120 task runs across the grid, counting repeated evaluations of the same tasks.

Compare 1, 2 and 4 workers under a team-wide cap of 13 actions per task and a deadline of either 10 or 13 ticks. Each worker can perform one ready action per tick. Each node belongs to one worker, assigned round-robin. Parallel capacity increases with headcount. No retries, voting, or feedback from the monitor occur. Every cell in the tight profile used 6,480 actions for one worker and 7,200 for either team; every relaxed cell used 7,200 actions. This distinguishes an equal spending limit from equal realized work.

The main sweep fixes local faults at 7% per action, crosses handoff corruption of 0%, 2%, 4%, 8% and 16% with missing receipts of 0%, 40% and 80%, and adds an all-zero control. Each local fault or corrupted handoff adds one unit, so errors cannot cancel. Only cross-worker handoffs face corruption or missing receipts. Receipts affect what the arithmetic monitor can verify; they never change a delivered value. This model tests scheduling and exposure to bad handoffs. Its chosen probabilities are uncalibrated against LLM behavior.

## Measured correct totals per 720 assigned tasks

Correct means the simulator submitted a final total matching the oracle. An incomplete task earns zero correct submissions. Results here are identical across all three receipt rates. The two right columns count seeds with a strictly higher yield than the solo worker under the 10-tick deadline.

|Handoff corruption|1 worker, 10 ticks|2 workers|4 workers|2-worker wins / 8|4-worker wins / 8|
|---:|---:|---:|---:|---:|---:|
|0%|260|349|349|8|8|
|2%|260|323|307|8|8|
|4%|260|299|266|7|3|
|8%|260|241|189|1|0|
|16%|260|176|121|0|0|

At 4% corruption the two-worker team gained 39 correct totals in aggregate. The four-worker team's six-answer gain masks three seed wins, two ties and three losses. Both teams fell below solo at 8%. These grid points bracket the observed change of sign; they do not resolve a precise crossover probability.

At 13 ticks solo produced 349 correct totals. The team columns above also give their 13-tick counts since both teams already completed every task at 10 ticks. With all tasks finished, adding handoffs can only preserve or corrupt a value in this simulator.

**All-zero control.** Solo finished 480 correct totals at 10 ticks, compared with 720 for each team. At 13 ticks all three delivered 720 correct totals with identical action counts. No faulty traces, alerts or abstentions occurred. Recall has no defined denominator here.

**Receipt sweep.** For four workers at 4% corruption and 10 ticks, correct totals held at 266 across the three receipt settings. As missing receipts rose from 0% to 40% to 80%, monitor recall fell from 100% to 85.0% to 68.1%. Abstention rose from 0% to 44.7% to 57.1%. The monitor checks each visible delivery against its source and checks arithmetic when all inputs are visible. Contradictions yield an alert; otherwise missing evidence yields abstention. A clean verdict means all observed actions passed. Partial traces are audited too.

## Inspect or reuse the results

- results/pooled.csv contains 96 configuration rows. results/per_seed.csv contains all 768 seed-level rows. results/settings.json records the inputs.
- gained_vs_one and lost_vs_one count paired tasks on which only the team or only solo produced a correct answer, respectively. Their difference gives delta_vs_one. Seed wins, ties and losses use that difference within each seed.
- propagated counts tasks where a later node consumed an already incorrect parent output. recall is alerted faulty traces / all faulty traces. false_positive_rate is alerted clean traces / all clean traces. abstention divides all abstentions by assigned tasks. Empty rate fields mean a zero denominator.
- dataset.py regenerates each seed's public tasks and independent truth ledger. simulator.py returns per-action records with worker, parent links, delivered values and receipt visibility. scoring.py grades a trace; run.py performs the sweep.
- To inspect a single chain, run the following in Python from this directory.

```python
from pprint import pprint
from dataset import generate
from simulator import simulate, public_view, monitor
from scoring import score

tasks, ledger = generate(20261108, 30)
task = tasks[-1]
trace = simulate(task, 20261108, agents=4, ticks=10, budget=13,
                 local_rate=.07, transfer_rate=.04, omit_rate=.40)
pprint(trace)
pprint(score(trace, ledger[task['id']], monitor(task, public_view(trace))))
```
