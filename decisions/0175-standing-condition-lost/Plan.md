# Plan — 0175 A report the specification requires and does not name

## Scope

`SPEC.md` Section 8.5 (Active Run Reconciliation) Part B, Section 14.2 (Recovery Behavior) and
Section 17.4 (Orchestrator Dispatch, Reconciliation, and Retry).

Section 14.1 (Failure Classes) is unchanged: nine classes, still partitioning where a failure arose.
Section 8.7 (Multiple Repositories and Shared Polling) is unchanged; see the trigger in
`Background.md`. `conformance/vocabulary.json` is unchanged; see the same file on the registry.

## Steps

1. **Section 8.5 Part B names the token.** Ensure the bullet requiring a standing-condition-loss
   report states the token it carries, `standing_condition_lost`, and the reason token naming which
   condition failed — `required_labels`, `assignee` or `routing`. Ensure both spellings are REQUIRED,
   so Section 14.1's comparability sentence is satisfied for this report.
   Done when Section 8.5 names `standing_condition_lost` and the three reasons, with the requirement
   level stated.

2. **Section 8.5 Part B says it is not a failure class.** Ensure the same passage states that the
   report is not a Section 14.1 classification: nothing failed, the refresh having succeeded, which
   is how the loss was observed.
   Done when the passage says so and cites Section 14.1.

3. **Section 14.2 carries the disposition.** Ensure Section 14.2 gains an entry for
   `standing_condition_lost` on the model of its `await_checks` entry: it is neither retried nor
   failed, it is not a Section 14.1 failure class, and it is listed there because the disposition is
   the one that section governs. Ensure the stop's mechanics are **cited** to Section 8.5 rather
   than restated, so the two sites cannot drift.
   Done when Section 14.2 names `standing_condition_lost`, disclaims the failure classification, and
   cites Section 8.5 without repeating its three clauses.

4. **Section 17.4's standing-condition check names the token.** Ensure the check asserting that a run
   stopped for a lost standing condition schedules no retry and releases its claim also asserts that
   the stop is reported as `standing_condition_lost` with the reason naming which condition failed,
   and that it is not reported under a Section 14.1 failure class.
   Done when the check names the token and the reason.

## Cross-cutting sync

- **Section 6.4 (Core Config Fields Summary (Cheat Sheet))** — unaffected. No configuration key
  changes; `tracker.required_labels` and `tracker.assignee` are referenced, not altered.
- **Section 17** — step 4. **Section 18** — no checklist item states the report; confirm and leave.
- **Section 19 and `CONFORMANCE-STATEMENT-TEMPLATE.md`** — no row owed. Both spellings are REQUIRED
  and the disposition is fixed, so nothing here is `Implementation-defined` and nothing must be
  documented. Confirm against the template rather than assume.
- **`conformance/vocabulary.json`** — no group added and no entry changed; the reasoning and its
  trigger are in `Background.md`.
- **`VCSX-SPEC.md`** — unaffected. Reconciliation is not the engine's.

## Anchor changes

None removed or renamed. Two code-token identifiers are **added**: `standing_condition_lost`, and
the reason vocabulary `required_labels` / `assignee` / `routing` carried beside it. They are new
spellings rather than replacements, so nothing in an earlier plan is falsified.

## Status

Not started.
