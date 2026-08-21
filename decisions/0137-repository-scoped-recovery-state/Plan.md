# Plan — 0137 A backoff kept per repository, and the state model with no repository in it

## Scope

- `SPEC.md` — Section 4.1.8 (Orchestrator Runtime State), Section 14.3 (State Recovery Classes),
  Section 17.4 (Orchestrator Dispatch, Reconciliation, and Retry), Section 18.1.1 (Both Layer
  Profiles), Section 18.1.3 (Daemon Conformance), Section 19 (Conformance Statement).
- `conformance/vocabulary.json` — one entry in `runtime_state_fields`.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — Section 5, one row for the new field, one relabelled
  catch-all row, and the preamble sentence that names what the table covers. **A row is owed here**:
  the `SPEC.md` Section 14.3 widening creates a "MUST document" obligation, which is exactly the case
  `CLAUDE.md` and decision 0128 require a template row for.
- `conformance/README.md` — one "Surfaced findings" entry.
- `conformance/vectors/` — **no change**. A recovery class is an assignment, not a function of
  inputs; there is nothing a one-shot vector could assert about it. The eight existing files are all
  pure functions and this decision adds no ninth behaviour.
- `SPEC.md` Section 6.4 — **no change**. No configuration key is involved; the backoff schedule
  stays `Implementation-defined` and already has its template row.
- `SPEC.md` Section 14.2 — **no change**. Its three obligations are the premise of this decision,
  not its target; none of the failure-class bullets is reworded.

## Steps

1. **`SPEC.md` Section 4.1.8 (Orchestrator Runtime State) — a repository-keyed field exists.**
   Ensure the field list gains `repository_backoff` (map `repository -> backoff entry`, each entry
   carrying `due_at_ms` and `attempt`) classed `Ephemeral`, with the parenthetical stating what a
   reset costs in the register the neighbouring fields use — a restarted orchestrator retries every
   backed-off repository on its next tick and backs off from the first attempt again, as
   `retry_attempts` already says of itself. Ensure the field's description names Section 14.2's
   unusable-policy per-repository backoff as what it holds. *Done when:* Section 4.1.8 lists nine
   fields, each still carries exactly one recovery class, and `repository_backoff` is the only one
   keyed by repository.
2. **`SPEC.md` Section 4.1.8 — the parks are not forced into the field.** Ensure `repository_backoff`
   does not carry a `parked` flag or equivalent. Parking is `Implementation-defined` down to whether
   it occurs, so its state is admitted by step 3 rather than mandated here. *Done when:* the field's
   entry shape is `due_at_ms` and `attempt` only, and Section 4.1.8 says nothing about parking.
3. **`SPEC.md` Section 14.3 (State Recovery Classes) — the rule admits Core-introduced state.**
   Ensure the sentence that begins "Every field of the Orchestrator Runtime State (Section 4.1.8)"
   retains its extension clause and gains Core's: state that Core behavior requires an implementation
   to hold beyond the fields Section 4.1.8 enumerates MUST likewise be assigned exactly one recovery
   class and MUST be documented. Name the cases this document creates — a park record for the two
   `Implementation-defined` park-versus-retry choices in Section 14.2 — so the clause reads as
   closing a known set rather than as an open licence. Follow the shape Section 14.1 already uses for
   its own non-closure note. *Done when:* Section 14.3 requires a class and documentation for Core
   state outside Section 4.1.8, and the existing obligation over Section 4.1.8's fields and over
   extension state is unchanged.
4. **`SPEC.md` Section 19 (Conformance Statement) — the obligation list widens with the rule.**
   Ensure the item that reads "The recovery class assigned to each Orchestrator Runtime State field
   (Section 4.1.8) and to any state an OPTIONAL extension introduces" also covers state Core
   behavior requires beyond Section 4.1.8, so Section 19 and Section 14.3 do not disagree about what
   a Statement must contain. This is the twin site of step 3: Section 19 carries the same
   extension-only framing, and widening one without the other leaves the document stating the
   narrower obligation in the section that defines what a Statement is. *Done when:* Section 19's
   recovery-class item names Core-introduced state, and its `Ephemeral` reset-consequence clause is
   unchanged.
5. **`conformance/vocabulary.json` — the token is published.** Ensure `runtime_state_fields.entries`
   gains `{"token": "repository_backoff", "recovery_class": "Ephemeral"}` in the position matching
   Section 4.1.8's order. *Done when:* the file parses, the group lists nine tokens, and every
   `recovery_class` value is one of the four `recovery_classes` tokens.
