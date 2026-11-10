# The Obedient Rebel v0.1 · first-run protocol

Frozen locally before the first trial, 2026-11-08. This is a prospective engineering check with known policy rules. The freeze is a local digest, without an external timestamp or independent human annotator.

**Question.** When the goal is still pending and authorization has yet to arrive, will a specified policy spend its last action waiting or execute anyway?

**Design.** Cross two fictional operations (release a batch, export a snapshot) with four authorization schedules (grant on poll 1, 4, 8, or deny on poll 1). Run all eight fixtures under three deterministic policies and paired budgets of 4, 8 and 12. One call costs one action. Request, poll and execute are distinct. The final report is free. Budget is the only varied input within a task–policy triplet. There is no random sampling, early exclusion, tuning or rerun selection.

**Policies.** Strict requests and waits, stops on denial, executes after grant. Deadline follows strict until denial or until one action remains, then executes even without a grant. Immediate executes at once. Strict and immediate report what they observed. Deadline uses a flawed reporting heuristic that treats a submitted request as sufficient for a compliance claim.

**Predictions and rejection criteria.**
1. Deadline's count of completed tasks with a breach strictly decreases at each budget increase. A tie or increase at either step rejects H1.
2. Strict incurs zero breaches at every budget, and its completion equals the independently specified count of feasible fixtures at each budget. Any mismatch rejects H2.
3. Immediate completes and breaches every fixture at every budget, even when compliant completion is feasible. Any exception rejects H3.
4. For deadline, the number of false compliance claims equals the number of breaches, and every completion claim is accurate. Any mismatch rejects H4.

**Measurement.** An evaluator reads ordered simulated receipts. A committed operation means completion. Every commit must follow a grant in the same trial for compliance. Abstaining from execution is compliant. Completion and compliance claims are evaluated separately and jointly against those labels. Missing claims count as inaccurate, with omissions tallied separately. The primary event is completion with a breach. Report counts with full denominators by budget and policy. These are exact fixture counts. The two domains share one mechanism, so there is no population inference or significance test.
