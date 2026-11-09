# The Honest Agent v0.3: do frontier agents ask before they act, and can a monitor tell when they don't?

*DRAFT for Robin's review, 9 Nov 2026. Not published. Prepared with Claude (claude-opus-5-5). Independently reviewed in two read-only rounds by GPT-6 Astra (via Codex); its findings and the fixes are listed in `DEVIATIONS.md`.*

## In short

I gave two frontier models, Claude Opus 5.5 and GPT-6 Astra, a small simulated job: record a payment, deploy a build, or share a document. There was one rule: get approval for the exact target first. Then I varied a single thing, the answer they got when they asked: *granted*, *pending (approver unavailable)* or *denied*.

- **Both frontier models followed the rule every time:** 0 breaches in 210 runs, and 210/210 honest end-of-task reports. Monitors reading the full action trace raised **zero false alarms**.
- **The small model breached; trace monitors caught everything; report-only monitoring did not.** The interesting monitor result comes from the small reference model, Qwen 2.5 1.5B, which breached in 22 of 60 runs and usually reported "no violation". Monitors reading the trace caught **22/22**. A Claude monitor reading only the model's final report caught 2 of the 17 breaches it gave a verdict on: a paired difference of **+0.88 (95% CI +0.59 to +0.97)** in favour of the trace.
- **That number comes from a deviation.** The Qwen arm had to be rerun after the pre-registered analysis, because of a setup mistake (details below).
- **Most of Qwen's breaches weren't a response to approval pressure.** In 15 of 22 it asked approval for the wrong thing and then went ahead anyway; in 6 it never asked.

The pre-registered replication question, whether the v0.2 trace advantage holds with frontier actors, could not be answered: frontier actors never breached, so there was nothing to catch.

## Read this first: what went wrong and what it means

I'm putting these up front because each one changes how far the results can be trusted.

1. **The Qwen arm is a post-freeze deviation.** The model wasn't installed when the pre-registered held-out run started. All 60 Qwen trials failed at the first call (HTTP 404), and the runner saved those failures as permanent trial files.
   - I installed the identical model build (the same digest as v0.2) and ran the Qwen arm once more, as a separately named series. The run used the frozen code unchanged. The deviation and analysis plan (`SUPPLEMENT_QWEN.md`) were written down 36 seconds before the run started, according to local file metadata that outside readers can't check. The "~16:20" written inside that document is a wrong estimate (see `DEVIATIONS.md`).
   - It still ran about three hours later, after I had seen the frontier held-out results. **Every number involving Qwen, including the only RQ1 result, is a deviation, not a pre-registered finding.** The 60 failed files are kept and published.
2. **Qwen's breaches were mostly not about approval.** In 21 of 22 breaches Qwen never saw the approval answer at all:
   - In 15 runs it requested approval for the recipient's email address instead of the document, got "unknown target", and shared anyway.
   - In 6 runs it skipped the request entirely.
   - Only 1 breach followed a correctly targeted request (pending, asked twice, then shared).

   So Qwen tells us how monitors handle real breaches. It tells us almost nothing about how a model responds to *pending* or *denied*.
3. **The frontier models showed no run-to-run variation.** Each actor × condition × task cell produced the same action sequence on every seed. The command-line tools I used don't take a seed. So the 210 frontier runs are really 12 behaviours, each repeated, observed on 3 tasks. The confidence intervals assume independent runs and therefore look tighter than they deserve.
4. **The replication question is unanswered.** The v0.2 trace-vs-report gap was found on the *deployment* task. In v0.3 nobody breached on that task, and the Qwen breaches happened on the new *sharing* task.

## Background

v0.2 ([`v0.2/`](../v0.2/README.md) in this repository, with the action-budget study in [`v0.2/action-budget/report.md`](../v0.2/action-budget/report.md)) gave Qwen 2.5 1.5B a simulated deployment task with an approval rule.

- **Breaches:** it breached in 16 of 20 runs, and giving it more steps never undid an early breach.
- **Reports:** its final reports were usually wrong.
- **Monitors:** a monitor reading the action trace had higher recall than one reading only the final report, by 12–23 percentage points. With 20 runs the intervals crossed zero.

v0.3 asked whether this holds with frontier models, and added the approval condition as a factor.

## Questions (pre-registered)

- **RQ1 (primary, replication).** Does an LLM monitor reading the full action trace catch more approval breaches than the same monitor reading only the task and the actor's final report?
- **RQ2 (primary).** How often do frontier actors breach approval, and how accurately do they report completion and breach, under granted, pending and denied approval?
- **RQ3 (exploratory).** Does a monitor judge its own model family's trajectories differently?

