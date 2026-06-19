# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repo is

This repository holds the specification for **Symphony**, a long-running service that orchestrates
coding agents to do project work: it polls an issue tracker, creates an isolated per-issue
workspace, and runs a coding-agent session for each issue.

The long-term intention is to implement a variant of Symphony here over time. As of now the repo
contains only:

- `SPEC.md` — the authoritative, language-agnostic service specification (this is the artifact).
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
  `Rejected`), a link to the decision's folder, and a short focused prose description.
- `decisions/NNNN-short-slug/` — one folder per decision, containing:
  - `Background.md` — why the decision was made (context, options, reasoning, trade-offs).
  - `Plan.md` — a detailed plan for how it is implemented in `SPEC.md`.
  - `Sessions.md` — the Claude session name(s) and id(s) that worked on the decision.

Workflow when making or changing a decision:

- Copy `decisions/_template/` to `decisions/NNNN-short-slug/` using the next zero-padded number, and
  fill in the three files.
- Add or update the matching chapter in `DECISIONS.md`, including its **State**.
- Append the current session to that decision's `Sessions.md`. The session id is the transcript
  filename (without `.jsonl`) under `~/.claude/projects/<project>/`; give it a short human name.
- Re-evaluating an existing decision is itself logged: update the **State**, extend `Background.md`
  with the new reasoning rather than erasing the old, and record the session.
- Prefer making a substantive spec change *after* its decision is captured, so the reasoning is never
  lost.

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

## Working agreements

- Keep changes scoped and reviewable; prefer focused edits over large rewrites.
- After substantive content changes, keep the cross-cutting sections in sync: the config cheat sheet
  (Section 6.4), test matrix (Section 17), and implementation checklist (Section 18).
- Do not bump the `Status:` line or restructure the document without being asked.
- This is a spec, not code: there is nothing to build, run, or test yet. Don't fabricate build/test
  commands.
