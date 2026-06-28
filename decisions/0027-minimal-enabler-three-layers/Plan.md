# Plan — 0027 Minimal enabler and the three-layer architecture

## Scope

Framing-level. Affected anchors in `SPEC.md`:

- Section 1 "Problem Statement" and Section 2 "Goals and Non-Goals" — state the enabler-not-enforcer
  principle and name the **secret-isolation invariant** as the sole Core-Conformance guarantee in the
  VCS/forge/tracker domain.
- Section 18 "Conformance" (18.1 Core / 18.2 extensions) — split a **broker-core** Core Conformance
  from the OPTIONAL engine and daemon layers.
- The broker entity (Section 10.8) and the sandbox (Section 9.6) — name them as the **broker core**,
  a standalone-conformant unit.
- A new short subsection naming the three **deployment topologies** (daemon, interactive-agent,
  engine-direct) as profiles over the layers.

This plan defines the end-state only; no `SPEC.md` edit is made while the decision is `Proposed`.

## Steps

1. **State the governing principle.** Ensure Sections 1–2 say Symphony *enables* Ways of Working and
   *enforces* none beyond the secret-isolation invariant (the agent never needs VCS/Forge
   credentials) and its scope guard. Done when the principle and the single invariant are stated as
   the Core-Conformance boundary for this domain.

2. **Name the three layers.** Ensure the spec defines: **broker core** (secret isolation + scope +
   per-run socket + credentialed-op mediation, ≈ decisions 0003/0004); **engine** (`vcsx`, optional;
   decision 0028); **autonomous daemon** (poll/dispatch/concurrency/multi-repo + task management +
   autonomous driver). Done when each layer is named with its responsibilities and its dependency
   direction (daemon → broker core; engine consumed by both front-ends).

3. **Broker core is independently conformant.** Ensure the spec states the broker core can be
   satisfied *without* the daemon, so an interactive-agent session gets secret isolation + WoW
   automation with no polling/dispatch. Done when broker-core conformance is defined separately from
   the daemon.

4. **Name the deployment topologies.** Ensure the spec lists three profiles — daemon (autonomous),
   interactive-agent (broker core + `ship`/`land`), engine-direct (`vcsx` alone, operator holds
   secrets) — each as a composition of the layers. Done when the three profiles appear with their
   layer composition.

5. **Conformance split.** Ensure Section 18 places broker-core in Core Conformance and the engine +
   daemon layers as OPTIONAL, so a deployment relying only on the forge's merge-time gate conforms.
   Done when 18.1 names only the broker-core guarantees and the layers are under 18.2.

## Cross-cutting sync

- **Section 6.4 (cheat sheet):** note the layer/topology split where config surfaces are summarized.
- **Section 17 (test matrix):** add a topology-conformance case — broker-core secret isolation holds
  in all three topologies; the daemon is absent in the interactive-agent topology.
- **Section 18 (checklist):** restructure into broker-core Core vs OPTIONAL layers.

## Anchor changes

New terms introduced (no renames or removals): **broker core**, **autonomous daemon**, **engine**
(as a layer), and the three deployment-topology profile names. Relates to decisions 0003/0004
(unchanged keystone) and is the parent of 0028–0032.

## Status

Accepted; `SPEC.md` application not started. The framing edits are deferred and batched with
decisions 0028–0032: 0027's planned spec text forward-references those decisions (engine ≈ 0028,
task management ≈ 0031, the configurable seams ≈ 0029–0032), so applying 0027 alone would bake
forward-references to still-`Proposed` framing into `SPEC.md`. Apply in step with those decisions.
