# Background — 0141 The operation no entry point named and no policy could dispatch

## Context

Issue #101 was filed by the `symphony-rs` build against `VCSX-SPEC.md`. Decision 0134 closed the
operation set and put `load_policy` in it. That removed the ground on which a `[policy]` edge naming
it was refused — Section 6.11's `unknown_operation` reaches "an operation the engine does not define
(Section 4.1)", and Section 4.1 defines it — and put nothing in its place.

`load_policy` is also the one member of the set whose result raises no `<op>:<reason>` trigger and
carries no Section 4.3 registry entry. `conformance/vcsx/vocabulary.json` says the same from the
registry side, in its own `operations` note for the token: "`config_reasons` carries them and
`reasons` has no `load_policy` entry".

So this validates:

```toml
[[policy.edge]]
on = "push:non_fast_forward"
do = "run_op"
op = "load_policy"
```

It parses, its `on` is a known trigger, its `do` is a known action, and its `op` names an operation
Section 4.1 defines. Section 6.5 constrains an edge's `on` and requires `op` to be present; it says
nothing about which operation `op` may name.

## The failure path

When that edge fires, the `push:non_fast_forward` outcome is **disposed of** by a `run_op` whose own
result cannot take its place in the machine. Section 5.4:

> An outcome is **disposed of** by an action that ends the flow — `escalate`, `park`, `fail`
> (Section 5.6) — or by a `run_op`, whose own result takes its place in the machine.

The `load_policy` result raises no trigger, so no edge matches it, and it carries no proto class, so
none of Section 5.4's three built-in defaults — `fail` for `error`, `escalate` for `needs_caller`,
continue for `done` — has anything to key on. Section 5.4 does not say what happens next, and the
flow carries on past a push that did not land.

Three implementations are faithful to the text and mutually incompatible: **refuse the edge at
validation** (but with which reason? `unknown_operation` is false as its row is worded, and
`malformed_policy` names a value failing a constraint its section states, where no section states
one here); **accept, dispatch, and apply the `done` default**, so the flow proceeds past the outcome
the edge was written to handle; **accept, dispatch, and park or fail**, reading Section 5.4's MUST
as reaching a result with no class. A policy that validates on one conforming engine and is refused
by another is the defect 0134 closed the operation set to prevent — and closing it is what opened
this one: before 0134 every engine refused this edge, for a reason Section 6.11 wrote down.

`provision` is the near neighbour and shows the question is about disposition rather than about
`load_policy` alone. Section 4.1 says its "result does not re-enter the action-policy machine as an
`<op>:<reason>` trigger", the same property, and nothing refuses a `run_op` edge naming it either.
There the built-in defaults still have something to key on — Section 4.3 gives `provision` `ok`,
`unreachable` and `store_unsupported`, each with a class. For `load_policy` there is no reason and
no class, so a *successful* dispatch has no expressible result at all. That is the difference
between an odd edge and an undisposable one.

### The second defect, which changes the shape of the answer

`load_policy` is not an entry point in the prose. Section 8.1 enumerates "`ship`, `land`" and then
"`provision`, `status`, `diff`, `commit`, `integrate`, `push`, `create_pr`, `merge`, `pull`,
`await_checks` — individual operations (Section 4.1)". That is **ten**; Section 4.1 defines
**eleven**. So under the documents as written, the only way to reach `load_policy` is the `run_op`
edge this issue asks to refuse — refuse it and the operation becomes unreachable, while Section 4.1
says "the consumer holds it and supplies it to every subsequent invocation", which presupposes an
invocation that produces it. Refusing without the entry point is worse than the status quo.

Two artifacts already disagree with the enumeration. `VCSX-CONTRACT.md` Section 6 introduces the
`run_op` operation list with "The named operations are:" and puts `load_policy` first. And
`conformance/vcsx/vocabulary.json`'s `entry_points` group carries **thirteen** entries with
`load_policy` among them, while its `spec_refs` cite `VCSX-SPEC.md` Sections 7 and **8.1** — the
section that names ten. The registry does not merely disagree with the prose; it cites the prose it
disagrees with as its source, against `conformance/vcsx/README.md`'s "Every entry is read from the
sections its `spec_refs` cite; nothing here is invented". So the Section 8.1 half is prose catching
up with two artifacts rather than a decision.

That drift is invisible to the tooling in both directions: `scripts/validate_spec_consistency.py`
check 6 walks two closed groups — `operations` and `lifecycle_positions` — and `entry_points` is not
one of them, so nothing compares the group against the enumeration it cites.

