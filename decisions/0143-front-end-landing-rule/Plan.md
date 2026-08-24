# Plan — 0143 Where a substituted result lands in a front-end sequence

## Scope

- `VCSX-SPEC.md` — Section 5.4 (Unmatched Policy and Determinism), Section 7.1 (`ship`), Section
  12.1 (the machine's helpers), Section 12.2 (`ship` Sequence), Section 12.3 (`land` Sequence),
  Section 13.1 (Test Matrix), Section 13.2 (Implementation Checklist).
- `conformance/vcsx/vectors/` — a new vector file for the front-end sequence function, and
  `conformance/vcsx/README.md`'s table row for it.
- `VCSX-CONTRACT.md` — Section 3's `ship` entry point description, which carries the same extent
  sentence Section 7.1 does.
- `conformance/vcsx/vocabulary.json` — **no change**. The decision names no new token: `continue`,
  `break` and `return` are pseudocode control transfers rather than published vocabulary, and
  `match-edge.json`'s note already records that `continue` is a Section 5.4 outcome rather than a
  Section 5.2 action.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — **no change**. The decision removes an
  under-specification rather than adding an `Implementation-defined` behaviour; nothing new is left
  to an engine to choose, so no row is owed (`CLAUDE.md`, decision 0128).
- `SPEC.md` and Symphony's artifacts — **no change** to normative text. Symphony invokes `ship` and
  reads the envelope; the completion test in step 6 is what its own reading of a `ship` result
  should eventually cite, but that is a consumer-side decision of its own.

## Steps

1. **Section 12.1 (or Section 12.2, wherever the sequences' vocabulary is introduced) — `dispatch`
   and `result_of` are defined, or one is removed.** Ensure the document either defines both names —
   what each is handed, what each returns, and where Section 5.4's disposition is applied — or
   spells one of them out of existence so a single spelling is used at all six call sites. Ensure no
   call site suggests that policy is consulted at one dispatch and not at another. *Done when:* the
   six call sites use one spelling, decision 0138's test passes for both names (a reader can supply
   the body without changing behaviour stated elsewhere), and no reader can derive from the spelling
   the refuted reading in which a repository edge never fires under a sequence.
2. **`VCSX-SPEC.md` Section 5.4 — `continue` has a referent.** Ensure the built-in default table's
   last entry — the one giving `continue` for a `done` result with no edge — says what continues:
   control returns to the dispatcher — the front-end sequence or the driver — at the point the
   dispatch was made. *Done when:* the word names something a reader can point at, and
   `match-edge.json`'s note about `continue` being an outcome rather than an action is consistent
   with it.
3. **`VCSX-SPEC.md` Sections 12.2 and 12.3 — the landing rule is stated where the sequences are
   written.** Ensure both sections state: a repository edge replaces the built-in **disposition** of
   the trigger; where the disposition returns control to the sequence, the **control transfer** is a
   property of the trigger and is unchanged; where it ends the flow, the invocation ends and no
   transfer applies; and where the transfer is `return`, the sequence reports the result the machine
   last handed back. Ensure the transfer is stated as selected by the result of the sequence's own
   `run_op`, with every substitution inside the machine invisible to the sequence. Ensure the
   flow-ending clause is present — without it the rule says a `push:non_fast_forward → escalate`
   edge continues the push loop, which Section 5.6 forbids. *Done when:* each of the ten branches in
   the two sequences has a determinate landing, the `push:pr_closed → run_op status` case among
   them, and the pseudocode shows the rule rather than leaving it to the prose beneath the block.
4. **`VCSX-SPEC.md` Section 12.2 — the two wrong writes are unreachable.** Ensure that under the
   stated rule a policy-bound `push:non_fast_forward` retries the push rather than breaking to
   `create_pr`, and a policy-bound `commit:worktree_moved` re-reads `is_dirty()` and re-dispatches
   `commit` rather than falling through to `push`. *Done when:* neither a pull request on the
   remote's prior head nor a push of an uncommitted worktree is derivable from Section 12.2 under
   any `[policy]` edge.
5. **`VCSX-SPEC.md` Section 12.3 — the same, for the merge loop.** Ensure a policy-bound
   `merge:head_moved` keeps the `continue` transfer, so the built-in re-read-and-retry is not
   silently disabled, and ensure `VCSX-SPEC.md` Section 12.3's existing sentence "reaches a caller
   through this sequence only where a repository binds it to an edge that ends the flow" stays true
   word for word. *Done when:* both hold.
6. **`VCSX-SPEC.md` Section 13.1 — the completion test a caller reads.** Ensure a clause states that
   a front-end that completed its sequence reports the result of the operation the sequence ends at
   — `create_pr` for `ship`, `merge` for `land` — and that a caller tests **the operation the result
   names** rather than its proto class, a repository edge being permitted to end a front-end early
   with a `done`-class result. Ensure the clause does not reach for an `outputs` key: the
   `output_keys` group carries the keys Section 8.2 fixes and the rest of `outputs` is
   entry-specific, so a pull-request identifier there is not portably testable. Ensure **no count of
   that group is written**, here or in `VCSX-SPEC.md`: decision 0141 adds an entry to it, so a
   number is false on the day that decision lands and the conclusion never needed one. *Done when:*
   the clause exists, a consumer can tell a completed `ship` from a truncated one using only the
   envelope, and nothing this step writes has to be re-checked when the group grows.
7. **`VCSX-SPEC.md` Section 7.1 — the extent sentence is not read as a postcondition.** Ensure that
   section's "drives the change from the current worktree up to and including opening or updating
   the pull request" is not contradicted by step 6, stating if needed that it describes the extent
   of the sequence rather than a guarantee about every invocation — which the five built-in exits
   without a pull request already establish. *Done when:* Sections 7.1 and 13.1 agree, and neither
   implies a `ship` always reaches `create_pr`. Ensure `VCSX-CONTRACT.md` Section 3's parallel
   sentence — `ship` drives "up to and including opening/updating the pull request" — reads the same
   way, since the reach check reports it as the twin site and the contract is what a consumer reads
   first.
8. **`VCSX-SPEC.md` Section 13.2 — the checklist covers the rule.** Ensure the implementation
   checklist names the disposition/transfer split and the completion test. *Done when:* the lines
   exist and do not restate Section 13.1's wording.
9. **The vector file.** Ensure a vector file exists for the front-end sequence function named in
   step 1, its inputs being the sequence, the position in it, the trigger and the edge set. Ensure
   it carries three pairs on the `continue`-shaped branches (`push:non_fast_forward`,
   `commit:worktree_moved`, `merge:head_moved`), each with and without a repository edge, plus the
   discriminating `push:pr_closed → run_op status` case on a `return`-shaped branch, plus a
   flow-ending-edge case for the middle clause. Ensure each `expect` names the disposition taken,
   the control transfer, **and** what the invocation reports. Ensure `conformance/vcsx/README.md`'s
   vector table gains the row. *Done when:* every branch shape is covered, no `expect` names only
   the next operation dispatched, and the corpus would fail an engine implementing the refuted
   reading.

## Cross-cutting sync

- `VCSX-SPEC.md` Section 13.1 (test matrix): steps 6 and 9's behaviours.
- `VCSX-SPEC.md` Section 13.2 (checklist): step 8.
- `VCSX-SPEC.md` Section 13.3 and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`: no change — no
  obligation is added or removed.
- `SPEC.md` Sections 6.4, 17, 18: no change.

## Ordering

- Independent of decisions 0140, 0141 and 0142; it touches none of the sections they edit. The
  independence from 0141 is a property of step 6's wording: that decision adds an entry to the
  `output_keys` group, so a step stating the group's size would owe it an ordering. None does.
- **Before the issue #103 decision.** The landing point this decision defines is the object a
  resumed sequence's cursor names; settling #103 first leaves its cursor pointing at an undefined
  concept.
- **A separate decision from issue #111's invariants, applied in the same editing pass.** They stay
  separate records: under this rule the first two are derivable rather than additional, which makes
  them a regression test on it rather than a new constraint on policy, and the third — that `ship`
  returns a `done` class only from `create_pr` and `land` only from `merge` — is the invariant this
  decision spends. But both edit one anchor set — Section 12.2's block, Section 12.3's block,
  Section 13.1's Front-ends row, and Sections 7.1/7.2 — so applying them in series with a gap
  between them is where a plan's quoted spans go stale. This record is written first, because #111's
  derivation cites this rule as its premise.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0143-front-end-landing-rule/Plan.md --rev 97617c2`
reports nothing once each quotation names its file in the sentence carrying it, which is why two
anchors here are described rather than quoted.

## Anchor changes

- **Added:** whichever of `dispatch` / `result_of` survives step 1 becomes a defined name; the other
  may be removed. Both are pseudocode function names appearing only in Sections 12.2 and 12.3, and
  no registry publishes either.
- **Changed:** `VCSX-SPEC.md` Section 5.4's built-in default entry for a `done` result with no edge
  gains its referent (step 2).
- No reason token, config key or registry token is renamed or removed.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.4, 7.1, 12.1, 12.2, 12.3, 13.1, 13.2),
`VCSX-CONTRACT.md` (Section 3), `conformance/vcsx/vectors/front-end-sequence.json` and
`conformance/vcsx/README.md`.

Step 1 resolved by spelling `dispatch` out of existence rather than by defining both names:
every dispatch site is now `run_op`, and Section 12.1 defines it, `result_of` and
`disposed_by_policy` — the third being what lets the pseudocode show which block is the
built-in disposition an edge replaces, which is step 3's requirement that the rule be visible
in the block rather than only in the prose beneath it. Issue #107.
