# Background — 0165 A decision State that says whether the text landed

## Context

Reported from `symphony-rs` as issue #142, filed against `5a4fdf7` while re-pinning from `4d610da`.

At `5a4fdf7`, `DECISIONS.md` recorded decisions 0162 and 0163 as `State: Accepted`. Both decision
folders were present at that revision. Neither decision's normative text was anywhere in the tree:
it was on `apply-0162-tracker-category-levels`, whose tip `96f7582` was not an ancestor of `main`.
A stacked pull-request chain had collapsed — #140 was closed when its base branch was deleted on
merge, and #141 then merged 0163's text *into* the branch #140 would have carried onward.

The narrow half of that report is closed: #152 merged the stranded work, and `main` at `5a69193`
carries both decisions' text.

The general half is this decision. It is the second pin in a row where a consumer read `Accepted`
for text that was not in the tree — seven decisions at `4d610da` (0141, 0142, 0147, 0149, 0150,
0151, 0153), two at `5a4fdf7`.

## The mechanism

**`Accepted` is defined to span both states the consumer needs to tell apart.** The legend says so
in as many words:

> `Accepted` (decided; **to be / being applied**)

So this is not a chapter omitting something a reader could have looked up. The log has no vocabulary
for the distinction, by construction. A consumer asking "does the specification say this yet" is
asking a question `State` was not built to answer, and there is no other field in a chapter that
answers it either.

**What that costs is not hypothetical, and it is not symmetrical.** Two situations look identical
from a pinned tree:

1. Written but not yet applied. Building to the pinned text is correct until upstream writes
   something.
2. Applied onto a branch `main` cannot reach. The next revision's text already exists, so the same
   work is knowingly being done against words that have already been replaced.

`symphony-rs` reports the second case biting concretely at `5a4fdf7`: 0163 moves
`conformance/vectors/prompt-rendering.json` and adds three Section 17 checks about Section 12.2
rendering, so a consumer greening that corpus at the pin would be greening a vector upstream had
already rewritten. That build left `prompt-rendering.json`'s `iterate-issue-object` vector red
rather than green, and recorded that it could not state the reason in its own ledger, because the
reason was on a branch.

**The repository already has a "has it landed" field, and it has drifted.** This is the measurement
that decides the shape of the fix rather than merely motivating one.

`decisions/NNNN-*/Plan.md` carries a `## Status` section, and `decisions/_template/Plan.md`
prescribes it as "Not started / In progress / Applied to SPEC.md." It is maintained: all 164 plans
have one. Classified at `5a69193` by reading the first paragraph of each `## Status`:

| Reading | Count |
|---|---|
| `Applied…` | 150 |
| `Accepted; SPEC.md application not started` / `Not started` | 7 |
| `Applied … (working tree; not yet committed)` | 4 |
| Partial (`Steps 1–3 applied`) or superseded | 3 |

Six of the seven "application not started" plans are **stale**, and the text they describe is in
`SPEC.md` now. Checked at `5a69193`:

- 0030 (`action-policy machine`) — `SPEC.md` Section 9.12 is titled "The Action-Policy Machine";
  `grep -c 'action-policy machine' SPEC.md` → 8.
- 0031 (`autonomous task management`) — Section 8.10 is titled "Autonomous Task Management
  (OPTIONAL)".
- 0032 (`message formulation`) — `grep -c 'pr_to_squash' SPEC.md` → 3.

The four "not yet committed" statuses (0010–0013) describe a working tree that stopped existing many
revisions ago.

That is the finding that matters. A "has it landed" fact recorded as prose, in a per-decision file
that nothing re-reads once the decision is closed, drifts — and it drifted in the direction that
misleads, saying "not applied" for text that is present. The fix cannot be "maintain `Plan.md`'s
`Status` more carefully", because that is the thing that was already tried and is already there.

What distinguishes the field this decision adds is not diligence but **position**: it sits in the
index a consumer reads, and the pull request that lands the text is the one that flips it. Either
that commit changed both or it changed neither.

## Options considered

- **Option A — a fifth State, `Applied`.** `Accepted` narrows to "decided; the text is not in `main`
  yet"; `Applied` means "decided, and the normative text is reachable from `main`". The applying
  pull request flips it in the same commit that lands the text.

  Trade-offs: costs a one-time backfill pass over 164 chapters, and it is not fully mechanical (see
  the drift above). Overloads a field that until now recorded only whether a question was closed,
  so a reader must learn that `State` now answers two things.

- **Option B — keep four states and mark only the exception**, as `Accepted (not yet applied)`,
  reusing the parenthetical mechanism the legend already defines for a decision revisited in part.

  Trade-offs: no backfill at all, since every existing chapter has landed or is one of the handful
  that has not. Costs nothing to adopt. But the default reads "applied", so the failure mode is
  silence: forget the marker and a consumer reads landed text where there is none — precisely the
  reported bug, reintroduced with no signal. And the value becomes a string requiring substring
  matching rather than an enum, so a parenthetical someone writes three different ways is three
  different values to a checker.

- **Option C — derive it instead of recording it**, by having a script check whether each decision's
  anchors are present in the tree.

  Trade-offs: no field to drift, which is the strongest thing that can be said for any option here.
  It loses on what "landed" means: a decision that renames a token leaves the *old* anchor absent
  and the new one present, a decision that removes a clause leaves nothing to find, and a decision
  applied in part would read as applied. The measurement above is the evidence — establishing
  whether 0030's text was present took reading Section 9.12 and knowing what 0030 asked for, which
  is a judgement and not a grep.

