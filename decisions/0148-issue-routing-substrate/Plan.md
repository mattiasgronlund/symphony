# Plan — 0148 Routing keys and the record they route over

## Scope

- `SPEC.md` — Section 4.1.1 (Issue), Section 8.7 (Multiple Repositories and Shared Polling), Section
  11.2 (Linear adapter), Section 11.7 (Adapter descriptors), Section 6.3 (dispatch preflight),
  Section 6.4 (config cheat sheet), Section 17.4 (test matrix), Section 18 (implementation
  checklist).
- `conformance/vectors/` — one new file. Routing is a pure function of the record and the mapping,
  which is the shape the corpus takes.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — Section 4.1, one row (the publication choice).

## Steps

1. **`SPEC.md` Section 4.1.1 — `project` and `team`.** Ensure the record carries both as string or
   null, OPTIONAL and tracker-dependent, in the shape `branch_name` and `blocked_by` already use,
   and normalized with `Lowercase Normalization` (Section 4.2) as `labels` are. Ensure `project` is
   described as the tracker's container the issue belongs to, with the `forgejo` adapter's owning
   repository named as its instance of that, and that an adapter whose tracker has no such model
   leaves the field null. Ensure the publication clause is stated over what the adapter publishes:
   the identifier MUST distinguish the tracker's containers under `Lowercase Normalization`, and an
   adapter whose stable identifier does not publishes the human-facing key or slug instead and
   documents which. *Done when:* every routing key Section 8.7 names has a field, the fields are
   normalized the way every other compared field is, and Section 4.2's sentence about normalization
   being defined over every case-insensitive comparison stays true.
2. **`SPEC.md` Section 8.7 — the routing bullet is stated over the record.** Ensure the bullet
   quoted as "Routing uses an explicit, tracker-implementation-specific mapping in the policy
   config" states that routing is evaluated **after normalization**, over the Section 4.1.1 record,
   as a pure function of that record and the policy config; that the mapping's key space is the
   normalized fields — `project`, `team`, `labels`, `assignees`, `state` — rather than per-tracker
   key names; and that the per-adapter examples become statements about which of those an adapter
   populates. Ensure the existing prohibition on routing by untrusted free-form issue content is
   kept and now has a referent: the mapping names fields of the record, and `metadata` is not one.
   *Done when:* the section's own `linear` and `forgejo` examples are expressible against Section
   4.1.1, and no reader can conclude the mapping is applied to a raw tracker payload.
3. **`SPEC.md` Section 8.7 — an issue two rules claim is not dispatched.** Ensure the section states
   that where more than one repository's rule matches an issue, the issue is not routed and not
   dispatched, and the condition is reported; and that this is stated over the issue rather than
   over the configuration, because two rules may be disjoint over every issue that exists today.
   Ensure the reason is given — a dispatch grants an agent commit and pull-request authority in the
   repository it routes to. *Done when:* "routed to exactly one repository" has a stated behaviour
   for the case where the mapping says two, and no implementation is licensed to pick.
4. **`SPEC.md` Section 11.7 — the descriptor declares the fields.** Ensure a tracker adapter's
   descriptor declares whether it populates `project` and whether it populates `team`, beside the
   declarations Section 11.7 already carries. *Done when:* an operator can tell from the descriptor
   whether a routing key is available before configuring one.
5. **`SPEC.md` Section 6.3 — a mapping on an unpopulated field is a preflight error.** Ensure the
   dispatch preflight refuses a routing mapping keyed on a field the selected adapter's descriptor
   says it does not populate, in the shape Section 6.3 already carries for `tracker.api_key` under a
   `secret`-mode adapter and for a non-empty `tracker.transitions` against an adapter that does not
   declare `set_state`. *Done when:* a mapping that would match no issue is a startup/preflight
   failure rather than a deployment that silently routes nothing.
6. **`SPEC.md` Section 11.2 — the Linear adapter's queries carry the fields.** Ensure the clause
   stating that candidate and issue-state refresh queries include labels (and, under decision 0140,
   assignees) extends to the routing fields the adapter populates, filtered after normalization, for
   the reason already written beside it: so a refresh can observe a change and stop or release
   existing work. *Done when:* an issue moved between projects or teams mid-run is visible to
   Section 16.3's refresh rather than absent from the enumeration.
