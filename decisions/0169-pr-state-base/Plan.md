# Plan — 0169 A clause with nothing to read

## Scope

`VCSX-SPEC.md` only: Section 9.2 (Forge Backend Plugin), the `status` entry of Section 4.1
(Operations), Section 13.1 (Test Matrix) and Section 13.2 (Implementation Checklist).

No change to `SPEC.md`. Section 9.10's three clauses stand as written and become dischargeable; no
Symphony-side behaviour changes. No change to `VCSX-CONTRACT.md`, which names the operations and
their typed results rather than a capability's answer shape.

## Steps

1. **`pr_state` answers the base.** Ensure Section 9.2's `pr_state(work_branch, known_validator)`
   entry lists the base the pull request currently targets alongside its number, its state and the
   head it currently carries, REQUIRED of every forge backend rather than capability-gated.
   Done when the entry names the base among the values the determinate answer carries.

2. **The reason it is reported and not keyed on is stated where the prohibition is.** Ensure the
   sentence forbidding a caller's base as the lookup key keeps its wording and gains the
   distinction: keying on base would hide a pull request opened or retargeted against a different
   base, which is what `create_pr:base_mismatch` exists to find, while reporting the base of
   whatever the head-keyed lookup returned is what makes such a pull request visible.
   Done when the paragraph states both directions and the `MUST NOT` is unchanged.

3. **`status` reports the base.** Ensure the `status` entry of Section 4.1 names the base alongside
   the number and the open/closed/merged state in its pull-request output, so the value reaches a
   caller. Ensure the base is carried on the determinate answer and is null in the other three
   pull-request conditions exactly as the number and state already are, so `pr_state_unavailable`,
   `pr_state_unchanged` and `pr_state_throttled` are unchanged and no output token is added.
   Done when the `status` entry names the base and no new output is introduced.

4. **The test matrix asserts it.** Ensure Section 13.1's operations-and-reasons item asserts that
   `pr_state` answers the base of the pull request the head-keyed lookup returned, including one
   targeting a base other than the caller's resolved base — the case the key exists to find — and
   that `status` reports that base rather than the caller's own.
   Done when Section 13.1 contains the assertion beside `create_pr:base_mismatch`.

5. **The implementation checklist names it.** Ensure Section 13.2's plugin-API item, or the item
   nearest `pr_state`'s answer shape, names the base among what a forge backend's pull-request read
   answers.
   Done when Section 13.2 names the base as part of that answer.

## Cross-cutting sync

- **`VCSX-SPEC.md` Section 13.1** — step 4. **Section 13.2** — step 5.
- **`VCSX-SPEC.md` Section 13.3 (Conformance Statement)** — no obligation added. The base is
  REQUIRED of every backend rather than `Implementation-defined`, and nothing here must be
  documented by an implementation.
- **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`** — no row owed, for the reason above and against the
  template's own structure: Section 2 declares broad required surfaces, Section 3 is the
  `Implementation-defined` table, and Section 6.2's forge table records the capabilities a backend
  declares rather than the shape of a required answer. A row for a field every backend MUST answer
  admits one value.
- **`SPEC.md` Sections 6.4, 9.10, 17, 18** — unaffected. Section 9.10's clauses are unchanged in
  wording and unchanged in what they require; what changes is that the third one now has a value to
  read. Section 17.2's identity check and Section 18.1.4's bullet already state all three clauses.

## Anchor changes

None. No code-token identifier is renamed or removed and no section is retitled. The base is a new
member of an existing answer rather than a rename of one.

## Status

Applied to `VCSX-SPEC.md`: Section 9.2's `pr_state` entry and its lookup-key paragraph, Section
4.1's `status` entry, Section 13.1's operations-and-reasons item, and a new Section 13.2 checklist
bullet. All five steps.
