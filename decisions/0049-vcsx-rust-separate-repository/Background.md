# Background — 0049 Implement `vcsx` in Rust as a separate repository

## Context

Decision 0042 fixed the engine layer's realization (its own codebase from the start, pinned by
`version_floor`, reached over the invocation contract) and its sequencing (`engine-direct` first). It
deliberately named no implementation language, because `SPEC.md` Section 3.4 states that this
specification "names no engine implementation or language normatively" and `VCSX-SPEC.md` Section 1.1
keeps the engine spec equally neutral. Decision 0045 then fixed the multi-implementation model: this
decision log binds every implementation, while idiomatic realization choices — concurrency model,
error idiom, libraries, layout — are invisible to the contract and live in each implementation's own
log.

What remained undecided is therefore narrow and concrete: which language the first engine is written
in, which repository holds it, and where that implementation's own decision log lives. Implementation
is now beginning, so those three are answered here. Nothing about the engine's specified shape is
re-opened; 0042's realization and sequencing are confirmed, not revisited.

One further input is available that 0042 recorded only as a possibility. Its Option C — "generalize an
existing wrapper layer into the engine" — pointed at the wrapper layer in the repository that embeds
this specification (`scripts/vcs/`), which 0042 admitted "as a seed, not exclusive with A". That layer
is now a known quantity and its transferable and non-transferable parts can be named precisely rather
than left as an open build choice.

## Options considered

### Language

- **Option A — Rust (chosen).** Trade-offs: the engine's core is a policy machine over a closed token
  vocabulary whose proto classes are frozen within a major version (`VCSX-SPEC.md` Sections 4.2, 4.3,
  8.5), and Rust's sum types let the shape of the matching ladder be enforced by the type system
  rather than by tests — a lifecycle position structurally cannot take a `#class` fallback
  (Section 5.3). The engine is a short-lived subprocess with a strict exit-code and envelope contract
  (Section 8.3) invoked once per operation, so a single static binary with no runtime start-up cost
  suits both the invocation model and the way 0028 pins the engine as an external tool. Costs: the
  forge plugins are ordinary HTTP/JSON clients where other ecosystems are more mature, and the
  contributor pool for a Way-of-Working tool is smaller.
- **Option B — Go.** Trade-offs: the strongest ecosystem for the forge plugin layer (mature GitHub and
  Forgejo clients) and also a single static binary, which is the property the pinning model actually
  depends on. But the reason registry and the matching ladder become runtime-checked string handling
  rather than exhaustive types, which moves the largest cluster of `VCSX-SPEC.md` Section 13.1 checks
  from the compiler back into tests.
- **Option C — Python.** Trade-offs: matches the existing wrapper layer, so Option C seeding would be
  a direct port rather than a re-write. But it needs an interpreter on every machine that runs the
  engine, which fights the "pinned external tool" model, and offers the least support for a frozen
  token vocabulary.

### Repository

- **Option A — a separate implementation repository (chosen).** The specification repository keeps
  `SPEC.md`, `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, and this decision log; the Rust engine lives in its
  own repository with its own decision log. Trade-offs: keeps the specification honestly
  language-neutral, which is the property 0045's whole multi-implementation model rests on, and keeps
  the implementation's idiomatic log from competing with this one. Costs: the shared token vocabulary
  now has a third spelling across two repositories, and a contract change plus its implementation land
  as two changes rather than one.
- **Option B — the engine in this repository, beside its specification.** Trade-offs: one change lands
  a spec edit and its implementation together, and token drift is visible in a single diff. But
  co-locating exactly one implementation with the contract that is supposed to bind several makes
  neutrality a matter of discipline rather than structure, and it is the arrangement 0042 already
  rejected when it chose "its own codebase" over an in-process module.
- **Option C — a monorepo holding the engine and a future Symphony implementation.** Trade-offs:
  attractive later, when both are in motion. But 0042's chosen sequencing means only one is in motion
  now, and the cross-repo tax it weighed is only paid when both are — so this buys nothing yet while
  pre-committing the layout.

### Sequencing

Not re-opened. 0042 chose `engine-direct` first and this decision confirms it. The alternatives
(`interactive-agent` first, `daemon` first) were weighed there and nothing in the language or
repository choice bears on them.

## Decision and reasoning

Write the first `vcsx` engine in **Rust**, in its **own repository**, building the `engine-direct`
topology first per 0042.

The language choice follows the engine's actual centre of gravity. Three of the eight checks in
`VCSX-SPEC.md` Section 13.1 — matching, unmatched policy, determinism — are about the policy machine,
and the reason registry (Section 4.3) is a closed table of 26 rows whose proto class must not change
within a major version. That is a type-system problem before it is a plumbing problem, and it is where
a mistake is both most likely and least visible: a reason routed to the wrong class silently changes
which policy edge fires. Rust's exhaustive matching turns most of that cluster into compile errors. The
forge plugins, where Rust is weakest, are the part of the engine most insulated behind a neutral
interface (Section 9.2) and least likely to be where correctness is lost.

The repository split follows 0045 rather than convenience. The specification's language-neutrality is
not a stylistic preference; it is the mechanism that lets a second implementation exist at all, and
co-locating the first implementation with the contract erodes it by degrees that are hard to notice in
review. Keeping them apart also gives the implementation somewhere to record the choices 0045 defined
as invisible to the contract, without those entries diluting a log that binds every implementation.

**The wrapper layer is a design seed, not liftable code.** What transfers is proven behavior: the
escalate-on-ambiguity bias, one JSON object on stdout, the `done` / `needs_caller` / `error` proto
classes, riding out forge rate limits rather than escalating them, and deriving the remote slug and
branch from jj in a secondary workspace that has no colocated git storage — the case `VCSX-SPEC.md`
Sections 3.3 and 13.1 both call out and the one most implementations get wrong. What does **not**
transfer is the exit-code numbering: the wrappers use `0` / `2` / `10` / `64`, while Section 8.3
requires `0` / `10` / `20` / `2`, with `2` meaning a usage or configuration error in which the policy
did not run. The two schemes overlap on `0` and reuse `2` and `10` with different meanings, so code
carried across would satisfy its own tests while silently violating the invocation contract. Read the
wrapper layer for its shape; re-derive every numeric value from Section 8.3.

Decision-log hygiene follows 0045 unchanged. A change to `VCSX-SPEC.md` or `VCSX-CONTRACT.md`, or a
gap in either that Rust exposes, routes a decision back to **this** log. Rust-idiomatic choices — crate
layout, whether the engine is async at all, the error idiom, the HTTP client — live in the
implementation repository's own log and never appear here.

We would reconsider the language if the forge plugin layer came to dominate the work and its ecosystem
gap proved expensive in practice, or if a second engine implementation in another language made
cross-language corpus pressure the deciding factor. We would reconsider the repository split if the
cross-repo cost began to dominate while both codebases are in motion — the case 0042 already
anticipated, noting that its Option B (an in-process module behind the identical contract) "needs no
re-decision, the contract being identical across encodings".

The decision is **Accepted**. Depends on 0042 (realization and sequencing) and 0045
(multi-implementation model and decision-log hygiene); relates to 0027 and 0028 (the engine layer it
realizes). It leaves three follow-ons, taken up immediately as decisions 0050, 0051, and 0052.
