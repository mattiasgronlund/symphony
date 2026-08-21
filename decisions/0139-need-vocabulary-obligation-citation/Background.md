# Background — 0139 An obligation answered in full, and the heading that did not say so

## Context

`scripts/validate_spec_consistency.py` has warned for three decisions running:

```text
warning: VCSX-SPEC.md Section 8.4: 2 obligation(s), 1 row(s) in
VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md — check each is answered
```

It was the only warning left standing after decisions 0136–0138, and it is closed here.

Both prior decisions that met it examined it and left it. Decision 0132 diagnosed the cause exactly
— the template "answers with a whole section (Section 5, "`need` Vocabulary Emitted") whose heading
carries no section citation for the validator to count" — and recorded it as a non-gap. Decision
0134 carried that forward and added a second reason: the obligation is "the `need` vocabulary's own
spec-level stability clause rather than a choice an engine makes", and "no detector is worth
writing: no general rule separates a spec-level MUST-be-documented from an implementation one."

## The claim that does not hold

0134's added reason is half right, and the half that is wrong is the half the disposition rested on.
The obligation sentence in `VCSX-SPEC.md` Section 8.4 carries two obligations in one clause:

> the `need` vocabulary is part of the public contract and MUST be documented and stable within a
> major version

**Stable within a major version** is spec-level, exactly as 0134 says. `VCSX-SPEC.md` Section 8.5
fixes what may not change within a `MAJOR` and names the `need` vocabulary among it; an engine does
not choose that.

**Documented** is not. It is an obligation on the engine, and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` already reads it that way and already discharges it: its
Section 5 says "List every `need` **this engine** can emit, including the registry-named ones it
uses", and tabulates the eight registry needs plus an `<other>` row. A section that asks the engine
to enumerate its own vocabulary is not answering a spec-level guarantee; it is answering an
implementation obligation.

So the obligation is answered twice over and neither answer was visible to the count: the
documentation half by the template's Section 5, whose heading cites nothing, and the stability half
by its Section 1 ("Version and Major-Stable Surface"), whose prose cites Section 8.5 rather than
8.4. The warning was never about a missing answer — 0132 was right about that — but it was also not
about a distinction no rule can draw. It was about a heading that did not follow the template's own
convention.

## What was checked

- The validator's `template_rows` counts two shapes: a row citing its section in the second column,
  and a heading matching `(Section N)`. `### 4.1 Operation Reasons (Section 4.3)` is the convention
  already in this template; `## 5. \`need\` Vocabulary Emitted` was the one answering section that
  did not follow it.
- The first of Section 8.4's two obligations — the `Implementation-defined` `detail` — is rowed at
  `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md:87`. It was never the missing one.
- Template Section 1 names "the `need` vocabulary" among what Section 8.5 fixes as major-stable, so
  the stability half has a home even though it cites the wrong section number to be counted for it.
- After the change the validator reports 0 errors and 0 warnings, against 0 errors and 1 warning at
  `211d515`.

## Options considered

### Cite Section 8.4 in the answering heading — chosen

One token. The heading becomes `## 5. \`need\` Vocabulary Emitted (Section 8.4)`, which is the shape
the validator's whole-subsection rule exists for and the shape three other headings in the same file
already use. Nothing normative changes and no obligation is added or removed.

### Leave it, as 0132 and 0134 did

The status quo, and it has a real case: a standing warning is a standing marker, and silencing one
costs the reminder that the sentence is doing two jobs. Three decisions read it and none was misled.

It loses because a permanent warning is a worse marker than it looks. A checker that always prints
one line trains a reader to skip the line, and the next genuine warning arrives underneath it — as
one nearly did during decisions 0136–0138, where two new obligation miscounts appeared and had to be
told apart from the standing one by memory. A marker that must be remembered rather than read is not
doing the job the warning was kept for.

### Exempt the sentence in the checker

`OBLIGATION_EXEMPT_SECTIONS` exists and would take `VCSX-SPEC.md` Section 8.4 in one line. This is
what 0134's reasoning points at, and it is the option that reasoning would have chosen.

It loses on what it would assert. Exempting the section says no Conformance Statement owes anything
for it, and that is false: the `detail` field is rowed and the `need` vocabulary is tabulated. The
exemption would suppress a true positive to silence a citation defect, and it would silence the
first obligation along with the second, since exemption is per section rather than per sentence.

### Split the sentence in `VCSX-SPEC.md`

Separate the documentation obligation from the stability guarantee so each is counted where it
belongs. It is the most honest repair of the underlying conflation and it was seriously considered.

It loses on cost against benefit. It edits a normative document to satisfy a counting tool, which
inverts the direction the tooling is supposed to run in, and the sentence reads correctly as prose —
a vocabulary that is part of the public contract is documented *and* stable, and saying so in one
clause is not a defect. The template is the derived artifact and is the right place to absorb this.

## Reconsideration triggers

- **A second obligation sentence conflating a spec-level guarantee with an implementation one.**
  One instance is absorbed by a citation. A pattern would mean the checker's marker set is too
  coarse, and the sentence split rejected above becomes the cheaper answer.
- **A template section answering an obligation without citing it.** This was the only one at
  `211d515`. If another appears, the convention is worth stating in `CLAUDE.md` rather than
  rediscovering per section.
- **The stability half ever needing its own answer.** It is currently answered under Section 1
  citing Section 8.5. A change making an engine document its own stability window would need a row,
  not a heading.
