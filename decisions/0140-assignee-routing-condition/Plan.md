# Plan — 0140 A dispatch condition no configuration and no record could supply

## Scope

- `SPEC.md` — Section 4.1.1 (Issue), Section 5.3.1 (`tracker` (object)), Section 6.3 (Dispatch
  Preflight Validation), Section 6.4 (Core Config Fields Summary), Section 8.2 (Candidate Selection
  Rules), Section 11.2 (Adapter Semantics), Section 11.3 (Normalization Rules), Section 11.7
  (Adapter Capability Descriptor), Section 17.4 (Orchestrator Dispatch, Reconciliation, and Retry),
  Section 18.1.3 (Daemon Conformance), Section 19 (Conformance Statement).
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — Section 4.1 (Core) gains one row. The decision adds an
  `Implementation-defined` + MUST-document obligation (which identifier an adapter publishes in
  `assignees`), so the row is owed (`CLAUDE.md`, decision 0128).
- `conformance/vectors/candidate-eligibility.json` — new file pinning `should_dispatch`.
- `conformance/README.md` — the vector table gains its row; the deferral bullet covering candidate
  eligibility is narrowed to the adapter's fetch. That file and `conformance/vcsx/README.md` both
  carry a deferral list, and only the first is edited.
- `conformance/vocabulary.json` — **no change**. `config_namespaces` carries top-level namespaces
  (`tracker`, `polling`, …) rather than keys inside them, and no group publishes Section 4.1.1's
  record fields, so neither `tracker.assignee` nor `assignees` owes an entry.
