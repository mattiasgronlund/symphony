# Background — 0133 A token that was the whole class, and a bound that was the only bound

## Context

Issues #81 and #82 were the entire open queue. Both were filed by an implementation building against
`d76844b`, both land on `await_checks`, and both are real — each was verified against the tree before
this decision was drafted.

They are the same defect twice. `await_checks` carries two enumerations that were each correct when
each had one member, and each has since gained a second member somewhere else in the document while
the sentence that reasons over it was not revisited:

- The **class** `done` had one `await_checks` reason, `ok`, when Section 7.2 was written. Decision
  0125 minted `no_checks` and Section 7.2 still names the token.
- The **await parameters** had one that could authorize a loop when Section 8.1 was written. There
  are now four, and the section says which of them *end* a wait without ever saying which of them
  lets a wait have a second read.

Neither is a wording slip. In both cases a sentence names one member of a set because at the time
naming the member and naming the set were the same act, and the distinction only becomes visible —
and load-bearing — once the set grows.

## What the defects do

### The merge that does not happen (#82)

Four artifacts carry the awaiting `land`. Exactly one drifted:

| Artifact | What it says an awaiting `land` does on `no_checks` |
| -- | -- |
| `VCSX-SPEC.md` Section 7.2 | ends on the await's result — "where that result is not `ok`" |
| `VCSX-SPEC.md` Section 13.1 | "a `land --await` against such a repository **merges** rather than ending on the await's result" |
| `VCSX-SPEC.md` Section 4.3 | both class `done`, "both continue the flow" |
| `VCSX-CONTRACT.md` Section 3 | "composes the two operations below and introduces no sequencing of its own" |

The failure path is short. A repository configures no required checks — or a required check is
dropped from branch protection, or a workflow file stops matching. `await_checks` reads once and
reports `no_checks`, which Section 4.1 states is a determinate answer that ends the wait on the first
read. Section 7.2, read literally, then ends the `land` on it: `needs_caller`, no merge. Every
awaiting `land` in that repository stops merging, and the two documents a consumer would check
against say it should have merged.

The cost lands precisely on decision 0125's own argument. 0125 split `no_checks` off `ok` so that a
merge gate that stops existing is *visible* — "under a shared `ok` nothing in the record marks the
day it changed". Section 7.2 unrepaired makes the same change *breaking*: the day branch protection
loses its last required check is the day every awaiting `land` parks. A token minted to make a silent
change visible would instead have made it an outage, which inverts the decision that minted it.

### The loop with no terminator (#81)

Section 8.1 gives four await parameters, says "an invocation supplying none makes a single read and
cannot loop", and then says which of them *end* a wait: the first two with `still_pending`, the
fourth with `budget_floor`. It never says which of them authorizes a second read, and the two
questions come apart on `await_budget_floor`.

Read as an authorization, a floor alone is a loop with no terminator. The floor is compared against
"the snapshot each read observes" (Section 9.2), and a forge that publishes no budget produces no
snapshot to compare against. Forgejo publishes none, so this is the ordinary case against one of the
two backends the reporting implementation carries, not a contrived one. An invocation supplying only
`await_budget_floor` reads until the process is killed — which contradicts Section 8.1's own "cannot
loop" and the sentence the network bound is argued from, that an engine runs a bounded sequence of
operations and exits.

`await_interval_ms` has the same shape for a plainer reason: a cadence is not an end.

The divergence is worse than the hang, because a hang at least announces itself. One conforming
engine reads a floor as authorizing a loop and hangs; another reads it as the reporter's does and
returns `still_pending` after one read. Both are defensible readings of the same sentence, so a
consumer cannot write one invocation that behaves the same on both — which is the property Section
5.4's determinism clause exists to hold.

## Decisions taken

### Section 7.2 states the class, not the token

`land --await` continues to the merge where the await's result is class `done` and ends on it
otherwise, stated as the disposition Section 5.4 already gives every operation result rather than as
a rule this composition adds.

That framing does more than fix the token. Section 7.2 already claims to introduce "no sequencing
rule of its own", and with a token in the clause the claim was false — a token-specific stop *is* a
sequencing rule. Phrased over the class the claim becomes true: the composition inherits Section
5.4's built-in defaults, and a sixth `done` reason added later needs no edit here. Issue #82 proposed
exactly this, and it is the answer.

**A separate policy-override clause was considered and declined.** The worry it addresses is real:
0125 promised that "a repository that holds it binds the reason and gets the stop", and a
class-phrased clause must not take that promise away. It does not, and the reason is that Section
5.4's wording is already conditional — "for `done` **with no edge**, continue". A repository binding
`await_checks:no_checks` to a `park` has an edge, the edge disposes of the outcome, and the flow
ends. Inheriting Section 5.4 inherits its exception, so the minimal edit is the complete one, and a
clause restating it would be a second statement of a rule the document already states once.

