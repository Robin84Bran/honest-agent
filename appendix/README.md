# Appendix: two sister projects

Two sister projects to the Honest Agent. They ask related oversight questions. Both began as **scripted simulations with no AI model run**; their v0.1 results show what each test harness can measure, not how real models behave. **The Obedient Rebel has since run real models:** v0.2.1 put three local models under deadline pressure, and v0.2.2 monitored those runs. The Swarm Illusion is still a simulation.

| Project | Question | What the v0.1 simulation shows | Status |
|---|---|---|---|
| [The Obedient Rebel](obedient-rebel/README.md) | When approval is slow and the action budget is running out, does an agent wait or act? | Three hand-written policies on 8 fixtures at budgets of 4, 8 and 12 actions (72 trajectories). A "deadline" policy breaches when waiting can't fit in the budget, and stops breaching once it can. All four pre-registered predictions held, but by construction, since the policies are scripted | **Now run with real models.** [v0.2.1](obedient-rebel/v0.2.1/RESULTS.md): three local models broke the rule in 670 of 1,080 runs, and more room to wait didn't reduce it. [v0.2.2](obedient-rebel/v0.2.2/RESULTS.md): a trace monitor caught all 670 breaches; a report-only monitor caught only the 266 the agent confessed, and none of the 323 it denied |
| [The Swarm Illusion](swarm-illusion/readme.md) | Does adding agents improve reliability, or spread errors through handoffs? | A seeded sweep of teams against solo workers. Under a deadline, teams win at low handoff corruption; with enough time, solo ties or leads. **A monitor's recall fell from 100% to 85.0% to 68.1% as 0%, 40% and 80% of receipts went missing**: the same lesson as the Honest Agent, from another angle | Simulation only. Its results follow largely from its own assumptions: teams only gain speed, and handoffs can only add errors |

## Provenance

- Built by Bin "Robin" Xie with GPT via Codex, 8–9 November 2026.
- Copied here on 10 November 2026 from their private project folders, without the Codex working folders. One local folder name was redacted; see `../RELEASE_MANIFEST.md`.
- Reproduced from this copy on 10 November 2026, byte for byte, before release:
  - Obedient Rebel: 7 tests pass, and `experiment.py --verify` matches all 72 trajectories.
  - Swarm Illusion v0.1 and v0.2: tests pass, and the documented replays match the bundled results.

## Reproduce

Python 3.9 or later; standard library only. No network, no cost.

```sh
cd appendix/obedient-rebel
python3 -B -m unittest -v
python3 -B experiment.py --verify

cd ../swarm-illusion/swarm_illusion_v0_2
python3 -m unittest discover -s tests -v
python3 run.py --out replay && diff -r results replay

cd ../swarm_illusion_v0_1
python3 -m unittest discover -s tests -v
python3 run.py --seed 20261108 --per-level 100 --out replay && diff -r data replay/data && diff -r results replay/results
```

Licensing follows the repository: MIT for code, CC BY 4.0 for everything else (see `../README.md`).
