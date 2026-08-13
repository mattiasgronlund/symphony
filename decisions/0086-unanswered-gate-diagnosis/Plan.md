# Plan — 0086 An unanswered gate's condition is named, and the three conditions are tokens

## Scope

`VCSX-SPEC.md`: Sections 6.6 "`[hooks]`", 8.2 "Result Envelope", 13.1 "Test Matrix", 13.2
"Implementation Checklist", 13.3 "Conformance Statement". `conformance/vcsx/vocabulary.json`.

No `VCSX-CONTRACT.md` change: the result envelope and the keys inside `outputs` are deferred to this
document (`VCSX-CONTRACT.md` Section 11), and no token this decision adds is spelled there.

## Steps

1. **The three condition tokens (Section 6.6)** — ensure the section that divides what exceeding a
   hook bound produces names the three conditions as tokens: `bound_elapsed` (the unit was still
   running when the bound elapsed and was stopped), `not_started` (the engine could not start the
   unit), `answer_unreadable` (the unit answered and the engine could not read the answer in the form
   it fixed). Ensure the paragraph states that the condition is reported for every hook that gave the
   engine no usable answer, on either side of the division, and that the tokens diagnose rather than
   route — the repair being the same shape in each case is why Section 4.3 spends one reason on all
   three. *Done when* the three tokens appear in Section 6.6 with a gloss each, and the
   routes-versus-diagnoses boundary is stated without contradicting Section 4.3.

2. **`unfinished_hooks` reads the tokens (Section 8.2)** — ensure the `unfinished_hooks` description
   names its fields as `hook`, `trigger` and `condition`, with `condition` carrying one of the three
   Section 6.6 tokens rather than prose. Preserve the absent-or-empty rule.
   *Done when* the key's `condition` field cites the token set instead of describing it.

3. **`unanswered_gates` (Section 8.2)** — ensure `outputs` carries `unanswered_gates`: an array, each
   entry naming the `hook`, the `position` that ran it, the `condition` (the same three tokens), and
   an `Implementation-defined` `detail`; absent or empty where every gate answered. Ensure the prose
   states why it is an array — the result re-enters the machine, so a traversal that routes past one
   unanswered gate can reach another (Section 5.6) — and keeps the existing "the reason routes and the
   condition diagnoses" boundary against `hook_unanswered`.
   *Done when* the key exists with its fields, its absent-or-empty rule, and the array rationale.

4. **The two halves spell it identically (Section 8.2)** — ensure the section states that both keys
   carry the same three condition tokens, so one consumer branch reads both halves.
   *Done when* the sentence exists and names no third spelling.

## Cross-cutting sync

- **Test matrix (Section 13.1)**, under "Gate blocking" — a `before:<op>` hook that gave the engine no
  usable answer yields `<op>:hook_unanswered` and names its condition in `unanswered_gates` with one of
  the three tokens; a result-triggered hook in the same condition is reported in `unfinished_hooks`
  with the same token set and does not block; a traversal that passes two unanswered gates reports
  both entries rather than the last.
- **Implementation checklist (Section 13.2)** — extend the invocation-contract line with the two
  `outputs` keys and the shared condition tokens.
- **Conformance Statement (Section 13.3)** — add the `detail` field of an `unanswered_gates` entry to
  the enumerated `Implementation-defined` resolutions, beside the escalation `detail` (Section 8.4).
- **`conformance/vcsx/vocabulary.json`** — add a `hook_conditions` group with the three tokens and
  their meanings, and an `output_keys` group naming `unperformed_intents`, `unfinished_hooks` and
  `unanswered_gates` with the fields each entry carries.
- **No vector.** What a hook bound produces is observed by running a unit that does not answer, which
  is the reasoning `conformance/vcsx/README.md` already records for decision 0081's half of this: the
  tokens are in `vocabulary.json` and the behavior needs a live hook.

## Anchor changes

New code tokens: `bound_elapsed`, `not_started`, `answer_unreadable`, `unanswered_gates`. No existing
anchor is renamed or removed; `unfinished_hooks` keeps its name, its meaning and its absent-or-empty
rule, and gains named fields for what its prose already described.

## Status

Applied to `VCSX-SPEC.md`.
