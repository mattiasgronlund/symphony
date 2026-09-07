# Plan — 0171 A parameter that never named the turn

## Scope

`SPEC.md` only: Section 10.7 (Agent Runner Contract), Section 17.5 (Coding-Agent Adapters) and
Section 18.1.2 (Broker Core Conformance).

Section 10.6 (Agent Error Categories) is unchanged: its note already routes every early stop through
`cancel` and already places the resumable outcome on the turn, and it is the passage the others are
being brought into line with. Section 16.6 is unchanged: it already calls `release` with the absent
value, which is what this decision makes admissible rather than a defect.

## Steps

1. **`cancel`'s parameter is OPTIONAL.** Ensure Section 10.7's `cancel` bullet states that
   `continuation_ref` is OPTIONAL — absent where the turn in flight is the first, which has none
   (Section 10.7's own `run_turn` rule), and present otherwise.
   Done when the bullet marks the parameter OPTIONAL and names the first-turn case.

2. **The bullet says what the parameter is for, since it is not an identity.** Ensure the `cancel`
   bullet states that `continuation_ref` names the continuation the cancelled turn was started from
   rather than the turn itself, so an adapter that can drain cleanly holds the state a resumable
   outcome is produced from, and that a cancelled first turn is resumable only where the adapter can
   mint one.
   Done when the bullet distinguishes the parameter from a turn handle.

3. **The single-in-flight invariant is stated.** Ensure Section 10.7 states that an Agent Runner
   instance has at most one turn in flight at a time, which is what makes an absent
   `continuation_ref` unambiguous, and names Section 16.6's turn loop as the construction that
   already guarantees it.
   Done when Section 10.7 contains the invariant and cites Section 16.6.

4. **The resumable yield moves to the turn's own outcome.** Ensure Section 10.7's `cancel` bullet no
   longer reads as though `cancel` returns a resumable `continuation_ref`: the adapter interrupts
   and drains, and whether the cancelled turn is resumable or failed is reported through the
   outstanding `run_turn`'s own return, which is where Section 10.6 places it and the only call
   still live when the drain answers.
   Done when the `cancel` bullet attributes the outcome to `run_turn` and cites Section 10.6.

5. **`release`'s parameter is OPTIONAL on the same terms.** Ensure Section 10.7's `release` bullet
   states that `continuation_ref` is OPTIONAL, absent where the run ends before any turn returned
   one — the path Section 16.6 takes when the first turn's prompt fails — and that the adapter frees
   whatever it holds for the run in that case.
   Done when the `release` bullet marks the parameter OPTIONAL and names that path.

6. **Section 17.5's `cancel` bullet covers the first turn and the corrected reporting.** Ensure the
   Core check asserts that a cancel against an in-flight first turn is accepted with no
   `continuation_ref`, and that resumable-or-failed is reported through the turn's own return rather
   than by `cancel`.
   Done when the bullet names the first-turn case and the reporting call.

7. **Section 18.1.2's turn-centric item matches.** Ensure the Broker Core item describing the
   turn-centric contract no longer reads as though `cancel` reports whether the turn is resumable,
   and names the OPTIONAL parameter.
   Done when the item attributes the outcome to the turn.

## Cross-cutting sync

- **Section 6.4 (Configuration Cheat Sheet)** — unaffected. No configuration key changes.
- **Section 17** — step 6. **Section 18** — step 7, in Section 18.1.2.
- **Conformance Statement templates** — no row owed. No `Implementation-defined` value and no
  MUST-document obligation is added; whether an adapter can drain cleanly is already covered by the
  capability descriptor's resume mode (Section 10.9), which keeps its existing row.
- **`VCSX-SPEC.md`** — unaffected. The Agent Runner is not the engine's.
- **Conformance corpus** — unaffected. A cancel against an in-flight turn is not deterministic and
  host-independent, so it is outside the corpus's subset and stays a Section 17.5 check.

## Anchor changes

None. No code-token identifier is renamed or removed and no section is retitled. `cancel`,
`release`, `run_turn` and `continuation_ref` all keep their spellings; what changes is the
parameter's requirement level and which call reports the outcome.

## Status

Applied to `SPEC.md`: Section 10.7's `cancel` and `release` bullets and the new single-in-flight
paragraph, Section 17.5's `cancel` check, and Section 18.1.2's turn-centric item. All seven steps.
