# Plan — 0098 The `repo.policy.toml` hook namespace, and per-branch sections

## Scope

`VCSX-SPEC.md`: Sections 5.2 "Actions" (`run`), 6.5 "`[policy]` Edges", 6.6 "`[hooks]`", 6.10
"Validation", 11 "Security and Trust Model", 13.1 "Test Matrix", 13.2 "Implementation Checklist",
plus a new subsection for per-branch sections.

`SPEC.md`: Sections 5.2 "File Format", 5.3 "Configuration Schema" (removing 5.3.4 from it), 5.6
"`repo.policy.toml` (Repository Way of Working)", 6.4 "Configuration Cheat Sheet", 15.4
"Configuration Trust Sourcing and Hook Safety", 17 "Test Matrix", 18 "Implementation Checklist".

`VCSX-CONTRACT.md`: Sections 4, 10.

`conformance/vcsx/vocabulary.json` (`policy_sections`, `config_reasons`),
`conformance/vcsx/vectors/policy-validation.json`, `conformance/vcsx/README.md`.

## Tokens introduced

- `[hooks.engine.<name>]` — replaces `[hooks.<name>]`.
- `[hooks.workspace]` — replaces the bare `hooks.<lifecycle>` keys.
- `[[branch]]` with its `match` table — the per-branch section.
- `duplicate_branch_section` — configuration reason (Section 6.10).

## Tokens removed

- `context` as a key of a hook declaration. It survives as a property the consumer supplies with the
  merged surface, not as something an author writes. Edge `context` is unaffected.

## Steps

1. **Hooks are prefixed (`VCSX-SPEC.md` Section 6.6)** — ensure named engine hooks are declared
   under `[hooks.engine.<name>]`, and that the section states the workspace namespace is the
   consumer's and disjoint from it. *Done when* no example or rule addresses a hook as
   `[hooks.<name>]`.

2. **Context is derived, not declared (`VCSX-SPEC.md` Sections 6.6, 3.2)** — ensure a hook
   declaration carries no `context` key; ensure the section states that a hook's context is fixed by
   the artifact it is declared in, that the consumer supplies it with the merged surface, and that
   the engine still receives one per hook because it is handed one document. Ensure 0095's unit rule
   is restated as a consequence rather than a separate prohibition: a host-side hook's unit cannot
   come from the working tree because a host-side hook is one the working tree did not declare.
   *Done when* `context` appears in no hook example and the engine's per-hook context is still
   stated.

3. **Lifecycle hooks get their own namespace (`SPEC.md` Sections 5.3.4 → 5.6, 6.4)** — ensure the
   lifecycle keys are addressed as `hooks.workspace.after_create` and siblings; ensure the section
   documenting them sits with the repository artifacts rather than inside Section 5.3, which
   declares itself to be about operator config. *Done when* Section 5.3 documents only operator keys
   and the lifecycle hooks are documented where they live.

4. **`WORKFLOW.md` carries both namespaces (`SPEC.md` Section 5.2)** — ensure its front matter may
   declare `hooks.engine.<name>` as well as `hooks.workspace`, both in-sandbox by virtue of the
   artifact. *Done when* the in-sandbox `before:commit` gate can be declared where it is sourced
   from.

5. **`repo.policy.toml` is read from one revision (`SPEC.md` Section 15.4)** — ensure the sentence
   splitting it across two revisions is replaced: host-side hooks are declared in
   `repo.policy.toml` and read from the policy source; the `before:commit` gate is declared in
   `WORKFLOW.md` and read from the worktree. Ensure the edge invoking the gate stays in
   `repo.policy.toml`, so control flow remains trusted while the gate's body is not. *Done when* no
   artifact is read from two revisions.

6. **Per-branch sections (`VCSX-SPEC.md`, new subsection under Section 6)** — ensure a `[[branch]]`
   section carries a `match` table naming exactly one matcher, `prefix` being the one defined;
   ensure the most specific matching section applies with longest prefix winning; ensure a section
   merges over the top level key by key; ensure the top level applies alone where nothing matches,
   so no empty-prefix default is required. *Done when* the resolution is deterministic by
   construction and a later matcher can be added without changing an existing section.

7. **Validation for sections (`VCSX-SPEC.md` Section 6.10)** — ensure two sections with identical
   `match` are `duplicate_branch_section`, and a `match` naming no recognized matcher or more than
   one is `malformed_policy`. *Done when* both rows exist and the reasoning cites Section 5.4's
   refusal of non-determinism.

## Cross-cutting sync

- **`VCSX-CONTRACT.md`** — the `repo.policy.toml` content list names both hook namespaces and the
  per-branch sections; the trust-sourcing section states that a hook's context follows its artifact.
- **`VCSX-SPEC.md` test matrix (Section 13.1)** — a hook declared in `repo.policy.toml` is host-side
  and one in `WORKFLOW.md` is in-sandbox with no key saying so; a `[hooks.engine.<name>]` and a
  `hooks.workspace` key of the same name coexist; the longest matching `[[branch]]` prefix applies
  and merges over the top level; two identical matches are refused; a policy with no matching
  section runs the top level alone.
- **`VCSX-SPEC.md` implementation checklist (Section 13.2)** — both namespaces, derived context, and
  section resolution.
- **`SPEC.md` cheat sheet (Section 6.4)** — the lifecycle keys renamed under `hooks.workspace`.
- **`SPEC.md` test matrix (Section 17)** and **checklist (Section 18)** — the single-revision read
  of `repo.policy.toml`, and the gate declared in `WORKFLOW.md`.
- **`conformance/vcsx/vocabulary.json`** — `policy_sections` gains `[hooks.engine]`,
  `[hooks.workspace]` and `[[branch]]`; `config_reasons` gains `duplicate_branch_section`.
- **`conformance/vcsx/vectors/policy-validation.json`** — every vector declaring a hook moves to the
  new namespace and drops `context`; vectors for section resolution and for the duplicate match.

## Anchor changes

- `[hooks.<name>]` is renamed to **`[hooks.engine.<name>]`**; the bare lifecycle keys move under
  **`[hooks.workspace]`**.
- The hook declaration key **`context` is removed**. It remains a property of the merged surface the
  consumer supplies. Edge `context` is unchanged.
- `SPEC.md` Section 15.4's split of `repo.policy.toml` across two revisions is removed: the
  `before:commit` gate is declared in `WORKFLOW.md`.
- `SPEC.md` Section 5.3.4 moves out of Section 5.3.
- `VCSX-SPEC.md` gains `[[branch]]`, its `match` table, and `duplicate_branch_section`.

## Status

Accepted. Applied to `VCSX-SPEC.md`, `SPEC.md`, `VCSX-CONTRACT.md`,
`conformance/vcsx/vocabulary.json` and `conformance/vcsx/vectors/policy-validation.json`.

Inserting `[[branch]]` as Section 6.10 renumbered Validation from 6.10 to 6.11, and 43 lines of
`VCSX-SPEC.md` plus 34 across the conformance corpus and the Conformance Statement template were
updated with it. The decision log was deliberately left alone: those records describe what the
specification said when they were written, and rewriting their citations would falsify the history
decision 0002 exists to preserve.
