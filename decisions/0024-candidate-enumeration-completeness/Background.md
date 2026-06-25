# Background — 0024 Candidate enumeration completeness

## Context

The neutral contract for `fetch_candidate_issues` (Section 11.1) says only "return issues in configured
active states for a configured project" — it states no completeness requirement. Pagination is specified
only inside the `tracker.kind == "linear"` block (Section 11.2: "Pagination REQUIRED for candidate issues",
"Page size default: 50"), so it reads as a Linear mechanism rather than a contract every adapter owes.

But the orchestrator depends on the complete candidate set: the poll tick sorts candidates by dispatch
priority client-side (Section 8.1 step 4) and dispatches while slots remain, with the sort order
`priority` → `created_at` → `identifier` (Section 8.2). A first-page-only result silently breaks priority
ordering — a high-priority issue on a later page is invisible to the scheduler.

The 22-fork sweep (`adapter-layer-fork-evidence` memory) caught exactly this: the Monday and Feishu Bitable
forks select a cursor / `has_more` but never follow it, capping at one page. Nothing in the *neutral*
contract forbids it today, so it sits in a gray area when it is really a correctness defect.

Reframe: pagination completeness is not an optional *capability* (like `add_comment`, which a backend can
legitimately lack) — it is a **correctness requirement** the orchestrator's priority sort depends on. The
paging *mechanism* (cursor, offset, `has_more`, page token, page size) is adapter-specific. So the fix is to
state the completeness requirement neutrally and make silent capping non-conformant, not to add a
"do you paginate?" capability flag.

## Options considered

- **Completeness as a neutral requirement (chosen).** State on `fetch_candidate_issues` that it MUST return
  the complete matching set, paginating internally; silent partial enumeration is non-conformant; a broken
  enumeration surfaces `tracker_pagination_error`; a hard-capped backend documents the cap. Keep the Linear
  page-size/cursor as Linear specifics.
- **A declared capability with a bounded mode.** The adapter declares `complete` vs `bounded` (a
  server-side priority-ordered top-N sufficient to fill dispatch slots); the orchestrator skips its
  client-side sort for `bounded`. A real *scale* optimization (it avoids enumerating thousands of issues
  every tick), but it adds a contract axis and assumes server-side priority ordering most backends lack.
  Not warranted by the evidence yet; noted as a possible future extension.
- **Defer.** Capture only.

## Decision and reasoning

`fetch_candidate_issues` (Section 11.1) MUST return the complete set of matching candidate issues. The
adapter paginates internally as its API requires; the paging mechanism and page size are adapter-specific. A
silently partial result is non-conformant, because the orchestrator's priority sort and dispatch (Section
8.2) assume the complete candidate set. A failed or incomplete enumeration surfaces `tracker_pagination_error`
(Section 11.4). Where a backend API hard-caps results with no way to page further, the cap is an
`Implementation-defined` limitation the adapter MUST document; silently dropping issues the adapter could
have fetched is not permitted. The Linear "Pagination REQUIRED / page size 50" lines stay as the Linear
adapter's realization of this neutral requirement.

Reasoning: this is a correctness fix — the client-side priority sort needs the full candidate set — and it
neutralizes another Linear-shaped requirement, continuing the theme of decisions 0019/0020/0023. It turns
the Monday/Bitable silent-cap from a gray area into a conformance bug, while leaving the paging mechanism
adapter-specific.

Problems to watch: complete enumeration every poll tick is costly for large backlogs (already the status quo
for the Linear adapter); the bounded/server-side-ordered mode (the deferred option) is the scale
optimization to revisit if that cost bites. The hard-cap edge is a genuine limitation that MUST be
documented and is distinct from silently dropping fetchable issues.