- `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — **no change**.
  Nothing the engine owns is involved: candidate selection is Symphony's, above the engine's seam.

## Steps

1. **Section 4.1.1 "Issue" — the record carries `assignees`.** Ensure a field bullet `assignees`
   (list of strings) exists, documented in the same shape as `blocked_by` and `branch_name`:
   OPTIONAL and tracker-dependent, an adapter whose tracker has no assignee model leaving it empty
   so assignee-gated dispatch (Section 8.2) does not gate; normalized with `Lowercase Normalization`
   (Section 4.2) as `labels` are; and a stated obligation that the identifier an adapter publishes
   MUST distinguish the tracker's principals under `Lowercase Normalization` — an adapter whose
   stable identifier does not (a case-significant opaque id) publishing the login or handle instead,
   and documenting which it publishes (`Implementation-defined`). Place it beside `labels`, whose
   treatment it parallels. *Done when:* the field exists with the emptiness behavior, the
   normalization, and the publication obligation, and no clause states the requirement over the
   comparison instead of over the publication (`SPEC.md` Section 4.2's "Every case-insensitive
   comparison in this specification is defined over this operation" must stay true as written).
2. **Section 5.3.1 "`tracker` (object)" — the configuration carries `tracker.assignee`.** Ensure a
   field bullet `assignee` (string) exists with `Default: null` meaning no assignee filter, matched
   as `required_labels` is: surrounding whitespace ignored on both sides, compared under `Lowercase
   Normalization` (Section 4.2), a blank configured value matching no issue, and an issue matching
   when its `assignees` contain it. Ensure `SPEC.md`'s existing sentence "An issue MUST contain
   every configured label to dispatch or continue" is not weakened; the assignee condition is
   covered by the same dispatch-or-continue rule rather than by a second one. *Done when:* the field
   exists with its default and its full matching rule, and a reader can evaluate the condition from
   Section 5.3.1 plus Section 4.1.1 alone.
3. **Section 8.2 "Candidate Selection Rules" — the routing bullet becomes two evaluable
   conditions.** Ensure the `SPEC.md` bullet quoted as "routed to this worker by the configured
   assignee" no longer appears, and that in its place the list carries two conditions: one testing
   `tracker.required_labels` membership, and one testing `tracker.assignee` against the issue's
   `assignees` (a null configured assignee not gating). Ensure the list's remaining conditions and
   their order are unchanged, and that the section still fixes no precedence among them. *Done
   when:* Section 8.2 lists nine conditions, each evaluable from the resolved configuration and the
   Section 4.1.1 record, and the phrase "this worker" no longer appears in a candidate-selection
   condition.
4. **Section 11.2 "Adapter Semantics" — the Linear clause covers assignees.** Ensure the `SPEC.md`
   bullet quoted as "Candidate and issue-state refresh queries include issue labels" also names
   assignees, with filtering after normalization, and with the reason already stated there extended
   to it — so refresh can observe an assignment change and stop or release existing work. *Done
   when:* the clause names both labels and assignees, states filtering happens after normalization,
   and the enumeration-completeness rule above it is unchanged.
5. **Section 11.3 "Normalization Rules" — `assignees` has a mapping row.** Ensure the additional
   normalization details carry an `assignees` entry in the shape the `labels` and `blocked_by`
   entries already use: normalized per `Lowercase Normalization`, empty where the tracker has no
   assignee model, and the published identifier being the adapter's documented choice. *Done when:*
   the row exists and does not restate the Section 4.1.1 obligation in different words.
6. **Section 11.7 "Adapter Capability Descriptor" — the descriptor declares `assignees`.** Ensure
   the descriptor declares whether the adapter populates `assignees`, in the shape the section
   already uses for auth mode and for write support, and ensure the section states that a configured
   `tracker.assignee` against an adapter that does not populate `assignees` is a dispatch-preflight
   configuration error (Section 6.3) — the same binding the section already carries for
   `tracker.transitions` and `set_state`. *Done when:* the descriptor's declared surface includes
   the `assignees` question and the Section 6.3 binding is stated here as well as there.
7. **Section 6.3 "Dispatch Preflight Validation" — the check is in the list.** Ensure the validation
   checks carry a line: when `tracker.assignee` is non-null, the selected tracker adapter declares
   that it populates `assignees` (Section 11.7); otherwise configuration error. Place it beside the
   `tracker.transitions` / `set_state` line it is modelled on. *Done when:* the check appears in
   Section 6.3's list and names Section 11.7 as the source of the declaration.
8. **Section 6.4 "Core Config Fields Summary (Cheat Sheet)" — the key has a row.** Ensure a
   `tracker.assignee` row exists reading as the other `tracker.*` rows do, with `default null`.
   *Done when:* the cheat sheet carries nine `tracker.*` rows and the default matches Section
   5.3.1's.
9. **Section 17.4 "Orchestrator Dispatch, Reconciliation, and Retry" — the matrix exercises the
   condition.** Ensure rows exist for: an issue whose `assignees` do not contain a configured
   `tracker.assignee` is not eligible; a null `tracker.assignee` does not gate; an adapter that
   populates no `assignees` against a configured `tracker.assignee` fails dispatch preflight rather
   than silently matching no issue; and an assignment removed while a run is in flight is observed
   on the refresh, as a removed required label already is. *Done when:* the four rows exist and each
   is stated over an observable the suite can produce.
10. **Section 18.1.3 "Daemon Conformance" — the checklist names the field and the preflight.**
    Ensure the checklist entry covering candidate eligibility names assignee matching alongside
    required labels, and that the preflight entry covers the descriptor check. *Done when:* both
    appear and neither duplicates Section 17.4's wording.
11. **`CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1 (Core) — the obligation has a row.** Ensure a
    row exists for the identifier an adapter publishes in `assignees`, citing `SPEC.md` Section
    4.1.1, with a resolution placeholder in the shape that file's pull-request-target carrier row
    already uses. The row carries the guarantee as well as the answer: which identifier is
    published, and that it distinguishes the tracker's principals under `Lowercase Normalization`.
    *Done when:* the row exists and `python3 scripts/validate_spec_consistency.py` reports 0 errors
    and 0 warnings.
