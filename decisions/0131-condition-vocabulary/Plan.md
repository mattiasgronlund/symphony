# Plan — 0131 A value set closed in prose, and the field that points at it

## Scope

`VCSX-SPEC.md`: Sections 8.2 "Result Envelope", 13.1 "Test Matrix".

`conformance/vcsx/vocabulary.json`: a new `forge_unavailable_conditions` group; `hook_conditions`'
note; the `output_keys` entries `unperformed_intents`, `unfinished_hooks`, `unanswered_gates`,
`failed_by_policy`, `forge_budget` and `forge_unavailable_condition`; `schema_version`.

`conformance/vcsx/README.md`: the Schema section, and a new section stating what the registry
publishes.

`VCSX-CONTRACT.md`, `SPEC.md`, `CONFORMANCE-STATEMENT-TEMPLATE.md`,
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`, `conformance/vocabulary.json`: **none** — verified, see
"Cross-cutting sync".

## Steps

1. **The licence sentence.** In Section 8.2 "Result Envelope", ensure the bullet beginning
   `` `outputs` carries `forge_unavailable_condition` `` states, after "absent for every other
   reason", that the three are named tokens so the diagnosis a consumer reads is spelled the same on
   every engine, naming Section 6.6 as fixing the same for its own three. Ensure the bullet's
   existing "same arrangement `unanswered_gates` makes" sentence is kept — it claims cross-key
   uniformity, which is a different claim from cross-engine portability and is not replaced by it.
   Ensure no RFC 2119 keyword and no `Implementation-defined` is introduced, and that prose wraps at
   100 columns. Done-condition: Section 8.2 and Section 6.6 each carry a sentence fixing their three
   conditions as named tokens spelled the same on every engine.

2. **The test matrix row that makes it observable.** In Section 13.1, ensure the transient-forge
   check names the three tokens rather than referring to "its condition": the clause reading "a
   `forge_unavailable` result carries its condition in `outputs` and a result of any other reason
   carries none" states which of `server_error`, `bound_elapsed` and `transport_failure` occurred, in
   the shape the same section already uses for `outputs.unanswered_gates`. Ensure the "a result of
   any other reason carries none" half survives. Done-condition: Section 13.1 asserts the three
   forge-unavailable tokens by name, as it already asserts the three hook conditions by name.

3. **The group.** Ensure `conformance/vcsx/vocabulary.json` carries a top-level
   `forge_unavailable_conditions` group in `hook_conditions`' exact shape — `spec_refs`, `note`,
   `entries` of `{token, meaning}` — with entries `server_error`, `bound_elapsed` and
   `transport_failure`, each meaning read from the sections cited and none invented. Ensure
   `spec_refs` cite, verbatim in the file's existing citation format, Sections 4.3 "Reason-Token
   Registry", 8.1 "Entry Points and Arguments", 8.2 "Result Envelope" and 9 "Plugin API". Ensure the
   group is placed adjacent to `hook_conditions`, the set it mirrors. Done-condition: each of the
   three tokens appears in `VCSX-SPEC.md` in a section the group's `spec_refs` cite.

4. **The duplication, recorded in the note.** Ensure `forge_unavailable_conditions`' `note` states
   that `bound_elapsed` is also a `hook_conditions` token, that Section 6.6 fixes the spelling and is
   the authority for it, and that Section 9 reuses it deliberately so one event on two kinds of unit
   does not diagnose differently by which program the engine was waiting on. Ensure
   `hook_conditions`' `note` gains a one-clause pointer to `forge_unavailable_conditions` recording
   that `bound_elapsed` is shared. Done-condition: the sharing is discoverable from either group's
   note without reading the other's entries.

5. **The `meaning` stops restating the values.** Ensure the `output_keys` entry
   `forge_unavailable_condition` points at the group rather than enumerating its members, so the
   registry stays a derived view rather than two copies of one list. Ensure the entry keeps what is
   its own — that it is absent for every other reason, and that the reason routes while the condition
   diagnoses. Done-condition: neither `server_error` nor `transport_failure` appears anywhere in
   `output_keys`.

6. **`fields` becomes objects.** Ensure every `output_keys` entry carrying `fields` —
   `unperformed_intents`, `unfinished_hooks`, `unanswered_gates`, `failed_by_policy`, `forge_budget`
   — carries an array of objects whose `name` is the field name, rather than an array of strings, so
   one shape holds across the group. Ensure `task_model`'s group-level `fields` is **untouched**: it
   is a record of the consumer's task-model field set rather than an `output_keys` entry's field
   list, and `conformance/vcsx/README.md` already records `task_model` as departing from the entry
   shape. Done-condition: no entry under `output_keys` carries a flat-string `fields`, and
   `task_model.fields` is unchanged.

7. **The links.** Ensure `values_from` names the group closing a field's value space, and only where
   `VCSX-SPEC.md` fixes that space to exactly one group:
   - `forge_unavailable_condition` carries `values_from: "forge_unavailable_conditions"` at **entry**
     level, the key being scalar rather than an array of records.
   - `unfinished_hooks`' `condition` field carries `values_from: "hook_conditions"`.
   - `unanswered_gates`' `condition` field carries `values_from: "hook_conditions"`.

   Ensure `unanswered_gates`' `position` field carries **no** `values_from`: Section 5.1 admits "any
   engine-defined `before:<op>`" and Section 4.1 states an engine MAY define additional operations
   and their positions, so `lifecycle_positions` is the required set and not the field's value space.
   Ensure no `values_from` is authored on `unperformed_intents`' `action` (the consumer-effected
   subset of `actions`, which the registry cannot express without leading rather than deriving), on
   either `trigger` field (a composed grammar), on `failed_by_policy`'s `reason` (repository-authored,
   as the entry already states), or on `detail`, `hook`, `arguments`, `buckets` and `observed_at`.
   Done-condition: every `values_from` in the file names an existing non-empty group, and every field
   carrying one has its value space fixed to exactly that group by the section the entry cites.

8. **`schema_version`.** Ensure it reads `2`. Done-condition: the file states a version a consumer
   reading `fields` as strings can branch on.

9. **`fields` is documented.** In `conformance/vcsx/README.md`'s "Schema" section, ensure `fields` is
   described: the fields the specification fixes inside an entry's record, either an array of strings
   or an array of objects whose `name` is the field name; and `values_from` as the group that closes
   that field's value space, present only where the specification fixes it to exactly one group.
   Done-condition: a reader can tell from the README alone what shape `fields` takes and what
   `values_from` licenses a generator to do.

10. **What this registry publishes.** Ensure `conformance/vcsx/README.md` carries a new `##` section
    — heading level matching `Precedence`, `Schema`, `Normalizations` and `Using it` — stating
    decision 0103's reader test, citing `conformance/README.md` as where it was introduced, and
    recording that decision 0131 applied it to this file with the scan's result. Ensure it does
    **not** introduce a deferral list for this registry: a bullet naming the reader a set lacks is
    added only for sets actually derived, and deriving the full list is separate work. Done-condition:
    the engine registry states what it contains and why, so a report in #78's shape arrives against a
    published question rather than one that has to be re-derived from a decision in the other tree.

