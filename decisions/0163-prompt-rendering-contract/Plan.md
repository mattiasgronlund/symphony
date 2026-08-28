# Plan — 0163 The prompt template contract is a cross-implementation contract

## Scope

`SPEC.md`, by section title: Section 5.4 (Prompt Template Contract); Section 5.5 (Workflow
Validation and Error Surface); Section 12.1 (Inputs); Section 12.2 (Rendering Rules); Section 12.3
(Retry/Continuation Semantics); Section 17.1 (Workflow and Config Parsing); Section 18.1.3 (Daemon
Conformance); Section 19 (Conformance Statement).

`CONFORMANCE-STATEMENT-TEMPLATE.md` (two new rows), `conformance/vectors/prompt-rendering.json`
(four new vectors, one restated description) and `conformance/README.md`.

The division between the two homes is deliberate and load-bearing for later readers: **Section 5.4
owns the surface a template is written against** — syntax subset, filters, which variables exist —
because that is the contract with the repository author. **Section 12.2 owns what a bound value
renders to** — null, member resolution, timestamps — because that is the contract with the record.
No rule is stated in both.

## Steps

1. **`SPEC.md`, Section 5.4 (Prompt Template Contract), the REQUIRED subset.** Ensure the rendering
   requirements state a minimal template surface every conforming implementation MUST support,
   spelled in the syntax the corpus uses: `{{ path }}` interpolation with dotted member access; `{%
   for x in seq %}…{% endfor %}` over a list and over a map; and two-element key/value pair indexing
   for a map entry, which Section 12.2 already requires. Ensure it states that a construct outside
   the subset — whitespace control, conditionals, assignment, additional tags — is
   `Implementation-defined`, MUST be documented (Section 19), and that a `WORKFLOW.md` using one is
   not portable across implementations. Ensure the existing strict-failure requirements are kept as
   they stand. Done when a repository author can read Section 5.4 alone and know which constructs
   render everywhere, and when "Liquid-compatible semantics are sufficient" no longer stands as the
   only statement of the surface.

2. **`SPEC.md`, Section 5.4, filters.** Section 5.4's "Unknown filters MUST fail rendering" is kept
   as it stands and now reads against the subset's empty table. Ensure the section states that the
   subset defines no filters; that an implementation MAY offer filters and MUST document those it
   offers (Section 19); and that a template using a filter is outside the portable surface. Done
   when the strict-filter MUST names the set it is unknown against.

3. **`SPEC.md`, Section 5.4, `attempt`.** Ensure the `attempt` template-input bullet reads that the
   variable is always bound and is `null` on a first attempt, an integer on a retry or continuation
   run — dropping "absent". Ensure it states why, in the section's voice: strict variable checking
   is a rule about names the render context does not define, and `attempt` is a name this
   specification defines, so it is never unknown. Done when no sentence in Section 5.4 admits an
   absent `attempt`.

   Section 5.4's existing "Unknown filters MUST fail rendering" is kept by step 2 and is quoted
   there against Section 5.4, which is where it occurs.

4. **`SPEC.md`, Section 12.1 (Inputs).** Ensure the third input reads as a bound `attempt` (integer
   or null) rather than "OPTIONAL `attempt` integer", so the inputs list and Section 5.4 agree on
   whether the name is in the render context. Done when the bullet no longer marks the input
   OPTIONAL.

5. **`SPEC.md`, Section 12.3 (Retry/Continuation Semantics).** Ensure "first run (`attempt` null or
   absent)" reads "first run (`attempt` null)". Done when the parenthetical names one state.

6. **`SPEC.md`, Section 12.2 (Rendering Rules), the null rule.** Ensure the rules state that a bound
   null renders as the empty string, over every nullable value the template context carries —
   Section 4.1.1's nullable fields, its blocker-ref fields, and `attempt`. Done when the rule is
   stated once over the context rather than per variable.

