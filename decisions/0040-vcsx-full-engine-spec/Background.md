# Background — 0040 Author the full vcsx engine specification

## Context

Decision 0039 authored `VCSX-CONTRACT.md`, the contract *surface* of the `vcsx` engine — the names and
surface semantics Symphony's `SPEC.md` references — and deliberately deferred the deep detail to a
"full engine specification" that did not yet exist: the engine invocation contract and version grammar,
the field-level `repo.policy.toml` schema, the plugin API, the concrete per-operation reason-token
registry, and the internal algorithms (`VCSX-CONTRACT.md` §11).

With the 0027–0032 batch now applied to `SPEC.md` against that surface, the surface is load-bearing but
its deferral target is still empty. An implementer building the engine (or a second consumer embedding
it) has the vocabulary but not the schema, the result contract, the plugin interfaces, or the
reference algorithms. The forward reference needs to resolve to a real document, the way `SPEC.md`
resolves its Codex-app-server-protocol deferral to that protocol's own specification.

## Options considered

- **Option A — keep deferring to an unwritten full spec.** Trade-offs: no new artifact to maintain, but
  the engine cannot be implemented from the surface alone, and "consult the full engine specification"
  points at nothing. Rejected.
- **Option B — fold the full detail into `VCSX-CONTRACT.md`.** One `vcsx` document containing both the
  surface and the full detail. Trade-offs: no indirection, but it inflates the small, heavily
  cross-referenced surface that `SPEC.md` points at into a large document, coupling the stable
  vocabulary layer to the churn of schema/algorithm detail. It also loses the clean two-level deferral
  that mirrors the Codex-protocol pattern.
- **Option C — author a separate `VCSX-SPEC.md` the surface defers to (chosen).** A full, standalone,
  language-agnostic engine spec that `VCSX-CONTRACT.md` §11 names as its deferral target. Trade-offs: a
  second document to keep name-aligned with the surface, but it keeps the surface small and stable while
  the full spec carries the invocation contract, the `repo.policy.toml` field schema, the plugin API,
  the reason registry, and the reference algorithms.

## Decision and reasoning

Choose **Option C**. Author `VCSX-SPEC.md` as the full engine specification and wire `VCSX-CONTRACT.md`
(header, §11, §12) to name it as the deferral target. The layering is now three clean levels, each
deferring the next's detail rather than restating it: Symphony `SPEC.md` → the `vcsx` contract surface
(`VCSX-CONTRACT.md`) → the full engine spec (`VCSX-SPEC.md`). This mirrors how `SPEC.md` already defers
to an external protocol specification and keeps every document language-agnostic.

`VCSX-SPEC.md` fixes what the surface deferred: the operation set and the concrete reason-token registry
with stable proto classes; the full action-policy machine (triggers, actions, the `#class` matching
ladder, unmatched policy, determinism, escalation binding); the field-level `repo.policy.toml` schema
(with `vcsx.toml` merge, base resolution, execution-context labeling); the two front-ends and the
embedded-driver contract; the transport-neutral invocation contract (result envelope, exit codes,
escalation payload, versioning with a `version_floor` floor); the plugin API for VCS and forge backends
with capability descriptors; the message-formulation seams (`scan-content`, PR composition,
`pr_to_squash`) with no built-in format; a security/trust model that enforces nothing itself but
structures a consumer's boundary; and reference algorithms (matching, `ship`, `land`, base resolution,
PR-body composition). Every shared token is spelled identically to the surface (`VCSX-SPEC.md` §14).

We would reconsider if the surface/full split proves to cost more in name-drift maintenance than the
indirection saves (fold into one document, Option B), or if the engine's real implementation forces a
schema the language-agnostic spec cannot express without naming a runtime (then the spec defers that
part explicitly rather than naming an implementation).
