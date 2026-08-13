# Plan — 0084 Every condition gets a home, and one exit code names "no result"

## Scope

`VCSX-SPEC.md`: Sections 6.10 "Validation", 8.1 "Entry Points and Arguments", 8.3 "Exit Codes", 8.6
"Invocation Preconditions", 10.2 "Pull-Request Composition", 13.1 "Test Matrix", 13.2
"Implementation Checklist". `conformance/vcsx/vocabulary.json` and `conformance/vcsx/vectors/`.

No `VCSX-CONTRACT.md` change: the invocation contract, including exit codes, is deferred to this
document (`VCSX-CONTRACT.md` Section 11).

## Steps

1. **`template_unbound` (Section 6.10)** — ensure the validation table carries a row for
   `body_source = "template"` (Section 10.2) with no template unit bound, mapped to a reason
   `template_unbound`, grouped with the consistency failures beside `set_state_unbound`.
   *Done when* the row exists and cites Sections 5.2, 10.2.

2. **Validation's judgement input (Section 6.10)** — ensure the section states what validation is
   judged from: the policy document, the actions the consumer can effect (which is what
   `set_state_unbound` turns on), and **the repository units the consumer bound** (which is what
   `template_unbound` turns on). Ensure the sentence is explicit that a template unit is a
   Section 10.2 repository unit rather than a Section 5.2 action, so the condition is determinable
   before the policy runs.
   *Done when* the judgement input is enumerated in prose and names bound repository units.

3. **`arguments_unreadable` (Section 8.6)** — ensure the precondition table carries a row for an
   invocation whose arguments the engine cannot decode in the encoding it published (Section 8.1),
   mapped to `arguments_unreadable`.
   *Done when* the row exists and cites Section 8.1.

4. **Ordering carve-out (Section 8.6)** — ensure the section states that `arguments_unreadable` is
   established **before** validation rather than after it, because an engine that cannot decode its
   arguments cannot locate the policy it would validate, and that every other precondition follows
   validation as the section already states. Ensure the existing rule — where a configuration error
   and a precondition failure both hold, the configuration reason is reported — is preserved for the
   other rows. *Done when* the carve-out is stated and the existing ordering sentence still holds
   for every other precondition reason.

5. **Entry Points and Arguments (Section 8.1)** — ensure the section states that an invocation whose
   arguments the engine cannot decode is refused with the `usage_or_config` status and the
   `arguments_unreadable` reason (Section 8.6), so the surface Section 8.1 hands the engine carries
   a defined failure rather than one the engine invents. *Done when* Section 8.1 names the
   disposition and cross-references Section 8.6.

6. **Exit Codes (Section 8.3)** — ensure the section reserves `1` for an invocation that produced no
   Section 8.2 result, with stdout carrying nothing and the diagnostic on stderr, and states that
   **any other code means the same** — so a consumer's mapping over exit codes is total without the
   specification enumerating the ways a process can die.
   *Done when* the list carries `1` with that meaning and the any-other-code sentence follows it.

7. **Exit Codes (Section 8.3)** — ensure the section states that on every path that produces a
   result, stdout carries exactly one JSON object and nothing else, so a caller separates "no
   result" from "result" without parsing. Ensure the existing sentence "The JSON result is emitted
   regardless of exit code" is scoped to the four statuses so it no longer contradicts the reserved
   code. *Done when* the stdout discipline is stated and the "regardless of exit code" sentence
   names the four result-bearing codes.

## Cross-cutting sync

- **Test matrix (Section 13.1)**, under "Invocation contract" — a policy binding `body_source =
  "template"` with no template unit bound is refused at validation with `template_unbound` and
  publishes nothing, rather than reaching `create_pr` after a `push`; an invocation whose arguments
  cannot be decoded yields `usage_or_config` with `arguments_unreadable`, exit `2`, and a
  well-formed envelope on stdout; an invocation that produces no result exits `1` with stdout empty;
  a caller reading stdout finds exactly one JSON object on every result-bearing path.
- **Implementation checklist (Section 13.2)** — extend the invocation-contract line with the
  reserved code and the stdout discipline.
- **Conformance Statement (Section 13.3)** — no new row: the reserved code and the stdout rule are
  fixed rather than `Implementation-defined`. The engine's argument encoding is already enumerated
  there (Section 8.1).
- **`conformance/vcsx/vocabulary.json`** — add `template_unbound` to `config_reasons`,
  `arguments_unreadable` to `precondition_reasons`, and `1` to `exit_codes` with its meaning.
- **`conformance/vcsx/vectors/policy-validation.json`** — add a vector refusing a `template` body
  source with no unit bound, and one accepting the same policy where a unit is bound.

## Anchor changes

None. `template_unbound` and `arguments_unreadable` are new code tokens; no existing anchor is
renamed or removed.

## Status

Applied to `VCSX-SPEC.md`.
