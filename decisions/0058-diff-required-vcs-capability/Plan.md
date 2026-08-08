# Plan — 0058 `diff(base)` is a required VCS backend capability

## Scope

`VCSX-SPEC.md` Sections 9.1 "VCS Backend Plugin" and 13.3 "Conformance Statement".
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` follows.

No `VCSX-CONTRACT.md` edit: its Section 6 names the operations a configuration references
("Named operations include: `commit`, `integrate`, `push`, `create_pr`, `merge`") without claiming to be
exhaustive, and its Section 11 defers the plugin API to `VCSX-SPEC.md`. No `SPEC.md` edit: Symphony does
not reference the engine's VCS backend capabilities. No corpus change: the plugin API is not
deterministic from inputs alone and is already listed under `conformance/vcsx/README.md`'s deferred
slices.

## Steps

1. **`diff(base)` is a required VCS backend capability.** Ensure Section 9.1's required-capability list
   has an entry `diff(base)` → `diff:*` describing the branch delta against the resolved base
   (Section 6.4), read-only, in the bullet shape its neighbours use. Done when every operation Section
   4.1 requires of a VCS backend traces to a capability in this list.
2. **The list is stated to be a minimum.** Ensure Section 9.1 records that the capabilities listed are
   the minimum every backend MUST provide, and that an engine defining an additional operation
   (Section 4.1) MUST document the capabilities it requires of a backend. Done when a reader can answer
   whether a backend may be asked for more than the list without inferring it.
3. **Section 13.3 collects the new obligation.** Ensure the Conformance Statement's required content
   includes the capabilities any engine-defined operation requires of a backend (Section 9.1), alongside
   the descriptors its plugins advertise. Done when the "MUST document" clause added in Step 2 has a
   home in the Statement.
4. **The template has a row for it.** Ensure `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`'s VCS backend
   section carries a place to declare capabilities required beyond Section 9.1's list. Done when an
   engine that defines an extra operation has somewhere to record what it demands of a plugin.

## Cross-cutting sync

`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Step 4). No vocabulary change: `vocabulary.json` records
tokens the two documents share, and plugin capability names are not among its groups.

## Anchor changes

None. `diff(base)` is a new capability name; no existing anchor is renamed or removed.

## Out of scope

- **A capability descriptor field for `diff`.** It is required of every backend, so there is nothing to
  advertise; Section 9.1's descriptor fields are unchanged.
- **Parts 1a and 1b of issue #2**, taken up as decision 0057.

## Status

Applied to `VCSX-SPEC.md` (Sections 9.1, 13.3) and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.
