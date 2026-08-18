# Plan — 0134 A vocabulary two documents closed and one left the engine to extend

## Scope

- `VCSX-SPEC.md` — "Operation Set", "Reason-Token Registry", "Triggers", "Validation", "Versioning
  and the Version Grammar", "VCS Backend Plugin", "Capability Descriptors", "Test Matrix",
  "Implementation Checklist", "Conformance Statement", "Alignment with `VCSX-CONTRACT.md`".
- `VCSX-CONTRACT.md` — "Engine Operations and Typed Results", "Lifecycle Positions".
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — the Core Conformance checklist, the `need` vocabulary
  preamble, "VCS Backends", "Forge Backends".
- `conformance/vcsx/vocabulary.json` and `conformance/vcsx/README.md`.
- `scripts/validate_spec_consistency.py`.
- `SPEC.md` — **no change**. It already lists four positions and all eleven operations, closed, and
  nowhere admits engine extension. Its Sections 6.4, 17 and 18 therefore need no sync.

## Steps

1. **`VCSX-SPEC.md` "Operation Set" — the `load_policy` entry carries the `Read-only` marker.** The
   operation reads a policy document and changes none of the three things that term quantifies over,
   so the marker is the property the registry's `read_only` field derives from rather than a property
   the registry invents. *Done when:* the entry ends `reported as configuration errors. Read-only.`
2. **`VCSX-SPEC.md` "Operation Set" — the closing paragraph states the sets as this specification's.**
   Ensure the paragraph opens with the specification fixing the operation set and the lifecycle
   positions, an engine defining neither of its own, and both extended only by a MINOR release, and
   that it retains verbatim the two exception clauses: `provision` has no position because the policy
   that would carry the gate is not readable when it must first run, and `await_checks` has none
   because a gate before a wait would run a unit that inspects nothing. *Done when:* the string
   `MAY define additional operations` does not occur in the file.
3. **`VCSX-SPEC.md` "Operation Set" — the no-position rule is stated over operations, not listed.**
   Replace the two-item list in "An operation gated at no fixed position — `integrate` and `pull` —
   enters none wherever it is dispatched" with the rule over any operation carrying no lifecycle
   position. *Done when:* the sentence names no operation.
4. **`VCSX-SPEC.md` "Reason-Token Registry" — the closing paragraph carries the invariant, not a
   count.** Ensure the paragraph states that an operation with no `before:<op>` position carries
   neither `blocked` nor `hook_unanswered`, without naming the operations it covers, and that the
   trailing engine-extension sentence is re-framed to an operation a MINOR release introduces.
   *Done when:* the phrase `none of the four` does not occur, and the invariant is true of
   `await_checks` and `provision` without either being named.
5. **`VCSX-SPEC.md` "Triggers" — the lifecycle-position bullet is the whole list.** *Done when:* the
   parenthetical `(and any engine-defined `before:<op>`)` is gone and the bullet still states that a
   position is matched exactly, has no class form, and that `provision` raises no trigger.
6. **`VCSX-SPEC.md` "Validation" — `position_cycle` is judged over the positions the specification
   defines.** *Done when:* the sentence reads "the `before:<op>` positions Section 4.1 defines".
7. **`VCSX-SPEC.md` "Versioning and the Version Grammar" — a MINOR may add a lifecycle position, and
   the sets belong to the release.** Ensure `new lifecycle positions` sits beside `new operations` in
   the MINOR-additions bullet, and that a following bullet states: the two sets are the
   specification's rather than an engine's; a token outside the running version's set is
   `unknown_trigger` on every conforming engine; a MINOR may add a position where it may not add a
   trigger kind or a key component, on the argument this section's second bullet already makes for
   an edge's key, run in the opposite direction; and removal of a position or an operation is MAJOR.
   *Done when:* both bullets exist and no new `Implementation-defined` or MUST-document obligation is
   introduced.
8. **`VCSX-SPEC.md` "VCS Backend Plugin" — the minimum-not-maximum claim loses its engine-extension
   premise.** Ensure the paragraph still says the capability list is a minimum every backend MUST
   provide rather than a maximum, now on the ground that the operation set is the specification's so
   no engine adds one requiring more, and that a capability a backend provides beyond the list is
   that backend's own rather than shared surface. *Done when:* the MUST-document clause about
   capabilities an engine-added operation requires is gone and the minimum-not-maximum claim is
   otherwise unchanged. Note the trap: this section defines no OPTIONAL VCS capability — the
   OPTIONAL ones are "Forge Backend Plugin"'s — so the paragraph must not be rewritten as though it
   did.
