# Plan — 0005 Config and trust split

## Scope

Splits the configuration model into two surfaces: `WORKFLOW.md` (Section 5) and a new operator-owned
policy config artifact. Revises the Configuration Specification (Section 6), "Hook Script Safety"
(Section 15.4), and "Dynamic Reload Semantics" (Section 6.2). Field-by-field placement is detailed by
the owning decisions (credentials 0003; sandbox 0004; agent 0006; VCS 0007; tracker and state-machine
0008; repo map 0009); this decision lands the principle and the two artifacts.

## Steps

1. Ensure the spec defines the dividing principle: `WORKFLOW.md` contains only settings used inside
   the sandbox; all settings Symphony uses outside the sandbox live in operator-owned policy config
   that the repo/agent cannot modify. Done when both artifacts and the rule are defined.
2. Ensure `WORKFLOW.md`'s scope is narrowed to the prompt template and in-sandbox hooks, and that it
   is described as repo-owned and untrusted. Done when Section 5 reflects the narrowed scope and the
   trust change.
3. Ensure hooks are split: privileged setup hooks in policy config run outside the sandbox; build/test
   hooks in `WORKFLOW.md` run inside the sandbox without credentials. Done when Section 15.4 and the
   hooks schema reflect the split.
4. Ensure dynamic reload (Section 6.2) covers both surfaces, with invalid reload keeping last-known-
   good effective configuration for each. Done when reload semantics name both artifacts.

## Cross-cutting sync

Config cheat sheet (6.4): partition into a `WORKFLOW.md` table and a policy-config table. Test matrix
(17) and checklist (18): add policy-config validation and reload rows; update the hook rows for the
split.

## Anchor changes

- `hooks.*` (Section 5.3.4) — partitioned: privileged setup hooks move to policy config; in-sandbox
  hooks remain in `WORKFLOW.md`.
- "Hooks are fully trusted configuration" (Section 15.4) — removed/qualified: only policy-config hooks
  are trusted; `WORKFLOW.md` hooks run sandboxed and credential-less.
- New anchors: the policy config artifact and the in-sandbox-only rule.

## Status

Not started. Recorded as `Proposed`; `SPEC.md` not yet edited.
