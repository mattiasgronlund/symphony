# Plan — 0153 A resume continues the flow, and the token carries the root trigger

## Scope

- `VCSX-SPEC.md` — Section 5.5 (Escalation Binding), Section 8.2 (Result Envelope), Section 8.1
  (Entry Points and Arguments), Section 12.2 (`ship` Sequence), Section 12.3 (`land` Sequence),
  Section 13.1 (Test Matrix), Section 13.2 (Implementation Checklist).
- `VCSX-CONTRACT.md` — Section 5.6's resume paragraph carries the same silence.
- `conformance/vcsx/vocabulary.json` — the `output_keys` entry for `resume_token`, and the
  `arguments` entry for `resume`, whose note carries Section 8.1's bullet almost verbatim.
- `conformance/vcsx/vectors/` — no two-invocation harness; see step 8. Decision 0142's
  `conformance/vcsx/vectors/resume-precondition.json` restates Section 8.1's re-entry phrasing in
  its `notes` and in one vector's description; see step 10.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — no new row expected; the token's **form** row already
  exists and decision 0142 narrows it. Check rather than assume (see Cross-cutting sync).
- `SPEC.md` and Symphony's artifacts — no change. Symphony supplies no `resume` today.

## Steps

1. **`VCSX-SPEC.md` Section 5.5 — a resume continues the flow.** Ensure the section states what
   happens **after** the re-entry produces a result: the result is disposed of by Section 5.4 as any
   result is, and the flow continues from where the re-entered dispatch sat. Ensure the
   single-operation case is obtained as a **consequence** rather than as a case — for a
   bare-operation entry point the remainder of the flow is empty, so the invocation reports the
   result and ends — and that a driver composing its own sequence out of bare operations gets that
   behaviour for the same reason, its sequence being the driver's and not the engine's. *Done when:*
   a resumed `ship` that re-dispatches `integrate` successfully has a stated continuation, and the
   bare-operation behaviour is written down rather than left to be inferred from an empty remainder.
2. **`VCSX-SPEC.md` Section 5.5 — the token carries three things, not two.** Ensure the sentence
   quoted as "it carries the point to re-enter and the flow bound already spent" enumerates three:
   the operation or lifecycle position to re-enter; the **root trigger** — the result of the
   sequence's own `run_op` that the chain the point belongs to descends from (decision 0143) — where
   the point is not that dispatch itself; and the count. Ensure the field is stated as the **root**
   rather than over substitution — as the trigger an edge replaced — so it is present on the
   built-in path where no edge fired: `VCSX-SPEC.md` Section 12.2 routes `push:non_fast_forward` to
   `integrate` itself and escalates `integrate:merge_conflicts`, and a resumed `integrate` there
   needs the root to know its landing is the push retry. Ensure the field is stated as unneeded
   where the point is a lifecycle position, the gated operation's own result being the root. Ensure
   the `MUST NOT` over `expected_worktree`, `expected_head` and anything else a position established
   is **untouched**, and that the reason it still holds is available: a trigger is control-flow
   state of the same kind as the count, not something a position inspected. *Done when:* the token's
   contents determine a continuation for every shape Section 12.2 and Section 12.3 can produce, and
   nothing a position established has been admitted.
3. **`VCSX-SPEC.md` Section 5.5 or Section 8.2 — the token is fixed-width, and the trigger is
   spelled by its registry token.** Ensure one sentence states that each of the three parts is
   fixed-width and none grows with the policy graph — `VCSX-SPEC.md` Section 5.4's tail-replacement
   means a chain of any length descends from one root — so a phrase naming a point in the flow
   cannot be read as licence for a serialized traversal. Ensure the trigger is stated to be carried
   by its registry token (`VCSX-SPEC.md` Sections 5.1 and 4.3) rather than by an ordinal into any
   generated enumeration, with the reason: an ordinal decodes into a different trigger after a MINOR
   insert shifts it, silently, from a record that still looks valid. *Done when:* both properties
   are stated where an implementer meets the token's contents, and neither reads as advice.
4. **`VCSX-SPEC.md` Section 8.2 — the envelope bullet matches.** In `VCSX-SPEC.md` Section 8.2, the
   `resume_token` bullet describes the value twice — as "an opaque token naming the point that
   raised the need and the flow bound already spent", and in its closing sentence as "The token
   carries the point and the count and nothing a lifecycle position established". Ensure **both**
   enumerate the three parts step 2 gives Section 5.5. Ensure the presence rule — absent where
   `status` is not `needs_caller`, absent for the two holds — is unchanged. *Done when:* the two
   sections describe one object, and no description in either still enumerates two parts.
