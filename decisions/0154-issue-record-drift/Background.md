# Background — 0154 The record grew three fields and the vector that enumerates it did not

## Context

Issue #120, filed by the `symphony-rs` build against `4d610da`. Section 12.2 fixes which maps the
iteration order governs, and does it by naming the record:

> The maps this order governs are the ones a template names by path: the `issue` object, whose
> members are the fields Section 4.1.1 defines, and `metadata`.

Section 4.1.1 defines sixteen fields. `conformance/vectors/prompt-rendering.json`'s
`iterate-issue-object` vector expects thirteen keys and supplies thirteen in its `given.issue`. The
three that are absent are `assignees` (decision 0140), `project` and `team` (decision 0148) — the
two most recent decisions to touch the record, both landing after decision 0135 authored the vector.

So the document and the corpus require different things and no implementation satisfies both. A
build that follows Section 12.2 renders sixteen keys and fails the vector; a build that passes the
vector puts thirteen fields in the template context and has not implemented Section 12.2's own
sentence. The reporting build holds the three fields out of the context to keep the vector green and
says why: turning a green vector red would make "red" mean two things in its conformance ledger —
work it owes, and a vector it believes is wrong — and those have to stay distinguishable.

Issue #121 is the sibling and is answered separately: it is about a rule stated over the same
record's fields, not about the record's membership.

## Which artifact is wrong, and how the corpus answers that itself

The vector was authored as a **derived enumeration** of Section 4.1.1, and its own decision says so.
Decision 0135's `Plan.md` step 8:

> *Done when:* the vector exists with `id` `iterate-issue-object`, its `given.issue` carries every
> Section 4.1.1 field and no other, and its description records that the expectation rests on that
> field set being the normalized record's.

The vector no longer meets the done-condition it was accepted under. That is what settles the
direction without appeal to a general precedence rule: this is not two rules disagreeing, it is one
artifact that stopped tracking the thing it was written to track. `conformance/README.md` states the
precedence anyway, in its own words — "`SPEC.md` governs both artifacts. Every value is read from
the sections its `spec_refs` cite" — and states it sharply for the registry one section further
down: "Where this file and `SPEC.md` disagree, the specification is right and this file is a bug."

## The half the issue does not ask for: `given` is wrong too

The issue asks for `expect`. `given` is the half that decides whether the vector is well-defined at
all. `conformance/README.md`'s harness contract is one line — "Invoke the implementation's
realization of `function` with `given`" — and two harness styles satisfy it:

- **Mapping.** Deserialize `given.issue` into the implementation's own record type. The three absent
  fields take their empty values, the record has sixteen members, and the vector fails.
- **Verbatim.** Hand the decoded object to the renderer as the map it is. The record has thirteen
  members and the vector passes.

Every other vector in the file supplies a partial issue — `substitute-issue-identifier` gives four
keys — and none of them can tell the two styles apart, because they name fields by path and an
absent field is a field they never mention. `iterate-issue-object` is the only vector in the corpus
that iterates the container, so it is the only one whose result depends on which harness style the
implementer built, and the corpus does not say which that is.

Repairing `expect` alone therefore fixes the mapping harness and breaks the verbatim one. Carrying
all sixteen fields in `given` as well makes both styles render the same sixteen keys, which is what
the vector was for and what decision 0135's done-condition already asked for.

`branch_name` stays null in `given`, so the vector keeps pinning that a null-valued field is still a
member of the map. The three new fields are given values rather than their empty ones, which
additionally catches an implementation that puts `project` in the template context only on the path
where routing consumed it.

## Why the subset reading loses

The issue offers the other exit: Section 12.2's sentence is what moves, and a template sees a subset
of the record.

Steelmanned, it is not a silly position. `project` and `team` were added by decision 0148 as
**routing** keys — read by the orchestrator's mapping, with no evident use in an agent's prompt.
A document that exposes every field it adds to the record has committed the prompt surface to grow
with every future routing, scheduling or accounting field, each of which a repository's
`WORKFLOW.md` may then name and depend on.

It loses on the rendering contract it would have to fight. Section 12.2 renders with strict variable
checking and Section 5.5 makes an unknown variable a `template_render_error`, which Section 12.4
turns into a failed run attempt. A hidden field is therefore not invisible: it is a repository whose
template names `{{ issue.project }}` failing every dispatch, against a Section 4.1.1 whose opening
line says the record is the one "used by orchestration, prompt rendering, and observability output".
The subset would owe its own membership rule, its own dispatch-preflight check so that failure is
caught once rather than per attempt, and a reason why a template may read `description` and
adapter-owned `metadata` — free-form both — and not the name of the project the issue sits in.
There is no confidentiality gain to buy that with: the fields at issue are less sensitive than the
ones already rendered.

