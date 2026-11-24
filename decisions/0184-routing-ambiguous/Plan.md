# Plan — 0184 One condition reported under a spelling, and its sibling under none

## Scope

- `SPEC.md`:
  - Section 8.2 (Candidate Selection Rules), the routing sentence;
  - Section 8.7 (Multiple Repositories and Shared Polling), the ambiguity bullet and a new scope
    bullet;
  - Section 13.1 (Logging Conventions);
  - Section 14.2 (Recovery Behavior);
  - Sections 16.2 (Poll-and-Dispatch Tick), 16.4 (Dispatch One Issue) and 16.7 (Worker Exit and
    Retry Handling);
  - Section 17.4 (Orchestrator Dispatch, Reconciliation, and Retry) and Section 18.1.3 (Daemon
    Conformance).
- Conformance data: `conformance/vocabulary.json`, `conformance/README.md`,
  `conformance/vectors/issue-routing.json` and `conformance/vectors/standing-conditions.json`.

Section 14.1 (Failure Classes) is unchanged. Section 8.5 Part B is unchanged: its "in the shape
Section 8.7 already uses" still holds, and the shape now carries a token on both sides.

## Steps

1. **Section 8.7 names the token.** Ensure the ambiguity bullet says the condition is reported
   under `routing_ambiguous`, naming every repository the mapping matched. Done when the bullet
   carries the token.
2. **Section 8.7 states the scope.** Ensure a bullet follows the ambiguity bullet, stating that the
   report:
   - is owed for an issue that fails none of Section 8.2's conditions over the record, which it
     names;
   - is not gated by the `running` or `claimed` memberships or either concurrency limit;
   - is REQUIRED in spelling, and is not a Section 14.1 classification;
   - has its disposition in Section 14.2, and no fixed frequency.

   Done when the bullet beginning "The `routing_ambiguous` report is owed" exists.
3. **Section 8.2 points at the reporting sites.** Ensure the sentence ending "which a fire has none
   of" is followed by one saying each site also evaluates the mapping to report an ambiguity,
   citing Sections 16.2 and 16.7.
4. **Section 13.1.** Ensure a message-formatting bullet requires a `routing_ambiguous` record to
   name every repository the mapping matched, and leaves the list's rendering unfixed.
5. **Section 14.2.** Ensure a bullet for `routing_ambiguous` follows the `standing_condition_lost`
   bullet. It says the issue is neither dispatched, retried nor failed, is not a failure class, and
   takes no claim, no running entry and no retry entry. It also says why neither
   `workflow_config_failures` disposition fits.
6. **Pseudocode.** Ensure:
   - `on_tick` evaluates `route_issue` for every candidate before the dispatch loop and calls
     `log_routing_ambiguous` where `record_conditions_hold`;
   - `on_retry_timer` reports and returns after `should_dispatch`;
   - `dispatch_issue` returns, without reporting, where `repo_of(issue)` is not exactly one
     repository.

   Done when `log_routing_ambiguous` appears in Sections 16.2 and 16.7 and not in Section 16.4.
7. **Section 17.4.** Ensure three checks follow the `standing_condition_lost` check:
   - the token, every repository matched, and no failure class;
   - a saturated instance still reports, while an issue a record condition holds back does not;
   - a retry fire reports and leaves the issue released.
8. **Section 18.1.3.** Ensure the routing item names `routing_ambiguous` and its scope.
9. **Conformance data.**
   - Ensure `conformance/vocabulary.json` has a `non_failure_conditions` group, `exhaustive: false`,
     holding `routing_ambiguous`, `standing_condition_lost` (with `reasons`),
     `await_checks:still_pending`, `await_checks:budget_floor` and `token_budget_exceeded`
     (`core: false`).
   - Ensure `conformance/README.md` lists the group in its table and in the open-set paragraph,
     which counts seven groups.
   - Ensure `issue-routing.json` uses `routing_ambiguous` and adds `expect.matched`, with a vector
     `three-repositories-match`.
   - Ensure `standing-conditions.json`'s labels note cites the published reasons.

   Done when `python3 scripts/validate_spec_consistency.py` reports no errors.

## Cross-cutting sync

- **Section 6.4**: no configuration key changes.
- **Sections 17 and 18**: steps 7 and 8.
- **Conformance Statement template**: no row owed. Nothing is `Implementation-defined`. The list's
  rendering and the report's frequency are left unfixed rather than made a documented choice.

## Anchor changes

- Added: `routing_ambiguous` (`SPEC.md` Section 8.7).
- Added: `non_failure_conditions` (`conformance/vocabulary.json`).
- Added: `log_routing_ambiguous`, `record_conditions_hold` and `route_issue` in Section 16
  pseudocode; `route_issue` is the function name `issue-routing.json` already uses.
- Renamed in `conformance/vectors/issue-routing.json`: the label `multiple_rules_matched` becomes
  `routing_ambiguous`.
