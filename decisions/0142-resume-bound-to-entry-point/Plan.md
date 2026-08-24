# Plan — 0142 A resume token that named a point and not the invocation it belongs to

## Scope

- `VCSX-SPEC.md` — Section 5.5 (Escalation Binding), Section 7.2 (`land`), Section 8.1 (Entry Points
  and Arguments), Section 8.6 (Preconditions), Section 13.1 (Test Matrix), Section 13.2
  (Implementation Checklist).
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — the `resume_token` row narrows.
- `conformance/vcsx/vocabulary.json` — a new `arguments` group.
- `conformance/vcsx/vectors/` — a precondition vector for a crossed token.
- `scripts/validate_spec_consistency.py` — `CLOSED_GROUPS` gains `arguments`.
- `SPEC.md` and Symphony's own artifacts — **no change**. Symphony supplies no `resume` today; the
  engine's precondition is invisible to it.

## Steps

1. **`VCSX-SPEC.md` Section 8.1 — `await_first` is an argument.** Ensure the section enumerates the
   argument `VCSX-SPEC.md` Section 12.3's `function land(await_first)` takes and `VCSX-SPEC.md`
   Section 7.2 calls "`--await` — or whatever the front-end's encoding for it is", with `Default:
   unset` (a `land` that merges without awaiting), in the shape the four await parameters already
   use. Ensure Section 7.2's citation of Section 8.1 for it now resolves. *Done when:* Section 8.1
   names the argument, the default matches Section 12.3's branch, and no argument Section 12's
   signatures take is missing from Section 8.1.
2. **`VCSX-SPEC.md` Section 8.1 — the sequence-selecting property is fixed.** Ensure the section
   states which of its arguments select among an entry point's sequences, derived rather than
   asserted: an argument that appears as a parameter of a Section 12 front-end sequence function.
   Ensure the derivation is stated, so a future selector inherits the property instead of needing a
   judgement. *Done when:* a reader can decide of any argument in Section 8.1 whether it selects a
   sequence, using only Sections 8.1 and 12.
3. **`VCSX-SPEC.md` Section 5.5 or Section 8.1 — a resumed invocation does not consult a sequence
   selector.** Ensure one sentence states that arguments selecting among an entry point's sequences
   are not consulted on a resumed invocation, and that a caller wanting the prefix dispatches the
   operation itself — which is the composition Section 7.2 already describes. Place it where the
   resume's re-entry is described — beside `VCSX-SPEC.md` Section 8.1's "rather than beginning at
   its entry point", which is where that phrase occurs, Section 5.5 stating the same rule in its own
   words. *Done when:* a merge-loop token supplied to an awaiting `land` has a stated outcome, and
   that outcome is not a refusal.
4. **`VCSX-SPEC.md` Section 8.1 — the refusal list gains the fourth condition.** Ensure the
   `VCSX-SPEC.md` sentence quoted as "one issued under a different policy, against a different
   repository, or by a different major version" carries a fourth condition — a `resume` whose flow
   the invocation being resumed cannot express — of which the entry point named on the resuming
   invocation differing from the one that issued the token is the case an engine can always decide.
   Ensure `VCSX-SPEC.md` Section 8.1's existing justification sentence ("a refused resume costs a
   re-invocation from the entry point") still reads as the reason for the direction. *Done when:*
   the list names four conditions and the fourth is stated over the invocation rather than over
   `ship` and `land` by name.
5. **`VCSX-SPEC.md` Section 8.6 — the `resume_unusable` row mirrors it.** Ensure the `VCSX-SPEC.md`
   row quoted as "issued under a different policy, against a different repository, or by a different
   major version (Sections 5.5, 8.1)" carries the fourth condition in the same words as Section
   8.1's. Ensure the paragraph placing `resume_unusable` among the three reasons that reach
   `provision` is unchanged, and that the new condition is what makes that placement decidable
   there. *Done when:* the row and Section 8.1 name the same four conditions, and no new
   precondition token is introduced. Ensure `conformance/vcsx/vocabulary.json`'s
   `precondition_reasons` entry for `resume_unusable`, whose `meaning` restates the same three
   conditions, is extended with the fourth — the reach check reports it, and a registry that lists
   three where the document lists four is the drift decision 0141 found in `entry_points`.
