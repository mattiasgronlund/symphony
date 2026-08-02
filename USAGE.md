# Codex Phased SPEC Workflow

This bundle turns a large canonical `SPEC.md` into phased, reviewable implementation using reusable Codex skills.

## Workflow

Each substantial phase uses these gates:

0. Optional discovery spike
1. Behavior contract and user/admin documentation
2. Verification design, harness, and high-value failing tests
3. Incremental implementation with a thin walking skeleton
4. Documentation conformance, final validation, and closure

The phase keeps cumulative `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` sections, plus concise stage checkpoints.

## Installation

### New repository

From the repository root, copy the contents of this bundle while preserving dot-directories:

```bash
cp -R /path/to/codex-phased-spec-workflow/. .
```

Then add your canonical `SPEC.md`.

### Existing repository

Do not blindly overwrite `AGENTS.md`, `.agent/PLANS.md`, roadmap, or traceability files.

1. Commit or stash current work.
2. Copy `.agents/skills/` into the repository.
3. Merge the supplied `AGENTS.md` rules into the existing applicable `AGENTS.md`.
4. Compare and merge `.agent/PLANS.md` with any existing planning standard.
5. Copy missing templates under `docs/implementation/templates/`.
6. Keep existing canonical documentation paths when they are already established; update skill paths if necessary.
7. Run `python3 scripts/validate_workflow_bundle.py`.
8. Ask Codex to reconcile the installation:

```text
$spec-roadmap audit the installed phased workflow against this repository. Preserve existing instructions and do not implement product code.
```

## First-time preparation

Place the large specification at `SPEC.md`, or adapt the canonical path in `AGENTS.md` and the skills.

Run:

```text
$phase-workflow prepare
```

Equivalent explicit command:

```text
$spec-roadmap prepare the repository planning system from SPEC.md
```

Review the resulting:

- Requirement IDs in `SPEC.md`
- `docs/implementation/ROADMAP.md`
- `docs/implementation/TRACEABILITY.md`
- First detailed phase ExecPlan
- Open questions and discovery spikes

## Typical phase commands

### Plan the next phase

```text
$phase-workflow plan next
```

### Define the behavior contract

```text
$phase-workflow behavior phase 3
```

Review user/admin documentation, examples, permissions, failures, recovery, and scenarios. Approve or request changes before proceeding.

### Prepare verification

```text
$phase-workflow verify phase 3
```

Review the scenario-to-evidence matrix, test harness changes, and expected failing-test evidence.

### Implement

```text
$phase-workflow implement phase 3
```

To continue after interruption:

```text
$phase-workflow resume
```

### Close the phase

```text
$phase-workflow close phase 3
```

### Ask Codex what is next

```text
$phase-workflow status phase 3
```

or:

```text
$phase-workflow run-next-stage phase 3
```

The latter performs only the earliest stage whose prerequisites are satisfied.

## Recommended review policy

Use manual review gates after Stage 1 and Stage 2:

- Stage 1: approve intended system behavior and terminology.
- Stage 2: approve how correctness will be demonstrated.

Stage 3 may proceed milestone by milestone. Stage 4 verifies that documentation and implementation conform.

## Multiple phases

Avoid fully detailing every phase at project start. Maintain a complete roadmap, a full plan for the next phase, and optionally a lighter outline for the following phase. Expand later phases closer to implementation because discoveries from earlier work may change them.

For sequential execution:

```text
$phase-workflow plan next
$phase-workflow behavior next
$phase-workflow verify next
$phase-workflow implement next
$phase-workflow close next
```

Prefer separate Codex sessions or commits for each gate so diffs remain reviewable.

## Suggested Git checkpoints

```bash
git add SPEC.md AGENTS.md .agent .agents docs/implementation
git commit -m "Establish phased implementation workflow"
```

For a phase:

```text
planning → behavior-contract commit → verification commit → implementation commits → closeout commit
```

## Adapting paths

If your repository uses different paths, update all references consistently in:

- `AGENTS.md`
- `.agent/PLANS.md`
- Each relevant `SKILL.md`
- `docs/implementation/README.md`

Do not create duplicate competing roadmaps or specifications.

## Skill discovery

Repository-scoped skills live under `.agents/skills/<skill-name>/SKILL.md`. Start Codex from the repository or a descendant directory so applicable repository skills and `AGENTS.md` files are discovered.

You can mention a skill explicitly using `$skill-name`. The descriptive frontmatter also allows Codex to select a matching skill automatically, but explicit invocation is preferable for gate-controlled work.

### Claude Code

The same skills are available to Claude Code as project skills under
`.claude/skills/`, each a symlink to the canonical copy in `.agents/skills/`, so
both agents share one source of truth. In Claude Code invoke a skill as
`/skill-name` (for example `/phase-workflow`); the frontmatter `name` and
`description` drive discovery the same way. Run Claude Code from the repository
root (or a descendant) so the project skills and `AGENTS.md`/`CLAUDE.md` are
picked up.

## Bundle contents

```text
AGENTS.md
.agent/PLANS.md
.agents/skills/
  spec-roadmap/
  phase-planner/
  phase-workflow/
  phase-behavior-contract/
  phase-verification/
  phase-implementer/
  phase-closeout/
docs/implementation/
  README.md
  ROADMAP.md
  TRACEABILITY.md
  templates/
scripts/validate_workflow_bundle.py
USAGE.md
```

## Important limitation

The supplied `AGENTS.md`, roadmap, traceability file, and planning standard are generic starting points. Codex should inspect and reconcile them with the actual repository, commands, architecture, and existing instructions before implementation.
