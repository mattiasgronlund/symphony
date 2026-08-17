# Plan — 0103 Which prose enumerations are published, and what their token is

## Scope

`SPEC.md`: Section 14.1 "Failure Classes" (each class gains an identifier-shaped token beside its
prose name), Section 14.2 "Recovery Behavior", Sections 17.2, 17.4 and 18.1.4 (the checks that name
a class), Section 19 "Conformance Statement", Section 11.6 "Workflow State Machine and Transition
Triggers" (the run outcomes are named as a published set), and Section 17's registry paragraph.

`conformance/vocabulary.json`: two new groups — `transition_triggers` (Section 11.6's run outcomes)
and `failure_classes` (Section 14.1's nine, plus the token shape).

`conformance/README.md`: the Schema section, the "What the slice covers" table, the not-closed-set
paragraph, and the "Deferred to later slices" list, which gains the reader test and loses the two
bullets this decision publishes.

`CONFORMANCE-STATEMENT-TEMPLATE.md`: the two `MUST document` rows named by failure class, and the
recovery-disposition table.

Sections 7.1, 7.2 and 7.3 are **recorded, not published**: each keeps a deferral bullet naming the
reader it lacks.

## Steps

1. **`Failure Classes` — each class gains a token.** Ensure every one of the nine carries an
   identifier-shaped token beside the Title Case name it already has, in the shape Section 14.1
   already uses for `token_budget_exceeded`. Done-condition: Section 14.1 spells failure categories
   one way, and a reader can tell for each of the nine what an implementation branches on.

2. **`Failure Classes` — the set's openness is stated.** Ensure the closing note's permission for an
   OPTIONAL extension to define additional categories is stated as the set being open, so the
   registry can record `exhaustive: false` from the prose rather than from `token_budget_exceeded`'s
   existence. Done-condition: a reader can tell whether a generated type may close the enum without
   inspecting Section 8.8.

3. **`Recovery Behavior` — the recovery mapping uses the tokens.** Ensure Section 14.2's per-class
   dispositions address each class by its token, keeping the prose name where the prose reads
   better. Done-condition: every disposition is traceable to exactly one token.

4. **The checks that name a class.** Ensure Sections 17.2, 17.4 and 18.1.4 name the token alongside
   or instead of the prose title, so a conformance check asserts something spelled identically
   everywhere. Done-condition: `grep -n 'Engine Invocation Failures\|Repository Provisioning
   Failures' SPEC.md` shows no occurrence outside Sections 14.1 and 14.2 that lacks its token.

5. **`Conformance Statement` — the class-named rows.** Ensure Section 19 and
   `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1's two park-vs-retry rows are keyed by token, so a
   statement author transcribes a token rather than a title. Done-condition: no row in the template
   names a failure class only by its prose title.

6. **`Workflow State Machine and Transition Triggers` — the run outcomes are a published set.**
   Ensure Section 11.6 states that the trigger vocabulary's two origins are published separately —
   the agent-emitted signals by the engine (`VCSX-SPEC.md` Section 5.1) and the
   orchestrator-observed run outcomes here — so a reader of Section 11.6 alone can find both.
   Done-condition: Section 11.6 names where each half is published, and neither document restates
   the other's half.

7. **`Test and Validation Matrix` — the registry paragraph.** Ensure the sentence listing the
   published token sets names the transition triggers (Section 11.6) and the failure classes
   (Section 14.1). Done-condition: every group in `vocabulary.json` is traceable to a set this
   paragraph names.

8. **`vocabulary.json` — `transition_triggers`.** Ensure the group exists with `spec_refs` citing
   Sections 11.6 and 7.3, `requirement_level: "REQUIRED"` (a repository writes these and Section
   11.6 calls the vocabulary closed), `exhaustive: true` for the run outcomes it carries, and the
   five tokens with the condition each names. Ensure the `note` records that the agent-emitted half
   is `signals` in `conformance/vcsx/vocabulary.json` and is deliberately not restated, and that
   Section 11.6 makes an unmatched trigger a silent no-op — which is why the spelling is REQUIRED
   rather than RECOMMENDED. Done-condition: a repository author can check a `repo.policy.toml` `on`
   value against the two registries and nothing else.

9. **`vocabulary.json` — `failure_classes`.** Ensure the group exists with `spec_refs` citing
   Sections 14.1 and 14.2, `exhaustive: false` (step 2), each entry carrying its token, its prose
   name, its Section 14.2 recovery disposition, and whether it is core or extension-defined (`Node
   Provisioning Failures` and `Executor Bring-up Failures` are the node-scheduler extension's;
   `token_budget_exceeded` is the budget extension's). Done-condition: a Conformance Statement
   author can fill the recovery-disposition table from this group alone.

10. **`conformance/README.md` — the reader test.** Ensure the "Deferred to later slices" preamble
    states the test this decision names: a prose enumeration is published when something outside the
    implementation's own source spells it — a repository author writing configuration, a Conformance
    Statement author filling a table, or a conformance check asserting a value. Done-condition:
    every bullet in the list states the reader it lacks, so a later reader re-asks one question
    rather than re-deriving a reason.

11. **`conformance/README.md` — the bullets this decision resolves and the ones it does not.**
    Ensure the "Orchestration states and transition triggers" bullet is split: Section 11.6's run
    outcomes are published (step 8), Section 7.1's states and Section 7.3's internal lifecycle
    events keep bullets naming the missing reader (no snapshot, status surface or API response
    exposes a state; Section 7.3's events are not a wire vocabulary). Ensure the "Failure classes"
    bullet is removed as published, and the Section 7.2 bullet records that the measurement in this
    decision's `Background.md` is its reconsideration check. Done-condition: no bullet carries a
    reason that belongs to a different set.

12. **`conformance/README.md` — schema, coverage table, closed-set paragraph.** Ensure the group
    field list documents any new entry field the two groups introduce, the coverage table carries a
    row for each, and the not-closed-set paragraph states the correct count and each group's reason.
    Done-condition: the schema documents every field the file uses.

13. **`conformance/README.md` — the surfaced finding.** Ensure "Surfaced findings" records that
    Section 14.1 spelled failure categories two ways before this decision — nine Title Case titles
    and one snake_case category — as resolved by step 1. Done-condition: the finding is readable
    without reference to this decision folder.

## Cross-cutting sync

Section 6.4's config cheat sheet gains nothing: no configuration key changes, though
`tracker.transitions` values are now checkable against `transition_triggers`. Section 17 is covered
by steps 4 and 7; Section 18 by step 4; Section 19 by step 5.

## Anchor changes

**Pending acceptance.** If applied, Section 14.1's nine failure classes gain identifier-shaped
tokens as new anchors; the Title Case names are retained as prose names, so no anchor is removed.
Two registry group names are added: `transition_triggers`, `failure_classes`. Nothing is renamed.

## Status

Not started. Proposed pending acceptance; `SPEC.md` is unchanged.
