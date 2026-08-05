# Background — 0042 Realize `vcsx` as a separate deliverable, engine-direct first

## Context

Decisions 0027 (three layers, the engine an OPTIONAL layer), 0028 (the engine an independent
deliverable; one policy-graph executor, two front-ends), 0039 (`VCSX-CONTRACT.md`) and 0040
(`VCSX-SPEC.md`) settle the *shape* of the VCS engine layer, are all Accepted, and the 0027–0032 batch
is applied to `SPEC.md`. None of them fix *realization and sequencing*: whether the engine is a
separate codebase from the start or a module extracted later, and which of the three topologies
(Section 3.4) is built first. The repository holds no implementation, so this is the first choice in
this domain that binds code rather than text.

Two facts constrain the space before any option is weighed:

- **A Symphony-native VCS/forge implementation is already foreclosed.** Section 9.7: the per-issue git
  and forge operations "are realized through the VCS engine contract… there are no parallel Symphony
  VCS/forge adapters for those operations." Choosing one re-opens 0028 as `Superseded` rather than
  adding an option to this decision.
- **`OPTIONAL` in Section 3.4 is topology-scoped, not build-scoped.** Section 18.1 lists a VCS engine
  whose plugin layer realizes push/back-merge and the forge operations, plus the action-policy machine,
  as REQUIRED for Core Conformance — so the engine is skippable only by not building the daemon. The
  tension resolves through per-topology conformance profiles (broker-core / daemon / engine-direct),
  each with its own Section 17/18 subset; that split is identified but not yet decided or written.
  Whichever realization is chosen, it is the follow-on.

## Options considered

Realization — how the engine contract is satisfied:

- **Option A — a separate deliverable from the start (chosen).** Its own codebase, pinned and invoked
  as an external tool with a `version_floor` (`VCSX-SPEC.md` Section 8.5), Symphony reaching it over
  the invocation contract. Trade-offs: matches 0028 literally; the engine is reusable outside Symphony
  immediately and the `engine-direct` and `interactive-agent` topologies exist as soon as it does; a
  process boundary makes the contract real by construction. Costs two codebases and version-skew
  management, and cross-repo iteration is expensive while both sides are still moving.
- **Option B — an in-process module behind the contract, extracted later.** `VCSX-SPEC.md` Section 8
  sanctions both encodings ("an in-process API or a subprocess with structured input and output. The
  contract is the same either way; only the encoding differs"). Trade-offs: an honest boundary at no
  cross-repo cost, both sides change in one commit, and extraction stays mechanical. But the boundary
  holds only as long as something enforces it — the mitigation is running one conformance suite through
  both encodings — and standalone reuse and `engine-direct` do not exist until extraction, leaving
  Section 3.4's "independent deliverable" aspirational meanwhile.
- **Option C — generalize an existing wrapper layer into the engine.** The surrounding repository
  already runs a proto-engine: status/commit/push operations, `ship`/`land` front-ends, a prefix→base
  branch policy, a caller-escalation exit, and git / jj / jj-secondary-workspace handling — close to a
  one-to-one map onto the engine's operation set, base resolution (`resolve = by_prefix`), escalation
  binding, and checkout modes. Trade-offs: starts from code proven against real repositories, but that
  code is shaped by one repository's Way of Working — the "enforce one WoW" pull 0027 rejected — and
  its runtime may not be the engine's. Not exclusive with A or B; available as a seed.
- **Option D — a minimal fixed-policy subset.** Only the operations the daemon calls, in a hardcoded
  sequence, with the action-policy machine deferred. Trade-offs: fastest to a running daemon, but it
  is the monolith 0027 rejected, and retrofitting the policy machine over hardcoded sequences is the
  expensive direction. Rejected other than as a deliberate throwaway.

Sequencing — which topology is built first:

- **`engine-direct` first (chosen).** The engine alone, operator-held credentials; 0028 calls this the
  engine's original home. Trade-offs: cheapest validation of `repo.policy.toml` and the policy machine,
  with no agent-secret boundary to get right yet — but the secret-isolation invariant stays unbuilt
  longest.
- **`interactive-agent` first.** Broker Core plus `ship`/`land` driving one agent session. Trade-offs:
  proves the single Core-Conformance guarantee earliest, but needs both the broker and a usable engine
  before anything runs at all.
- **`daemon` first.** Trade-offs: the largest surface, requires both of the above anyway, and defers
  every validation to the end.

## Decision and reasoning

Choose **Option A** on the realization axis and **`engine-direct` first** on the sequencing axis. The
two compose, and each is what makes the other affordable.

The standing objection to a separate deliverable is the cross-repo tax, and that tax is only paid while
both codebases are in motion. Sequencing `engine-direct` first means only one is, so the structure
0028 asks for costs nearly nothing at the point it is established — and establishing it later, after
Symphony has grown around an in-process call, is the expensive direction. Reuse outside Symphony is
0028's whole rationale; a process boundary secures the contract by construction, where Option B's
boundary holds only as long as a dual-encoding conformance suite keeps enforcing it.

`engine-direct` first also puts the artifact most likely to be wrong — the policy vocabulary and the
`repo.policy.toml` schema — in front of a real user, a human driving `ship`/`land` on real
repositories, before Symphony exists to freeze it. Option C is admissible as a seed for that work
provided the generalization runs toward the schema in `VCSX-SPEC.md` Section 6 rather than toward the
seed repository's own Way of Working.

Two things are carried from the first commit so the later layers are extensions rather than retrofits:

- execution-context labeling (`host_side` / `in_sandbox`, `VCSX-SPEC.md` Section 3.2), even while no
  consumer splits a policy across a sandbox boundary — that is the seam the Broker Core later splits
  on, and it is cheap to carry and expensive to introduce late;
- the `version_floor` pin (`[engine]`, `VCSX-SPEC.md` Sections 6.2 and 8.5), so the consumer-side
  pinning discipline exists before there is a consumer to break.

Accepted residual risk: the secret-isolation invariant — the one guarantee Symphony must enforce
(0027) — stays unbuilt and unproven the longest under this sequencing. That is the deliberate trade for
validating the policy machine first. Its design is already fixed by decisions 0003/0004, and it is not
what `engine-direct` usage would inform, since `engine-direct` has no sandboxed agent by definition.
The ordering is consistent with the enabler-not-enforcer stance: what gets built first is the part
repositories own.

We would reconsider if cross-repo iteration cost comes to dominate once Symphony development runs in
parallel with engine development — Option B is then available without re-deciding, because the
invocation contract is identical across encodings; if `engine-direct` usage shapes the engine around
the human case such that the host-side / in-sandbox split does not fit, which the day-one context
labeling is meant to prevent; or if no second consumer ever materializes, in which case the separate
deliverable is paying for reuse nobody takes.

The decision is **Accepted**. No `SPEC.md` change follows from it: Section 3.4 already states the
engine is "an independent deliverable, pinned as an external tool and released on its own cadence," and
Section 5.6 already defers the field-level `repo.policy.toml` schema (including `[engine]`
`version_floor`) to the engine contract.
