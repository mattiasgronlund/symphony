# Plan — 0144 What a concurrency slot counts, and when a run starts occupying one

## Scope

- `SPEC.md` — Section 8.3 (Concurrency Control), Section 8.5 (Reconciliation), Section 7.1 (Issue
  Orchestration States), Section 9.11 (Remote Node-Scheduler), Section 17.4 (test matrix), Section
  18 (implementation checklist).
- `decisions/0138-reference-algorithm-gaps/Background.md` and `DECISIONS.md`'s 0138 chapter — a
  logged review finding.
- `conformance/README.md` — its decision-0138 entry restates the same false magnitude.
- `conformance/vectors/available-slots.json` — **no change**, and that is a step rather than an
  omission.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — **no change**. This decision adds no
  `Implementation-defined` behaviour and no MUST-document obligation, so no row is owed
  (`CLAUDE.md`, decision 0128).

## Steps

1. **`SPEC.md` Section 8.5 — the false clause goes and the conclusion stays.** Ensure the second of
   the two consequences drawn from the reconciliation-ownership invariant — the bullet beginning "A
   run stopped because its issue reached a terminal or non-active state schedules no retry at all" —
   no longer contains the clause quoted as "because `claimed` counts against `available_slots`", and
   that the cost it states is the one that follows under the Section 8.3 formula: the issue holds
   its own claim until the retry fires and releases it, so an issue closed and reopened inside that
   window is skipped by every tick in between (Section 8.2), while other issues' dispatch is
   unaffected. Ensure Part B still schedules no retry and the invariant paragraph above the two
   consequences is untouched. *Done when:* no sentence in `SPEC.md` asserts that `claimed` counts
   against `available_slots`, and the bullet's conclusion is unchanged.
2. **`SPEC.md` Section 8.3 — say what `running_count` counts.** In Section 8.3, ensure the sentence
   quoted as "Slot accounting is placement-opaque: it counts agent sessions, not where they run"
   stays and reads as the reason for a new statement beside the formula: `running_count` is the
   number of entries in the `running` map (Section 4.1.8), and `claimed` does not enter the
   computation — an issue reserved but not running takes no slot, which is what makes Section 8.2's
   `claimed` condition and its concurrency condition independent tests. *Done when:* whether an
   issue queued for retry holds a slot is answerable from Section 8.3 alone, without consulting
   `conformance/vectors/available-slots.json`.
3. **`SPEC.md` Section 7.1 — `Provisioning` and `Running` are phases of one running entry.** In
   Section 7.1, ensure states 3 and 4 state that a dispatched run occupies an entry in `running`
   from dispatch until the run ends, and that `Provisioning` and `Running` name phases of that entry
   rather than membership tests against the map. Ensure state 4's wording quoted as "Worker task
   exists and the issue is tracked in `running` map" no longer reads as a membership test that would
   put a provisioning run outside the count. *Done when:* an implementation reading Sections 7.1 and
   8.3 together holds one collection for dispatched runs, and state 3's dispatch-slot claim is true
   rather than contradictory.
4. **`SPEC.md` Section 9.11 — the acquisition bullet is true under the formula.** In Section 9.11,
   ensure the acquisition bullet quoted as "It holds a dispatch slot but is not yet `Running`, so a
   slow acquire does not block the poll tick" cites the phase reading as the reason it holds a slot,
   rather than leaving the reader to reconcile it with Section 8.3's formula. Ensure no second
   counter is introduced. *Done when:* the bullet names the mechanism — the entry `dispatch_issue`
   wrote — and is checkable against the formula. Note that this sentence occurs twice, at Section
   7.1 state 3 and here; both are in scope and step 3 covers the first.
5. **`SPEC.md` Section 16.4 — the entry's lifetime is visible where it is created.** Ensure the
   comment beside `state.running[issue.id] = { … }` states that the entry exists from this point
   until the run ends, including through a remote acquisition performed inside the worker (Section
   16.6), so `Provisioning` is a phase of it. *Done when:* the reference algorithm shows what
   Section 7.1 asserts, and no step reads as writing the entry only once the agent starts.
