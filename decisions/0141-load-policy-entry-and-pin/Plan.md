# Plan — 0141 The operation no entry point named and no policy could dispatch

## Scope

- `VCSX-SPEC.md` — Section 4.1 (Operation Set), Section 4.3 (Reason Registry), Section 5.1
  (Triggers), Section 6.11 (Validation), Section 8.1 (Entry Points and Arguments), Section 8.2
  (Result Envelope), Section 8.6 (Preconditions), Section 13.1 (Test Matrix), Section 13.2
  (Implementation Checklist), Section 13.3 (Conformance Statement).
- `VCSX-CONTRACT.md` — Section 6's `run_op` lead-in, which introduces the operation list.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — the operation-set checklist bullet naming `provision`'s
  exemptions, and one new obligation row for the pin.
- `conformance/vcsx/vocabulary.json` — `operations` gains a per-entry flag; `config_reasons` gains
  `operation_not_dispatchable`; `precondition_reasons` gains the pin-mismatch reason; `output_keys`
  gains the pin; and two existing notes restate what this decision changes — `lifecycle_positions`
  carries the `provision`-only argument, and `reasons` carries the universal claim step 5 scopes.
- `conformance/vcsx/README.md` and `conformance/vcsx/vectors/match-edge.json` — both restate
  "defined for every operation", which step 5 scopes. Named here because
  `scripts/check_plan_anchors.py`'s reach check found them, and an edit addressed only to
  `VCSX-SPEC.md` Section 4.3 would leave two corpus artifacts asserting what the specification no
  longer does.
- `conformance/vcsx/vectors/policy-validation.json` — cases for the refusal; a precondition vector
  file for the pin mismatch.
- `scripts/validate_spec_consistency.py` — `CLOSED_GROUPS` gains `entry_points`.
- `SPEC.md`, `CONFORMANCE-STATEMENT-TEMPLATE.md`, `conformance/vocabulary.json` — **no change**.
  Symphony invokes `ship` and individual operations; it writes no `[policy]` edge and holds no
  policy surface between invocations, so nothing it owns moves.

## Steps

1. **`VCSX-SPEC.md` Section 8.1 "Entry Points and Arguments" — the enumeration names
   `load_policy`.** Ensure the individual-operations bullet lists `load_policy` alongside the ten
   operations already there, so the enumeration matches Section 4.1's eleven and the `entry_points`
   group it cites. *Done when:* the bullet names eleven operations, and
   `scripts/validate_spec_consistency.py` (after step 12) reports no drift between the group and the
   section.
2. **`VCSX-SPEC.md` Section 4.1 "Operation Set" — the bootstrap pair is marked once.** Ensure
   `VCSX-SPEC.md` Section 4.1 states, in one place a validator and a reader can both cite, that
   `load_policy` and `provision` run **outside the action-policy machine**: no `run_op` edge may
   name either, and neither raises a trigger an `on` may name. Ensure the marker is stated over the
   property rather than over the two names, so an operation a MINOR release adds with that property
   inherits it. Ensure the existing `VCSX-SPEC.md` `provision` argument — a gate on it "would be
   absent on the invocation that creates the checkout and present on one that refreshes it" — is
   what the prose leans on, rather than a new one. *Done when:* the property is named once, both
   operations are covered by it, and `VCSX-SPEC.md` Section 4.1's opening sentence ("Operations are
   the unit `run_op` runs") carries the carve-out rather than contradicting it.
3. **`VCSX-SPEC.md` Section 6.11 "Validation" — the table refuses the edge, with its own reason.**
   Ensure a row exists: a `run_op` naming an operation that runs outside the action-policy machine
   (Section 4.1) is a configuration error with the reason `operation_not_dispatchable`. Ensure the
   `unknown_operation` row is unchanged — it still names an operation the engine does not define —
   and that `VCSX-SPEC.md` Section 6.11's closing paragraph, which separates reasons by "a repair a
   reader can act on", is not contradicted. *Done when:* the table carries twenty-three rows, the
   new one is stated over the property rather than over `load_policy` and `provision` by name, and
   no existing reason widens.
4. **`VCSX-SPEC.md` Section 5.1 "Triggers" — the parenthetical covers both.** Ensure the
   `VCSX-SPEC.md` sentence quoted as "`provision` has no position and raises no trigger (Section
   4.1)" covers `load_policy` as well, so an `on = "load_policy:#error"` edge falls under the
   existing `unknown_trigger` row. *Done when:* both operations are named there and no new reason
   token is introduced for the trigger side.
