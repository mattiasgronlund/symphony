# Background — 0190 A policy source the implementation does not support

## Context

Reported from `symphony-rs` as issue #191, split out of #189 (decision 0189) at that thread's
suggestion.

`vcs.policy_source` is typed `policy_branch` | `target_branch`, default `policy_branch` (Sections
6.4, 9.7). Section 15.4 makes the second value an operator's choice: "An operator MAY set
`vcs.policy_source = "target_branch"` and accept exactly that". Section 6.3's reason table has no
row for either of two configurations:

1. **A value outside the type**, for example a misspelt `policy-branch`. Nothing says whether it is
   refused or read as the default.
2. **A value inside the type that the implementation does not implement.** `symphony-rs` declines
   `target_branch` (its decision 0011 R113). It refuses both cases at configuration validation, with
   a typed error outside the table, so neither refusal has a token anyone can branch on.

## What the text required before this decision

The only conformance text for the mode is the `vcs.policy_source` item in Section 18.1.4 (VCS
Engine), listed under "REQUIRED for Conformance". It states how both modes behave. So declining
`target_branch` was non-conforming, and the MAY in Section 15.4 belonged to the operator alone.
`symphony-rs` agreed on the thread: R113 had been marked `not raised` on the grounds that the spec
was clear, and what the spec clearly said was that it did not conform. Allowing an implementation to
decline is therefore a change, not a reading.

What supporting the mode costs Symphony was checked against the text. The engine already implements
both modes: `policy_source` is an engine argument with each mode's semantics stated in
`VCSX-SPEC.md` Section 8.1. Symphony's own part is the mode-dependent rules:

- the `policy_branch` requirement in check 3;
- the two policy-branch refusals: a configured `policy_branch` equal to the resolved target, and a
  per-issue target naming the policy branch;
- Section 9.7's third target source dropping out, with a target then REQUIRED from the issue or from
  `vcs.base_branch`;
- host-side hook units read from the target instead of the policy branch (Section 15.4).

## The failure paths

- **Reading a misspelt value as the default** puts an operator who asked to leave the default trust
  model under it, and nothing reports it. The operator believes host-side Way of Working is read
  from the target, while it is read from a branch they may not have configured to be safe. This is
  the worst outcome of the gap, because it is silent.
- **Judging the mode after check 3** reports the wrong cause. An operator who writes `target-branch`
  and no `policy_branch` gets `missing_vcs_field`, which tells them to add a branch they deliberately
  do not want. That happens because check 3's required set depends on the mode, and a mode that
  cannot be honoured leaves the set undefined.
- **Judging the mode after the whole predicate,** where `symphony-rs` has its guard today
  (`crates/symphony-config/src/validate.rs:553-574`), reports a later check's token instead. For
  example, a misspelt mode with no `tracker.kind` reports `missing_tracker_kind`. A check whose
  required set ignores the mode cannot see this. That is why `symphony-rs`'s check 3, which skips
  the branch requirement under any mode but `policy_branch`, would pass the first ordering vector
  with the guard still misplaced.

## Decision

**An implementation MAY decline `target_branch`.** Whether it supports the mode is
`Implementation-defined`, and an implementation MUST document it, in a row of
`CONFORMANCE-STATEMENT-TEMPLATE.md`.

- An implementation that supports the mode MUST behave as Sections 9.7 and 15.4 state.
- An implementation that declines it MUST refuse it at dispatch preflight.
- `policy_branch` is always supported.
- The Section 18.1.4 item is scoped to an implementation that supports the mode.
- The engine is unaffected. Declining is Symphony choosing not to pass the mode, not the engine
  lacking it.

The precedent is `tracker.kind`: check 3 there reads "names a kind the implementation supports", and
`unsupported_tracker_kind` refuses the rest. The case for declining is stronger here. An
implementation that cannot be configured into `target_branch` makes a guarantee anyone can check
from outside: no configuration puts the trust root on a branch the service merges into. A deployment
shared by several teams may want exactly that, and requiring both modes would make the guarantee
impossible to offer.

**One token, `unsupported_policy_source`, covers both cases:** "`vcs.policy_source` names a policy
source the implementation does not support".

- A value outside the type is refused, never read as the default. "Unknown keys SHOULD be ignored"
  (Section 5.3) is about keys and does not reach values, and the text now says so where the check
  is stated.
- One token rather than two, because two only help if a monitor would act differently on each, and
  it would not: in both cases the operator fixes the value. The operator-visible error names the
  value, which tells the operator which case they are in. `unsupported_tracker_kind` covers the same
  pair for `tracker.kind`.

**The new row is judged before `missing_vcs_field`**, between it and `invalid_repository_key`. It is
judged per `repository` entry, after resolution against the orchestrator level (Section 5.3.7), like
check 3. The table's stated order, "then each entry's resolved `vcs`", gains the reason: the policy
source is read first because it fixes which fields check 3 requires.

**The corpus carries the declared set as an input.**