## Decision

Six parts, one decision, because a policy that may name the operation as a trigger would otherwise
survive the decision that refused it as an action.

1. **Section 8.1 enumerates `load_policy`.** The prose catches up with `VCSX-CONTRACT.md` Section 6
   and the registry. Its four Section 6.1 failure names already fit there: they are
   `usage_or_config`, an invocation result rather than an operation one.
2. **A `run_op` naming an operation that runs outside the action-policy machine is a configuration
   error**, with a new reason token — `operation_not_dispatchable`. The property is marked once in
   Section 4.1 and covers `load_policy` and `provision` today.
3. **The registry carries the property as a flag** on `operations` entries — `policy_dispatchable`,
   beside the existing `read_only` and `lifecycle_position` — so an engine that generates from the
   corpus inherits it.
4. **Section 5.1's parenthetical extends to both operations.** It reads "`provision` has no position
   and raises no trigger (Section 4.1)" today, so `on = "load_policy:#error"` validates as a
   permanently dead edge. Extending it puts that under the existing `unknown_trigger` row and needs
   no second token.
5. **Section 4.3's universal claim is scoped to the operations the machine can dispatch.** "Every
   operation therefore has at least one `done` reason and at least one `error` reason" and the
   `(any)` rows' "defined for every operation" both stop being false for `load_policy`. This closes
   0134's own recorded-not-repaired finding by replacing a count with the invariant — the same move
   0134 made for `blocked` and `hook_unanswered`.
6. **Section 8.6's `git_access` paragraph narrows.** It contemplates "an entry outside the set that
   reaches such an operation through a `run_op` edge", and lists `provision` among the reaching
   operations. Once no `run_op` may name `provision`, that scope is `integrate`, `push` and `pull`,
   or the paragraph reads as contemplating an edge validation now refuses.

And, resolving what the entry-point blessing was blocked on:

7. **A policy-surface pin, as a fingerprint.** OPTIONAL, default unset; `load_policy` issues it; an
   invocation supplying one is refused where the surface it validated does not match. Section 4.1's
   sentence is rewritten with it.

### Which property the refusal is stated over

