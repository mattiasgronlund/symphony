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

## Update — 2026-08-27: revised candidate scope

The candidate scope above is the June reading and is kept as recorded. As of the re-evaluation
(`Background.md`, update of 2026-08-27), the scope each remaining option would carry is:

- **Option B (clarifying note), restated.** The note is no longer only a note. Naming the sandbox
  launch as the per-session attach point repeats the defect unless the launch is configurable, so a
  conforming B ensures a `sandbox.*` configuration surface exists (at minimum a profile selector and a
  launch wrapper, `Implementation-defined`, no-op where absent) alongside the note at Section 9.6
  "Agent Sandbox and Execution Isolation" — which makes it a config-field change with cross-cutting
  sync to the cheat sheet (Section 6.4), the test matrix (Section 17), the checklist (Section 18), and
  a Conformance Statement row per `CONFORMANCE-STATEMENT-TEMPLATE.md`. It also repairs Section 17's
  "Agent launch wraps the session in the configured sandbox", which today asserts a configuration no
  section defines.
- **Option C (host-side seam), shrunk.** Reduced to a single permission stated against the executor
  (`Execution Process`, Section 3.1): whether a local executor MAY be its own launch context when the
  orchestrator↔executor seam is in-process. No new abstraction, no launch-wrapper indirection, no
  per-host config block beyond what B introduces; the remote half is out of scope by Section 8.3's
  placement-opaque rule and Section 9.11's `compute.sharing`.
- **Option D (cooperative capping), new.** An OPTIONAL statement that a deployment MAY divide a CPU
  budget across concurrent runs by naming gate-control variables in the composed environment (Section
  9.6, *Constructed environment*), with the per-run share derived from or bounded by
  `agent.max_concurrent_agents` (Section 8.3). Carrier exists; what would be added is the policy plus
  its documentation obligation, with the same cross-cutting sync as B.

## Status

Not started — **Proposed (partly overtaken by 0035, 0117)**, finding recorded and re-evaluated
2026-08-27. No option selected; no `SPEC.md` change. The non-secret env-passthrough half of the
originating brief is no longer tracked as a separate future decision: its carrier landed with 0117 and
its policy is now this decision's Option D. Section 9.4's single execution contract for two hook
contexts (Sections 5.3.4, 15.4) is recorded as an adjacent gap and needs its own decision.
