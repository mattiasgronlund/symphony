# Background — 0046 Conformance corpus, first slice

## Context

Decision 0045 named a shared, language-neutral conformance corpus as the mechanism that makes
Sections 17–18's prose intent an objective pass/fail identical in every implementation language, and
deferred its first slice to "when implementation begins". This decision drafts that first slice and
fixes the choices every later slice inherits: a serialization format, a repository layout, a vector
schema, the harness contract, and which behaviors the first slice covers.

The corpus has two jobs: it is the cross-language enforcement mechanism (an implementation runs it
against its own binary and reports the result in its Conformance Statement, Section 7 of
`CONFORMANCE-STATEMENT-TEMPLATE.md`), and — as a side effect of authoring it against `SPEC.md` — it
exercises the spec and surfaces under-specification.

## Options considered

Serialization format:

- **Option A — JSON vectors (chosen).** Every language parses JSON with no third-party dependency;
  `SPEC.md` already uses ```json``` for payloads. Trade-off: no comments, so per-vector rationale
  lives in `description` fields.
- **Option B — YAML.** Friendlier to write and used by `WORKFLOW.md` front matter, and it allows
  comments; but it is not universally in a language's standard library and its implicit type
  coercion (the "Norway problem", sexagesimal, unquoted dates) undercuts the one property the corpus
  exists for — *identical* parsing everywhere. Rejected.
- **Option C — per-language test files.** Rejected outright: the corpus must be data, not code, or it
  is not language-neutral.

Scope of the first slice:

- **Option A — pure, host-independent functions only (chosen).** `sanitize_workspace_key`,
  `normalize_state`, `resolve_config_defaults`, `retry_backoff_delay_ms`, `available_slots`,
  `per_state_concurrency_limit`, `sort_for_dispatch`. None needs a sandbox, tracker, engine,
  filesystem, or network, so a conforming harness is a few lines and the slice runs identically on
  day one. Trade-off: it omits much of Section 17.
- **Option B — include integration behaviors now** (tracker reads, workspace safety invariants, the
  action-policy machine, message formulation). Rejected for the first slice: each needs fixtures or
  live services and a `Real Integration Profile` harness (Section 17.8); mixing them in would make
  the corpus un-runnable without infrastructure and blur the infra-free property that makes this
  slice worth shipping first.

Harness:

- **Specify a contract, not a harness (chosen).** The corpus states only: load each file, invoke the
  named `function` with `given`, assert the result equals `expect` (with a documented interpretation
  note for `sort_for_dispatch`'s ordering and `resolve_config_defaults`'s dotted-path partial
  assertion). Shipping a *reference* harness was rejected — it would be written in some language and
  reintroduce the neutrality problem the corpus removes; the per-language harness is small enough to
  write once per implementation.

Normative status and relationship to Section 17:

- The corpus is **RECOMMENDED shared evidence**, not a new REQUIRED gate. It operationalizes the
  deterministic subset of Section 17 and does not replace Section 17's human-readable matrix, which
  also covers non-deterministic and integration checks. The Conformance Statement template already
  carries the "Shared conformance corpus" evidence row this feeds. Making it a hard REQUIRED gate was
  set aside as premature before a second implementation exists to prove the contract.

## Decision and reasoning

Choose JSON (Option A) and the pure-function first slice (Option A); specify the harness as a
contract only; keep the corpus RECOMMENDED evidence tied to the Conformance Statement, with a single
pointer added to Section 17's intro on acceptance.

Every expected value is derived verbatim from the `SPEC.md` sections named in each file's
`spec_refs` (backoff from Section 8.4, slots from Section 8.3, the sanitization rule from Sections
4.2 and 9.5, the sort order from Section 8.2, the defaults from Section 6.4). Where the spec is
silent, no vector is authored: non-ASCII workspace-key sanitization does not fix whether "character"
in Section 9.5 Invariant 3 is a byte, a code point, or a grapheme, so a non-ASCII vector would encode
an answer the spec does not determine. That gap is recorded as a surfaced finding (corpus `README.md`)
and a spec-clarification follow-on — the corpus doing its second job.

The decision was **Proposed** as a draft for review and is now **Accepted**: the Section 17 pointer
in `Plan.md` is applied, and the non-ASCII clarification is taken up as its own decision.

We would reconsider the format if the corpus proves it needs comments or cross-references JSON cannot
carry; the harness contract if a second implementation's harness finds it ambiguous; and the
pure/integration split if maintaining separate slices proves not worth it.
