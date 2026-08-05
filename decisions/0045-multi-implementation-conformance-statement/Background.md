# Background — 0045 Multi-implementation conformance: the Conformance Statement

## Context

The long-term intention (CLAUDE.md) is to implement Symphony from `SPEC.md` — and the near-term
question that prompted this decision is how to run *several* implementations, potentially in
different programming languages, without fragmenting the contract. The spec is already built for
this: it is language-agnostic (Status line, Section 3.2's portability layering), and successive
decisions have added the machinery variation needs — 0027's three layers, 0040's engine
contract/spec split, 0042's engine as a separately-pinned deliverable, 0043's layer-keyed
conformance profiles, and Section 14.3's state recovery classes.

What is missing is not more machinery but a *home* for one kind of choice. "Language-specific
choice" is two different things:

- **Contract-visible variation** — choices the spec deliberately leaves open but that a consumer,
  an auditor, or another implementation can observe: the `Implementation-defined` / `MUST document`
  obligations (there are 26 in `SPEC.md` today), the profile and topology an implementation claims
  (0043), the OPTIONAL extensions it ships (Section 18.2), the engine `version_floor` and the agent
  protocol floor it pins (Sections 8.5 and 10.2), and the recovery class it assigns each
  Orchestrator Runtime State field (Section 14.3). Every one of these is already required to be
  documented *somewhere*, but nowhere does the spec say *where*, or require them assembled — so two
  implementations cannot be compared, an implementation cannot be audited at a glance, and the
  recurring failure — an obligation silently skipped — stays invisible.
- **Idiomatic realization** — choices the contract cannot observe and the spec is silent on:
  concurrency model, error-handling idiom, dependency-injection style, serialization and config
  libraries, project layout. Across languages the hazard is these leaking upward into normative text
  (violating CLAUDE.md's language-agnostic discipline) or into *this* decision log, which exists only
  for choices that bind `SPEC.md`.

Two adjacent gaps surface with the same question and are named, not closed, here: there is no
shared, language-neutral conformance corpus that turns Sections 17 and 18's prose intent into
executable pass/fail vectors every implementation runs; and there is no definition of live-state
interoperability between two implementations — Sections 14.3 and 14.4 give *containment* (each
implementation reconstructs from tracker and filesystem), not *handoff*.

## Options considered

How a language-specific implementation records its contract-visible choices:

- **Option A — a normative, human-readable Conformance Statement with a repo-owned template
  (chosen).** `SPEC.md` gains a short normative section requiring every conforming implementation to
  publish a Conformance Statement consolidating: the `SPEC.md` / `VCSX-SPEC.md` /
  `VCSX-CONTRACT.md` revisions targeted; the claimed layer profiles and deployment topology (0043);
  the OPTIONAL extensions shipped and their config namespaces (Section 18.2); the engine
  `version_floor` and agent protocol floor pinned (Sections 8.5, 10.2); a resolution for every
  `Implementation-defined` / `MUST document` obligation; the recovery class assigned each
  Orchestrator Runtime State field (Section 14.3); the trust and safety posture (Sections 1, 9.6,
  15); and any known deviation. The repo carries the template
  (`CONFORMANCE-STATEMENT-TEMPLATE.md`) each implementation copies into its own repo and fills.
  Trade-offs: gives the 26 scattered obligations one auditable home; makes two implementations
  diff-able; the template pre-enumerates the obligations so none is silently skipped; costs one new
  `SPEC.md` section and one template file. It *restates* obligations that already exist rather than
  adding new ones — the same "derive from one list rather than restate it" move 0043 made for profile
  subsets — so its risk is drift between the template and the clauses it mirrors, mitigated by
  pre-populating it from `SPEC.md`'s own tokens and keeping it a checklist of pointers, not a second
  source of truth.
- **Option B — leave the obligations scattered (status quo).** Each `MUST document` clause stands
  alone; an implementation documents each wherever it likes. Trade-offs: zero new surface, honest to
  today's text; but nothing can be audited at a glance, there is no uniform shape across languages,
  and the silent-skip failure stays invisible. Rejected: the point of multiple implementations is
  comparability, which scatter defeats.
- **Option C — fold the consolidation into Section 18 only.** Add the documentation obligations as
  checklist items; no published-artifact concept, no template. Trade-offs: cheaper; but Section 18
  is the *implementer's* definition-of-done for behaviors, not a *published declaration* a consumer
  reads, and a checklist bullet cannot carry a filled-in resolution value. Rejected as half the
  mechanism — the template is what makes the output uniform across languages, and the publication
  requirement is what makes it consumable.
- **Option D — a machine-readable conformance manifest (schema'd TOML/JSON).** Define a descriptor an
  implementation emits and tooling validates. Trade-offs: strongest for automated interop and
  cross-implementation tooling; but it over-commits the spec to a wire format before any
  implementation exists to shape it, against the same defer-schema-until-needed discipline 0040
  applied to the engine. Rejected *for now*; recorded as the natural successor once a second
  implementation or a conformance harness creates real demand.

The two adjacent gaps:

- **Shared conformance corpus.** The cross-language enforcement mechanism: data-driven vectors and
  scenarios — config and `WORKFLOW.md` inputs mapped to expected parse results, error/category
  codes, workflow-transition-graph and action-policy-machine outcomes, and message-formulation
  outputs — that every implementation runs against its own binary, so Sections 17 and 18's prose
  intent becomes an objective pass/fail identical in every language. Not built here: it is a
  spec-adjacent deliverable whose first slice is authored when implementation begins (the phased
  workflow is dormant per CLAUDE.md). Recorded so it is not re-derived.
- **Decision-log hygiene.** This log captures choices that bind `SPEC.md` and therefore every
  implementation; language-idiomatic choices live in each implementation's *own* decision log and
  never here. The one bridge: a language that reveals a genuine gap or ambiguity in `SPEC.md`
  triggers a decision *here* and a spec fix, rather than a local workaround — so multi-language
  pressure improves the spec instead of fragmenting it.
- **Live-state interoperability.** Explicitly out of scope. Sections 14.3 and 14.4 give containment,
  not handoff of a running issue between two implementations. If cross-implementation handoff becomes
  a goal it is its own decision, and `SPEC.md` grows an interoperation clause — the same escalation
  0043 already anticipated for engine interoperation — rather than a restated data model. Flagged so
  its absence is a recorded choice, not an oversight.

## Decision and reasoning

Choose **Option A**; defer **Option D**. Introduce the Conformance Statement as a normative,
human-readable, published artifact and ship its template in the repo now; the `SPEC.md` section that
requires it is planned in `Plan.md` and not yet applied, matching 0043's sequencing — capture the
decision, then edit. Keep the format human-readable rather than a machine schema until a second
implementation or a conformance harness gives the schema something real to fit.

The Statement adds no obligation: it is a *view* over 0043's profiles, Section 18.2's extensions,
Sections 8.5 and 10.2's floors, the `Implementation-defined` clauses, and Section 14.3's recovery
classes — the same single-source derivation 0043 used so a checklist restated in three places cannot
drift into three checklists. It also keeps `SPEC.md` language-agnostic by construction: the template
records an implementation's choices *outside* the normative text, so no language, library, or
framework detail is ever pulled into the spec to express them.

Around the Statement sit the three recorded positions: the contract-visible / idiomatic split that
says which choices the Statement is for; the decision-log hygiene rule that keeps idiomatic choices
out of this repo while routing genuine spec gaps back into it; the shared corpus as the follow-on
that makes conformance objective across languages; and the live-state-interop non-goal.

We would reconsider if a second implementation or a conformance harness materializes (promote to
Option D's machine manifest); if the template drifts from the clauses it mirrors (fold it back into
`SPEC.md` or generate it from the spec's tokens); or if cross-implementation live-state handoff
becomes a goal (its own decision, with an interoperation clause in `SPEC.md`).

The decision is **Accepted**; the `SPEC.md` change is planned in `Plan.md` and not yet applied. The
template `CONFORMANCE-STATEMENT-TEMPLATE.md` is created with this decision.
