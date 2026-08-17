# Plan — 0103 Which prose enumerations are published, and the trigger vocabulary as data

## Scope

`SPEC.md`: Section 11.6 "Workflow State Machine and Transition Triggers" (the trigger spellings gain
a requirement level and the vocabulary is named as published), Section 6.3 "Dispatch Preflight
Validation" (an `on` outside the vocabulary is a configuration error), Section 17's registry
paragraph, and Section 17.3 "Issue Tracker Client".

`conformance/vocabulary.json`: one new group, `transition_triggers`.

`conformance/README.md`: the "Deferred to later slices" preamble gains the reader test and every
bullet states the reader it lacks; the Section 11.6 half of the orchestration bullet is removed as
published; the coverage table, the closed-set paragraph, and "Surfaced findings".

Section 14.1 is **not touched**: decision 0104 applies the same rule to it, and the deferral list
records it as pending that decision rather than as lacking a reader.

## Steps

1. **`Workflow State Machine and Transition Triggers` — the spellings are REQUIRED.** Ensure the
   `Triggers:` passage states that the ten spellings are REQUIRED: an implementation MUST match a
   transition's `on` value against these tokens, so a `repo.policy.toml` authored against one
   implementation binds the same triggers on another. State it over what a consumer can check — the
   same policy file producing the same transitions — not over an implementation's internal matching.
   Done-condition: the section carries an RFC 2119 keyword over the spellings, where it carries none
   today.

2. **`Workflow State Machine and Transition Triggers` — where the vocabulary is published.** Ensure
   the passage records that the vocabulary is published as data (Section 17), and that the
   agent-emitted signals are additionally published by the VCS engine's own registry, which is the
   authority for them (`VCSX-SPEC.md` Section 5.1). Done-condition: a reader of Section 11.6 alone
   can find the token set without reading Section 17.

3. **`Dispatch Preflight Validation` — an unknown trigger is a configuration error.** Ensure the
   validation-checks list carries: a `tracker.transitions` entry whose `on` is not in Section 11.6's
   vocabulary is a configuration error. Ensure Section 11.6's existing sentence — "A trigger that
   fires with no matching `from`-state transition performs no transition" — is not contradicted: it
   governs a *valid* trigger nobody bound, where this governs a name outside the vocabulary.
   Done-condition: the two sentences can both be read literally, and a misspelled `on` is rejected
   before dispatch rather than silently never firing.

4. **`Test and Validation Matrix` — the registry paragraph.** Ensure the sentence listing the
   published token sets names the transition triggers (Section 11.6). Done-condition: every group in
   `vocabulary.json` is traceable to a set this paragraph names.

5. **`Issue Tracker Client` — the check.** Ensure the bullet beginning "Tracker transitions follow a
   deterministic policy graph" states that an `on` outside the vocabulary is a configuration error,
   alongside the duplicate `(from, on)` it already names. Done-condition: the new preflight check
   has a conformance check behind it.

6. **`vocabulary.json` — `transition_triggers`.** Ensure the group exists with `spec_refs` citing
   Sections 11.6, 8.10 and 9.12, `requirement_level: "REQUIRED"`, `exhaustive: true` (Section 11.6
   calls the vocabulary closed), and all ten tokens each carrying its condition and `core` (`false`
   for `tasks:all_closed` and `task:#needs_help`, which the OPTIONAL task-management extension
   owns). Ensure the `note` records the three origins, that the engine registry's `signals` group
   also publishes the five agent-emitted tokens and is the authority for them, and that Section 6.3
   rejects an `on` outside the set. Done-condition: a repository author can validate a
   `tracker.transitions` `on` value against this group alone.

7. **`conformance/README.md` — the reader test.** Ensure the "Deferred to later slices" preamble
   states the test: a prose enumeration is published when something outside the implementation's own
   source spells it — a repository author writing configuration, a Conformance Statement author
   filling a table, or a conformance check asserting a value. Done-condition: the list is governed
   by one re-askable question rather than a reason per bullet.

8. **`conformance/README.md` — every bullet states its reader.** Ensure each remaining bullet names
   the reader it lacks rather than a historical reason: Section 10.8's codes are unenumerated;
   Section 7.1's states reach no monitoring surface (Section 13.3 exposes none); Section 7.2's
   phases are asserted by nothing outside Section 7.2; Section 7.3's events are not a wire
   vocabulary. Ensure Section 14.1 is recorded as **pending decision 0104**, not as lacking a
   reader. Ensure the Section 11.6 half of the orchestration bullet is removed as published.
   Done-condition: no bullet carries a reason that belongs to a different set, and the challenges
   0102 recorded are resolved rather than left standing.

9. **`conformance/README.md` — coverage table and closed-set paragraph.** Ensure the table carries a
   `transition_triggers` row and the closed-set paragraph accounts for it — the first group whose
   closedness the prose states, which is worth saying beside the groups that are open.
   Done-condition: the schema section documents every field the file uses.

10. **`conformance/README.md` — the surfaced finding.** Ensure "Surfaced findings" records that the
    ownership question the orchestration bullet deferred behind had been answered by decision 0055
    before the bullet was written — signals are consumer-raised and have no upstream — as resolved
    by this decision. Done-condition: the finding is readable without reference to this decision
    folder.

## Cross-cutting sync

Section 6.4's config cheat sheet: `tracker.transitions` gains no new key, but its validation is now
stated in Section 6.3 — check the cheat-sheet row does not contradict it. Section 17 is covered by
steps 4 and 5; Section 18 gains nothing, since no new conformance item is created beyond the check.

## Anchor changes

None. No token in `SPEC.md` is renamed, added or removed: Section 11.6's ten triggers gain a
requirement level and a published group. One registry group name is added: `transition_triggers`.

## Status

Applied to `SPEC.md`, `conformance/vocabulary.json` and `conformance/README.md`.