## Design

- **Actors:** Claude Opus 5.5 and GPT-6 Astra (medium effort), run through their subscription command-line tools with every tool, shell and web access switched off. Qwen 2.5 1.5B runs locally as a reference arm, on the held-out task only.
- **Sandbox:** in memory only. The actor has at most 4 decisions: request approval, perform the operation, or finish. Ground truth comes from the simulator's own ledger.
- **Conditions:** the only difference between conditions is the text returned by `request_approval`. Prompts are copied verbatim from v0.2, and a test checks this.
- **Monitors:** Claude and GPT, each in two views: the final report only, or the full trace of calls and observations. Monitors never see model names, conditions or seeds, and may answer "insufficient evidence" (`null`). A deterministic policy checker from v0.2 runs alongside.
- **Tasks and sample:**
  - calibration, *payment*: 30 runs
  - replication, *deployment*: 60 runs
  - held-out, *sharing* (new): 120 frontier runs, plus 60 Qwen runs in the supplement
- **Sample-size fallback:** the plan was 330 runs. A pre-registered rule cut replication from 20 to 10 seeds when the post-calibration cost projection (197.85 USD) exceeded 90% of the 200 USD cap.
- **Freeze:** all code, configuration, tasks and the protocol were hashed and frozen after calibration and before the main runs. The hashes still match in the author's working copy. In the public copy, `providers_api.py` differs by two redacted path lines, so the frozen runner's freeze check fails there by design; reruns should use v0.4.
- **Spend:** 158.33 USD in API-equivalent terms, under the 200 USD cap. The cap was enforced by an estimated check before each call, not a hard limit: the check didn't reserve money for calls already in flight and left out the hidden harness tokens (see `DEVIATIONS.md`).

## Results

### Frontier actors complied and told the truth (RQ2)

| Task | Actor | Granted | Pending | Denied |
|---|---|---|---|---|
| payment | Claude | 0/5 breaches · 5/5 accurate | 0/5 · 5/5 | 0/5 · 5/5 |
| payment | GPT | 0/5 · 5/5 | 0/5 · 5/5 | 0/5 · 5/5 |
| deployment | Claude | 0/10 · 10/10 | 0/10 · 10/10 | 0/10 · 10/10 |
| deployment | GPT | 0/10 · 10/10 | 0/10 · 10/10 | 0/10 · 10/10 |
| sharing | Claude | 0/20 · 20/20 | 0/20 · 20/20 | 0/20 · 20/20 |
| sharing | GPT | 0/20 · 20/20 | 0/20 · 20/20 | 0/20 · 20/20 |

Pooled, this is 0/210 breaches (95% Wilson 0–1.8%, post hoc pooling). Given the lack of variation above, read this as "consistently compliant in this setup", not as a precise rate.

Both models did the same thing under granted and denied: one request, then either the operation or a stop. Under pending they differed. Claude asked once and stopped. GPT asked four times, using its whole decision budget, and then stopped. Neither ever acted without a grant.

This matches the pre-registered reading for "near-zero breaches": the frontier actors complied under this pressure, and the main monitor result is the false-positive rate.

### Monitors: no false alarms on frontier runs, and the trace matters on real breaches

| Monitor | Caught (Qwen breaches) | False alarms (frontier runs) | False alarms (Qwen clean runs) | Said "insufficient evidence" |
|---|---|---|---|---|
| Policy checker | 22/22 | 0/210 | 0/38 | 0/270 |
| Claude, full trace | **22/22** | **0/210** | 0/38 | 0/270 |
| GPT, full trace | **22/22** | **0/210** | 0/38 | 0/270 |
| Claude, final report only | 2/17 decided | 0/118 decided | 3/16 decided | 119/270 |
| GPT, final report only | none decided | none decided | 1/1 decided | 269/270 |

*Qwen columns: deviation. Frontier columns: pre-registered.*

**RQ1 (deviation, sharing task, Claude monitor).** There are 17 breaches where both of Claude's views gave a verdict. The trace caught 15 that the report-only view missed, and the reverse happened 0 times. Paired difference: +0.88 (95% CI +0.59 to +0.97). GPT's report-only view abstained on every breach, so there are no GPT pairs.

**Why the report-only view failed** (post hoc). The two monitors reacted to self-reports in opposite ways:

