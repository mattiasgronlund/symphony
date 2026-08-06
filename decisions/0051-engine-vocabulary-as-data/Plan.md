# Plan — 0051 The engine token vocabulary as data

## Scope

No `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, or `SPEC.md` edit. The alignment rule this decision mechanizes
already exists as `VCSX-SPEC.md` Section 14 "Alignment with `VCSX-CONTRACT.md`", and the registry is a
*derived view* over the enumerations those documents already fix — adding it changes no requirement.

The specification repository gains `conformance/vcsx/`, a self-contained subtree holding the registry
and its schema.

## Steps

1. **`conformance/vcsx/vocabulary.json` exists and enumerates every token class Section 14 names.**
   Ensure it carries: the operations (Section 4.1) with each one's lifecycle position and read-only
   status; the required lifecycle positions; the proto classes (Section 4.2); the full reason registry
   (Section 4.3) as `(operation, reason, class)` rows; the trigger kinds and the signal and task-state
   event tokens (Section 5.1); the actions (Section 5.2) with the party that effects each; the
   registry-named `need` tokens (Section 8.4); the exit-code mapping (Section 8.3); the result-envelope
   field names (Section 8.2); the execution contexts (Section 3.2); the checkout modes (Section 3.3);
   and the `repo.policy.toml` section names (Section 6). Done when every token class in Section 14's
   list is represented.
2. **Every entry cites the section it is read from.** Ensure the file carries `spec_refs` at the top
   level and per token group, so a reader can resolve any row back to the prose that fixes it. Done
   when no group lacks a citation.
3. **The registry restates no requirement's substance.** Ensure entries carry names and the properties
   the specification fixes about them — a reason's proto class, an operation's lifecycle position, an
   action's effecting party — and not the prose of the rules those properties feed. Done when the file
   contains no normative sentence.
4. **`conformance/vcsx/README.md` defines the schema and the precedence rule.** Ensure it states the
   file's schema, that `VCSX-SPEC.md` governs and the registry is derived, that a disagreement is a bug
   in the registry, and how a consumer is expected to use it (generate or check types; verify the two
   documents spell every token identically). Done when all four are stated.
5. **The Symphony corpus tree is left untouched.** Ensure `conformance/README.md` and
   `conformance/vectors/` are unchanged: the two subtrees derive from different specifications and
   share only a parent directory. Done when the change adds only files under `conformance/vcsx/`.

## Out of scope

- **An engine conformance corpus.** Behavior vectors exercising the matching ladder and the fail-safe
  rules (Sections 5.3–5.4) in decision 0046's shape are the natural successor and need their own
  derivation work. This decision publishes the vocabulary; vectors over it are a separate slice.
- **A checker in this repository.** Whether the two documents are verified against the registry by a
  script here, or only by the engine repository consuming it, is left open; the artifact is what both
  approaches need first.
- **Making the registry normative.** `VCSX-SPEC.md` governs. Elevating the registry would make it a
  second specification, which `Background.md` names as the reconsideration trigger, not the goal.

## Cross-cutting sync

None. No token is added, renamed, or removed, so `VCSX-SPEC.md` Section 14's alignment rule is
satisfied by construction: the registry is populated *from* the two documents as they stand.

## Anchor changes

None. `conformance/vcsx/vocabulary.json` and `conformance/vcsx/README.md` are new files.

## Status

Applied — `conformance/vcsx/vocabulary.json` and `conformance/vcsx/README.md` are created; no
specification edit required.
