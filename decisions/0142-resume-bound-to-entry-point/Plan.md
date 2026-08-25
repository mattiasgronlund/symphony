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
2. **Removed.** This step fixed a sequence-selecting property in prose, derived from Section 12's
   signatures. The derivation is wrong — `ship` takes two parameters, one of which the commit loop
   reads at every turn — and the property is withdrawn entirely (`Background.md`, "The property that
   this decision's Background records under the property that was the wrong shape three times).
   Nothing replaces it in Section 8.1; step 3 states the rule
   positionally instead. *Done when:* no clause in Section 8.1 classifies an argument by what it
   selects.
3. **`VCSX-SPEC.md` Section 5.5 or Section 8.1 — a resumed invocation does not run the flow ahead of
   the point it re-enters.** Ensure one sentence states that consequence and what follows from it:
   an argument the flow reads only ahead of the re-entered point has no effect on a resumed
   invocation, so a resumed `land` does not consult `await_first` (Section 12.3) while a resumed
   `ship` does consult `message`, which Section 12.2's commit loop reads at every turn. Ensure the
   sentence quantifies over where the flow reads an argument rather than over a class of arguments,
   and that a caller wanting the prefix dispatches the operation itself — the composition Section
   7.2 already describes. Place it where the resume's re-entry is described — beside `VCSX-SPEC.md`
   Section 8.1's "rather than beginning at its entry point", Section 5.5 stating the same rule in
   its own words. *Done when:* a merge-loop token supplied to an awaiting `land` and an await-branch
   token supplied to a bare `land` both have a stated outcome, neither is a refusal, and no argument
   had to be classified to reach either.
4. **`VCSX-SPEC.md` Section 8.1 — the refusal list gains the fourth condition.** Ensure the
   `VCSX-SPEC.md` sentence quoted as "one issued under a different policy, against a different
   repository, or by a different major version" carries a fourth condition: a `resume` issued by a
   different entry point — the entry point named on the resuming invocation differing from the one
   that issued the token. Ensure the condition is **not** stated in the general form (the flow the
   token names being expressible in the invocation being resumed): that form quantifies over a
   sequence-point enumeration no section provides, and with step 3 in place it reaches no case the
   entry-point test misses. Ensure `VCSX-SPEC.md` Section 8.1's existing justification sentence ("a
   refused resume costs a re-invocation from the entry point") still reads as the reason for the
   direction. *Done when:* the list names four conditions, the fourth is stated over the entry point
   named on the invocation rather than over `ship` and `land` by name, and an engine can evaluate it
   from the token alone.
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
   validators, `resume`, and decision 0141's policy pin), and its requiredness. Ensure requiredness
   carries the three shapes Section 8.1 states rather than a boolean — required at every entry point
   (`local_vcs`), required at named entry points keyed against the `entry_points` group
   (`store_location` for `provision`), or conditional with a `spec_ref` to where the condition is
   stated — the shape `VCSX-SPEC.md` Section 8.1 uses for `git_access`, for the forge repository
   coordinate and for `forge_access`, none of which is required per entry point. Ensure **no**
   `selects_sequence` field is added: the property is withdrawn (step 2). Ensure the group's
   `spec_refs` cite Section 8.1 and its note states that membership is closed there. *Done when:*
   every Section 8.1 argument has an entry, no entry is invented, no entry carries a property
   Section 8.1 does not state, and the group's membership equals the section's enumeration.
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
- **Coupled to decision 0153 in encoding, not in substance.** That decision adds the root trigger to
  the token outright. This one adds no part where an engine's point encoding already determines the
  entry that issued it — which is the argument step 4 rests on, `ship` never running `merge` — and
  one where it does not, since step 4's condition must be evaluable from the token alone. So the two
  are one format revision landed together and two landed apart, with a window in which a token
  issued between them decodes on neither build. This decision will plausibly land first, since it
  orders itself after 0141 while 0153 orders itself after 0143, so the obligation 0153's record puts
  on whichever of the two is applied second is stated here as well, rather than left to whichever
  record a reader opens first. Raised on the implementation reply to PR #114.
- **Independent of the issue #103 decision.** An earlier draft made step 4 wait on that decision's
  enumeration of sequence points, because the condition was stated in the general form. It is not:
  the condition is the entry point, which the token carries, so no enumeration is consulted and
  nothing here waits. Do not restore the general form when that enumeration arrives — see step 4 and
  `Background.md`.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0142-resume-bound-to-entry-point/Plan.md --rev
97617c2` reports one reach finding, on the phrase "from the entry point" at `VCSX-SPEC.md` Section
5.2. That is stock phrasing rather than a twin of the sentence step 4 edits, and Section 5.2 is not
touched.

## Anchor changes

- **Added:** `await_first` as a Section 8.1 argument (step 1), and the `arguments` registry group
  (step 9). No `selects_sequence` field is added; an earlier draft of this plan proposed one and it
  is withdrawn.
- **Changed:** Section 8.1's refusal sentence and Section 8.6's `resume_unusable` row go from three
  conditions to four; `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`'s `resume_token` row narrows in
  wording while keeping its subject. Plans citing the three-item phrasing are not edited; they
  record what was true when written.
- No token is renamed or removed. Whether the resume token itself gains a part is an engine's
  question rather than this plan's — see Ordering, and decision 0153, which adds one outright.

## Status

Applied to `VCSX-SPEC.md` (Sections 8.1, 8.6, 13.1, 13.2, 13.3),
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Section 3), `conformance/vcsx/vocabulary.json`,
`conformance/vcsx/README.md`, the new `conformance/vcsx/vectors/resume-precondition.json`, and
`scripts/validate_spec_consistency.py` — in one editing pass with decision 0141, applied after it.

Step 3's sentence sits in Section 8.1 beside the `resume` bullet's "rather than beginning at its
entry point"; Section 5.5 was left alone, the rule reading there as a property of an argument that
section does not otherwise discuss.

Two things the plan did not name were carried with it, both forced by step 9's requirement that the
group be closed and complete against Section 8.1:

- **`forge_parameters` was prose and is now a bullet.** It was the one argument Section 8.1 named
  outside the section's own field-documentation pattern, so a membership check reading that
  pattern would report it missing while the section did name it. Nothing about the argument
  changed.
- **`policy_source` and `await_first` join the consumer-configuration enumeration.** That sentence
  says which values an engine MAY read from the consumer configuration and excepts four; every
  argument the section names has to sit on one side of it, or the group carries a null where the
  specification should carry an answer. `policy_source` was absent from both sides before this
  decision — an omission rather than a decision, the exception's stated reason ("a value a previous
  invocation returned, which a configured copy would make stale by construction") not touching it —
  and `await_first` is new here. The sentence now states that the excepted set is closed by that
  shared reason rather than by enumeration, so a later argument lands on a side without a fifth
  edit.

The group carries `null` where Section 8.1 genuinely states nothing rather than guessing:
`git_credential`'s optionality and requiredness, which the section marks neither way and no
precondition names. Four things Section 8.1 names and fixes no token for — the forge repository
coordinate, the identity the work branch is derived from, the commit identity, and the execution
context — are outside the group, recorded in its note and in the check's own stated limits, a
registry being unable to publish a token the specification does not spell.

Issue #104.
