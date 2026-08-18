# Plan — 0132 Nine derived artifacts, and the enumerations they drifted from

## Scope

- `SPEC.md` — Section 17's registry enumeration; Section 19's Statement enumeration; Section 9.4's
  hook key names; Section 9.7's cross-document citation; Section 18's checklist hook-timeout line.
- `VCSX-SPEC.md` — Section 13.3's Statement enumeration; the task-model field list.
- `VCSX-CONTRACT.md` — Section 8's task field list.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — five obligation rows.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — two obligation rows.
- `conformance/vocabulary.json` — three new groups.
- `conformance/README.md` — coverage table and reader list for the three new groups.
- `scripts/validate_spec_consistency.py` — new.

No normative requirement changes. No `Implementation-defined` behavior and no "MUST document"
obligation is added, so `CLAUDE.md`'s template-row rule is checked and not triggered by this
decision's own edits — the rows it adds are for obligations that already existed.

## Steps

1. **`SPEC.md`, Section 17 "Test and Validation Matrix", the sentence beginning "The token sets this
   specification names".** Ensure the enumeration names every group `conformance/vocabulary.json`
   publishes, including the emitted event envelope fields (Sections 10.4, 10.7), the neutral
   token-usage record (Section 13.5), and the Orchestrator Runtime State fields with the recovery
   class stated for each (Sections 4.1.8, 14.3). Ensure the same sentence names the layer profiles,
   the validation profiles, and the deployment topologies. Ensure the clause naming who reads the
   registry admits a Conformance Statement author alongside an implementation and a repository
   author. *Done when:* every group name in `conformance/vocabulary.json` has a phrase in that
   sentence, and no phrase names a group that does not exist.

