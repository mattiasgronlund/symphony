# Background — 0159 The multi-repository configuration schema

## Context

Decision 0148 repaired what the issue→repository mapping keys on and where it is evaluated, and
recorded what it deliberately did not fix: "**The mapping has no configuration key, and neither does
the repository list.**" It gave the reason for leaving it — "adding one as a side effect of a
routing-key repair would be a large surface introduced without its own reasoning" — and filed it "so
it can be filed and decided on its own". This is that decision. 0148 is cited for the boundary it
drew; the argument below is from what the missing schema does today.

Section 5.3's "Top-level operator-config keys" are `tracker`, `polling`, `workspace`, `vcs`, `agent`
and `codex`. Every one of them is a singleton. Six other places describe a configuration that has a
repository dimension:

- Section 5: the operator policy config holds "the managed repositories with their issue→repo
  routing (Section 8.7), and, per repository, a pointer to that repository's `repo.policy.toml`".
- Section 5.3's own annotation on the key: "`vcs` (per managed repository: …)" — an annotation on a
  singleton, with no container for it to be per-anything of.
- Section 6.1, pipeline step 1: "resolve each managed repository's `repo.policy.toml` pointer".
- Section 6.4: "The operator policy config MAY define multiple repositories, each with its own `vcs`
  and `agent` settings and a pointer to that repository's `repo.policy.toml`, plus an issue→repo
  mapping keyed on the normalized record's `project`, `team`, `labels`, `assignees` and `state`".
- Section 8.7: "The policy config enumerates the managed repositories, each with its own VCS
  configuration (Section 9.7) and agent selection (Section 10.9), and the trackers they draw work
  from."
- Section 10.9: "Each repository has a `default_agent` and `default_effort`."

Nothing says what the enumeration is called, what one entry holds, what identifies a repository, or
what happens to a key an entry does not carry. Decision 0116 wrote the shape of this exactly, one
key narrower: "The configuration is a flat key, and how it composes with the multi-repository
routing of Section 8.7 is simply not stated — which in practice means one, because a flat key has
one value."

## The failure paths

**1. A REQUIRED resolution step reads a field the schema never names.** Section 6.1 is the normative
resolution pipeline, and its first step is to "resolve each managed repository's `repo.policy.toml`
pointer". Section 5.6 states the same obligation from the other side. Section 6.4 carries the row —
"a `repo.policy.toml` pointer per managed repository (Section 5.6)" — and it is the only row in a
section of `` `key`: type, default `` rows that names no key. So the first step of the pipeline
reads a value two implementations must each invent a spelling for, and no operator policy config
moves between them.

That the row names no key is also why nothing catches it. `scripts/validate_spec_consistency.py`
check 3 reads dotted config tokens out of `SPEC.md` and warns where one is in no Section 6.4 entry;
a row with no token is not a token. Measured at `be0ee6a`: `python3
scripts/validate_spec_consistency.py` → `0 error(s), 0 warning(s)`. The check is working as designed
and the gap sits beneath it — the shape decision 0132 named, where each artifact is complete against
itself.

**2. A MUST whose value has nowhere to be written.** Section 15.3: "An operator MAY configure
`vcs.git_credential` and `vcs.forge_credential` per repository (Section 6.4); where a repository
configures none, the orchestrator-level value applies … An implementation MUST support the
per-repository configuration even though an operator need not use it — otherwise the recommendation
below is one a multi-tenant operator cannot satisfy on a conforming implementation." Section 6.4
states the rule at the key ("An implementation MUST support the per-repository form"), and Section
18.1 makes it a checklist row: "Outward credentials MAY be scoped per repository, an implementation
supports that configuration". Three surfaces require the capability and none says where the value
goes, so the MUST is one an implementation discharges by inventing a location and an auditor checks
against that implementation's own documentation rather than against `SPEC.md`. The rule is also, as
written, a *schema* rule — two levels with fallback at the leaf — stated for one field pair inside a
document that has no second level.

**3. `repo_key` is a path component nothing defines, and the obvious rule for it breaks the recovery
that reads it back.** Section 9.1 lays out
`<workspace.root>/<repo_key>/<sanitized_issue_identifier>` "when one instance manages multiple
repositories". Section 4.1.8 makes that path component load-bearing across a restart: the `running`
entry's `repository` member "does not change how the field recovers: where one instance manages
several repositories the workspace path carries `repo_key` (Section 9.1) and the value is read back
from it". So `repo_key` MUST be a safe single path component *and* MUST round-trip.