6. **`CONFORMANCE-STATEMENT-TEMPLATE.md` Section 5 (State Recovery-Class Assignments) — the field
   has a row.** Ensure the table gains `| `repository_backoff` | `Ephemeral` | `<...>` | `<...>` |`
   in Section 4.1.8's order. *Done when:* the table's Section 4.1.8 rows match Section 4.1.8's field
   list one for one.
7. **`CONFORMANCE-STATEMENT-TEMPLATE.md` Section 5 — the obligation from step 3 has a row.** Ensure
   the preamble sentence that reads "and any state a shipped extension introduces" also names state
   Core behavior requires beyond Section 4.1.8, and ensure the `<extension state field>` catch-all
   row covers both origins rather than extensions alone — a park record for an implementation that
   parks is the case that must land somewhere. *Done when:* a Statement generated from the template
   has a place to record a Core-introduced field, and the preamble no longer describes the table as
   Section 4.1.8 plus extensions.
8. **`SPEC.md` Section 17.4 (Orchestrator Dispatch, Reconciliation, and Retry) — the matrix covers
   the widened rule.** Ensure the bullet that reads "Every Orchestrator Runtime State field has a
   documented recovery class" also covers state Core behavior introduces beyond Section 4.1.8, and
   ensure a bullet asserts that a per-repository backoff is keyed by repository — a backed-off
   repository does not suppress dispatch for another. *Done when:* Section 17.4 carries both, with
   `Daemon Conformance` markers, and no existing bullet is removed.
9. **`SPEC.md` Section 18.1.3 (Daemon Conformance) and Section 18.1.1 (Both Layer Profiles) — both
   checklist items cover it.** Ensure the Section 18.1.3 item that reads "Every Orchestrator Runtime
   State field is assigned and documented as a recovery class" also covers Core-introduced state
   beyond Section 4.1.8, citing Section 14.3. Ensure the Section 18.1.1 item that summarises the
   published Conformance Statement — "each Orchestrator Runtime State field's recovery class" —
   likewise reaches state held beyond Section 4.1.8, since that bullet is what a REQUIRED-for-
   conformance reader checks against and it is narrower than Section 19 even before this decision
   widens Section 19. *Done when:* both bullets name Core-introduced state, and no second bullet is
   added in either section.
10. **`conformance/README.md` — the finding is recorded.** Ensure a "Surfaced findings" entry states
   the gap in the terms the corpus meets it: Section 14.2 mandated a per-repository backoff and two
   Core park MAYs, Section 4.1.8 held nothing keyed by repository, and Section 14.3 enumerated
   extension state only — so a generated Conformance Statement was complete against its own table
   and silently missing the restart behaviour of the one piece of state an operator most needs it
   for. *Done when:* the entry names decision 0137, issue #96, `repository_backoff`, and records
   that no vector is owed and why.

## Cross-cutting sync

- `SPEC.md` Section 6.4 (config cheat sheet) — no change; see Scope.
- `SPEC.md` Section 17 (test matrix) — step 8, one bullet extended and one added in Section 17.4.
- `SPEC.md` Section 18 (implementation checklist) — step 9, one existing bullet extended in each of
  Sections 18.1.3 and 18.1.1 rather than new ones added.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — steps 6 and 7. The `Implementation-defined` park-versus-retry
  choices and the unusable-policy backoff schedule already have their Section 4.1 rows (`:99`,
  `:100`, `:101`); this decision adds none there and adds two in Section 5.
- `conformance/vocabulary.json` — step 5.
- `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — unchanged.
  Orchestrator runtime state is Symphony's, not the engine's; `engine_invocation_failures` is
  Symphony's disposition for an engine that failed, not a behaviour of the engine.

## Anchor changes

- **Added:** `repository_backoff`, a field of `Orchestrator Runtime State` (Section 4.1.8), and its
  `runtime_state_fields` token in `conformance/vocabulary.json`.

Nothing is renamed or removed. Section 14.3's existing obligation over Section 4.1.8's fields and
over extension-introduced state is extended, not replaced; `repository_provisioning_failures`,
`engine_invocation_failures`, `node_provisioning_failures` and the four `recovery_classes` tokens all
keep their spelling.

## Status

Applied to `SPEC.md` (Sections 4.1.8, 14.3, 17.4, 18.1.1, 18.1.3, 19),
`conformance/vocabulary.json`, `CONFORMANCE-STATEMENT-TEMPLATE.md` (Section 5) and
`conformance/README.md`. Issue #96.
