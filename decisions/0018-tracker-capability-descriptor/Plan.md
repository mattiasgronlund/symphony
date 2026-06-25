# Plan — 0018 Tracker capability descriptor

## Scope

Adds a tracker adapter capability descriptor mirroring the agent adapter descriptor (Section 10.9). Relaxes
the all-operations mandate in Section 11.1 "REQUIRED Operations" so reads stay REQUIRED and writes are
capability-gated; adds a new Section 11.7 defining the descriptor; adds the `tracker_unsupported_operation`
error category (Section 11.4); adds a dispatch-preflight check (Section 6.3) tying `tracker.transitions`
(decision 0017) to the `set_state` capability. Cross-cuts the Section 17.3 test rows and Section 18
checklist. Out of scope: normalized-Issue field optionality and provider representation of states.

## Steps

1. In Section 11.1 "REQUIRED Operations", ensure the three read operations remain REQUIRED of every adapter
   and the write operations (`add_comment`, `set_state`, `link_pull_request`) are described as
   capability-gated per the adapter capability descriptor (Section 11.7), rather than universally
   mandated. Done when Section 11.1 no longer states that every adapter MUST support all six operations and
   points to Section 11.7 for writes.

2. Ensure a Section 11.7 "Adapter Capability Descriptor" exists, stating: each tracker adapter advertises a
   static capability descriptor (data, not a runtime call) declaring which writes it supports
   (`add_comment`, `set_state`, `link_pull_request`); the three reads are REQUIRED and not part of the
   descriptor; the descriptor MAY depend on resolved config and is fixed for the run; the orchestrator
   reads it before a write and MUST NOT invoke an undeclared write; an unsupported optional write is
   skipped and logged, not failed; an undeclared write invoked anyway yields `tracker_unsupported_operation`;
   an unsupported write MUST NOT be silently no-oped or replaced by a synthesized substitute; a non-empty
   `tracker.transitions` requires the `set_state` capability. Done when Section 11.7 defines the descriptor
   with those properties.

3. Ensure `tracker_unsupported_operation` is listed among the Section 11.4 RECOMMENDED error categories.
   Done when the category appears in the list.

4. Ensure Section 6.3 "Dispatch Preflight Validation" validation checks include: when `tracker.transitions`
   is non-empty, the selected tracker adapter MUST declare the `set_state` capability, else configuration
   error. Done when that check is present in the Section 6.3 list.

5. Cross-cutting sync of Section 17.3 and Section 18 (see below). Done when both mention the capability
   descriptor and the unsupported-write sentinel.

## Cross-cutting sync

- Section 17.3 "Issue Tracker Client": add a row asserting that reads are REQUIRED while writes are gated by
  a static capability descriptor; an unsupported write surfaces `tracker_unsupported_operation` and is
  never a silent no-op; non-empty `tracker.transitions` without `set_state` is a preflight error.
- Section 18 checklist: extend the tracker-adapter bullet so each adapter advertises a write-capability
  descriptor and unsupported writes surface a typed sentinel rather than a silent no-op.
- Section 6.4 cheat sheet: no change (the descriptor is adapter-declared, not a config field).

## Anchor changes

- New anchors: Section 11.7 "Adapter Capability Descriptor"; the error category
  `tracker_unsupported_operation`.
- Section 11.1 "REQUIRED Operations" keeps its title but narrows its mandate to the read operations; the
  write operations remain listed there but are gated by Section 11.7.

## Status

Applied to `SPEC.md`.