9. **`VCSX-SPEC.md` "Capability Descriptors" — the first-use half is the OPTIONAL capability and the
   descriptor field.** With engine-added operations gone, two of that enumeration's three items go
   with them; what survives is an OPTIONAL capability an operation reaches against a backend that
   does **not** declare it, and a descriptor field answerable only after the checkout is open. A
   *declared* capability is supported and cannot surface as `unsupported`, so the survivor must be
   stated over the undeclared case. *Done when:* "an operation an engine defines beyond Section 4.1"
   no longer appears in the first-use enumeration, and the Conformance Statement sentence names the
   optional capability or descriptor field the claim was demonstrated against.
10. **`VCSX-SPEC.md` "Conformance Statement" — the Statement records no engine-added operation's
    capabilities.** *Done when:* the clause "the capabilities any operation it defines beyond Section
    4.1 requires of a backend (Section 9.1)" is gone from the capability-descriptors bullet and the
    rest of that bullet is unchanged.
11. **`VCSX-SPEC.md` "Test Matrix" — the trigger-kinds row asserts a version-uniform vocabulary.**
    Ensure the row still asserts `unknown_trigger` for a token that is neither a known position nor a
    result form, and additionally that the vocabulary a token is judged against is the running
    version's rather than the engine's, so two conforming engines at one version accept and refuse
    the same tokens. Ensure the plugins row's first-use sentence matches step 9. *Done when:* both
    rows read as stated.
12. **`VCSX-SPEC.md` "Implementation Checklist" — the operation-set bullet states the sets as fixed.**
    *Done when:* the bullet names the operation set and the lifecycle positions as this specification
    fixes them, neither extended by the engine.
13. **`VCSX-SPEC.md` "Alignment with `VCSX-CONTRACT.md`" — the two are aligned as sets, not only as
    spellings.** *Done when:* the section states that the operations and the lifecycle positions are
    additionally fixed as sets by the specification, so `VCSX-CONTRACT.md`'s closed lists are the
    whole of each at a version rather than a core an engine extends.
14. **`VCSX-CONTRACT.md` "Engine Operations and Typed Results" — the list is complete and closed.**
    Ensure `status`, `diff` and `pull` are present with one-line glosses at contract altitude
    condensed from `VCSX-SPEC.md` "Operation Set" and importing none of its field-level outputs;
    ensure the introducing sentence closes the list; and ensure a following paragraph states that the
    set is fixed at a version, that an engine defines no operation of its own, and that an operation
    is added only by a MINOR release of the full engine spec. *Done when:* the section carries eleven
    `- ` operation bullets, the word `include` does not introduce them, and the eleven names match
    `VCSX-SPEC.md` "Operation Set" exactly.
15. **`VCSX-CONTRACT.md` "Lifecycle Positions" — the fixed points are fixed at a version.** *Done
    when:* the opening sentence adds that an engine defines no position of its own and that a
    position is added only by a MINOR release of the full engine spec, and the four positions are
    otherwise unchanged.
16. **`conformance/vcsx/vocabulary.json` — the `operations` group carries eleven entries including
    `load_policy`.** Ensure the entry carries `read_only: true` and `lifecycle_position: null` and a
    note restating what "Operation Set" states about it. Ensure `operations.note` and
    `lifecycle_positions.note` carry the version-owned framing in place of "The required set. An
    engine MAY define additional operations and their before:<op> positions." *Done when:* the file
    parses, `operations` has eleven entries, and no note claims an engine may add to either set.
17. **`conformance/vcsx/vocabulary.json` — `unanswered_gates`' `position` gains
    `values_from: "lifecycle_positions"`.** With the position set closed, the field's value space is
    exactly that group, which is the registry's own stated condition for authoring a link. *Done
    when:* the field carries the link and its `meaning` records why the link is now authorable.
18. **`conformance/vcsx/README.md` — the two paragraphs premised on the open set are repaired.** The
    `values_from` discipline's worked counter-example is `unperformed_intents`' `action`; the
    `position` case is recorded as resolved by this decision. The `operations` normalization note
    states the `lifecycle_position: null` rule rather than listing the operations it covers. *Done
    when:* neither paragraph calls `lifecycle_positions` the *required* set.
