# Background — 0060 A conforming executor bounds the flow, and an exhausted bound is `needs_caller`

## Context

Issue #4. `VCSX-SPEC.md` Section 5.2 says a `run_op` result "is itself a trigger, so a policy is a
graph, not a flat list", and Section 12.2 writes `ship` with an unbounded `loop:` that retries `push`
after each `integrate`. Nothing in the document bounds the traversal: there is no iteration cap, no
cycle detector, and no deadline — "timeout" does not appear in `VCSX-SPEC.md`. The natural terminations
are that `integrate` returns `merge_conflicts` and escalates, or that `push` returns `ok`.

The issue calls this the mildest of the three it filed, on the grounds that "two engines with different
bounds agree on every policy that terminates, so the divergence is confined to policies that are already
broken". Working it shows that framing is too narrow in one direction and too wide in another.

### The unbounded case is not confined to a broken policy

`push:non_fast_forward → integrate → retry push` is not a repository's mistake; it is the built-in
default routing Section 12.2 itself prescribes, and Section 4.3 records `push:non_fast_forward` as
"Remote moved; integrate then retry". It terminates because the remote eventually stops moving. A base
branch that receives a push between every one of ours produces `push:non_fast_forward` and
`integrate:ok` alternately and indefinitely — a live-lock from a correct policy over a correct backend
against a busy repository. So the hang is reachable without anyone writing a bad graph, which is what
makes "the engine hangs" worth a MUST rather than a documented `Implementation-defined` shrug.

### The only sound bound is a count, not a cycle detector

The issue names "no cycle detector" among the missing safeguards. A cycle detector is the wrong
mechanism, in either form:

- **Statically**, over the policy graph: the `push`/`integrate` cycle *is* the built-in routing, so
  refusing a graph with a cycle would refuse Section 12.2.
- **At runtime**, on a repeated `(trigger, edge)` pair: the second time the base moves is an ordinary
  event, so an executor that stopped there would abort a correct flow that was about to converge.

What separates a converging flow from a looping one is how many operations it takes, not whether it
revisits an edge. Only a count can tell them apart.

### The count has a unit that makes the bound a proof

`run_op` is the only action whose result re-enters the machine:

- `run` does not re-enter on its own. A `before:*` hook's block surfaces as the *gated operation's*
  reason — `<op>:blocked` or `<op>:failed` (Section 6.6) — so it reaches the machine through a
  `run_op`; an `after`/result-triggered hook "is best-effort and does not block".
- `create_task`, `set_state` and `notify` are consumer-effected intents, emitted once (Section 5.2).
- `escalate`, `park` and `fail` are terminal.

So every non-terminating flow is an unbounded sequence of `run_op` dispatches, and a bound on that count
is not a heuristic that usually catches loops — it is a termination proof for every policy the schema
can express. This also survives the case a lifecycle position introduces: an edge on `before:push` may
itself `run_op("integrate")`, which re-gates `before:push`, and every hop of that loop is still counted.

### Why the *outcome* cannot be left to the engine

The issue offers, as a sufficient minimum, "a sentence in Section 12.2 or Section 5.4 saying so — and
adding it to Section 13.3's list of `Implementation-defined` behaviours an engine must document".
Publishing the bound is necessary but not sufficient. Section 8.3 turns the invocation status into an
exit code and Section 8.5 freezes the status values and the mapping for a whole `MAJOR`, so an
`Implementation-defined` outcome means two conforming engines return different exit codes for the same
run. That is the defect decision 0056 fixed for a configuration error and decision 0059 fixed for a
parked flow, and the document's own use of `Implementation-defined` is consistent about the line: it
covers *mechanisms* — checkout-mode detection, discovery precedence, argument encodings, the escalation
`detail` field — and never the class of outcome a caller branches on. The bound's **value** is a
mechanism; the bound's **disposition** is contract.

## Options considered

- **Option A — MUST bound one invocation by a count of `run_op` dispatches, with a stated floor;
  exhaustion ends the invocation at `needs_caller` carrying a new `flow_exhausted` need (chosen).**
  Trade-offs: adds one `need` token, which Section 8.5 already permits a `MINOR` to introduce, and one
  `Implementation-defined` value with a Section 13.3 row. Costs a second member in the carve-out
  decision 0059 wrote for `intervention` ("the one need no front-end resolves" becomes two needs that
  name a hold), which is an amendment to a just-accepted decision's phrasing rather than to its
  substance.
- **Option B — leave bounding to the engine: `MAY` bound, `Implementation-defined` outcome, documented
  in Section 13.3.** The issue's stated minimum. Trade-offs: the cheapest change and it makes the
  divergence visible in each engine's Conformance Statement. Rejected on both halves. Optional bounding
  leaves "the engine hangs" a conforming behavior, and an autonomous consumer cannot absorb it — a hung
  invocation holds a workspace slot with no result to classify, which is worse than any answer. And an
  `Implementation-defined` outcome documents the disagreement rather than removing it: a caller
  branching on exit code still cannot write one branch that works against two engines.
- **Option C — exhaustion carries the existing `intervention` need.** Trade-offs: adds no token, and it
  is defensible under Section 8.4's naming rule, since a `need` names what is required and both cases
  require the same thing — out-of-band human attention. Rejected because it would make the two
  indistinguishable in the envelope: decision 0059 nulls `op`/`reason`/`class` for a hold, so `need` is
  the only structured field left, and a consumer could not tell a policy that asked to hold from an
  engine that stopped one. That is the objection 0059 itself raised against letting `human_review` cover
  a park. `message` and the `Implementation-defined` `detail` are not a substitute for a token a
  consumer branches on.
