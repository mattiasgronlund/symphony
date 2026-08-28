# Background — 0162 The four tracker categories a guarantee is checked by

## Context

`conformance/README.md` carried this as an open finding:

> **Section 17.3 requires four RECOMMENDED tracker categories by name (open).** Section 11.4
> declares its eleven error categories RECOMMENDED, but Section 17.3's `Core Conformance` checks
> name `tracker_unsupported_operation`, `tracker_state_unreachable`, `tracker_state_conflict` and
> `tracker_pagination_error` as the values a conforming implementation surfaces. Four of eleven are
> therefore required in practice while the set is declared advisory — the same asymmetry decision
> 0102 resolved for Section 5.5, one section over.

The finding understated it. Section 17.3 is a test matrix; a matrix requiring a name is a matrix
that has drifted from the section it tests. What measurement shows is that the four are spelled into
the specification's own **normative prose**, at sections that state what an operation fails with.

## The mechanism

**Where the four actually occur.** Measured against `SPEC.md` at `a4048bc`, by `grep -n <token>
SPEC.md`, counting sites outside Section 11.4's defining list:

| Token | Sites outside its own definition |
|-------|----------------------------------|
| `tracker_pagination_error` | Section 11.2 ("A failed or incomplete enumeration surfaces `tracker_pagination_error`"); Section 17.3; — |
| `tracker_unsupported_operation` | Section 11.7 ("anyway returns `tracker_unsupported_operation`"); Section 17.3; Section 18.1.2 |
| `tracker_state_unreachable` | Section 11.8 ("`set_state` fails with `tracker_state_unreachable`"); Section 17.3; Section 18.1.2 |
| `tracker_state_conflict` | Section 11.8 ("`set_state` fails with `tracker_state_conflict`"); Section 17.3; Section 18.1.2 |

And where the other seven occur:

- `tracker_api_request` and `tracker_payload_invalid`: **one** site each, the bullet that defines
  them. Nowhere else in the document.
- `tracker_api_status` and `tracker_backend_errors`: their defining bullet plus Section 11.4's own
  Linear note, which is illustrative — "the Linear adapter, being GraphQL over HTTP, reports…" —
  rather than a rule an adapter is judged against.
- `unsupported_tracker_kind`, `missing_tracker_api_key`, `missing_tracker_project_slug`: **one**
  site each, their own bullet, and nothing anywhere in the specification produces them by name. That
  third group is decision 0164's subject and is not re-levelled here.

So the eleven are not one set spelled at one altitude. Four are the vocabulary the document's own
normative sentences fail operations with; four are a target vocabulary an adapter maps a transport
onto; three are orphans.

**What the level costs.** RECOMMENDED means an implementation MAY use another name. Section 11.8
says `set_state` "fails with `tracker_state_unreachable`… rather than" succeeding, and Section 11.5
puts that failure on the broker's result path, where the agent and the orchestrator branch on it.
Two implementations can therefore both conform while one reports `tracker_state_conflict` and the
other reports `state_changed_underneath`, and nothing in the document prefers either. The consumer
that breaks is not a human reading logs — it is any caller that branches, which Section 11.8's own
sentence describes ("The orchestrator … re-reads the issue and re-evaluates"). A caller branching on
an advisory name branches on something the specification permits to differ.

**Measured downstream.** `symphony-rs` at `ee74fe7` generates `TrackerErrorCategory` in
`crates/symphony-vocab/src/generated.rs` from `conformance/vocabulary.json`, and carries the level
through into the generated type's own documentation: "RECOMMENDED, because the names are a target
vocabulary rather than a checked spelling", with
`TrackerErrorCategory::parse("tracker_something_else")` asserted in
`crates/symphony-vocab/src/lib.rs` to confirm the type admits an unknown token. The generator is
faithful to the registry and the registry is faithful to Section 11.4. Every artifact in the chain
is correct against the one above it, and the chain publishes an advisory spelling for a value
Section 11.8 tells a caller to branch on. This is the shape decision 0132 named: each artifact
complete against itself, the disagreement between them invisible.

