# Plan — 0154 The record grew three fields and the vector that enumerates it did not

## Scope

- `conformance/vectors/prompt-rendering.json` — the `iterate-issue-object` vector's `given.issue`,
  `expect.rendered` and `description`.
- `scripts/validate_spec_consistency.py` — a seventh check and the docstring that lists them.
- `conformance/README.md` — the "Surfaced findings" entry.
- `SPEC.md` — **unchanged**. The document is right; only artifacts derived from it move.

## Steps

1. **`iterate-issue-object` — `given.issue` carries every Section 4.1.1 field.** Ensure the
   vector's `given.issue` has one key per field Section 4.1.1 "Issue" defines and no other, adding
   `assignees`, `project` and `team` to the thirteen already present. Give the three added fields
   values rather than their empty ones — `["alice"]`, `"web-platform"`, `"core"` — so the vector
   also catches a context that carries `project` only where routing consumed it; leave `branch_name`
   null so a null-valued member stays pinned. *Done when:* the vector's `given.issue` key set equals
   the field set Section 4.1.1 defines, which step 4's check asserts.

2. **`iterate-issue-object` — `expect.rendered` enumerates the same set in ascending code-point
   order.** Ensure the expected string is those field names, each bracketed, ascending as Section
   12.2 fixes it — "Yield a map's entries in ascending order of key":
   `[assignees][blocked_by][branch_name][created_at][description][id][identifier][labels][metadata][priority][project][state][team][title][updated_at][url]`.
   *Done when:* the rendered keys equal `given.issue`'s key set and are in ascending order, both
   asserted by step 4's check.

3. **`iterate-issue-object` — the description names what holds it to the record.** Ensure the
   vector's `description` keeps its existing sentence that the expected keys are the fields Section
   4.1.1 defines, and adds that `scripts/validate_spec_consistency.py` holds the two in agreement,
   so a reader who changes one is told where the other lives. *Done when:* the description names the
   script.

4. **`scripts/validate_spec_consistency.py` — check 7 compares the three spellings of one set.**
   Ensure a table-driven check exists over the vectors whose `expect` enumerates a set a section
   fixes, carrying one row today: `conformance/vectors/prompt-rendering.json`,
   `iterate-issue-object`, read from `SPEC.md` Section 4.1.1. Ensure it reports an **error** (not a
   warning) when any of these does not hold: the section's field set equals the vector's
   `given.issue` key set; that set equals the keys the expectation renders; the rendered keys are in
   ascending code-point order. Ensure it is called from `main()` with the other six. *Done when:*
   the check errors on the vector as it stands before steps 1 and 2, and reports nothing after them.

5. **`scripts/validate_spec_consistency.py` — the docstring lists check 7 and its limit.** Ensure
   the `Checks:` list gains an entry naming what check 7 compares and the decision that added it,
   and the deliberate-limits list gains one: the table has a single row because the corpus holds a
   single enumeration-shaped vector, so a vector this table does not name is unchecked, as every
   vector was before this decision. *Done when:* both appear in the module docstring.

6. **`conformance/README.md` — the drift is recorded under "Surfaced findings".** Ensure an entry
   states the gap in the terms the repair meets it: the vector was authored as a derived enumeration
   of Section 4.1.1 under decision 0135, two later decisions added three fields to that section
   without re-deriving it, no rule named the corpus as a sync target, and check 7 now holds the two
   in agreement. *Done when:* the entry names decision 0154, the vector id, and check 7.

7. **The repair is demonstrated rather than asserted.** *Done when:* `python3
   scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings with steps 1 to 4 applied,
   and with step 4 applied and steps 1 and 2 reverted reports one error per field the vector omits —
   three at this revision, naming `assignees`, `project` and `team`.

## Cross-cutting sync

- `SPEC.md` Section 6.4 (config cheat sheet) — no change; no configuration key is involved.
- `SPEC.md` Section 17 (test matrix) — no change. Section 17.1's map-iteration bullet already
  states the behaviour; this decision changes none, only an artifact derived from Section 4.1.1.
- `SPEC.md` Section 18 (implementation checklist) — no change, for the same reason.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — **no row owed**. The decision creates no
  `Implementation-defined` behaviour and no "MUST document" obligation; it removes a divergence
  between two artifacts, which is the opposite direction from the rule decision 0128 wrote.
- `conformance/vocabulary.json` — unchanged. No token is added, renamed or removed.
- `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — unchanged. Prompt
  rendering is Symphony's, not the engine's.

## Anchor changes

None. No code token, error class, field name, vector id or section title is renamed or removed. The
vector keeps its `id`; `given.issue` gains three keys that Section 4.1.1 already defines.

## Status

Applied to `conformance/vectors/prompt-rendering.json`, `scripts/validate_spec_consistency.py` and
`conformance/README.md`. Issue #120.
