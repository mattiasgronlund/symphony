# Plan — 0114 One pull request per issue is a rule about which one

## Scope

`SPEC.md`: Section 9.10 "Forge Operations, Pull Requests, and Review Writes" (the identity and the
re-verification), Section 17 "Test and Validation Matrix" (the validation profiles list and a
`Concurrency Stress` profile), Section 17.2 or 17.4 (the checks), Section 18.1.

`conformance/vocabulary.json`: no new token unless the refusal needs one; the broker's forge verbs
already return "a stable reason code on failure", so the refusal takes a reason code alongside
`pr_conflict` and `scope_denied`.

## Steps

1. **`Forge Operations` — the identity.** Ensure Section 9.10 states that Symphony resolves the pull
   request for an issue to the forge's own pull-request identity and carries **that**, not the work
   branch, into every subsequent mutating operation for the run. Done-condition: a reader can tell
   that a branch name is a lookup key rather than the identity of the thing written.

2. **`Forge Operations` — re-verify before the write.** Ensure the text requires that immediately
   before a mutating forge write the identity is re-read and checked against what the run
   established — the pull request exists, carries this run's work branch as its head, and targets the
   resolved base — and that a mismatch refuses the write. Done-condition: a hijacked title is a
   refusal rather than an overwrite.

3. **`Forge Operations` — the refusal is not retried.** Ensure the text states that a mismatch means
   another writer is acting on the same pull request, so the repair is an operator's: retrying
   re-reads a state a second writer is still changing. Done-condition: the disposition is stated,
   not left to Section 8.4's backoff.

4. **`Forge Operations` — what "immediately before" bounds, and what it does not.** Ensure the text
   states that the re-read and the write are the closest pair the forge's interface allows with no
   intervening Symphony operation, that this narrows rather than closes the window, and that a
   backend whose forge offers a conditional update SHOULD use it — the shape `expected_head` already
   has (Section 9.7, `VCSX-SPEC.md` Section 9.2). Done-condition: the guarantee is stated over
   something a consumer can check and does not claim atomicity Symphony cannot provide.

5. **`Forge Operations` — the failure it prevents reaches history.** Ensure the text notes that the
   squash subject is derived from the pull-request title verbatim, so a hijacked title enters
   history at the merge. Done-condition: the stakes are readable where the rule is.

6. **Forge verbs — the reason code.** Ensure the broker's forge verbs carry a stable reason code for
   the refusal, alongside `pr_conflict` and `scope_denied`. Done-condition: an agent receiving the
   refusal can branch on it.

7. **Section 17 — the `Concurrency Stress` profile.** Ensure the validation-profiles list gains a
   `Concurrency Stress` profile, RECOMMENDED, described as running concurrent sessions against one
   repository and one pull request, on the same footing and for the same reason as
   `Real Integration Profile`: it needs a live forge and real concurrency. Done-condition: the
   profile is defined where the others are and its optionality is argued, not asserted.

8. **Section 17 — the check.** Ensure a check exists that concurrent sessions produce no hijack:
   every write either applies to the identity its session established or is refused; and a
   single-session check that a pull request retargeted or closed between two runs is refused rather
   than written. Done-condition: the second check runs without concurrency, showing the rule is a
   correctness rule rather than a concurrency feature.

9. **Section 18.1.** Ensure the checklist carries the identity rule and the re-verification.
   Done-condition: the checklist states what a conforming implementation carries into a mutating
   forge write.

## Cross-cutting sync

Section 6.4's cheat sheet gains nothing: no configuration key changes. Section 17's profile list and
Section 18.1 are covered by steps 7–9. Section 19 gains nothing — no `Implementation-defined` choice
is introduced beyond the backend's use of a conditional update, which `VCSX-SPEC.md` already records.

## Anchor changes

New anchors: one broker forge-verb reason code for the refusal, and the `Concurrency Stress`
validation profile name. No anchor is renamed or removed.

## Status

Applied to `SPEC.md` (Sections 9.10, 17, 17.9, 18, 18.1).