### Only a bound authorizes a loop, and naming a floor without one is refused

`await_bound_ms` and `await_max_reads` are what authorize a second read. `await_interval_ms` paces
reads a bound already authorized; `await_budget_floor` can only end one early. An invocation
supplying either of the latter two and neither of the former is **refused** before the policy runs,
with a new precondition reason `await_bound_missing`.

The alternative — treat such an invocation as the no-parameter case and make one read silently — is
the reporting implementation's own behaviour and was the obvious minimal answer. It loses on what it
does with the consumer's intent. An invocation naming a floor is asking for a bounded wait; making
one read and reporting `still_pending` answers a question the consumer did not ask, and answers it in
a way that looks like a wait that ran. The refusal says what is wrong — a wait was configured with
nothing to end it — at the point the consumer can still fix it, and Section 8.6 exists for exactly
the class of defect judged from the invocation's arguments alone.

The cost is a genuine expressiveness loss, recorded here rather than in a footnote: a consumer that
legitimately wants "read once, but stop early if the bucket is low" cannot say it in one parameter.
Under the refusal that invocation must also carry `await_max_reads = 1`, which is more words for the
same wait. That is a real consumer and the refusal inconveniences it. The trade is accepted because
the two-parameter spelling is available and unambiguous, while the one-parameter spelling is the one
that divides two conforming engines.

### A floor the snapshot cannot answer fires

A floor whose bucket the observed snapshot does not carry — no snapshot at all, or no bucket of that
name — **ends the wait** with `budget_floor`.

This is the opposite of what issue #81 proposed and the opposite of the recommendation put to the
maintainer, so the trade-off is stated plainly rather than justified away.

The reasoning for it: an engine that cannot establish there is room to keep spending does not keep
spending. That is the same disposition Section 9 gives every undetermined capability answer — the
engine reports rather than proceeding on an absent answer — and it makes the floor's behaviour
independent of whether a particular forge publishes a budget, which is a property a consumer can
check without knowing which backend is underneath.

The cost is concrete and falls on a real backend. Forgejo publishes no budget, so against it every
floor-carrying invocation makes exactly one read and reports `budget_floor`, and a Symphony
deployment parks on that reason. It is never a wait with no end — with the refusal above in force a
floor can only be supplied alongside a bound — but it is a wait that ends immediately and reports a
limit nobody can go and look at.

Two things bound the cost. The floor is OPTIONAL and `vcs.await_budget_floor` defaults unset, so a
deployment reaches this only by opting in. And the reason is distinguishable: a consumer seeing
`budget_floor` on the first read against a forge it knows publishes no budget can tell what happened,
which it could not if the floor were silently ignored.

The declined option deserves its own statement, because it is the one that gets revisited. A floor
the snapshot cannot answer *establishes nothing about the budget*, and continuing the wait is the
reading that treats an unanswerable comparison as no comparison rather than as a failed one — which
is how Section 9's catch-all is worded for a capability that could not determine an answer, and which
is the distinction between an absent thing and an unreadable one that 0125's own `no_checks`
reasoning turns on. That reading also keeps the floor free against forges publishing nothing, which
is the majority case in the reporting implementation's deployment. It was not chosen; its trigger is
below.

### The tie-break is `budget_floor`

Where a bound and a floor are both reached on the same read, the read reports `budget_floor`. The
order falls out of Section 8.1's own words rather than being invented: the floor is compared against
"the snapshot **each read** observes", so it judges the read just made, while the bound and the read
count decide whether to read again. Judging what a read said before judging whether to read again is
the only order that respects that sentence. Issue #81 derived the same answer the same way.

### The terminal conditions are re-framed as a read allowance

Section 4.1's fourth terminal condition — "a bound the invocation supplied was reached" — becomes the
invocation's **read allowance** ending, an invocation authorizing no loop having an allowance of one
read. Still five conditions.

The re-framing is what makes the enumeration true of every invocation. Under the old wording a
no-parameter invocation that finds the checks pending matches *none* of the five: no bound was
supplied, so no bound was reached, yet the operation must stop and report something. Under the
allowance wording it matches exactly one, and `still_pending` is the reason — which is what an engine
had to do anyway, now stated rather than inferred.

## The finding this decision's own repair turned up

Section 8.6's `provision` sentence is stale, and the edit planned for it would have made it worse.

> What remains is `arguments_unreadable`, `local_vcs_missing`, `git_access_missing` and
> `store_location_missing`, together with the forge pair where a forge is configured.

`provision` also reaches `base_branch_not_permitted` and `resume_unusable`. Both are judged "wherever
the argument was supplied, whatever the entry" — the section says so of each in its own paragraph —
and the first is asserted in the test matrix, which requires `base_branch_not_permitted` "whatever
the entry, including entries that need no base". So a sentence claiming to be exhaustive for
`provision` is short by two.

