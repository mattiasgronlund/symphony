# Plan — 0178 A refused target transitions nothing, and a budget park gets a trigger of its own

## Scope

`SPEC.md` Section 9.7 (Repository Provisioning and the VCS Engine), Section 8.8 (Token Budget Guards
(OPTIONAL)), Section 11.6 (Workflow State Machine and Transition Triggers), Sections 17.2 and 17.4, and Section
18.2 (RECOMMENDED Extensions (Not REQUIRED for Conformance)). `conformance/vocabulary.json`'s
`transition_triggers` group.

## Steps

1. **Section 9.7's refusal transitions nothing.** Ensure the list under "Where an issue is refused
   for either reason, Symphony:" has two entries, MUST log and SHOULD comment, and no
   `set_state`/"configured blocked state" entry. Ensure the paragraph beginning "The issue is not
   dispatched" says the refused issue stays a candidate that is filtered on each evaluation, as an
   ineligible candidate is (Section 8.2). Done when "configured blocked state" no longer occurs in
   Section 9.7.

2. **Section 8.8 fires a trigger instead of naming an undefined disposition.** Ensure the failure
   disposition bullet for `token_budget_exceeded` says that the run is aborted, that the orchestrator
   fires the `token_budget_exceeded` trigger (Section 11.6) in place of `run_failed` for that
   attempt, and that where no transition binds it the issue is parked where it is. Done when
   "policy's blocked disposition" no longer occurs in `SPEC.md`.

3. **Section 11.6 lists the trigger.** Ensure the Triggers list carries an OPTIONAL group for the
   token budget guards extension (Section 8.8) with `token_budget_exceeded`: a run attempt aborted by
   a per-session or per-issue cap, fired in place of `run_failed`. Ensure the `run_failed` entry
   says it does not fire for an attempt that fires `token_budget_exceeded`. Done when both entries
   exist.

4. **The vocabulary carries the trigger.** Ensure `conformance/vocabulary.json`'s
   `transition_triggers.entries` contains `token_budget_exceeded` with `core: false` and a condition
   matching step 3, that the group's `spec_refs` cite Section 8.8, and that the group's `note` names
   the extension as a fourth origin. Ensure the `blocked` entry is unchanged. Done when the file
   parses as JSON and contains the entry.

5. **Section 17.2's refusal row drops the transition.** Ensure the row beginning "An operator config
   whose `vcs.policy_branch` equals" no longer says "transitioned to the configured blocked state",
   and says the refused issue stays a candidate. Done when "configured blocked state" no longer
   occurs in `SPEC.md`.

6. **Section 17.4's budget row and Section 18.2's budget entry name the trigger.** Ensure the row
   beginning "If token budget guards are implemented, a `token_budget_exceeded` outcome is parked"
   says it fires `token_budget_exceeded` in place of `run_failed`. Ensure Section 18.2's token budget
   guards entry names the trigger it owns. Done when both mention the trigger.

## Cross-cutting sync

- Section 6.4: unaffected; no key added or removed.
- Section 17: steps 5 and 6. Section 18: step 6.
- Conformance Statement templates: no row owed. The extension already has its row ("Token budget
  guards | 8.8"), and the decision adds no `Implementation-defined` value.
- `conformance/vocabulary.json`: step 4.

## Anchor changes

- Added: `token_budget_exceeded` as a Section 11.6 transition trigger, in addition to its existing
  use as a Section 14.1 extension failure category.
- Removed: the Section 9.7 "configured blocked state" obligation. It was not a code-token anchor.

## Status

Not started.
