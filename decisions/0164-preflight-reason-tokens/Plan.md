# Plan — 0164 A preflight refusal that cannot say which check refused

## Scope

`SPEC.md`, by section title: Section 6.3 (Dispatch Preflight Validation); Section 11.4 (Error
Handling Contract); Section 13.1 (Logging Conventions); Section 17.1 (Workflow and Config Parsing);
Section 18.1.3 (Daemon Conformance).

`conformance/vocabulary.json` (a new `config_error_reasons` group; the `tracker_error_categories`
group loses three entries), `conformance/vectors/config-preflight.json` (new),
`conformance/README.md`, and `scripts/validate_spec_consistency.py` (one `CLOSED_GROUPS` row).

This decision and decision 0162 both edit Section 11.4 and do not collide — see 0162's `Plan.md` for
the disjointness argument. Whichever applies second restates any count Section 11.4 carries over its
own entries.

## Steps

1. **`SPEC.md`, Section 6.3 (Dispatch Preflight Validation), the reason table.** Ensure the section
   carries a condition-to-reason table in `VCSX-SPEC.md` Section 6.11's shape — a two-column table,
   one row per condition, the reason in backticks — covering every validation check the section
   states, with the twelve tokens the decision fixes: `no_repository_configured`,
   `invalid_repository_key`, `missing_vcs_field`, `missing_tracker_kind`,
   `unsupported_tracker_kind`, `missing_tracker_api_key`, `missing_tracker_project_slug`,
   `set_state_capability_unmet`, `assignee_capability_unmet`, `routing_field_unpopulated`,
   `unknown_transition_trigger`, `missing_agent_command`. Ensure the introducing sentence states
   what the token is for: it is surfaced with the operator-visible error so an operator or a
   monitoring surface can branch on the cause without parsing a message. Done when every check in
   the section has a row and every row names a condition the section checks.

2. **`SPEC.md`, Section 6.3, the two checks that carry two conditions.** Ensure the `tracker.kind`
   check distinguishes absence from non-support, and the `repository` check distinguishes an empty
   set from an invalid key, so each condition in the table corresponds to something the section
   states rather than to a reading of a compound bullet. Done when no table row splits a condition
   the section states as one.

3. **`SPEC.md`, Section 6.3, the evaluation order.** Ensure the section states which reason is
   reported where several conditions hold — the first in the stated order — and why the order is
   what it is: a check is ordered after whatever produces the value it reads, and the three
   capability-dependent checks (`set_state_capability_unmet`, `assignee_capability_unmet`,
   `routing_field_unpopulated`) read a descriptor that only a resolved `tracker.kind` selects. Done
   when a configuration failing several checks has one determinate reason.

4. **`SPEC.md`, Section 6.3, the parse-failure boundary.** Ensure the section states what the table
   does not cover: it names refusals of a configuration that has been read and decoded, and this
   specification names no class for an operator policy config that does not parse — Section 5.5's
   classes are `WORKFLOW.md`'s. Done when a reader looking for a parse reason is told it is not here
   rather than left to conclude the table is short.

5. **`SPEC.md`, Section 11.4 (Error Handling Contract), the three orphans.** Ensure
   `unsupported_tracker_kind`, `missing_tracker_api_key` and `missing_tracker_project_slug` are no
   longer listed as tracker error categories, the section's list holding only the transport-neutral
   categories an adapter maps its transport's failures onto. Ensure the section notes where the
   three went, so a reader arriving from an older reference finds them (Section 6.3). Done when
   every remaining entry in the section names a condition an adapter can raise.

6. **`SPEC.md`, Section 13.1 (Logging Conventions).** Ensure a configuration-refusal record carries
   its reason token, so the branch the table exists for is available on the surface an operator
   actually watches. Match the section's existing context-field pattern rather than introducing a
   new record shape. Done when the token reaches a log record and the field is named.

7. **`SPEC.md`, Section 17.1.** Ensure a check states that each Section 6.3 condition surfaces its
   reason token, and that a configuration failing several conditions reports the first in the stated
   order. Done when the matrix asserts the tokens and the order rather than only the refusal.

8. **`SPEC.md`, Section 18.1.3 (Daemon Conformance).** Ensure the dispatch-preflight bullets name
   the reason tokens as part of what preflight produces. Done when the checklist bullet can be
   implemented without opening Section 6.3 to discover that a token is owed.