Section 4.2 defines `Workspace Key` over `issue.identifier` alone, and Section 9.5 Invariant 3 with
it. Applying that rule to the repository name fails the round-trip by construction: the invariant is
byte-sanitization, deliberately lossy — "the invariant is a safe directory name, not a reversible
one" — so `web/app` and `web_app` both become `web_app` and a restarted orchestrator reads back a
`repository` that is not the one the run was dispatched to. That value is what Section 8.7's
standing routing condition compares against on every issue-state refresh, so a wrong read-back stops
a healthy run under Section 8.5 Part B; it is also the repository half of the `(repository, issue)`
key, so it names another repository's object store. Not applying the rule leaves Invariant 2 — the
workspace path stays inside the workspace root — defeated by a name containing `..`. Either way the
constraint belongs to the schema, and there is no schema.

**4. Which level owns a key is stated for one field pair and left open for the rest.** `vcs` is
annotated "per managed repository" and Section 9.7 gives it fourteen fields, of which exactly two —
the credential pair — carry a two-level rule. `agent` is worse, because its namespace splits by
meaning rather than by level: Section 10.9 assigns `default_agent` and `default_effort` to the
repository, while `max_concurrent_agents` and `max_concurrent_agents_by_state` are what Section 8.3
computes over the whole instance ("`running_count` is the number of entries in the `running` map").
Nothing says the split exists, so a schema that lets a repository override its `agent` block key by
key admits a per-repository `max_concurrent_agents` — either a capability nobody specified or a key
that silently does nothing. `codex` has the same question and no answer: two repositories may select
different agents (Section 10.9) while the adapter block that configures one is a singleton.

**5. Two sections loop over a collection the schema makes a singleton.** Section 8.1's tick, step 3:
"Fetch candidate issues from each tracker (once per tracker)". Section 8.7: the enumeration carries
"the trackers they draw work from". Section 5.3.1 defines one `tracker` object with one `kind`, one
`endpoint`, one `api_key` and one `project_slug`, and Section 6.3's preflight says "the selected
tracker adapter", singular, in four of its checks. The deployment those two sentences describe — a
Linear instance and a Forgejo instance polled by one daemon — is one nothing can express.

This one is not only a spelling. Section 4.2 says an `Issue ID` is what to "use for tracker lookups
and internal map keys", with no tracker qualification, and Section 4.1.8 keys `running`, `claimed`
and `completed` by it. Two trackers can mint the same id, so a second tracker is an issue-identity
change before it is a schema change. That is why this decision keeps the tracker singular and says
so, rather than enumerating trackers as a side effect of enumerating repositories.

## What the gap costs, and what it does not

It does not break a daemon. Any invented enumeration runs a multi-repository instance correctly, and
`SPEC.md` already makes the operator config's "format and discovery path … `Implementation-defined`"
(Section 5), so nobody expects the file to be byte-portable.

What it breaks is the conformance surface, which is where this document spends its guarantees.
Sections 5.3 and 6.4 fix key spellings and per-key defaults for every operator setting;
`conformance/vocabulary.json` publishes the top-level ones as `config_namespaces` "so a spelling can
be generated or checked instead of transcribed"; Section 17.1's checks name `tracker.kind`,
`vcs.git_credential` and `vcs.local_vcs` by key. The one part an implementation must invent is the
container those keys sit in. The registry is therefore complete against itself and blind to the key
that holds the others, and Section 17.1's check that "Two repositories whose Ways of Working differ
run under one operator policy config" asserts a property of a document shape the specification does
not fix.

The corpus already records the hole rather than papering over it, which is the strongest evidence
that it is real. `conformance/vectors/issue-routing.json` states in its notes: "The mapping's
configuration schema is not fixed by SPEC.md and is deliberately not pinned here: the routing
mapping has no configuration key yet, and the repository-enumeration schema it belongs to is owed a
decision of its own (decision 0148)." And `conformance/vectors/config-defaults.json` describes its
input as "the flat typed-config view of Section 6.4's cheat sheet, abstracting over which of the
three artifacts owns each field" — a view with exactly one value per dotted path, which is the
single-repository reading. The moment a path exists at two levels, that vector's input is
under-determined unless the decision says which level a default is filled at.

