# Plan — 0162 The four tracker categories a guarantee is checked by

## Scope

`SPEC.md`, by section title: Section 10.6 (Timeouts and Error Mapping); Section 11.4 (Error Handling
Contract); Section 17.3 (Issue Tracker Client); Section 18.1.2 (Broker Core Conformance); Section 19
(Conformance Statement).

`CONFORMANCE-STATEMENT-TEMPLATE.md` (two new rows), `conformance/vocabulary.json` (the
`tracker_error_categories` and `agent_error_categories` groups) and `conformance/README.md`.

No new section, no removed section, no renamed token. The change is a requirement level on four
named categories, an openness rule on two registries, and the obligations that follow.

This decision and decision 0164 both edit Section 11.4 and do not collide: this one levels
`tracker_unsupported_operation`, `tracker_state_unreachable`, `tracker_state_conflict` and
`tracker_pagination_error`; 0164 removes `unsupported_tracker_kind`, `missing_tracker_api_key` and
`missing_tracker_project_slug`. Neither set overlaps and no step here states a count of the
section's entries, so the two apply in either order.

## Steps

1. **`SPEC.md`, Section 11.4 (Error Handling Contract), the four REQUIRED spellings.** Ensure the
   section states that `tracker_unsupported_operation`, `tracker_state_unreachable`,
   `tracker_state_conflict` and `tracker_pagination_error` are REQUIRED spellings: where the
   condition each names occurs, an implementation MUST report it under that name. Ensure the
   remaining categories are stated as RECOMMENDED — a target vocabulary each adapter maps its
   transport's failures onto — so the section carries both levels explicitly rather than one level
   in its opening line. Done when a reader can tell each entry's level from the section without
   inferring it from position, and when no sentence in the section still declares one level over all
   entries.

2. **`SPEC.md`, Section 11.4, the predicate.** Ensure the section states *why* those four and not
   others, in one short passage: a category is REQUIRED where it is what makes a guarantee this
   specification states observable when it fails — the capability descriptor gating writes (Section
   11.7), which Section 17.3 checks as "never silently no-oped"; `set_state`'s two failure modes and
   the orchestrator's differing response to each (Section 11.8), and candidate enumeration's
   completeness (Section 11.2). Ensure it states the converse for the rest: they name how a
   transport broke, and no rule in this specification disposes of a tracker failure by which of them
   occurred — Section 11.4's own orchestrator-behavior bullets dispose by where the failure arose.
   Done when a category added later can be levelled by applying the stated predicate rather than by
   analogy.

3. **`SPEC.md`, Section 11.4, openness and the documentation obligation.** Ensure the section states
   that the set is not closed: an implementation MAY define additional categories for conditions
   these do not name, and MUST document any it defines (Section 19). Follow the shape Section 5.5
   already uses for its class set. Done when the clause exists and names Section 19.

4. **`SPEC.md`, Section 10.6 (Timeouts and Error Mapping), openness and the documentation
   obligation.** Ensure the "Error mapping (RECOMMENDED normalized categories)" list carries the
   same clause: the set is not closed, an implementation MAY define additional categories, and MUST
   document any it defines (Section 19). The categories themselves keep their RECOMMENDED level —
   nothing in this specification branches on which one a turn failed with, which is the property
   that levels Section 11.4's four and does not level these. Done when the clause exists and the
   level is unchanged.

5. **`SPEC.md`, Section 17.3 (Issue Tracker Client).** The three checks naming the four already
   assert the behavior this decision levels and are kept as they stand. Ensure the check that reads
   "Error mapping covers transport failures, unsuccessful status, backend-reported errors, and
   malformed payloads (the transport-neutral categories of Section 11.4)" also states that the four
   REQUIRED spellings are reported under those names, so the matrix says which of its assertions is
   about a name and which is about a behavior. Done when no check in the section requires a spelling
   the section it cites calls advisory.

6. **`SPEC.md`, Section 18.1.2 (Broker Core Conformance).** Ensure the two bullets naming
   `tracker_unsupported_operation` and `tracker_state_unreachable` / `tracker_state_conflict` state
   that these are REQUIRED spellings (Section 11.4), so the checklist bullet can be implemented
   without opening Section 11.4 to learn whether the name is binding. Done when the bullets name the
   level alongside the token.

