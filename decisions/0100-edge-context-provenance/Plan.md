# Plan — 0100 An edge does not declare its execution context

## Scope

`VCSX-SPEC.md`: Section 6.5 `[policy]` Edges (the declaration is removed and replaced by the
derivation rule), Section 3.2 "Execution Contexts (Trust)" (an operation's side of the boundary is
distinguished from an edge's context), Section 11 "Security and Trust Model" and Section 13.1's
`provision` and policy-edge rows (the guarantee is restated over a tagged edge rather than a declared
one), Section 13.2's checklist.

`VCSX-CONTRACT.md`: the `[hooks.engine.<name>]` bullet already states the rule for hooks; it gains
the edge.

`conformance/vcsx/vocabulary.json`: `execution_contexts` gains a note saying where a context comes
from. No entry is removed — both tokens survive; only their source changes.

`conformance/vcsx/vectors/match-edge.json`: two vectors carry `"context": "in_sandbox"` on an edge.

`SPEC.md`: no change. It names neither `host_side` nor `in_sandbox` (`grep -c 'host_side\|in_sandbox'
SPEC.md` → 0) and reaches the split through Section 15.4's artifact sourcing, which this decision
does not alter.

## Steps

1. **`[policy]` Edges — the `context` key is gone from the edge description.** Ensure the sentence
   beginning "Each edge binds a trigger to an action" names only `from` as OPTIONAL and no longer
   contains the parenthetical "defaulted per the action". Done-condition: the string `defaulted per
   the action` does not appear in `VCSX-SPEC.md`.

2. **`[policy]` Edges — the derivation rule is stated.** Ensure Section 6.5 carries a short passage,
   in the shape Section 6.6 uses for hooks, establishing that: an edge does not declare its execution
   context; the artifact it is declared in fixes it, so an edge in `repo.policy.toml` is host-side and
   one in the consumer's in-sandbox artifact is in-sandbox; the engine still receives one per edge
   because it is handed one merged surface and never sees two artifacts (Section 3.2), the consumer
   tagging each edge as it tags each hook; and that deriving it removes a combination the declared
   form admitted — a working-tree edge declaring `host_side` and drawing a credential. Done-condition:
   Section 6.5 states the artifact rule and cross-references Sections 3.2 and 6.6.

3. **`[policy]` Edges — a stale `context` is ignored.** Ensure Section 6.5 states that a `context` key
   on an edge is ignored under Section 6.1's unknown-key rule rather than refused. Done-condition: the
   sentence exists and names Section 6.1; no new row appears in Section 6.11's table.

4. **The worked example carries no `context`.** Ensure no `[[policy.edge]]` example in Section 6.5
   shows a `context` key, and that the existing comment on the `run` edge ("its context follows the
   artifact that declares it") reads correctly now that the same is true of the edge itself.
   Done-condition: `grep -n 'context' VCSX-SPEC.md` shows no occurrence inside a `[[policy.edge]]`
   block.

5. **Execution Contexts (Trust) — an operation's side of the boundary is not an edge's context.**
   Ensure Section 3.2 distinguishes the two: its host-side/in-sandbox lists say which operations reach
   the remote or hold credentials, and an edge's or hook's context comes from the artifact that
   declared it. Ensure it states the interaction — an in-sandbox edge dispatching an operation that
   needs a credential receives none, so the operation reports its own failure (Sections 4.3, 11).
   Done-condition: Section 3.2 no longer reads as assigning a context to an edge by the operation it
   dispatches, and Section 9.1's "realize the version-control operations Section 3.2 places host-side"
   remains true.

6. **Section 11 — the guarantee is restated over a tagged edge.** Ensure the bullet beginning "The
   engine labels every policy edge and hook with its execution context" says that the context comes
   from the artifact each was declared in and is tagged by the consumer while assembling the merged
   surface, and that "An in-sandbox edge or hook MUST NOT receive credentials" survives verbatim.
   Done-condition: the MUST NOT is unchanged and no sentence in Section 11 implies an edge declares
   its own context.

7. **Section 13.1 — the matrix row.** Ensure the `provision` row's clause reading "an edge declared
   `in_sandbox` receives no credential whatever it dispatches, `provision` included" no longer says
   *declared*, and ensure the policy-schema rows assert the new rule: an edge's context follows its
   artifact, and a `context` key on an edge is ignored rather than refused. Done-condition: the string
   `an edge declared` does not appear in `VCSX-SPEC.md`.

8. **Section 13.2 — the checklist.** Ensure the checklist item covering hook context also covers the
   edge, so an implementer reads one rule for both. Done-condition: the checklist names the artifact
   as the source of an edge's context.

9. **`VCSX-CONTRACT.md`.** Ensure the bullet stating "A hook declares no execution context: the
   artifact it is declared in fixes that" covers the policy edges named in the same bullet.
   Done-condition: the contract states the rule for both objects in one sentence.

10. **`conformance/vcsx/vocabulary.json`.** Ensure `execution_contexts` carries a `note` recording
    that a context is not declared in the policy document — it is fixed by the artifact an edge or
    hook was declared in and tagged by the consumer. Done-condition: the note exists and the two
    entries are unchanged.

11. **`conformance/vcsx/vectors/match-edge.json`.** Ensure no vector's `edges` entry carries a
    `context` key, and add one vector asserting that an edge carrying one still matches — the key is
    ignored, not refused. Done-condition: `python3 -c "import json; d =
    json.load(open('conformance/vcsx/vectors/match-edge.json')); print(sum('\"context\"' in
    json.dumps(v.get('given', {}).get('edges', [])) for v in d['vectors']))"` reports only the
    ignore-vector.

## Cross-cutting sync

Section 13.1 (test matrix) and Section 13.2 (checklist) are covered by steps 7 and 8. Section 6.4 is
untouched by this decision — the config cheat sheet this repository's `CLAUDE.md` names is `SPEC.md`'s,
and `SPEC.md` carries no edge-context key. Section 13.3 gains nothing: this decision removes a
choice rather than delegating one.

## Anchor changes

- `[policy]` edge key `context` — **removed**. An edge's execution context is no longer declared;
  it is fixed by the artifact the edge is declared in (Sections 3.2, 6.5). A document still carrying
  the key has it ignored (Section 6.1). The `host_side` / `in_sandbox` tokens themselves are
  unchanged and still name the two contexts.

## Status

Applied to `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `conformance/vcsx/vocabulary.json` and
`conformance/vcsx/vectors/match-edge.json`.
