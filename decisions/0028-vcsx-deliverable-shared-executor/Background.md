# Background — 0028 `vcsx` as an independent deliverable; one shared policy executor

## Context

The VCS mechanics and orchestration that Symphony needs are generic and reusable. They are being
extracted into an external engine (working name `vcsx`) that any repository consumes as a pinned
**mise tool** (the way the surrounding repository already consumes `archdoc`), and that works
**without** Symphony at all — the interactive/standalone case is the engine's original home.

Two constraints shape how Symphony depends on it:

- **Language-agnostic discipline.** `SPEC.md` is language-neutral ("Draft v1 (language-agnostic)") and
  must not name a runtime. So Symphony defers to the engine's **contract** (its protocol, the
  `ship`/`land` entry points, the policy executor), never its implementation — mirroring how the spec
  already defers to the Codex app-server protocol as a source of truth instead of duplicating it.
- **One Way of Working, honored identically.** A consistency hazard surfaced: if interactive
  `vcsx ship`/`land` ran one orchestration sequence and the daemon ran a *separate* policy graph, the
  WoW would be expressed twice and drift. The interactive and autonomous paths must be two
  **front-ends over one executor reading one repository policy**.

## Options considered

- **Option A — Symphony reimplements orchestration; `vcsx` supplies only primitives.** Trade-offs:
  keeps `vcsx` minimal, but produces two executors (the interactive `ship` sequence and the daemon
  policy graph) that inevitably diverge. This is the drift hazard above. Rejected.

- **Option B — The policy-graph executor lives in `vcsx`; two front-ends over it (chosen).**
  `ship`/`land` are entry points to the executor; the daemon **embeds the same executor** and adds
  only the autonomous driver (the initiator trigger and the `escalate` binding — decisions 0030/0031).
  Both read one `repo.policy.toml` (decision 0029), so they are provably consistent by construction.
  `vcsx` is an independent deliverable, pinned and released on its own; `SPEC.md` references only its
  contract. Trade-offs: `vcsx` is therefore **not** tiny (it owns the executor) — but Symphony's
  *marginal* code over it stays tiny (task management + autonomous bindings + poll/dispatch).

- **Option C — Require the `vcsx` binary by name in normative text.** Trade-offs: strongest coupling,
  but violates the language-agnostic discipline. Rejected — require the **contract**, not the binary;
  the binary is the canonical realization a conformant deployment ships.

## Decision and reasoning

Choose **Option B**: "one executor, two front-ends." The executor is part of the engine; interactive
`ship`/`land` and the daemon are front-ends that differ only in their *initiator* and their
`escalate` binding (decision 0030). This is what makes the three topologies (decision 0027) provably
equivalent rather than coincidentally similar.

`vcsx` is an independent deliverable consumed as a mise tool, released on its own cadence, and
`SPEC.md` defers to its contract the same way it defers to the Codex protocol. This refines decisions
0007 (VCS abstraction) and 0022 (forge adapter surface): the broker's commit/push/pr/merge are
realized **through the engine contract**, and forge/transport neutrality relocates into the engine's
plugin layer rather than living as parallel Symphony adapters.

We would reconsider if the executor proves un-shareable across the sandbox boundary (forcing the
daemon to run a different executor than `ship`/`land`), or if a deployment needs orchestration the
engine contract cannot express.

The decision is **Accepted**; decision 0027 (the parent dependency) is Accepted. The corresponding
`SPEC.md` change is **not** made yet — application is deferred to land in step with the companion
`vcsx` spec and decisions 0029–0030 (see `Plan.md` Status).
