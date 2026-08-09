# Plan — 0069 `observability.*` is the configuration namespace for observability settings

## Scope

`SPEC.md` only: the `RECOMMENDED Extensions (Not REQUIRED for Conformance)` checklist (Section 18.2),
the `Per-Execution Usage Ledger (OPTIONAL)` section (Section 13.6), and the
`Core Config Fields Summary (Cheat Sheet)` (Section 6.4).

No edit to `Configuration Schema` (Section 5.3): its "Top-level operator-config keys" list enumerates
the *core* schema, and no extension namespace appears in it — not `budget`, `quota`, `compute`, or
`server`. Its Note already permits an extension to define additional top-level keys and requires the
extension to document its field schema, which is precisely the mechanism this decision uses.

No edit to `Logging Outputs and Sinks` (Section 13.2), `OPTIONAL Human-Readable Status Surface`
(Section 13.4), or `Humanized Agent Event Summaries (OPTIONAL)` (Section 13.7): none of them names a
config key today, so none carries a namespace to correct. Section 18.2 is where a namespace is named
for every other extension, and naming it once is what keeps the three surfaces consistent.

No edit to `Test and Validation Matrix` (Section 17): no behavior is added. The namespace reserves a
key prefix; it defines no field to parse, default, or validate, so there is nothing to assert. A
Section 17 bullet would have to invent a field to test.

No edit to `OPTIONAL HTTP Server Extension` (Section 13.8): `server.*` is an existing, separately
owned namespace and is untouched. Its placement in `WORKFLOW.md` front matter is in tension with
Section 5 and is recorded as a surfaced finding rather than changed here (see `Out of scope`).

No `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, or conformance-vector edit: the namespace is Symphony's, and
no engine token or behavior changes.

## Steps

1. **Section 18.2's TODO is replaced by a namespace bullet.** Ensure the bullet beginning "TODO: Make
   observability settings configurable" no longer exists, and that
   `RECOMMENDED Extensions (Not REQUIRED for Conformance)` instead carries a bullet stating that
   observability settings own the `observability.*` config namespace, naming the surfaces that
   configure there — the log sink (Section 13.2), a human-readable status surface (Section 13.4),
   humanized event summaries (Section 13.7), and the usage ledger's storage location and retention
   (`observability.ledger.*`, Section 13.6). Done when `SPEC.md` contains no `TODO` about
   observability configuration and a reader can find the namespace by searching `observability.*`.
2. **The bullet states the artifact and why.** Ensure it states that the namespace belongs to the
   operator policy config, not `WORKFLOW.md`, because these are deployment concerns with host-side
   effects that a repository-owned, in-sandbox artifact MUST NOT carry (Sections 5, 15.4). Done when
   an implementer cannot place a sink path in `WORKFLOW.md` and cite this bullet.
3. **The bullet states the scope line.** Ensure it states that this specification names the
   namespace, not the fields — sinks and surfaces being implementation-defined (Sections 13.2,
   13.4) — and that an implementation defines what it needs under `observability.*` and documents it
   with the extension (Section 5.3) and in its Conformance Statement (Section 19). Done when the
   absence of a field schema reads as a decision rather than an omission.
4. **The ledger's namespace is named.** Ensure Section 13.6's "Scope and configuration" bullet reads
   that the ledger owns its configuration under the `observability.ledger.*` namespace (Section 18.2)
   rather than "under its own namespace", keeping the existing "documented with the extension" and
   "Core conformance does not require these fields" clauses. Done when Section 13.6's namespace
   obligation names a namespace.
5. **The cheat sheet carries the namespace.** Ensure Section 6.4's "Operator policy config" list
   carries `observability.*` (OPTIONAL observability settings, no core fields, Section 18.2) and
   `observability.ledger.*` (usage-ledger settings, no core fields, Section 13.6), in the one-bullet-
   per-key shape the list already uses. Done when a reader implementing the config layer from the
   cheat sheet alone learns the namespace exists and that it has no core fields.

## Cross-cutting sync

- Section 6.4 "Core Config Fields Summary (Cheat Sheet)": changed by Step 5.
- Section 17 "Test and Validation Matrix": no change, for the reason in `Scope`.
- Section 18 "Implementation Checklist": Section 18.2 changed by Steps 1–3. Section 18.1 is
  unchanged: nothing here is REQUIRED for conformance.
- `CONFORMANCE-STATEMENT-TEMPLATE.md`: its Section 2 namespace column carries `observability.*` and
  `observability.ledger.*` — applied under decision 0070, which owns that file.
- `conformance/vocabulary.json`: `config_namespaces` carries `observability` — applied under decision
  0071, which creates that file.

## Anchor changes

None removed or renamed. Added: the config namespaces `observability.*` and
`observability.ledger.*`. The Section 18.2 TODO bullet is removed as a bullet, but it was never an
anchor: no other passage referenced it.

## Out of scope

- **Defining observability fields.** Rejected as Option E in `Background.md`: Sections 13.2 and 13.4
  make the sink and the surface implementation-defined, so there is no cross-implementation field to
  define, and naming one would prescribe the UI details the TODO rules out.
- **Reconciling `server.*`'s placement.** Section 13.8 enables the HTTP server from `WORKFLOW.md`
  front matter, which Section 5 forbids for a setting Symphony executes with host access. Recorded in
  `conformance/README.md`'s surfaced findings; it is a defect in Section 13.8 and needs its own
  decision.
- **Adding `vcs` to Section 5.3's top-level key list.** Noticed while enumerating namespaces
  (Section 6.4 documents `vcs.*` as operator config; Section 5.3's list omits it) and recorded as a
  surfaced finding. Unrelated to observability.
- **Making anything configurable.** This decision reserves a namespace. Whether an implementation
  ships a configurable sink at all remains its choice.

## Status

Applied to `SPEC.md` (Sections 6.4, 13.6, 18.2).
