# Background — 0041 Integrate the phased-spec implementation workflow

## Context

The repository's long-term intention is to implement a variant of Symphony from `SPEC.md` over time
(see `CLAUDE.md`, "What this repo is"). A reusable **Codex Phased SPEC Workflow** bundle was provided
to make that transition disciplined: it turns a large canonical `SPEC.md` into phased, reviewable
implementation through a fixed gate sequence — optional discovery, behavior contract, verification
design, incremental implementation, and conformance/closure — backed by reusable skills, an ExecPlan
standard, a roadmap, and a traceability matrix.

The bundle ships as generic starting material and, by its own `USAGE.md`, expects to be *reconciled*
with the target repository rather than dropped in verbatim. Two frictions had to be resolved:

- The bundle's `AGENTS.md` is written as though implementation is already underway and stable
  requirement IDs already exist in `SPEC.md`. Neither is true here: the near-term task is refining
  `SPEC.md` (and the layered `vcsx` documents), and no requirement IDs, roadmap, or traceability rows
  have been generated. Installed verbatim, it would push an agent to start implementation and
  contradict the current focus.
- The bundle is Codex-oriented (`.agents/skills/`, `$skill-name` invocation), but this repo is worked
  with Claude Code too. The skills needed to be available to both agents without maintaining two
  divergent copies.

## Options considered

- **Option A — install the bundle verbatim.** Simplest. Trade-off: its `AGENTS.md` misrepresents the
  current state (implementation underway, requirement IDs present) and would mislead agents; its
  skills would only be discoverable by Codex, not Claude.
- **Option B — take only the skills, drop the governance/planning docs.** Lighter footprint.
  Trade-off: the skills reference `.agent/PLANS.md`, `docs/implementation/ROADMAP.md`, and
  `TRACEABILITY.md` by name; dropping them breaks the workflow's internal references and the
  validator.
- **Option C — install the full bundle, reconciled (chosen).** Keep the skills as the single source
  of truth under `.agents/skills/`, mirror them to Claude via `.claude/skills/` symlinks, and fold the
  workflow governance into `CLAUDE.md` — the workflow is installed but **dormant** until
  implementation is explicitly begun — with `AGENTS.md` a symlink to `CLAUDE.md` so both toolchains
  read one shared instruction file.

## Decision and reasoning

Chose Option C. The workflow is a genuine asset for the eventual spec→implementation transition, so
it is worth installing whole and keeping internally consistent (the validator,
`scripts/validate_workflow_bundle.py`, passes). Making the skills available to Claude via symlinks —
rather than copies — keeps one source of truth and avoids the drift a duplicated skill set invites;
symlinked skills are already an idiom in this ecosystem. The same single-source principle governs the
instruction files: rather than maintaining a separate Codex `AGENTS.md` and Claude `CLAUDE.md` that
would drift, the governance lives in `CLAUDE.md` and `AGENTS.md` is a symlink to it, so Claude Code
and AGENTS.md-aware agents (Codex) read identical instructions. Marking the workflow dormant preserves
the near-term focus on refining `SPEC.md` and honours the decision-log discipline (no product
implementation is started as a side effect of installing tooling).

What would make us reconsider later:

- Adopting a formal skill-parity mechanism (for example a shared-skills registry with an attested
  lockstep gate) instead of plain symlinks.
- Moving the canonical skill location from `.agents/skills/` to a Codex-specific `.codex/skills/`, if
  that convention is adopted repo-wide.
- The point at which implementation actually begins: the workflow stops being dormant and
  `spec-roadmap` is run to generate requirement IDs, the roadmap, and the traceability matrix.
