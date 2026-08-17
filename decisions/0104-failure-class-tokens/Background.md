# Background — 0104 The failure classes get a token

## Context

Decision 0103 named the test the registry publishes by: **a prose enumeration is published when
something outside the implementation's own source spells it.** Section 14.1's nine failure classes
pass it, and 0103 could not publish them, because the specification does not fix what their token
is.

This decision closes that. It is separated from 0103 for one reason: it is an anchor change (0002)
across seven documents, and an anchor change wants a decision to be accepted against rather than
arriving inside a registry slice.

## The reader is a person, and the document they write is published

The nine classes are read by more than a conformance check:

- **`CONFORMANCE-STATEMENT-TEMPLATE.md` carries two rows named by class** — the persistent
  park-vs-retry disposition of `Repository Provisioning Failures` and of `Engine Invocation
  Failures`. A statement author copies those names by hand into a document their implementation
  publishes. This is the transcription surface the registry exists to remove, in its most literal
  form.
- **Sections 17.2, 17.4, 18.1.4 and 19 name classes in backticks.** Those checks assert *behaviour*
  — "skip that repository's dispatches, retry on a later tick" — and name the class descriptively,
  so the spelling is not measured the way Section 5.5's is by the corpus. A slower signal than the
  corpus, but a real one: Section 19 is the Conformance Statement.
- **Section 14.2 gives every class a distinct recovery**, so the class is what a consumer branches
  on to select one.

## What blocks the group: the document answers the shape question twice

Section 14.1 enumerates nine Title Case titles:

```text
1. `Workflow/Config Failures`         6. `Observability Failures`
2. `Repository Provisioning Failures` 7. `Engine Invocation Failures`
3. `Workspace Failures`               8. `Node Provisioning Failures`   (OPTIONAL)
4. `Agent Session Failures`           9. `Executor Bring-up Failures`   (OPTIONAL)
5. `Tracker Failures`
```

and then, in its own closing note, names a tenth in a different shape:

> Note: an OPTIONAL extension MAY define additional failure categories outside this core list. For
> example, the token budget guards extension (Section 8.8) defines `token_budget_exceeded`, which is
> parked rather than retried (Section 14.2); classes 8 and 9 above are defined by the OPTIONAL
> node-scheduler extension (Section 9.11).

`token_budget_exceeded` is a failure category by Section 14.1's own words, is asserted by a Section
17.4 check, and is `snake_case`. So the specification spells failure categories two ways in one
section, and a registry that picked between them would be deciding what the prose left open — the
thing 0071 forbade and 0102 restated. **The document has to answer once before a group can be
derived.**

## Options considered

**Option A — `SPEC.md` gains an identifier-shaped token for each of the nine, keeping the Title Case
names as their prose names.** Chosen; reasoning below.

**Option B — publish the titles verbatim; each implementation slugifies.** The conservative option
and the only one needing no specification change: the registry would carry `"Workflow/Config
Failures"` exactly as written, invent nothing, and leave the identifier to the implementation. Its
case is that the titles *are* what the specification says, and a registry faithful to its source is
the whole design.

It loses on the mechanism the registry exists for. Two implementations slugifying `Workflow/Config
Failures` independently produce `workflow_config_failures`, `workflow/config_failures`, or
`WorkflowConfigFailures` — and nothing catches the divergence, because each is a defensible reading
of the same published string. The registry would have taken a set that diverges silently and
published it in a form that still diverges silently, now with its authority behind the ambiguity.
Faithfulness to the source is the goal only where the source is unambiguous; here it is the defect.

**Option C — the registry mints the slugs.** Cheapest, immediate, no specification change, and it
does fix the divergence. It loses because a derived view that mints a token is leading its source: a
later reader cannot tell which tokens `SPEC.md` fixed and which the registry decided, which is
precisely 0071's stated signal that a registry has stopped being derived. The cost of Option A is
paid once; the cost of Option C is paid by every later reader.

## What application turned up

Three things the plan did not anticipate, found while applying it.

