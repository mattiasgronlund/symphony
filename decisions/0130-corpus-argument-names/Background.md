# Background — 0130 The corpus names what an algorithm takes; the contract names what a caller sends

## Context

Decision 0129 removed the from-context after issue #77 observed that
`conformance/vcsx/vectors/match-edge.json` supplied a `from_context` input the invocation contract
never carried — and that this was the *second* time a vector file had done so, #68 having found
`policy-validation.json` supplying `consumer_capabilities` for an input `VCSX-SPEC.md` Section 8.1 did
not define. The issue named the mechanism rather than the two instances:

> the corpus was written from what the matching and validation algorithms *take*, and `§8.1` was
> written from what a caller *sends*, and nothing reconciles the two lists.

The user authorised sweeping the whole corpus against Section 8.1 in the same branch rather than
filing it (decision sheet `vcsx-from-context`, version `13ce1d6b`). This decision is that sweep and
what it found.

## The sweep

Every `given` field name across `conformance/vcsx/vectors/*.json`, counted per file, taken after
0129's removals:

```text
base                 base-resolution.json 13
bound_units          policy-validation.json 8
consumer_capabilities policy-validation.json 38
decisive             compose-envelope.json 14
edges                match-edge.json 19
ending               compose-envelope.json 14
engine_version       policy-validation.json 38
entry                base-precondition.json 12, compose-envelope.json 14, identity-precondition.json 12
fail_reason          compose-envelope.json 5
policy               base-precondition.json 12, identity-precondition.json 12, policy-validation.json 38
policy_branch        policy-validation.json 2
policy_source        base-precondition.json 12, base-resolution.json 4
precondition_reason  compose-envelope.json 3
status               exit-codes.json 5
supplied_base        base-resolution.json 4
trigger              match-edge.json 19
work_branch          base-resolution.json 13
```

Checked against Section 8.1's two lists — the arguments and the consumer-configuration keys — that
sorts three ways.

| Field | Verdict |
|---|---|
| `bound_units`, `policy_branch`, `policy_source` | Section 8.1 arguments, spelled correctly. No change. |
| `entry`, `policy`, `engine_version`, `work_branch`, `base`, `trigger`, `edges`, `status`, `ending`, `decisive`, `fail_reason`, `precondition_reason` | Not Section 8.1 arguments — entry points, the policy document, engine-held or engine-derived values, and envelope fields. No change. |
| `consumer_capabilities`, `supplied_base` | **Defects.** Both name a Section 8.1 input under a spelling Section 8.1 does not use. |

## What the defect does

Section 8.1 fixes the obligation itself: *"Exact argument encodings are `Implementation-defined` and
MUST be documented; argument **names** for shared concepts MUST match this specification."* A vector
file is not an engine, so it does not violate that clause directly — but
`conformance/vcsx/README.md` states what it is:

> **`VCSX-SPEC.md` governs. This file is derived.** […] Where this file and `VCSX-SPEC.md` disagree,
> the specification is right and this file is a bug.

and what it is for: an implementation "generates or checks its reason enum […] from this file, so a
token change upstream becomes a build failure rather than a silent behavior change". A derived view
that renames what it derives defeats that in the one direction it is supposed to defend. A runner
executing these vectors against a real engine has to bind `consumer_capabilities` to *something*, and
the something is `effectable_actions` — a mapping the runner author invents, in the same act the
corpus exists to make unnecessary.

**`consumer_capabilities`** is Section 8.1's `effectable_actions` under an older name: the same three
consumer-effected actions (`create_task`, `set_state`, `notify`, Section 5.2), the same semantics, the
same empty default, feeding the same `set_state_unbound` refusal. Decision 0121 introduced the
argument name in response to #68 and renamed `bound_units` alongside it — and left this one on the
pre-0121 spelling, in the very file 0121 was repairing, where the two now sit eight lines apart with
one reconciled and one not. It appears in all 38 vectors and in the two notes that gloss it, one of
which mentions both names in a single sentence.

**`supplied_base`** is the milder instance and turns out to be the more interesting one. It mirrors
Section 12.4's `resolve_base` pseudocode, which reads:

```text
function resolve_base(work_branch, base_config, remote, policy_source):
  if policy_source == "target_branch":
    return { branch: supplied_base,          # the invocation's, else the consumer
                                             # configuration's; base_config is not read,
```

