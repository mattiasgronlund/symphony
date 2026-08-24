# Background — 0150 The diff a commit would record, and the identity that comes with it

## Context

Issue #110, first of two decisions; split from #102, where the template's inference was the first
half. Section 9.1's capability list is short of three capabilities the specification's own
operations, positions and examples require. This decision takes the one that depends on nothing:
`worktree_diff()`.

**The strongest form of the finding is not the derivation — it is that an engine has already had to
invent it.** The `symphony-rs` VCS backend trait carries all three capabilities under the report's
own names and shapes: `worktree_diff() -> Result<String, EngineFault>`
(`crates/vcsx-engine/src/backend.rs:554`), `read_at_source(remote, branch, path)` (`:576`),
`export_source(remote, branch, into)` (`:600`). Each arrived with that build's decision 0047, months
before the report, each carries the doc sentence "Beyond `§9.1`'s list, which is 'the minimum every
backend MUST provide, not a maximum', and published in `§13.3` for that reason", and two backends
implement them (`vcsx-plugin-git`, `vcsx-plugin-jj`). So the specification is not being asked
whether it *might* need these. It is being asked to name three capabilities an engine implementing
Section 4.1 and Section 6.6 as written has already had to invent, under names it chose, and to stop
them being published as backend extras — the divergence decision 0149's template reword covers and
this pair is the repair for.

## The gap, stated in Section 9.1's own words

Section 10.4 says what the engine supplies at the position:

> What the engine supplies at the position is the content and nothing else … the commit message and
> **the diff the commit would record** at `before:commit`, the composed title and body at
> `before:create_pr`.

Section 9.1's `diff(base_ref)` is "the branch delta against the resolved base (Section 6.4)" — a
different question, and one that answers nothing about content the VCS has not recorded.
`worktree_revision()` answers an *identity* rather than content. Nothing in Section 9.1 or Section
9.2 answers the question Section 10.4 asks.

The report argued from Section 4.1's "Each is realized through the plugin layer". **Section 9.1's
own closing paragraph is the stronger citation, because it makes the claim rather than implying
it:**

> The list is the minimum every backend MUST provide, not a maximum: **every operation Section 4.1
> defines is realizable through it**, and which operations there are is this specification's to say
> rather than an engine's (Sections 4.1, 8.5), so no engine adds one that would require more.

That is false today, in the section the repair edits.

**And this one is on the documented happy path.** Section 6.5's own example policy prints the edge:

```toml
[[policy.edge]]
on = "before:commit"
do = "run"                     # run a hook
hook = "scan-content"          # a hook name (Section 6.6)
```

and Section 10.4 is what the engine supplies when that fires. So the capability list is short of
something every engine that supports the specification's canonical example needs. That is why this
half is separable from the other two, which are reachable only through `load_policy` and a
`[hooks.engine]` declaration, and why it is a defect in the list rather than an extension of it.

## The load-bearing half: the identity has to come with the diff

This is not in the report, and it is a **live defect** rather than a gap the document merely leaves
open.

Section 10.4 closes with:

> The title and body scanned at `before:create_pr` are the values the operation writes: the engine
> composes them once (Section 10.2) and recomposes nothing between the scan and the write, so that
> position needs no identity to condition on **where the other two do** (Sections 6.6, 9.1, 9.2).

That asserts `before:commit`'s scanned content is covered by `expected_worktree`. It stops being
true the moment the diff is a second read of the tree: an engine that reads the diff at T₁ and takes
`worktree_revision()` at T₂ will, for a tree that moves in between and then holds still, match the
identity and produce `commit:ok` over content the scan never saw. The gate then gated the wrong
bytes — the failure Section 6.6 states as "a gate is only a gate if what it inspected is what
proceeds", and the one `expected_worktree` exists to prevent.

The `symphony-rs` build has exactly that pair, and its own comments show how easily it is missed by
someone holding the capability in their hands: `worktree_diff()` at `crates/vcsx-engine/src/op.rs:
1185`, while the gate's content is composed and **before** the position runs; `worktree_revision()`
at `:1703`, *inside* the operation, after it. That build's trait doc pins the *adjacent* property —
`worktree_diff` and `is_dirty` must not disagree, because "a backend whose two answers could
disagree would let a gate inspect a tree the `commit` then captures differently"
(`backend.rs:546-549`) — and it does not reach this one.

### A sequencing rule is one hole short of enough

The obvious repair is an ordering: the identity is taken no later than the diff. It closes the T₁/T₂
case and leaves one open.

Take the identity at T₁ and the diff at T₂ > T₁. `worktree_revision()`'s contract is that the
identity "MUST differ whenever a `commit` would capture different content" — it is stated over
*content*. So a tree that moves to B after T₁ and **moves back** to A before the capture matches
`expected_worktree` exactly, and the scan inspected B's diff while A is committed. An editor writing
a file and reverting it, or a formatter run twice, reaches it. No ordering rule can see it, because
the identity is by design blind to a round trip.

### The paired return, and the two objections it answers

