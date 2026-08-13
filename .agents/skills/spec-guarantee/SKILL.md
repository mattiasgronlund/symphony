---
name: spec-guarantee
description: Draft or repair a normative guarantee in SPEC.md, VCSX-SPEC.md, or VCSX-CONTRACT.md — the test a MUST or MUST NOT clause has to pass before it is stated. Use whenever a clause promises that an engine or a backend will or will not do something.
---

# Spec Guarantee

A guarantee is only as good as what a consumer can check. State it over something observable through
this specification's own operations, not over the mechanism that happens to provide it today.

## The test

> Can a consumer verify this without knowing which VCS is underneath?

- "A push MUST NOT use a force flag" — **fails**. Readable only off the argv.
- "A read writes nothing to the history" — **fails**. `history` is not defined in the document, and
  the literal reading is unsatisfiable for a backend whose read snapshots the working copy.
- "A repeated read against a modified working tree does not move the revision a push would publish"
  — **passes**.

Apply the test while drafting. Applying it at review is how the same clause gets stated wrongly more
than once.

## Worked failure (decision 0083)

One guarantee was stated wrongly three times in a single decision, and two of the three were
introduced by the repair for the previous one:

1. Over a **mechanism** — "no force push". A proxy that held while git was the only backend, and
   that a second backend was always going to expose.
2. Over an **undefined term** — "writes nothing to the history". Nine informal uses of `history` in
   the document, and `jj status` defeats the literal reading by snapshotting the working copy into a
   commit.
3. Over a **scoped effect presuming an unstated arrangement** — scoping the prohibition to what the
   work branch reaches is equivalent to "a read changes nothing" only when the work bookmark sits
   off the working-copy commit, which the document had not said.

Each repair moved one step closer to quantifying over something a caller can observe. The third one
got there only because the arrangement was written down as a requirement on the backend.

## Checklist

- Every term the clause quantifies over is defined in this document or is an existing code token.
- The clause states an effect, not a mechanism; the mechanism is left to the backend.
- Any arrangement the guarantee depends on is stated as a requirement on the backend, not left as an
  assumption in the prose around it.
- The requirement is satisfiable *through the operation set*, not merely stateable: exercise the
  engine's own commit sequence against it rather than only the quiet case.
- The measurement is recorded next to the claim, with tool and version, so it stays re-checkable.
- Where behavior legitimately varies, the clause uses `Implementation-defined` with a "MUST document"
  obligation rather than picking a winner.
- Both ends of a paired guarantee — the definition and the clause that relies on it — quantify over
  the same named things, so they cannot drift apart.

## Boundary

Do not name a specific VCS, language, or library in normative text. Where a mechanism must be
described, describe its effect and leave the mechanism to the backend. Record the decision behind
the clause with the `decision-record` skill.