`await_bound_missing` is judged the same way and would have been the third such row omitted from a
list already missing two. Adding it silently is the repair-that-reproduces-the-defect the
`decision-record` skill names, and this decision's own subject is enumerations that fell behind their
sets. The sentence is repaired instead: it names the required-argument set plus the three judged
wherever their argument is supplied.

Recurrence count for the class, continuing 0132's: this is the fifth time an enumeration in these
documents has been found stale against a set that grew, and the second time inside the decision
repairing an instance of it. `scripts/validate_spec_consistency.py` did not catch this one and could
not have — it compares registries against prose, and this is one prose sentence enumerating what
three other prose paragraphs establish. Check 5 added here narrows the gap for the await enumeration
specifically; the general case stays open and is recorded below.

## Options considered

### Where the class repair goes

**Section 7.2 alone, stated over the class.** Chosen. It is the sentence that is wrong, the class is
already the thing Section 4.3 reasons over, and Section 13.1's existing clause becomes a consequence
of the rule rather than an exception to it.

**Rephrase Section 13.1's `land --await` sentence to match.** Declined, and deliberately: the
sentence is *correct as written*. It asserts the observable behaviour a test checks — a `land
--await` against a repository with no required checks merges — and rewriting it in the class's
vocabulary would replace a testable assertion with a restatement of the rule it tests. A test matrix
that only restates the specification tests nothing.

**Section 12.3 gains the await branch.** Chosen, and it is the half that makes the repair executable.
Section 7.2 describes the composition in prose and Section 12.3 is where `land`'s sequence is written
as pseudocode; a reader building from the algorithm found no await in it at all. The branch uses
Section 12.2's existing idiom verbatim — `if r.class != done: return result_of(r)` — because the
specification already knows how to write this, and a second spelling of one rule is how the two
drift.

### The unobservable floor

Argued above in both directions. The maintainer chose the firing disposition against the
recommendation put to them; the declined reading is stated in its own terms rather than as a foil,
because it is the one a reconsideration trigger reopens.

### Whether `await_bound_missing` is a precondition or a configuration error

**A precondition.** It is judged from the invocation's arguments alone, with no capability consulted
and no checkout opened, and what is at fault is the invocation rather than a document — which is
Section 8.6's own stated test. The policy is well formed whatever the invocation names.

It is placed with `base_branch_not_permitted` and `resume_unusable` rather than with the six rows
naming a missing argument, and the distinction is not bookkeeping: those six name an argument that is
simply absent where the entry required one, while this names a *combination* the invocation
assembled — a parameter that can only end a wait, with nothing that started one. The section's
closing count of six therefore stays correct, and the sentence saying why is in the section rather
than only here.

## Recorded, not repaired

- **`await_max_reads` has no stated floor**, so `0` is a bound that authorizes a loop and permits no
  read. Under this decision an invocation supplying `await_max_reads = 0` and a floor passes the new
  precondition — a bound was supplied — and then has an allowance of no reads, reaching none of the
  five terminal conditions. The repair is a stated minimum, which is a change to the parameter's own
  definition rather than to the authorization question this decision answers. Named so a later reader
  finds it. (0132's idiom: recorded rather than filed, having been found while writing this.)
- **The general enumeration-drift check remains unbuilt.** Check 5 asserts the await enumeration
  specifically, because that is the set this decision touches. Every prose sentence in these
  documents that enumerates what other prose establishes has the same exposure and no checker — the
  Section 8.6 `provision` sentence above being the instance that proves it.

## Reconsideration triggers

- **A fifth await parameter.** This is decision 0112's own trigger, and it is the one that reopens
  the authorization split: a new parameter would have to be classified as authorizing, pacing or
  ending, and if it fits none of the three then the split is the wrong shape rather than an
  incomplete one.
- **A forge that publishes a budget only sometimes** — per-endpoint, or only after the first throttle.
  The unobservable-floor answer assumes "no snapshot" is a property of the backend, so a backend where
  it is a property of the moment turns a deployment-time opt-in into an intermittent `budget_floor`,
  and the declined reading becomes the better one.
- **A consumer that legitimately wants "one read, but stop if the bucket is low"** and finds the
  two-parameter spelling a burden rather than a nuisance. The refusal forbids the one-parameter
  spelling; if that turns out to be the common shape, the answer is to make the floor authorizing
  after all and to bound it some other way.
- **`checks_state` or the budget snapshot gaining a way to distinguish a forge with no budget
  interface from a forge reporting an empty budget** — 0125's trigger restated on the budget side. The
  unobservable floor fires today because the two are indistinguishable.

Depends on 0112 (the operation, its parameters, and the containment they implement) and 0125 (the
second `done` reason, whose promise the class repair must keep) — both cited as support for what the
documents now say, not as the reason for what this decision decides. Relates to 0132, whose
enumeration-drift class this is a fifth instance of, and to 0002, whose stable-anchor rule the
`Plan.md` follows.