The form without the hole makes the binding the backend's, because the backend is the only party
that can bracket one read:

> `worktree_diff()` answers the diff a `commit` would record **and** the identity
> `worktree_revision()` answers for the tree it read. The engine supplies that identity as
> `expected_worktree` for the `commit` the position gates.

One read, one pair, and Section 6.6's "a gate is only a gate if what it inspected is what proceeds"
becomes a property of the capability rather than of an engine's call order. `worktree_revision()`
stays for the dispatch where no diff is taken — a `commit` reached without a `before:commit` scan —
so nothing is retired.

**The honest objection to it was that the capability answers two things, which Section 9.1 has no
precedent for.** That objection does not hold, and the section carries both a precedent and an
assumption:

- **The precedent.** `ahead_behind(base_ref)` answers two values from one call, and for exactly this
  reason: Section 4.1 reports `ahead`/`behind` as a pair against the resolved base, and two numbers
  taken against two different reads of the relationship are not a state anything held. Section 9.1
  prints it in the same bullet as `current_branch()` and `is_dirty()` under "Each answers its
  value", so a compound answer is already inside what that sentence covers.
- **The assumption.** Section 9.1's `commit` bullet already binds the identity to a read at the
  position: "`expected_worktree` is the identity `worktree_revision()` answered **when the working
  tree was read at `before:commit`** (Sections 6.6, 12.2)." That sentence describes one read at the
  position producing the identity the capture is conditioned on. Once `worktree_diff()` exists, that
  read **is** the diff — so the paired return is the sentence's own reading made true by
  construction, and the sequencing rule is what an engine has to add to keep a sentence the section
  already asserts. It is not a new shape; it is the shape Section 9.1 was already describing before
  the capability that performs the read had a name.

The cost is one return value on a trait method in two backends, both the same engine's, and it
**removes the live defect rather than writing a rule against it**: under the sequencing rule the two
existing reads become a call-order invariant with no type behind it, kept by a comment; under the
paired return the identity cannot be taken from a different read than the diff, because there is no
second call to take it from.

**Section 10.4's closing sentence moves either way**, and the repair is to say what covers
`before:commit` rather than to weaken what it says about `before:create_pr`: the identity that came
with the diff is what the scanned content is bound by. "needs no identity to condition on where the
other two do" stays true and stops being the only thing said.

## The two carried items

- **`worktree_diff()` inherits `is_dirty()`'s set rather than stating its own.** Section 9.1 already
  pins that set for the predicate — "every change the VCS does not ignore, including content the VCS
  has not yet recorded" — so `worktree_diff()` is `is_dirty()`'s question answered with content.
  Writing the inheritance down matters: a backend that answered a **staged** diff would satisfy a
  loose reading and hand the scan the wrong content, which is a defect the paired identity does not
  catch, because a staged diff and the tree's identity can both be taken from one read.
- **`worktree_revision()`'s allowance note names one capability and should name the position.**
  Section 9.1's write-to-bookkeeping allowance "bites hardest here, because this capability is
  consulted at a position on invocations the gate then blocks." `worktree_diff()` is consulted at
  the same position on the same invocations, so the note is better restated over the position than
  over one capability.

## Confirmed against a build, and two things it learned there

Reported on the implementation reply to PR #114, after this decision was captured and against the
same pinned text. The pair this record predicts is the pair that engine had — `Dispatch::compose`
read the worktree diff before the position and `Dispatch::commit` read `worktree_revision()` after
it — so a `before:commit` unit that writes in the worktree had its writes named by the identity
taken after them: `commit:worktree_moved` unreachable through that window, content committed that no
position inspected, and `ok` reported. A `vcsx-cli` test bound to Section 6.5's own `scan-content`
shape was passing *because* of it. It was repaired there rather than held for the specification
edit, on the ground that Section 9.1 already fixes `expected_worktree` as the identity answered
"when the working tree was read at `before:commit`", so the two-read arrangement was a wrong write
against the pinned text rather than a gap in it. The point that a sequencing rule is one hole short
held up in the building: two reads disagree in whichever order they are taken.

Two findings came back from it, and both belong in the edit rather than in this record alone:

