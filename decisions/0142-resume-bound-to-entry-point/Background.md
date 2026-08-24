# Background — 0142 A resume token that named a point and not the invocation it belongs to

## Context

Issue #104 was filed by the `symphony-rs` build against `VCSX-SPEC.md`. Section 8.1 fixes three
things a `resume` is established against and says nothing about the entry point that issued it:

> An engine MUST refuse a `resume` it cannot establish as its own and current — one issued under a
> different policy, against a different repository, or by a different major version — before the
> policy runs (Section 8.6), rather than re-entering a point that no longer means what it meant.

Section 8.6's row is the same three, and Section 13.1's Resuming row names **one** of them ("a token
issued under a different policy is refused with `resume_unusable` before the policy runs") and no
other condition anywhere.

So a `resume_token` a `ship` returned may be supplied to `land`, or to a bare `push`, and no row
refuses it. The entry point is absent from all three lists, while Section 8.1 is the section that
defines the entry points and Section 8.6 is the section that scopes almost every other precondition
by them.

## The failure path

A `ship` token can name a point `land` would never reach: `ship` never runs `merge` (Section 12.2),
`land` never runs `create_pr` (Section 12.3). A consumer that crossed them made an error the engine
can see, does not report, and proceeds past.

Both readings are faithful, and an engine has to pick one before it can be written — so the
divergence is real rather than theoretical, and it is *documented* rather than prevented. The
Conformance Statement template already carries "Form of the `resume_token`, and how the engine
establishes that one it is handed is its own and current". Two conforming engines can therefore
answer it differently — one refusing a crossed token, one accepting it — and both are Section
13.3-compliant while a consumer that works against one gets a different result from the other. That
is the shape decision 0134 closed for the trigger vocabulary: a value that validates on one engine
and is refused by another, with the Statement recording the divergence instead of removing it.

The consequences are asymmetric, and the asymmetry points one way. Accepting a crossed token costs
at most an operation the caller could have invoked directly. Refusing one costs a re-invocation from
the entry point — which is the trade Section 8.1 already names, in the direction of refusing: "a
refused resume costs a re-invocation from the entry point, where an accepted stale one runs an
operation the policy no longer routes."

## Decision

**Bind the token to the entry point that issued it**, and state the condition in the general form
that subsumes the entry-point test:

1. **Section 8.1's refusal list gains a fourth condition**, mirrored in Section 8.6's
   `resume_unusable` row: a `resume` whose flow is not expressible in the invocation being resumed.
   The entry-point crossing is the case that decides it — the entry point named on the resuming
   invocation differing from the one that issued the token, so `ship`→`ship` and `push`→`push` pass
   and every crossing fails, with no dependence on what the point happens to name.
2. **Section 13.1's Resuming row stops naming one of the conditions and names the set**, or it
   drifts again the next time one is added.
3. **The Conformance Statement row narrows to the form question.** What stays is a real question —
   an engine answers it with a versioned record carrying a format tag, the major, fingerprints, the
   spent count and the point, and whether it is signed at all is forced by Section 1.3, which leaves
   the engine no key to hold between invocations. What leaves the cell is *whether a crossed token
   is refused*, which was never a form question.
4. **Section 8.1 enumerates `await_first`**, with its default (unset — `land` merges without
   awaiting), like every other argument in that section.
5. **The sequence-selecting property is fixed in prose where it has a referent**, and one sentence
   states what a resumed invocation does with such an argument: it is not consulted.
6. **The registry gains an `arguments` group**, closed from the start, carrying Section 8.1's
   argument names and the per-argument properties that section already states as prose.

Parts 4–6 are what make part 1 statable; the reasoning for each is below.

### The argument that decides it, which neither the report nor the first recommendation made

Binding gives `resume_unusable` a **decidable** judgement at the entries where its stated inputs do
not exist. Section 8.6 judges the reason "wherever a `resume` was supplied, whatever the entry, and
from the invocation's arguments together with what the engine holds independently of them — the
policy it validated and its own major version". At `provision` the policy half has nothing to
compute over: Section 6.1 calls it "the one entry point that runs where no policy could be read",
and Section 8.6 nonetheless places `resume_unusable` inside `provision`'s otherwise-exhaustive list
— "Those three reach `provision` for the reason they reach every entry: what they judge is a value
the invocation named."

The entry-point field settles that without reaching for the policy at all: `provision` never issues
a token, so every token supplied to it mismatches on that field alone. The same holds for
`load_policy` once decision 0141 makes it an entry point — it dispatches nothing and escalates
nothing, so it can issue no token and refuses every one for a **stated** reason. The reporting
engine refuses at those entries today on its own fail-closed judgement; the fourth condition
replaces a local choice with a specified one.

### It costs nothing new

- `resume_unusable` already exists, and Section 8.6 already scopes it "wherever a `resume` was
  supplied, whatever the entry" — the scoping rule the fourth condition needs is written.
- No new token, so no Section 13.3 obligation and no Conformance Statement row (decision 0128's trap
  does not fire).
- The engine's judgement becomes complete from what the token must already carry: it already
  establishes the policy, the repository and the major version.
- It **narrows** an existing template row rather than adding one — the same move 0134 made when it
  narrowed three rows and added none.

## Options considered

### Declare the three-item list exhaustive, and make the token portable across entry points

The steelman is better than it first looks:

- **Section 8.6 enumerates rather than exemplifies everywhere else in that table**, so a three-item
  list reads as the whole of it. An *engine* adding a fourth condition is widening a precondition
  registry the same section says an engine MUST document additions to.
- **What the token names is a point**, and Section 5.5's point is an operation or a lifecycle
  position. An operation is a Section 8.1 entry point in its own right, so a `ship` token supplied
  to `land` re-enters an operation that caller could have invoked directly, through the same policy,
  with the same gate.
- It costs one clause and leaves every engine's current behaviour conforming.

It loses on its own first argument. The objection is true of an engine acting unilaterally, which is
exactly why the *specification* should decide it — left open, the registry-widening worry is
realized in the worse form, as two engines that differ. And the second argument does not survive the
case a crossed token actually creates: a `ship` token can name a point `land` never reaches, so "the
caller could have invoked it directly" is false precisely where the crossing matters.

## Recorded: the case withdrawn, and why

Two crossings were raised that entry-point equality does not catch, both under `land`'s
`await_first`. One is uncovered; the other was withdrawn, and the withdrawal is worth keeping
because the reasoning generalizes.

- **Await-branch token → bare `land`** — genuinely uncovered. The point is not in the sequence being
  run, so there is nothing to re-enter, and `resume_unusable` is right. This is what "expressible in
  the invocation being resumed" reaches and the bare entry-point test does not.
- **Merge-loop token → `land --await`** — **not** refused. Section 5.5 re-enters the point that
  raised the need "rather than beginning at its entry point", so the sequence's prefix is not run
  and the wait is not skipped so much as never entered. Refusing it would refuse a token for an
  argument the resumed invocation was never going to consult, and would make a resumed invocation's
  legality depend on a flag that does not change what it does. What that case needs is a sentence,
  not a refusal: arguments that select among an entry point's sequences are not consulted on a
  resumed invocation — and a caller that wants a wait dispatches `await_checks` itself, which is
  exactly the composition Section 7.2 already says `--await` is.

## The step-zero finding: the replacement sentence had issue #100's defect

The sentence above — "arguments that select among an entry point's sequences are not consulted on a
resumed invocation" — was drafted and then found to be stated over a class Section 8.1 does not
define. Section 8.1 enumerates arguments; nothing there marks which of them select a sequence, so an
engine reading the sentence decides for itself whether `--await` is one, whether `policy_source` is
one, and whether the next parameter added is one. Two engines that decide differently are both
conforming. **That is issue #100's defect — a condition that cannot be evaluated from the specified
configuration — reproduced in the repair for a different one, in the same batch, one document
over.**

And the specific argument it was written for is in a worse position than unmarked: **`await_first`
is not in Section 8.1 at all.** That section enumerates four await parameters — `await_bound_ms`,
`await_max_reads`, `await_interval_ms`, `await_budget_floor` — and no sequence selector. The concept
appears only in Section 7.2's prose ("Under `--await` — or whatever the front-end's encoding for it
is (Section 8.1)") and in Section 12.3's signature `function land(await_first)`. So Section 7.2
cites Section 8.1 for an argument Section 8.1 does not carry, while Section 8.1 requires that
argument "*names* for shared concepts MUST match this specification" — and this one has no name to
match. There is nothing to mark today.

That makes the repair three steps rather than one, and the first is owed regardless of this issue:

1. **Section 8.1 enumerates it**, with its default.
2. **The property is fixed in prose, where it has a referent**: an argument that selects among an
   entry point's sequences. Today that set is derivable without a new concept — it is the parameters
   of Section 12's front-end sequence functions: `ship()` takes none, `land(await_first)` takes one.
   That derivation is what makes the condition *evaluable*, and it inherits a future selector
   automatically, because a parameter that does not appear in a Section 12 signature cannot select a
   sequence.
3. **The registry carries the flag**, so an engine that generates from the corpus inherits it
   instead of transcribing a judgement — the two-layer arrangement decision 0141 landed on for
   operations: prose fixes the property, the registry derives it.

### The cost of step 3, stated rather than discovered

Decision 0141's `policy_dispatchable` was a field on an existing group. This is not.
`conformance/vcsx/vocabulary.json` carries twenty-one entry-bearing groups plus `task_model` —
`entry_points`, `output_keys`, `envelope_fields`, `repo_policy_sections`, `precondition_reasons` and
the rest — and **there is no `arguments` group at all**. So the flag costs a new group, authored
against Section 8.1's prose, which is the longest enumeration in the document.

It is owed anyway, and this issue is the second demand for it rather than the first:

- Section 8.1's argument *names* are normative, which is the property every other group in that file
  exists to pin.
- The section already carries per-argument properties as prose lists: the consumer-configuration
  exception ("the two read validators and `resume` excepted"), and per-entry requiredness spread
  across a dozen "REQUIRED for … its absence is refused before the policy runs (Section 8.6)"
  clauses. A second prose list beside the first is how issue #100 happened; the first list is
  already unmaintained-by-construction.
- And it is about to grow: decision 0141's policy pin makes the excepted set **four**. That is the
  third hand-maintained membership in the same section inside one batch of issues.

Create the group and let it carry the properties Section 8.1 already states — optionality, the
consumer-configuration exception, and `selects_sequence` — rather than creating it for one flag. It
must be **closed** from the start: `validate_spec_consistency.py`'s check 6 walks closed groups
only, and `entry_points` not being one is what let decision 0141's drift stand.

## The dependency, which is firm rather than preferred

"Expressible in the invocation being resumed" is decidable only once issue #103 enumerates the
sequence points. Today there is no enumeration to test membership against, so the condition would be
a rule an engine could not evaluate — issue #100's defect a third time. The entry-point half, the
Section 8.1 enumeration of `await_first` and the `arguments` group are applicable now; the general
phrasing waits on #103's decision and is stated in its terms.

The strength of the answer also depends on #103, though not its direction. If a resume continues the
front-end sequence, binding is close to forced: the token names a point in a *sequence*, so a `ship`
token supplied to `land` asks the engine to continue a traversal the invocation is not running, and
there is no coherent behaviour to define for it. If a resume re-dispatches the point and stops,
binding still holds on Section 8.1's own trade, but a crossed token then re-dispatches one operation
the caller could have invoked directly — which is the case where the exhaustive reading is genuinely
defensible.

## What was checked

At `97617c2`, against the working tree:

- Section 8.1's refusal sentence and Section 8.6's `resume_unusable` row name the same three
  conditions; Section 13.1's Resuming row names one.
- Section 8.6 judges `resume_unusable` "wherever a `resume` was supplied, whatever the entry", and
  places it among the three that reach `provision`.
- Section 8.1 enumerates four await parameters and no sequence selector; `await_first` occurs in
  `VCSX-SPEC.md` only at Section 12.3's signature and its inline comment, and `--await` only in
  Section 7.2's prose and one Section 13.1 row.
- `conformance/vcsx/vocabulary.json` carries twenty-one entry-bearing groups plus `task_model`, and
  no `arguments` group. `precondition_reasons` carries fifteen tokens including `resume_unusable`.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` carries one `resume_token` row, citing Sections 8.1, 8.2
  and 8.6.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## Reconsideration triggers

- **Issue #103 landing narrow** — a resume that re-dispatches the point and stops. The binding still
  holds, but the "no coherent behaviour" argument weakens to a cost argument, and a later reader
  re-opening this should know which argument they are re-opening.
- **An entry point gaining a second sequence-selecting parameter.** The prose derivation (parameters
  of a Section 12 signature) is what should absorb it; if a selector ever appears that is *not* a
  Section 12 parameter, the derivation is wrong rather than incomplete.
- **A consumer with a legitimate reason to cross entry points** — a driver that composes its own
  sequence and wants to resume a `ship`-issued point under a bare operation. Section 8.1's trade is
  what it would have to argue against.
- **The `arguments` group proving unmaintainable against Section 8.1's prose.** If authoring it
  shows the enumeration is not actually a list of tokens, that is evidence the section needs
  restructuring rather than that the group is wrong.