## Cross-cutting sync

`VCSX-SPEC.md` Section 13.1 (test matrix) — **changes**, step 2.

`VCSX-SPEC.md` Section 13.2 (implementation checklist) — **checked, unchanged.** Its transient-forge
bullet already reads "with `forge_unavailable`'s condition in `outputs`", which is the summary
altitude that section keeps; naming the three there would state the matrix's detail in the checklist.

`VCSX-SPEC.md` Section 13.3 (Conformance Statement) and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — **checked, unchanged.** This decision adds no
`Implementation-defined` behavior and no "MUST document" clause, so `CLAUDE.md`'s rule that such an
obligation MUST add its row to the matching template is not triggered. Stated here rather than left
to be inferred, that rule having been missed three decisions running before 0128 caught it.

`VCSX-CONTRACT.md` — **no edits, verified rather than assumed.** `forge_unavailable` appears nowhere
in it, so Section 14's alignment rule — no token spelled in one document and absent from the other —
is not engaged by a group derived from Section 8.2.

`SPEC.md` and `CONFORMANCE-STATEMENT-TEMPLATE.md` — **no edits, verified.** Neither spells
`forge_unavailable` or any of the three conditions.

`conformance/vocabulary.json` (the Symphony registry) — **no edits.** A separate artifact with its own
schema and its own consumers; it keeps `schema_version: 1`.

## Anchor changes

Added anchors:

- `forge_unavailable_conditions`, a top-level group in `conformance/vcsx/vocabulary.json`.
- `values_from`, a registry field name, on an `output_keys` entry or on one of its `fields` members.
- `name`, the field-name key inside a promoted `fields` object.

No anchor is renamed or removed. No `VCSX-SPEC.md` section is inserted, retitled or renumbered, so
every existing `Section N.M` cross-reference keeps its target.

Deliberately **not** an anchor: `lifecycle_positions` as the value space of
`unanswered_gates.position`. The group exists and the link does not, and the reason is recorded in
`Background.md` so a later reader does not add it as an oversight repair.

## Status

Applied to `VCSX-SPEC.md` (Sections 8.2, 13.1), `conformance/vcsx/vocabulary.json` and
`conformance/vcsx/README.md`.
