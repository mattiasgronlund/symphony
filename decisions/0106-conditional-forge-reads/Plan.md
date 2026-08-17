# Plan — 0106 A read that answers `unchanged`, and the validator that asks for it

## Scope

`VCSX-SPEC.md`: Section 4.1 "Operation Set" (`status`'s outputs), Section 8.1 "Entry Points and
Arguments" (the validator argument), Section 8.2 "Result Envelope" (the validator in `outputs`),
Section 9 preamble (the fourth answer's place in the answer discipline), Section 9.2 "Forge Backend
Plugin" (`pr_state`'s argument, answer and prohibition; the descriptor field), Section 13.1 "Test
Matrix".

`VCSX-CONTRACT.md`: no change. The capability signature, the descriptor and the invocation argument
are all inside what Section 11 defers to the full engine spec (the plugin API, the invocation
contract, the field-level consumer-configuration schema), and this decision adds no name the two
documents share.

`conformance/vcsx/`: no vector data (decision 0111 fixes the fault-injection vector shape and the
`304` case is authored against it); the token vocabulary gains nothing, since no reason or `need`
token is added.

## Steps

1. **`pr_state` — the argument and the fourth answer.** Ensure the capability reads
   `pr_state(work_branch, known_validator)` and that its entry states four answers: the pull
   request — its number, its state, the head it currently carries, **and the validator to present
   on a later read** — none where the forge carries no pull request for the work branch,
   `unchanged` where the caller presented a validator and the resource has not moved since it was
   issued, or that the state could not be determined. Done-condition: the entry distinguishes
   `unchanged` from both `none` and undetermined in its own prose, and a reader can tell which of
   the four a `304` is.

2. **`pr_state` — the prohibition.** Ensure the entry states that a backend MUST NOT answer
   `unchanged` where it presented no validator or made no conditional read, in the shape Section 9
   states its other non-answer prohibitions. Done-condition: the requirement is stated over the
   backend's answer rather than as something the engine checks.

3. **`pr_state` — which reads carry a validator.** Ensure the entry (or the paragraph in Section
   9.1 that enumerates `pr_state`'s three readers) states that the engine supplies a known
   validator only on a read whose answer it reports — `status` — and never on the reads `push` and
   `merge` condition a write on, because `unchanged` carries no state and therefore no head, and a
   `merge` conditioned on a consumer-remembered head is not conditioned on one the engine read
   (Section 9.2 `request_merge`, `expected_head`). Done-condition: a reader can tell, for each of
   `pr_state`'s three readers, whether a validator is presented.

4. **Section 9 preamble — the answer discipline covers four answers.** Ensure the preamble's rule
   (a value-answering capability MUST be able to answer that it could not determine one, and MUST
   NOT spell that as the value's absent or negative case) reads correctly over a capability with a
   determinate `unchanged` answer, so `unchanged` is visibly neither the absent case nor the
   non-answer. Done-condition: the preamble's enumeration of determinate facts —
   "An absent counterpart, a base the checkout does not hold, …" — accounts for a resource that has
   not moved.

5. **`status` — the outputs.** Ensure `status`'s entry in Section 4.1 states that where the
   invocation supplied a validator and the forge answered `unchanged`, the pull-request fields
   carry the values the caller already holds nothing for, a `pr_state_unchanged` output reports it,
   and the operation still completes — the shape the entry already uses for `base_absent`.
   Done-condition: `status` reports three distinguishable pull-request conditions —
   `pr_state_unavailable`, `pr_state_unchanged`, and a state it read — and no two are spelled the
   same way.

6. **Section 8.1 — the validator argument.** Ensure an OPTIONAL invocation argument carrying the
   last validator the consumer received exists, stated as opaque in the shape Section 8.1 uses for
   the forge repository coordinate and the access parameters ("the engine holds it opaque … takes
   it, supplies it to the forge backend, and interprets nothing"), and that its absence is not a
   precondition failure — an invocation supplying none makes an unconditional read.
   Done-condition: Section 8.6's precondition registry gains no row, and a reader can tell the
   argument is the consumer's cache key rather than engine state.

7. **Section 8.1 — where it may be read from.** Ensure the argument is **excluded** from the
   consumer-configuration list ("The consumer-supplied values this section names — `local_vcs` and
   `forge`, …"), because it changes per invocation and a configured one would be stale by
   construction. Done-condition: the consumer-configuration sentence names every consumer-supplied
   value except this one, and says why this one is not among them.

8. **Section 8.2 — the validator in the envelope.** Ensure `outputs` carries the validator
   alongside the pull-request number and state, so the value the next invocation presents is the
   value this one returned. Done-condition: the round trip is readable from Section 8.2 and
   Section 8.1 alone, without consulting Section 9.2.

9. **Section 9.2 — the descriptor field.** Ensure the descriptor field list gains whether the
   backend supports conditional reads, and that the text states an unsupporting backend is supplied
   no validator, answers the full state, and yields no `pr_state_unchanged` output — and that this
   is **not** `unsupported` (Section 4.3), because the operation proceeds and what is absent is a
   saving rather than a capability the operation requires. Done-condition: a consumer's loop is
   stated to be correct against either backend.

10. **Section 13.1 — the test matrix.** Ensure checks exist for: a validator presented and the
    resource unmoved yields `pr_state_unchanged` and not an absent pull request; a backend
    declaring no conditional-read support is supplied no validator; the validator returned by one
    invocation is the one a later invocation presents; and `push` and `merge` read `pr_state`
    without a validator. Done-condition: each of steps 1, 3, 5 and 9 has a check that would fail if
    the step were reverted.

## Cross-cutting sync

`VCSX-SPEC.md` Section 13.2's implementation checklist gains the conditional-read primitive and the
descriptor field; Section 13.3's Conformance Statement gains the backend's declaration of whether
it supports conditional reads and, where it does, the mechanism it realizes the validator with
(`Implementation-defined`, as `worktree_revision()`'s form already is).

No `repo.policy.toml` key changes, so Section 6's schema and the contract surface's Section 4 are
untouched.

## Anchor changes

New anchors: the `pr_state_unchanged` output token, the invocation argument carrying the validator,
and one forge descriptor field. `pr_state`'s signature gains a parameter — the capability name is
unchanged, so no existing reference breaks. No anchor is renamed or removed.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 8.1, 8.2, 9, 9.1, 9.2, 13.1, 13.2, 13.3).
