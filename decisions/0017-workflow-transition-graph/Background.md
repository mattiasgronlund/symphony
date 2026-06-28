# Background — 0017 Workflow transition graph

## Context

Decision 0008 gave Symphony a policy-owned workflow state-machine and chose milestone signals as how
the agent drives lifecycle: the agent emits semantic signals (`ready-for-review`, `blocked`, `done`)
and a policy map (`tracker.milestones`, a flat `signal -> state_name` lookup) turns each into a tracker
transition. 0008 explicitly considered and rejected "outcome-driven only" in favour of this.

The 2026-06-25 tracker-focused sweep of ~22 retarget forks (recorded in 0008 `Background.md` and the
`adapter-layer-fork-evidence` memory) surfaced two problems with that shape:

- **The milestone-signal map is essentially unattested.** No fork wires agent-emitted milestone names
  through a `signal -> state` map. The dominant pattern is run-*outcome* → state, decided in
  orchestrator code (success → handoff, failure → `Human Review`, PR opened → `Merging`), with state
  *names* in config but the transition *graph* hardcoded. The one fork with a structured signal pipeline
  (JhihJian) keys transitions on a closed, operator-defined *outcome* vocabulary the agent emits, mapped
  through an explicit per-state-of-the-graph `transitions` table — not a flat lookup.
- **The spec over-claims.** Section 11.6 asserts a "workflow state-machine [that] names the allowed
  states and transitions and the conditions under which Symphony performs them (for example a milestone
  signal, or a run outcome such as a pull request being opened)", but the only concrete config artifact
  is the flat `tracker.milestones` map. Outcomes get prose; only signals get config. The run-outcome
  vocabulary already exists in the document (Section 7.2 run-attempt terminal reasons, Section 7.3
  transition triggers) but is never connected to tracker transitions.

So "milestone vs outcome" is a false opposition: the two are different *trigger sources* (agent-emitted
intent vs orchestrator-observed mechanics), and the real gap is that the state-machine is a lookup table,
not a graph, and only one of its two trigger sources is expressible in config.

## Options considered

- **Elevate run-outcomes to a peer mechanism.** Keep `tracker.milestones`; add a parallel
  `outcome -> state` map. Smallest change, closes the asymmetry, but leaves the state-machine as two flat
  lookup tables rather than an actual graph, and keeps two separate config surfaces.
- **Keep milestones as forward design; no spec change.** Defensible (a spec may lead the ecosystem, and
  0008 chose milestones on principle), but leaves Section 11.6's outcome side unimplementable from config
  and the over-claim standing.
- **Reframe Section 11.6 as an explicit transition graph (chosen).** Replace the flat map with a directed
  graph: edges `{from, on, to}` keyed on a single, closed trigger vocabulary that unifies agent-emitted
  milestone signals and orchestrator-observed run outcomes. This is the substance of JhihJian's model and
  the only option that makes Section 11.6 honest about being a state-machine.

Within the chosen option, two realization sub-choices were pinned with the user:

- **Graph nodes = existing tracker workflow-state names**, not a new neutral `stage` noun. JhihJian
  introduces a `stage` namespace plus a `stage -> state` map; the spec already has neutral state names
  (`active_states`/`terminal_states`, Section 5.3.1) as nodes and already makes the adapter map a state
  name to its provider representation (0008). Reusing them avoids a fifth lifecycle noun (`run`/`turn`/
  `step` per 0014, plus the Section 7.1 claim states and the tracker states) and keeps the ripple small.
- **Trigger vocabulary is closed and spec-defined.** Run-outcome triggers are drawn from Section 7.2/7.3
  (the orchestrator stays the source of truth); milestone-signal triggers are the defined agent set
  (`ready-for-review`, `blocked`, `done`). Operators wire triggers to transitions; they do not mint new
  trigger names.

## Decision and reasoning

Section 11.6's workflow state-machine becomes an explicit directed graph over tracker workflow-state
names. Each transition is `{from, on, to}`; in state `from`, when trigger `on` fires, Symphony performs
`set_state(issue_id, to)` (Section 11.1). Triggers are one closed vocabulary with two origins:

- **Milestone signals** — emitted by the agent through the broker CLI to express intent
  (`ready-for-review`, `blocked`, `done`).
- **Run outcomes** — observed by the orchestrator, not the agent: `dispatched`, `pull_request_opened`,
  `run_succeeded`, `run_failed`, `retries_exhausted`, each tied to a Section 7.2 terminal reason or
  Section 7.3 trigger.

The graph lives in operator policy config as `tracker.transitions` (a list of `{from, on, to}`), replacing
`tracker.milestones`. It sits under `tracker` (next to `active_states`/`terminal_states`), not under a new
top-level `workflow` key, to avoid colliding with the repo-owned `WORKFLOW.md` / "Workflow Definition"
(Section 4.1.2). A trigger that fires with no matching `from`-state transition performs no transition. The
graph MUST be deterministic: at most one transition per `(from, on)`; duplicates are a config error.

The adapter still maps each workflow-state name to its provider representation (GitLab scoped label,
Projects v2 option-id, Jira transition); Section 11.6 defines the graph over neutral names only and does
not specify representation. How a tracker declares which states/writes it can represent is deferred to a
separate tracker-capability decision.

This preserves 0008's load-bearing principle — the agent expresses intent, operators own the resulting
transitions — while making the run-outcome trigger source first-class and turning the state-machine into
an actual graph.

Problems to watch: the run-outcome trigger set is coupled to Sections 7.2/7.3 and MUST be kept in sync if
those change; `tracker.transitions` replaces `tracker.milestones`, an anchor change other plans may
reference; and Section 11.6 must stay silent on provider representation so it does not pre-empt the
capability decision.

## Re-evaluation — generalized by 0030 (2026-06-28)

This decision **remains Accepted**; its transition-graph semantics are unchanged. Decision 0030 (the
action-policy machine) *generalizes* it rather than replacing it: the `(from, on, to)` transition
becomes one binding of the machine's `set_state` action, and the trigger kinds defined here
(milestone signals, run outcomes) become two of the machine's trigger kinds. The two load-bearing
rules of this decision are carried into 0030 intact — "a trigger with no matching transition performs
no transition" becomes 0030's **unmatched-signal-is-a-no-op** rule, and the determinism requirement
(at most one transition per `(from, on)`) becomes 0030's most-specific-wins matching. So 0017 is a
specialization of 0030, not superseded by it; this note records the relationship so a future reader
finds the generalization from here.

## Re-evaluation — task-state triggers added by 0031 (2026-06-28)

This decision **remains Accepted**. Decision 0031 (autonomous task management) adds a further trigger
kind to the graph for the daemon case: **task-state events** (`tasks:all_closed`, `task:#needs_help`)
join the milestone signals and run outcomes already defined here. Within 0030's action-policy machine
these are simply more triggers; the milestone vocabulary this decision keyed on is enriched — an
agent-asserted `done` becomes the computed `tasks:all_closed` — without changing the transition-graph
semantics. See 0031.