## The larger half: nothing was ever going to catch this

Two decisions added three fields to Section 4.1.1 and neither re-derived the vector. That is not
inattention: their `Cross-cutting sync` sections name what `CLAUDE.md` names — Sections 6.4, 17
and 18, and the Conformance Statement template — and no rule anywhere names `conformance/vectors`.

`scripts/validate_spec_consistency.py` exists for exactly this shape and says so in its own
docstring:

> a specification sentence enumerates something, a second artifact restates that enumeration, the
> two disagree, and nothing notices because each artifact is complete against itself

It did not catch this one because its six checks read the registries, the Conformance Statement
templates and the documents' own prose, and never the behavior corpus. Check 7 adds the corpus as
the third derived artifact, in the table-driven shape check 6 uses, comparing three spellings of one
set: the fields Section 4.1.1 defines, the keys `given.issue` supplies, and the keys `expect`
renders — plus the ascending code-point order Section 12.2 fixes, which the same vector claims and
nothing verified.

The honest limit is recorded rather than left to be discovered: **the table has one row, because the
corpus has one enumeration-shaped vector.** All twelve files were surveyed; every other `expect` is
a computed value, and `config-defaults.json` explicitly declares unlisted paths unconstrained, which
is the opposite of an enumeration. The table is the right shape for a check whose second instance
should not be special-cased next to the first, not evidence that a second instance exists.

A prose rule in `CLAUDE.md` instead of the check was considered and rejected on measured grounds:
decision 0128 records three consecutive decisions missing a Conformance Statement row that
`CLAUDE.md`'s working agreements already demanded in writing. A tenth bullet is the intervention
that has been measured not to work. The rule goes in the script's docstring, where the next person
editing the check will read it.

## Options considered

### Repair `expect` and stop, as the issue asks

The minimal change, and it closes the reported defect. It loses on the harness argument above: it
leaves the one vector in the corpus whose outcome depends on an unstated harness convention, now
failing for the other convention. The corpus's value is that an implementation can run it on day one
with no harness infrastructure; a vector that requires knowing which of two obvious harnesses was
meant is not that.

### The subset reading — Section 12.2 moves instead

Argued above. Rejected on strict variable checking, the preflight and membership rule it would owe,
and the absence of anything to gain.

### Treat the vector as a second rule and reconcile the document to it

Rejected outright and recorded because it is what an implementation is forced into by a green-vector
policy: `conformance/README.md` makes the corpus derived, and a derived artifact that leads produces
a specification edited to match its own restatement, which is decision 0132's drift class with the
arrow reversed.

### Special-case the check rather than table-drive it

Cheaper to write and honest about there being one instance. It loses on where the second instance
lands: a special case invites a second special case beside it, and check 6 already establishes the
table as the shape for "the membership a section closes". The cost is a table with one row, which
this file records rather than dresses up.

## What was checked

At `457877b`, against the working tree:

- Section 4.1.1 defines sixteen fields, read mechanically from its column-0 `` - `field` (type) ``
  bullets: `id`, `identifier`, `title`, `description`, `priority`, `state`, `branch_name`, `url`,
  `labels`, `assignees`, `project`, `team`, `blocked_by`, `created_at`, `updated_at`, `metadata`.
- `iterate-issue-object` expects thirteen keys and supplies thirteen in `given.issue`; the set
  difference is exactly `assignees`, `project`, `team`.
- No other vector file expects an enumeration of a set the specification fixes. Surveyed all twelve
  files' `function` and file-level `expect`: nine expect a computed scalar or list, `render_prompt`
  expects a rendered string or an error class, and `config-defaults.json` states that "paths **not**
  listed are unconstrained".
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings — the drift is
  invisible to it.
- Section 12.2's governed-maps paragraph and decision 0135's `Plan.md` step 8 are verbatim as
  quoted; `conformance/README.md`'s harness contract and precedence sentences likewise.

## Reconsideration triggers

- **A second enumeration-shaped vector.** The table's shape is paid for when it has a second row; if
  the corpus never grows one, folding check 7 back into a special case is a decision rather than a
  cleanup, and this is the record that it was one.
- **Section 4.1.1 gaining a field an implementation must not put in a prompt** — one carrying a
  credential, or personal data a deployment is obliged to minimize. That reopens the subset question
  on a ground today's fields do not supply, and it would be answered per field rather than by
  narrowing the container.
- **A harness contract that fixes whether `given` is mapped into the implementation's types or fed
  verbatim.** Pinning `given` at the full field set would then be belt-and-braces rather than the
  thing that makes this vector well-defined, and a later editor trimming it back should know which
  it was.
