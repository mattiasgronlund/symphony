# Background — 0048 Conformance corpus, prompt-rendering slice

## Context

Decision 0046 established the conformance corpus and its first slice of pure derivations, and its
`README.md` named prompt rendering as the next pure-slice candidate: "deterministic but
template-engine shaped". `render_prompt` is pure — given a template, a normalized issue, and an
attempt it returns a string (Section 12.1) — so it fits the pure-slice criterion (no sandbox,
tracker, engine, filesystem, or network). Authoring it forces two choices the first slice did not
face: how a vector expresses a *failure* expectation (Section 5.4 makes an unknown variable and an
unknown filter MUST-fail cases with error `template_render_error`, Section 5.5), and which template
syntax the vectors are written in, since Section 5.4 pins the *semantics* ("a strict template engine,
Liquid-compatible semantics are sufficient") but leaves the concrete delimiter and filter syntax to
the implementation.

## Options considered

Failure-vector schema:

- **Option A — extend `expect` to a success-or-error union (chosen).** A vector's `expect` is either
  the successful result (as today) or `{ error: <class> }` naming the error class the behavior must
  raise. The harness asserts equality on success and a raised class on failure. Trade-offs: reuses
  the existing envelope with no new top-level field, and establishes the convention every later
  error-path vector inherits (config validation, tracker errors); `expect` becomes a documented
  union.
- **Option B — a separate `expect_error` field.** Rejected: two fields for one concept when a vector
  is either a success or a failure, never both.
- **Option C — a sentinel rendered value for failures.** Rejected: it conflates a real output with
  an error and cannot distinguish a template that legitimately renders the sentinel.

Slice scope:

- Cover the clear MUSTs: known-variable substitution, nested-list iteration (Section 12.2), the
  unknown-variable and unknown-filter strict failures (Section 5.4), and `attempt` rendered as a
  present integer. Exclude the under-specified cases — first-run `attempt` rendering (see findings)
  and any specific *working* filter's output, since Section 5.4 does not enumerate the available
  filter set, so only unknown-filter *failure* is asserted, never a particular filter's result.

Template syntax:

- **Author in Liquid-compatible reference syntax (chosen).** A template must have *some* syntax;
  Section 5.4 names Liquid, and because `WORKFLOW.md` is repository-owned and must render on every
  implementation a repository targets, the template syntax is effectively a cross-implementation
  contract. The vectors use Liquid syntax and single-line templates with delimiters rather than
  inter-token whitespace, so an expected string does not depend on an engine's whitespace-control
  behavior. The softness of "sufficient" is surfaced as a finding, not resolved here.

## Decision and reasoning

Add slice 2 — `render_prompt`, six vectors in `conformance/vectors/prompt-rendering.json`. Extend the
vector `expect` to the success-or-error union and document it in the corpus `README.md` harness
contract. Author the vectors in Liquid-compatible reference syntax. Make no `SPEC.md` change.

The union is the smallest schema change that lets the corpus assert the spec's MUST-fail behaviors,
and it is the convention the corpus will reuse everywhere an error path is tested, so pinning it now
keeps later slices consistent. Every expected value traces to Section 5.4 / 5.5 / 12.2; where the
spec is silent no vector is authored, and two gaps are recorded rather than guessed:

- Section 5.4's "Liquid-compatible semantics are sufficient" is a floor, not a mandate, so a strictly
  conforming implementation could use a different concrete syntax; the reference vectors are Liquid,
  and tightening the clause to a shared syntax is a spec-clarification candidate.
- `attempt` is "null or absent" on the first run while strict mode fails unknown variables, so whether
  a first-run template that reads `attempt` renders empty or fails is undetermined; the slice tests
  `attempt` only as a present integer.

We would reconsider the syntax choice if a second implementation's non-Liquid engine cannot consume
the reference vectors (then Section 5.4 is tightened and the vectors re-expressed), and the `expect`
union if it proves too loose to distinguish outcomes (then a tagged discriminator).

The decision is **Accepted** and applied to the corpus; no `SPEC.md` change follows. Depends on 0046;
relates to 0044 (the failure-class vocabulary its error vectors name) and 0047 (the prior corpus
finding-to-decision path it reuses for the two open findings).
