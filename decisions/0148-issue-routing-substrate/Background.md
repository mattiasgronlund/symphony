# Background — 0148 Routing keys and the record they route over

## Context

Issue #113, the sibling of #100 rather than a restatement of it: that one is about one dispatch
bullet's computability, this is about whether a whole section's mechanism has a substrate.

Section 8.7 routes "each polled issue" to exactly one repository through "an explicit,
tracker-implementation-specific mapping in the policy config", and names the keys by example:

> - Routing uses an explicit, tracker-implementation-specific mapping in the policy config. For
>   example, the `linear` adapter maps by project, team, label, or assignee; the `forgejo` adapter
>   maps by repository and issue tags/state. Routing MUST NOT depend on untrusted free-form issue
>   content beyond what the mapping names.

Section 4.1.1 declares its record to be the only issue anything downstream of the adapter ever sees
— "Every tracker adapter normalizes its own payload into this shape, so this is the only issue the
orchestrator, the prompt renderer and the observability output ever see" — and it carries `id`,
`identifier`, `title`, `description`, `priority`, `state`, `branch_name`, `url`, `labels`,
`blocked_by`, `created_at`, `updated_at` and `metadata`.

Of Section 8.7's example keys: `label` is `labels` and `state` is `state`; `assignee` is `assignees`
once decision 0140 lands, and this decision assumes it. **`project`, `team`, and the `forgejo`
adapter's `repository` are in no field at all.** So a multi-repository deployment drawing from one
shared tracker — the deployment Section 8.7 exists for — cannot express the mapping Section 8.7
gives as its own example, and nothing says whether routing is supposed to happen before
normalization or after it.

`metadata` is available and is what Section 8.7's own last sentence rules out: an opaque
adapter-owned key/value map *is* "untrusted free-form issue content", the carve "beyond what the
mapping names" reads as naming a **field** rather than licensing a metadata key, and Section 4.1.1
says in its own words that "the orchestrator core does not interpret it".

## Why this is not a documentation nit

**The two readings put the mapping in different components, and only one of them is a policy-config
mapping.** If routing happens *after* normalization, the mapping is the orchestrator's, it is a pure
function of the policy config and the Section 4.1.1 record, and `project`/`team` are not available
to it — Section 8.7's own example is unimplementable. If routing happens *before* normalization, the
adapter holds the mapping and applies it to its own raw payload, where the keys exist — but then the
mapping is not a thing the orchestrator can be handed, "tracker-implementation-specific" becomes
"tracker-implementation-*private*", and each adapter re-implements a policy-config surface Section
5.3 does not define.

**Section 17.4 asserts the property from the orchestrator's side.** Two checks are written as things
a conforming implementation demonstrates over the mapping:

> - One instance can manage multiple repositories; each issue routes to exactly one repository via
>   the policy mapping
> - A tracker shared by several repositories is polled once per cycle and its issues are routed

A conformance claim against a mechanism whose substrate is undefined is a claim about whichever of
the two readings the implementer picked.

**And it decides where a routing defect is caught.** Section 8.7 says routing yields exactly one
repository and gives no rule for a mapping under which two rules claim one issue. Under the
after-normalization reading that is one place, checkable as a pure function of the record; under the
before-normalization reading it is once per adapter, and the answers can differ per adapter.

**The `linear` example's first key is unreachable twice over, which is worth noticing.** Section
5.3.1 carries a single `project_slug`, REQUIRED for dispatch when `tracker.kind == "linear"`, and
Section 11.1 defines `fetch_candidate_issues()` as returning "all matching issues in the configured
active states for a configured project". So under the configuration the document actually specifies,
every polled Linear issue belongs to the same project and routing by project selects everything or
nothing. The absent field is one half of the gap; the absent multi-project polling is the other, and
it is the one that says the routing section and the configuration section were written against
different pictures.

## Decision

**Routing happens after normalization.** The mapping is the orchestrator's: a pure function of the
policy config and the Section 4.1.1 record, evaluated once per polled issue, in one place.

**Section 4.1.1 gains `project` and `team`** — string or null, OPTIONAL and tracker-dependent, in
the shape `branch_name` and `blocked_by` already use, normalized with `Lowercase Normalization` as
`labels` are. An adapter whose tracker has no such model leaves them null. `project` is the
tracker's container the issue belongs to; for the `forgejo` adapter that is the issue's owning
repository, which is what Section 8.7's `forgejo` example calls "repository", and naming it once
rather than twice is what keeps the routing keys a fixed set rather than a per-adapter vocabulary.

**A mapping naming a field the adapter does not populate matches no issue rather than every issue,
and it is caught before it matches nothing silently.** Section 11.7's descriptor declares whether
the adapter populates `project` and `team`, and a mapping keyed on one an adapter does not populate
is a Section 6.3 dispatch-preflight configuration error. That is the shape Section 11.7 and Section
6.3 already carry twice — for `tracker.api_key` under a `secret`-mode adapter, and for a non-empty
`tracker.transitions` against an adapter that does not declare `set_state` — and it is the shape
decision 0140 chose for `tracker.assignee`. Without it the failure is an operator's deployment
routing nothing and reporting nothing.

