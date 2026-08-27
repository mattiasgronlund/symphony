# Background — 0153 A resume continues the flow, and the token carries the root trigger

## Context

Issue #103. Section 5.5 says what a resume re-enters and stops there. **No section says what happens
after that re-entry produces a result.** For an entry point that is a single operation the question
does not arise — the invocation reports the result and ends. For a front-end sequence it does:
Section 12.2 writes `ship` as a sequence with steps after each dispatch, and a `ship` that escalated
at `push` either reports the re-dispatched `push` and stops, or carries on to `create_pr`.

Every passage on the subject is about the re-entry and none is about what follows it — Section 5.5's
"A resume re-enters **the point that raised the need**", Section 8.1's "the invocation re-enters the
point that raised the need rather than beginning at its entry point", Section 8.2's "an opaque token
naming the point that raised the need and the flow bound already spent", Section 13.1's Resuming
row.

Two conforming engines, one policy, one token, two different results: a caller that resolves
`resolve_conflicts` and re-invokes `ship` gets, from one engine, `integrate:ok` and no pull request
and must invoke `ship` again; from the other, the pull request. Both are faithful to Section 5.5,
and a consumer cannot tell which it has without running it.

## The argument that decides it: the narrow reading defeats Section 5.6's accumulation

Section 5.6 states the property this whole area exists to hold:

> Stated over the invocation instead, the bound would hold for an embedded driver whose resolver
> returns inside one run and not for a front-end that returns to its caller and is invoked again — so
> the answer this section gives to non-termination would depend on which front-end asked.

Trace the narrow reading against exactly that front-end. `ship` escalates `resolve_conflicts` at
`integrate:merge_conflicts` with a token carrying count `N`. The caller resolves and re-invokes with
the token. The engine re-dispatches `integrate`, gets `integrate:ok`, and — narrowly — reports it
and stops. The invocation ended at `done`, so **no new token is issued** (Section 8.2: the key is
absent where `status` is not `needs_caller`). The count `N+1` is discarded. To get a pull request
the caller must now invoke `ship` afresh, with no token and a fresh budget.

So under the narrow reading the accumulated count is thrown away at the first successfully-resumed
invocation, and a resolve-and-resume loop never exhausts for the interactive front-end while it does
for a driver whose resolver returns in process. That is precisely the divergence Section 5.6 is
written to prevent, and Section 13.1's row — "a resolver that resolves every time reaches
`flow_exhausted` **across invocations** and not only within one" — becomes false for one of the two
front-ends.

This is verified against a build implementing the narrow reading rather than argued in the abstract:
`Engine::resume` re-enters the point, disposes of what it produces, and stops; the token is minted
only where an escalation carries one out (`crates/vcsx-engine/src/op.rs:961`); Section 8.2 puts
`resume_token` in `outputs` only at `needs_caller`. A resumed invocation that re-dispatches
successfully ends `ok`, issues no token, and drops the accumulated count on the floor. That build
changed position on this argument, having weighed and not found it when it chose.

## Two supporting arguments

- **Section 5.4 already names the disposition, and its name is "continue".** The re-dispatched
  operation's result re-enters the machine as any result does. `integrate:ok` matches no edge, class
  `done`, built-in default: *continue*. Under the narrow reading the engine would need a fourth
  disposition — "end the invocation reporting the result" — that Section 5.4 does not provide. Under
  the wide reading "continue" means the same thing everywhere: proceed with the remainder of the
  traversal, which for a bare-operation entry point is empty and for a sequence is the rest of the
  sequence. **The narrow reading is the one that needs a new rule; the wide one falls out of the
  rule already there.**
- **Section 7.1 states `ship`'s contract over what it drives**, "up to and including opening or
  updating the pull request". A resumed `ship` that reports `integrate:ok` did not do that.

## What the narrow reading would have cost, if it had been taken

Recorded so the trade stays legible rather than implicit. Section 5.6's accumulation paragraph and
Section 13.1's Resuming row would both have to be weakened to say the bound holds across resumed
re-entries and **not** across a caller's fresh re-invocation — which is the property those two
passages were written to assert.

