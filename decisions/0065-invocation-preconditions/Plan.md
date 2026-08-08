# Plan — 0065 Invocation preconditions are `usage_or_config`, with a registry of their own

## Scope

`VCSX-SPEC.md`: a new Section 8.6 "Invocation Preconditions" appended to the invocation contract, plus
edits to Sections 6.3 "`[scope]`", 8.2 "Result Envelope", 8.3 "Exit Codes", 8.5 "Versioning and the
Version Grammar", 13.1 "Test Matrix", 13.2 "Implementation Checklist", and 13.3 "Conformance
Statement".
`conformance/vcsx/vocabulary.json` and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` follow the new token
group.

A new subsection at the end of Section 8 renumbers nothing: Section 8.6 is free, and Section 9 onward is
unaffected. Placing it after Section 8.5 rather than before Section 8.2 — where it would read in
chronological order — is the same trade decision 0060 made for Section 5.6: Sections 8.2, 8.3, 8.4 and
8.5 are cited throughout both engine documents and the conformance data, and renumbering them to gain
reading order is not worth the churn.

No `VCSX-CONTRACT.md` edit: its Section 11 defers "the engine invocation contract (result envelope, exit
codes, escalation payload)" to `VCSX-SPEC.md` Section 8, it enumerates no invocation status and no
configuration reason, and `usage_or_config` does not appear in it. A precondition registry is entirely
on the deferred side.

No `SPEC.md` edit: Symphony's `Engine Invocation Failures` class (its Section 12.1) already covers
"only failures in which the policy never ran", which is precisely this case, and its summary of the
engine carries the triggers, actions and classes rather than the invocation statuses or the reason
registries. Its `scope.branch_pattern` keeps a default of its own (`symphony/<identifier>`), so the
engine-level default added in Step 1 does not change Symphony's configured behavior.

No vector change: `policy-validation.json` asserts `validate_policy` as a pure function over a policy
document, and a precondition needs a checkout and the invocation's arguments. `exit-codes.json` gains no
vector because no invocation status is added. `conformance/vcsx/README.md`'s "Deferred to later slices"
list gains the case, so a reader who finds the registry and no vectors finds the reason with it.

## Steps

1. **`branch_pattern` is OPTIONAL with a stated default.** Ensure Section 6.3's `branch_pattern` bullet
   is marked `(string, OPTIONAL)` and carries a nested `Default:` bullet stating that unset means the
   work branch is the checkout's current branch (Section 9.1 `current_branch`), and that a checkout with
   no current branch then has no work branch to derive, which Section 8.6 reports. Ensure the existing
   clauses — derivation from pattern and caller identity, the refusal of an arbitrary caller-named
   branch, name-only configuration, and the pinned push refspec — are unchanged. Done when the
   configuration state the `no_current_branch` reason describes is one the document admits exists.
2. **Section 8 gains a preconditions subsection.** Ensure `VCSX-SPEC.md` carries a subsection titled
   `Invocation Preconditions`, numbered 8.6, after `Versioning and the Version Grammar`. Done when
   Section 8 answers what an invocation returns when its setup fails, without the reader consulting
   Section 6.
3. **What a precondition is, and when it is established.** Ensure Section 8.6 states that the engine
   establishes the invoked entry point's preconditions between validating the policy (Section 6.10) and
   running it: it resolves the work branch (Section 6.3), which calls a VCS backend capability
   (`derive_work_branch` or `current_branch`, Section 9.1), and for an entry that commits it accepts the
   caller-supplied commit identity (Section 10.1), whose shape only the backend can judge because the
   engine holds it opaque. Done when the capability calls that happen before the first operation are
   named rather than implied.
4. **A precondition failure is not an operation result.** Ensure Section 8.6 states that no operation
   ran, so the Section 4.3 registry does not apply, no proto class is assigned, and there is no
   `<op>:<reason>` for the policy machine to route — the entry points are the front-end sequences and
   the operations (Section 8.1), and this is before the first of them. Done when an implementer cannot
   read the case as an `error`-class result with a null `op`.
5. **The outcome is stated once.** Ensure Section 8.6 states that the engine refuses to run the policy
   and returns the `usage_or_config` status (exit `2`, Section 8.3) with `op` and `class` null and
   `reason` carrying a precondition reason — the envelope Section 8.2 already defines for a run in which
   the policy did not run. Done when the exit code for a detached HEAD is the same on any conforming
   engine.
6. **The registry is a table of three.** Ensure Section 8.6 carries a `| Condition | Reason |` table, in
   the shape Section 6.10 uses, with: the work branch is the checkout's current branch (Section 6.3) and
   the checkout has none → `no_current_branch`; the derived work branch name is not a legal branch name
   for the VCS backend → `work_branch_invalid`; the caller-supplied commit identity is malformed as the
   VCS backend judges it (Section 10.1) → `identity_invalid`. Done when each of the issue's three states
   has exactly one token.
7. **The registry's rules mirror Section 6.10's.** Ensure Section 8.6 states that precondition reasons
   carry no proto class for the same reason configuration reasons do not, that they share the
   `usage_or_config` status so a consumer already branching on it absorbs a new one without a class
   edge, and that an engine MUST document any it adds beyond this registry (Section 13.3). Done when the
   two registries are governed alike.
8. **The boundary against operation reasons is explicit.** Ensure Section 8.6 states that an engine MUST
   NOT report a precondition reason for a condition an operation could have reported: once an operation
   is dispatched, its failure is that operation's own reason (Section 4.3). Done when the new registry
   cannot absorb failures that belong to Section 4.3.
9. **The dividing line against Section 6.10 is stated.** Ensure Section 8.6 records what separates the
   two registries: a configuration error is a property of `repo.policy.toml` alone and is detectable
   before any argument or checkout is in hand, while a precondition failure needs the invocation's
   arguments and the checkout; both refuse to run the policy and both report `usage_or_config`, which is
   why the status names usage and configuration together. Ensure it states that validation precedes
   precondition establishment, so where both hold the configuration reason is reported. Done when a new
   condition can be filed by asking what it is judged from, and when the report is deterministic where
   both apply.
10. **Section 8.2 cites both sources.** Ensure Section 8.2's `status` bullet cites Sections 6.10 and 8.6
    for the `usage_or_config` case, and its `op`/`reason`/`class` bullet states that under
    `usage_or_config` the `reason` carries the configuration reason (Section 6.10) or the precondition
    reason (Section 8.6). Done when the envelope bullet enumerates every token `reason` can hold under
    that status.
11. **Section 8.3 cites both sources.** Ensure the exit-code list's `2` entry cites Sections 6.10 and
    8.6. Done when a caller reading only the exit codes finds both ways to reach `2`.
12. **Section 8.5 governs the new tokens.** Ensure the major-stable-surface bullet lists the precondition
    reasons (Section 8.6) alongside the configuration reasons, and the `MINOR` bullet permits new
    precondition reasons alongside new configuration reasons, absorbed through the `usage_or_config`
    status, which does not change. Done when the new registry has the same versioning contract as the
    one it sits beside.
13. **The test matrix covers the three states.** Ensure Section 13.1's `Invocation contract` check
    states that a checkout with no current branch where no `branch_pattern` is configured, an illegal
    derived work-branch name, and a malformed commit identity each refuse to run the policy and yield
    `usage_or_config` with the precondition reason and null `op`/`class`. Done when the exit-code
    divergence the issue reports is a testable line.
14. **The checklist names preconditions.** Ensure Section 13.2's invocation-contract bullet lists the
    invocation preconditions alongside the result envelope, exit codes, escalation payload and
    versioning. Done when the definition of done includes refusing an invocation whose setup fails.
15. **The Conformance Statement covers added tokens.** Ensure Section 13.3's "Any reason token the
    engine adds beyond a registry" bullet names a precondition reason (Section 8.6) alongside an
    operation reason and a configuration reason. Done when an engine adding a fourth precondition reason
    has a stated place to publish it.
16. **The vocabulary registry carries the group.** Ensure `conformance/vcsx/vocabulary.json` gains a
    `precondition_reasons` group with `spec_refs` naming Section 8.6, a `note` recording that the tokens
    are carried under the `usage_or_config` status with null `op` and `class`, are part of the
    major-stable surface (Section 8.5), and MUST be documented if an engine adds any; with the three
    tokens and their conditions as entries. Ensure the `exit_codes` entry for `2` and the
    `invocation_statuses` note cite Section 8.6 alongside Section 6.10. Done when the registry
    distinguishes the two class-free reason sets by data.
17. **The template has a table for them.** Ensure `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4
    gains a `4.3 Precondition Reasons (Section 8.6)` subsection with a `| Reason | Condition |` table,
    in the shape its configuration-reason table uses, and that Section 4's lead-in names Section 8.6
    alongside Sections 4.3 and 6.10. Done when an engine filling in the template records an added
    precondition reason without improvising a table.
