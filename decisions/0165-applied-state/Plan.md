# Plan — 0165 A decision State that says whether the text landed

## Scope

`DECISIONS.md` only — the States legend and the `**State:**` line of every chapter. `CLAUDE.md`
mirrors the legend and moves with it.

No change to `SPEC.md`, `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, the conformance corpus, or either
Conformance Statement template. This decision adds no `Implementation-defined` or "MUST document"
obligation, so no Statement template row is owed.

## Steps

1. **The States legend enumerates five states.** Ensure `DECISIONS.md`'s `**States:**` paragraph
   defines `Applied` alongside `Proposed`, `Accepted`, `Rejected` and `Superseded`, with `Accepted`
   narrowed to a decision whose normative text is **not yet** reachable from `main`, and `Applied`
   meaning the decision is settled and its text **is** reachable from `main`.
   Done when the legend names five states and the word "Applied" appears in it.

2. **The legend states who flips it and when.** Ensure the legend says the pull request that lands a
   decision's normative text is the one that moves its State from `Accepted` to `Applied`, so the
   field and the text change in the same commit.
   Done when the legend contains that obligation.

3. **The legend states the fail-safe reading.** Ensure the legend says a chapter reading `Accepted`
   is a claim that upstream closed the question and **not** a claim about what the specification
   says, so a consumer reads the pinned tree rather than the State for the latter.
   Done when the legend contains that sentence.

4. **A decision needing no specification edit is `Applied` on acceptance.** Ensure the legend says
   so, since such a decision has no text to land and would otherwise sit at `Accepted` forever.
   Done when the legend covers the case.

5. **Backfill.** Ensure every chapter whose State was `Accepted` before this decision, and whose
   normative text is present in the tree at `5a69193`, reads `Applied`. The four `Superseded`
   chapters (0005, 0026, 0062, 0067) and the one `Proposed` chapter (0025) are unchanged.
   Done when `grep -c '^\*\*State:\*\* Applied' DECISIONS.md` is 159, `Accepted` is 0, `Superseded`
   is 4 and `Proposed` is 1, totalling 164.

6. **`CLAUDE.md`'s mirror matches.** Ensure the decision-log section's parenthetical state list
   enumerates the same five states.
   Done when `CLAUDE.md` names `Applied`.

7. **The birth value is stated where a chapter is authored.** Ensure `DECISIONS.md`'s
   new-decision paragraph states that a chapter is born `Accepted`, that only its apply pull request
   may write `Applied`, and that copying a neighbouring chapter's `State` is the specific way to get
   it wrong — with the one exception, a decision needing no specification edit, which its own text
   must say. Added in review; see the Review finding section of `Background.md`.
   Done when the paragraph names the birth value and the copying hazard.

## Backfill resolution

`Plan.md`'s `## Status` was the seed; 150 of 164 read an unambiguous `Applied…` and carry over
directly. The other 14 were resolved against the tree at `5a69193`, recorded here because they are
judgements rather than reads:

| Decision | `Plan.md` `## Status` said | Resolved | Evidence at `5a69193` |
|---|---|---|---|
| 0010 | Applied (working tree; not yet committed) | `Applied` | Section 14.3 `State Recovery Classes` |
| 0011 | Applied (working tree; not yet committed) | `Applied` | Section 4.1.8 `Orchestrator Runtime State`; Section 13.6 usage ledger |
| 0012 | Applied (working tree; not yet committed) | `Applied` | Section 8.8 `Token Budget Guards (OPTIONAL)` |
| 0013 | Applied (working tree; not yet committed) | `Applied` | Section 8.9 `Provider Quota Backpressure (OPTIONAL)` |
| 0025 | Not started — Proposed | `Proposed` (unchanged) | No option selected; no specification change |
| 0026 | Superseded by 0030 | `Superseded` (unchanged) | — |
| 0027 | `application not started` | `Applied` | Section 3.4 `Layers, the VCS Engine, and Deployment Topologies` |
| 0028 | `application not started` | `Applied` | `VCSX-CONTRACT.md` exists; Section 3.4 defers to it |
| 0029 | `application not started` | `Applied` | Section 5.6 `` `repo.policy.toml` (Repository Way of Working) `` |
| 0030 | `application not started` | `Applied` | Section 9.12 `The Action-Policy Machine`; `grep -c 'action-policy machine' SPEC.md` → 8 |
| 0031 | `application not started` | `Applied` | Section 8.10 `Autonomous Task Management (OPTIONAL)` |
| 0032 | `application not started` | `Applied` | `grep -c 'pr_to_squash' SPEC.md` → 3 |
| 0033 | Accepted and applied | `Applied` | The legend enumerates `Superseded` |
| 0046 | Steps 1–3 applied | `Applied` | First corpus slice landed; `conformance/vectors/` holds 16 files |

Six of these — 0027 through 0032 — had a `Plan.md` `## Status` reading `application not started`
for text that is demonstrably in `SPEC.md`. That drift is the measurement `Background.md` argues
from, and it is why the backfill was not taken from `Plan.md` alone.

Note on 0046: its `## Status` describes the first slice only, and later slices added files under the
same decision's heading. It is recorded `Applied` because the text the decision asked for is in the
tree; a decision whose scope grows across slices is not the case this State is trying to express.

## Cross-cutting sync

None in `SPEC.md` — this decision does not touch it, so Sections 6.4, 17 and 18 are unaffected.
`CLAUDE.md`'s legend mirror is covered by step 6.

## Anchor changes

None. No code-token identifier or section title is renamed or removed. `Applied` is a new value of
an existing field, not a rename of an existing one.

## Status

Applied to `DECISIONS.md` (States legend, the new-decision authoring paragraph, and all 164
chapters' `**State:**` lines) and `CLAUDE.md` (the decision-log legend mirror). Step 7 was added in
review, after `symphony-rs` observed that the backfill left no live `Accepted` for an author to copy.
