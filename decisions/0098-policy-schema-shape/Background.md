# Background — 0098 The `repo.policy.toml` hook namespace, and per-branch sections

## Context

Two changes to the same schema, taken together because each would otherwise rewrite the other's
work.

### The `hooks` namespace has two owners and no stated rule

`repo.policy.toml` carries two different hook schemas under one key.

`SPEC.md` Section 5.3.4 writes scalars:

```toml
[hooks]
after_create = "tools/bootstrap.sh"
timeout_ms   = 60000
```

`VCSX-SPEC.md` Section 6.6 writes subtables:

```toml
[hooks.scan-content]
context = "in_sandbox"
run     = "./scan"
```

TOML permits both in one document, so nothing breaks today. Three things are nonetheless wrong.

**A name is inexpressible.** A repository wanting an engine hook named `after_create` cannot have
one: TOML rejects `after_create = "..."` and `[hooks.after_create]` in the same document. Neither
specification says the lifecycle names are reserved, so the collision is discovered rather than
documented.

**Two timeouts sit in one namespace with different defaults.** `hooks.timeout_ms` is Symphony's,
default `60000`. The engine's hook bound is its own, `Implementation-defined` with a floor of 600
seconds. For a host-side hook declared in `[hooks.<name>]` and invoked by the engine,
`hooks.timeout_ms` is adjacent and authoritative-looking and does not apply.

**A valid Symphony config may be refused by a conforming engine.** Section 6.10 makes this
`malformed_policy`:

> A declared hook that names no unit to run — a `[hooks.<name>]` table with no `run`

The word *table* is what saves it: `after_create = "..."` is a scalar, so a careful engine skips it.
That disambiguation — **scalars belong to the consumer, tables to the engine** — is real,
load-bearing, and written nowhere. An engine reading "every key under `hooks` is a hook" refuses a
document Symphony considers valid, and Section 6.1's "unknown keys SHOULD be ignored" does not
rescue it, because these are not unknown keys but keys under a table the engine believes it owns.

**And the documentation sits in the wrong section.** `SPEC.md` Section 5.3 opens "This section
documents the operator policy config keys", and Section 5.3.4 `hooks` sits inside it describing
hooks that live in `repo.policy.toml` and `WORKFLOW.md`.

### Context is declared for one hook family and derived for the other

`SPEC.md` Section 5.3.4, on the lifecycle hooks:

> Both sets share the same lifecycle points. A lifecycle point MAY be defined in either artifact;
> when both define it, the `repo.policy.toml` hook runs on the host and the `WORKFLOW.md` hook runs
> inside the sandbox.

That is the artifact determining the context. The engine's named hooks declare `context` instead.
Two families, two mechanisms, no reconciliation — and the declared one admits a combination the
derived one cannot express: a hook declared `host_side` whose unit the working tree supplies, which
decision 0095 had to forbid in prose rather than by construction.

### A repository cannot vary its policy by target

Decision 0094 traded this away without naming it. Before, the policy came from the resolved base
revision, so work targeting `release/2.0` read that branch's own `repo.policy.toml` and a release
track could carry stricter host-side hooks. Afterwards one policy source governs every target, and
the capability is gone. `by_prefix` does not replace it: it maps a work-branch prefix to a *base
branch*, not to a set of hooks.

The loss lands exactly backwards from where a deployment wants it, since the release track is the
one that most wants a signing gate.

## Options considered

**For the namespace — symmetric or asymmetric prefixing.** Asymmetric moves only Symphony's keys, to
a `[workspace_hooks]` table of their own, and leaves `[hooks.<name>]` untouched. It is the smaller
diff by a wide margin: `[hooks.<name>]` is shared contract surface, named in `VCSX-CONTRACT.md`,
`conformance/vcsx/vocabulary.json`'s `policy_sections` and the validation vectors, so changing it is
a contract change across four artifacts. It also has a fair claim to being the *correct* asymmetry,
since the conflict was created by Symphony writing into a table `VCSX-SPEC.md` Section 6 owns.

Symmetric prefixing loses on diff size and wins on the fresh reader, which is the criterion chosen:
`[hooks.engine.<name>]` beside `[hooks.workspace]` states the two-owners fact at the point of
declaration, where `[hooks.<name>]` beside `[workspace_hooks]` leaves a reader to wonder why one is
prefixed and the other is not. Nothing implements this yet, so the contract-change cost is
bookkeeping rather than migration.

