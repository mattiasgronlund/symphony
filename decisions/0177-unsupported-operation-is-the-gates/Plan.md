# Plan — 0177 `tracker_unsupported_operation` is the gate's, not a transport mapping

## Scope

`SPEC.md` Section 11.4 (Error Handling Contract) only. Section 11.7 (Adapter Capability Descriptor)
is unchanged: its gate sentence is what this decision cites.

## Steps

1. **The opening sentence is scoped to transport failures.** Ensure the sentence beginning "Error
   categories are transport-neutral" no longer says every category is mapped from a transport by
   the adapter. It should say that each adapter maps its transport's failures onto the categories
   that name them. Done when the opening sentence no longer covers `tracker_unsupported_operation`.

2. **A note names who reports `tracker_unsupported_operation`.** Ensure a `Note:` beside the one
   naming `unsupported_tracker_kind` says that `tracker_unsupported_operation` is reported by the
   gate Section 11.7 places before a write is invoked, not mapped by an adapter from its transport,
   and that a declared write which the backend refuses is reported under the transport category its
   failure fits, the descriptor being fixed for the run. Done when Section 11.4 contains that note.

## Cross-cutting sync

- Section 6.4: unaffected; no key changes.
- Section 17.3: unaffected; its check on `tracker_unsupported_operation` already holds.
- Section 18: unaffected.
- Conformance Statement templates: no row owed; no new obligation.
- `conformance/`: unaffected.

## Anchor changes

None.

## Status

Not started.