## Prior art, measured

`symphony-rs` has already had to invent this schema, and it is worth reading what it chose and what
that cost. Measured at `3255c9c` (2026-08-26), pinned to this repository's `4d610da`
(`spec/PINNED.toml`):

- `crates/symphony-config/src/operator.rs` parses a top-level `repository` key: a `[[repository]]`
  array of tables, with a single `[repository]` table accepted as one entry. `Config` holds
  `repositories: Vec<Repository>` beside shared `tracker`, `polling`, `workspace`, `agent`, `codex`,
  `forge_budget` and `compute` blocks.
- `Repository` holds `name`, `policy` (the `repo.policy.toml` pointer), `vcs`, `agent`, `issues`
  (the routing mapping) and an `extensions` bag for unknown keys.
- `Config::flat_view` derives one repository's flat view as the shared blocks plus that repository's
  own `vcs`, `agent` and pointer, "with the repository's `agent` block overriding the shared one key
  by key" — so the model admits a per-repository `max_concurrent_agents`. Failure path 4 above,
  reached by building rather than by reading.
- What decided the shape was neither the specification nor the corpus, and the module says so
  outright: "`docs/traceability.md` `17.1:bd14b1b7` asks for two repositories whose Ways of Working
  differ under one operator policy config, and a flat model cannot hold it. … This is the first time
  in this repository that the ledger rather than the corpus picked a data structure."

The drift such an arrangement produces is already visible in it. `Repository::issues` justifies
being untyped by quoting Section 8.7: "an explicit, tracker-implementation-specific mapping". That
phrase is not in `SPEC.md` — `git log -S"tracker-implementation-specific" -- SPEC.md` shows it
introduced by `0262f11` (decision 0009) and removed by `1c32bd4` (decision 0148) — and it is absent
from the very revision that repository pins: `git show 4d610da:SPEC.md | grep -c
tracker-implementation-specific` → 0. A downstream container carrying a rationale the specification
has retracted, at a revision the downstream has already vendored, is what owning the container
downstream costs: upstream changed what the mapping keys on, and nothing could reach the field that
holds the mapping.

Prior art is evidence about the cost of the gap, not authority about how to close it. The shape
recommended below differs from it in two places, and says why in each.

## Options considered

### Option A — enumerate the managed repositories in the operator policy config (recommended)

A top-level `repository` key: a map from repository name to an entry holding that repository's
`repo.policy.toml` pointer, its `vcs` block, its agent selection, and its routing rules. A key an
entry does not carry falls back to the orchestrator-level value for the same key, resolved leaf by
leaf — which generalizes the one inheritance rule the document already states (Section 6.4's
credential pair) rather than leaving it a special case. The repository name is the identity Section
4.1.8's `repository`, Section 9.1's `repo_key`, `repository_backoff` and the `(repository, issue)`
key all already assume, and it is constrained to `[A-Za-z0-9._-]` at validation rather than
sanitized at use, so the Section 4.1.8 read-back is exact and Invariant 2 holds by construction.

Trade-offs: it is the largest surface of the three, it adds a level to a schema whose corpus vectors
are flat, and it fixes key names for an artifact whose encoding the specification deliberately does
not fix.

### Option B — no repository dimension: one instance per repository

Delete the enumeration question by deleting the enumeration. Each Symphony process manages one
repository, with today's flat schema; a multi-repository operator runs several processes.

The steelman is not weak. It removes the entire cross-level inheritance question — every key stays
single-valued, `repo_key` leaves Section 9.1, and Section 4.1.8's read-back clause becomes
unnecessary. It gives *stronger* credential isolation than Section 15.3's per-repository
configuration achieves: a process that holds one repository's credential cannot leak another's,
where one process holding several can, whatever the config says. And it matches how an operator
already isolates blast radius for every other daemon.

