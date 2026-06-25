# Plan — 0024 Candidate enumeration completeness

## Scope

States a neutral completeness requirement for `fetch_candidate_issues` (Sections 11.1/11.2): the adapter
MUST enumerate all matching candidate issues, paginating internally; silent partial enumeration is
non-conformant; a broken enumeration surfaces `tracker_pagination_error`; a hard-capped backend documents the
cap (`Implementation-defined`). The Linear page-size/cursor specifics stay. Generalizes the Section 17.3
pagination test row and syncs Section 18. Tracker read-side; relates to decision 0019.

## Steps

1. In Section 11.1, ensure the `fetch_candidate_issues` description states that it returns the complete
   matching set and that enumeration is complete (cross-referencing Section 11.2). Done when the op no longer
   reads as returning an unspecified subset.

2. In Section 11.2, ensure a neutral "Candidate enumeration" statement exists: `fetch_candidate_issues` MUST
   return the complete matching set; the adapter paginates internally (mechanism and page size
   adapter-specific); a silently partial result is non-conformant because the orchestrator's priority sort
   and dispatch (Section 8.2) assume the complete set; a failed or incomplete enumeration surfaces
   `tracker_pagination_error` (Section 11.4); a backend that hard-caps results documents the cap
   (`Implementation-defined`) and MUST NOT silently drop fetchable issues. Done when Section 11.2 carries the
   neutral requirement and the Linear lines remain as Linear specifics.

3. Cross-cutting sync of Section 17.3 and Section 18 (see below).

## Cross-cutting sync

- Section 17.3: change the "Pagination preserves order across multiple pages" row to assert that candidate
  enumeration is complete across pages and preserves order, that a silently partial result is non-conformant,
  and that a broken enumeration surfaces `tracker_pagination_error`.
- Section 18 checklist: add a bullet that `fetch_candidate_issues` enumerates the complete matching set
  (adapter paginates internally) and that a silent partial result is non-conformant.
- Section 6.4 cheat sheet: no change (no config field).

## Anchor changes

- New: a neutral "Candidate enumeration" completeness requirement in Section 11.2. The Linear "Pagination
  REQUIRED / page size 50" lines are unchanged (now framed as the Linear adapter's realization).

## Status

Applied to `SPEC.md`.
