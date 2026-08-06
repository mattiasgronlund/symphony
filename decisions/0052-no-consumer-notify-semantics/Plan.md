# Plan — 0052 `notify` with no consumer that can effect it

## Scope

`VCSX-SPEC.md` Sections 5.2 "Actions" and 8.2 "Result Envelope". No `VCSX-CONTRACT.md` edit: its
Section 11 "Deferred to the Full Engine Spec" defers the result envelope to `VCSX-SPEC.md` Section 8,
and no shared token is added, renamed, or removed. No `SPEC.md` edit: Symphony's consumers can effect
all three actions, so the case this decision resolves does not arise there.

## Steps

1. **The `notify` action states its behavior with no consumer that can deliver it.** Ensure the
   `notify(channel, payload)` bullet in Section 5.2 "Actions" records that it is a benign no-op when
   the consumer cannot deliver it, and that the no-op is surfaced rather than dropped. Done when the
   bullet no longer leaves the case unstated.
2. **Section 5.2 names the consumer-that-cannot-effect-it case once, for all three actions.** Ensure
   the paragraph that begins "`create_task`, `set_state`, and `notify` are effected by the consumer" is
   followed by prose establishing that a consumer need not be able to effect every such action — citing
   Section 1.3's human-at-a-prompt consumer — and pointing at each action's disposition:
   `create_task` and `notify` benign no-ops, `set_state` a configuration error at validation
   (Section 6.10). Done when a reader can determine all three dispositions from Section 5.2 without
   searching.
3. **A surfaced no-op is required, on Section 5.4's principle.** Ensure that same prose requires an
   emitted intent that no consumer performed to be reported in the result envelope, and grounds the
   requirement in Section 5.4's existing rule that an unmatched operation outcome MUST NOT be silently
   dropped. Done when the requirement is stated with its rationale pointing at Section 5.4 rather than
   asserted bare.
4. **The envelope carries the unperformed intents.** Ensure Section 8.2 "Result Envelope" documents
   `outputs.unperformed_intents` as the array of consumer-effected intents the engine emitted and no
   consumer performed, each naming its `action` and that action's arguments, and that it is absent or
   empty when every intent was performed. Done when the `outputs` bullet names the key and its shape.
5. **The escalate invariant is preserved, not weakened.** Ensure the added prose does not contradict
   Section 5.5's "`escalate` is the single point at which their behavior legitimately differs" — the
   engine's behavior is identical across front-ends, and only the consumer's capability varies. Done
   when Section 5.5 still reads true after the edit.

## Out of scope

- **Making the three consumer-effected actions uniform.** Option B in `Background.md` (emit every
  intent in every front-end) and Option C (make them all configuration errors) both change settled
  behavior; this decision fills the one genuinely open case.
- **A new top-level envelope field.** The intents ride in the existing `outputs`, which Section 8.2
  already defines as entry-specific structured data.
- **`SPEC.md`.** Symphony's daemon and interactive-agent consumers effect all three actions, so no
  Symphony-side clause changes.

## Cross-cutting sync

`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (decision 0050) carries a `Consumer-Effected Actions` section
whose rows record each action's behavior with no consumer that can effect it. Ensure its `notify` row
reads as a surfaced benign no-op once this decision is applied, so the template and the specification
agree. Done when the row matches Section 5.2.

No change to the `conformance/vcsx/vocabulary.json` action group: `notify` is neither renamed nor
re-parented, and its `effected_by` stays `consumer`.

## Anchor changes

None. No token is renamed or removed. `outputs.unperformed_intents` is a new key under an existing
envelope field.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.2, 8.2).