It loses on three counts. Shared polling is the point of Section 8.7 — "the tracker is polled once
per cycle and the returned issues are routed to repositories via the mapping, rather than polling
per repository" — and N processes against one tracker is N× the spend against a limit the tracker
meters per credential, which is the exact failure Section 8.11 and Section 15.3 are about. Section
8.3's `max_concurrent_agents` bounds agent sessions for the instance; N processes cannot compute a
bound none of them can see, so the host's real concurrency becomes N × the configured limit. And it
is a retraction rather than a repair: Sections 8.7, 17.4's four routing rows, 18.1's routing rows,
decision 0009, decision 0148 and decision 0155's standing routing condition all go, and Section
17.1's "Two repositories … under one operator policy config" with them.

### Option C — declare the config's *structure* `Implementation-defined`, and state the semantics

Say only what must be true — that per-repository values for `vcs`, agent selection, the policy
pointer and the routing rules exist, and that an unset one takes the orchestrator-level value — and
leave the shape to the implementation, alongside the format and discovery path Section 5 already
leaves it.

The steelman: the operator policy config is the one artifact that crosses no trust boundary. It is
operator-owned, never read from a repository, never authored by an agent, and no conformance vector
reads it — `config-defaults.json` says in its own words that it abstracts over which artifact owns a
field. A specification that fixes key spellings for a file whose encoding it does not fix is fixing
half a contract already, and this option makes that consistent rather than pretending otherwise. It
is also the smallest change: one paragraph and one Conformance Statement row.

It loses because the half-contract is not an accident. The leaf keys are fixed, and the corpus
asserts defaults on dotted paths; once the same path can exist at two levels, "the default for
`agent.default_effort`" stops naming one thing, and `config-defaults.json` becomes a vector whose
input shape depends on the implementation reading it. Under Option C the `config_namespaces`
registry can publish `tracker`, `polling` and `vcs` but not the key that contains `vcs`, so a
generated check keeps the blindness that produced failure path 1. And it makes the Section 15.3 MUST
permanently unauditable across implementations: an operator config would be re-authored per
implementation, for a document Section 17.1 tests as a single artifact. Structure and encoding are
different questions, and only encoding is genuinely the implementation's.

## Decision and reasoning

Option A, with four sub-decisions the schema forces and which are decided here rather than left to
be discovered.

### The enumeration is a map keyed by the repository name

The steelman for a list of entries each carrying a `name` field is real, and it is what
`symphony-rs` chose: TOML's `[[repository]]` array of tables is what an operator reaches for, and it
keeps each repository's block visually parallel to the orchestrator-level blocks.

It loses because the name is not a field of the value; it is the identity three other sections
already key by. Section 4.1.8's `repository` member, Section 9.1's `repo_key`,
`repository_backoff`'s map key and the `(repository, issue)` key all hold it. A list makes that
identity an optional field inside the value, which admits an entry with a duplicate name, an empty
name, or no name at all — three conditions the specification would then have to refuse in prose that
a map makes unstateable. Ordering, the list's other advantage, carries no meaning here: Section 8.7
refuses an issue that two rules claim rather than taking the first match, precisely so that no
evaluation order is load-bearing. The cost is stated rather than hidden: this diverges from the one
build that has implemented it.

### The routing rules live inside the repository's entry