- **Option D — exhaustion is `error`.** Trade-offs: it reads as a fault, and a consumer already has
  error handling. Rejected because Section 4.2 defines `error` as "the operation failed" and no
  operation failed — the executor declined to dispatch the next one. It would also drag in the question
  decision 0059 explicitly left open (an `error` status with no `error`-class result to report, the
  `fail` envelope), and it invites a consumer that retries errors with backoff to retry a flow whose
  defining property is that repeating it unchanged changes nothing.
- **Option E — exhaustion is `usage_or_config`.** Trade-offs: it puts the blame where a genuine policy
  loop belongs, on the configuration. Rejected because Section 8.2 reserves that status for "a run in
  which the policy did not run", and this policy ran — as far as it could. Non-termination is not
  statically detectable either, so it cannot be moved into Section 6.10 validation, where a
  configuration reason would have to be raised.
- **Option F — bound by wall clock rather than by count.** Trade-offs: a deadline bounds slow operations
  as well as many of them, which a count does not. Rejected as the *required* bound: a deadline is not
  deterministic, so no conformance vector can assert it, and the wall-clock budget of a run already
  belongs to the consumer — Symphony's `compute.max_wall_clock_ms` bounds the executor from outside.
  Kept as a permitted additional bound, with its disposition fixed to the same result, so that which
  bound fired is not visible in the envelope's shape.
- **Option G — a repository-configurable bound, for example `[engine] max_operations`.** Trade-offs:
  attractive because the bound doubles as the only cap on `push`/`integrate` retries, and how many
  retries are reasonable is genuinely repository-dependent — a busy monorepo and a quiet repository
  differ. Rejected for now: it adds a configuration key, a validation rule and a cheat-sheet row in
  order to answer a question about retry policy, which is not the question issue #4 asks, and a floor
  plus a generous engine default settles termination without it. Recorded rather than discarded: if
  repositories start wanting retry control, this is the surface it lands on.

## Decision and reasoning

Choose **Option A**. A conforming executor MUST bound one invocation's flow by a count of `run_op`
dispatches; the bound's value is `Implementation-defined`, MUST be documented, and MUST admit at least
64 dispatches. A flow that reaches any bound the engine imposes ends the invocation at `needs_caller`
(exit `10`) carrying an escalation whose `need` is `flow_exhausted`, with `op`, `reason` and `class`
null.

Four properties carry the decision.

**Counting `run_op` makes the bound total rather than best-effort.** Because `run_op` is the only action
whose result re-enters the machine, bounding its count bounds every loop the schema can express — there
is no second recursion to miss. That is worth more than the loop it was written for, in the same way
decision 0059's class-agreement invariant was worth more than the parked case: it is a property a
reviewer can re-check the next time an action is added, by asking only whether the new action's result
re-enters.

**A count rather than a cycle detector, because a repeat is ordinary.** The specification says so
explicitly, so that no engine reaches for the safeguard the issue named: a repeated `(trigger, edge)`
pair is the built-in routing meeting a base branch that moved twice, and an executor that stopped there
would refuse a correct policy against a busy remote.

**The floor is what makes the issue's own claim true.** "Two engines with different bounds agree on
every policy that terminates" holds only where both bounds exceed what the policy needs; with no floor
an engine whose bound is three conforms and agrees with nobody. The floor's exact value is arbitrary —
64 is roughly an order of magnitude above the worst case the built-in sequences produce, since a `ship`
costs one `commit`, one `create_pr` and two operations per `push` retry — but that it is *fixed* is not
arbitrary: it is the smallest thing that turns a hoped-for portability property into a stated one.

**`flow_exhausted` is a hold the engine imposed; `intervention` is one the policy asked for.** Both are
holds in the sense decision 0059 established — no automated party can move the flow, so no front-end
binds a resolver to either or resumes on either — and Section 8.4 now states that as a property of the
pair rather than of a single token. They stay distinct because they call for different responses: a park
is the policy working as written, while an exhausted flow says either that the graph does not converge
or that the remote is moving faster than the engine can follow, and both want a human looking at
something. Under Option C's collapse that distinction would exist only in prose the caller cannot
branch on.

The envelope needs no new rule. Decision 0059 stated that `class` agrees with `status` where the three
are non-null, and that all three are null where the run has no decisive operation result; an exhausted
flow adds a third instance of that case — 0059's own record anticipated it, noting that "a budget
exhausted after `push:ok` also ends a flow with nothing decisive to report".

**Deliberately left open and recorded.** `fail`'s envelope, still open from 0059 and untouched here: it
needs a prior answer to what `fail(reason)`'s argument is. And the repository-configurable bound
(Option G), which is a retry-policy question wearing a termination question's clothes.

We would reconsider if a consumer appeared that can legitimately resume an exhausted flow — one that
raises the bound and re-invokes carrying the prior flow's position, say. At that point `flow_exhausted`
would stop being unresolvable, and it would want a resume token rather than a bare hold, which is a
different shape from the one chosen here.

The decision is **Accepted** and applied to `VCSX-SPEC.md` (Sections 5.6, 8.2, 8.4, 12.2, 13.1, 13.2,
13.3), the vocabulary registry, and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`. It resolves issue #4.
Relates to 0059 (whose invariant this builds on, and whose `intervention` carve-out it widens), 0056
(which added `usage_or_config`, the status Option E would have reused), 0057 (the same
rule-outruns-its-enumeration shape), and 0044 (whose `Engine Invocation Failures` class covers only runs
in which the policy did not run, so an exhausted flow is not one).
