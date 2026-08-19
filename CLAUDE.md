# CLAUDE.md

Guidance for coding agents working in this repository. `AGENTS.md` is a symlink to this file, so
Claude Code and AGENTS.md-aware agents (for example Codex) read the same instructions.

## What this repo is

This repository holds the specification for **Symphony**, a long-running service that orchestrates
coding agents to do project work: it polls an issue tracker, creates an isolated per-issue
workspace, and runs a coding-agent session for each issue.

The long-term intention is to implement a variant of Symphony here over time. As of now the repo
holds specification and planning material, not implementation:

- `SPEC.md` — the authoritative, language-agnostic service specification (this is the artifact).
- `VCSX-CONTRACT.md`, `VCSX-SPEC.md` — the layered `vcsx` engine documents `SPEC.md` defers to.
- `DECISIONS.md` and `decisions/` — the decision log (see below).
- A phased-delivery workflow — reusable skills, ExecPlan standard, templates, and planning docs —
  that stays dormant until implementation is explicitly begun (see "Phased implementation workflow").
- `LICENSE`

There is no implementation yet. Treat `SPEC.md` as the primary work product.

## Current focus: improving SPEC.md

The near-term task is to refine and extend `SPEC.md`. **The most important constraint is that edits
MUST preserve the existing style and level of description.** Do not rewrite the document into a
different voice, granularity, or format. Improvements are surgical: clarify, correct, fill gaps, and
extend using the same conventions the document already uses.

When asked to "improve" the spec, default to changes that:

- Fix inaccuracies, ambiguities, contradictions, or gaps.
- Add missing detail at the *same altitude* as neighbouring text — not deeper, not shallower.
- Keep the document internally consistent (cross-references, defaults, error codes, field names).

If a requested change would alter the document's style or descriptive level, surface that tension
before making it rather than silently changing the register.

## SPEC.md style guide (must be preserved)

Match these conventions exactly. When in doubt, copy the shape of the nearest existing passage.

### Normative language
- Uses RFC 2119 keywords, written as **plain uppercase** in prose: `MUST`, `MUST NOT`, `REQUIRED`,
  `SHOULD`, `SHOULD NOT`, `RECOMMENDED`, `MAY`, `OPTIONAL`. (They appear in backticks only in the
  "Normative Language" definition section.)
- `Implementation-defined` is a defined term: the behavior is part of the contract but the spec does
  not pick one policy; implementations MUST document their choice. Use it deliberately.
- Be prescriptive and neutral. State requirements; avoid hedging, marketing, or tutorial tone.
- A guarantee MUST be stated over something a consumer can check without knowing which backend is
  underneath. Use the `spec-guarantee` skill when drafting or repairing any MUST/MUST NOT clause
  that promises an engine or a backend will or will not do something.

### Structure
- Decimal section numbering: `## N. Title`, `### N.M Subtitle`, `#### N.M.K Subsubtitle`. Headings
  are Title Case. Keep numbering contiguous and update cross-references if you insert/reorder.
- Cross-reference by section number in prose, e.g. "see Section 6.2", "fields listed in Section
  4.1.1".
- Asides are short labelled blocks: `Note:`, `Notes:`, `Important:`, `Important boundary:`,
  `Important nuance:`, `Design note:`. Follow the existing label set rather than inventing new ones.

### Formatting
- Wrap prose at **100 columns**. (Code blocks, tables, and unavoidably long tokens may exceed it.)
- Heavy use of bulleted lists with nested sub-bullets; numbered lists for ordered sequences and
  algorithms.
- Field documentation pattern: a bullet `` - `field.name` (type) `` followed by nested bullets for
  description, constraints, and `` - Default: `value` ``.
- Backticks wrap all code-like tokens: field/key names, file names (`WORKFLOW.md`), literal values
  (`linear`, `30000`), tracker/orchestration state names (`Todo`, `In Progress`), error/category
  codes (`missing_workflow_file`), event names, function names, and identifiers.
- Examples use fenced blocks: ```json``` for payloads, ```text``` for pseudocode.

### Language-agnostic discipline
- The spec is deliberately **language- and framework-neutral**. Do not introduce a specific
  programming language, library, or implementation detail into normative text.
- Reference algorithms (Section 16) use neutral pseudocode in ```text``` blocks with `snake_case`
  function and field names. Keep that style.
- Where behavior legitimately varies, use `Implementation-defined` plus a "MUST document" clause
  rather than picking a winner.

### Conformance vs. extensions
- The document separates **Core Conformance** from **OPTIONAL extensions**. Extensions live in their
  own sections/appendices and are marked `OPTIONAL`, with config keys owned by that extension.
- New optional behavior SHOULD be added as an extension, not folded into core requirements. Mark
  optionality explicitly and mirror Sections 17 (test matrix) and 18 (checklist) when adding it.
- The Codex app-server protocol is the source of truth for protocol shape; the spec defers to it and
  does not duplicate protocol schemas. Preserve that boundary.

## Decision log

Decisions that shape `SPEC.md` (and later the implementation) are recorded in `DECISIONS.md` plus a
per-decision folder under `decisions/`. The goal is to preserve the *reasoning* so a decision can be
re-evaluated later without re-deriving its context.

- `DECISIONS.md` — one chapter per decision: short heading, **State** (`Proposed` / `Accepted` /
  `Rejected` / `Superseded`), a link to the decision's folder, and a short focused prose description.
  See the `DECISIONS.md` States legend for what each means; `Superseded` (decision 0033) marks a
  decision replaced by a later one and names its successor.