**Why this is not decision 0102 repeated.** 0102 re-levelled Section 5.5's five workflow/template
classes to REQUIRED spellings and kept the set open. That precedent supplies the *form* of the
repair — a REQUIRED spelling under an open set — and not its reason. The reason here is that a
guarantee this specification states about tracker behavior is checked by the token: an enumeration
is complete or it surfaces `tracker_pagination_error`; a write is capability-gated or it returns
`tracker_unsupported_operation`. Take the token away and the guarantee is unobservable, which is the
test `spec-guarantee` applies. That reason is what selects four of eleven, and it selects the same
four the document already spells, which is the evidence that the split is real rather than fitted.

## The predicate

A category is REQUIRED where it is what makes a **Symphony-stated guarantee observable when it
fails**. Applied to all eleven it selects exactly the four:

- `tracker_unsupported_operation` — Section 11.7's capability descriptor is Symphony's construct;
  the token is how "never silently no-oped" is checked.
- `tracker_state_unreachable`, `tracker_state_conflict` — Section 11.8's `set_state` semantics are
  Symphony's construct; the tokens divide the two ways a transition write fails, and the
  orchestrator's response differs by which.
- `tracker_pagination_error` — Section 11.2's completeness guarantee is Symphony's; "a silently
  partial result is non-conformant" has no observable failure without it.

The other four describe how a transport broke. `tracker_api_status` is "for example non-2xx HTTP";
an adapter over a local store may never reach it. Nothing in the document conditions behavior on
which of the four a failure was: Section 11.4's orchestrator-behavior bullets dispose of a tracker
failure by *where it occurred* — candidate fetch, running-state refresh, startup cleanup — not by
its category.

## Options considered

- **Option A — re-level the four, keep the rest RECOMMENDED.** Trade-offs: states what four sections
  of the document already require, and the predicate that picks them is checkable against the other
  seven rather than being a list. It costs a two-level Section 11.4, which is a section whose
  members no longer share a requirement level — a reader must now read the level per entry.