7. **`SPEC.md`, Section 19 (Conformance Statement).** Ensure the "MUST record" enumeration of
   documented obligations also names the tracker error categories defined beyond Section 11.4's set
   and the agent-runner error categories defined beyond Section 10.6's, alongside the existing
   entries. Done when both obligations are reachable from Section 19 without reading Sections 10.6
   and 11.4.

8. **`CONFORMANCE-STATEMENT-TEMPLATE.md`.** Ensure the table carries a row for each new obligation,
   in the shape of the existing "Workflow/template error classes defined beyond Section 5.5's five"
   row: one citing Section **11.4** for tracker error categories defined beyond the set, and one
   citing Section **10.6** for agent-runner error categories defined beyond the set, each with a
   `<token + condition for each, or none>` placeholder. The section number in each row's citation
   MUST be the subsection carrying the obligation rather than the chapter, so `python3
   scripts/validate_spec_consistency.py` check 2 matches the section it was written for. Done when
   the check reports `0 error(s), 0 warning(s)`.

9. **`conformance/vocabulary.json`, `tracker_error_categories`.** Ensure the group records the
   two-level shape rather than one `requirement_level` over all entries: the four REQUIRED entries
   carry their level per entry, the group's own level describes the rest, and the `note` states the
   predicate in brief and that the set is open with additions documented. Ensure the `note` no
   longer says the Section 17.3 disagreement is "recorded in `conformance/README.md` rather than
   resolved here", that sentence's subject having been resolved. Done when the registry can be read
   for a token's level without consulting `SPEC.md`, and when check 4 still passes.

10. **`conformance/vocabulary.json`, `agent_error_categories`.** Ensure its `note` records that the
    set is open and that an added category MUST be documented (Section 10.6), keeping the group's
    RECOMMENDED level and the existing note about the three spellings it shares with Section 10.4's
    events. Done when both RECOMMENDED registries state their openness the same way.

11. **`conformance/README.md`.** Ensure the open finding whose heading begins "**Section 17.3
    requires four RECOMMENDED tracker categories by name" is rewritten as resolved, naming this
    decision, in the file's own voice: what the finding recorded (a matrix requiring four advisory
    names), what measurement added (the four are spelled into normative prose at Sections 11.2, 11.7
    and 11.8, while four of the remaining seven occur only in the list that defines them and three
    occur nowhere else at all), what the level cost (a caller told to branch on a name the
    specification permitted to differ), and what checks now. Ensure the "Sections 10.6 and 10.4
    share three spellings (recorded, not a defect)" entry records that 10.6 gained the openness
    clause here. Done when no entry in the file still describes this asymmetry as open.

## Sites checked, no change needed

Recorded so a later reader does not re-derive them. Checked against `a4048bc`.

- Sections 11.2, 11.7 and 11.8 already spell the four in the sentences that fail an operation with
  them. They are the evidence for the level rather than sites needing an edit, and they read
  correctly once Section 11.4 says the spelling binds.
- Section 11.4's orchestrator-behavior bullets dispose of a tracker failure by where it arose, not
  by category. They are cited by step 2 as the converse evidence and are unchanged.
- Section 14.2's `tracker_failures` disposition is over Section 14.1's failure class, not over these
  categories, and takes two dispositions for a reason decision 0104 records. Unaffected.
- Section 6.4 (the config cheat sheet) carries no error-category rows; this decision adds no
  configuration key.
- `conformance/vectors/` gains nothing. The tracker surface is deferred to the `Real Integration
  Profile` (Section 17.8), and a requirement level is an assignment rather than a function of
  inputs.
- `VCSX-SPEC.md` and `VCSX-CONTRACT.md` are unaffected: the engine's `reasons` and `config_reasons`
  registries are its own, and no engine document carries a tracker error category.

## Cross-cutting sync

- Section 6.4 cheat sheet: no change (step list above).
- Section 17 test matrix: step 5.
- Section 18 checklist: step 6.
- Conformance Statement template: **two rows owed**, step 8. This decision creates two new MUST
  document obligations — additional tracker categories (Section 11.4) and additional agent-runner
  categories (Section 10.6) — and `CLAUDE.md` requires a row for each.
  `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` is unchanged.

## Anchor changes

None. All eleven tokens keep their spelling. No section is renamed, added, or removed. What changes
is the requirement level attached to four of them.

## Status

Applied to `SPEC.md` (Sections 10.6, 11.4, 17.3, 18.1.2, 19),
`CONFORMANCE-STATEMENT-TEMPLATE.md`, `conformance/vocabulary.json` and `conformance/README.md` on
branch `apply-0162-tracker-category-levels`.