Not "raises no `<op>:<reason>` trigger", and not "carries no lifecycle position" — `await_checks`
has no position and is plainly dispatchable. The property is **an operation that runs outside the
action-policy machine**, and it is a consolidation rather than a new concept: the category is
already carved twice, at Section 6.11 ("`provision` is validated from those inputs **less the
first**") and Section 6.1 ("`provision` is the one entry point that runs where no policy could be
read"). `load_policy` is the operation that produces the document those exemptions are about. They
are the bootstrap pair.

Stated that way it reaches `provision` by the document's own argument rather than a new one. Section
4.1 denies `provision` a trigger because a gate on it "would be absent on the invocation that
creates the checkout and present on one that refreshes it — a trigger that sometimes exists, which
Section 5.4's one-edge-per-trigger rule is written to prevent". A `run_op provision` edge has
exactly that property: it was read out of the repository the operation obtains, so it can only ever
fire on the refresh path and never on the create path. The same sentence refuses the edge. (This is
a behaviour change for the reporting build, which accepts such an edge today precisely because
`provision` has reasons; it reached the same answer from the disposition side while this reasoning
reached it from the trigger side.)

### Why a new token rather than widening `unknown_operation`

Section 6.11's own separation rule is "a repair a reader can act on", and the repairs differ:
`unknown_operation` says fix the spelling; this one says dispatch it from its own entry point.
`malformed_policy` does not fit either — the same paragraph reserves it for an argument that is
*absent*, while here the argument is resolved and recognized. The token sits **inside**
`config_reasons`, so it creates no Section 13.3 obligation and owes no Conformance Statement row
(the decision 0128 trap does not fire). It owes `conformance/vcsx/vocabulary.json`, a Section 13.1
row, a Section 13.2 line, and a `policy-validation.json` vector.

### Why the property has to live in the registry, not only in Section 4.1's prose

This is the load-bearing correction, and it came from the implementation side. That engine refuses
today by reading the *generated reason table*: an operation with no `<op>:<reason>` entry cannot be
dispatched from a policy. It spells no operation name, so an upstream decision that gave
`load_policy` reasons would open the edge with no code change — which is the same
inheritance-by-property this decision is after.

But the property here is *runs outside the machine*, and `provision` has three class-bearing
reasons, so the reason table cannot express it. If the marker lives only in prose, every engine
hardcodes two operation names, and the claim that "a MINOR release adding an operation with that
property inherits the refusal" is **false in practice for exactly the engines that generate from the
corpus**: a MINOR adding a third such operation would pass their gate green while accepting an edge
the specification refuses. That is a worse failure than the one being repaired, because it is silent
and green. One flag, two refusals — it also serves part 4's trigger half, so there is no second
prose list to keep in step. It satisfies the corpus README's own discipline in the right direction,
too: the flag is a property Section 4.1's prose fixes, so the registry derives it rather than
inventing it.

## The pin: what it replaces and why the fingerprint wins

Section 4.1 says of `load_policy` that "the consumer holds it and supplies it to every subsequent
invocation, **which therefore read no repository**". Section 8.1 names no argument through which a
surface could be supplied back, and explicitly closes the other route — the consumer configuration
"carries no key `repo.policy.toml` carries" — while Section 8.6 requires the argument saying where
the policy is read from at every entry that reads one. So the sentence describing the operation's
entire purpose has no invocation shape to carry it.

**Supply-back is refused on trust, and that is not reopened.** An argument handing the engine a
surface lets a caller hand it a document no revision ever held — and that document declares the
host-side hooks Section 11's trust model exists to keep out of the working tree's reach. Section
3.2's "the consumer sources config by trust" is the property `load_policy` exists to make literally
true.

**Plain re-read** — every entry reads and validates the policy itself, `load_policy` returning the
surface for inspection — is what the reporting build ships, and it is coherent. Its cost is a
Section 13.1 row: "the policy is obtained once per unit of work through `load_policy`, and a change
to the policy source after that does not take effect until the next unit of work" becomes false. Not
everywhere, which is the part worth recording: along a **resumed chain** the row still holds,
carried by the resume token's own policy fingerprint — Section 8.1 already requires refusing a
resume "issued under a different policy", and that build compares a fingerprint of the *effective*
surface, after the `vcsx.toml` merge and the `[[branch]]` selection. Where it fails is the
**unresumed continuation**: a `ship`, a policy edit, then a fresh `land`. No token, nothing
compared, and the edit takes effect silently. The re-read does not merely leave the row stale; it
lowers a guarantee the engine already provides along resumed chains in order to describe the one
path where it does not.

**A revision pin** — the consumer holds the resolved revision, later invocations supply it, and the
engine reads and validates from the revision it resolved — is the option the row literally promises:
the invocation keeps executing the old document. It was seriously considered and loses on three
counts.

1. **A revision does not name what the row is about.** The row is about *the policy*, and the policy
   is the effective surface. Section 6.1 merges an engine-native `vcsx.toml` into the same surface
   and states **no location and no discovery rule for it at all** — only "when present, is merged" —
   where `repo.policy.toml`'s path is fixed "relative to the repository root" with
   `Implementation-defined` precedence. A revision of the repository cannot be established to cover
   a document the specification does not place in it. And a `[[branch]]` section merges over the top
   level for the branch selected by the *resolved base* (Sections 6.4, 6.10), so two invocations at
   one revision with different resolved bases execute different surfaces.
2. **Two notions of "same policy" in one document is issue #100's defect.** Section 8.1 already
   requires refusing a resume "issued under a different policy" — content identity, judged by the
   engine, with no revision anywhere in it. A revision pin adds a rival answer maintained
   separately, and the two disagree exactly where it matters: same content at a new revision, same
   revision with an edited `vcsx.toml`.
3. **A revision pin lets a caller run a policy the repository has withdrawn.** The pin's whole point
   is that the invocation keeps executing the old document. `repo.policy.toml` declares the
   host-side hooks, and Section 11's trust model rests on the operator controlling the revision they
   are read from — `policy_branch` "resolves to the copy belonging to the resolved `remote`, and
   never to a local branch of the same name", because otherwise it yields "host-side hooks chosen by
   whoever can write that checkout". Under a revision pin, an operator who removes a hook has not
   removed it: any consumer holding a pin from before the edit keeps running it, at the caller's
   discretion, and the engine cooperates. The fingerprint never executes a withdrawn document — it
   reads the current one and either runs it or refuses.

It also costs a precondition Section 8.6 cannot resolve, where a fingerprint costs none: the engine
reads the document anyway and compares what it read against what the consumer was handed.

**The chosen shape:**

- The pin is **OPTIONAL**, default unset. An invocation supplying none makes no continuation claim
  and runs whatever it reads, so a single-invocation consumer — Symphony's own `ship` — is
  untouched.
- **`load_policy` issues it**, which is what finally gives that entry point a purpose beyond
  inspection.
- **A resumed invocation needs none**: the token already carries the same fingerprint. The pin is
  that check promoted to a standalone argument for the case with no token.
- **A new precondition reason, not `resume_unusable`.** Section 6.11's separation rule again: a
  `resume_unusable` says re-invoke from the entry point; a pin mismatch says re-read the policy and
  decide whether this is still one unit of work. It sits inside `precondition_reasons`, so it owes
  `vocabulary.json`, a Section 13.1 row, a Section 13.2 line and a vector — and no Conformance
  Statement row.
- **Section 13.1's Policy-loading row states the mechanism rather than lowering it**: the surface a
  unit of work executes is fixed when the unit of work begins, and an invocation continuing one
  whose surface has since changed is refused rather than run under either document. That is a
  *stronger* row than today's and a falsifiable one, where "does not take effect until the next unit
  of work" describes a caching property no caller can observe.
- **Section 4.1's sentence is rewritten**, which it would have been under every option including the
  re-read: the clause "which therefore read no repository" is true only under supply-back. The
  consumer holds the surface for inspection and a pin for continuity, and every invocation reads and
  validates the document itself — which is what makes Section 3.2's property literal.

### The cost, not hidden

The fingerprint **refuses** where the revision pin would have proceeded. A consumer that edits its
policy mid-unit-of-work trades a silent behaviour change for a stop and a re-invocation. That is the
same trade Section 8.1 already made for the resume, in the same direction, with the same sentence
justifying it: "a refused resume costs a re-invocation from the entry point, where an accepted stale
one runs an operation the policy no longer routes."

## Why not "define the dispatch"

The report's second option — say in Section 5.4's disposition bullet what the machine does with a
`run_op` result that raises no trigger — is not merely larger; it has no coherent answer.
`load_policy`'s product is a surface a consumer holds **between** invocations, and there is no
consumer inside an invocation to hand it to. An engine that applied the freshly-read surface to the
rest of the traversal would swap the policy under a running flow, against Section 5.4's "the same
`repo.policy.toml` yields one operation flow"; an engine that discarded it would run an operation
with no observable effect and no `done` reason to report. Both are worse than the refusal, so the
two options are not a size trade.

## What was checked

At `97617c2`, against the working tree:

- `conformance/vcsx/vocabulary.json`'s `entry_points` group holds thirteen entries, `load_policy`
  among them with `"kind": "operation"`, and its `spec_refs` cite Sections 7 and 8.1. Section 8.1's
  prose names ten operations; Section 4.1 defines eleven.
- The `operations` group holds eleven entries carrying `read_only` and `lifecycle_position`, and the
  `load_policy` entry's note already states the property this decision marks in prose.
- `scripts/validate_spec_consistency.py`'s `CLOSED_GROUPS` names `operations` and
  `lifecycle_positions` only; `entry_points` is unchecked in both directions. The script reports 0
  errors and 0 warnings.
- Section 6.11's table carries twenty-two rows; none reaches a `run_op` naming a defined operation.
  Section 5.1's parenthetical names `provision` alone. Section 8.6's `git_access` paragraph names
  `provision`, `integrate`, `push`, `pull`.
- `conformance/vcsx/vectors/policy-validation.json` pins `validate_policy` with 38 vectors.

## Reconsideration triggers

- **A MINOR release adding a third operation that runs outside the machine.** The registry flag is
  what makes that inherit; if a future operation needs to be dispatchable from a policy *and* raise
  no trigger, the flag's meaning has to be split rather than reused.
- **A consumer that genuinely needs the old surface to keep executing.** That is the revision pin's
  case, and the withdrawal argument above is what it would have to answer.
- **`load_policy` gaining reason tokens.** Part 5 scopes Section 4.3's claim rather than giving the
  operation reasons; if a later decision gives it any, both the scoping and the
  `policy_dispatchable` flag need re-reading — the flag is deliberately not derived from the reason
  table, so it would not move on its own.
- **A second registry group drifting from the prose it cites.** `entry_points` is the first found;
  extending check 6 covers it, and a second instance would argue for closing every group by default
  rather than by table.
