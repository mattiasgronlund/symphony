# Plan — 0150 The diff a commit would record, and the identity that comes with it

## Scope

- `VCSX-SPEC.md` — Section 9.1 (VCS Backend Plugin), Section 10.4 (Content Scanning), Section 13.1
  (Test Matrix), Section 13.2 (Implementation Checklist).
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — only if a new `Implementation-defined` or MUST-document
  sentence is introduced; the intent is that none is (see Cross-cutting sync).
- `conformance/vcsx/vocabulary.json` — **no change**. Capabilities are not a group there, and
  `CLOSED_GROUPS` closes `operations` and `lifecycle_positions` only.
- `conformance/vcsx/vectors/` — no new file.
- `SPEC.md` and Symphony's artifacts — no change. Symphony reaches this through the engine contract
  and names no capability.

## Steps

1. **`VCSX-SPEC.md` Section 9.1 — `worktree_diff()` joins the list.** Ensure the required-capability
   list carries a capability answering the diff a `commit` would record, or that it could not be
   determined. Ensure it **inherits `is_dirty()`'s set rather than stating its own**, by citing that
   capability's existing sentence — "every change the VCS does not ignore, including content the VCS
   has not yet recorded" — so a backend answering a *staged* diff does not satisfy a loose reading.
   Ensure the bullet says it reads the checkout and acquires nothing. *Done when:* Section 10.4's
   `before:commit` supply is realizable through the plugin layer, and the capability's content set
   is the predicate's rather than a second one.
2. **`VCSX-SPEC.md` Section 9.1 — the capability answers a pair.** Ensure `worktree_diff()` answers
   the diff **and** the identity `worktree_revision()` answers for the tree it read, and that the
   engine supplies that identity as `expected_worktree` for the `commit` the position gates. Ensure
   the reason is stated where a reader meets it: one read, one pair, so the `VCSX-SPEC.md` Section
   6.6 property that a gate is only a gate if what it inspected is what proceeds becomes a property
   of the capability rather than of an engine's call order — an identity taken from a second read
   matches a tree that moved and moved back, which `worktree_revision()`'s content-stated contract
   cannot distinguish. Ensure the compound answer sits inside the `VCSX-SPEC.md` Section 9.1 bullet
   whose sentence reads "Each answers its value or that it could not determine one", as
   `ahead_behind(base_ref)`'s already does, rather than as an exception to it. Ensure
   `worktree_revision()` is **retained** for the dispatch where no diff is taken. *Done when:* no
   conforming engine can condition a `commit` on an identity taken from a read other than the one
   the scan inspected, and the property needs no ordering rule to hold.
3. **`VCSX-SPEC.md` Section 9.1 — the `commit` bullet and the realization paragraph agree with it.**
   Ensure the `commit` bullet's sentence quoted as "`expected_worktree` is the identity
   `worktree_revision()` answered when the working tree was read at `before:commit`" names the read
   that produces it once `worktree_diff()` exists, and that the realization paragraph's "`commit` is
   `worktree_revision` at its position then `commit`" accounts for the position where the diff is
   taken. Ensure the existing clause about `worktree_revision()` being unable to determine an
   identity — no `expected_worktree` to supply, `commit:failed` rather than capturing a tree no
   position inspected — still holds for the paired form, and that the paired form says **where**
   that case now arises: the answer comes from the composition, before the position runs, rather
   than from a second read after it, so a gate does not run over content the operation will not use.
   *Done when:* the three passages describe one read rather than two, the undetermined case has one
   answer, and a reader does not have to derive from the pairing which side of the position it falls
   on.
4. **`VCSX-SPEC.md` Section 9.1 — the allowance note is restated over the position.** Ensure the
   note that the write-to-bookkeeping allowance "bites hardest here, because this capability is
   consulted at a position on invocations the gate then blocks" names the position rather than one
   capability, since `worktree_diff()` is consulted at the same position on the same invocations.
   Ensure the note states the direction the pairing moves the price: one read at the position where
   a two-read arrangement writes the backend's bookkeeping state twice, so pairing spends the
   allowance less rather than more — decision 0079 priced the identity at one extra tree-write over
   a staging write that already happens, and the pair adds no second one. *Done when:* the note
   covers both capabilities without being written twice, and a reader weighing the allowance is not
   left assuming that a second capability at the position doubles its cost.
5. **`VCSX-SPEC.md` Section 9.1 — the network enumeration is unchanged and checked.** Ensure the
   sentence quoted as "The network-touching capabilities are exactly `ensure_store`, `fetch_base`,
   `fetch_counterpart` and `push`" is untouched and that "Every other capability above is local to
   the checkout" absorbs the addition. *Done when:* the enumeration still names four, and the new
   capability is covered by the local clause explicitly rather than by inference from its signature
   — which Section 9.1 forbids.
