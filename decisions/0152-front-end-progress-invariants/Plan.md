# Plan — 0152 What a front-end sequence must reach, not only where it stops

## Scope

- `VCSX-SPEC.md` — Section 7.1 (`ship`), Section 7.2 (`land`), Section 13.1 (Test Matrix), Section
  13.2 (Implementation Checklist).
- `conformance/vcsx/vectors/front-end-sequence.json` — the file decision 0143's plan creates; this
  decision adds cases to it rather than creating a file of its own.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — **no change**. No `Implementation-defined` behaviour
  and no MUST-document obligation is added, so no row is owed (`CLAUDE.md`, decision 0128).
- `SPEC.md` and Symphony's artifacts — no change.

## Steps

1. **`VCSX-SPEC.md` Section 7.1 — the two `ship` invariants join the paragraph that already carries
   their siblings.** Ensure the paragraph quoted as "It commits the tree it read: where the working
   tree changes between the `before:commit` position and the capture, nothing is committed" is
   joined by: the sequence dispatches no `push` step unless a `commit` **in the flow** returned a
   `done`-class result, where the guard read the working tree dirty; and it dispatches no
   `create_pr` step unless a `push` in the flow returned a `done`-class result. Ensure both are
   stated over the **flow** (Section 5.6) rather than over the invocation, so a resumed `ship`
   continuing a resolved `create_pr:blocked` is not refused by them. Ensure both are stated over the
   **sequence's own steps** rather than over `ship` as a whole, so an edge whose `run_op` dispatches
   `create_pr` is the repository's dispatch and is not falsified — the permission decision 0143
   grants. *Done when:* Section 12.2's bare `break` out of the commit loop is sound against a stated
   rule, and neither invariant refuses a conforming resume or a conforming repository edge.
2. **`VCSX-SPEC.md` Section 7.2 — the `land` invariant.** Ensure the paragraph quoted as "It merges
   the head it read" is joined by: the sequence returns a `done`-class result only where a `merge`
   in the flow reported `merge:ok`. Ensure the reason the reason-test and the class-test coincide is
   available — `VCSX-SPEC.md` Section 4.3 gives `merge` exactly one `done` reason — so the rule
   needs no phrase an engine has to interpret, such as the report's own wording about a merge the
   sequence did not make. *Done when:* a `land` whose built-in re-read-and-retry was disabled by an
   edge cannot report `done` without having merged.
3. **`VCSX-SPEC.md` Section 13.1 — the completion signal a caller reads.** Ensure the Front-ends row
   states that a `ship` that completed its sequence reports `create_pr`'s result and a `land` that
   completed reports `merge`'s — the **operation the result names**, not its class — because
   decision 0143 permits a repository edge to end a front-end early with a `done`-class result.
   Ensure the clause the test leans on is stated with it: the envelope's `op` is present exactly
   where a result was decisive and null only for the two escalation shapes Section 8.4 nulls, so a
   caller reading `op` has an answer on every ending a sequence produced. Ensure it is stated as an
   alternative to an `outputs` key with the reason given — the `output_keys` group carries the keys
   Section 8.2 fixes and notes that the rest of `outputs` is entry-specific, so a pull-request
   identifier there is not portably testable. Ensure **no count of that group reaches
   `VCSX-SPEC.md`**: cite the group by name, since decision 0141 adds an entry to it and a number
   written here is false on the day that decision lands. *Done when:* a consumer can distinguish a
   completed `ship` from one an edge truncated, using a field that exists today, and the row does
   not send them to a nullable field without saying when it is null.
4. **`VCSX-SPEC.md` Section 13.1 — the Front-ends row mirrors the three invariants.** Ensure the row
   carries the three progress conditions beside its existing upper bound, guard property and two
   convergence properties, marked as mirrors of the normative statements in Sections 7.1 and 7.2
   rather than as the place they live. Ensure the class/operation distinction from step 3 is stated
   beside them: the class is what the sequence tests of a step's own result, the operation is what
   the caller reads off the invocation's — read as one thing they look contradictory. *Done when:*
   the row states what the sequence must reach as well as where it stops, and both statements about
   classes are visibly about different classes.
5. **`VCSX-SPEC.md` Section 13.2 — the checklist lines.** Ensure the implementation checklist covers
   the progress conditions and the completion signal, without restating Section 13.1's wording.
   *Done when:* the lines exist and each names a thing an implementer does rather than a thing a
   test asserts.
6. **`conformance/vcsx/vectors/front-end-sequence.json` — the negative and the positive.** Ensure
   the file decision 0143's plan creates carries (a) the negative property: no vector's `expect`
   names `create_pr` after a push that did not report `done`; and (b) the positive half: every
   `expect` names **what the invocation reports** alongside the disposition taken and the control
   transfer. Ensure at least one case pins a truncated `ship` — `push:pr_closed → run_op status`
   reporting `status:ok` with `op: status` — beside a completed one reporting `create_pr`. *Done
   when:* a vector naming disposition and transfer but not the reported result cannot be written,
   and the truncated and completed endings are distinguishable in one `expect`.

## Cross-cutting sync

- `VCSX-SPEC.md` Sections 13.1 and 13.2: steps 3, 4 and 5.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` and Section 13.3: no row owed. Stated rather than left
  silent (decision 0128).
- `conformance/vcsx/vocabulary.json`: no change. No token is added; `output_keys` is cited, not
  edited.
- `SPEC.md` Sections 6.4, 17, 18: no change.

## Ordering

- **After decision 0143's record, in one editing pass with it.** 0143 supplies the premise the
  derivability argument rests on — the disposition/control-transfer split, with the transfer
  selected by the sequence's own `run_op` — and the two decisions edit **one anchor set**: Section
  12.2's block, Section 12.3's block, Section 13.1's Front-ends row, and now Sections 7.1 and 7.2.
  Applying them in series with a gap between them is where quoted spans go stale. Run `python3
  scripts/check_plan_anchors.py` on this plan against the revision 0143 landed on, not the one it
  was written against.
- Step 6 depends on 0143's plan step that creates the vector file; if that file does not yet exist
  when this decision is applied, step 6 creates it to 0143's stated shape rather than a different
  one.
- **Not ordered against decision 0141, and that is a property of step 3's wording rather than of the
  work.** 0141 adds an entry to the `output_keys` group; nothing here reads that group's size once
  the count is out of step 3, so the two decisions can land in either order. Restore a count in this
  plan or in `VCSX-SPEC.md` and this bullet becomes false — an ordering would then be owed.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0152-front-end-progress-invariants/Plan.md --rev
22b5194` reports two reach findings and no quote findings, both benign:

- `VCSX-SPEC.md:1692` (Section 8.1) carries the fragment "where the working tree", stock phrasing
  rather than a twin of Section 7.1's guarantee paragraph that step 1 extends.
- `SPEC.md:2102` (Section 9.10) carries "the head it read" — Symphony restating the engine's `land`
  guarantee for its own merge broker. Step 2 adds a clause to `VCSX-SPEC.md` Section 7.2 rather than
  changing what that sentence says, so the Symphony passage stays true; re-read it if step 2's
  wording moves.

## Anchor changes

- **Added:** three progress invariants in Sections 7.1 and 7.2; a completion-signal clause and three
  mirrored rows in Section 13.1; checklist lines in Section 13.2; cases in
  `front-end-sequence.json`.
- **Changed:** Section 13.1's Front-ends row gains a kind of statement it did not carry. Nothing in
  it is removed — the upper bound, the guard property and the two convergence properties all stand.
- **Removed:** nothing. No token, no section title.

## Status

Not started.