- `decisions/NNNN-short-slug/` — one folder per decision, containing:
  - `Background.md` — why the decision was made (context, options, reasoning, trade-offs).
  - `Plan.md` — a detailed plan for how it is implemented in `SPEC.md`.
  - `Sessions.md` — the Claude session name(s) and id(s) that worked on the decision.

Prefer making a substantive spec change *after* its decision is captured, so the reasoning is never
lost. Use the `decision-record` skill for the procedure — the folder mechanics, the bar a
`Background.md` has to clear, and how a re-evaluation or a review finding is logged. Invoke it as
`/decision-record` in Claude Code and `$decision-record` in Codex.

### Addressing SPEC.md from a Plan.md (decision 0002)

So plans stay re-executable in any order and after intervening edits, `Plan.md` steps address
`SPEC.md` by stable identity, never by line/column or paragraph/bullet ordinal:

- Prefer code-token identifiers (field names, error/category codes, state names, event names, file
  names); then section titles; cite a section number only as a secondary hint, paired with its title
  — e.g. `Section 8.4 "Retry and Backoff"`. Section numbers renumber on insert/reorder, so they are
  not a reliable primary key.
- Phrase each step as a declarative post-condition ("ensure X exists with `Default: Z`"), not an
  imperative positional diff. Where prose must be located, quote a short unique nearby token. Give
  each step a recognizable done-condition so it is self-checking and idempotent on re-execution.
- When a decision renames or removes an anchor (a code-token or a section title), record it
  append-only in that decision's `Plan.md` `Anchor changes` section. Do **not** keep a standalone
  registry of current anchors: `SPEC.md` is the source of truth for what exists now; the per-decision
  records are the history of what changed.

## Phased implementation workflow (dormant)

For when implementation begins, the repo carries a phased-delivery workflow that turns `SPEC.md`
into reviewable vertical slices: a discovery/behavior-contract/verification/implementation/closeout
gate sequence. It is installed but **dormant** — the near-term task remains refining `SPEC.md`, not
building product code. Do not generate requirement IDs, populate the roadmap or traceability matrix,
or start product implementation unless explicitly asked to.

Skills live under `.agents/skills/` (the canonical copies) and are mirrored to `.claude/skills/` as
symlinks. In Claude Code invoke them as `/spec-roadmap`, `/phase-workflow`, `/phase-planner`,
`/phase-behavior-contract`, `/phase-verification`, `/phase-implementer`, and `/phase-closeout`; Codex
invokes the same skills as `$spec-roadmap`, and so on. `USAGE.md` documents the commands.

`decision-record`, `spec-guarantee` and `plan-review` live in the same tree but are **not** part of
this dormant bundle: they govern the work happening now and are neither described by `USAGE.md` nor
checked by `scripts/validate_workflow_bundle.py`.

Use `plan-review` on a session plan once it is written and before its first edit — it checks the
plan's claims about the corpus, mechanically for the quoted spans (`python3
scripts/check_plan_anchors.py <plan.md> --rev <revision>`) and by reading for the conventions above
and for whether each consequence the plan keeps survives the premise it removes. Decision 0134's
plan carried four such claims that did not hold, one of which reached `VCSX-SPEC.md`.

### Source of truth (once planning begins)

- `SPEC.md` — canonical product requirements. Stable requirement IDs are introduced by `spec-roadmap`
  when planning begins; until then requirements are addressed by section title and code-token
  identity (see decision 0002).
- `docs/implementation/ROADMAP.md` — phase allocation, ordering, dependencies, and status (an
  unpopulated placeholder until preparation runs).
- `docs/implementation/TRACEABILITY.md` — every normative requirement mapped to phases and evidence
  (likewise a placeholder until preparation runs).
- `.agent/PLANS.md` — the ExecPlan format and maintenance rules.
- `docs/implementation/phases/phase-*.md` — one living ExecPlan per phase, created from
  `docs/implementation/templates/`.

### Governance (during implementation)

- Complex features, migrations, major refactors, and multi-session work require an ExecPlan
  conforming to `.agent/PLANS.md`.
- Read the applicable SPEC requirements, roadmap entry, traceability rows, and active ExecPlan before
  changing code.
- Do not silently resolve product ambiguity. Record the question, affected requirement IDs, and the
  blocker.
- Keep each phase's `Decision Log` and `Surprises & Discoveries` authoritative; add concise
  checkpoint outcomes after each stage.
- Do not begin a later stage until the prior gate is approved, unless the ExecPlan records an
  explicit exception and rationale.
- Preserve unrelated changes and review the Git diff before completion.
- Do not mark a phase complete without recorded, observable validation evidence.

`python3 scripts/validate_workflow_bundle.py` checks the workflow bundle's structure and skill
frontmatter; it validates the scaffolding only and does not build or test the spec.

## Working agreements

- Keep changes scoped and reviewable; prefer focused edits over large rewrites.
- After substantive content changes, keep the cross-cutting sections in sync. In `SPEC.md`: the
  config cheat sheet (Section 6.4), test matrix (Section 17), and implementation checklist
  (Section 18). In `VCSX-SPEC.md`: the test matrix (Section 13.1), implementation checklist
  (Section 13.2), and Conformance Statement obligations (Section 13.3).
- **A change that adds an `Implementation-defined` or "MUST document" obligation MUST add its row to
  the matching Conformance Statement template** — `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` for the
  engine, `CONFORMANCE-STATEMENT-TEMPLATE.md` for Symphony. The templates' tables are what a
  generator parses, so an obligation with no row is invisible to every check: the table is complete
  against itself and a Statement generated from it is silently missing the answer. Three decisions in
  a row missed this before it was caught downstream (decision 0128).
- Do not bump the `Status:` line or restructure the document without being asked.
- This is a spec, not code: there is nothing to build, run, or test yet. Don't fabricate build/test
  commands.
