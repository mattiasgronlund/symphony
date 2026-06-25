# Plan — 0023 Adapter-declared auth mode

## Scope

Adds an adapter-declared auth mode (`secret` | `none`) to the tracker capability descriptor (Section 11.7),
making `tracker.api_key`/`tracker.endpoint` and the dispatch-preflight key check conditional on it (Sections
5.3.1, 6.3), and clarifying the broker boundary for no-auth/local adapters (Section 11.5). Syncs Section 17.3
and Section 18. Tracker-scoped; relates to decisions 0003, 0005, and 0018.

## Steps

1. In Section 11.7, ensure the descriptor declares the adapter's auth mode: `secret` (a credential resolved
   through the secret provider, Section 15.3) or `none` (no credential; a host-side store). State that
   `tracker.api_key`/`tracker.endpoint` apply only to `secret`-mode, that preflight (Section 6.3) requires
   `tracker.api_key` only then, and that `linear`/`forgejo` are `secret`-mode while a `none`-mode adapter is
   admissible as an OPTIONAL extension. Done when Section 11.7 defines the auth mode.

2. In Section 5.3.1, ensure `api_key` is documented as used only by `secret`-mode adapters and `endpoint` as
   adapter-specific (`none`-mode/local adapters have none). Done when both fields state the conditionality.

3. In Section 6.3, ensure the `tracker.api_key` presence check applies only when the selected tracker adapter
   is `secret`-mode (Section 11.7). Done when the preflight check is conditional.

4. In Section 11.5, ensure a statement that the broker mediates tracker writes for scope and isolation even
   when the adapter has no credential (`none`-mode), and that a local adapter's store MUST be host-side
   (outside the bind-mounted workspace) so the agent cannot bypass the broker. Done when the boundary nuance
   is stated.

5. Cross-cutting sync of Section 17.3 and Section 18 (see below).

## Cross-cutting sync

- Section 17.3: add a row that a `none`-mode tracker adapter dispatches without `tracker.api_key`, while a
  `secret`-mode adapter requires it at preflight.
- Section 18 checklist: add a bullet that tracker adapters declare an auth mode (`secret` | `none`), that
  `api_key`/`endpoint` and the secret provider apply only to `secret`-mode, and that a `none`-mode local
  adapter keeps its store host-side.
- Section 6.4 cheat sheet: no new field; `tracker.api_key` is already listed (its conditionality is described
  in Sections 5.3.1/11.7).

## Anchor changes

- New anchor: the tracker auth mode (`secret` | `none`) declared in the Section 11.7 capability descriptor.
- `tracker.api_key` and `tracker.endpoint` gain `secret`-mode-conditional semantics; neither is renamed.

## Status

Applied to `SPEC.md`.
