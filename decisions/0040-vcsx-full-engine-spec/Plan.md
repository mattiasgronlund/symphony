# Plan — 0040 Author the full vcsx engine specification

## Scope

New artifact `VCSX-SPEC.md` at the repository root (a companion to `SPEC.md` and `VCSX-CONTRACT.md`),
plus wiring in `VCSX-CONTRACT.md` so the surface names the full spec as its deferral target. No
`SPEC.md` edit is made; `SPEC.md` continues to defer to the surface (`VCSX-CONTRACT.md`), which now
defers its deep detail to `VCSX-SPEC.md`.

`VCSX-SPEC.md` fixes what `VCSX-CONTRACT.md` §11 deferred:

- the operation set and the concrete per-operation reason-token registry with stable proto classes
  (`done`/`needs_caller`/`error`);
- the full action-policy machine: triggers, actions, the `#class` matching ladder, fail-safe
  unmatched-outcome / no-op unmatched-signal, determinism, and escalation binding;
- the field-level `repo.policy.toml` schema (`[engine]`, `[scope]`, `[base]`, `[policy]`, `[hooks]`,
  `tracker.transitions`, `[messages]`, `[tasks]`/`[driver]`), `vcsx.toml` merge, base resolution, and
  execution-context labeling;
- the two front-ends (`ship`, `land`) and the embedded-driver contract;
- the transport-neutral invocation contract: result envelope, exit codes, escalation payload, and
  versioning with a `version_floor` floor;
- the plugin API (VCS backend, forge backend) and capability descriptors;
- the message-formulation seams (`scan-content`, PR composition, `pr_to_squash`) with no built-in
  format;
- the security/trust model and reference algorithms.

## Steps

1. **Author `VCSX-SPEC.md`.** Ensure the file exists, is language-agnostic (names no implementation
   language normatively), and fixes each surface above with tokens spelled identically to
   `VCSX-CONTRACT.md`. Done when the file exists and the deferred items of `VCSX-CONTRACT.md` §11 each
   have a defining section.

2. **Wire the surface to the full spec.** Ensure `VCSX-CONTRACT.md` names `VCSX-SPEC.md` as its deferral
   target: the header status, §11 (per-item pointers into `VCSX-SPEC.md`), and §12 alignment. Done when
   §11 points every deferred item at a `VCSX-SPEC.md` section and the header no longer calls the surface
   a stub whose target is unwritten.

3. **State the alignment rule.** Ensure `VCSX-SPEC.md` §14 requires identical names across the surface
   and the full spec and states the governance (name here vs schema there). Done when the alignment rule
   is stated in both documents.

## Cross-cutting sync

None in `SPEC.md`. `SPEC.md` continues to reference `VCSX-CONTRACT.md`; the new indirection is entirely
between the two `vcsx` documents. `VCSX-SPEC.md` carries its own conformance test matrix and checklist
(Section 13) for the engine.

## Anchor changes

New artifact: `VCSX-SPEC.md`. `VCSX-CONTRACT.md` header/§11/§12 updated to name it. No `SPEC.md`
anchors are added, renamed, or removed.

## Status

Applied — `VCSX-SPEC.md` authored and `VCSX-CONTRACT.md` wired to it. Builds on decision 0039 (the
contract surface) and completes its deferred forward artifact. The three-level deferral is now closed:
`SPEC.md` → `VCSX-CONTRACT.md` → `VCSX-SPEC.md`.