12. **`SPEC.md` Section 19 (Conformance Statement) — the obligation is named there too.** That
    section enumerates the same obligations the template tabulates, in prose — its list already
    carries the pull-request-target carrier the template row above is modelled on. Ensure the
    identifier an adapter publishes in `assignees` is named in the same list, so the two artifacts
    agree. *Done when:* every obligation this decision adds appears both as a template row and in
    Section 19's enumeration. (Found by `scripts/check_plan_anchors.py`'s reach check, which
    reported `SPEC.md` Section 19 as a site carrying the wording this plan quoted only against the
    template.)
13. **`conformance/vectors/candidate-eligibility.json` — `should_dispatch` is pinned.** Ensure the
    file exists for function `should_dispatch`, one refusing condition per vector, its `expect`
    naming the refusing condition rather than a boolean, with the blank-configured-label case and
    the configured-assignee-absent case among them, and a passing vector for each of the null
    defaults. Ensure a note records why one condition per vector: Section 8.2 fixes no precedence
    among its conditions, so a vector holding two would pin an evaluation order the specification
    does not state — the reasoning `conformance/vcsx/vectors/policy-validation.json` already records
    for `validate_policy`. *Done when:* the file validates against the corpus's own schema
    conventions, and no vector holds two failing conditions.
14. **The Section 6.3 case is deliberately not vector-pinned.** Ensure no vector file is authored
    for `validate_dispatch_config`: it is called at Section 16.1 and Section 16.2 and defined
    nowhere, and `config-defaults.json` pins `resolve_config_defaults`, which defaults a
    configuration rather than judging one. The configured-assignee-against-a-non-populating-adapter
    case is covered by step 9's Section 17.4 row and waits for the decision that gives that function
    a body. *Done when:* the omission is recorded in this decision's `Background.md` rather than
    being silent, and no vector asserts against an undefined function.
15. **`conformance/README.md` — the table gains a row and the deferral narrows.** Ensure the vector
    table lists `vectors/candidate-eligibility.json` / `should_dispatch` / `Daemon` / Sections 8.2,
    16.2, and ensure that file's deferral bullet quoted as "candidate eligibility over live issues"
    is narrowed so what remains deferred is the adapter's fetch, the predicate over an
    already-normalized record plus resolved config no longer being deferred. *Done when:* both edits
    are present and the deferral no longer claims Section 8.2's predicate is non-deterministic.

## Cross-cutting sync

- Section 6.4 (cheat sheet): step 8.
- Section 17 (test matrix): step 9.
- Section 18 (checklist): step 10.
- `CONFORMANCE-STATEMENT-TEMPLATE.md`: step 11 — required, because step 1 introduces an
  `Implementation-defined` + MUST-document obligation. `SPEC.md` Section 19 carries the same
  obligation in prose: step 12.
- `VCSX-SPEC.md` Sections 13.1–13.3: no change; the engine has no part in candidate selection.

## Ordering

Independent of decisions 0141, 0142 and 0143, which are all `VCSX-SPEC.md`. It may be applied before
or after any of them.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0140-assignee-routing-condition/Plan.md --rev
97617c2` reports residual findings of one class only: a step header names its section by title, and
a title lives in a heading rather than in the section body the checker searches, so every quoted
title is reported as unmatched. The convention is `CLAUDE.md`'s (decision 0002) and is kept; the
findings are the checker meeting it, not the plan misquoting. Two reach findings accompany them and
neither is a missed site: `conformance/README.md:291` is the bullet step 14 edits, reported only
because the step names two section numbers after the file; and `conformance/README.md:369` is that
file's prose about the `Lowercase Normalization` vectors, which this decision does not touch —
adding a normalized field changes nothing about the three readings those vectors separate.

## Anchor changes

- **Removed:** the Section 8.2 condition phrased "It is routed to this worker by the configured
  assignee and contains every label in `tracker.required_labels`" — replaced by two conditions (step
  3). No plan cites the removed phrasing as an anchor.
- **Added:** `assignees` (Section 4.1.1), `tracker.assignee` (Section 5.3.1). No token is renamed.

## Status

Not started.
