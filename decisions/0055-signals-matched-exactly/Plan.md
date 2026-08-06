# Plan — 0055 Signals are matched exactly; the `#class` fallback is result-only

## Scope

`VCSX-SPEC.md` Sections 5.1 "Triggers", 5.3 "Matching Algorithm and the `#class` Fallback", and 12.1
"Match a Trigger". The vocabulary registry's `trigger_kinds` group and the `match_edge` vectors follow.
No `VCSX-CONTRACT.md` edit: its Section 5.3 describes matching at surface level and its Section 11
defers the algorithm here, and no shared token is added, renamed, or removed — `task:#needs_help` keeps
its spelling.

## Steps

1. **Section 5.1 says what a signal's matching discipline is, and what the `#` in `task:#needs_help`
   means.** Ensure the Signals bullet states that a signal is matched exactly and has no class form,
   and that the `#` names a condition across tasks — raised once when any task needs human help —
   rather than a proto class. Done when the token can no longer be read as a fallback rung.
2. **Section 5.3's signal bullet drops the class rung.** Ensure the ladder for a signal is the exact
   key then the unmatched-signal default, with the reason stated: a signal carries no proto class
   because it is a consumer-raised condition rather than an operation result. Done when no
   unresolvable `class_form` step remains.
3. **Section 5.3 scopes the `#class` fallback to typed results.** Ensure the closing paragraph says the
   fallback applies to typed operation results alone, those being the only triggers with a proto class.
   Done when the scope is stated rather than inferred from the bullets.
4. **Section 12.1's `ladder()` matches.** Ensure the signal branch returns the exact key alone. Done
   when the pseudocode calls no undefined `class_form`.
5. **The registry agrees.** Ensure `conformance/vcsx/vocabulary.json`'s `trigger_kinds` signal entry
   records `class_fallback: false`. Done when the registry and Section 5.3 state the same thing.
6. **The corpus covers both halves.** Ensure `match-edge.json` asserts that `task:#needs_help` is
   matched exactly as an ordinary token, and that a `#class` edge does not catch a signal. Done when
   both vectors exist and pass the registry cross-check.
7. **The README finding is marked resolved.** Ensure `conformance/vcsx/README.md`'s "Surfaced
   findings" records the resolution and names this decision. Done when the entry reads as resolved.

## Out of scope

- **Renaming `task:#needs_help`.** The spelling is a shared token under Section 14; renaming it would
  be a contract change requiring `VCSX-CONTRACT.md` in step, for no benefit once the `#` is explained.
- **Defining a concrete per-task event vocabulary.** Section 7.3 assigns the task model to the driver;
  a consumer raises whatever tokens its policy binds.
- **The other two findings 0053 surfaced**, taken up as decisions 0054 and 0056.

## Cross-cutting sync

`conformance/vcsx/vocabulary.json` `trigger_kinds` (Step 5) and `conformance/vcsx/README.md` findings
(Step 7). No change to `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`: no new
`Implementation-defined` obligation, reason token, or `need` is introduced. No `SPEC.md` change:
Symphony references the task-state events by name and never relies on a signal class fallback.

## Anchor changes

None. No token is renamed or removed. The removal is of an unresolvable *mechanism* (the signal class
rung), not of any name — `task:#needs_help`, `tasks:all_closed`, and the agent milestone signals all
keep their spellings.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.1, 5.3, 12.1) and `conformance/vcsx/` (vocabulary, vectors,
README).
