# Plan — 0181 A REQUIRED item names the task tables only where the extension ships

## Scope

`SPEC.md` Section 18.1.4 (VCS Engine) and Section 18.2 (RECOMMENDED Extensions (Not REQUIRED for
Conformance)). Section 8.10 (Autonomous Task Management (OPTIONAL)) is unchanged.

## Steps

1. **Section 18.1.4's action-policy item states its condition.** Ensure the item beginning "The
   action-policy machine (Section 9.12): `(trigger) → (action)`" says that `tracker.transitions` is
   matched by Symphony against its own trigger vocabulary (Section 11.6), and that `[tasks]` and
   `[driver]` are matched the same way where the implementation ships the OPTIONAL autonomous task
   management extension (Section 8.10). Done when the item names that condition for `[tasks]` and
   `[driver]`.

2. **Section 18.2's extension entry carries the obligation.** Ensure the autonomous task management
   entry says that Symphony, not the executor, matches `[tasks]` and `[driver]` against its own
   trigger vocabulary. Done when the entry states it.

## Cross-cutting sync

- Section 6.4: unaffected.
- Section 17: unaffected; no check changes.
- Section 18: steps 1 and 2.
- Conformance Statement templates: no row owed.
- `conformance/`: unaffected.

## Anchor changes

None.

## Status

Not started.
