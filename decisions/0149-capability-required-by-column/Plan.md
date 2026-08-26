# Plan — 0149 The column that said who provides and not who requires

## Scope

- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — Section 6.1 only: the paragraph above the
  beyond-Section-9.1 table, and that table's columns.
- `VCSX-SPEC.md` — **no change**. The defect is in the template's inference, not in the
  specification.
- `SPEC.md`, `VCSX-CONTRACT.md`, `conformance/` — no change.

## Steps

1. **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 6.1 — the inference is narrowed to what the
   premise licenses.** Ensure the paragraph quoted as "so a capability beyond the list is a
   backend's own rather than an engine's" no longer draws that conclusion, and instead states that
   the premise licenses only the narrower one — that a capability beyond the list is not an
   engine-added operation's, while it may still be the engine's, because `VCSX-SPEC.md` Section 9.1
   is a minimum for the operations the specification defines rather than a complete account of what
   they need. Ensure the existing citation to the two `VCSX-SPEC.md` sections that fix the operation
   set (4.1 and 8.5) is kept, since that half is true and is 0134's contribution. Ensure the
   instruction that follows asks for three things per capability — what it is, what requires it, and
   which shipped backends provide it — and keeps the "leave empty where none does" permission. *Done
   when:* no sentence in the template infers a capability's requirer from the operation set being
   closed, and the section asks the question a backend author needs answered: whether a capability
   above the floor is optional or load-bearing.
2. **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 6.1 — the table carries four columns.** Ensure
   the beyond-Section-9.1 table's headers are `Capability beyond Section 9.1 | Required by |
   Provided by (backend) | Signature and result`, with `Required by` restored at position two.
   Ensure the heading is unqualified rather than `Required by (operation)`: the real requirers are
   an operation (`load_policy`), a lifecycle position (`before:commit`) and a declaration in the
   document (a `[hooks.engine]` unit), and the qualified form excludes two of the three. Ensure the
   placeholder row gains a fourth cell. *Done when:* the table has four columns, and a Statement
   filled in as the template directs distinguishes what the engine requires from what a backend
   happened to bring.
3. **The parser is run in the same commit.** Ensure `python3 scripts/validate_spec_consistency.py`
   reports 0 errors and 0 warnings after the edit. The column insert is expected to be invisible to
   it — `check_obligations` scans only the second cell for section numbers and this table's number
   lives in the first, while the subsection heading `### 6.1 VCS Backends (Section 9.1)` keeps
   answering for `VCSX-SPEC.md` Section 9.1 — but the script is at 0/0 today, so any output is the
   edit's own. *Done when:* the run is clean and the reason it is clean is the one recorded here
   rather than a coincidence.

## Cross-cutting sync

- **No row is owed anywhere, and no obligation is created.** The reword adds no
  `Implementation-defined` behaviour and no MUST-document sentence, so decision 0128's rule does not
  fire. Stated rather than left silent, because three decisions in a row missed the case where it
  does.
- `VCSX-SPEC.md` Sections 13.1, 13.2 and 13.3: no change. The obligations the template's Section 6.1
  serves are unchanged; only the shape of the answer changes.
- `SPEC.md` Sections 6.4, 17, 18 and `CONFORMANCE-STATEMENT-TEMPLATE.md`: no change.

## Ordering

- **Independent.** This decision depends on neither decision 0141 (issue #101) nor decisions 0150
  and 0151 (issue #110), and it is owed whichever way those land — the argument is in
  `Background.md`. Applying it first is what makes the gap visible in the interval before
  `VCSX-SPEC.md` Section 9.1 is closed.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0149-capability-required-by-column/Plan.md --rev
22b5194` reports two findings, both known and neither actionable:

- a reach finding at `VCSX-SPEC.md:2160` (Section 8.5), which carries "rather than an engine's" —
  the sentence fixing the operation set as the specification's, the true half of the premise this
  decision keeps and the passage step 1's citation points at. Not edited.
- a quote finding reporting that `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` has no Section 9.1. It
  does not, and the plan does not claim it does: the string comes from the **column name itself**,
  `Capability beyond Section 9.1`, which is a header in the template that names a section of
  `VCSX-SPEC.md`. This is a false positive of the attribution heuristic and is recorded rather than
  worked around, because the alternative is renaming a column to satisfy a checker.

## Anchor changes

- **Changed:** the beyond-Section-9.1 table in `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 6.1
  gains a `Required by` column at position two; the paragraph above it is reworded. The heading
  `Required by (operation)`, which decision 0134 removed, is **not** restored in that form — the
  replacement is the unqualified `Required by`.
- **Removed:** the inference sentence "so a capability beyond the list is a backend's own rather
  than an engine's". Plans and records quoting it are not edited; they record what was true when
  written.
- No code-token identifier is renamed, and no registry group changes.

## Status

Applied to `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Section 6.1), the only file the plan scopes and
the only live artifact carrying the removed sentence — `DECISIONS.md` quotes it inside this
decision's own chapter, where it is history and is not edited.

Step 3's done-condition asks that a clean run be clean for the recorded reason rather than by
coincidence, so the reason was measured rather than read off the source: `template_rows` returns an
identical dict before and after the edit, Section 9.1 answered three times either way. The insert is
invisible because the function scans only `cells[1]` for section numbers and this table's number
lives in `cells[0]`, while the subsection heading `### 6.1 VCS Backends (Section 9.1)` supplies the
section's answer. `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

One of the two Anchor check findings does not reproduce. `python3 scripts/check_plan_anchors.py
decisions/0149-capability-required-by-column/Plan.md` reports a single finding — the recorded
quote-attribution false positive, the column name `Capability beyond Section 9.1` read as a citation
to a section the template does not have — at `HEAD` and at `22b5194` alike, the checker being
unchanged between them. The reach finding this plan records at `VCSX-SPEC.md:2160` does not fire.
Nothing is owed either way: that sentence is not edited, and the plan's scope does not depend on it.

**Named rather than missed, and not fixed here.** `VCSX-SPEC.md` Section 9.1's realization paragraph
carries the nearest thing to a source for 0134's inference — "which operations there are is this
specification's to say rather than an engine's (Sections 4.1, 8.5), so no engine adds one that would
require more. A capability a backend provides beyond this list is visible as that backend's own
rather than as shared surface." Its "so" clause is the true half and its second sentence is scoped
to a capability a backend already provides, so it is not the template's inference and this decision
scopes `VCSX-SPEC.md` out. But the two documents now read differently on the same question, and the
scoping is what decisions 0150 and 0151 revisit when they move capabilities into the list.

Issue #102.