9. **`conformance/vocabulary.json`, a new `config_error_reasons` group.** Ensure the group publishes
   the twelve tokens with a `condition` each, `spec_refs` naming Section 6.3 (and Sections 4.2, 9.7,
   11.6, 11.7 where a row's condition is fixed elsewhere), and a `note` recording: that these are
   preflight refusals of the operator configuration rather than adapter errors; that three arrived
   here from Section 11.4, where they had a token and no condition; that the reported reason is the
   first in Section 6.3's stated order; and that `unknown_transition_trigger` is deliberately
   spelled differently from the engine's `unknown_trigger`, the two being checked by different
   parties against different vocabularies. Done when the group is readable without `SPEC.md` open
   and `python3 scripts/validate_spec_consistency.py` passes.

10. **`conformance/vocabulary.json`, `tracker_error_categories`.** Ensure the three relocated tokens
    are removed from the group and its `note` records where they went and why — the group's own
    record that "The first three entries carry no `condition` because Section 11.4 states none" was
    the symptom, and the cause was that their conditions are Section 6.3's. Done when every
    remaining entry carries a `condition`.

11. **`scripts/validate_spec_consistency.py`, `CLOSED_GROUPS`.** Ensure the new group is registered
    so check 6 runs both directions over it: `conformance/vocabulary.json` → `config_error_reasons`,
    document `SPEC.md`, section `6.3`, with a token pattern matching a reason spelled in a table
    row's second column. This is the first Symphony entry in `CLOSED_GROUPS`, so ensure the
    dictionary's existing comment — which describes only the engine's groups and their region
    patterns — is extended to say what this row reads and why it needs no region pattern, in the
    voice of the comments already there. Done when the check reports `0 error(s), 0 warning(s)` and
    fails when a token is added to either side alone.

12. **`conformance/vectors/config-preflight.json`, new file.** Ensure the file pins the predicate:
    given a resolved operator configuration (Section 6.1's output, so no `$` resolution or secret
    provider is exercised — those are I/O-bound and deferred) together with the selected adapter's
    capability descriptor, expect either acceptance or the reason token reported. Ensure it carries
    a vector per token, plus at least one vector where several conditions hold and the expectation
    is the first in the stated order — which is the vector the order exists for, and the one an
    implementation evaluating checks in source order fails. Ensure the file states in its
    `description` why the function is pure and therefore in-corpus, on the reasoning
    `candidate-eligibility.json` already carries: over an already-resolved configuration the
    predicate computes a value from inputs. Done when each of the twelve tokens is asserted and the
    file follows the vector-file schema in `conformance/README.md`.

13. **`conformance/README.md`.** Ensure a finding entry records this in the file's own voice: three
    tokens sat in Section 11.4 with one occurrence each in the whole document and no condition, the
    registry recorded the missing condition without naming the cause, and the cause was that Section
    6.3 produced the conditions and named nothing — ten checks, one undifferentiated refusal, on the
    path that skips dispatch every tick while reconciliation keeps running. Ensure it records the
    measurement: `symphony-rs` at `ee74fe7` raises two of the three as
    `FaultReport::of::<ConfigInvalid>` while its generated `TrackerErrorCategory` carries all three
    as tracker variants, both faithful to a specification that put the token in one section and the
    condition in another. Ensure it records what checks now — check 6 over the new group, and
    `config-preflight.json` over the tokens themselves. Ensure the "What the corpus covers" and
    "Deferred to later slices" sections are updated where the new file changes what is deferred.
    Done when the entry names what was checking (nothing) and what checks now.

## Sites checked, no change needed

Recorded so a later reader does not re-derive them. Checked against `a4048bc`.

- `SPEC.md` Section 6.3's two dispositions — fail startup, or skip dispatch for the tick and keep
  reconciliation active — are unchanged. This decision names the cause of a refusal, not its
  consequence.
- `SPEC.md` Section 14.1's failure classes and Section 14.2's dispositions are unaffected: a
  preflight refusal is `workflow_config_failures`, and which reason token it carries does not change
  the class or its recovery behavior.
- `SPEC.md` Section 5.3's unknown-key rule stays the disposition for a key the schema does not
  declare, which is not one of these conditions.
- `SPEC.md` Section 11.7's capability descriptor is the input three of the checks read and is
  unchanged; the tokens name the refusal, not the descriptor.
- `SPEC.md` Section 6.4 (the config cheat sheet) carries no error rows and gains none; this decision
  adds no configuration key.
- `VCSX-SPEC.md` Section 6.11 is the model and is unchanged. Its `unknown_trigger` keeps its
  spelling; the deliberate difference from `unknown_transition_trigger` is recorded in step 9's note
  rather than by editing the engine.
- No Conformance Statement row is owed — see below.

## Cross-cutting sync

- Section 6.4 cheat sheet: no change.
- Section 17 test matrix: step 7.
- Section 18 checklist: step 8.
- Conformance Statement templates: **no row owed**. Every token is fixed by this specification and
  the reported-reason rule is determinate, so no `Implementation-defined` choice and no
  MUST-document obligation is created. Whether the table is extensible by an OPTIONAL extension is
  left open deliberately (see the decision's reconsideration triggers); were it made extensible, a
  row would be owed at that point.

## Anchor changes

- `unsupported_tracker_kind` — moves from `SPEC.md` Section 11.4 (Error Handling Contract) to
  `SPEC.md` Section 6.3 (Dispatch Preflight Validation). Spelling unchanged; owning section changed.
- `missing_tracker_api_key` — same.
- `missing_tracker_project_slug` — same.
- New tokens, no prior anchor: `no_repository_configured`, `invalid_repository_key`,
  `missing_vcs_field`, `missing_tracker_kind`, `set_state_capability_unmet`,
  `assignee_capability_unmet`, `routing_field_unpopulated`, `unknown_transition_trigger`,
  `missing_agent_command`.
- New registry group, no prior anchor: `config_error_reasons` in `conformance/vocabulary.json`.
- New vector file, no prior anchor: `conformance/vectors/config-preflight.json`.

No section is renamed, added, or removed.

## Status

Applied to `SPEC.md` (Sections 6.3, 11.4, 13.1, 17.1, 18.1.3), `conformance/vocabulary.json` (new
`config_error_reasons` group; `tracker_error_categories` loses three entries), the new
`conformance/vectors/config-preflight.json`, `conformance/README.md`, and
`scripts/validate_spec_consistency.py` (`CLOSED_GROUPS`, Symphony's first entry) on branch
`apply-0164-preflight-reason-tokens`. `python3 scripts/validate_spec_consistency.py` reports `0
error(s), 0 warning(s)`.
