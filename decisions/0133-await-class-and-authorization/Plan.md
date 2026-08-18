# Plan — 0133 A token that was the whole class, and a bound that was the only bound

## Scope

- `VCSX-SPEC.md` — Section 7.2's `land --await` paragraph; Section 12.3's `land` sequence; Section
  8.1's four await parameters; Section 4.1's `await_checks` entry; Section 4.3's registry rows and
  the `still_pending`/`budget_floor` paragraph; Section 8.6's precondition table and three of its
  paragraphs; Section 13.1's bounded-wait row; Section 13.2's `await_checks` bullet.
- `VCSX-CONTRACT.md` — Section 6's `await_checks` bullet. Section 3's `land` bullet is confirmed
  correct and not edited.
- `conformance/vcsx/vocabulary.json` — one new `precondition_reasons` entry; two `reasons` notes;
  the `operations` note for `await_checks`.
- `scripts/validate_spec_consistency.py` — check 5.

No `Implementation-defined` behavior and no "MUST document" obligation is added: every answer is
determinate, so no Conformance Statement template row is owed. Verified against
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`, whose `### 4.3 Precondition Reasons` is a fill-in table
rather than an enumeration of registry tokens, and against `VCSX-SPEC.md` Section 13.3, which
requires documenting only reasons added *beyond* the registry.

`SPEC.md`'s `vcs.await_*` keys are deliberately out of scope: they carry the values a consumer
supplies and none of their descriptions states which parameter authorizes a loop.

## Steps

1. **`VCSX-SPEC.md`, Section 7.2 "`land`", the paragraph beginning "`land` MAY be invoked to await
   first".** Ensure the paragraph continues to the merge where the await's result is class `done` and
   ends on it otherwise, stated as the disposition Section 5.4 already gives every operation result
   rather than as a rule the composition adds. *Done when:* the paragraph names no `await_checks`
   reason token, and its own "introduces no sequencing rule of its own" claim is true of what it
   states.

2. **`VCSX-SPEC.md`, Section 12.3 "`land` Sequence", `function land()`.** Ensure the function takes
   `await_first` and gains a leading branch that checks the flow bound, dispatches `await_checks`,
   and returns `result_of(a)` where `a.class != done`, in the idiom Section 12.2 already uses
   (`if r.class != done: return result_of(r)`). Ensure the section's prose notes that the dispatch
   counts once against the flow bound however many reads it made (Section 5.6). *Done when:* the
   pseudocode carries a class check and no reason token, and Section 7.2's prose and this sequence
   describe the same behaviour.

3. **`VCSX-SPEC.md`, Section 8.1, the four await parameters, beside "an invocation supplying none
   makes a single read and cannot loop".** Ensure the section states:
   - that `await_bound_ms` and `await_max_reads` are what authorize a second read, that
     `await_interval_ms` paces reads a bound already authorized, and that `await_budget_floor` can
     only end a wait early;
   - that an invocation supplying `await_interval_ms` or `await_budget_floor` and neither
     `await_bound_ms` nor `await_max_reads` is refused before the policy runs as `await_bound_missing`
     (Section 8.6);
   - that a floor and a read allowance reached on the same read report `budget_floor`, derived from
     this section's own "the snapshot each read observes" — the floor judges the read just made, the
     allowance decides whether to read again;
   - that a floor the observed snapshot cannot answer — no snapshot, or no bucket of that name — ends
     the wait with `budget_floor`, with the reasoning (an engine that cannot establish there is room
     does not keep spending) and the consequence (against a forge publishing no budget, a
     floor-carrying invocation reads once).
   *Done when:* for each of the four parameters the section says both whether it authorizes a second
   read and what it ends.

4. **`VCSX-SPEC.md`, Section 4.1, the `await_checks` entry.** Ensure the fourth of the five terminal
   conditions is the invocation's **read allowance** ending, an invocation authorizing no loop having
   an allowance of one read. Still five conditions. *Done when:* a no-parameter invocation that finds
   the checks pending matches exactly one condition in the list.

5. **`VCSX-SPEC.md`, Section 4.3, the rows `await_checks | still_pending` and
   `await_checks | budget_floor`, and the paragraph beginning "`await_checks:still_pending` and
   `await_checks:budget_floor` both end a wait".** Ensure `still_pending`'s gloss follows the
   allowance framing and `budget_floor`'s covers the floor the snapshot cannot answer. Ensure the
   paragraph carries the tie-break and keeps its "the repairs differ" argument. *Done when:* both
   glosses agree with Section 8.1 and neither says "a supplied bound was reached" alone.