- **The pairing spends Section 9.1's bookkeeping allowance *less*, not more.** In that backend `add
  -A` ran twice, once per read, at two moments with a unit between them; paired, it runs once, and
  `diff --cached` and `write-tree` both read the index it produced. The index is git's atomicity
  boundary in decision 0079's own argument, and that decision priced `worktree_revision()` at "one
  extra `write-tree` over an `add -A` that already happens" — so the capability that made 0079
  nervous about the allowance gets cheaper on it rather than dearer. Step 4 is where that goes,
  since the note it restates is what the price is attached to.
- **The undetermined case moves with the read.** A backend that cannot answer now fails from the
  composition, before the position runs, rather than at the capture after it. Section 9.1's reason
  for `commit:failed` is unchanged; what changes is that a gate no longer runs over content the
  operation will not use. It is derivable from the pairing, which is the argument for stating it in
  Section 9.1 rather than leaving it to be derived — step 3.

## The network enumeration needs no edit

`worktree_diff()` reads a copy the checkout already holds, takes neither the access parameter nor
the credential, and acquires nothing. Section 9.1's "The network-touching capabilities are exactly
`ensure_store`, `fetch_base`, `fetch_counterpart` and `push`" stays true and "Every other capability
above is local to the checkout" absorbs it. That is an enumeration rather than an inference from the
signature, which Section 9.1 states explicitly, so the addition has to be checked against the list
rather than argued from the arguments — and it is.

## Options considered

### A sequencing rule instead of the paired return

"The identity is taken no later than the diff", stated normatively and mirrored into Section 13.1.
It is the smaller edit, it changes no capability signature, and it costs no backend anything. It is
the fallback if the paired return is judged too much.

It loses on the A→B→A case above, which no ordering reaches, and on being a rule rather than a
shape: a sequencing property is one an engine has to keep, and nothing in a capability signature, a
descriptor field or Section 9.3's determinable half can check it. The paired return makes the wrong
shape unwritable.

### Leave the diff to `diff(base_ref)` and narrow Section 10.4

Say the `before:commit` scan is supplied the branch delta rather than the working-tree diff, and no
capability is added. It loses because it changes what the position is for: Section 10.4's scan at
`before:commit` inspects what the commit would record, and a branch delta against the resolved base
says nothing about uncommitted content — which is precisely the content Section 9.1 says
`is_dirty()` counts and `ship` commits. Narrowing the position would make the canonical
`scan-content` example scan a different thing from the one it exists to scan.

### Leave the capability engine-private and rely on decision 0149's reworded row

The status quo plus the template repair. It loses on Section 9.3 and Section 6.11: a capability the
list does not have cannot be declared in a descriptor, so a policy needing one an engine's backend
does not provide is an engine-defined failure at first use rather than `capability_unsupported` at
validation. And three engines name one requirement three ways, which is the divergence the
descriptor discipline exists to prevent. Decision 0149 is what makes the gap visible in the
meantime, not a substitute for closing it.

### Fold both halves of issue #110 into one decision

It loses because the two halves rest on different premises and only one of them was settled when
this was written: `read_at_source` and `export_source` turn on `load_policy`'s status as an entry
point (decision 0141) and on Section 6.1's `vcsx.toml` gap. Folding them means this reasoning — a
scan on the documented happy path with a supply the plugin layer cannot answer, plus a live ordering
defect — is recorded as a rider on a decision whose Background is about `load_policy`.

## What was checked

At `22b5194`, against the working tree:

- Section 9.1's capability list contains no capability answering a working-tree diff;
  `diff(base_ref)` is "the branch delta against the resolved base (Section 6.4). Read-only." and
  `worktree_revision()` answers "an identity for the working tree as `commit` would capture it".
- Section 9.1's `commit` bullet binds `expected_worktree` to "the identity `worktree_revision()`
  answered when the working tree was read at `before:commit`"; its realization paragraph says
  "`commit` is `worktree_revision` at its position then `commit`, which is what makes the tree the
  gate inspected the tree captured (Section 6.6)".
- `ahead_behind(base_ref)` is in the same bullet as `current_branch()` and `is_dirty()` under "Each
  answers its value", and Section 4.1 reports `ahead`/`behind` as a pair.
- Section 9.1's closing paragraph carries "every operation Section 4.1 defines is realizable through
  it" and the network enumeration verbatim as quoted.
- Section 10.4's supply sentence and closing sentence are verbatim as quoted.
- Section 6.5's example policy binds `before:commit` → `run` → `scan-content`.
- Capabilities are **not** a group in `conformance/vcsx/vocabulary.json`, and `CLOSED_GROUPS` in
  `scripts/validate_spec_consistency.py` closes `operations` and `lifecycle_positions` only — so
  nothing is owed the registry by this addition.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## On vectors

No vector is added. Capability behaviour is not vector-shaped the way a validation is, and the
corpus should not grow a case for it. What the addition buys is the checkable half of Section 9.3: a
backend declares the capability in its descriptor, and a policy that needs one an engine's backend
does not declare is `capability_unsupported` at validation rather than an engine-specific failure at
first use. The paired identity is checkable in Section 13.1 as a property of the capability rather
than as a vector over one input.

## Reconsideration triggers

- **A second position that scans working-tree content.** The paired return binds one read to one
  capture; a position that scans the tree and gates a different operation would need the pairing
  restated over it rather than extended by analogy.
- **A checkout mode whose diff cannot be taken in the same read as its identity.** Section 9.1's
  write-to-bookkeeping allowance exists because some modes record the tree before they can inspect
  it; a mode where the two reads are structurally separate would put the sequencing fallback back on
  the table, with the A→B→A case as its known and accepted hole.
- **`worktree_revision()` losing its remaining caller.** It stays for the dispatch where no diff was
  taken; if `before:commit` became mandatory for every `commit`, the two capabilities would collapse
  into one and the pair would stop being a pair.