6. **`VCSX-SPEC.md` Section 10.4 — the closing sentence says what covers `before:commit`.** Ensure
   the sentence quoted as "so that position needs no identity to condition on where the other two
   do" stays true for `before:create_pr` and is joined by the statement of what binds
   `before:commit`'s scanned content: the identity that came with the diff. Ensure the repair adds
   rather than weakens — `before:create_pr`'s reason is unchanged. *Done when:* no sentence in
   Section 10.4 asserts coverage the mechanism does not provide, and the scan's binding is readable
   where the supply is described.
7. **`VCSX-SPEC.md` Section 13.1 — the matrix row.** Ensure a row covers a working tree written to
   between the `before:commit` scan and the capture being reported `commit:worktree_moved` rather
   than committed, **including where the tree moved and moved back** — the case an ordering rule
   admits and the pair refuses. Ensure a second clause covers a backend answering a staged diff
   being non-conforming, since the capability's set is `is_dirty()`'s. *Done when:* the row fails an
   engine that takes the identity in a separate read, and one whose backend answers the wrong
   content set.
8. **`VCSX-SPEC.md` Section 13.2 — the checklist line.** Ensure the implementation checklist covers
   supplying `expected_worktree` from the read that produced the scanned diff. *Done when:* the line
   exists and does not restate Section 13.1's wording.

## Cross-cutting sync

- `VCSX-SPEC.md` Sections 13.1 and 13.2: steps 7 and 8.
- `VCSX-SPEC.md` Section 13.3 and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`: **no row is expected to
  be owed** — the capability's behaviour is specified rather than left to the implementation, and
  its content set is inherited rather than declared. If drafting introduces any
  `Implementation-defined` or "MUST document" sentence in Section 9.1 or Section 10.4, its row goes
  in the **same commit** (`CLAUDE.md`, decision 0128); `check_obligations` errors rather than warns
  on a missing one.
- `conformance/vcsx/vocabulary.json`: no change, and this is checked rather than assumed —
  capabilities are not a group there.
- `python3 scripts/validate_spec_consistency.py` must report 0 errors and 0 warnings; it does today,
  so any output is this decision's own.

## Ordering

- **Blocked by nothing.** `worktree_diff()` is reachable through Section 6.5's own example edge and
  Section 10.4's supply at `before:commit`, and nothing about it turns on whether `load_policy` is
  an entry point.
- **Before decision 0151**, which adds the other two capabilities to the same list and edits the
  same closing paragraph. Two decisions editing one anchor set in series is where a plan's quoted
  spans go stale; 0151's plan names this one for that reason.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0150-worktree-diff-capability/Plan.md --rev
22b5194` reports three reach findings and no quote findings, all benign and recorded so a later
reader does not re-investigate:

- `VCSX-SPEC.md:270` (Section 4.1) and `VCSX-SPEC.md:3005` (Section 12.2) carry the phrase about
  content the VCS has not recorded, which step 1 quotes from `is_dirty()`'s bullet in Section 9.1.
  Those are the same property stated for the operation and for the `ship` guard; neither is edited,
  and the inheritance step 1 writes down is what keeps all three in agreement.
- `VCSX-SPEC.md:1744` (Section 8.1) carries the fragment "the other two do", which is stock phrasing
  rather than a twin of Section 10.4's closing sentence that step 6 edits.
- `VCSX-SPEC.md:2391` (Section 9) carries the fragment about a value a backend could not determine,
  which is that section's general statement of the property Section 9.1's bullets instantiate. Step
  2's quotation is of the bullet, and Section 9's framing is not edited.

## Anchor changes

- **Added:** `worktree_diff()` as a Section 9.1 required capability, answering a pair.
- **Changed:** Section 9.1's `commit` bullet and realization paragraph name the read that produces
  `expected_worktree`; the `worktree_revision()` allowance note is restated over the position;
  Section 10.4's closing sentence gains the clause for `before:commit`.
- **Removed:** nothing. `worktree_revision()` is retained.

## Status

Applied. Steps 1 to 6 are in `VCSX-SPEC.md` Sections 6.6, 9.1 and 10.4; steps 7 and 8 are in
Sections 13.1 and 13.2. No row is owed `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`, as Cross-cutting
sync expected: the edit introduces no `Implementation-defined` or MUST-document sentence, and the
identity `worktree_diff()` answers is the value `worktree_revision()`'s existing Section 13.3 row
already answers for. `conformance/vcsx/vocabulary.json` and `conformance/vcsx/vectors/` are
unchanged, and `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

Two findings are recorded in `Background.md` under `Findings from applying the plan`: one site the
plan's scope did not reach, repaired here, and the reading taken where step 2 admits two.