6. **`VCSX-SPEC.md`, Section 8.6 "Invocation Preconditions".** Ensure:
   - the table carries a row *"An await parameter that only ends a wait was supplied with neither
     `await_bound_ms` nor `await_max_reads` (Section 8.1)"* → `await_bound_missing`;
   - a paragraph places it with `base_branch_not_permitted` and `resume_unusable` — judged wherever an
     await parameter was supplied, whatever the entry — and says in one sentence why the closing
     count of "six rows naming a missing argument" is unchanged: what is wrong is the combination the
     invocation named, not an argument absent where one was required;
   - the checkout-free enumeration ending "…`base_branch_missing` and `base_branch_not_permitted`
     are" names it;
   - the `provision` sentence beginning "What remains is" names the required-argument set plus the
     three judged wherever their argument is supplied — `base_branch_not_permitted`, `resume_unusable`
     and `await_bound_missing`. *(Finding: the sentence was already short by two before this decision
     touched it; see `Background.md`.)*
   *Done when:* every reason `provision` can reach is named in that sentence, and the closing
   six-row count matches the rows that satisfy it.

7. **`VCSX-SPEC.md`, Section 13.1 "Test Matrix", the bounded-wait row.** Ensure it asserts: an
   invocation naming only a floor or only an interval is refused with `await_bound_missing` whatever
   the entry; a floor naming a bucket the snapshot does not carry ends the wait with `budget_floor` on
   the first read; a read allowance and a floor reached together yield `budget_floor`; a no-parameter
   invocation that finds the checks pending yields `still_pending`; and a `land --await` continues to
   the merge on every class `done` reason rather than on `ok`. Leave the existing "a `land --await`
   against such a repository merges" sentence verbatim. *Done when:* each behaviour this decision
   states has an assertion in the row.

8. **`VCSX-SPEC.md`, Section 13.2 "Implementation Checklist", the `await_checks` bullet.** Ensure it
   carries the authorization split and the refusal. *Done when:* the bullet names what authorizes a
   loop, not only what bounds one.

9. **`VCSX-CONTRACT.md`, Section 6, the `await_checks` bullet.** Ensure the five-condition sentence
   is re-framed to the read allowance in step 4's words. Confirm — do not edit — that Section 3's
   `land` bullet already reads "composes the two operations below and introduces no sequencing of its
   own". *Done when:* the contract and `VCSX-SPEC.md` Section 4.1 state the same five conditions.

10. **`conformance/vcsx/vocabulary.json`, `precondition_reasons.entries`.** Ensure an entry with
    token `await_bound_missing` exists, with a `meaning` in the group's voice, placed after
    `resume_unusable`. *Done when:* the entry's meaning states both what is refused and that it is
    judged whatever the entry.

11. **`conformance/vcsx/vocabulary.json`, `reasons.entries`.** Ensure the notes on
    `await_checks:still_pending` and `await_checks:budget_floor` follow Section 4.3 — the allowance
    framing, the tie-break, and the floor the snapshot cannot answer. *Done when:* neither note
    contradicts Section 4.3's gloss.

12. **`conformance/vcsx/vocabulary.json`, `operations.entries`, `await_checks`.** Ensure its note
    carries the loop authorization: only `await_bound_ms` and `await_max_reads` authorize a second
    read. *Done when:* the note states it alongside the existing flow-bound sentence.

13. **`scripts/validate_spec_consistency.py`.** Ensure a **check 5, the await enumeration** exists in
    the file's existing shape: a module-level constant for the four parameter names and for the count
    of terminal conditions; an assertion that each parameter occurs in `VCSX-SPEC.md` Section 8.1 and
    in `conformance/vcsx/vocabulary.json`; and an assertion that the count of terminal conditions
    stated in `VCSX-SPEC.md` Section 4.1 and in `VCSX-CONTRACT.md` Section 6 agree. Ensure the module
    docstring's numbered list names the check and states its limit rather than leaving it to be
    discovered. *Done when:* the script exits 0 on the edited tree with no warning beyond the three
    pre-existing ones, and exits non-zero if a parameter is removed from Section 8.1.

## Cross-cutting sync

- `VCSX-SPEC.md` Section 13.1 (test matrix) — step 7.
- `VCSX-SPEC.md` Section 13.2 (implementation checklist) — step 8.
- `VCSX-SPEC.md` Section 13.3 (Conformance Statement obligations) — no change. This decision adds no
  `Implementation-defined` value and no "MUST document" clause.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — no row owed, for the reason in Scope above.
- `SPEC.md` Section 6.4 (config cheat sheet), Section 17 (test matrix), Section 18 (checklist) — no
  change. The `vcs.await_*` keys carry values and state no authorization rule.

## Anchor changes

- Added: `await_bound_missing` (precondition reason, `VCSX-SPEC.md` Section 8.6).

No renames. No removals. No section retitled.

## Status

Applied. Issues #81 and #82.
