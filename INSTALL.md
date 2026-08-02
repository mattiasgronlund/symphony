# Installation Checklist

1. Extract the archive outside or at the root of the target repository.
2. Back up or commit existing repository instructions and planning files.
3. Copy `.agents/skills/` into the target repository.
4. Merge `AGENTS.md` rather than replacing existing valid instructions.
5. Merge `.agent/PLANS.md` if an ExecPlan standard already exists.
6. Copy missing `docs/implementation/` templates.
7. Add or identify the canonical `SPEC.md`.
8. Run `python3 scripts/validate_workflow_bundle.py`.
9. Start Codex from the repository root.
10. Run `$phase-workflow prepare`.
11. Review and approve phase boundaries before implementation.
