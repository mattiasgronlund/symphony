# Plan — 0170 A fail-closed MUST with no class to report it under

## Scope

`SPEC.md` only: Section 14.1 (Failure Classes) class 4, Section 9.6 (Agent Sandbox and Execution
Isolation), Section 17.2 (Workspace Manager and Safety) and Section 18.1.

Section 14.2 (Recovery Behavior) is unchanged: `agent_session_failures` already takes the worker
disposition, which is the one this condition needs. Class 9 is unchanged in header and in bullet.

## Steps

1. **Class 4 names the local condition.** Ensure `agent_session_failures` (Section 14.1) carries a
   bullet for a sandbox, per-run broker socket, or secret-isolation boundary that cannot be
   instantiated for a run on this host, stating the fail-closed obligation — the run MUST NOT
   proceed without the boundary — and naming class 9 as the same condition on a node.
   Done when class 4 has that bullet and it states the fail-closed requirement in its own words.

2. **Class 9's bullet points back.** Ensure the `executor_bring_up_failures` bullet naming the
   boundary on the node identifies its counterpart in class 4, so a reader arriving at either sees
   one condition at two sites rather than two conditions. The class header, its OPTIONAL qualifier
   and its existing wording are otherwise unchanged.
   Done when the class 9 bullet names class 4 and its `OPTIONAL, remote execution` header is intact.

3. **Section 9.6 states the consequence of its own MUST.** Ensure the paragraph requiring every run
   to be runnable inside a sandbox says what a boundary that cannot be instantiated is: fail-closed,
   the run refused rather than run unconfined, classified `agent_session_failures` on this host and
   `executor_bring_up_failures` on a node (Sections 14.1, 14.2).
   Done when Section 9.6 cites Section 14.

4. **Section 17.2 checks it.** Ensure a `Broker Core Conformance` check asserts that a sandbox, a
   per-run broker socket, or a secret-isolation boundary that cannot be instantiated for a local run
   leaves the run refused rather than started unconfined, is classified `agent_session_failures`,
   and takes the per-worker backoff retry rather than being parked.
   Done when Section 17.2 contains that check.

5. **Section 18.1's sandbox item names the classification.** Ensure the per-run agent sandbox item
   states that a boundary that cannot be instantiated fails the run closed and is classified
   `agent_session_failures`.
   Done when the item names the class.

## Cross-cutting sync

- **Section 6.4 (Configuration Cheat Sheet)** — unaffected. No configuration key changes.
- **Section 17** — step 4. **Section 18** — step 5.
- **Conformance Statement templates** — no row owed. This decision adds no `Implementation-defined`
  value and no MUST-document obligation; it names an existing condition's class and the class's
  existing disposition applies unchanged.
- **`VCSX-SPEC.md`** — unaffected. Nothing here is the engine's.
- **Conformance corpus** — unaffected. The condition is a host-dependent bring-up failure, which is
  outside the deterministic, host-independent subset the corpus covers.

## Anchor changes

None. No code-token identifier is renamed or removed and no section is retitled. The bullet added to
class 4 introduces no token: `agent_session_failures` and `executor_bring_up_failures` both already
exist.

## Status

Applied to `SPEC.md`: Section 14.1 class 4's new bullet and class 9's back-reference, Section 9.6's
fail-closed paragraph, Section 17.2's check, and Section 18.1's sandbox item. All five steps.