- **Option B — re-level all eleven, the decision 0102 shape exactly.** Trade-offs: uniform, one
  level to read, and the phrasing 0102 uses ("where one of the conditions below occurs, MUST fail
  with the class named for it") costs a non-HTTP adapter nothing, since its conditions never arise.
  It is the tidier document. Against it: it cannot be applied to Section 11.4 as written. Three of
  the eleven carry no condition at all — the registry records this, "The first three entries carry
  no `condition` because Section 11.4 states none" — so the conditional phrasing has nothing to
  attach to, and requiring their spelling would entrench three tokens in an adapter error contract
  that no adapter raises and that decision 0164 removes. It would also make REQUIRED four names
  (`tracker_api_request` and its three siblings) that no sentence in the specification uses, which
  is requirement without a consumer: the reason to fix a spelling is that something reads it.

- **Option C — strip the names, softening 17.3, 18.1.2, and the prose in Sections 11.2, 11.7 and
  11.8 to state the condition without the token.** Trade-offs: it makes the document consistent the
  other way, and it has a precedent in the document already — Section 17.5 names **no** agent error
  category, so the parallel section handles the parallel registry exactly like this. That is a
  genuinely strong argument and it is why this option is not a foil: if the answer were "these names
  are advisory", 17.5 shows what that looks like and the edit is smaller. It loses because the
  agent-runner case is not parallel where it matters. Section 10.6's categories classify what an
  adapter observed of a process it launched, and Section 10.7 disposes of a turn by its outcome
  rather than by the category name. Section 11.8's tokens are the *result of a brokered write
  returned across the sandbox boundary* (Section 11.5) to a caller told to branch on it. Softening
  the prose would mean deleting the branch or leaving it keyed on nothing.

- **Option D — leave it, keep the finding open.** Trade-offs: costs nothing today. Against it: the
  finding names the evidence that would force the issue as "a second tracker adapter asserted
  against those checks", and Section 17.3's first check already requires two — "At least the
  `linear` and `forgejo` tracker adapters implement the read and write operations". The evidence the
  finding was waiting for is a requirement the same section states, so the trigger has already
  fired.

## Decision and reasoning

**Option A.** `tracker_unsupported_operation`, `tracker_state_unreachable`, `tracker_state_conflict`
and `tracker_pagination_error` are REQUIRED spellings: where the condition each names occurs, an
implementation MUST report it under that name. The remaining categories stay RECOMMENDED, a target
vocabulary an adapter maps its transport onto.

The reasoning in one line: a name is REQUIRED where the specification's own sentences fail an
operation with it and tell a caller to branch on the result — and those sentences already exist, at
three sections, for exactly these four.

Two consequences are stated rather than left derivable:

- **Section 11.4 becomes a two-level section, and says so.** The four are marked at their bullets
  and the section states the predicate, so a category added later is levelled by argument rather
  than by where it lands in the list.
- **The other seven keep a level that now means something.** RECOMMENDED was previously the level of
  every entry including four the document required; it now describes only entries nothing branches
  on.

**Openness, and the section next door.** Section 5.5 states that its class set "is not closed: an
implementation MAY define additional classes… It MUST document any class it defines", and
`CONFORMANCE-STATEMENT-TEMPLATE.md` carries the matching row. Sections 11.4 and 10.6 are both silent
on openness and neither has a row, so an implementation that adds a tracker or agent category today
adds it invisibly. Both gain the clause and both gain a row. Doing 11.4 alone would close the
reported instance and leave the identical hole one section away — and would install between 11.4 and
10.6 the asymmetry this decision removes between 11.4 and 17.3. `conformance/README.md`'s "Sections
10.6 and 10.4 share three spellings (recorded, not a defect)" entry is the standing note that 10.6
was already under examination for a different reason.

**No vector is owed.** A requirement level is an assignment, not a value computed from inputs, and
every file in `conformance/vectors/` is a one-shot pure function. The tracker read and write surface
is deferred to the `Real Integration Profile` (Section 17.8) for the reason `conformance/README.md`
states: what needs a live tracker is producing the record.

**Reconsideration triggers.**

- A tracker adapter whose backend makes one of the four conditions unreachable *and* which needs a
  different token for a near neighbour — a tracker with no state graph, where "unreachable" and
  "conflict" are one condition. The predicate would then be selecting a token for a guarantee that
  backend does not offer, and the level would need to become conditional on the capability
  descriptor rather than flat.
- A second consumer branching on one of the seven. If a recovery rule ever disposes of a tracker
  failure by whether it was `tracker_api_status` rather than by where it occurred, that token has
  acquired the property the four have and should be re-levelled with the same argument.
- An implementation reporting that the two-level section is read wrong in practice — entries whose
  level a reader assigns by position rather than by the marking. That is the cost Option B avoids,
  and it would be evidence for paying B's price instead.

## What the plan review changed (2026-08-28)

Running `python3 scripts/check_plan_anchors.py` on the plan before its first edit found one
misattributed quotation and one convention the plan had got wrong in a way all three of this
session's plans shared.

- **A phrase attributed to the section that owns the construct rather than the section that says
  it.** The plan's predicate step quoted "never silently no-oped" against Section 11.7, the section
  defining the capability descriptor. The phrase is Section 17.3's, at `SPEC.md:5313`. The step now
  names Section 11.7 for the construct and Section 17.3 for the check it states, which is also the
  more useful pair: the predicate turns on a guarantee being checkable, and the check is the
  evidence that it is.
- **The addressing pair, written with quotation marks, reads as a claim about the corpus.**
  `CLAUDE.md` requires a section number to be "paired with its title — e.g. `Section 8.4 "Retry and
  Backoff"`", and `check_plan_anchors.py` treats a quoted span as a claim to verify against the
  section *body*, where a title occurs only in the heading. Every such pair therefore reported as a
  span that "does not occur there". Decision 0161's applied plan does not hit this because it writes
  the pair in parentheses — `Section 5.3.4 (hooks.workspace)`. The mechanism is inherent rather than
  incidental: `section_body`'s heading pattern is `^#{2,5}\s+<number>\.?\s+\S`, so the body it
  returns begins *after the title's first character* and a full title can never occur in the section
  it titles. A quoted pair therefore fails for every section in the corpus, not for some. Five pairs
  per plan were converted, which removed the whole class: 8, 13 and 10 findings across the three
  plans fell to 3, 7 and 4, all of them the R class that decision 0161's own reviewed plan also
  carries. `CLAUDE.md` now states the parenthesised form and why, so the next plan does not
  rediscover it; repairing `section_body` instead was considered and not done, that function being
  shared by four checks in `scripts/validate_spec_consistency.py` whose reads would change with it.
