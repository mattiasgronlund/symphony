# Plan — 0071 The Symphony token vocabulary as data

## Scope

New file `conformance/vocabulary.json`, beside the existing Symphony corpus (`conformance/README.md`,
`conformance/vectors/`).

`conformance/README.md` gains the registry's standing, precedence, schema, slice contents and
deferred groups, and is retitled from a corpus-only document to one covering two artifacts — the
shape `conformance/vcsx/README.md` already has.

`SPEC.md`: `Emitted Runtime Events (Upstream to Orchestrator)` (Section 10.4) gains the
exhaustiveness ruling, and the preamble of `Test and Validation Matrix` (Section 17) gains the
registry and its precedence rule.

`conformance/vcsx/README.md`: one sentence, which distinguished the two trees as "a set of behavior
vectors" versus "a vocabulary registry" — a distinction that stops holding once the parent directory
has a registry too.

No edit to `Logging Conventions` (Section 13.1), `Per-Execution Usage Ledger (OPTIONAL)` (Section
13.6), `State Recovery Classes` (Section 14.3), `Orchestrator Runtime State` (Section 4.1.8),
`Live Session (Agent Session Metadata)` (Section 4.1.6), or `Configuration Schema` (Section 5.3):
each already fixes its tokens normatively, so the registry reads them as they stand. Only Section
10.4 was ambiguous, because it labelled a list Section 10.7 requires an adapter to emit as an
example.

No vector change: the registry is a lookup, not a behavior. `conformance/vectors/config-defaults.json`
exercises `resolve_config_defaults` over fields, not over namespace ownership.

No `VCSX-SPEC.md` or `VCSX-CONTRACT.md` edit, and no change to `conformance/vcsx/vocabulary.json`:
the engine's registry derives from a different specification and gains no token here.

No `CONFORMANCE-STATEMENT-TEMPLATE.md` edit: its rows are obligations, not tokens. The registry
supplies data a Statement author reads (the recovery-class defaults, the namespace column); it does
not change what the Statement must record.

## Steps

1. **Section 10.4's list is ruled open, its names fixed.** Ensure
   `Emitted Runtime Events (Upstream to Orchestrator)` introduces its list without "for example", and
   carries a `Note:` stating (a) the list is not exhaustive — an adapter MAY emit additional events
   for conditions this specification does not name, and a consumer MUST tolerate an unrecognized
   event name rather than failing the turn or the session — and (b) the names are fixed for the
   conditions they do name, which is what Section 10.7's requirement that each adapter emit the
   neutral event vocabulary means in practice, citing the consumers that key on the spellings (turn
   processing, Section 10.3; the live session's `last_event`, Section 4.1.6; the ledger's
   `source_event`, Section 13.6). Done when Sections 10.4 and 10.7 can both be read literally, and a
   generator knows whether to close the enum.
2. **The registry exists and carries the named token sets.** Ensure `conformance/vocabulary.json`
   exists carrying, at minimum, the emitted events (Section 10.4), the REQUIRED log context fields
   (Section 13.1), the usage-ledger entry fields and their key (Section 13.6), and the state recovery
   classes (Section 14.3). Done when each of the four sets the issue names is readable as data.
3. **The slice also carries what those sets are defined in terms of.** Ensure the file carries the
   event envelope fields (Section 10.4), the neutral token-usage record (Sections 4.1.6, 10.7, 13.5),
   the per-field recovery-class assignments (Sections 4.1.8, 14.3), and the configuration namespaces
   with the artifact each belongs to (Sections 5.3, 5.6, 18.2, and the extension section owning each
   key). Done when a Conformance Statement author can fill the recovery-class table's "Spec default"
   column and the extensions table's namespace column from the registry.
4. **Every group cites the sections it is read from.** Ensure the file carries `spec_refs` at the top
   level and per group, so any entry resolves back to the prose that fixes it. Done when no group
   lacks a citation.
5. **The registry restates no requirement's substance.** Ensure entries carry names and the
   properties the specification fixes about them — a ledger field's type and REQUIRED-ness, a
   runtime-state field's recovery class, a namespace's owning artifact — and not the prose of the
   rules those properties feed. Done when the file contains no normative sentence.
