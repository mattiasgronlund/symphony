# Background — 0168 A published property with one value left

## Context

Reported from `symphony-rs` as issue #144, against `5a4fdf7`. `SPEC.md` Section 5.5 (Workflow
Validation and Error Surface) states one dispatch gating behavior for all five of its error classes;
`conformance/vocabulary.json`'s `error_classes` group carries a three-two split across the same five
tokens — `blocks_dispatch` on the three workflow classes, `fails_attempt` on the two template ones.

## The mechanism

**Which side is the later writing is not a judgement call.** Measured at `363acfb`:

```
$ git log --oneline -S'"gating"' -- conformance/vocabulary.json
1a15eb6 The error class names the condition, and the error tokens as data (0102)
$ git log --oneline -S'none blocks new dispatches for the' -- SPEC.md
81b79f2 Apply 0160: where WORKFLOW.md is read from, and whose it is
```

One commit each. Decision 0102 wrote the split into the registry; decision 0160 removed it from the
prose and did not touch the corpus. 0160's own chapter lists the collapse among its consequences —
Section 5.5's "two-behavior dispatch gating collapses to one, the split having existed only because
the file was assumed preflight-checkable". So the prose governs and the registry is stale, which is
the half the report asks about and the half that is not in question.

**The repair the report implies is the wrong one, and 0102's own test says why.** From 0102's
chapter, explaining why `error_classes` carries `gating` while the failure-class group carries no
recovery disposition at all:

> The contrast with `error_classes` carrying `gating` is deliberate: Section 5.5 states gating as a
> **two-valued property**, Section 14.2 states paragraphs of behaviour.

`gating` earned its place because the property was two-valued — there was a choice per entry, and
publishing it saved a consumer from deriving it. 0160 made it one-valued. Flipping three entries to
`fails_attempt` leaves a five-row table in which every row says the same thing, which is what 0102
declined to add for recovery dispositions on 0071's line that entries carry the properties the
specification fixes rather than the prose of the rules those properties feed.

**Section 5.5 fixes the arity, not merely the current values.** Its extension clause:

> The set is not closed: an implementation MAY define additional classes for conditions these five
> do not name. It MUST document any class it defines, and each one takes the dispatch gating
> behavior below, **there being one**.

So gating is now a property of the *section* rather than of the *entry*, and no future entry —
including one an implementation defines for itself — can reintroduce a split without that sentence
changing first. A per-entry field cannot become informative again while that clause stands.

**The only consumer confirms it from the other end.** The question was put to `symphony-rs` before
recording, because removing the field is a larger downstream edit than flipping three constants and
the answer could have falsified the reasoning above. It did not:

> `ErrorClass::gating()` is called in exactly one production site in this repository,
> `WorkflowConfigFault::gating()` ... Every other call is in a test. ... **no dispatch path, no
> recovery path and no report reads the value to decide anything.**

That build's own conclusion is the sharper statement of the argument: "a field whose every entry
reads the same is one an implementation reads once and then hard-codes, which is worse than not
publishing it." It reversed from the flip its issue implicitly asked for.

**A third site carries the same staleness, and it is the one that asks a consumer for a wrong
answer.** Found while confirming the report. `CONFORMANCE-STATEMENT-TEMPLATE.md`, Section 4.1:

```
| Workflow/template error classes defined beyond Section 5.5's five | 5.5 |
  `<token + dispatch gating behavior for each, or none>` |
```

The template asks an implementation to state a gating behavior for each class it defines. Section
5.5 does not let it choose one. So a Statement generated from that template either records a value
the specification already fixed — harmless but noise — or records a different one, which is a
non-conformance the template invited. Its two neighbouring rows, for the tracker and agent-runner
error categories, ask for `<token + condition for each, or none>`, which is what this row should
have asked for once the behavior stopped being a choice.

## Options considered

- **Option A — remove `gating` from the five entries, state the one behavior in the group's `note`,
  and correct the template row** to ask for the condition rather than a behavior.

  Trade-offs: it is the largest downstream edit of the three — a generated accessor disappears
  rather than changing what it returns. It also removes the last machine-readable trace of the
  gating behavior from the corpus, which is the objection `symphony-rs` raised and Option C answers.

- **Option B — flip the three `blocks_dispatch` entries to `fails_attempt`** (the report's implicit
  ask, and its build's initial position).

  Trade-offs: much the cheapest, and it has a real argument: it keeps every consumer's generated
  accessor compiling, and it leaves the schema able to express a split if Section 5.5 ever
  reintroduces one, at no cost today. It loses because Section 5.5's extension clause has fixed the
  arity at one, so the room it preserves is room the specification has closed; and because a
  five-row table with one repeated value is read once and hard-coded, which publishes nothing while
  looking as though it publishes something.

- **Option C — remove the per-entry field and add a group-level scalar `gating`**, so the value
  stays data rather than becoming prose. `requirement_level` and `exhaustive` are precedent for a
  group-level scalar property.

  Trade-offs: this is the strongest alternative, and it answers `symphony-rs`'s closing objection
  directly — the value stays machine-readable, at the arity the specification actually fixes, and a
  generator emits one constant instead of losing a method. It loses on what a consumer would *do*
  with the constant. A published token earns its place by removing a choice a consumer would
  otherwise have to make: an enum to close, a match to write, a spelling to transcribe. There is no
  longer a branch here — the behavior is the dispatch path's, unconditionally — so the generated
  constant is one nothing reads, which is the same defect as Option B's repeated column with one
  row instead of five.

## Decision and reasoning

**Option A.** The field existed because there was a choice to publish. There is no longer a choice,
so there is nothing to publish and only something to state.

**On `symphony-rs`'s closing objection**, which is the part worth answering rather than noting. They
observe that after the field goes, Section 5.5's "every class carries a behaviour" obligation "would
then rest entirely on prose with nothing in the registry to check it against", and suggest the
extension clause is where it would have to say so.

The objection is well-founded and aimed one site to the left. Section 5.5 does not require an
implementation to *carry* a behavior; it **assigns** one — "each one takes the dispatch gating
behavior below, there being one". There is nothing for an implementation to get wrong, so there is
nothing to check. What survives is the obligation to document any class it defines, which is a
Conformance Statement obligation and not a registry one, and which the template row already carried
— while asking for the wrong thing beside it. So the concern lands squarely on the template row, and
that row is what this decision fixes; the registry needs no replacement check because the
requirement it would check does not exist.

**On the open-set fallback.** `symphony-rs` notes that its `WorkflowConfigFault::gating()` fallback —
an unrecognized class from another implementation's envelope takes the blocking behavior — becomes
the only rule rather than a fallback. Under Section 5.5 that fallback is now wrong rather than
merely redundant: an unrecognized class defined by another implementation takes Section 5.5's one
behavior, which fails the attempt and blocks nothing. That is theirs to change and is recorded here
because it is a consequence of this decision rather than of their build.

## Reconsideration trigger

Reopen if Section 5.5's extension clause is revised to let a class choose its gating, or if a second
behavior is introduced for any class. Either would restore the arity the field was for, and the
field returns per entry — a schema addition rather than a value change, which is the honest cost of
having removed it.

A second trigger is a consumer that needs the behavior as a generated constant for something other
than a branch — a Statement generator emitting the value, say. Option C is then the answer rather
than Option A, and the evidence to look for is a consumer naming what it would do with the constant,
which is precisely what this decision could not find one of.
