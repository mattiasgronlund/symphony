# Plan — 0070 The Conformance Statement records the Section 13 resolutions

## Scope

`SPEC.md`: `Logging Outputs and Sinks` (Section 13.2) and `Conformance Statement` (Section 19).

`CONFORMANCE-STATEMENT-TEMPLATE.md`: `OPTIONAL Extensions Shipped` (Section 2), the lead-in of
`` `Implementation-defined` and `MUST document` Resolutions `` (Section 4), `Core` (Section 4.1), and
`Extension-scoped (resolve only if shipped)` (Section 4.2).

No edit to `OPTIONAL Human-Readable Status Surface` (Section 13.4) or
`Session Metrics and Token Accounting` (Section 13.5): both already say "implementation-defined" in
their own text, so the obligation the new rows point at exists. Only Section 13.2 lacked one.

No edit to `Test and Validation Matrix` (Section 17): no behavior is added or changed. Section 17.6
already checks that logging sink failures do not crash orchestration and that a status surface, if
implemented, is driven from orchestrator state.

No edit to `Implementation Checklist (Definition of Done)` (Section 18): Section 18.1.1 already
requires "A published Conformance Statement (Section 19) recording ... every `Implementation-defined`
resolution", which covers the additions by construction.

No `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, or `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` edit: the engine's
Statement (decision 0050) has its own obligations, and none of Section 13 is among them.

## Steps

1. **The log sink is an `Implementation-defined` obligation.** Ensure `Logging Outputs and Sinks`
   states that where logs are written (stderr, file, remote sink, etc.) is `Implementation-defined`,
   that the sink or sinks and the behavior when one of them fails are part of the implementation's
   contract, and that they are recorded in its Conformance Statement (Section 19). Ensure the
   existing three requirement bullets — operator-visible startup/validation/dispatch failures, one or
   more sinks permitted, and continue-with-a-warning on sink failure — are unchanged. Done when a
   template row for the sink points at an obligation `SPEC.md` states.
2. **Section 19's list names the Section 13 behaviours.** Ensure the "A resolution for every
   `Implementation-defined` behavior" bullet's "including:" enumeration carries, in section order
   between the tracker-adapter clause and the park-vs-retry clause, the log sink or sinks and what
   happens when one of them fails (Section 13.2), and the human-readable status surface, if any, and
   the presentation of rate-limit data (Sections 13.4, 13.5). Done when every obligation the template
   pre-enumerates for Section 13 is also named where Section 19 enumerates.
3. **The template's `13.x` placeholders are resolved.** Ensure the Section 2 extensions table cites
   `13.6` for the per-execution usage ledger row and `13.8` for the HTTP status/control server row,
   and that the autonomous task management row cites `8.10` alone — Section 13 has no
   task-management subsection. Done when no `13.x` remains in the file.
4. **The ledger row carries its namespace.** Ensure the per-execution usage ledger row's Config
   namespace column reads `observability.ledger.*` rather than `<namespace>` (Section 13.6, decision
   0069). Done when the row names a namespace.
5. **The status surface is a shippable extension in Section 2.** Ensure the Section 2 table carries a
   `Human-readable status surface` row citing `13.4` with the `observability.*` config namespace, so
   the Section 4.2 row below can be marked `n/a` against it. Done when an implementation that ships
   no status surface has one place to say so.
6. **Section 4's lead-in states the rows are not exhaustive.** Ensure the lead-in of
   `` `Implementation-defined` and `MUST document` Resolutions `` states that the rows are
   pre-enumerated from `SPEC.md` but not exhaustive — Section 19 introduces its own list with
   "including" — so a filler adds a row for any obligation not listed rather than omitting its
   resolution. Done when the open-endedness of Section 19's list is visible in the form that
   implements it.
7. **Section 4.1 carries the two core rows.** Ensure the Core table carries a row for the log sink or
   sinks and the behavior when one of them fails (Section 13.2), and a row for the human-readable
   presentation of rate-limit data (Section 13.5) whose placeholder admits "none", both placed in
   section order between the tracker rows and the `Repository Provisioning Failures` row. Done when
   an implementation resolving every core row has resolved both.
8. **Section 4.2 carries the status-surface row and an `<other>` escape.** Ensure the
   Extension-scoped table carries a row for the human-readable status surface — what it is and what
   it draws from — citing `13.4`, and a final `` `<other>` | `<section>` | `<... / n/a>` `` row in
   the shape Section 2's last row uses. Done when a resolution Section 19 implies but the form does
   not pre-enumerate has a place to be written.

## Cross-cutting sync

- `SPEC.md` Section 6.4 "Core Config Fields Summary (Cheat Sheet)": no change — this decision records
  choices, not config fields. The `observability.*` cheat-sheet entries are decision 0069's.
- `SPEC.md` Section 17 "Test and Validation Matrix": no change, for the reason in `Scope`.
- `SPEC.md` Section 18 "Implementation Checklist": no change, for the reason in `Scope`.
- `conformance/vocabulary.json`: unaffected — the template's rows are obligations, not tokens.

## Anchor changes

None removed or renamed. `SPEC.md` gains no new section or code token; the template gains three rows,
one extensions-table row, and one escape row, none of which is referenced from elsewhere.

The template's `13.x` citations are corrected to `13.6` / `13.8` and, on the autonomous task
management row, dropped in favour of `8.10` alone.

## Out of scope

- **Adding Section 2 rows for every OPTIONAL Section 13 surface.** The runtime snapshot interface
  (Section 13.3) and humanized event summaries (Section 13.7) are OPTIONAL and have no Section 4
  resolution to gate, so neither needs a Section 2 row today; the `<other>` row covers an
  implementation that wants to declare them. Only the status surface gains a row, because a Section
  4.2 row now depends on it.
- **An `<other>` row in Section 4.1.** Its instruction is that a core row MUST NOT be left blank; a
  permanent placeholder row would contradict it. Step 6's lead-in sentence covers the same need.
- **Generating the template from `SPEC.md`.** Named in `Background.md` as the remedy if the two drift
  a third time; not taken here.

## Status

Applied to `SPEC.md` (Sections 13.2, 19) and `CONFORMANCE-STATEMENT-TEMPLATE.md` (Sections 2, 4, 4.1,
4.2).