- `config-preflight.json`'s `given` gains `supported_policy_sources?`. This is what the
  implementation's Conformance Statement declares, and an absent field means `["policy_branch"]`.
- A vector is run against its own set, never skipped. The predicate is a pure function of what the
  vector gives it, exactly as `descriptor` already is. The file's own description already says a
  vector "may name a third kind to exercise that path without asserting the extension is Core".
- The corpus checks that the predicate answers correctly for a given set. The Conformance Statement
  row records the set the implementation actually offers. A vector cannot check the second, so it
  does not try.

`symphony-rs` checked what the rule costs it. The harness calls the pure predicate
(`crates/symphony-conformance/src/lib.rs:240`), not the runtime type, which keeps `policy_branch` as
a non-optional `String` (`validate.rs:142`). The product passes `["policy_branch"]`, and the new row
refuses `target_branch` before that type is built. So passing the `target_branch` vectors means the
harness gains a parameter, not that the product gains the mode.

Vectors, on top of 0189's:

- **Revised:** 0189's `valid-target-branch-mode-without-policy-branch` states
  `["policy_branch", "target_branch"]` and stays valid.
- **New:**
  - `unsupported-policy-source-declined`: `target_branch` under `["policy_branch"]` →
    `unsupported_policy_source`.
  - `unsupported-policy-source-outside-type`: `policy-branch` (misspelt), with a `policy_branch`
    present → `unsupported_policy_source`, not valid.
  - `order-policy-source-before-vcs-field`: a misspelt mode and no `policy_branch` →
    `unsupported_policy_source`. This pins the row against the one immediately after it.
  - `order-policy-source-before-tracker-kind`: a misspelt mode and no `tracker.kind` →
    `unsupported_policy_source`. This pins the row against a later check that ignores the mode, and
    is the vector that catches a guard placed after the whole predicate. `symphony-rs` proposed it.

## Options considered

- **A. Require both modes; the MAY is the operator's.** The steelman: portability. A configuration
  valid on one conforming implementation is valid on all of them, and an operator never has to ask
  which modes an implementation offers. It loses because the cost of declining is a refusal at
  startup with a stable token, not silent breakage. Requiring the mode also removes a security
  property some deployments choose on purpose.
- **B. Two tokens: `invalid_policy_source` for a value outside the type and
  `unsupported_policy_source` for a declined mode.** The steelman: a monitor could tell a typo from
  a capability gap without parsing a message. It loses because the operator's remedy is the same,
  fixing the value, and the error already names the value. `unsupported_tracker_kind` is the
  precedent of one token over the same pair.
- **C. Judge the mode after the whole predicate,** as `symphony-rs` does today. The steelman: it
  keeps the mode check separate from the table's order and from check 3. It loses on the failure
  paths above, because a later check reports a cause the operator does not have.
- **D. Skip a vector whose declared set differs from the implementation's.** The steelman: a
  decliner then never answers for a set containing `target_branch`, which is dead code in its
  product. It loses because check 3's conditional is exactly what the `target_branch` vector pins,
  and skipping would leave that conditional untested in every decliner's corpus.
- **E. Require `supported_policy_sources` on every vector.** The steelman: it is explicit, and no
  harness can apply the wrong default. It loses because the file treats optional inputs as defaulting
  when absent (`base_branch_allowed?`, and 0189's `policy_source?`), and because `["policy_branch"]`
  is the smallest set, so the default makes no claim about the optional mode.

## Not done here

- **An engine-side sentence for an out-of-type `policy_source`.** `symphony-rs` checked its engine:
  `vcsx` decodes `--policy-source` into a closed enum and reports a value outside it as
  `arguments_unreadable` (`crates/vcsx-cli/src/encoding.rs:734-736`, `main.rs:92-99`). That is a
  natural reading of `VCSX-SPEC.md` Section 8.6's "could not be decoded in the encoding the engine
  published". Symphony's preflight refuses the value before any invocation anyway. A second engine
  reading Section 8.6 differently is the trigger to add the sentence.

## Review findings

- **An ordinal reference, written one decision earlier.** 0189 called the `vcs` fields check
  "Section 6.3's third check" in four places. This decision inserts a check ahead of it, which
  would have left all four pointing at the wrong check. Decision 0002 keeps plans off positional
  addresses for this reason, and the same failure reached the normative text because nothing
  applies that rule to the spec's own cross-references. Plan review caught it before the first
  edit, and step 14 names the check by what it checks. It is the first recurrence noted of this
  shape in the spec text, not a repair reproducing an earlier one.

## Reconsideration triggers

- A third policy source is added. Whether the declared set needs a minimum beyond `policy_branch`
  would then need restating.
- Operators report configurations that fail to move between implementations because of the mode.
  That is the portability cost option A names arriving in practice.

Relates to 0189 (the policy branch in check 3, and the vector this decision revises), 0164
(Section 6.3's reason table), and 0128 (template rows).