And the narrow reading was **not unreasonable**: it is what Section 5.5 and Section 8.2 literally
describe today, both of which enumerate a two-element token. This decision is changing those
sentences, not correcting a misreading of them.

## Where the opacity argument actually points

Section 8.1's opacity paragraph was read on the issue as support for the narrow reading:

> an engine that published its structure would owe a stable spelling for "the point that raised the
> need" across every graph shape a policy can express — a schema for the executor's traversal, in
> exchange for nothing a consumer does with it.

It argues the engine will not **publish** a spelling, which is an argument for the token carrying
*more* behind an opaque wrapper rather than less: a consumer that cannot read the value cannot be
owed stability for what is inside it. The sentence immediately before it — "the value is the
engine's own rather than another party's" — cuts toward the engine being free to put more in it.
What it still argues against is a token whose **size** grows with the policy graph, which is what
the fixed-width constraint below is for.

## What the token carries: three fields, and the third is a trigger

Section 5.5 defines *point* concretely as an operation or a lifecycle position, and Section 8.2 says
"The token carries the point and the count and nothing a lifecycle position established." That is
not enough to continue Section 12.2 from the middle, and the two-element description is the real
obstacle rather than the opacity.

The reason a point is not enough is worth stating precisely, because it is what fixes the third
field. Section 12.2's `push` sits inside a loop with `create_pr` after it, and a repository that
binds `push:non_fast_forward → run_op integrate` produces an `integrate` dispatch that sits
**nowhere** in the sequence. Section 5.4 says its result "takes its place in the machine" — the
machine, not the sequence. So a resumed `integrate` has two legitimate continuations, distinguished
only by *how the dispatch was reached*, and a single-valued cursor cannot name one.

Decision 0143 supplies the object that resolves it. Under that decision a repository edge replaces
the built-in **disposition** of the trigger; where the disposition returns control to the sequence
the **control transfer** is the trigger's and is unchanged; where it ends the flow the invocation
ends; where the transfer is `return` the sequence reports the result the machine last handed back —
with the transfer selected by the result of the **sequence's own** `run_op`, every substitution
inside the machine invisible to it.

So the token carries:

- **the operation or lifecycle position to re-enter** — Section 5.5's point, unchanged;
- **the sequence's own `run_op` result the chain descends from** — 0143's root — where the point is
  not that dispatch itself;
- **the count.**

Two sharpenings on the second, both of them decision 0143's doing rather than this decision's.

**It is a trigger, not a sequence position.** Under 0143 the position is not an independent value:
the transfer is a property of the trigger, and the trigger has exactly one position because the
sequence tested it. So the token names the trigger and the position is derived — which is what keeps
an engine from owing "a stable spelling for the point that raised the need across every graph shape
a policy can express", the thing Section 8.1's opacity paragraph says it should not. A token
carrying a position would owe that spelling; one carrying a trigger owes the trigger vocabulary,
which Section 5.1 and the registry already publish. Section 5.4's tail-replacement bounds it: a
chain of any length descends from one root, so one trigger rides and the token stays **fixed-width**
— one operation-or-position, one trigger, one count, none growing with the graph.

**It is the root, not "the trigger an edge replaced".** The field is owed on paths where no edge
fired at all: Section 12.2's built-in routes `push:non_fast_forward` to `integrate` itself and
escalates `integrate:merge_conflicts`, so a resumed `integrate` needs `push:non_fast_forward` to
know that its landing is the push retry. Phrased over substitution the field would be absent exactly
there. Where the point is a lifecycle position the field is unneeded — the gated operation proceeds
and its own result is the root — which is the loop Section 5.6 already describes.

**Spell the trigger by its registry token, not by an ordinal.** A trigger encoded as an index into a
generated enumeration decodes, after a MINOR insert upstream shifts every ordinal, into a
*different* trigger — silently, from a record that still looks valid. This is not hypothetical: the
`symphony-rs` engine writes the operation in its own token by registry token for exactly that reason
(`crates/vcsx-proto/src/resume.rs:149-158`). "The token carries the trigger" reads as satisfied by
either encoding and only one of them survives a MINOR.

