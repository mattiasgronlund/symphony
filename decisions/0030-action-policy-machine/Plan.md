# Plan — 0030 The action-policy machine

## Scope

Affected anchors in `SPEC.md`:

- Section 11.6 / the `tracker.transitions` model (decision 0017) — reframed as one binding within the
  machine.
- The VCS-operation lifecycle hooks (decision 0026: `before_commit`/`before_push`/`after_push`/
  `before_pull_request`) — reframed as trigger names; `after_push` → `push:ok`.
- A new "action-policy" subsection defining triggers, actions, matching, and the unmatched policies.
- The engine reason-token contract — each reason carries a proto class.

This plan defines the end-state only; no `SPEC.md` edit is made while the decision is `Proposed`.

## Steps

1. **Define the machine.** Ensure `SPEC.md` defines a single `(trigger) → (action)` policy, with the
   trigger kinds (lifecycle positions, typed operation results, task-state events) and action kinds
   (`run_op`, `run`, `escalate`, `create_task`, `set_state`, `notify`, `park`, `fail`). Done when
   triggers and actions are enumerated.

2. **Hooks are edges.** Ensure the spec states the lifecycle positions of decision 0026 are trigger
   names (not a separate hook axis), with `after_push` expressed as `push:ok`. Done when the four
   positions appear as triggers and the separate-axis framing of 0026 is superseded.

3. **`#class` fallback matching.** Ensure matching is most-specific-wins over `op:reason`, then
   `op:#class`, then `#class`, then a built-in default, where `#class` is the proto outcome class
   (`done`/`needs_caller`/`error`). Done when the precedence order and an example ladder
   (`push:non_fast_forward` → `push:#error` → `#error`) are stated.

4. **Two unmatched policies.** Ensure an unmatched *signal* is a benign no-op (decision 0017) while an
   unmatched *operation outcome* is **fail-safe** (park/fail + surface the proto reason). Done when
   both unmatched behaviors are stated and distinguished by trigger kind.

5. **Abstract `escalate`.** Ensure `escalate` names the need and the *front-end* binds the resolver
   (daemon → agent task per decision 0031; interactive → return typed result to the human). Done when
   `escalate` and its per-front-end binding are defined and tied to decision 0028's two front-ends.

6. **Reason class is public.** Ensure the engine reason-token contract records the proto **class** of
   each reason alongside the token, since configs branch on it. Done when the contract states the
   class is part of the public surface.

## Cross-cutting sync

- **Section 6.4 (cheat sheet):** add the trigger/action vocabulary and the `#class` fallback rule.
- **Section 17 (test matrix):** add cases — a `push:#error` edge catches an unnamed push error; an
  unmatched operation outcome is fail-safe (parked, not dropped); an unmatched signal is a no-op; an
  `escalate` binds to a task under the daemon and to the human interactively.
- **Section 18 (checklist):** note that the machine subsumes the transition graph and the hook axis.

## Anchor changes

New tokens: `escalate`, the `#class` trigger forms (`#error`, `op:#needs_caller`, …), the
`before:merge` position (shared with decision 0032). Generalizes decision 0017 (`tracker.transitions`
becomes a `set_state` binding). Supersedes the positional-hook axis of decision 0026 — the four names
`before_commit`/`before_push`/`after_push`/`before_pull_request` persist as trigger positions
(`after_push` ≡ `push:ok`). Depends on decisions 0027, 0028.

## Status

Accepted; `SPEC.md` application not started. Dependencies 0027 and 0028 are Accepted. The
re-evaluations are recorded: decision 0017's `Background.md` notes its generalization (it stays
Accepted); decision 0026 moves to `Superseded` (the new state added by decision 0033) with an
append-only `Background.md` note naming 0030 as its successor. `SPEC.md` application is deferred and
batched with the companion `vcsx` spec (0028) and decisions 0031–0032, which share this machine's
triggers and actions.