7. **`SPEC.md`, Section 12.2, the closed member set.** Ensure the rules state that the `issue`
   object's members are the fields Section 4.1.1 defines and no others, and that naming a member
   outside them fails rendering with `template_render_error` (Section 5.5). Ensure `metadata` is
   carved out explicitly: it is adapter-owned and open (Section 4.1.1), so member access under
   `metadata` is permitted for any key and a key the adapter did not supply is a bound null under
   step 6. Ensure the rule records why closing the set matters — under an open set a misspelled
   field name and a genuinely null field render identically, so the null rule would erase the signal
   that a template names a field the record does not have. Done when a reader can tell `{{
   issue.assignee }}` from `{{ issue.assignees }}` by the rule rather than by the implementation.

8. **`SPEC.md`, Section 12.2, timestamp rendering.** Ensure the rules state that a `timestamp` value
   (Section 4.1.1) renders as RFC 3339 in UTC, the form Section 11.3 parses on the way in. Done when
   `{{ issue.created_at }}` has one rendering for a given instant on every implementation.

9. **`SPEC.md`, Section 5.5, the `template_render_error` condition.** Ensure the class's
   parenthetical also names a member outside the `issue` object's field set alongside the unknown
   variable, the unknown filter, and the invalid interpolation, so the class covers what step 7
   introduces. Done when the condition list and Section 12.2's rule name the same set of failures.

10. **`SPEC.md`, Section 17.1.** Ensure checks exist for each rule this decision makes observable: a
    first-run `attempt` renders rather than failing; a null issue field renders as empty; a member
    outside Section 4.1.1's set fails `template_render_error` while a `metadata` key the adapter did
    not supply renders as empty; a timestamp renders RFC 3339 UTC; and a template using a construct
    outside the subset is not required to render. Done when every rule added by steps 1–8 has a row
    phrased as an observable check in the section's voice.

11. **`SPEC.md`, Section 18.1.3.** Ensure the "Strict prompt rendering with `issue` and `attempt`
    variables" bullet names what strict now means here: the REQUIRED subset, no portable filters, a
    bound null rendering empty, and a closed `issue` member set. Done when the checklist bullet can
    be implemented without opening Sections 5.4 and 12.2.

12. **`SPEC.md`, Section 19 (Conformance Statement).** Ensure the "MUST record" enumeration names
    the template constructs supported beyond the REQUIRED subset and the filters the implementation
    offers (Section 5.4). Done when both obligations are reachable from Section 19.

13. **`CONFORMANCE-STATEMENT-TEMPLATE.md`.** Ensure the table carries a row for each, citing Section
    **5.4**: one for template constructs beyond the subset, one for the filters offered. The
    citation MUST be the subsection carrying the obligation so `python3
    scripts/validate_spec_consistency.py` check 2 matches. Done when the check reports `0 error(s),
    0 warning(s)`.

14. **`conformance/vectors/prompt-rendering.json`, new vectors.** Ensure four vectors exist:
    `attempt-null-renders-empty` (`attempt: null`, a template reading it, rendering the null as
    empty rather than failing); `null-issue-field-renders-empty` (a nullable Section 4.1.1 field
    supplied as null); `unknown-issue-member-fails` (a member outside Section 4.1.1's set, expecting
    `template_render_error`, using a near-miss of a real field name so the vector exercises the case
    an author actually hits); and `timestamp-renders-rfc3339` (a `created_at` instant with its RFC
    3339 UTC rendering). Ensure each keeps the file's single-line-template convention. Done when
    each rule from steps 6, 7 and 8 is asserted by a vector and the file's `spec_refs` name every
    section the new vectors rest on.

15. **`conformance/vectors/prompt-rendering.json`, `unknown-filter-fails`.** Ensure its description
    records what the vector now means: the portable subset defines no filters, so this vector is
    satisfied by an implementation that offers none as well as by one that offers some and lacks
    this name — it asserts the strict-failure rule rather than the absence of a particular filter.
    Done when the description no longer implies a filter table the specification does not state.