7. **`SPEC.md` Section 17.4 — three rows.** Ensure the matrix covers (a) an issue routed by a
   normalized record field rather than by a raw tracker payload; (b) an issue matched by two
   repository rules not being dispatched and the condition being reported; (c) a mapping keyed on a
   field the selected adapter does not populate being refused at dispatch preflight. Ensure the two
   existing routing rows are kept and now have a substrate. *Done when:* (b) fails an implementation
   that picks the first match, and (c) fails one that routes nothing quietly.
8. **`SPEC.md` Section 18 — the checklist follows.** Ensure the implementation checklist covers
   evaluating the routing mapping over the normalized record. *Done when:* the line exists and does
   not restate Section 17.4's wording.
9. **`SPEC.md` Section 6.4 — the cheat sheet lists the record's new fields where it lists the
   others.** Ensure the cheat sheet's account of what an adapter populates matches Section 4.1.1.
   *Done when:* no field of Section 4.1.1 that an operator's configuration can name is missing from
   Section 6.4.
10. **`CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1 — the publication row.** Ensure a row records
    which identifier the adapter publishes in `project` and `team`, citing Section 4.1.1 — the
    obligation added in step 1. Ensure it composes with, rather than duplicates, the row decision
    0140 adds for `assignees`. *Done when:* `python3 scripts/validate_spec_consistency.py` reports 0
    errors and 0 warnings, and every MUST-document sentence this decision adds has a row
    (`CLAUDE.md`, decision 0128).
11. **`conformance/vectors/issue-routing.json` — the pure function.** Ensure a vector file covers
    routing as a function of `{ issue: <normalized record fields>, rules: [ … ] }` → `{ repository:
    <name> | none, refused: <reason> | null }`, with cases for a single match, no match, two matches
    (refused), and a rule naming a field the record leaves null (no match, not every match). *Done
    when:* the file needs no adapter and no live tracker, and the two-match case is the one an
    implementation that picks the first rule fails.

## Cross-cutting sync

- `SPEC.md` Sections 6.4, 17.4 and 18: steps 9, 7 and 8.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1: step 10. **A row is owed** for the publication
  choice (decision 0128).
- No recovery-class row is owed: the new fields live on the issue record (Section 4.1.1), not on the
  Orchestrator Runtime State (Section 4.1.8).

## Ordering

- **After decision 0140.** That decision adds `assignees` to Section 4.1.1 and `tracker.assignee` to
  Section 5.3.1, and step 2's key space names `assignees`. It also establishes the
  descriptor-plus-preflight shape steps 4 and 5 follow and the publication clause step 1 inherits;
  writing this one first would either duplicate that reasoning or contradict it.
- Independent of decisions 0144–0147.

## Out of scope, and owed separately

The routing mapping has no configuration key and the managed-repository list has no configuration
key: `SPEC.md` Section 5.3's top-level keys are six and include neither, while `SPEC.md` Sections
6.4 and 8.7 both assert both exist, and `SPEC.md` Section 8.1's tick sequence says "Fetch candidate
issues from each tracker (once per tracker)" where `SPEC.md` Section 5.3.1 defines one `tracker`
object. That schema — a repository enumeration interacting with per-repository `vcs` (`SPEC.md`
Section 9.7), `agent` (`SPEC.md` Section 10.9), the `repo.policy.toml` pointer and per-repository
credentials (`SPEC.md` Section 15.3) — is its own decision and is deliberately not added here. **Do
not fold it into this plan when it arrives**: this decision fixes what the mapping keys on and where
it is evaluated, and nothing in it depends on where the mapping is written. The reasoning is in
`Background.md`, under the heading naming what this decision does not fix.

## Anchor changes

- **Added:** `project` and `team` on Section 4.1.1; two descriptor declarations in Section 11.7; a
  preflight refusal in Section 6.3; `conformance/vectors/issue-routing.json`.
- **Changed:** Section 8.7's routing bullet is restated over the normalized record and gains the
  after-normalization statement and the two-rules rule; Section 11.2's query clause extends.
- **Removed:** nothing. The per-tracker key names in Section 8.7's examples stop being the mapping's
  key space and become descriptions of what each adapter populates; the words survive with a
  different job.

## Status

Applied to `SPEC.md` (Sections 4.1.1, 6.3, 6.4, 8.7, 11.2, 11.7, 17.4, 18.1.3, 19),
`CONFORMANCE-STATEMENT-TEMPLATE.md` (Section 4.1), `conformance/vectors/issue-routing.json`
and `conformance/README.md`. Section 19 is not in the Scope list above: it carries the same
`MUST document` obligations the template tabulates, in prose, so the publication choice step 1
adds is named there too — the site decision 0140's step 12 found by the same reach check.
Issue #113.
