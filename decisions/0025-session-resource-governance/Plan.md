# Plan — 0025 Session resource governance and the host-side launch seam

## Scope

This decision records a finding (see `Background.md`); it selects **no option**, so no `SPEC.md`
change is planned under it. If an option is later Accepted, its implementation plan is written then —
either by extending this plan or in a superseding decision. The candidate scope per option is mapped
below so a future executor has a starting point, not as a committed plan.

## Steps

No implementation steps — no option is selected. Candidate scope per option, for reference only:

- **Option A (spec silent).** No `SPEC.md` change.
- **Option B (clarifying note).** One OPTIONAL `Note:` / `Design note:` attached to Section 9.6 "Agent
  Sandbox and Execution Isolation": the sandbox launch is the per-session resource-governance attach
  point for the agent subtree (work-conserving CPU weight under a shared parent, `Implementation-
  defined`, no-op where cgroup-v2 / delegation is absent, no new sandbox privilege per Section 15.3),
  and host-side VCS operations (Sections 9.7–9.9) and policy-config hooks (Section 9.4) are governed at
  the service/orchestrator level, not per session. No config field, no core requirement change.
- **Option C (host-side execution-wrapper seam).** A new OPTIONAL section plus a per-host config block
  (enable flag, parent slice, per-session weight, optional collective reserve) and a launch-wrapper
  indirection so host-side per-session work joins the session's resource domain; cross-cutting sync to
  Sections 6.4 / 17 / 18; anchor additions recorded in that decision.

## Cross-cutting sync

None under this decision (no option applied). The sync each option would require is noted in the
per-option scope above.

## Anchor changes

None.

## Status

Not started — **Proposed**, finding recorded only. No option selected; no `SPEC.md` change. The
non-secret env-passthrough half of the originating brief is tracked as a separate future decision.
