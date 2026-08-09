# Background — 0070 The Conformance Statement records the Section 13 resolutions

## Context

Resolves part 1 of issue #15, raised while deciding what `SPEC.md` Section 13 means for an
implementation (against `06a3bc19`).

Section 19 requires a conforming implementation to publish "a resolution for every
`Implementation-defined` behavior and every other 'MUST document' obligation in this specification",
and introduces its enumeration with "including:", so the list is open by construction.
`CONFORMANCE-STATEMENT-TEMPLATE.md` is the RECOMMENDED shape of that Statement and pre-enumerates the
obligations as rows so none is silently skipped — which decision 0045 names as the whole point: the
recurring failure it exists to prevent is "an obligation silently skipped".

Three Section 13 behaviours are left to the implementation and appear in neither place:

- the **log sink** (Section 13.2) — "The spec does not prescribe where logs are written";
- the **human-readable status surface** (Section 13.4) — "OPTIONAL and implementation-defined";
- the **presentation of rate-limit data** (Section 13.5) — "Any human-readable presentation of
  rate-limit data is implementation-defined".

So an implementation filling in the template has nowhere to write three resolutions Section 19's own
"including:" implies it owes. The template's Section 4.2 also has no `<other>` escape row of the kind
its Section 2 already provides, so there is not even a generic row to improvise into — and a
Statement that omits a resolution because the form lacked a field is precisely the failure Section 19
exists to prevent.

Separately, the template's Section 2 extensions table cites a placeholder `13.x` in three rows. The
placeholders date from the template's creation with decision 0045, when Section 13's subsections had
not been numbered against. Two resolve — the per-execution usage ledger is Section 13.6 and the HTTP
status/control server is Section 13.8 — and the third, on the autonomous task management row
(`8.10 / 13.x`), resolves to nothing: Section 13 has no task-management subsection, so the row's
section is Section 8.10 alone.

One thing the issue does not name turned out to matter. The template is "a checklist of *pointers*
into `SPEC.md`; it restates no obligation's substance". Section 13.4 and Section 13.5 both say
"implementation-defined" in their own text, so a row for each points at an obligation that exists.
Section 13.2 does not: it says only that the spec does not prescribe. Adding a row for it without
touching `SPEC.md` would make the template the source of an obligation the specification never
states — the exact drift 0045 mitigates by pre-populating the template from the spec's own tokens.

## Options considered

- **Option A — resolve the obligations in `SPEC.md`, then add the rows (chosen).** Make Section 13.2
  say the sink is `Implementation-defined` and recorded in the Statement; extend Section 19's
  "including:" list with the Section 13 behaviours; then add the template rows, split core from
  extension-scoped, plus the `<other>` escape and the `13.x` fixes. Trade-offs: it edits `SPEC.md`
  for what was reported as a template gap, and adds one clause to Section 13.2. It is the only order
  that keeps the template derived.
- **Option B — add the rows to the template only** (rejected). It is the minimal change and what the
  issue's "Ask" literally requests. But for Section 13.2 the row would carry an obligation `SPEC.md`
  does not state, which inverts the template's standing from a view over the specification into a
  second source of requirements. The template's own preamble forbids it.
- **Option C — put all three rows under the template's Section 4.1 (Core)** (rejected). It is the
  workaround the reporting implementation used and it is simple. But Section 4.1 says core rows MUST
  be resolved and MUST NOT be left blank, while Section 13.4's status surface is explicitly OPTIONAL
  — filing it as core would demand a resolution from an implementation that ships no surface, and
  blur the Core/extension boundary the template inherits from Sections 17 and 18.
- **Option D — rely on the `<other>` rows and add nothing specific** (rejected). Section 2 already
  has an `<other>` row and Section 4 could get one, so an implementation *could* write the three
  resolutions in. But a pre-enumerated row is the mechanism: decision 0045 chose the template over a
  checklist precisely because a generic slot does not tell an implementer that an obligation exists.
  An escape row catches what nobody anticipated; it is not a substitute for what is already known.
- **Option E — drop the placeholder rows' section column instead of resolving `13.x`** (rejected).
  Cheap, and it would stop the citation being wrong. But the Section column is how a filler finds the
  obligation, and Section 13.6 and Section 13.8 are the sections; leaving the column empty trades a
  wrong pointer for no pointer.

## Decision and reasoning

Choose **Option A**, applied in that order: the specification states the obligation, then the
template carries the row.

**The template may only point at what `SPEC.md` states.** That is the constraint doing the work here,
and it is why a change reported as three missing table rows is partly a specification change. Section
13.2's "The spec does not prescribe where logs are written" is a *disclaimer*; `Implementation-defined`
is a *contract term* carrying a MUST-document obligation. Turning the first into the second is what
makes the row legitimate — and it is a fair reading of the existing text rather than a new
requirement, since Section 17.6 already makes sink failure behavior a `Core Conformance` check
("Logging sink failures do not crash orchestration"), which an auditor cannot check without knowing
what the sinks are.

**Core versus extension follows the specification's own marking, not the convenience of the form.**
The log sink (13.2) and the rate-limit presentation (13.5) sit in core sections, and every
implementation can answer both — the second with "none" where nothing is presented, which is a
resolution rather than a blank. The status surface (13.4) is marked OPTIONAL in its own heading, so
it is an extension-scoped row and gains a Section 2 extensions-table row to be `n/a`-able against,
carrying the `observability.*` namespace decision 0069 names. Filing each row by the specification's
own marking keeps the template diff-able against Sections 17 and 18, which use the same split.

The `<other>` escape row goes in Section 4.2 and a sentence goes in Section 4's lead-in saying the
rows are pre-enumerated but not exhaustive, mirroring Section 19's "including". Section 4.1 gets the
sentence but no row: its instruction is that a core row MUST NOT be left blank, and a permanent
placeholder row would contradict it on every filled-in Statement.

What would make us reconsider: if Section 19's list and the template's rows drift again — the risk
0045 already named — the remedy is to generate the template from `SPEC.md`'s tokens rather than to
keep patching both. This decision is the second time the two have been reconciled by hand.

The decision is **Accepted** and applied to `SPEC.md` (Sections 13.2, 19) and
`CONFORMANCE-STATEMENT-TEMPLATE.md` (Sections 2, 4, 4.1, 4.2). Depends on 0045 (which created the
Statement and the template) and 0069 (whose namespace the new Section 2 row carries); relates to 0050
(the engine's counterpart Statement, whose template carries reason tables of the same kind) and 0043
(the profile split the Core/extension boundary follows).
