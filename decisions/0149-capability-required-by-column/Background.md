# Background — 0149 The column that said who provides and not who requires

## Context

Issue #102. Decision 0134 rewrote the capability question in
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 6.1. The new text infers, from the operation set
being closed, that a capability beyond `VCSX-SPEC.md` Section 9.1 must be a backend's own:

> Section 9.1's required capabilities are a minimum for a backend, not a maximum: the operation set is
> the specification's and this engine adds none to it (Sections 4.1, 8.5), so a capability beyond the
> list is a backend's own rather than an engine's. List each one a shipped VCS backend provides; leave
> empty where none does.

The columns moved with the sentence, from `Capability | Required by (operation) | Signature and
result` to `Capability beyond Section 9.1 | Provided by (backend) | Signature and result`.

The premise is right and the inference does not follow.

## The inference fails structurally, not because two capabilities happen to be missing

The premise licenses exactly one conclusion: **not an engine-added operation's**. It cannot license
"the backend's", because `Required by` and `Provided by` answer different questions — the engine is
the party that *requires* a capability and the backend is the party that *provides* it, and a floor
being met says nothing about who wanted what sits above it.

That holds even if Section 9.1 were complete. `VCSX-SPEC.md` Section 6.6 leaves host-side unit
resolution `Implementation-defined` ("How an engine resolves a `host_side` unit is
`Implementation-defined` and MUST be documented (Section 13.3)"), so an engine may need a capability
for whichever mechanism it documents, and that capability is the engine's requirement however many
backends provide it. **0134 removed the column that carried the fact and added one that does not,
where it should have added.**

It also leaves the section's original question unasked. The old form asked what an engine that
defines operations beyond Section 4.1 additionally requires of a backend; 0134 made that condition
unmeetable by anyone, which is a good reason to change the sentence. What replaced it asks what a
backend provides beyond the list, which is a different question. **"What does this engine require of
every backend, beyond Section 9.1, in order to implement the specification's own operations" now has
no row anywhere in the template**, and every engine that implements Section 4.1 has an answer to it.

## What the wrong row does to a reader

`VCSX-SPEC.md` Section 13.3's tables are a declaration a consumer relies on. Filled in as directed,
a Statement publishes an engine requirement in a column headed `Provided by (backend)`, and a
backend author reading it concludes those capabilities are theirs to add or drop.

The reader that row serves is a backend author deciding whether a capability above the floor is
**optional** — drop it and the engine still conforms — or **load-bearing** — drop it and the engine
cannot implement Section 4.1 or Section 6.6. Only `Required by` answers that, and a Statement filled
in as the template now directs answers it wrongly.

This is field-verified rather than hypothetical. The `symphony-rs` engine's `CONFORMANCE.md` carries
the four-column form already — `Capability beyond §9.1 | Provided by | Required by | Signature and
result` — with a paragraph above the table naming which template inference is being contradicted and
why, because filling the table as the template directs would publish three engine requirements as
backend extras (that build's decision 0011 **R73**). Three capabilities, invented by an engine to
implement this specification, published under Section 13.3 as its own, with prose explaining why the
template is being disobeyed. The reword retires the prose and resolves R73; the rows are unchanged
but for a column swap into the template's order.

## Decision

Reword the inference so it licenses only what the premise supports, and restore the column:

> Section 9.1's required capabilities are a minimum for a backend, not a maximum. The operation set is
> the specification's and this engine adds none to it (Sections 4.1, 8.5), so a capability beyond the
> list is not an engine-added operation's — but it may still be the engine's, because Section 9.1 is a
> minimum for the operations the specification defines rather than a complete account of what they
> need. List each capability beyond the list, what requires it, and which shipped backends provide it.

with the table carrying four columns:

| Capability beyond Section 9.1 | Required by | Provided by (backend) | Signature and result |

## Why it is owed independently of decision 0150 and 0151

Those two decisions add `worktree_diff()`, `read_at_source()` and `export_source()` to Section 9.1,
after which a conforming engine's four-column table should be **empty**. That is an argument for the
reword rather than against it: while the capabilities are engine-private, the reworded row is the
only artifact that says *this engine requires them of every backend* rather than *some backend
happened to bring them*. It is what makes the gap visible between now and the decision that closes
it.

The rows do not disappear when those decisions land — they **move**. A capability arriving in
Section 9.1 stops being a row of prose in a Statement and becomes a declared descriptor field with a
determinable `capability_unsupported` refusal behind it (Sections 9.3, 6.11). That is the whole
value of closing the gap, and it is why this reword is a bridge rather than a competitor.

This decision depends on neither issue #101's decision (0141) nor #110's two, and can be captured
and applied on its own.

## Two mechanical facts, both checked

- **`scripts/validate_spec_consistency.py` does parse this file's tables**, and the column change is
  safe under it for a reason worth knowing rather than assuming: `template_rows` reads every row and
  `check_obligations` matches obligation sentences against the sections those rows cite, scanning
  only the **second** cell for section numbers. This table's number lives in its **first** cell
  (`Capability beyond Section 9.1`), so inserting `Required by` at position two changes nothing the
  parser counts, and the subsection heading `### 6.1 VCS Backends (Section 9.1)` keeps answering for
  Section 9.1 either way. The script is at 0 errors / 0 warnings today, so any output after the edit
  is the edit's own.
- **No row is owed anywhere.** The reword adds no `Implementation-defined` behaviour and no
  MUST-document obligation, so decision 0128's trap does not fire. Stated in the record rather than
  left silent, because three decisions in a row missed the case where it does.

## Options considered

### Close the gap in Section 9.1 instead, and leave the template's inference true as written

The more useful repair, and the reason it is not this decision: it makes the capabilities portable
across backends and brings them under Section 9.3's descriptor discipline and Section 6.11's
`capability_unsupported`, rather than leaving each engine to name its own. Three engines will
otherwise name one requirement three ways.

It loses **as an answer to this issue** rather than on its merits. The template's inference is
invalid independently of whether Section 9.1 is complete — see the structural argument above — so it
needs repairing either way, while closing Section 9.1 is a design decision with a real option space
that would be buried if it rode along: what a *revision* is in a document that holds branch names
opaque, where a materialization lands and who owns its lifetime, whether a capability narrows or
retires Section 6.6's `Implementation-defined` clause and its Section 13.3 row. Those are decisions
0150 and 0151, and splitting them is what keeps their reasoning readable.

### Restore the old `Required by (operation)` heading unchanged

The pre-0134 form. It loses for the reason 0134 changed it: "Required by (operation)" is scoped to
operations, and the capabilities that actually sit above the floor are required by an operation
(`load_policy`), by a lifecycle position (`before:commit`) and by a declaration in the document (a
`[hooks.engine]` unit) respectively. The heading has to be `Required by`, unqualified, or it
excludes two of the three real cases. Verified against the field data: the `symphony-rs` table's
`Required by` cells read `load_policy`, "any invocation whose policy declares a `[hooks.engine]`
unit", and "the `before:commit` position".

### Drop the table and ask the question in prose

An engine describes in Section 6.1's prose what it requires beyond the floor. It loses on the thing
Section 13.3's tables exist for: the tables are what a generator parses, and an obligation answered
in prose is invisible to every check — decision 0128's finding, one artifact over.

## What was checked

At `22b5194`, against the working tree:

- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 6.1 carries the 0134 sentence verbatim as quoted
  and a three-column table headed `Capability beyond Section 9.1 | Provided by (backend) | Signature
  and result`.
- `VCSX-SPEC.md` Section 4.1's opening sentence is "Operations are the unit `run_op` runs (Section
  5.2). **Each is realized through the plugin layer** and returns a typed result (Section 4.2)."
- `VCSX-SPEC.md` Section 9.1's realization paragraph maps `provision`, `integrate`, `pull`, `commit`
  and `status` onto capabilities; `load_policy` maps onto none, in Section 9.1 or Section 9.2.
- `VCSX-SPEC.md` Section 6.6's host-side unit resolution is `Implementation-defined` and MUST be
  documented (Section 13.3).
- `scripts/validate_spec_consistency.py`'s `template_rows` and `check_obligations` behave as
  described; `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## Reconsideration triggers

- **Section 9.1 gaining every capability the specification's own operations need** — decisions 0150
  and 0151 landing in full. The four-column table should then be empty for a conforming engine, and
  the question becomes whether the row is worth keeping at all. Keeping it is still the safer
  answer, since Section 6.6's `Implementation-defined` resolution can produce a fresh engine
  requirement at any time; but the argument for it weakens, and the row's emptiness is then evidence
  rather than an omission.
- **A capability whose requirer is neither an operation, a position nor a declaration.** The
  unqualified `Required by` heading is a bet that those three exhaust the shapes; a fourth would
  need the column's meaning stated rather than left to the cells.