**Section 8.7's routing bullet is restated over the record's fields** rather than over per-tracker
key names, so the mapping's key space is `project`, `team`, `labels`, `assignees` and `state` — the
normalized fields — and the per-adapter examples become statements about which of those an adapter
populates. The prohibition on routing by untrusted free-form content survives unchanged and gains a
referent: the mapping names fields of the record, and `metadata` is not one of them.

**An issue matched by more than one repository rule is not dispatched**, and the ambiguity is
reported as a configuration error against that issue. It is stated over the issue rather than over
the configuration because two rules can be disjoint across every issue the tracker holds today and
overlap on the one filed tomorrow, so it is not a validation a preflight can complete. Refusing
rather than picking is the whole of the argument: a dispatch sends an agent with commit and
pull-request authority into a repository, and picking the first matching rule sends it into a
codebase the operator did not point it at. A skipped issue is visible and recoverable; a misrouted
one is a pull request in the wrong repository.

**A publication clause, mirroring decision 0140's.** The identifier an adapter publishes in
`project` or `team` MUST distinguish the tracker's containers under `Lowercase Normalization`; an
adapter whose stable identifier does not — a case-significant opaque id — publishes the human-facing
key or slug instead, and documents which. This is not belt-and-braces: Section 4.2's normalization
is not a comparison an adapter opts into ("Every case-insensitive comparison in this specification
is defined over this operation"), so an adapter publishing a case-significant id gets it lowercased
by the core, two containers differing only in case become one, and the symptom is an issue routed to
the wrong repository rather than an error. 0140 recorded this as a review finding against its own
first draft; it is inherited here rather than re-derived, and it is stated over the **publication**
rather than over the comparison so Section 4.2's sentence stays true.

## What this decision does not fix, and why it is separable

**The mapping has no configuration key, and neither does the repository list.** Section 5.3's
top-level operator-config keys are `tracker`, `polling`, `workspace`, `vcs`, `agent`, `codex` — no
repository enumeration and no routing mapping — while Section 6.4 asserts both exist ("The operator
policy config MAY define multiple repositories, each with its own `vcs` and `agent` settings and a
pointer to that repository's `repo.policy.toml`, plus a tracker-specific issue→repo mapping") and
Section 8.1's tick sequence says "Fetch candidate issues from each tracker (once per tracker)" where
Section 5.3.1 defines a single `tracker` object.

That is a real gap and it is **not** this decision's. It is a schema — a repository enumeration
interacting with per-repository `vcs` (Section 9.7 already documents `vcs` as "per managed
repository"), per-repository `agent` selection (Section 10.9), the per-repository `repo.policy.toml`
pointer, and per-repository credentials (Section 15.3) — and adding one as a side effect of a
routing-key repair would be a large surface introduced without its own reasoning. Recorded here so
the next reader does not mistake its absence for an oversight in this decision, and so it can be
filed and decided on its own.

**Nothing here depends on it.** This decision fixes what the mapping may key on and where it is
evaluated; the schema decides where the mapping is written. A single-repository deployment — one
rule, no keys, matching every issue — is fully expressible today and is what Section 8.7's own "MAY
manage multiple repositories" makes the default, so the substrate repair is usable before the schema
lands. That ordering is also the one the `symphony-rs` build is living: routing there is the
orchestrator's, the mapping names `labels` and normalized `state` — the two of Section 8.7's keys
the record carries — `metadata` is not read, a deployment needing project- or team-keyed routing
projects the attribute into a label in its adapter and routes on that as a recorded workaround, and
a mapping under which two rules claim one issue refuses rather than picking.

## Options considered

### Say routing precedes normalization, and the mapping is the adapter's

The issue's second option, and the steelman is not weak. All the keys exist in the raw payload, so
nothing has to be added to a Core record for attributes the orchestrator core never interprets.
Identity semantics stay where the knowledge is: only the adapter knows whether its tracker's project
handle is a slug, a name or an opaque id, and Section 4.2 fixes one normalization for every field
the core holds. It matches Section 11.1's existing precedent, where `project_slug` scopes the query
and appears in neither Section 8.2's conditions nor Section 4.1.1's record. And Section 8.7's own
"tracker-implementation-specific" reads naturally as "the adapter's".

It loses on four counts, and the fourth is the one decision 0140 already paid for:

1. **Section 17.4's two checks assert a property of the mapping from the orchestrator's side.** They
   would have to be reworded to stop asserting a property of a mapping the orchestrator never sees,
   which is a weakening of the conformance surface rather than a repair to it.
2. **The ambiguity rule becomes per-adapter.** "Exactly one repository" is then established once per
   adapter implementation, and two adapters in one deployment can answer differently.
3. **The "smaller edit" is the larger edit.** It needs a policy-config surface for a per-adapter
   mapping defined somewhere, or an explicit `Implementation-defined` declaration per adapter — and
   Section 5.3 tells a reader "Unknown keys SHOULD be ignored for forward compatibility", so an
   adapter reading its mapping from a key the schema does not define reads a key the schema says
   SHOULD be ignored, and an operator cannot distinguish a routing adapter from one that ignored
   their routing.
4. **A routing attribute can change while a run is in flight, and query scope cannot see it.** This
   is the argument decision 0140 reversed itself on for the sibling half of Section 8.2's bullet.
   Section 11.2 states the shape for labels — "Required label filtering happens **after
   normalization** so refresh can observe label removal and stop or release existing work" — and
   Section 16.3's `reconcile_running_issues` iterates `for issue in refreshed`, while Section 8.5
   Part B enumerates terminal / active / neither and has **no absent branch at all**. An issue moved
   to a different project mid-run is simply absent from a scoped enumeration, reaches none of the
   three branches, and its run continues against a repository the mapping no longer selects. Under
   after-normalization routing the value rides the record and the refresh sees it.

### Route on `metadata`

Zero new fields, and the adapter already owns the map. It loses on Section 8.7's own last sentence,
on Section 4.1.1's statement that the core does not interpret `metadata`, and on the failure mode: a
misspelled metadata key is indistinguishable from an issue that legitimately lacks it, so the
deployment routes nothing and reports nothing. The descriptor-plus-preflight shape in the decision
exists precisely to make that failure loud, and `metadata` has no schema for a preflight to check
against.

### Add a single opaque routing key rather than two named fields

`route_key` (string or null), which the adapter fills with whatever its tracker's container is —
project, team, repository. One field instead of two, and no per-tracker mapping of names.

It loses because it cannot express Section 8.7's own example: the `linear` adapter maps by project
**or** team, and a deployment may want one repository per team and a different rule for one project
inside it. Collapsing the two into one value forces the adapter to choose which one the deployment
gets, which is the operator's decision arriving at the wrong layer. It also makes the value's
meaning unstatable in the descriptor — "what does `route_key` hold" has a different answer per
adapter, which is the divergence the named fields avoid.

### Leave Section 8.7 as it stands

It costs nothing for a single-repository deployment, which reads the mapping as one rule matching
everything and is right to. It loses because Section 8.7 and Section 17.4 are `Daemon Conformance`:
a mechanism that cannot be evaluated from the specified configuration and the specified record is
not a requirement, and the divergence it admits is invisible in exactly the deployments where it
does no harm.

## What was checked

At `22b5194`, against the working tree:

- Section 4.1.1 lists thirteen fields; `project`, `team` and any repository-of-issue field are
  absent. Its framing sentence about being the only issue anything downstream sees is verbatim as
  quoted.
- Section 8.7's routing bullet is verbatim as quoted, and its four `linear` keys are `project`,
  `team`, `label`, `assignee`.
- Section 5.3.1 carries `project_slug` (string), REQUIRED for dispatch when `tracker.kind ==
  "linear"`; Section 11.1's `fetch_candidate_issues()` returns issues "for a configured project"
  (singular).
- Section 5.3's top-level operator-config keys are six — `tracker`, `polling`, `workspace`, `vcs`,
  `agent`, `codex` — with no repository enumeration and no routing mapping; Section 6.4 asserts
  both; Section 8.1's tick step 3 says "each tracker".
- Section 17.4's two routing rows are verbatim as quoted.
- Section 11.7's descriptor and Section 6.3's dispatch preflight already carry the
  declare-then-refuse shape twice (`tracker.api_key` under a `secret`-mode adapter; a non-empty
  `tracker.transitions` against an adapter that does not declare `set_state`).
- Section 4.2's `Lowercase Normalization` sentence — "Every case-insensitive comparison in this
  specification is defined over this operation" — is what makes the publication clause necessary.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## Reconsideration triggers

- **A tracker whose container model is neither a project nor a team.** Two named fields is a bet
  that the container axis is at most two deep. A tracker with three — organization, space, board —
  would either need a third field or would reopen the opaque-key option with a better case than it
  has today.
- **The routing-mapping schema landing with a shape that wants raw keys.** If the mapping's
  configuration turns out to be naturally per-adapter, the before-normalization reading gets a
  second hearing — but it still has to answer the mid-run reassignment case, which is the count it
  loses on independently of where the mapping is written.
- **A Core consumer of `project` or `team` beyond routing** — prompt rendering, workspace keying,
  observability grouping. The fields are added as routing substrate; a second consumer would make
  their normalization and their publication clause load-bearing in a place this decision did not
  weigh.
- **Multi-project polling arriving in `tracker`.** The `linear` example's `project` key becomes
  meaningful only then, and the configuration change is what would make routing-by-project a live
  path rather than a documented one.