16. **`conformance/vectors/prompt-rendering.json`, the file description.** Ensure it states that the
    templates are written in the REQUIRED subset (Section 5.4). The file's current description says
    "Templates use Liquid-compatible syntax (Section 5.4)" and that "an engine that is not
    Liquid-compatible maps these to its equivalent", which was true of a floor and is not true of a
    subset. (`conformance/README.md`'s open finding separately says "the slice authors the reference
    vectors in Liquid syntax"; step 17 rewrites that entry.) Done when the description names the
    normative surface the vectors are written against.

17. **`conformance/README.md`, the harness contract.** Its `render_prompt` entry under the harness
    contract ends "Templates use Liquid-compatible syntax (Section 5.4)", which describes a floor
    and not a subset. Ensure it names the REQUIRED subset instead, so a harness author meets the
    normative surface where they meet the function. Done when no sentence in the file describes the
    vectors' templates as merely Liquid-compatible.

18. **`conformance/README.md`, the findings.** Ensure the two open findings — the headings beginning
    "**Template syntax is a floor, not a mandate" and "**`attempt` "null or absent" versus strict
    mode" — are rewritten as resolved, naming this decision, in the file's own voice. Ensure the
    entry records what measurement added: that the one implementation had already answered all four
    questions and the specification none of them, with the tests named; that the corpus was already
    stricter than the specification it tests, and had recorded the divergence it routed around in
    its own description; and that two of the four gaps — the closed member set and the timestamp —
    were found by reading the implementation rather than by authoring a vector. Done when no entry
    in the file still describes prompt rendering as under-specified.

## Sites checked, no change needed

Recorded so a later reader does not re-derive them. Checked against `a4048bc`.

- Section 5.4's "Liquid-compatible semantics are sufficient" survives step 1 as the statement of the
  engine's *semantics*, which the subset does not replace — it adds the surface. It has to survive,
  or `conformance/README.md`'s resolved decision-0135 entry, which quotes the phrase as Section
  5.4's, goes stale. Step 1's done-condition is that the phrase is no longer the *only* statement of
  the surface, not that it is removed.
- `SPEC.md` Section 4.1.5's `attempt` field already reads "(integer or null, `null` for first run,
  `>=1` for retries/continuation)". It is the wording the other three sites are aligned onto, not a
  site needing an edit.
- Section 4.1.1's field bullets are unchanged. The closed member set is stated in Section 12.2 over
  Section 4.1.1's list rather than restated there, so the list stays the single definition and
  `scripts/validate_spec_consistency.py` check 7 keeps reading it.
- Section 5.2's parsing rules and returned workflow object concern the front matter/body split, not
  the body's syntax. Unchanged.
- Section 5.4's prompt-authority passage and the empty-body fallback are unaffected: authority is
  about what a prompt may cause, not what it renders to.
- Section 12.4's failure semantics already dispose of a rendering failure by failing the run
  attempt, which is what makes each rule here consequential. Unchanged.
- `SPEC.md` Section 11.3's "`created_at` and `updated_at` -> parse ISO-8601 timestamps" is the input
  side and is cited by step 8 as the reason for the output form. Unchanged.
- `scripts/validate_spec_consistency.py` gains no check. Check 7 already holds
  `iterate-issue-object` to Section 4.1.1, which is the enumeration step 7 closes over; the subset
  and the value rules are prose the corpus asserts by vector rather than enumerations a second
  artifact restates.
- Section 6.4 (the config cheat sheet) carries no template rows; this decision adds no configuration
  key. Neither engine document renders a prompt.

## Cross-cutting sync

- Section 6.4 cheat sheet: no change.
- Section 17 test matrix: step 10.
- Section 18 checklist: step 11.
- Conformance Statement template: **two rows owed**, step 13 — template constructs beyond the subset
  and the filters offered, both `Implementation-defined` with a MUST-document obligation.
  `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` is unchanged.

## Anchor changes

None. `attempt`, `template_render_error`, `template_parse_error` and every Section 4.1.1 field keep
their spelling. No section is renamed, added, or removed. What changes is what the specification
fixes about rendering, and what "OPTIONAL"/"absent" means for one input.

## Status

Applied to `SPEC.md` (Sections 5.4, 5.5, 12.1, 12.2, 12.3, 17.1, 18.1.3, 19),
`CONFORMANCE-STATEMENT-TEMPLATE.md`, `conformance/vectors/prompt-rendering.json`,
`conformance/README.md`, and `conformance/vocabulary.json` (repair, `Background.md` "What applying
the plan repaired") on branch `apply-0163-prompt-rendering-contract`.
