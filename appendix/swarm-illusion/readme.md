# The Swarm Illusion

A runnable Python experiment on when delegation helps a team finish more tasks correctly and when errors spread through handoffs. All measurements come from a seeded, scripted simulation. Real LLM teams have yet to be evaluated.

## Releases

| Version | Contents | Download |
|---|---|---|
| [v0.2 — parameter sweep](swarm_illusion_v0_2/README.md) | Eight seeds, 720 paired tasks per configuration, five handoff corruption rates, three missing-receipt rates, and an all-zero control. Includes pooled and per-seed results. | [v0.2 ZIP](swarm_illusion_v0_2.zip) |
| [v0.1 — first experiment](swarm_illusion_v0_1/README.md) | The original 300 synthetic inventories, independent answer ledger, delegation traces, monitor verdicts, and first-run results. | [v0.1 ZIP](swarm_illusion_v0_1.zip) |

## What the sweep found

With a 10-tick deadline and a shared cap of 13 actions per task, two workers beat one on all eight seeds at 0% and 2% handoff corruption. At 4%, two workers produced 299 correct answers versus 260 for one. At 8%, they produced 241. With 13 ticks, every configuration performed the same amount of work. Solo then tied both teams at zero handoff corruption and led at every positive rate tested. [Pooled counts](swarm_illusion_v0_2/results/pooled.csv) · [Per-seed comparisons](swarm_illusion_v0_2/results/per_seed.csv)

Missing receipts affected detection. At 4% corruption and 10 ticks, four workers produced 266 correct answers across all three receipt settings. Monitor recall fell from 100% to 85.0% to 68.1% as missing receipts rose from 0% to 40% to 80%.

## Reproduce v0.2

From this project directory, run the following with Python 3.9 or later. Only the standard library is required.

```sh
cd swarm_illusion_v0_2
python3 -m unittest discover -s tests -v
python3 run.py --out replay
diff -r results replay
```

The default run evaluates 69,120 task runs. An empty diff confirms the regenerated files match the bundled release.