5. **`VCSX-SPEC.md` Section 4.3 — the universal claim is scoped to what the machine can dispatch.**
   Ensure the `VCSX-SPEC.md` sentence quoted as "Every operation therefore has at least one `done`
   reason and at least one `error` reason" and the `(any)` rows' "defined for every operation" are
   scoped to the operations a policy can dispatch, so `load_policy` is outside the claim rather than
   a counterexample to it. Ensure the scoping is written as an invariant rather than as a list of
   exceptions, matching the `blocked` / `hook_unanswered` treatment already in that paragraph. *Done
   when:* the claim is true as written for every operation it now covers, and the Section 4.3 item
   decision 0134 recorded as unrepaired no longer describes the document.
6. **`VCSX-SPEC.md` Section 8.6 — the `git_access` scope narrows.** Ensure the `VCSX-SPEC.md`
   paragraph quoted as "an entry outside the set that reaches such an operation through a `run_op`
   edge reports that operation's own `failed`" no longer contemplates a `run_op` reaching
   `provision`; the reachable set through an edge is `integrate`, `push` and `pull`. *Done when:*
   the paragraph names no operation an edge may no longer dispatch, and the REQUIRED-for set it
   opens with is unchanged.
7. **`VCSX-SPEC.md` Section 8.1 — the policy pin is an argument.** Ensure an OPTIONAL argument
   exists carrying the policy-surface pin a previous `load_policy` returned, `Default: unset` — an
   invocation supplying none makes no continuation claim and runs whatever it reads. Ensure it is
   excepted from the consumer configuration for the reason the two read validators and `resume`
   already are (the engine holds nothing between invocations), which makes that excepted set four.
   Ensure the engine holds it opaque as it holds the `resume_token`. *Done when:* the argument
   exists with its default, the consumer-configuration sentence names four exceptions, and no clause
   admits a caller-authored policy surface as an argument.
8. **`VCSX-SPEC.md` Section 8.2 — `load_policy` returns the pin in `outputs`.** Ensure the fixed
   `outputs` keys carry the pin, in the shape `resume_token` already uses, and that Section 8.2 says
   which invocations carry it. *Done when:* the key is documented beside `resume_token` and the
   `output_keys` group (step 11) matches.
9. **`VCSX-SPEC.md` Section 8.6 — a supplied pin that does not match is a precondition failure.**
   Ensure a row exists for a supplied policy pin the engine cannot match against the surface it
   validated, with its own precondition reason rather than `resume_unusable`; the repairs differ,
   which is Section 6.11's own separation rule. Ensure a resumed invocation is not required to
   supply one, the token already carrying the same judgement. *Done when:* the row exists, the
   reason is new, and Section 8.1's resume paragraph is not widened to cover it.
10. **`VCSX-SPEC.md` Section 4.1 — the `load_policy` paragraph says what a consumer holds.** Ensure
    the `VCSX-SPEC.md` sentence quoted as "the consumer holds it and supplies it to every subsequent
    invocation, which therefore read no repository" is replaced: the consumer holds the surface for
    inspection and the pin for continuity, and every invocation reads and validates the document
    itself. *Done when:* no clause claims a subsequent invocation reads no repository, and
    `VCSX-SPEC.md` Section 3.2's "the consumer sources config by trust" is still the property the
    paragraph turns on.
11. **`conformance/vcsx/vocabulary.json` — the registry carries the property and the three tokens.**
    Ensure every `operations` entry carries a `policy_dispatchable` flag, `false` for `load_policy`
    and `provision` and `true` for the rest, with the group note stating what it marks and citing
    Section 4.1; ensure `config_reasons` carries `operation_not_dispatchable`,
    `precondition_reasons` the pin-mismatch reason, and `output_keys` the pin, each with its
    `spec_refs`. Ensure the `lifecycle_positions` note, which today explains the absent position for
    `provision` alone, covers both bootstrap operations, and the `reasons` note carries step 5's
    scoping rather than the unscoped universal claim. *Done when:* the flag is present on all eleven
    entries, no token is added that the specification does not fix, and no registry note asserts a
    claim `VCSX-SPEC.md` no longer makes.
12. **`scripts/validate_spec_consistency.py` — `entry_points` is a closed group.** Ensure
    `CLOSED_GROUPS` names `conformance/vcsx/vocabulary.json`'s `entry_points`, reading its
    membership from `VCSX-SPEC.md` Section 8.1, so a group citing a section it disagrees with is
    reported. *Done when:* the check walks three groups, and the script reports 0 errors and 0
    warnings against the edited documents — and reports an error if step 1 is reverted.