**The `MUST NOT` over position-established state is untouched.** A trigger is not something a
lifecycle position inspected; it is control-flow state of the same kind as the count the token
already carries. Nothing about `expected_worktree` or `expected_head` loosens.

## What is easy to miss

- **`conformance/vcsx/vocabulary.json`.** Its `output_keys` entry for `resume_token` says in its own
  words "It carries the point and the count and nothing a lifecycle position established". That is
  the registry restating the two-element description, so it moves with the sections. A corpus note
  asserting what the specification no longer says is decision 0132's drift class.
- **Section 13.1's Resuming row**, which describes the re-entry and never the continuation.
- **`VCSX-CONTRACT.md` Section 5.6.** The contract restates the resume in its own words — "A resume
  re-enters the point that raised the need, and it round-trips through the consumer … the flow bound
  accumulates across a resumed chain rather than restarting" — and carries **the same silence**,
  stopping at the re-entry. It does not carry the token's enumeration and should not gain one, but a
  reader of the contract alone is left with the question this decision answers. Found by
  `scripts/check_plan_anchors.py` reporting it as a site carrying the quoted phrasing that this
  decision's plan did not name; recorded because it is the layered document doing what the derived
  artifacts do — restating a sentence rather than citing it, and therefore drifting silently.
- **The format revision.** This decision adds a part to the token and decision 0142 adds another —
  the entry point. Landed together that is **one** format revision; landed apart it is two, and a
  token issued between the two decodes on no build that has taken either. The two decisions are
  separable in substance and not in encoding. Worth stating in whichever plan goes second rather
  than being discovered when the second one bumps a tag the first just bumped.

## Options considered

### The narrow reading, stated explicitly

A resumed invocation re-enters the point, reports that result and ends; the caller re-invokes the
sequence, which is idempotent step by step — a clean working tree dispatches no `commit`, an
existing pull request is updated rather than opened again. It needs **no change to Sections 12.2 and
12.3**, it is what Section 5.5 and Section 8.2 literally describe, and it keeps the token at two
elements, which is the strongest form of Section 8.1's fixed-width concern.

It loses on Section 5.6's accumulation, above: the count is discarded at the first successfully
resumed invocation, so a resolve-and-resume loop never exhausts for one of the two front-ends. That
is the specific divergence Section 5.6 exists to prevent, and Section 13.1 asserts the property it
breaks.

### The wide reading with a sequence cursor rather than a trigger

The first form the wide reading was proposed in: the token names a position **in the sequence**. It
loses twice. It owes the traversal schema Section 8.1 says an engine should not publish, since a
position needs a stable spelling across every graph shape a policy can express. And after decision
0143 it is redundant: the transfer is a property of the trigger and the trigger has exactly one
position, so a cursor would be a second spelling of a derived value — which is the defect issue #100
reports one document over.

### The wide reading with the trigger stated over substitution

"The trigger an edge replaced." Rejected because the field is absent exactly where it is most
needed: Section 12.2's built-in routes `push:non_fast_forward` to `integrate` with no edge involved,
and a resumed `integrate` there has no way to know its landing is the push retry.

### Answer this together with issue #104's entry-point binding

Proposed on the issue, and it was right at the time: under a cursor, a `ship` token supplied to
`land` continues a sequence the invocation is not running, which forces #104's fourth refusal
condition. Decision 0142 has since settled that condition on the entry point alone and withdrawn the
sequence-selecting property, so nothing here forces it and nothing there waits on this. The two
remain coupled in **encoding** rather than in substance — see the format-revision note above.

## What was checked

At `22b5194`, against the working tree:

- Section 5.5's "A resume re-enters **the point that raised the need**" paragraph and its "it
  carries the point to re-enter and the flow bound already spent, and it MUST NOT carry
  `expected_worktree`, `expected_head`, or anything else a position established" sentence are
  verbatim as quoted.
- Section 8.2's `resume_token` bullet ends "The token carries the point and the count and nothing a
  lifecycle position established (Section 5.5)", and the key is absent where `status` is not
  `needs_caller`.
- Section 8.1's opacity paragraph is verbatim as quoted, and precedes the refusal sentence decision
  0142 extends.