6. **Open sets say so in data.** Ensure the groups the specification leaves open carry
   `exhaustive: false` with a note naming the clause that opens them — `events` (Section 10.4, per
   Step 1) and `config_namespaces` (Section 5.3's allowance for extensions to define additional
   top-level keys). Done when a generator can tell from the file alone which enums must admit an
   unknown token.
7. **`conformance/README.md` documents the registry and the precedence rule.** Ensure it introduces
   the directory as two artifacts with different jobs, and carries the registry's standing
   (`SPEC.md` governs, the file is derived, a disagreement is a bug here, and a property the prose
   does not fix is the signal to move the concept into `SPEC.md` and re-derive), its schema including
   `exhaustive`, `key` and the `artifact` values used by `config_namespaces`, how an implementation,
   a reviewer and a Statement author each use it, what the slice covers, and which token sets are
   deferred with the reason for each. Done when all of those are stated and the vector-corpus
   material below is unchanged in substance.
8. **`SPEC.md` names the registry and its standing.** Ensure the preamble of
   `Test and Validation Matrix`, after the existing vector-corpus paragraph, states that the token
   sets this specification names are published beside that corpus as a token registry so an
   implementation can generate or check its spellings instead of transcribing them, and that the
   registry is a derived view — this specification governs, it restates no requirement's substance,
   and a disagreement between them is a defect in the registry. Done when an implementer reading only
   `SPEC.md` learns the registry exists and may not treat it as normative.
9. **The engine README's distinguishing sentence is corrected.** Ensure
   `conformance/vcsx/README.md` no longer distinguishes the two trees as "a set of behavior vectors"
   versus "a vocabulary registry", and instead records that the parent directory carries a registry
   of its own on the same terms and that the two are not merged, for the reason the vector corpora
   are not. Done when no sentence in the repository claims Symphony has no registry.
10. **The findings authoring surfaced are recorded, not fixed.** Ensure `conformance/README.md`'s
    "Surfaced findings" carries, as open items: Section 5.3's top-level key list omitting `vcs`,
    which Section 6.4 documents; and Section 13.8 placing `server.*` in `WORKFLOW.md` front matter
    against Section 5's rule for settings executed with host access. Done when the registry's entries
    for both are traceable to a recorded finding rather than to a judgement call.

## Cross-cutting sync

- `SPEC.md` Section 6.4 "Core Config Fields Summary (Cheat Sheet)": no change — the registry adds no
  config field. The `observability.*` entries are decision 0069's.
- `SPEC.md` Section 17 "Test and Validation Matrix": changed by Step 8 (preamble only; no check is
  added, removed, or reworded).
- `SPEC.md` Section 18 "Implementation Checklist": no change. Running the corpus is RECOMMENDED, not
  REQUIRED (Section 17's preamble), and checking against the registry is likewise not a conformance
  condition — an implementation that spells the tokens correctly by hand conforms.
- `conformance/README.md` (Steps 7, 10) and `conformance/vcsx/README.md` (Step 9).

## Anchor changes

None removed or renamed. Added: `conformance/vocabulary.json` (a new file). Section 10.4's list keeps
every token it had; only its lead-in and the new `Note:` change.

## Out of scope

- **A Section 14-style alignment rule for `SPEC.md`.** The engine has one and Symphony does not; the
  registry stands on Section 17's precedence paragraph instead. Writing such a rule is a larger
  change with its own scope (which documents does it bind?) and is named in `Background.md` as a
  reconsideration trigger.
- **The deferred token sets** — error and category codes (Sections 5.5, 10.6, 10.8, 11.4),
  orchestration states and transition triggers (Sections 7.1, 7.3, 11.6), failure classes (Section
  14.1), and the RECOMMENDED snapshot and API shapes (Sections 13.3, 13.8.2). Each is recorded in
  `conformance/README.md` with its reason; several need a per-entry REQUIRED/RECOMMENDED distinction
  the schema does not yet carry.
- **A checker in this repository.** Whether `SPEC.md` is verified against the registry by a script
  here, or only by each implementation consuming it, is left open — as it was for the engine.
- **Fixing the two surfaced findings.** Recorded under Step 10; each needs its own decision.

## Status

Applied — `conformance/vocabulary.json` created; `conformance/README.md`,
`conformance/vcsx/README.md`, and `SPEC.md` (Sections 10.4, 17) updated.
