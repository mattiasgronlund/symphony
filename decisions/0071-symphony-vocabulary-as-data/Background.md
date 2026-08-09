# Background — 0071 The Symphony token vocabulary as data

## Context

Resolves part 3 of issue #15, raised while deciding what `SPEC.md` Section 13 means for an
implementation (against `06a3bc19`).

Decision 0051 published the engine's shared token vocabulary as `conformance/vcsx/vocabulary.json`,
so an engine implementation generates or checks its reason enum, proto-class mapping and action set
from a file rather than transcribing them, and an upstream rename becomes a compile error. Its
argument was that `VCSX-SPEC.md` Section 14 already made a shared token's spelling a contract, and
that a third spelling in a separate repository could not be held aligned by review.

`SPEC.md` has no counterpart. Four of its token sets are prose that an implementation has no choice
but to re-spell by hand:

- the emitted runtime events (Section 10.4);
- the REQUIRED log context fields (Section 13.1);
- the usage-ledger entry fields (Section 13.6);
- the state recovery classes (Section 14.3).

The drift `VCSX-SPEC.md` Section 14 closes for the engine is therefore open for Symphony, and it is
silent in the same way: an event renamed upstream changes nothing downstream until someone reads a
re-pin diff. Symphony's exposure is arguably worse than the engine's, because `SPEC.md` is explicitly
written for multiple implementations in multiple languages (decision 0045) — every one of them
spells these tokens independently.

Section 10.4 adds a second problem on top of the first. It introduces its list with "Important
emitted events include, **for example**", which makes it unclear whether the list is exhaustive. That
matters for codegen in a specific way: an exhaustive enum built from a list the specification calls
an example would refuse a conformant event and claim a completeness the specification disclaims,
while an open enum built from a list that was meant to be closed loses the exhaustiveness check that
is the whole reason to generate a type. And the ambiguity is not only about codegen — Section 10.7
states that "Each adapter MUST emit the neutral event vocabulary (Section 10.4)", which is a
requirement to spell something exactly, pointed at a list labelled as illustrative. The two sections
cannot both be read literally.

## Options considered

**Whether to publish a registry at all:**

- **Option A — a Symphony token registry in the same shape as the engine's (chosen).** A JSON file
  enumerating the token sets `SPEC.md` names, each group citing the sections it is read from.
  Trade-offs: one more artifact to keep aligned with the prose, and the standing risk that a derived
  view is read as normative. Both are the costs 0051 already accepted and mitigated with an explicit
  precedence rule.
- **Option B — a pinned-spec hash check.** The implementation pins a `SPEC.md` revision and re-reads
  Section 10.4 on bump. Trade-offs: no new artifact. Rejected: it converts a silent failure into a
  diff someone has to read, which is the mechanism that already failed — and it does nothing for the
  second and third implementations, which is the case `SPEC.md` is written for.
- **Option C — inline the tokens into the Conformance Statement template.** Each implementation
  transcribes its spellings into its Statement, where a reviewer can compare them. Rejected: a
  Statement is a human-readable declaration, not something a build consumes; it catches a divergence
  at audit time rather than at compile time.

**Where the file belongs:**

- **`conformance/vocabulary.json` (chosen).** The Symphony corpus already occupies `conformance/`
  directly — `README.md` plus `vectors/` — while the engine's data sits in the `conformance/vcsx/`
  subtree (decisions 0046, 0051, 0053). Placing Symphony's registry beside Symphony's vectors is the
  symmetric position, and `SPEC.md` Section 17 already points at `conformance/` for the corpus.
- **`conformance/symphony/vocabulary.json`** (rejected). Superficially tidier — two named subtrees
  rather than one named and one unprefixed. It requires moving the whole existing corpus, which
  breaks the paths cited in decisions 0046, 0048, 0051 and 0053, in `conformance/vcsx/README.md`, and
  in `SPEC.md` Section 17, to buy symmetry no consumer needs.
