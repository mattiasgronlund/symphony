# Background — 0126 A section cannot supply the value that selects it

## Context

Issue #74. `VCSX-SPEC.md` Section 6.10 selects a `[[branch]]` section by the resolved base branch —
"the section applies where the resolved base branch (Section 6.4) starts with its value" — and admits
every top-level key inside a section: "Any key the top level carries MAY appear under a section".

`[base]` is a top-level table and is what resolves that branch. So is `[scope]`, whose
`branch_pattern` fixes the work-branch name that `[base] resolve = "by_prefix"` selects the base
from. The selector depends on values the selected section may change.

## What the defect does

Two circuits, one direct and one through the work branch.

Resolve the base from the top level and section A applies. Apply section A's `[branch.base] branch`
and the base is a different branch, which may select section B, or none. Under `by_prefix` the loop is
one step longer: a section's `[branch.scope] branch_pattern` changes the work branch, which changes
the base, which changes which section applies.

Nothing refuses either. Section 6.11 has `duplicate_branch_section` for two sections with the same
`match` and `base_unresolvable` for a `by_prefix` map with no empty-prefix default; neither names this.
Section 6.10's own "Resolution is by **longest prefix**, and exactly one section applies" is a property
of the prefix comparison and says nothing about which base to compare against, and Section 6.4
describes base resolution without reference to `[[branch]]` at all — so neither section knows the other
is upstream of it.

The consequence is two conforming engines dispatching operations against different branches from one
document, which is what Section 6.10 closes by claiming it avoids: longest-prefix-wins was chosen
because it "settles it by construction rather than by a precedence rule an implementation could read
differently". That argument settles which section wins and not what the sections are compared against.

## The shape is one this repository has already repaired once

Issue #51 was `policy_source = "target_branch"` resolving the base from `[base]`, inside the document
the base was what located. The repair cut the circuit: under that mode "every key here — `branch`,
`resolve` and `prefixes` alike — sits in the document the base is what locates", and Section 6.4
supplies nothing.

This is the same defect one level in — not the document the base locates but the *section of it* the
base selects — and the argument transfers unchanged: a value named inside a scope cannot select the
scope it is read from. Naming that as a recurrence is the useful part. The first repair was stated
over the document, so it did not reach a construct that carves the document into scopes, and a repair
stated over the general form would have.

## Decision

Refuse a `[[branch]]` section that carries `[base]` or `[scope]`, at validation, with a reason of its
own: `branch_section_selector_key`.

Total, checkable from the document alone, and consistent with the posture Section 5.4 and Section 6.11
take everywhere else — a policy in which two things could both apply is refused rather than
disambiguated by a rule an implementation could read differently.

A reason of its own rather than `malformed_policy` because the repair is specific and nameable: move
the key to the top level, or express the variation another way. `malformed_policy` is what Section
6.11 reserves for "a well-formedness failure no other condition in the table names", and this
condition has a name.

## What it costs, stated rather than left to be discovered

A repository cannot give a release track its own base or its own branch-name pattern through a
`[[branch]]` section. That is a real loss and it is narrow: Section 6.10's worked example — a
`release/` track that keeps individual commits through `[branch.messages.squash]` — is untouched, as
is every hook, edge, message and task key, all of which are downstream of selection.

The variation the refusal blocks is also the one that was never coherent. A repository wanting a
different base per track expresses it with `[base] resolve = "by_prefix"` at the top level, which is
the mechanism that exists for exactly that and which resolves in one pass.

## Options considered

**An explicit two-phase resolution.** Resolve from the top level, select the section, re-resolve with
the section merged, and refuse only where the second pass selects a different section. Steelmanned,
and it is the option that gives up nothing: it keeps the feature's full expressiveness, refuses
exactly the documents that are actually circular rather than every document that could be, and a
repository whose section sets a base that still selects that same section is admitted — which is the
common case for someone reaching for the key at all.

It loses on what a reader has to hold. The refusal becomes a property of a fixpoint rather than of a
key's presence, so "is this policy valid" stops being answerable by looking at it. Section 6.11's
five-input rule stays satisfied in the letter and not in the spirit: validation would still read only
the document, and would read it twice with a comparison between. And the two-pass rule is one an
implementation can get subtly wrong in a way the one-pass rule cannot — which is the same argument
Section 6.10 makes for longest-prefix-wins over a precedence rule.

**Fix the selector to the top level and let a section's own copies apply downstream.** No new refusal,
schema unchanged. It loses because one key would mean two things depending on where it is read — the
top-level `[base]` selects and the section's `[base]` does not — which is precisely the split Sections
6.5 and 6.6 went out of their way to *remove* when they made execution context follow the artifact
rather than a key. Reintroducing it for base resolution would be moving in the opposite direction from
the document's own recent history.

## Reconsideration trigger

Reconsider if a matcher is added that does not depend on the resolved base. Section 6.10 anticipates
one — "a later decision adding another — a glob, say" — and a matcher keyed on something else would
make `[base]` inside a section harmless for that matcher while remaining circular for `prefix`. The
refusal is stated over the keys rather than over the matcher, so it would then be refusing something
that had stopped being a circuit.

## Relationship to other decisions

It is the recurrence of the defect issue #51 and decision 0101 repaired, found in the construct that
carves the policy document into scopes. It takes `[[branch]]` sections and `by_prefix` resolution as
given and constrains only what may appear inside a section.
