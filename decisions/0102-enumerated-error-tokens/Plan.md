# Plan — 0102 The enumerated error tokens as data, and a class that names its condition

## Scope

`SPEC.md`: Section 5.5 "Workflow Validation and Error Surface" (the requirement level, the
condition-not-stage rule, a stated condition per class, and the set's openness), Section 17 "Test and
Validation Matrix" (the registry paragraph's list of published token sets), Section 17.1 "Workflow
and Config Parsing" (the checks name their tokens), Sections 18.1.1 and 18.1.3.

`conformance/vocabulary.json`: three new groups — `error_classes`, `tracker_error_categories`,
`agent_error_categories` — and the `requirement_level` group field they introduce.

`conformance/README.md`: the Token Registry preamble, the Schema section, the "What the slice covers"
table, the not-closed-set paragraph, the "Deferred to later slices" error bullet, and "Surfaced
findings".

`conformance/vectors/prompt-rendering.json`: the `description`'s cross-reference, and a
`template_parse_error` vector, which the corpus does not exercise today.

`CONFORMANCE-STATEMENT-TEMPLATE.md`: Section 4.1's `MUST document` table.

Sections 11.4 and 10.6 are **read from, not edited**: their requirement level is unchanged and this
decision publishes what they already state.

## Steps

1. **`Workflow Validation and Error Surface` — the spellings are normative.** Ensure the section
   states that the five spellings are REQUIRED: where one of the conditions occurs, the workflow
   loader or the prompt renderer MUST fail with the class named for it, cross-referencing the loader
   (Section 5.1 "WORKFLOW.md Discovery and Path Resolution"), the template contract (Section 5.4
   "Prompt Template Contract") and the failure semantics (Section 12.4 "Failure Semantics").
   Done-condition: the section carries an RFC 2119 keyword over the spellings, where it carries none
   today.

2. **`Workflow Validation and Error Surface` — the set is open.** Ensure the section states that an
   implementation MAY define additional classes for conditions the five do not name, MUST document
   any it defines, and MUST assign each one of the two dispatch gating behaviors the section already
   states. Done-condition: a reader can tell whether a generated type may close the enum, and the
   answer is no.

3. **`Workflow Validation and Error Surface` — a class names its condition, not its stage.** Ensure
   the section states that a class names the condition rather than the stage at which an
   implementation detects it: an unknown variable and an unknown filter are both
   `template_render_error` however early the template engine resolves them, and `template_parse_error`
   is reserved for a body that is not well-formed template syntax. State it over the class an
   implementation fails with, never over which pass performs the check. Done-condition: an
   implementation whose engine rejects an unknown filter while parsing can read the section and know
   it must still report `template_render_error`.

4. **`Workflow Validation and Error Surface` — every class states its condition.** Ensure each of the
   five carries the condition it names, in the annotation shape Section 11.4 "Error Handling
   Contract" already uses: `missing_workflow_file` — the file cannot be read at the resolved path;
   `workflow_parse_error` — the front matter is not well-formed YAML; `workflow_front_matter_not_a_map`
   — the front matter is well-formed YAML that does not decode to a map; `template_parse_error` — the
   prompt body is not well-formed template syntax; `template_render_error` — the body is well formed
   and names something the engine cannot resolve. Done-condition: no annotation names a phase, and in
   particular `template_parse_error` is no longer annotated "(during prompt rendering)".

5. **`Test and Validation Matrix` — the registry paragraph.** Ensure the sentence listing the token
   sets published beside the corpus ("the emitted runtime events…, the REQUIRED log context fields…")
   also names the workflow and template error classes (Section 5.5), the tracker error categories
   (Section 11.4), and the agent-runner error categories (Section 10.6). Done-condition: every group
   in `vocabulary.json` is traceable to a set this paragraph names.

6. **`Workflow and Config Parsing` — the checks name their tokens.** Ensure the three "returns typed
   error" bullets name `missing_workflow_file`, `workflow_parse_error` and
   `workflow_front_matter_not_a_map` respectively, and that the strict-rendering bullet names
   `template_render_error`. Ensure a bullet covers the classification rule of step 3 — a body that is
   not well-formed template syntax is `template_parse_error`, and an unknown filter is
   `template_render_error` whatever stage detects it. Done-condition: `grep -n 'returns typed error'
   SPEC.md` returns nothing.

7. **`REQUIRED for Conformance` — the conformance items.** Ensure Section 18.1.1's configuration
   bullet records that Section 5.5's error classes are REQUIRED spellings, and that Section 18.1.3's
   strict-prompt-rendering bullet names `template_render_error`. Done-condition: an implementer
   reading the checklist alone learns the spellings are part of conformance.

8. **`vocabulary.json` — `error_classes`.** Ensure the group exists with `spec_refs` citing Section
   5.5 (and Sections 5.1, 5.2, 5.4 where the conditions are defined), `requirement_level:
   "REQUIRED"`,
   `exhaustive: false`, a `note` carrying the condition-not-stage rule and the additional-class
   obligation, and five entries each carrying `token`, its condition, and `gating` valued
   `blocks_dispatch` for the first three and `fails_attempt` for the last two. Done-condition: the
   five tokens and the gating split can be read off the file without opening `SPEC.md`.

9. **`vocabulary.json` — `tracker_error_categories`.** Ensure the group exists with `spec_refs` citing
   Section 11.4, `requirement_level: "RECOMMENDED"`, and the eleven tokens carrying the condition
   Section 11.4 states for each — and no condition for the three it states none for. Ensure the
   `note` records that Section 17.3 "Issue Tracker Client" requires four of them by name —
   `tracker_unsupported_operation`, `tracker_state_unreachable`, `tracker_state_conflict`,
   `tracker_pagination_error`. Done-condition: the group's level and Section 11.4's opening sentence
   agree, and the four named in Section 17.3 are identifiable. The group carries no `exhaustive` key:
   Section 11.4 does not state that its set is open, and inferring it would be the registry deciding
   a question the prose left alone — the openness a generator needs follows from the level instead
   (step 11).

10. **`vocabulary.json` — `agent_error_categories`.** Ensure the group exists with `spec_refs` citing
    Section 10.6 "Timeouts and Error Mapping", `requirement_level: "RECOMMENDED"`, and the nine
    tokens as bare strings, since Section 10.6 states no condition for any of them. Ensure the `note`
    records that `turn_failed`, `turn_cancelled` and `turn_input_required` are also `events` entries,
    and that the category is named after the event that produced it. Done-condition: a generator
    emitting one type per group has the overlap stated rather than discovered.

11. **`conformance/README.md` — the Schema section documents `requirement_level` and `gating`.**
    Ensure the group field list carries `requirement_level` (string, OPTIONAL) — the level the
    section states for the set as a whole — and states what it means for a generated type: a
    `RECOMMENDED` group's names are a target vocabulary an implementation MAY diverge from, so a type
    generated from one MUST admit an unknown token whether or not the group carries `exhaustive`, and
    a check generated from it is advisory where a `REQUIRED` group's is not. Ensure `gating` and
    `condition` are documented alongside `artifact`. Done-condition: the schema documents every field
    the file uses.

12. **`conformance/README.md` — the preamble and the coverage table.** Ensure the opening paragraph's
    list of the token sets `SPEC.md` names includes the three error sets, and ensure "What the slice
    covers" carries a row for each new group. Done-condition: the table lists every group in
    `vocabulary.json`.

13. **`conformance/README.md` — the not-closed-set paragraph.** Ensure the paragraph beginning "Two
    groups are explicitly **not** closed sets" states the correct count and the reason each of the
    new groups is open. Done-condition: the stated count matches the number of groups carrying
    `exhaustive: false`.

14. **`conformance/README.md` — the deferral narrows to Section 10.8.** Ensure the "Error and category
    codes" bullet under "Deferred to later slices" covers only the brokered-result reason codes
    (Section 10.8 "Privileged Operation Broker (`symphony` CLI)"), on its own reason: they are
    introduced by "for example" with three illustrations and no enumeration, so there is nothing to
    publish that would not be invented. Done-condition: the bullet no longer cites Sections 5.5, 11.4
    or 10.6, and no longer gives the per-entry requirement-level reason.

15. **`conformance/README.md` — the surfaced findings.** Ensure "Surfaced findings" records the
    Section 17.3 asymmetry (four RECOMMENDED tracker categories required by name in `Core
    Conformance` checks) as **open**, and the Section 10.6 / Section 10.4 name overlap as recorded
    rather than repaired. Done-condition: both findings are readable without reference to this
    decision folder.

16. **`prompt-rendering.json` — the `description` cites the level.** Ensure the description's
    strict-mode sentence attributes the `template_render_error` requirement to Section 5.5's REQUIRED
    spellings rather than asserting a MUST the specification did not carry, and states the
    condition-not-stage rule for a reader of the corpus alone. Done-condition: every MUST in the file
    is traceable to a MUST in `SPEC.md`.

17. **`prompt-rendering.json` — a `template_parse_error` vector.** Ensure a failure vector exercises a
    body that is not well-formed template syntax, expecting `template_parse_error`, so the
    classification rule of step 3 is checkable rather than only stated. Use the `iterate-labels`
    template with its closing tag removed, so the contrast with the passing vector is the malformation
    alone. Done-condition: `python3 -c "import json;
    d=json.load(open('conformance/vectors/prompt-rendering.json'));
    print(sorted({v['expect'].get('error') for v in d['vectors']} - {None}))"` prints both
    `template_parse_error` and `template_render_error`.

18. **`CONFORMANCE-STATEMENT-TEMPLATE.md` — the new `MUST document` obligation.** Ensure Section 4.1's
    table carries a row for the additional error classes an implementation defines beyond Section
    5.5's five, with a resolution naming the tokens and their gating, or `none`. Done-condition: the
    obligation step 2 introduces has a place to be resolved.

## Cross-cutting sync

Section 6.4's config cheat sheet gains nothing: no configuration key is added or changed. Section 17
is covered by steps 5 and 6; Section 18 by step 7. Sections 11.4 and 10.6 are unedited, so Sections
17.3 and 17.5 need no change — the Section 17.3 asymmetry is recorded as a finding rather than
repaired (step 15).

## Anchor changes

None. No token is renamed, added or removed from `SPEC.md`: the five Section 5.5 classes gain a
requirement level, a stated condition and a published group; the Section 11.4 and 10.6 tokens are
published as they stand. Three registry group names are added — `error_classes`,
`tracker_error_categories`, `agent_error_categories` — and one group field, `requirement_level`.

## Status

Applied to `SPEC.md`, `conformance/vocabulary.json`, `conformance/README.md`,
`conformance/vectors/prompt-rendering.json`, and `CONFORMANCE-STATEMENT-TEMPLATE.md`.