19. **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — the three engine-extension rows are narrowed.** The
    Core Conformance checklist item loses "required" and gains "neither extended by this engine"; the
    "VCS Backends" capability table is introduced as the capabilities a backend provides beyond the
    Section 9.1 minimum, with its columns renamed to match; the "Forge Backends" first-use row reads
    `<OPTIONAL capability / descriptor field, or "not claimed">`. *Done when:* the string
    `engine-added operation` does not occur in the file. No template row is **added**: this decision
    creates no `Implementation-defined` or MUST-document obligation.
20. **`scripts/validate_spec_consistency.py` — check 2 re-homes an extension's obligation.** In
    `obligation_sentences`, scan back from the match to the nearest column-0 `- ` line and, where it
    declares `OPTIONAL extension, Sections? N.M` and no blank line intervenes, attribute the
    obligation to that section instead of the enclosing one. *Done when:* `SPEC.md` Section 14.2
    reports three obligations against three rows and Section 9.11 three against four, and `covers()`
    is unchanged.
21. **`scripts/validate_spec_consistency.py` — check 2 skips fenced code blocks.** Mask fenced
    regions with spaces, preserving newlines so offsets and section arithmetic still hold. *Done
    when:* `VCSX-SPEC.md` Section 6.6 reports three obligations against three rows.
22. **`scripts/validate_spec_consistency.py` — check 6 reads the closed groups prose→registry.** Add
    a module-level `CLOSED_GROUPS` table naming `operations` and `lifecycle_positions`, the document
    and sections that fix each, and the pattern that spells a token there; error on any token the
    prose defines and the registry omits. *Done when:* dropping `pull` from the registry's
    `operations`, or `before:create_pr` from its `lifecycle_positions`, makes the script exit 1 with
    a message naming the omitted token, and restoring each returns it to 0 errors.
23. **The script's docstring records check 6 and its narrowness.** *Done when:* the checks list has
    six entries and the deliberate-limits list has four, the fourth stating that a group the table
    does not name is unchecked in that direction.

## Cross-cutting sync

- `SPEC.md` Sections 6.4, 17 and 18 — no change. `SPEC.md` is not edited by this decision.
- `VCSX-SPEC.md` Section 13.1 (test matrix) — step 11, two rows.
- `VCSX-SPEC.md` Section 13.2 (implementation checklist) — step 12, one bullet.
- `VCSX-SPEC.md` Section 13.3 (Conformance Statement obligations) — step 10 **removes** an
  obligation and adds none.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — step 19 narrows three existing rows. Because the
  decision adds no `Implementation-defined` or "MUST document" obligation, no row is owed
  (`CLAUDE.md`'s rule, decision 0128).
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — unchanged; nothing in `SPEC.md` moved.

## Residual warnings, and why each is not a gap

The validator exits zero with one warning. Two of the three that stood before this decision are
repaired in the checker rather than in the documents (steps 20, 21), on the reasoning
`Background.md` records.

- **`VCSX-SPEC.md` Section 8.4 — 2 obligations, 1 row.** The second is the `need` vocabulary's own
  spec-level stability clause rather than a choice an engine makes, and the template answers it with
  a whole section ("`need` Vocabulary Emitted") whose heading carries no section citation for the
  validator to count. Recorded as a non-gap in decision 0132 and carried forward unchanged. No
  detector is worth writing: no general rule separates a spec-level MUST-be-documented from an
  implementation one.

## Anchor changes

No token is renamed or removed. The changes are to prose, to two registry `note` fields, and to
three rows of `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`; every operation name, position name, reason
token, configuration reason and capability name is spelled exactly as before.

One registry **membership** change: `load_policy` is added to `conformance/vcsx/vocabulary.json`'s
`operations` group, which previously published ten of the eleven operations `VCSX-SPEC.md`
"Operation Set" defines. The token is not new — the same file's `entry_points` group already carried
it — so nothing that referenced it needs chasing.

One marker addition: `VCSX-SPEC.md` "Operation Set" now marks `load_policy` **Read-only**, which is
the property the registry's `read_only: true` derives from. No enumeration of the read-only
operations exists in any document, so the marker has no list to be added to.

## Status

Applied to `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`,
`conformance/vcsx/vocabulary.json`, `conformance/vcsx/README.md` and
`scripts/validate_spec_consistency.py`. Issues #88, #89 and #90.