## Decision and reasoning

**Option A.** Two reasons, and the second came from the consumer.

**It fails in the safe direction.** Forget to flip `Applied` and a consumer reads "not landed" for
text that has landed: they build to the pinned tree, which is what `symphony-rs` does anyway under
its own rule that the pinned text decides. Forget Option B's parenthetical and a consumer reads
"landed" for text that has not — the reported bug, silently. Option B is cheaper precisely where
being cheap costs the most.

**It is the only one of the three a consumer can gate on.** `symphony-rs` reports (issue #142) that
nothing in its `xtask/` parses `DECISIONS.md` today — the file is hashed by `spec-pin` and otherwise
read only by people and agents. So "which would the existing gate rather read" had no answer, and
the question that separates the options is which one a gate could *ever* read. A fifth State keeps
the value an enum, parseable and checkable. That build has committed to gating on it: every upstream
decision it cites as load-bearing must read `Applied` at the pin, so a citation to text that has not
landed becomes a build failure there rather than a sentence in a ledger entry. It also retires a
sentence that build's decision 0011 currently has to carry — "`accepted` says upstream closed the
question, and it does not say the specification now reads differently" — which exists only because
this field did not.

That is worth weighing honestly rather than as a tiebreak: it is one consumer's commitment, and this
specification does not add fields because one implementation asked. What makes it evidence is that
the commitment is only possible under one of the two options. Option B cannot be gated on without a
substring convention, and a convention no document states is not something a build can rely on.

**On the backfill.** `symphony-rs` proposed defaulting to `Accepted` wherever the apply history is
not obvious, on the same fail-safe reasoning. That is rejected for this pass, and the drift
measurement is why: 150 of 164 plans record an unambiguous `Applied…`, and defaulting the remainder
to `Accepted` would mark six decisions as unlanded whose text is demonstrably in `SPEC.md` — turning
a stale record into a fresh one and making the new field wrong on the day it is introduced. A field
that starts wrong is not conservatively wrong; it is a field nobody trusts.

The backfill therefore reads `Plan.md`'s `## Status` as a **seed** and verifies the residue against
the tree. The 150 clean `Applied…` plans carry over. The 14 that do not are resolved individually,
and the resolution is recorded in this decision's `Plan.md` so a later reader sees which were
judgements rather than reads.

**Reconsideration trigger.** Reopen this if `Applied` is observed drifting — a chapter reading
`Applied` whose text is not in `main`, or the reverse — from a pull request that changed the text
without changing the State. That would mean the atomicity this decision rests on is not holding in
practice, and the answer would then be Option C's derivation applied to the narrower question of
whether the State matches the tree, rather than a third field. A second trigger is `symphony-rs`
not shipping the gate it committed to: the enum argument above is load-bearing, and if nothing ever
parses the field, Option B's cheapness becomes the better trade.

## Review finding: the backfill inverted the risk it was protecting

Raised by `symphony-rs` against the applied change on branch `0165-applied-state` at `e850f72`,
before it merged. Counted there: 165 chapters — 160 `Applied`, 4 `Superseded`, 1 `Proposed`, and
**`Accepted` zero**.

Zero is correct as a fact about today. Everything upstream has accepted has landed, the stranded
0162 and 0163 having merged the same morning. The defect is what that leaves behind for an author.

**The shape of it.** The fail-safe argument above rests on `Accepted` being what a chapter is *born*
with: forget to flip it and the chapter under-claims, which is harmless. After the backfill there is
no live `Accepted` anywhere in the file. A new chapter is written by copying a neighbour, and every
neighbour reads `Applied`. So the path of least resistance became writing `Applied` at acceptance
time, before the apply pull request merges — a claim about `main` that the commit making it cannot
support, which is exactly the condition issue #142 was filed about.

**It was introduced by the repair for that condition**, which is what makes it worth recording
rather than quietly fixing. The backfill is the step that removed every instance of the safe value,
and it did so in service of the argument that a field which starts wrong is a field nobody trusts.
Both things are true: the backfill had to happen, and it left the document unable to teach its own
birth state. Neither the legend nor `Background.md` said a chapter starts at `Accepted`; both only
said what moves it to `Applied`, which a reader can satisfy by never having been at `Accepted` at
all.

**The repair.** `DECISIONS.md`'s authoring paragraph now states the birth value explicitly, names
copying a neighbour as the specific way to get it wrong, and gives the one exception (a decision
needing no specification edit, which its own text must say). The instruction sits where an author
about to add a chapter is already reading, rather than in the legend, which is read by consumers.

A mechanical gate was considered and not taken: a check that a chapter whose `State` reads `Applied`
was not created in the same commit is stronger, and `scripts/validate_spec_consistency.py` is where
it would live. It is deferred because it needs commit history rather than tree content, which is a
new class of input for that script, and because the authoring instruction is likely sufficient on
its own. The reconsideration trigger for it is the first premature `Applied` observed in review —
which is now a thing a reviewer knows to look for, this section being the record of why.

**Second-order note.** `symphony-rs` reports that the gate it committed to — every load-bearing
upstream decision must read `Applied` at the pin — currently passes vacuously, nothing in the file
reading anything else, and that it will document the gate as unproven until it has caught one. The
first real exercise is round 2: any of 0166 onward accepted before its text lands. That is the
correct posture and is recorded here because it is evidence about this decision, not that one: a
field whose first genuine use is still ahead of it has not yet been shown to work.