- **Folding it into `conformance/vcsx/vocabulary.json`** (rejected on 0051's own reasoning): the two
  derive from different specifications, have different schemas, and are consumed by different
  implementations.

**Whether Section 10.4's list is exhaustive:**

- **Option D — not exhaustive, but the listed names are fixed (chosen).** An adapter MAY emit
  additional events for conditions the specification does not name, and a consumer MUST tolerate an
  unrecognized name; an implementation that emits an event for one of the listed conditions MUST
  spell it as listed.
- **Option E — exhaustive** (rejected). It would give the strongest generated type. But it makes any
  adapter-specific event non-conformant, which contradicts the neutral-adapter model: Section 10.4
  itself provides for "payload fields as needed", Section 10.9 has each adapter normalize its own
  protocol, and protocols differ in what they report. Declaring closure would also be a substantive
  new restriction, adopted to make codegen convenient.
- **Option F — leave it open ("for example" and nothing more)** (rejected). It is the status quo and
  the cheapest. It leaves Section 10.7's MUST pointing at a list the document calls illustrative, so
  an adapter could rename `turn_failed` and claim conformance. That is the drift this decision is
  about.

## Decision and reasoning

Choose **Option A**, at `conformance/vocabulary.json`, with **Option D**'s ruling stated in `SPEC.md`
Section 10.4 first.

**The ruling belongs in the specification, not in the registry.** This is the part that ordered the
work: a registry cannot decide whether a list is closed, because the registry is derived and the
specification governs. So Section 10.4 gains a `Note:` stating both halves — the set is open and a
consumer MUST tolerate an unrecognized name; the names are fixed for the conditions they name, which
is what Section 10.7's "MUST emit the neutral event vocabulary" means in practice. That resolves the
contradiction between the two sections in the direction both can survive, and only then does the
registry record it as `exhaustive: false`.

**Openness is a property of the set, not of the names.** Keeping those two apart is what makes the
answer usable: a generated type admits an unknown token (so a conformant adapter-specific event is
not refused) while every known token is still checked (so a rename is still a build failure). The
same shape is already in the engine registry, where `operations` carries "The required set. An engine
MAY define additional operations".

**The prose governs; the artifact is derived** — inherited from 0051 unchanged, and now stated in
`SPEC.md` itself rather than only in a README, because Symphony's registry has no Section 14 to lean
on. Section 17's preamble gains a paragraph naming the token sets and the precedence rule, so an
implementer reading only `SPEC.md` learns that the registry exists and that a disagreement is a
defect in the registry.

The slice is the four token sets the issue names plus three that make them usable rather than
readable: the neutral token-usage record (Sections 4.1.6, 13.5), which both the event `usage` map and
the ledger entry are defined in terms of; the per-field recovery-class assignments (Section 4.1.8),
which are what the Conformance Statement's recovery-class table is compared against; and the
configuration namespaces (Sections 5.3, 18.2), which are what its extensions table's namespace column
is drawn from — the same list decision 0069 just added `observability.*` to. Error and category
codes, orchestration states and transition triggers, failure classes, and the RECOMMENDED response
shapes are deferred with their reasons recorded, on the corpus's own slice discipline; several of
them need a per-entry distinction between REQUIRED and RECOMMENDED spellings that this slice does not
have to invent.

Authoring the `config_namespaces` group surfaced two findings that are recorded rather than fixed:
Section 5.3's "Top-level operator-config keys" list omits `vcs`, which Section 6.4 documents; and
Section 13.8 places `server.*` in `WORKFLOW.md` front matter, which Section 5 forbids for a setting
Symphony executes with host access. The registry records both as the sections state them, since a
derived view may not correct its source.

We would reconsider on 0051's trigger, unchanged: if the registry begins accumulating properties the
prose does not fix, it has stopped being a derived view, and the remedy is to move the concept into
`SPEC.md` and re-derive rather than to let the registry lead. A second trigger is specific to
Symphony: if a Section 14-style alignment rule is ever written into `SPEC.md`, the registry becomes
the mechanism for it and the Section 17 paragraph should defer to that rule instead of standing
alone.

The decision is **Accepted** and applied: `conformance/vocabulary.json` is created,
`conformance/README.md` documents it, and `SPEC.md` Sections 10.4 and 17 carry the ruling and the
precedence rule. Depends on 0051 (whose artifact, schema and precedence rule this reuses) and 0046
(whose corpus discipline both inherit); relates to 0045 (the multi-implementation strategy that makes
independent spellings the default), 0011 (the ledger whose entry fields are one of the groups), 0010
(the recovery classes), and 0069 (whose namespace the `config_namespaces` group carries).