**For context — keep declaring it, or derive it from the artifact.** Keeping it is one fewer change
and preserves a capability: today one file can declare a host-side hook and an in-sandbox hook side
by side. Deriving it costs that, since the artifact then fixes the context and the in-sandbox one
must move to `WORKFLOW.md`.

Deriving wins on two counts. It makes 0095's rule structural rather than stated — a host-side hook's
unit cannot come from the working tree, because a host-side hook is one declared in the artifact the
working tree does not supply. And it collapses a genuine oddity: `repo.policy.toml` is today read
from **two revisions**, host-side sections from the policy source and the in-sandbox `before:commit`
gate from the worktree (Section 15.4). Under derivation the gate's *declaration* moves to
`WORKFLOW.md` and `repo.policy.toml` is read from exactly one revision.

The edge that invokes the gate stays where it is, so nothing is given up that matters: control flow
remains trusted and unremovable by the agent, while the gate's body is the agent's — which is the
division the whole hook argument has been converging on.

**For per-branch matching — prefix, glob, or expressions.** Prefix matching with longest-wins is
deterministic by construction, which Section 5.4's one-edge-per-trigger rule needs: two sections
that both matched and both contributed an edge for one trigger would be ambiguous. It reuses the
matching `by_prefix` already has, so there is no new semantics to specify, test or publish. It
cannot match a suffix, so a repository naming branches `2.1-release` rather than `release/2.1` is
not served.

Glob adds that at the cost of a precedence rule for two matching globs and a dialect question across
implementations. Expressions add conditioning on things other than the branch name at the cost of a
grammar, an evaluation order and a failure mode.

Prefix-now-extensible-later is chosen: ship longest-prefix-wins, but as a *named* matcher inside a
`match` table, so a later decision adds `glob` without a breaking change to every section that
already exists.

## Decision and reasoning

**Hooks are prefixed symmetrically.** `[hooks.engine.<name>]` for the named units a `run` edge
invokes; `[hooks.workspace]` for the lifecycle points. Both artifacts carry both namespaces, so
`WORKFLOW.md` gains the ability to declare named engine hooks — which it needs, because that is
where in-sandbox ones now live.

**Context is derived from the artifact, not declared.** The `context` key is removed from hook
declarations. A hook declared in `repo.policy.toml` is host-side; one declared in `WORKFLOW.md` is
in-sandbox. The engine still receives a context per hook, because it is handed one merged surface
and never sees two files (Section 3.2) — but it is the consumer that tags each hook while assembling
that surface, which decision 0097's `load_policy` already has it doing. `context` becomes
engine-visible and author-invisible.

Edge `context` is untouched: an edge's context participates in matching, a hook's does not, and
collapsing the two would be a different decision with a different argument.

**Per-branch sections.** A `[[branch]]` section carries a `match` table naming exactly one matcher —
`prefix` today — and any policy keys it wishes to differ in. The most specific matching section
applies, longest prefix winning; where none matches, the top level applies alone, so no empty-prefix
default is needed as `by_prefix` requires one. A section **merges over** the top level key by key,
mirroring the `vcsx.toml` merge rule the schema already has, so a release track states a signing
gate without restating every hook.

Two sections with identical `match` are `duplicate_branch_section`, on the same reasoning as
`duplicate_edge`: the specification refuses non-determinism rather than resolving it. A `match`
naming no recognized matcher, or more than one, is `malformed_policy` — a declared key whose value
the schema does not admit, which Section 6.1's forward-compatibility rule explicitly does not cover.

**Under `target_branch` the sections are the target's own** (decision 0097), so a contributor who
can land a pull request can author one. That is a consequence of the opt-out rather than of this
decision, and Section 15.4 already states it.

**The lifecycle-hook documentation moves** out of `SPEC.md` Section 5.3, which declares itself to be
about operator config, into the section that owns the repository artifacts.

**Reconsideration triggers.** Reopen the matcher if a deployment's branch naming is not
hierarchical — the evidence is a repository wanting a suffix rule and having to rename branches to
get one, which is the specification dictating naming rather than describing it. Reopen the derived
context if a repository genuinely needs a host-side and an in-sandbox hook of the same name in one
artifact; the artifact split makes that inexpressible, and it is the one capability this decision
removes.

Relates to 0095 (whose unit-provenance rule this makes structural), 0097 (whose `load_policy` is
where the consumer tags context, and whose `target_branch` mode changes who authors a section), 0094
(whose split removed the per-target policy this restores), and 0002.
