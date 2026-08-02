#!/usr/bin/env python3
"""Validate the structure and basic frontmatter of the phased-workflow bundle."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "AGENTS.md",
    ".agent/PLANS.md",
    "USAGE.md",
    "docs/implementation/ROADMAP.md",
    "docs/implementation/TRACEABILITY.md",
    "docs/implementation/templates/phase-execplan-template.md",
    "docs/implementation/templates/scenario-template.md",
    "docs/implementation/templates/verification-matrix-template.md",
]
REQUIRED_SKILLS = {
    "spec-roadmap",
    "phase-planner",
    "phase-workflow",
    "phase-behavior-contract",
    "phase-verification",
    "phase-implementer",
    "phase-closeout",
}


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError("missing YAML frontmatter")
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"Missing required file: {rel}")

    skill_root = ROOT / ".agents" / "skills"
    actual_skills = {p.name for p in skill_root.iterdir() if p.is_dir()} if skill_root.exists() else set()
    missing_skills = REQUIRED_SKILLS - actual_skills
    if missing_skills:
        errors.append(f"Missing skills: {', '.join(sorted(missing_skills))}")

    for skill in sorted(REQUIRED_SKILLS & actual_skills):
        path = skill_root / skill / "SKILL.md"
        if not path.is_file():
            errors.append(f"Missing SKILL.md: {path.relative_to(ROOT)}")
            continue
        try:
            values = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"Invalid {path.relative_to(ROOT)}: {exc}")
            continue
        if values.get("name") != skill:
            errors.append(f"Skill name mismatch in {path.relative_to(ROOT)}")
        if not values.get("description"):
            errors.append(f"Missing description in {path.relative_to(ROOT)}")

    if errors:
        print("Workflow bundle validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Workflow bundle valid: {len(REQUIRED_SKILLS)} skills and {len(REQUIRED_FILES)} core files checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
