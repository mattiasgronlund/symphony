# Background — 0027 Minimal enabler and the three-layer architecture

## Context

`SPEC.md` models Symphony as one long-running service that *performs* the VCS, forge, and tracker
work (Sections 9.x, 11.x) with the credential broker (decisions 0003/0004) embedded inside it. Work
toward consuming an external VCS-workflow engine (working name `vcsx`, the subject of decision 0026
and 0028) surfaced two problems with that monolith:

- It risks **enforcing** one Way of Working (gate at boundaries, hygiene, base-merge, PR policy)
  rather than enabling many. An operator brief crystallized the requirement: enable *as much* WoW
  automation as possible while keeping the agent free of VCS/Forge secrets, and still allow a
  100%-custom WoW.
- It conflates three separable concerns — the credential boundary, the VCS engine, and the
  long-running automation — so the credential broker cannot be used on its own (for an interactive
  agent session), and the engine cannot be reused outside Symphony.

The single durable guarantee Symphony must make in this domain is the **secret-isolation
invariant**: the agent working in the repo never needs VCS or Forge credentials (the keystone of
decision 0003). Everything else is policy a repository should be free to choose.

## Options considered

- **Option A — Keep the monolith; require `vcsx` as the engine.** Trade-offs: simplest conceptually,
  but bakes a WoW into the service, makes `vcsx` a hard dependency, and leaves the broker un-factored
  so the interactive-agent and engine-only cases stay second-class.

- **Option B — Factor into three layers (chosen).**
  1. **Broker core** (≈ decisions 0003/0004): secret isolation, scope enforcement, the per-run
     socket, and credentialed-operation mediation. This is the *only* enforced invariant and is
     independently conformant — usable for an interactive agent session with no daemon.
  2. **`vcsx` engine**: VCS mechanics, the `ship`/`land` orchestrators, and the policy executor
     (decision 0028). Optional; one realization of the WoW.
  3. **Autonomous daemon**: polling, dispatch, bounded concurrency, multi-repo routing, plus task
     management (0031) and the autonomous driver. Layered on the broker core.

  Symphony **enables** WoW and **enforces** nothing beyond secret isolation. Three deployment
  topologies fall out with sharp conformance boundaries: daemon (autonomous), interactive-agent
  (broker core + `ship`/`land`), and engine-direct (`vcsx` alone, operator holds secrets).
  Trade-offs: a layered conformance model to document and test, but it matches the
  "as little as possible" mandate, makes the broker core reusable, and keeps the engine independent.

- **Option C — Invent a Symphony-native engine instead of `vcsx`.** Trade-offs: free to fit
  Symphony's idiom, but reinvents the engine, forfeits reuse, and loses the standalone/interactive
  cases. Rejected.

## Decision and reasoning

Choose **Option B**. The secret-isolation invariant is the whole of Core Conformance in this domain;
everything WoW-shaped becomes repo-owned configuration and configurable seams (decisions 0029–0032).
The broker core (0003/0004) is elevated to a standalone-conformant unit so "interactive agent with
secured secrets + full WoW automation" is a first-class topology, not a footnote, and the daemon is
a layer that consumes it. `vcsx` is one (optional) engine behind the seams, not a requirement.

This is the headline that decisions 0028 (`vcsx` deliverable + shared executor), 0029 (repo-owned WoW
config + trust sourcing), 0030 (the action-policy machine), 0031 (autonomous task management), and
0032 (message formulation) all hang off. It does not change decisions 0003/0004; it re-frames the
surrounding monolith around them.

We would reconsider if a second hard invariant proves necessary in Core Conformance (beyond secret
isolation + scope), or if the three-layer boundary proves leaky — e.g. if the broker core cannot in
practice be exercised without the daemon.

The decision is **Accepted**; the corresponding `SPEC.md` change is **not** made yet. Application is
deferred and batched with decisions 0028–0032, because 0027's planned spec text forward-references
that still-`Proposed` framing (see `Plan.md` Status). The design sketch behind it is
`tmp/vcsx-symphony-design.html`.
