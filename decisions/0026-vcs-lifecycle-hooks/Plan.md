# Plan — 0026 VCS-operation lifecycle hooks aligned with `vcsx`

## Scope

Additive, OPTIONAL. Affected anchors in `SPEC.md`:

- Section 9.4 "Workspace Hooks" — add a sibling VCS-operation lifecycle hook set; keep the existing
  workspace lifecycle hooks (`after_create` / `before_run` / `after_run` / `before_remove`) distinct.
- Section 15.4 "Hook Script Safety" — classify each new hook onto the existing two-trust-level model.
- Sections 9.8 "Git Automation and Work Branch", 9.9 "Broker Git Verbs", 9.10 "Forge Adapter, Pull
  Requests, and Review Writes" — name the lifecycle points at which the new hooks fire (around
  commit/push and the `pr` verb).
- Section 9.6 "Agent Sandbox and Execution Isolation" — note the bind-mounted working tree as the
  only channel between an in-sandbox `before_commit` and a host-side `after_push`.
- Section 5.3.4 `hooks` (object) — add the OPTIONAL VCS-lifecycle keys, split from the workspace keys.
- Cross-cutting: Section 6.4 (cheat sheet), Section 17 (test matrix), Section 18 (checklist).

This plan defines the end-state only; no `SPEC.md` edit is made while the decision is `Proposed`.

## Steps

1. **Introduce the VCS-operation lifecycle hook set.** Ensure `SPEC.md` defines an OPTIONAL set of
   four hooks — `before_commit`, `before_push`, `after_push`, `before_pull_request` — fired around the
   broker's commit/push (Sections 9.8–9.9) and forge `pr` (Section 9.10) verbs, explicitly distinct
   from the workspace lifecycle hooks of Section 9.4. Done when each of the four names appears as a
   defined hook with its firing point stated.

2. **Two contract classes by prefix.** Ensure `before_*` hooks are veto hooks: a non-zero result
   blocks the operation and surfaces a stable reason code consistent with the broker result contract
   (Section 10.8) — for example `check_failed`, `forbidden_tokens` — and `before_pull_request` MAY
   additionally rewrite the pull-request title/body. Ensure `after_*` hooks are best-effort: their
   failure or timeout is logged and never blocks the operation, mirroring the `after_run` /
   `before_remove` semantics already in Section 9.4. Done when both classes' blocking-vs-best-effort
   semantics are stated and tied to existing reason-code and hook-failure language.

3. **Trust classification on the existing model.** Ensure Section 15.4 places `before_commit` at the
   repo-owned, untrusted, in-sandbox level (it warms an artifact, receives no credentials or secrets,
   runs under the Section 9.6 sandbox profile) and places `before_push`, `after_push`, and
   `before_pull_request` at the operator-owned, trusted, host-side policy-config level. Done when each
   of the four hooks is assigned a trust level by name in Section 15.4.

4. **`after_push` secret + outward-write allowance.** Ensure `after_push` MAY receive a declared
   secret through the secret-provider interface (Section 15.3) and MAY perform outward writes under
   the operator's credentials (for example publishing a sidecar ref), with the secret never present
   in the sandbox. Done when `after_push` is documented as secret-bearing and host-credentialed, and
   the no-secret-in-sandbox invariant (Section 15.3) is cited as preserved.

5. **Worktree as the only cross-boundary channel.** Ensure Section 9.6 states that an in-sandbox
   `before_commit` and a host-side `after_push` communicate **only** through durable state in the
   bind-mounted working tree — never the broker channel, process state, or environment — so a warmed
   artifact crosses the trust boundary as worktree content. Done when the worktree-channel rule is
   stated for the `before_commit` → `after_push` pair.

6. **Inputs available to the hooks.** Ensure the spec lists the context each hook receives:
   `before_*` get the relevant content and a surface label plus `branch` and resolved `base`;
   `after_push` additionally gets the pushed commit identifier (so an integration can bind a worktree
   artifact to exactly what was pushed). Done when `after_push` is documented as receiving the pushed
   commit id and the `before_*` hooks as receiving a surface label.

7. **Base resolution stays configuration.** Ensure base resolution remains `vcs.base_branch` (Section
   9.7) and is **not** introduced as a lifecycle hook (mirrors the companion `vcsx` demotion of
   `resolve-base`). Done when no `resolve_base`-style hook is added and base resolution is unchanged.

8. **Config keys (Section 5.3.4).** Ensure the `hooks` object documents the four OPTIONAL VCS-lifecycle
   keys separately from the workspace-lifecycle keys, each defaulting to unset (a missing hook is a
   no-op), and notes that the set is OPTIONAL. Done when the keys are listed with `OPTIONAL` and an
   unset default.

9. **Mark OPTIONAL extension.** Ensure the set is labeled an OPTIONAL extension owning its own config
   keys, so Core Conformance is unaffected and a deployment relying only on the forge's merge-time
   gate wires none of them. Done when the OPTIONAL marking is present and Section 18.1 is not expanded
   to require the set.

## Cross-cutting sync

- **Section 6.4 (cheat sheet):** add the four OPTIONAL VCS-lifecycle hook keys (unset default), grouped
  apart from the existing `hooks.after_create` / `before_run` / `after_run` / `before_remove` rows.
- **Section 17 (test matrix):** add cases — a `before_push` non-zero blocks the push with the expected
  reason code; an `after_push` failure is logged and does not block; a `before_pull_request` rewrite
  is applied to the PR body; a warmed `before_commit` artifact is visible to a host-side `after_push`
  via the worktree; with no VCS-lifecycle hooks configured, behavior is unchanged.
- **Section 18 (checklist):** add a RECOMMENDED-extension entry under Section 18.2 (not 18.1).

## Anchor changes

New code-tokens introduced (no renames or removals): `before_commit`, `before_push`, `after_push`,
`before_pull_request`. Companion `vcsx`-side anchor changes (for cross-reference; not `SPEC.md`
anchors): `validate` → `before_commit`/`before_push`; `scan-content` →
`before_commit`/`before_pull_request`; `pr-body-transform` → folded into `before_pull_request`;
`post-push` → `after_push`; `post-gate` → folded into `after_push`; `resolve-base` → removed (base
becomes config).

## Status

Superseded by decision 0030 (see this decision's `Background.md` re-evaluation). This plan is **not**
executed as written: under 0030 the lifecycle positions are realized as trigger names within the one
action-policy machine, not as a separate hook axis, so the spec edits land through decision 0030's
plan. No `SPEC.md` change was ever made under this decision.