5. **`VCSX-SPEC.md` Section 8.1 — the `resume` argument's description follows.** Ensure the bullet
   quoted as "Supplied, the invocation re-enters the point that raised the need rather than
   beginning at its entry point, and the flow bound continues from the count the token carries" says
   that the flow then continues rather than that the invocation ends at the re-entered point. Ensure
   the opacity paragraph is **kept as written** — it argues against publishing a traversal schema,
   which the trigger encoding avoids rather than incurs — and that the refusal sentence decision
   0142 extends is untouched. *Done when:* Section 8.1 and Section 5.5 agree on what a supplied
   `resume` does after the re-entry.
6. **`VCSX-SPEC.md` Sections 12.2 and 12.3 — the sequences show the continuation.** Ensure each
   sequence's pseudocode makes a resumed entry visible rather than leaving "continue" to be
   inferred: the sequence is entered at the point the token names, with the root trigger selecting
   the control transfer per decision 0143. Ensure the shape agrees with decision 0143's rule rather
   than restating it — the transfer is the trigger's, pinned to the sequence's own `run_op` — and
   that no second spelling of a sequence position is introduced. *Done when:* an implementer can
   read a resumed `ship` off Section 12.2 without inventing an enumeration of sequence points, and
   the answer agrees with the un-resumed case.
7. **`VCSX-SPEC.md` Sections 13.1 and 13.2 — the Resuming row describes the continuation.** Ensure
   the Resuming row in `VCSX-SPEC.md` Section 13.1, which today describes the re-entry and never
   what follows it, states that a resumed front-end continues its sequence — a resolved
   `resolve_conflicts` under `ship` reaching the pull request in the resuming invocation rather than
   requiring a fresh one — and that the accumulated count therefore survives into it, which is what
   makes that row's existing clause "a resolver that resolves every time reaches `flow_exhausted`
   **across invocations** and not only within one" true for the interactive front-end as well as for
   a driver. Ensure `VCSX-SPEC.md` Section 13.2 gains the matching line. *Done when:* the row's
   existing across-invocations claim is supported by a stated continuation rather than contradicted
   by an unstated stop.
8. **`VCSX-CONTRACT.md` — the contract carries the same silence.** In `VCSX-CONTRACT.md` Section
   5.6, the paragraph beginning "A resume re-enters the point that raised the need, and it
   round-trips through the consumer" describes the re-entry and the accumulating bound and stops
   there — the same omission this decision repairs one document up. Ensure it states the
   continuation in the contract's own register, without duplicating `VCSX-SPEC.md`'s token
   enumeration, which the contract deliberately does not carry. *Done when:* a reader of the
   contract alone knows whether a resumed front-end reports the re-entered result or continues its
   sequence. This site was found by `python3 scripts/check_plan_anchors.py` against an earlier draft
   that named only `VCSX-SPEC.md` and the registry.
9. **`conformance/vcsx/vocabulary.json` — the registry notes move with the sections, and there are
   two.** Ensure the `output_keys` entry for `resume_token`, whose `meaning` restates "It carries
   the point and the count and nothing a lifecycle position established", enumerates the same three
   parts. Ensure the `arguments` entry for `resume` follows step 5 as well as step 2: its note
   carries Section 8.1's bullet almost verbatim — "the invocation re-enters the point that raised
   the need rather than beginning at its entry point, and the flow bound continues from the count
   the token carries" — so the sentence step 5 edits has a twin in the registry, and an edit
   addressed to the section alone leaves the registry asserting what the section no longer says.
   Decision 0142 wrote that entry after this plan was drafted, which is why the first draft named
   `output_keys` and nothing else. *Done when:* both entries are checked, the registry asserts
   nothing the specification no longer says — decision 0132's drift class — and `python3
   scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.