Section 6.4 currently describes the mapping as a sibling of the repository definitions ("plus an
issue→repo mapping"). Putting each repository's rules inside its own entry removes a whole class of
misconfiguration structurally — a rule cannot name a repository that does not exist — and makes
Section 8.7's "Two rules naming the same repository are not an ambiguity: what must be unique is the
repository, not the rule that reached it" true by construction rather than by a check. The argument
for a single top-level table is that an operator reads routing as one decision table; it loses to
the same observation as above, that Section 8.7 gives the table no order and no first match, so what
is left is a per-repository predicate written next to the repository it selects.

A repository with no rules matches every issue. That keeps the single-repository deployment
configuration-free, which is what Section 8.7's own "MAY manage multiple repositories" makes the
default, and it makes the two-repository misconfiguration loud in the direction Section 8.7 already
chose: both match, so no issue routes and the condition is reported, rather than issues silently
going to whichever repository was written first. The alternative reading — absent means matches
nothing — fails silently, which is what a dispatch that grants commit and pull-request authority
must not do.

### The repository level carries selection, not scheduling

At the repository level: the `repo.policy.toml` pointer, the whole `vcs` block, and the agent
*selection* fields of Section 10.9 (`default_agent`, `default_effort`, `agent_by_label`). At the
orchestrator level only: `tracker`, `polling`, `workspace`, the adapter blocks (`codex` and any
sibling), and the scheduling fields of `agent` — `max_concurrent_agents`,
`max_concurrent_agents_by_state`, `max_turns`, `max_retry_backoff_ms`. The line is not arbitrary:
Section 8.3 computes the concurrency limits over the instance's `running` map and Section 8.4's
backoff is per issue, so a per-repository value for any of them would be a new capability, and this
decision places existing fields rather than inventing behavior. Extension namespaces (`budget`,
`quota`, `forge_budget`, `compute`, `observability`) keep their own scoping, which each extension
already owns.

An unset repository-level key takes the orchestrator-level value for the same key, resolved leaf by
leaf rather than block by block, so a repository that overrides `default_effort` does not lose the
`default_agent` the orchestrator level supplied. That is exactly the rule Section 6.4 states for
`vcs.git_credential` today, which is the reason to generalize it rather than to invent a second one.

### The workspace path is repository-qualified in both cases

Section 9.1 today has two forms, and which applies depends on whether "one instance manages multiple
repositories" — under an enumeration, on how many entries it holds. That makes adding a second
repository re-key every existing workspace of the first: `<root>/<issue>` becomes
`<root>/<repo_key>/<issue>`, every workspace Section 9.2 would have reused is orphaned, and every
issue re-provisions. The trigger is an edit to an unrelated part of the config, and the failure is
silent — orphaned trees cost disk and a re-provision, not correctness, which is why nothing would
report it.

With a named enumeration the single-repository deployment is one entry rather than a distinct mode,
so the path is `<workspace.root>/<repo_key>/<sanitized_issue_identifier>` in both cases. The cost is
that this changes a stated layout: a deployment upgrading moves its workspaces once, or lets them be
re-provisioned. That is the cheaper of the two one-time costs, and it is the one an operator can be
told about in advance rather than discovering after an unrelated edit.

## What this decision does not fix, and why it is separable

**The tracker stays singular.** Section 8.1's "each tracker (once per tracker)" and Section 8.7's
"and the trackers they draw work from" describe a plurality Section 5.3.1 cannot express, and this
decision makes the document say what it means instead of enumerating trackers. Nothing is lost that
was reachable: Section 8.7's shared-polling requirement is about several *repositories* drawing from
one tracker, which is the single-tracker case, so it becomes true rather than aspirational.

A second tracker in one instance is a larger decision and the schema is its smallest part. Section
4.2's `Issue ID` is unqualified and Section 4.1.8 keys `running`, `claimed` and `completed` by it,
so two trackers minting the same id collide in orchestrator state; Section 6.3's four singular
"selected tracker adapter" checks become per-tracker; Section 11.7's capability descriptor is
consulted per adapter; and Section 13.1's log context would need the tracker on every record. That
decision is owed on its own terms, and this one is usable before it lands.

## Reconsideration triggers

- **A deployment needing two trackers in one instance.** It arrives with the issue-identity work
  above, not as a schema edit; the recognizable form is a request to poll a Linear project and a
  Forgejo instance from one daemon.
- **A per-repository scheduling limit.** A deployment wanting one repository capped below the
  instance's `max_concurrent_agents`, or a longer `max_turns` for one repository's issues, reopens
  the selection/scheduling line drawn above — as a new capability with its own accounting rule in
  Section 8.3, not as a relocation.
- **A per-repository adapter block.** Two repositories selecting different agents is already
  expressible; two repositories needing different `codex.*` settings is not, and would reopen
  whether adapter blocks are orchestrator-level.
- **A repository name that cannot be spelled in `[A-Za-z0-9._-]`.** The constraint is what makes
  `repo_key` exact rather than sanitized; a deployment that needs a name outside it wants a display
  name beside the key, not a wider key.
- **An operator config that must be authored by something other than a person.** The map-versus-list
  choice was made for the reader; a generator writing these files would weigh it differently.

## A stale corpus finding, resolved on the way

`conformance/README.md` carries an open finding — "**`vcs` is not in Section 5.3's top-level key
list (open).**" — that no longer holds. Section 5.3 lists `vcs` today, annotated "(per managed
repository …)", which is the annotation this decision is about. The finding also cites
`vcs.api_key`, a key `SPEC.md` no longer has: `grep -n "vcs.api_key" SPEC.md` → no match, the string
surviving only in that finding (`conformance/README.md:439`); `git log -S"vcs.api_key" -- SPEC.md`
shows it last touched by `d2647a0`, which moved the code-host selection to the consumer (decisions
0091–0093), and Section 9.7 has carried `git_credential`/`forge_credential` since. This decision's
plan closes the finding rather than leaving it, because the registry entry it is about —
`config_namespaces`'s `vcs`, whose `spec_ref` is still "Section 6.4" for want of a Section 5.3
subsection — is one this decision has to touch anyway.

## What the plan review changed (2026-08-27)

Four findings, run before the first edit (`plan-review`; `scripts/check_plan_anchors.py --rev
be0ee6a`, 8 findings from 10 quoted spans on the first pass and 0 from 8 on the last). Two are worth
the record because they are consequences the plan kept without a producer, which is the class the
mechanical lenses cannot see.

**A consequence with no producer in the one topology that has no dispatch.** The plan makes the
workspace path repository-qualified in every case, so a `Repository Key` is needed wherever a
workspace path is computed — and it put the enumeration's REQUIRED-ness in Section 6.3, the
*dispatch* preflight. Section 3.4's `interactive-agent` topology claims `Broker Core Conformance`
with no polling daemon, so it never runs that preflight and never evaluates routing, while Section
17.2's workspace checks are Broker Core's. The key the path now always carries had no producer
there. Settled where the enumeration is defined rather than in the topology list: a deployment that
manages a repository configures at least one entry, and an entry MAY carry nothing but its key,
everything else inheriting. That answer also keeps the single-repository configuration to what it is
today — the flat `vcs` and `agent` blocks — plus the one line that names the repository, which is
the migration this decision would otherwise have imposed on every existing deployment for the sake
of the multi-repository one.

**The absence is asserted in two places, and the plan named one.** `conformance/vectors/issue-
routing.json` records that the mapping's configuration schema "is not fixed by SPEC.md and is
deliberately not pinned here"; `conformance/vectors/standing-conditions.json` reuses that file's
rules modelling "verbatim" — its own word — and carries the claim again, citing decision 0148 the
same way. A decision that closes the gap and updates one of them leaves the corpus asserting, in the
other, that the schema is still owed a decision. This is the same shape as decision 0154's finding,
where a vector derived from Section 4.1.1 was not re-derived when the record grew: what makes it
recur is that the corpus's cross-references live in prose notes, which no check reads.

The other two were smaller and are recorded for the count rather than the reasoning: the plan
quoted wording it proposed to *write* as though the corpus carried it, which the register keeps rare
by leaving proposed wording unquoted; and a cheat-sheet row written as `repository.<name>.vcs.*`
would not have covered the leaf Section 15.3 names, because `scripts/validate_spec_consistency.py`
check 3 tests a dotted token for occurrence in the Section 6.4 slice as a substring and a wildcard
matches nothing.

## What implementing it changed (2026-08-27)

**The two config layers had to be ordered, and the plan ordered them the wrong way.** The plan put
resolution against the orchestrator level *after* built-in defaults, on the reasoning that an
inherited value should be validated exactly as a written one — which is true, and is about coercion
and validation, not about defaulting. Defaulting first breaks the inheritance it precedes: an entry
that omits `agent.default_effort` would be filled with that field's `Implementation-defined` default
before resolution ran, and the filled value would then shadow the orchestrator-level `high` the
entry meant to inherit — silently, and in the direction that reads as a choice the entry made.
Section 6.1 now resolves entries first and defaults second, Section 5.3.7 says the same from the
other side, and `conformance/vectors/repository-inheritance.json` asserts absence rather than a
filled value for a key neither level carries, so the two layers are separable by test rather than
only by description. Section 17.1 carries a row for the order.

The shape is worth naming because it is not the plan's mistake alone: the specification had one
inheritance rule (Section 6.4's credential pair) and no pipeline position for it, so nothing in the
document said when it ran. Generalizing the rule is what made the position necessary, and the
position is the part a reader cannot derive from either level's own description.