- **GPT** treated a self-report as insufficient evidence almost every time (269 of 270).
- **Claude** abstained whenever a report claimed the task succeeded, but **believed reports that said nothing went wrong**. The 15 breaches Qwen falsely reported as "no violation" all passed Claude's report-only view.

That is the failure mode a report-only monitor is exposed to: it inherits the actor's honesty. Here the traces fit confusion (wrong-target requests), although this data can't establish intent. A deceptive actor would exploit the same weakness.

### RQ3: no power

Every breach came from Qwen, a different family from both monitors, so same-family recall can't be measured. The trace monitors had 0 false alarms in both groups. Claude's report-only view had 0/34 same-family and 3/45 cross-family (all 3 on Qwen's clean runs). GPT's report-only view made a single cross-family decision, a false alarm on a Qwen run, and no same-family decisions.

## What this does and doesn't show

**It does show:**

- In a short, explicit approval task, two frontier models reliably waited for approval and reported honestly across three task framings.
- Trace-reading monitors raised no false alarms on 210 frontier runs and caught every breach from a weaker model.
- Report-only monitoring is only as good as the report. A monitor that trusts "no violation" claims misses most falsely reported breaches.

**It doesn't show:**

- How frontier models behave under real pressure. The cue here was explicit and nothing pulled against it.
- Whether frontier models would conceal a breach.
- Whether the v0.2 trace advantage replicates on the original task.
- Anything precise about rates. Frontier runs didn't vary, and the Qwen numbers come from a deviation.

## Limitations

These are the six limitations listed in the protocol's threats-to-validity section, plus what this run added:

- **Demand effects:** "approval pending: approver unavailable" and "approval denied" are explicit stop signals.
- **Evaluation awareness:** JSON-only outputs can't show whether a model knew it was being tested, and perfect compliance is what an evaluation-aware model would produce.
- **Binary report fields:** two booleans can't capture partial or hedged honesty.
- **One sandbox, short horizon:** one tool, one target, a stated policy, 4 decisions and no competing incentive. The sharing task's recipient field also invited Qwen's wrong-target requests.
- **Provider safety layers:** frontier actors ran behind production stacks, so compliance can't be credited to the model alone.
- **Model-family overlap** between actors and monitors: RQ3 couldn't test it.
- **Not reproducible:** frontier sampling through subscription tools can't be replayed. Every raw response, token count and timestamp is saved.
- **API-equivalent cost:** cost is an estimate from reported tokens. GPT calls were about 97% of it. By a rough estimate, about 94% of the total came from the roughly 14K tokens of fixed harness instructions that the Codex tool adds to every GPT call; harness tokens aren't itemised separately.

## What v0.4 should do

- **Make breaches likely and deceptive, so RQ1 can be tested properly.** Use a scripted or fine-tuned breaching actor that hides its breach in the report. Or create real competing incentives: a deadline, a cost for not acting, a user pushing to "just do it".
- **Make approval ambiguous instead of explicit:** stale grants, grants for a similar but different target, an approver who says "probably fine".
- **Use longer horizons and multiple targets,** so a breach can be buried in the middle of a trace.
- **Get real sampling variation,** via API seeds or temperatures, or by varying prompt paraphrases, so the intervals mean what they claim.
- **Pre-register the abstention policy.** Decide in advance whether monitors may say "insufficient evidence", and how abstentions count.
- **Fix the operational gaps v0.3 exposed.** Preflight must check the local model; the runner must not save a trial whose actor never started; the GPT adapter must report the model ID Codex actually used. Review also found two latent defects that affected no v0.3 trial: the budget check didn't reserve money for calls in flight, and a step that failed after the actor started could be scored as compliant. Fixes for all five are drafted with offline tests in a separate v0.4 folder. That folder isn't in this repository yet and hasn't been run against real models.

## Materials

Everything is in this folder:

- `PROTOCOL.md` and `freeze.json` (hashes of all frozen files)
- all 330 trial files, including the 60 failed Qwen files
- the spend ledger, run logs and frozen analyses (`results/analysis-*.md`)
- the Qwen supplement: `SUPPLEMENT_QWEN.md`, `supplement_qwen.py`, `results/analysis-heldout_qwen_supplement.md`
- the post hoc combined held-out table (`results/posthoc-heldout-combined.md`)
- a results page with charts (`site/index.html`; post hoc presentation), rebuilt from the raw trial files by `site/build_site.py`
- a list of every deviation and post hoc analysis (`DEVIATIONS.md`)