10. **`conformance/vcsx/vectors/resume-precondition.json` — the argument survives, and is confirmed
    rather than assumed.** Decision 0142 created this file after this plan was drafted. Its `notes`
    and its `land_token_resumed_at_an_awaiting_land_is_established` vector both reason, citing
    Section 8.1, from "A resume re-enters the point rather than beginning at the entry point", and
    conclude that "the branch ahead of the re-entered point is never run". That reasoning survives
    this decision: the continuation step 1 states runs **forward** from the re-entered point, so a
    branch ahead of it is still never reached and the vector's expectation is unchanged. Ensure the
    paraphrase still matches Section 8.1 once step 5 has edited it. Ensure no vector changes: the
    token's third part is not among the four conditions this file exercises, so its `notes` clause
    "no vector inputs the point the token names — no condition here reads it" stays true with a
    root trigger in the token. *Done when:* the file has been re-read against the edited Section
    8.1 rather than left as a twin nobody opened, and any expectation that does move is a
    deliberate change this step names.

## Cross-cutting sync

- `VCSX-SPEC.md` Sections 13.1 and 13.2: step 7.
- `VCSX-CONTRACT.md` Section 5.6: step 8. The contract restates the resume in its own words and
  carries the same silence; it was not in this plan's first draft.
- `conformance/vcsx/vocabulary.json`: step 9, and it is **two** entries rather than one —
  `output_keys` and `arguments`. This is the derived artifact most easily missed, because the notes
  restate a specification sentence in their own words rather than citing it, and because the second
  entry did not exist when this plan was first drafted.
- `conformance/vcsx/vectors/resume-precondition.json`: step 10. Confirmed unchanged rather than
  assumed unchanged.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 3 and `VCSX-SPEC.md` Section 13.3: the existing
  row asks for the **form** of the `resume_token`. This decision changes what the token carries, not
  whether the form is `Implementation-defined`, so no row is expected to be owed — but check it in
  the same commit, and if any new `Implementation-defined` or MUST-document sentence appears, its
  row goes with it (`CLAUDE.md`, decision 0128).
- `SPEC.md` Sections 6.4, 17, 18: no change.

## Ordering

- **After decision 0143.** That decision defines the landing point and the
  disposition/control-transfer split; the token's third field is its root, and without it step 1's
  continuation — the flow resuming from where the re-entered dispatch sat — points at a concept with
  no definition.
- **Independent of decision 0142 in substance** — that decision withdrew the sequence-selecting
  property and settled its fourth refusal condition on the entry point alone, so neither waits on
  the other.