2. **`conformance/vocabulary.json`.** Ensure groups `layer_profiles`, `validation_profiles` and
   `deployment_topologies` exist, in the shape `transition_triggers` uses — `spec_refs`, `note`,
   `requirement_level`, `exhaustive`, `entries` — carrying:
   - `layer_profiles`: `Broker Core Conformance`, `Daemon Conformance`. `exhaustive: true` (Section
     17: "It comprises two layer profiles").
   - `validation_profiles`: `Core Conformance`, `Extension Conformance`, `Real Integration Profile`,
     `Concurrency Stress`. `exhaustive: true`.
   - `deployment_topologies`: `daemon`, `interactive-agent`, `engine-direct`. `exhaustive: true`
     (Section 3.4: "Three deployment topologies compose the layers"). Each entry records the
     profiles it claims, since Section 3.4 states them per topology and `engine-direct` claims none
     defined in `SPEC.md`.
   *Done when:* each group's `entries` match its cited section verbatim and `schema_version` is
   unchanged, group addition being additive (decision 0131's reasoning for the same case).

3. **`conformance/README.md`, the "What the slice covers" table and the reader list.** Ensure the
   three new groups have rows citing Sections 3.4 and 17, and that the Conformance Statement author
   bullet names them as what it reads for its conformance-claim and topology fields. *Done when:*
   the table has one row per group in `conformance/vocabulary.json`.

4. **`CONFORMANCE-STATEMENT-TEMPLATE.md`, Section 4.1 "Core".** Ensure a row exists for each of:
   the composed environment set an agent receives (9.6); the carrier by which an issue names its
   target (9.7); how it is established that no other route can write the policy branch (15.4); how a
   host-side unit is resolved (15.4); and — in Section 4.2, being extension-scoped — the aggregation
   sink and retention (13.5). *Done when:* no section carrying an `Implementation-defined` or
   "MUST document" site in `SPEC.md` is answered by zero rows, and every section answered by fewer
   rows than it has obligations has been checked by hand and recorded below.

5. **`SPEC.md`, Section 19 "Conformance Statement", the bullet beginning "A resolution for every".**
   Ensure the enumeration names the four obligations added in step 4 that it does not already carry
   — 9.7's target carrier, 15.4's two, and 13.5's sink and retention. The composed environment set is
   already there. *Done when:* each row added in step 4 has a clause above it in Section 19.

6. **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`, Section 3.** Ensure a row exists for the bound a forge
   backend imposes on its search for a work branch's pull request (9.2), and for
   `worktree_revision()`'s form and how a backend derives it (9.1). *Done when:* both are present
   with the per-backend framing the neighbouring forge rows use.

7. **`VCSX-SPEC.md`, Section 13.3 "Conformance Statement", the capability-descriptor bullet.** Ensure
   the enumeration names `worktree_revision()`'s form and derivation. *Done when:* every
   "MUST be documented (Section 13.3)" site in `VCSX-SPEC.md` is named in that section's list.

8. **`SPEC.md`, Section 9.4 "Workspace Hooks".** Ensure the four supported hooks are named
   `hooks.workspace.after_create`, `hooks.workspace.before_run`, `hooks.workspace.after_run`,
   `hooks.workspace.before_remove`, and that the execution contract's timeout key is
   `hooks.workspace.timeout_ms`. *Done when:* no `hooks.` key outside the `hooks.workspace.` and
   `hooks.engine.` namespaces appears anywhere in `SPEC.md`.

9. **`SPEC.md`, Section 18.1.2, the checklist line "Hook timeout config".** Ensure it names
   `hooks.workspace.timeout_ms`. *Done when:* it matches Section 6.4's cheat-sheet spelling.

10. **`SPEC.md`, Section 9.7 "Repository Provisioning and the VCS Engine", the sentence containing "a
    branch named inside that file cannot select the revision the file is read from".** Ensure the
    parenthetical cites `VCSX-SPEC.md` Sections 6.4 and 8.1 rather than `VCSX-CONTRACT.md` Section
    15.4. *Done when:* every `<doc>.md` Section `N` reference in the three documents resolves to a
    heading in the document it names.

11. **`VCSX-CONTRACT.md`, Section 8 "Task Model and Broker Task Verbs", the task field list.** Ensure
    the parent and tracker-link entries name their fields as tokens — `parent` and `tracker_link` —
    in the shape the four fields above them use, keeping the statement that both are optional.
    *Done when:* both strings appear as code tokens in the list.

12. **`VCSX-SPEC.md`, the task-model sentence containing "an optional parent, and an optional tracker
    link".** Ensure it names the same two tokens. *Done when:* every entry in
    `conformance/vcsx/vocabulary.json`'s `task_model.fields` occurs as a token in
    `VCSX-CONTRACT.md` or `VCSX-SPEC.md`.

13. **`SPEC.md`, Section 5 "Configuration Contracts", the sentence containing "Symphony consumes it
    through the VCS engine contract".** Ensure the parenthetical cites `VCSX-CONTRACT.md` Section 4
    "`repo.policy.toml` (Config Surface)" rather than Section 3.4, which that document does not
    have. *Done when:* check 1 of the validator reports no unresolved reference. **Found by the
    validator on its first run, not by the review pass.**

14. **`CONFORMANCE-STATEMENT-TEMPLATE.md`, Section 5 "State Recovery-Class Assignments", and
    `SPEC.md` Section 19's recovery-class bullet.** Ensure the reset consequence Section 14.3
    requires of every `Ephemeral` field has a place to be recorded — a fourth column on the
    recovery-class table — and that Section 19's bullet names it beside the class assignment. Ensure
    the template heading cites Section 14.3 so the surface is machine-visible. *Done when:* Section
    14.3's three obligations are each answered by a named surface. **Found by the validator's
    warning tier, not by the review pass.**

15. **`scripts/validate_spec_consistency.py`.** Ensure it exists and reports, without arguments and
    from the repository root: unresolved section references within and across the three documents;
    sections whose obligations outnumber the matching template's rows; config keys used outside
    the namespace their defining section fixes; and registry entries with no occurrence in the
    document that governs them. Ensure its docstring states both known limits — the obligation check
    matches per section, so a row answering a different obligation in the same section passes; and
    the registry check is a substring test, so a token that is also an English word passes whether
    or not the document fixes it. *Done when:* the script exits non-zero on the tree before this
    decision's edits and zero after, and every residual warning is accounted for below.

## Residual warnings, and why each is not a gap

The validator exits zero with three warnings. Each was checked by hand; none is a missing answer.

- **`SPEC.md` Section 14.2 — 4 obligations, 3 rows.** The fourth is `node_provisioning_failures`'
  park-vs-retry choice, which has a row filed under Section 9.11, the extension that defines it.
- **`VCSX-SPEC.md` Section 6.6 — 4 obligations, 3 rows.** The fourth is not an obligation: the
  `[hooks.engine]` TOML example carries the comment "its form is Implementation-defined", which
  restates the obligation stated in the prose below it. A sentence-level count sees two.
- **`VCSX-SPEC.md` Section 8.4 — 2 obligations, 1 row.** The second is the `need` vocabulary, which
  the template answers with a whole section (Section 5, "`need` Vocabulary Emitted") whose heading
  carries no section citation for the validator to count.

## Cross-cutting sync

- Section 6.4's cheat sheet already carries the prefixed hook spellings; no change.
- Section 17's registry paragraph is edited by step 1; no test-matrix row changes, since the decision
  adds no behavior a matrix row could assert.
- Section 18's checklist changes only the hook-timeout key (step 9).
- `VCSX-SPEC.md` Sections 13.1 and 13.2 are unchanged; step 7 touches 13.3 only.
- Both Conformance Statement templates gain rows (steps 4, 6); no obligation is added by this
  decision, so no further row is owed.

## Anchor changes

None. No section is retitled, and no code token is renamed or removed. Two prose phrases become
tokens (`parent`, `tracker_link`), which adds anchors rather than changing them.

## Status

Applied. Issues #83, #84, #85.