6. **`SPEC.md` Section 17.4 — two rows.** Ensure the matrix covers (a) a dispatched run occupying a
   concurrency slot from dispatch through its `Provisioning` phase until it ends, so a slow node
   acquire does not admit a second dispatch of the same headroom; and (b) an issue that is claimed
   and queued for retry occupying **no** slot, so a `max_concurrent_agents: 1` deployment with one
   issue in backoff dispatches a different eligible issue. Ensure the existing rows on
   `Provisioning` and on retry requeueing are not duplicated. *Done when:* both properties are
   checks a suite can run, and the second one fails a `claimed`-based implementation.
7. **`SPEC.md` Section 18 — the checklist follows.** Ensure the implementation checklist covers
   computing headroom from the `running` map alone. *Done when:* the line exists and does not
   restate Section 17.4's wording.
8. **`conformance/vectors/available-slots.json` — unchanged, deliberately.** Ensure the file is not
   edited and its four vectors still pass. Its `description` field restates Section 8.3's
   placement-opaque sentence; that restatement stays true under step 2, which adds to the section
   rather than changing what the formula counts, so the site is named here to record that it was
   checked rather than overlooked. *Done when:* `git diff` shows no change to it and the corpus is
   green.
9. **Decision 0138 — log the review finding.** Ensure `decisions/0138-reference-algorithm-gaps/
   Background.md` gains an appended review-finding section recording that the magnitude it stated
   for the old behaviour does not hold under Section 8.3's formula and the pinned vector, that the
   repair is correct on its other grounds, and what the cost actually is. Ensure `DECISIONS.md`'s
   0138 chapter has its magnitude sentence corrected in place, naming this decision, and that its
   **State** carries the parenthetical the States legend provides for a decision revisited in part.
   Ensure the earlier reasoning is extended rather than erased. *Done when:* 0138's chapter no
   longer asserts a concurrency-slot cost and says where the correction came from.
10. **`conformance/README.md` — the third artifact carrying the false magnitude.** In that file's
    decision-0138 entry, ensure the clause reporting that a retry queued for a closed issue "holds a
    claim, and therefore a concurrency slot, for up to `agent.max_retry_backoff_ms`" states the
    corrected cost instead. This site was found by `python3 scripts/check_plan_anchors.py` against
    an earlier draft of this plan, which named only `SPEC.md` and `DECISIONS.md`; it is the reach
    finding the tool exists for, and it is why the plan enumerates three artifacts rather than two.
    *Done when:* no file in the repository asserts that a claim costs a concurrency slot, and the
    corpus README's account of decision 0138 matches that decision's own chapter.

## Cross-cutting sync

- `SPEC.md` Sections 17.4 and 18: steps 6 and 7.
- `SPEC.md` Section 6.4 (config cheat sheet): no change — no configuration key is added or
  redefined.
- `CONFORMANCE-STATEMENT-TEMPLATE.md`: no row is owed. Stated here rather than left silent, because
  three decisions in a row missed the case where one **is** (decision 0128).

## Ordering

- **Before decision 0145.** That decision's `Background.md` records the slot consequence as
  withdrawn on this decision's authority; capturing and applying this one first is what makes the
  withdrawal a citation rather than an assertion.
- Independent of decision 0146, which needs neither half.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0144-slot-accounting-and-provisioning-phase/Plan.md
--rev 22b5194` reports five reach findings and no quote findings. Four are benign and are recorded
so a later reader does not re-investigate them:

- `conformance/vectors/available-slots.json:5` carries Section 8.3's placement-opaque sentence in
  its `description`. Named in step 8; it stays true.
- `SPEC.md:1394` (Section 8.8) and `conformance/vectors/retry-fire-disposition.json:11` carry the
  fragment "and the issue is", which is stock phrasing inside step 3's quotation of Section 7.1
  state 4 rather than a twin of the sentence being edited. Neither section is touched.
- `conformance/README.md:435-436` are the site step 10 exists for. The tool reported them against an
  earlier draft that named only `SPEC.md` and `DECISIONS.md`; they are now in scope, and the finding
  persists only because the step names the file and its decision-0138 entry rather than a line.

## Anchor changes

- **Changed:** Section 8.5's second consequence bullet loses its `available_slots` clause and states
  a different cost; Section 8.3 gains a statement of what `running_count` counts; Section 7.1 states
  3 and 4 gain the phase reading. No token is renamed.
- **Removed:** no code-token identifier and no section title. The phrase "because `claimed` counts
  against `available_slots`" ceases to exist in `SPEC.md`; plans quoting it are not edited, since
  they record what was true when written.
- **Added:** nothing to any registry. `conformance/` gains no file.

## Status

Not started.
