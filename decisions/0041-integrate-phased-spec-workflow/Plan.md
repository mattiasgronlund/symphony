# Plan — 0041 Integrate the phased-spec implementation workflow

## Scope

No `SPEC.md` edit. This decision adds the phased-delivery workflow scaffolding, its agent-facing
governance, and this decision record. `SPEC.md`, `VCSX-CONTRACT.md`, and `VCSX-SPEC.md` are
untouched.

## Steps

Steps are declarative post-conditions, addressed by stable file and skill identity (decision 0002).
Each is idempotent and self-checking.

1. **Skills present.** `.agents/skills/<name>/SKILL.md` exists for `spec-roadmap`, `phase-planner`,
   `phase-workflow`, `phase-behavior-contract`, `phase-verification`, `phase-implementer`, and
   `phase-closeout`, each with valid `name`/`description` frontmatter, and
   `spec-roadmap/references/review-checklist.md` is present. Done-condition:
   `python3 scripts/validate_workflow_bundle.py` reports 7 skills valid.
2. **Skills available to Claude.** `.claude/skills/<name>` is a symlink to `../../.agents/skills/<name>`
   for each of the seven skills. Done-condition: `.claude/skills/<name>/SKILL.md` resolves through the
   symlink for every skill.
3. **Shared agent instructions.** `CLAUDE.md` carries the workflow's dormant guardrail, the
   source-of-truth list, and the governance rules, and notes that requirement IDs are introduced only
   when planning begins. `AGENTS.md` is a symlink to `CLAUDE.md`, so Claude Code and AGENTS.md-aware
   agents (Codex) read one shared instruction file. Done-condition: `AGENTS.md` resolves to
   `CLAUDE.md` (`test -f AGENTS.md` true through the link) and that file contains the "dormant"
   guardrail.
4. **Planning scaffolding.** `.agent/PLANS.md`, `docs/implementation/README.md`,
   `docs/implementation/ROADMAP.md`, `docs/implementation/TRACEABILITY.md`,
   `docs/implementation/templates/{phase-execplan,scenario,verification-matrix}-template.md`, and a
   tracked `docs/implementation/phases/` directory all exist. Done-condition: files present; the
   validator's required-file checks pass.
5. **Validator.** `scripts/validate_workflow_bundle.py` exists and exits 0 from the repository root.
   Done-condition: exit status 0.
6. **Usage docs.** Root `USAGE.md` and `INSTALL.md` are present, and `USAGE.md` documents Claude Code
   invocation (`/skill-name`) alongside Codex (`$skill-name`). Done-condition: `USAGE.md` contains a
   "Claude Code" subsection.
7. **Claude discoverability.** `CLAUDE.md` points to the dormant workflow, the dual-agent skill
   locations, and the validator. Done-condition: `CLAUDE.md` contains a "Phased implementation
   workflow" section.

## Cross-cutting sync

None in `SPEC.md`. The config cheat sheet (Section 6.4), test matrix (Section 17), and implementation
checklist (Section 18) are unaffected because no normative spec content changed.

## Anchor changes

None.

## Status

Applied. All seven steps satisfied; `scripts/validate_workflow_bundle.py` exits 0. The workflow is
dormant pending an explicit decision to begin implementation.