6. **`VCSX-SPEC.md` Section 13.1 — the Resuming row names the set.** Ensure the `VCSX-SPEC.md` row
   quoted as "a token issued under a different policy is refused with `resume_unusable` before the
   policy runs" names the whole set of conditions rather than one of them, and that it includes a
   crossed entry point and a token supplied to an entry that issues none (`provision`, and
   `load_policy` under decision 0141). *Done when:* the row no longer names one of four, and a
   reader can tell from it what an engine refuses.
7. **`VCSX-SPEC.md` Section 13.2 — the checklist line follows.** Ensure the implementation checklist
   covers establishing a supplied `resume` against all four conditions. *Done when:* the line exists
   and does not restate Section 13.1's wording.
8. **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 3 — the row narrows to the form.** Ensure that
   file's row quoted as "Form of the `resume_token`, and how the engine establishes that one it is
   handed is its own and current" no longer invites an engine to answer *whether* a crossed token is
   refused, that being specified rather than declared, while keeping the form question — what the
   token encodes, and whether it is signed. *Done when:* the row asks only what two conforming
   engines may legitimately answer differently, and `python3 scripts/validate_spec_consistency.py`
   reports 0 errors and 0 warnings.
9. **`conformance/vcsx/vocabulary.json` — an `arguments` group.** Ensure a closed group exists
   carrying every argument Section 8.1 enumerates, each with the properties that section states:
   whether it is OPTIONAL, whether it is excepted from the consumer configuration (the two read
   validators, `resume`, and decision 0141's policy pin), and whether it selects among an entry
   point's sequences. Ensure the group's `spec_refs` cite Section 8.1 and its note states that
   membership is closed there. *Done when:* every Section 8.1 argument has an entry, no entry is
   invented, and the group's membership equals the section's enumeration.
10. **`scripts/validate_spec_consistency.py` — the new group is checked.** Ensure `CLOSED_GROUPS`
    names `arguments`, reading its membership from Section 8.1, so the group and the prose cannot
    drift in either direction. *Done when:* the check walks the group, and removing an argument from
    either side is reported as an error.
11. **A vector for the crossed token.** Ensure a precondition vector covers a token whose issuing
    entry point differs from the invoked one, expecting `resume_unusable`, modelled as a
    precondition over supplied arguments rather than as a two-invocation harness — the file's inputs
    being the issuing entry, the invoked entry and the token's other bindings. Ensure a passing
    vector covers the same entry point on both sides. *Done when:* both vectors exist and neither
    requires a live invocation.

## Cross-cutting sync

- `VCSX-SPEC.md` Sections 13.1 and 13.2: steps 6 and 7.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`: step 8 — a **narrowing**, not an addition. The decision
  introduces no new `Implementation-defined` behaviour and no new token, so no row is owed
  (`CLAUDE.md`, decision 0128); the existing row stops covering a question the specification now
  answers.
- Section 13.3's obligation paragraph mentions the same `resume_token` question; ensure it narrows
  with the row rather than diverging from it.
- `SPEC.md` Sections 6.4, 17, 18: no change.

## Ordering

- **After decision 0141.** Step 9's `arguments` group must carry the policy pin among the
  consumer-configuration exceptions, and step 6's Resuming row names `load_policy` as an entry that
  issues no token — both of which 0141 creates.
- **Steps 1, 2, 4, 5, 9, 10 and 11 are applicable now.** Step 4's general phrasing — the flow the
  token names being expressible in the invocation being resumed — is decidable only once the issue
  #103 decision enumerates a sequence's points; until then the condition is written over the entry
  point alone, which is the case an engine can always decide, and the general form replaces it in
  the same words when that enumeration exists. Do not state the general form over an enumeration
  that does not exist: a condition an engine cannot evaluate is the defect decision 0140 repairs,
  not the repair.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0142-resume-bound-to-entry-point/Plan.md --rev
97617c2` reports one reach finding, on the phrase "from the entry point" at `VCSX-SPEC.md` Section
5.2. That is stock phrasing rather than a twin of the sentence step 4 edits, and Section 5.2 is not
touched.

## Anchor changes

- **Added:** `await_first` as a Section 8.1 argument (step 1), and the `arguments` registry group
  (step 9).
- **Changed:** Section 8.1's refusal sentence and Section 8.6's `resume_unusable` row go from three
  conditions to four; `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`'s `resume_token` row narrows in
  wording while keeping its subject. Plans citing the three-item phrasing are not edited; they
  record what was true when written.
- No token is renamed or removed.

## Status

Not started.