13. **Vectors.** Ensure `conformance/vcsx/vectors/policy-validation.json` carries a case for a
    `[policy]` edge with `op = "load_policy"` and one with `op = "provision"`, each expecting
    `operation_not_dispatchable`, and a case for an `on` naming `load_policy` expecting
    `unknown_trigger`. Ensure a precondition vector covers a supplied pin that does not match the
    validated surface, expecting the new reason. Keep one condition per vector, as
    `policy-validation.json`'s own notes require. Ensure
    `conformance/vcsx/vectors/match-edge.json`'s note and `conformance/vcsx/README.md`'s prose, both
    of which restate the universal claim, are scoped with it. *Done when:* every new token has at
    least one vector, no vector holds two failing conditions, and no corpus note restates the
    unscoped claim.
14. **`VCSX-CONTRACT.md` Section 6 — the lead-in matches.** Ensure the sentence introducing the
    operation list carries the same carve-out as Section 4.1: `run_op` runs the operations, less the
    two that run outside the machine. *Done when:* the contract does not describe `load_policy` as
    an operation `run_op` may name.
15. **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — the two obligations.** Ensure the operation-set
    checklist bullet that names `provision`'s exemptions names `load_policy`'s alongside them, and
    ensure an obligation row exists for the form of the policy pin and how the engine establishes
    that a supplied one still matches — modelled on the `resume_token` row, and cited to the
    sections that fix it. Ensure Section 13.3's obligation paragraph names the same thing, so the
    row and the obligation agree. *Done when:* both are present and `python3
    scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.
16. **`VCSX-SPEC.md` Sections 13.1 and 13.2 — the matrix and the checklist.** Ensure Section 13.1
    carries rows for: a `run_op` edge naming either bootstrap operation refused with
    `operation_not_dispatchable` before anything runs; an `on` naming one of them refused as
    `unknown_trigger`; `load_policy` invoked as an entry point returning the surface and the pin;
    and a supplied pin that no longer matches refused with the new reason. Ensure the Policy-loading
    row is restated to say what the pin makes observable — the surface a unit of work executes is
    fixed when the unit of work begins, and an invocation continuing one whose surface has since
    changed is refused rather than run under either document — rather than the current unobservable
    caching phrasing. Ensure Section 13.2 gains the matching checklist lines. *Done when:* every
    part of this decision has a row, and the Policy-loading row is falsifiable by a consumer.

## Cross-cutting sync

- `VCSX-SPEC.md` Section 13.1 (test matrix), 13.2 (checklist), 13.3 (Conformance Statement
  obligations): steps 15 and 16.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`: step 15 — required. The pin's form is engine-owned and
  `Implementation-defined`; the two new reason tokens sit inside their registries and owe no rows
  (`CLAUDE.md`, decision 0128).
- `SPEC.md` Sections 6.4, 17, 18: no change.

## Checked and unaffected

- `conformance/vcsx/vectors/base-precondition.json` and `identity-precondition.json` both carry a
  note about an entry outside a precondition's set reaching an operation through a `run_op` edge.
  Neither names `provision`: the first names `integrate` and `create_pr`, the second `commit`,
  `integrate` and `pull`. Both survive step 6 unchanged. Recorded because the reach check reports
  them.
- `VCSX-SPEC.md` Section 6.5's derived-context paragraph — "an in-sandbox edge's `run_op` naming an
  operation that reaches the remote receives no credential and reports that operation's own reason
  at the dispatch" — survives step 6 unchanged: the operations it contemplates that an edge may
  still name are `integrate`, `push` and `pull`, and the one it loses (`provision`) is refused
  earlier, at validation. Recorded because the reach check flags the site and a later reader should
  find the answer rather than the question.

## Ordering

- Apply **before** decision 0142. That decision's fourth resume condition is stated over the entry
  point the token was issued by, and its step-zero registry work presumes Section 8.1's enumeration
  is complete; it also counts the consumer-configuration exceptions, which step 7 here makes four.
- Independent of decisions 0140 and 0143.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0141-load-policy-entry-and-pin/Plan.md --rev
97617c2` reports one quote-fidelity finding and it is an artifact: a step header names its section
by title, and a title lives in a heading rather than in the section body the checker searches. The
reach findings it reports are answered above, in the scope list and in the checked-and-unaffected
section.

## Anchor changes

- **Added:** `operation_not_dispatchable` (Section 6.11), the pin argument and its `outputs` key
  (Sections 8.1, 8.2), the pin-mismatch precondition reason (Section 8.6), and the
  `policy_dispatchable` registry flag.
- **Changed:** Section 4.1's `load_policy` paragraph loses the clause "which therefore read no
  repository" (step 10). Decision 0134's plan quotes the surrounding sentence; it is not edited,
  being the record of what was true when written.
- No token is renamed or removed.

## Status

Not started.
