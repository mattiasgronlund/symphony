# Background — 0043 Layer-keyed conformance profiles

## Context

Decision 0027 factored Symphony into three layers and made the Broker Core "independently
conformant — it can be satisfied for a single interactive agent session with no polling daemon"
(Section 3.4). Section 18.1 never followed: it requires the polling orchestrator, the tracker client,
complete candidate enumeration, multi-repo routing, the retry queue, and reconciliation for
conformance. `Core Conformance` therefore means *the `daemon` topology*, and the unit 0027 elevated to
a standalone deliverable has no profile it can claim. The `interactive-agent` and `engine-direct`
topologies are described in Section 3.4 and then unrepresented in Sections 17 and 18.

A second, narrower mismatch sits beside it: Section 3.4 describes the `daemon` topology as "the
autonomous daemon over the Broker Core, optionally driving the VCS Engine", while Section 18.1
requires a VCS engine outright.

The gap was identified in the 2026-07-05 design-review interview and left unresolved; decision 0042
named it as the follow-on that choosing `engine-direct` first makes immediate, since `engine-direct`
is precisely a topology today's conformance text cannot express.

## Options considered

Unit of conformance:

- **Option A — layer-keyed profiles with structural per-item scoping (chosen).** Conformance is
  defined per layer: `Broker Core Conformance` and `Daemon Conformance`, with engine conformance
  deferred to `VCSX-SPEC.md` Section 13 rather than restated. Topologies are declared compositions of
  those profiles. Section 18.1's flat list is regrouped under the layer it belongs to, and Section 17's
  subsections carry a profile scope, so each profile's subset is *derived from one list* rather than
  restated. Trade-offs: matches Section 3.4's own framing ("three deployment topologies compose the
  layers"); no list is duplicated, so no list can drift; a future topology costs one composition line.
  The regrouping touches every Section 18.1 bullet, though it adds none and removes none.
- **Option B — topology-keyed profiles.** One profile per topology (`broker-core`,
  `interactive-agent`, `daemon`), each with its own written-out Section 17/18 subset. Trade-offs: the
  most direct reading of "define conformance profiles", but the topologies nest — `interactive-agent`
  contains `broker-core`, `daemon` contains both — so each list restates the previous one and a single
  requirement change must land in three places. Rejected for the drift it builds in.
- **Option C — per-item tags only.** Keep one `Core Conformance` list and tag each bullet with its
  layer. Trade-offs: the smallest edit, but nothing states what an implementation must satisfy to
  *claim* a profile; the reader assembles it. Rejected as half the mechanism.
- **Option D — relax Section 3.4 instead.** Accept that `Core Conformance` means the daemon and
  withdraw the Broker Core's independent-conformance claim. Trade-offs: cheapest, and honest about
  what Section 18.1 says today — but it re-opens 0027's headline as partly `Superseded` and demotes
  `interactive-agent` and `engine-direct` to descriptive prose. Rejected: the layering is the design,
  not the conformance text's accident.

Engine coupling for the daemon:

- **Option B1 — conditional on remote operations (chosen).** The engine layer is REQUIRED of any
  deployment that performs a remote VCS or forge operation (push, back-merge, `create_pr`, merge).
  Trade-offs: preserves Section 3.4's "optionally driving the VCS Engine" without weakening anything
  real, since every non-degenerate deployment performs those operations; reads the same way
  `Extension Conformance` already does ("if … is implemented"). Costs one conditional.
- **Option B2 — unconditionally required for the daemon profile.** Trade-offs: simpler to state and
  matches Section 18.1 as written, but it would require editing "optionally driving the VCS Engine"
  out of Section 3.4 and forbids a deployment that only edits worktrees and writes tracker state — a
  restriction with no invariant behind it.

## Decision and reasoning

Choose **Option A** and **Option B1**.

Layer-keyed is the only unit that does not duplicate a list, and duplication is the failure mode that
matters here: a conformance checklist restated three times becomes three checklists. Section 3.4
already says topologies *compose layers*, so making the layer the unit of conformance states in
Sections 17 and 18 what Section 3.4 states in prose, rather than introducing a second taxonomy beside
it. The engine is deliberately not given a profile in `SPEC.md`: `VCSX-SPEC.md` Section 13 already
carries the engine's test matrix and implementation checklist, and restating it here would duplicate
across documents the way 0040 rejected for the schema. `SPEC.md` asserts only the *condition* under
which a conforming engine is required.

`Core Conformance` is kept as the umbrella term rather than retired, with the two layer profiles as
its components. Existing uses elsewhere in the document — "Core conformance does not require these
fields" in the OPTIONAL extensions, "the only Core-Conformance guarantee in the VCS/Forge/tracker
domain" in Section 3.4 — stay true under the split, so the edit adds structure without invalidating
prose it does not touch.

Two allocation calls fall out of the split and are made here rather than left to the editor:

- **The tracker adapter splits read/write**, along the line the document already draws. The read
  surface (`fetch_candidate_issues`, state refresh, terminal fetch; Section 11.1) is `Daemon
  Conformance` — it exists to find and reconcile work. The write surface (`set_state`, comments;
  Section 11.5 "Tracker Writes (Broker Boundary)") is `Broker Core Conformance`, because a Way of
  Working performs `set_state` in any topology that runs one, and those writes are broker-mediated by
  the 0003 boundary.
- **The Agent Runner and its adapters are `Broker Core Conformance`.** The executor composes the
  workspace manager, the agent runner, and the per-run broker (Section 3.1), and the
  `interactive-agent` topology drives an agent session with no daemon; the prompt *template* and its
  `WORKFLOW.md` loader are `Daemon Conformance`, since an interactive initiator supplies the prompt.

Section 3.4's `daemon` description survives verbatim under Option B1, and the conditional is stated
where the requirement lives (Section 18.1's engine group) rather than as a caveat in the architecture
prose.

We would reconsider if a fourth topology appears that is not a union of these layers — the
composition table would then be hiding a real distinction rather than expressing one; if the
`Broker Core` / `Daemon` line proves un-drawable for some requirement, forcing an item to be
duplicated in both groups (the first sign Option B's shape was right after all); or if `VCSX-SPEC.md`
Section 13 diverges enough from `SPEC.md`'s expectations that a deployment can hold a conforming
engine and still fail to interoperate, in which case `SPEC.md` grows an interoperation clause rather
than a restated checklist.

The decision is **Accepted**; the `SPEC.md` change is planned in `Plan.md` and not yet applied.
