# Plan — 0082 `[messages.squash] strategy` defaults to `merge`

## Scope

`VCSX-SPEC.md`: Sections 6.8 `[messages]`, 8.6 "Invocation Preconditions", 9.3 "Capability
Descriptors", 13.1 "Test Matrix". `conformance/vcsx/vocabulary.json` where it records the
`[messages]` surface.

No `VCSX-CONTRACT.md` change: the field-level `repo.policy.toml` schema is deferred to this document
(`VCSX-CONTRACT.md` Section 11), and no shared token is renamed.

## Steps

1. **`[messages.squash]` `strategy` (Section 6.8)** — ensure the section states the default in the
   schema's own field pattern: `strategy` selects the merge strategy, one of `squash`, `merge` or
   `rebase`, with `- Default: `merge``. Ensure the accompanying sentence gives the reason without
   citing Section 11 for it: `merge` is the one strategy under which the commits the engine wrote
   and gated survive into durable history as written, where `rebase` re-parents them and `squash`
   collapses them, which is the posture Sections 4.1 and 11 state for the work branch. *Done when*
   `strategy` carries `Default: merge` and the reason is stated without attributing a ranking to
   Section 11.

2. **`[messages.squash]` `strategy` (Section 6.8)** — ensure a token the section does not name is a
   configuration error (`malformed_policy`, Section 6.10) rather than silently defaulted, on
   Section 6.10's rule that a declared key whose value the schema does not admit is not covered by
   forward compatibility.
   *Done when* the sentence exists and cites Section 6.10.

3. **Invocation Preconditions (Section 8.6), the "What separates this registry" paragraph** — ensure
   the boundary is stated as: a configuration error is judged from the policy document together with
   what the engine holds independently of the invocation — the descriptors its configured backends
   advertise (Section 9.3) and its own defaults — while a precondition failure needs the
   invocation's arguments and the checkout the engine was pointed at. Ensure the paragraph states
   that a descriptor field a backend can answer only once it has opened the checkout is **not**
   something the engine holds independently of the invocation, so a policy requiring it keeps
   Section 9.3's first-use disposition. *Done when* the phrase "a property of `repo.policy.toml`
   alone, detectable before any argument or checkout is in hand" no longer appears,
   `capability_unsupported` is inside the definition, and the checkout-dependent carve-out is
   stated.

4. **Capability Descriptors (Section 9.3)** — ensure the section's split is unchanged in rule and
   sharpened in scope: an absent `[messages.squash] strategy` is determinable, because the engine
   holds its own default (Section 6.8), so the first-use half's producers are an optional
   capability, a descriptor field only the checkout answers, and an operation an engine defines
   beyond Section 4.1. *Done when* Section 9.3 names what remains on the first-use side.

## Cross-cutting sync

- **Test matrix (Section 13.1)**, under "Plugins" — ensure it states that a policy naming a merge
  strategy no configured forge declares is refused at validation with `capability_unsupported`,
  including where the strategy is the Section 6.8 default and the key is absent; and that a
  Conformance Statement claiming Section 9.3's first-use half **names the engine-added operation or
  optional capability it demonstrated it against**, because that half has no producer among the
  required policy keys.
- **Implementation checklist (Section 13.2)** — no change required; the plugin line already carries
  capability descriptors.
- **Conformance Statement (Section 13.3)** — no new row. The default is fixed rather than
  `Implementation-defined`, which is the point of choosing A over B.
- **`conformance/vcsx/vocabulary.json`** — ensure `message_formulation` (or the section recording
  the `[messages]` surface) carries the three strategy tokens and names `merge` as the default.

## Anchor changes

None. No code token or section title is renamed or removed; `strategy` gains a default.

## Status

Applied to `VCSX-SPEC.md`.