- **Coupled to decision 0142 in encoding.** This decision adds a part to the token outright; 0142
  requires it to answer which entry point issued it, which is a part in any engine whose point
  encoding does not already determine that. Landed together that is one format revision; landed
  apart it is two, and a token issued between them decodes on no build that has taken either. 0142
  will plausibly land first, since it orders itself after 0141 while this one waits on 0143 — so
  **both** records now state the coupling rather than leaving it on whichever is applied second
  (raised on the implementation reply to PR #114, against 0142's record for not naming it).

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0153-resume-continues-the-flow/Plan.md --rev
22b5194` reports reach findings at four sites. One is load-bearing and is now step 8 —
`VCSX-CONTRACT.md:217`, where the contract restates the resume and stops at the re-entry exactly as
`VCSX-SPEC.md` does. The other three are benign. Line numbers below are refreshed to `b7912f6`; the
assessments are the original ones and are unchanged.

- `VCSX-SPEC.md:2440` (Section 8.6) carries "beginning at its entry", which is the precondition
  section restating Section 8.1's phrasing for a `resume` that is refused. Nothing there turns on
  what follows the re-entry.
- `VCSX-SPEC.md:866` (Section 5.6) carries "continues from the count", which is the flow-bound
  paragraph this decision cites as its argument rather than edits.
- `conformance/vcsx/vectors/identity-precondition.json:10` carries "entry point and the" in a
  `given`, which is decision 0142's territory rather than this one's.

Re-run at `d78d7af`, after decisions 0140–0146, 0148 and 0152 landed, reported **three** findings.
All three are artifacts decision 0142 wrote after this plan was drafted, and all three are now
named:

- `conformance/vcsx/vocabulary.json:352` (`arguments`) carries "and the flow bound" — in fact the
  whole of Section 8.1's `resume` bullet. This one is **load-bearing** rather than benign: step 5
  edits that bullet, and a registry note repeating it is exactly the drift class step 9 exists to
  prevent. Step 9 now covers both entries rather than `output_keys` alone.
- `conformance/vcsx/vectors/resume-precondition.json:17` (`notes`) and `:102` (`vectors`) carry
  "rather than beginning at". Benign, and step 10 now records that judgement rather than leaving
  the file unopened.

Two silences in the re-run were checked rather than assumed. `conformance/vcsx/vocabulary.json:285`
(`output_keys`) carries the same "and the flow bound" fragment and does not report because step 9
names it. `conformance/vcsx/vectors/identity-precondition.json:10` still carries its fragment and
still does not report, because the list above names it through the group `given` — silence there is
this record working, not the site having gone away.

Re-run again at `b7912f6`, after decisions 0147 and 0149 landed, reports **no** finding from 19
quoted spans, and every address above resolves unchanged. That pair edited `SPEC.md`,
`CONFORMANCE-STATEMENT-TEMPLATE.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` and
`conformance/vocabulary.json`, none of which this plan addresses — each site was re-read at that
revision rather than inferred from the file list.

## Anchor changes

- **Changed:** Section 5.5's token-contents sentence and Section 8.2's `resume_token` bullet go from
  two parts to three; Section 8.1's `resume` bullet states the continuation; Sections 12.2 and 12.3
  show a resumed entry; Section 13.1's Resuming row gains the continuation;
  `conformance/vcsx/vocabulary.json`'s `resume_token` meaning follows.
- **Added:** the root trigger as a token part; the fixed-width statement; the registry-token
  encoding requirement.
- **Removed:** nothing. Section 8.1's opacity paragraph and Section 5.5's `MUST NOT` over
  position-established state both stand unchanged, and the two-part phrasing they sat beside is
  superseded rather than contradicted. Plans quoting "the point and the count" are not edited; they
  record what was true when written.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.5, 8.1, 8.2, 12.2, 12.3, 13.1, 13.2, 13.3), `VCSX-CONTRACT.md`
(Section 5.6), `conformance/vcsx/vocabulary.json` (both the `output_keys` `resume_token` entry and
the `arguments` `resume` entry) and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (the `resume_token`
form row). `SPEC.md`, `CONFORMANCE-STATEMENT-TEMPLATE.md` and `conformance/` outside
`conformance/vcsx/vocabulary.json` are unchanged.

Step 10 resolved as the plan predicted, and the prediction was checked rather than taken:
`conformance/vcsx/vectors/resume-precondition.json` is unedited. Its reasoning turns on "the branch
ahead of the re-entered point is never run", where *ahead* names the prefix — Section 12.3's
`await_first` branch sits before the merge loop, and Section 8.1's own paragraph says so — so a
continuation running forward from the re-entered point still never reaches it. Its `notes` clause
"no vector inputs the point the token names — no condition here reads it" also survives, no
condition reading the root trigger either. Section 8.1's paraphrase was re-read against the edited
bullet and still matches; the edit sharpened the sentence it paraphrases rather than moving it.

Two sites the plan's Cross-cutting sync told this pass to check rather than assume, both hits, and
both the same shape — the token's *contents* had leaked into text describing its *form*, so a
two-part enumeration survived in two places no step named. Neither owed a **new** row, which is what
the plan predicted; each owed an edit to an existing one. `VCSX-SPEC.md` Section 13.3 read "the form
of the `resume_token` — what it encodes", which after this decision reads as licence over contents
the specification now fixes; it is narrowed to name the three parts Section 5.5 fixes and to leave
the engine only their spelling. `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`'s matching row enumerated
the two parts literally in its answer field — `<the point and the spent flow-bound count; …>` —
which is decision 0132's drift class one artifact further out than step 9 reached, and a Statement
generated from it would have published a two-part token under a three-part specification. Both are
edited; the template row's `Section` column gains `5.5`.

No new `Implementation-defined` or MUST-document obligation is created, so no Conformance Statement
row is added (`CLAUDE.md`, decision 0128): the registry-token encoding is a MUST on the engine and
the fixed-width property is a constraint, neither delegating a choice. The consumer-observable half
of the change is Section 13.1's Resuming row; the two properties a consumer cannot observe through
an opaque token — fixed width, registry-token spelling — are stated in Section 13.2 instead, which
is where an obligation an implementer carries and a conformance test cannot reach belongs.

Checks: `python3 scripts/validate_spec_consistency.py` — 0 errors, 0 warnings; `python3
scripts/validate_workflow_bundle.py` — valid; `python3 scripts/check_plan_anchors.py
decisions/0153-resume-continues-the-flow/Plan.md --rev 2cba688` — 0 findings from 19 quoted spans,
before and after the edits.