**The suffix is load-bearing.** The obvious slug drops the category word — `Workspace Failures` →
`workspace` — and reads better. It cannot be used: `workspace`, `tracker` and `observability` are
already `config_namespaces` entries, so three of the nine would collide exactly with a configuration
key, and a reader seeing `tracker` in a record could not tell which set it came from. Keeping
`_failures` costs nothing and removes the ambiguity, so every token is the prose name transliterated
rather than shortened.

**Section 14.2 did not name the classes it disposes of, and the mapping is not one-to-one.** Its
bullets carry their own descriptive headings — "Dispatch validation failures", "Worker failures",
"Dashboard/log failures" — none of which is a Section 14.1 class name. The correspondence was
inferable but unstated, which is a defect in its own right and also a blocker here: a registry entry
carrying a recovery disposition would have been *inventing the mapping*, which is exactly what a
derived view may not do. So Section 14.2's bullets now name their classes, and two facts became
visible in the process:

- `workspace_failures` and `agent_session_failures` **share** the worker disposition, because both
  fail one attempt and convert to a backoff retry.
- `tracker_failures` takes **two** dispositions, because what a tracker failure costs depends on
  where it occurred: a candidate fetch skips a tick, a state refresh keeps the workers it already
  has.

A nine-row mapping would have hidden both. This is why the registry group carries **no** recovery
disposition: with the mapping stated in Section 14.2 the group would only restate it, and 0071's line
is that entries carry "the properties the specification fixes about them — not the prose of the rules
those properties feed". A disposition is that prose. The contrast with `error_classes` carrying
`gating` is deliberate: Section 5.5 states gating as a two-valued property of each token, where
Section 14.2 states paragraphs of behaviour.

**The requirement level was not asked and had to be settled.** The decision sheet fixed the token
*shape* and did not ask whether the spellings are REQUIRED. Left unstated they would be unusable for
the reader that motivated the decision — a Conformance Statement author transcribing a class name
into a published document gains nothing from a token another implementation may spell differently.
So the level is REQUIRED, on 0102's test: the condition is Symphony's own, faced identically by every
implementation. Recorded here as a call this decision made rather than one it was given.

## Decision and reasoning

**Each of the nine gains an identifier-shaped token beside the Title Case name it already has.** The
prose keeps its titles, which read better in Section 14.1's and Section 14.2's sentences; the token
is what a consumer branches on, a Conformance Statement is keyed by, and the registry publishes.
This also makes the section self-consistent for the first time: `token_budget_exceeded` stops being
an anomaly and becomes the shape the section uses.

**The order matters and is 0071's.** The specification fixes the token, then the registry publishes
it. Reversing that — publishing first and letting the prose catch up — is what the registry's
precedence rule exists to prevent.

**`exhaustive: false`, on evidence rather than reading.** `token_budget_exceeded` is a failure
category outside the nine, so the set is demonstrably open. This does not contradict a consumer
closing its own enum at nine: 0071 settled the shape for `events` — openness is a property of the
set, not of the names. Issue #54's reporter closed theirs at nine and is right to have done so for a
build shipping no such extension; one shipping Section 8.8 produces ten and needs the tenth. Their
own argument for closing it holds unchanged — a failure class never arrives from outside, and
Section 14.2 gives every class a distinct recovery, so an unknown class would be a recovery nobody
can select.

**The cost, stated plainly.** Sections 14.1, 14.2, 17.2, 17.4, 18.1.4 and 19 plus
`CONFORMANCE-STATEMENT-TEMPLATE.md`, and an anchor addition recorded append-only under 0002. Nothing
is renamed or removed — the titles survive as prose names — so no existing reference breaks; what
changes is that a second way to address each class now exists, and the plan's job is to make sure
the conformance surfaces use it.

**Reconsideration trigger.** If a later reader finds the nine tokens are only ever used by the
registry and the Conformance Statement, and never by an implementation's own branching, then Section
14.2's recovery mapping was the real consumer all along and the token should have been derived from
that table rather than from the class list. The evidence would be an implementation whose failure
taxonomy keys on recovery rather than on class.

Depends on 0103 (whose reader test selects this set) and 0071 (whose ordering rule this follows).
Relates to 0102 and 0002.