- Section 5.6 bounds a flow "by a count of `run_op` dispatches and resume re-entries" and states "an
  `escalate` ended and a resume continued is one flow, and a resumed invocation continues from the
  count its `resume_token` carries rather than starting a fresh budget".
- Section 13.1's Resuming row asserts "a resolver that resolves every time reaches `flow_exhausted`
  **across invocations** and not only within one, the bound being over the flow".
- Section 12.2's push loop routes `push:non_fast_forward` to `integrate` built in and escalates
  `integrate:merge_conflicts`; Section 6.5's example policy binds the same trigger to `run_op
  integrate`.
- `conformance/vcsx/vocabulary.json`'s `output_keys` entry for `resume_token` restates the
  two-element description verbatim.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## Found while applying this, at `2cba688`

**The token's contents had leaked into two places that describe its *form*, and the plan named
neither as a step.** Both were reached because the plan's Cross-cutting sync said to check the
`resume_token` form row rather than assume it, and the check fired twice. Neither owed a **new**
Conformance Statement row — the plan's prediction was right, this decision creating no
`Implementation-defined` choice and no MUST-document obligation — but each owed an edit to a row
that already existed.

`VCSX-SPEC.md` Section 13.3 read "the form of the `resume_token` — what it encodes, whether it is
signed". Before this decision the token's contents were the engine's, so *what it encodes* was an
accurate name for what an engine declares. After it the contents are the specification's, and the
same phrase reads as licence over them: an engine could answer that row with a two-part token and
point at Section 13.3 for the permission. Narrowed to "how it spells the three parts Section 5.5
fixes", which keeps the obligation and moves the boundary back to spelling.

`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`'s matching row went further: its answer field enumerated
the two parts literally, `<the point and the spent flow-bound count; …>`. That is decision 0132's
drift class one artifact further out than step 9 reached — a restatement in the template's own words
rather than a citation — and it is the failure mode `CLAUDE.md` records from decision 0128 read from
the other side: the row existed, so no check reported it missing, and a Statement generated from it
would have published a two-part token under a three-part specification with every table complete
against itself. Both edited; the template row's `Section` column gains `5.5`.

**The consumer-observable half and the implementer-only half were separated deliberately.** Section
13.1's Resuming row takes the continuation, which a caller can observe: a resumed `ship` reaches
`create_pr` or it does not. The fixed-width property and the registry-token spelling went to Section
13.2 instead, because the token is opaque (Section 8.1) and no conformance test can look inside one
to check either. Putting them in the test matrix would have written a row no test can fail.

**Step 10's prediction was checked rather than taken, and it is the claim that could most easily
have been wrong.** `conformance/vcsx/vectors/resume-precondition.json` reasons from "the branch
ahead of the re-entered point is never run", and the plan asserts a forward continuation leaves that
true. It does, but only because *ahead* names the prefix rather than the remainder: Section 12.3's
`await_first` branch sits before the merge loop, and Section 8.1's own paragraph confirms the
reading — "the await branch runs once, before the merge loop a resume re-enters". Had *ahead* meant
*later in the sequence*, the continuation would have run exactly what the vector says is never run,
and the vector's expectation would have moved. Section 8.1's paragraph now says "the prefix, not the
remainder, which it continues into", so the reading the vector depends on is stated rather than
inferred from an example.

## Reconsideration triggers

- **A front-end sequence whose steps are not reachable from a trigger's position.** The whole
  derivation rests on decision 0143's "the trigger has exactly one position because the sequence
  tested it". A sequence step that no trigger identifies would need a cursor after all, and the
  opacity objection would have to be paid rather than avoided.
- **A policy shape where one trigger's chain has more than one root.** Section 5.4's
  tail-replacement is what makes the third field fixed-width; a disposition that composed rather
  than replaced would make the token grow with the graph, which is the thing Section 8.1 argues
  against.
- **The trigger vocabulary ceasing to be a published registry.** The choice of a trigger over a
  position is paid for by Section 5.1 and the registry already publishing the vocabulary; if that
  stopped being true the engine would owe a spelling either way.
- **Decision 0143's transfer split being replaced.** The token's third field is that decision's
  root; a different landing rule would need the field re-derived rather than carried over.