`supplied_base` is not a parameter of that function and is not bound anywhere in it — it is a free
name the body reads, glossed in a comment as "the invocation's, else the consumer configuration's",
which under Section 8.1 is `base_branch`. So the corpus did not mirror an algorithm's local; it
mirrored an algorithm's *gap*. `base-resolution.json`'s own notes already describe the value as the
invocation's, so the file claims to model the caller's input and only the spelling disagrees.

## Decision

Rename both to Section 8.1's spellings — `effectable_actions` and `base_branch` — in the vectors and
in the notes that gloss them. Repair Section 12.4's signature to bind `base_branch` rather than read
an unbound `supplied_base`, so the algorithm, the contract and the corpus agree on one name.

Section 8.1 is otherwise **already correct and unchanged**. Recorded explicitly because the natural
reading of a decision in this branch is that a contract gap was repaired, and here there is none: the
contract said the right thing and two derived artifacts said something else.

## Options considered

**Leave the algorithm's own parameter names and say so in the notes.** This is the honest steelman for
`supplied_base` in particular, and it has a real principle behind it: a vector file models a
*function's* inputs, the reference algorithms are that function's specification, and forcing the
corpus onto the invocation contract's vocabulary would misname any value that genuinely is an
algorithm-internal one. `base-resolution.json` exercises `resolve_base`, not an invocation, and a note
saying "these vectors name the algorithm's parameters" would be true and cheap.

It loses on the facts of this case rather than on the principle. `supplied_base` is not one of
`resolve_base`'s parameters — it is unbound in the pseudocode — so there is no algorithm vocabulary to
be faithful to; the choice is between Section 8.1's name and no name at all. And the file's own notes
already call the value "the invocation's", so the vectors have already made the claim that this models
a caller's input. The general principle survives for a case that actually presents it: see the
reconsideration trigger.

**Rename `consumer_capabilities` and leave `supplied_base`.** Repairs the instance with a
demonstrated cost — 38 vectors, a name a runner must map — and leaves the four-vector one. It loses
because the mechanism is the subject: a rule with an exception the reader must judge is the rule that
produced this, decision 0121 having renamed one field and not its neighbour in the same file.

## The standing check

The three instances are #68's `consumer_capabilities` (a missing argument), #77's `from_context`
(another missing argument), and this one — a field whose input the contract *does* carry, under
another name. The first two were gaps in the contract and were repaired by adding or removing surface;
this one is a gap in the *reconciliation*, which is why it needs a decision of its own rather than a
third repair of the same kind.

Nothing mechanical connects the two lists, and this decision does not add tooling — the corpus is
data, and a checker for it is a program some implementation would have to own, which is the boundary
`conformance/vcsx/README.md` already draws for fault-injection vectors. What it adds is a rule where a
vector author reads it: a `given` field naming an invocation input MUST use Section 8.1's spelling.
That is the shape of repair decision 0128 chose for the same class of problem — it extended
`CLAUDE.md`'s cross-cutting sync list rather than generating the template — and 0128's reasoning
applies unchanged: fixing the instances and leaving the mechanism is what lets the next one land.

## Reconsideration trigger

A vector file that legitimately needs to model an algorithm-internal value the invocation contract has
no name for — a `resolve_base` local, an executor traversal counter, a value the engine derives and
never receives. The rule as written would force it onto a Section 8.1 spelling that does not exist,
which is worse than the drift it prevents. The answer then is a note in that file saying the field
names an algorithm's parameter deliberately, not a second spelling for a contract argument; the rule
should gain that exception when a real case presents it, and not before.

## Finding not repaired: Section 12.4's default-mode path

Repairing `supplied_base` exposed a second, larger gap in Section 12.4 that this decision deliberately
does not touch. Section 8.1 gives the base three sources, most specific first — the invocation's
`base_branch`, the consumer configuration's, then `[base] branch` (Section 6.4) — and Section 12.4
models that precedence only under `policy_source = "target_branch"`. Its default-mode path reads
`base_config.branch` alone, so the pseudocode as written resolves a base the invocation did not ask
for whenever an invocation supplies one under the default mode.

That is a defect in the reference algorithm rather than in a name, it is not what this sweep was
scoped to, and repairing it means deciding how the three-source precedence is expressed in
pseudocode — a question with its own answer. Recorded here so it is assignable rather than noticed and
lost. The renaming this decision does makes it *more* visible, not less: after it, Section 12.4 takes
a `base_branch` parameter that its own default-mode path never reads.

## Scope of the sweep

Stated so a later reader does not over-read the clean result: this was a sweep of `given` field
*names* against Section 8.1. It is not a semantic audit of the vectors, it does not check that a
field's *values* are well formed, and it does not cover `expect` fields at all.
