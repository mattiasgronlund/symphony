# Plan — 0078 A dispatch runs the operation's `before:<op>` position

## Scope

`VCSX-SPEC.md`: Sections 4.1 "Operation Set", 5.2 "Actions", 5.6 "Flow Bound and Termination", 6.6
"`[hooks]`", 8.6 "Invocation Preconditions", 12.2 "`ship` Sequence", 12.3 "`land` Sequence", 13.1 "Test
Matrix", 13.2 "Implementation Checklist".

No section is added, removed, or renumbered.

No reason token, no `need` token, no configuration key. The decision fixes *when* an existing position
runs; every result it can produce (`<op>:blocked`, `<op>:failed`) is already in Section 4.3 and already
defined for every gated operation. `conformance/vcsx/vocabulary.json` is therefore unchanged — Step 9
verifies rather than edits it.

No `VCSX-CONTRACT.md` edit. Its Section 7 names the four positions as "the fixed points around the
operations of Section 6" and says nothing about which caller runs one; the contract names no pseudocode
and no capability signature, so nothing shared by Section 14 changes spelling.

No `SPEC.md` edit. Symphony's Section 9 mirrors the trigger and action vocabulary and states no rule
about who runs a position, so the sequence it describes is unaffected.

Lands before 0079, which depends on it: 0079's invariant attaches to the position a dispatch runs.

## Steps

1. **Section 4.1 states the rule.** Ensure the prose following the operation list states that a gated
   operation's position runs as part of dispatching it; that the engine runs `before:<op>` whenever
   `<op>` is dispatched — by a front-end sequence, by a `[policy]` `run_op` edge, or by a retry — so
   what reached the operation does not decide whether it is gated; that gating is a property of the
   operation rather than a step a caller takes around it, citing Section 6.6's "the gated operation's
   own reason" and Section 13.1's "at every gated operation" as the two requirements a caller could not
   guarantee for a dispatch it does not make; and that an operation gated at no fixed position
   (`integrate`, `pull`) enters none wherever it is dispatched. Done when the reading is fixed in the
   section that already says "gated at".

2. **Section 4.1 records the consequence.** Ensure a `Note:` states that a position runs where its
   operation runs and nowhere else; that a `ship` over a working tree the dirtiness guard reads as
   clean dispatches no `commit` and so enters no `before:commit`; that a repository wanting a unit to
   run whether or not a commit follows binds it to a result trigger rather than to a gate; and that a
   `before:commit` unit inspects the working tree it runs in, so a clean tree carries nothing for it to
   find. Done when the behavior change is stated where a reader of `before:commit` meets it.

3. **Section 5.2 carries it on the action.** Ensure the `run_op(op, args?)` bullet states that
   dispatching a gated operation runs its `before:<op>` position first, so an operation reached through
   an edge is gated exactly as one a front-end sequence dispatches. Done when the action a policy edge
   carries says what it runs.

4. **Section 6.6 states the corollary.** Ensure the `before:*` hook bullet states that the position
   runs wherever its operation is dispatched from, so a block surfaces identically for a front-end
   sequence and for a `run_op` edge. Done when the surfacing rule names no privileged caller.

5. **Section 5.6 names the loop the rule introduces.** Ensure the paragraph establishing that a bound
   on `run_op` dispatches bounds every expressible loop also names a `run_op` edge at `before:<op>`
   dispatching that same operation — the dispatch running the position that dispatches it — and states
   that the bound ends it as it ends any other. Done when the one new cycle the rule admits is
   accounted for where cycles are accounted for.

6. **Section 8.6 closes its own example.** Ensure the paragraph whose worked example routes `status:ok`
   to `run_op` `commit` states that the dispatch runs the operation's `before:<op>` position as any
   dispatch does, and that the entry point fixes which invocations are refused in advance rather than
   which are gated. Done when the section that raises the shape answers the question it raises.

7. **Section 12.2 stops running positions itself.** Ensure `ship`'s pseudocode contains no
   `run_lifecycle` call, that each `run_op` comment names the position its dispatch runs, and that the
   prose following states that the sequence runs no position of its own and that a working tree the
   guard reads as clean enters no `before:commit`. Done when the pseudocode no longer implies the
   rejected reading.

8. **Section 12.3 stops running the position and threading the head.** Ensure `land`'s pseudocode
   contains no `run_lifecycle` call and no `expected_head` argument; that its comment records that the
   dispatch runs `before:merge` — reading the pull request and applying `pr_to_squash` for a squash
   strategy — and then merges the head that position read; and that the prose states the retry
   re-dispatches the operation, which re-runs the position, preserving 0077's soundness argument
   verbatim in substance, and that `expected_head` is not an argument the sequence threads but the head
   the dispatch's own position read. Done when 0077's property survives the change in who runs the
   position.

9. **Cross-cutting sync and the vocabulary check.** Ensure Section 13.1's gate-blocking check also
   covers a gated operation dispatched by a `[policy]` `run_op` edge — the `status:ok` → `run_op`
   `commit` shape — running `before:commit` and being blocked there identically; ensure its front-end
   check covers a `ship` over a clean working tree dispatching no `commit` and entering no
   `before:commit`; ensure Section 13.2's operation-set bullet names each gated operation running its
   position as part of every dispatch; and verify `conformance/vcsx/vocabulary.json` is unchanged, no
   token being added and no class changed. Done when the matrix pins both directions of the rule and
   the vocabulary diff is empty.

10. **Conformance corpus note.** Ensure `conformance/vcsx/README.md` records under "Deferred to later
    slices" that whether a position runs for a policy-dispatched operation needs a hook to observe
    having run, so it joins the hook-execution deferral rather than gaining a vector. Done when the
    absence of a vector is recorded rather than silent.

## Cross-cutting sync

- Section 13.1 test matrix — Step 9.
- Section 13.2 implementation checklist — Step 9.
- `conformance/vcsx/vocabulary.json` — verified unchanged, Step 9.
- `conformance/vcsx/README.md` — Step 10.
- Section 6.4's configuration cheat sheet is `SPEC.md`'s, not this document's; nothing here changes a
  `repo.policy.toml` key.

## Anchor changes

- **Removed:** `run_lifecycle` — the pseudocode function Sections 12.2 and 12.3 used to run a lifecycle
  position from a front-end sequence. The position is now run by the dispatch (Step 1), so the sequences
  name no such step. No normative text outside those two code blocks referenced it.
- **Removed:** `head_read_at_this_position()` — the pseudocode expression Section 12.3 used to supply
  `expected_head`. The capability argument `expected_head` (Section 9.2) is unchanged and keeps its
  meaning; only the sequence's threading of it goes.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 5.2, 5.6, 6.6, 8.6, 12.2, 12.3, 13.1, 13.2) and
`conformance/vcsx/README.md`. `conformance/vcsx/vocabulary.json` verified unchanged.