18. **The corpus records why it has no vectors.** Ensure `conformance/vcsx/README.md`'s "Deferred to
    later slices" list carries invocation preconditions (Section 8.6), with the reason — the derivation
    and the identity are judged against a real checkout by a real backend, so no vector file supplies
    the input — and a pointer to the `precondition_reasons` group in `vocabulary.json`. Done when the
    absence of vectors for a new registry is stated rather than inferred.

## Cross-cutting sync

`conformance/vcsx/vocabulary.json` (Step 16), `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Step 17), and
`conformance/vcsx/README.md` (Step 18).

Section 6.10 needs no edit beyond being cited from Section 8.6: its registry, its conditions and its
`Implementation-defined` multi-condition rule are unchanged, and the precedence between the two
registries is stated in Section 8.6 rather than duplicated.

Section 8.4 needs no edit: `escalation` is present exactly when the status is `needs_caller`, and a
precondition failure is `usage_or_config`, so it carries none.

Section 4.3 needs no edit: no operation reason is added, and Step 8 keeps the boundary from the other
side.

The `SPEC.md` cross-cutting sections named in `CLAUDE.md` are untouched; this decision changes
`VCSX-SPEC.md`, whose counterparts are Sections 13.1 and 13.2, handled in Steps 13 and 14.

## Anchor changes

None removed or renamed. Added: Section 8.6 "Invocation Preconditions" (a new section title) and three
reason tokens — `no_current_branch`, `work_branch_invalid`, `identity_invalid`.

`branch_pattern` keeps its spelling; only its optionality and default are stated.

## Out of scope

- **A `status` that succeeds on a detached HEAD**, reporting the detachment in its outputs rather than
  refusing. Recorded in `Background.md` as the reconsideration trigger; it would narrow the precondition
  to the entries that write.
- **`fail`'s envelope.** Still open from decisions 0059 and 0060: an explicit `do = "fail"` on a
  `done`-class trigger yields `status == "error"` with no `error`-class result, and settling it needs a
  prior answer to what `fail(reason)`'s argument is. It is adjacent — another envelope with no result to
  report — but its blocker is unchanged.
- **A behavior vector for the precondition envelope.** A precondition needs a checkout and the
  invocation's arguments; it belongs with the plugin behavior `conformance/vcsx/README.md` already
  defers.

## Status

Applied to `VCSX-SPEC.md` (Sections 6.3, 8.2, 8.3, 8.5, 8.6, 13.1, 13.2, 13.3),
`conformance/vcsx/vocabulary.json`, `conformance/vcsx/README.md`, and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.
