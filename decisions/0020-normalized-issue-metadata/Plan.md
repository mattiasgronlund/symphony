# Plan — 0020 Normalized issue metadata and optional fields

## Scope

Adds an opaque `metadata` carrier to the normalized `Issue` (Section 4.1.1) and marks `branch_name` and
`blocked_by` OPTIONAL/tracker-dependent. Records adapter-dependent derivation in Section 11.3, makes the
blocker-gating degradation explicit in Section 8.2, and syncs prompt rendering (Section 12.2) and the
Section 17.3 normalization test rows. No config or new entity; `metadata` is part of the existing `Issue`.

## Steps

1. In Section 4.1.1 "Issue", ensure a `metadata` (map) field exists: opaque, adapter-owned key/value pairs
   carrying tracker-specific data the other fields do not capture, empty when the adapter has none, not
   interpreted by the orchestrator core, and usable by an adapter to round-trip a provider write handle
   (for example a GitHub Projects v2 item id). Done when `metadata` is documented on the Issue entity.

2. In Section 4.1.1, ensure `branch_name` and `blocked_by` are documented as OPTIONAL and tracker-dependent:
   an adapter without native branch metadata leaves `branch_name` null or MAY synthesize one; an adapter
   without a dependency model leaves `blocked_by` empty, and blocker-gated dispatch (Section 8.2) then
   observes no blockers. Done when both fields state their tracker-dependent/optional semantics.

3. In Section 8.2, ensure the `Todo` blocker rule notes that an adapter that does not populate `blocked_by`
   reports no blockers, so the rule does not gate. Done when the rule is self-contained on that point.

4. In Section 11.3, ensure the normalization details state that `blocked_by` and `branch_name` derivation is
   Linear-specific (other adapters populate per their model or leave empty), and that `metadata` contents
   are `Implementation-defined` (MUST document). Done when Section 11.3 reflects adapter-dependent fields
   and an Implementation-defined `metadata`.

5. In Section 12.2, ensure `metadata` is among the nested maps preserved for templates. Done when the
   rendering rule lists it.

6. Cross-cutting sync of Section 17.3 (see below).

## Cross-cutting sync

- Section 17.3 "Issue Tracker Client": qualify the blocker-normalization row as Linear-specific and add a
  row that `blocked_by`/`branch_name` are tracker-dependent (empty `blocked_by` ⇒ no blocker gating) and a
  row that `metadata` carries adapter-defined provider-specific fields.
- Section 6.4 cheat sheet: no change (`Issue` is a domain entity, not config).
- Section 18 checklist: no change (it does not enumerate normalized `Issue` fields).

## Anchor changes

- New field: `metadata` on the Section 4.1.1 `Issue` entity.
- `branch_name` and `blocked_by` gain OPTIONAL/tracker-dependent semantics; neither is renamed or removed.

## Status

Applied to `SPEC.md`.
