# Background — 0106 A read that answers `unchanged`, and the validator that asks for it

## Context

Issue #58 asks for conditional requests on the forge read capabilities, with a `not_modified`
outcome, "so a poll loop costs ~nothing against the API budget". It is the first of four engine
primitives the issue proposes, and it is the one the other three are ordered behind: without it a
consumer cannot build an efficient check-watch loop at all.

The engine already tells a consumer to poll. `merge:checks_pending` carries the default need
`await_checks` (Section 4.3) — a need the consumer meets by waiting and coming back. What Section
4.3 does not provide is an affordable way to come back.

## What coming back costs today

The only read that reports a pull request is `status`, and where a forge is configured it reports
the pull-request state through `pr_state` (Sections 4.1, 9.2). `pr_state(work_branch)` answers the
pull request's number, its state and the head it currently carries — a full read of the resource,
every time, whatever changed. There is no argument on the capability, and no field in the envelope,
that lets a caller say *answer only if it moved*.

So the loop the registry sends a consumer into is: dispatch `status`, read `outputs.pr`, sleep,
dispatch `status` again. For a twenty-minute check run polled every thirty seconds that is forty
full reads per unit of work. The cost is linear in concurrent units of work and it is charged
against a credential the consumer supplies (`forge_credential`, Section 8.1) and, today, against a
budget the same consumer cannot observe — which is decision 0107's half of this and why the two
are written together.

The engine is not the party that decides to poll. Section 2.2 keeps retry and back-off outside the
engine and this decision does not move them: no loop, no cadence and no budget policy is added
here. But the engine is the only party that *can* make a poll cheap, because it owns the forge
call. A primitive the consumer cannot implement for itself is exactly what belongs on this side of
the boundary.

## Verified: what the two GitHub APIs actually offer

The claim this decision turns on is that a conditional read is cheaper than an unconditional one.
Checked against the upstream documentation on 2026-08-17 rather than assumed:

- **GitHub REST** supports `If-None-Match`, and the accounting is explicit: "Making a conditional
  request does not count against your primary rate limit if a `304` response is returned and the
  request was made while correctly authorized with an `Authorization` header." The same page
  recommends it for exactly this use — "especially useful when you poll an endpoint, because each
  `304 Not Modified` response is fast and does not use your rate limit".
- **GitHub GraphQL** documents no ETag, no conditional request and no `304`. Its limit is a
  points-based budget, and its own documentation states that "The REST API also has a separate
  primary rate limit" — so the two are distinct budgets, which is where 0107's per-bucket
  requirement comes from.

The second finding is worth stating plainly because it cuts against the issue's own framing. The
downstream failure that prompted issue #58 was a GraphQL `--watch` poll loop, and **a conditional
read would not have prevented it on the API it happened on**, because that API offers no such
mechanism. What this decision buys is a cheap poll for a consumer reading pull-request state
through REST; what protects a consumer on an API with no conditional read is the visible budget
(0107) and the cadence a consumer paces against it. Recording that here rather than letting the
primitive inherit credit for a failure it does not retire.

Forgejo's coverage was not established. Its documentation does not state a conditional-request
contract for the pull-request endpoints, and this specification is in no position to assert one on
a backend's behalf. That the engine *cannot* know is the argument for the descriptor field below,
rather than an omission in this record.

## The answer shape: a fourth answer, not an absence

`pr_state` today has three answers, and Section 9 fixes the discipline they follow: a
value-answering capability MUST be able to answer that it could not determine a value, and that
answer MUST NOT be spelled as the value's absent or negative case. `pr_state`'s entry states the
consequence — an absent pull request lets `push` proceed and `create_or_update_pr` create, while an
undetermined one refuses both.

`unchanged` is a fourth answer and it is neither of the other two. It is a determinate fact about
the resource — the state is the one the caller already holds — where `none` is a determinate fact
that there is no pull request and `undetermined` is the backend declining to state either. Folding
it into any of the three reproduces exactly the failure Section 9 exists to prevent: read as
`none`, a `304` on a poll would let `create_or_update_pr` open a second pull request; read as
`undetermined`, the cheapest possible answer would refuse the operations the expensive one permits.

So the capability gains an argument and an answer, and the prohibition is stated in the same shape
Section 9 states the others: a backend MUST NOT answer `unchanged` where it did not ask, or where
it asked without a validator. An engine cannot check that claim, which is why it is stated as a
requirement on the backend rather than as a property the engine enforces — the same footing as
`push`'s no-rewrite guarantee, which Section 9.1 likewise states over an effect the engine cannot
observe.

## The validator round-trips through the consumer, because the engine holds nothing

The engine persists nothing between invocations: it takes a credential for the duration of an
invocation and holds none beyond it (Sections 1.3, 8.1), and each invocation is a bounded run that
exits. There is therefore no engine-side cache to hold a validator in, and no way to make this work
without the consumer carrying it: the validator leaves in the result envelope and comes back as an
invocation argument.

That is also why it is opaque. The engine holds the forge repository coordinate, the base ref, the
commit identity and both access parameters opaque (Sections 8.1, 9.2) — it takes them, hands them
to the plugin that uses them, and interprets none. A validator is the same kind of value, and
parsing one would put a forge's cache-header grammar back in the engine, which is the mixing
Sections 9.1 and 9.2 are separate to prevent. `If-None-Match` with an entity tag is one
realization; a forge whose conditional read is a modification timestamp is another. This
specification states the distinction the value MUST make and names no mechanism, which is the
disposition Section 9.1 already gives `worktree_revision()`.

## The engine supplies a validator only where it can use the answer

`pr_state` has three readers, and Section 9.1 already notes that two of them act on the answer
rather than reporting it: `push` refuses over a CLOSED/MERGED pull request, and `merge` takes the
`expected_head` it conditions the write on from the same read.

An `unchanged` answer carries no state and therefore no head. Supplying a validator on those two
reads would produce an answer neither operation can act on — and the failure mode is not a refusal
but a wrong write, since a `merge` that resolved `unchanged` to "the head I was told about last
time" would be conditioning a merge on a head *the consumer* remembered rather than one the engine
read. That is the guarantee `merge:head_moved` exists to provide (decision 0077), defeated by a
caching argument.

So the rule is stated over which read it is: the engine supplies a known validator on a read whose
answer it **reports** — `status` — and never on a read another operation **conditions a write on**.
A consumer polling for checks is served, and no write becomes conditional on consumer-held state.

## Where `unchanged` is reported

In `status`'s outputs, not as a reason token.

`status` already reports what a read did and did not establish in exactly this place: `base_absent`
for a base the checkout demonstrably holds no copy of, and `pr_state_unavailable` for a configured
forge that could not be asked (Section 4.1). "The pull request has not moved" is the same kind of
fact, established by the same read, and belongs beside them.

The alternative — a `status:not_modified` reason of its own, which is how issue #58 phrases it —
was rejected. It would give `status` two `done` reasons distinguished by whether the *caller*
supplied an argument, and a reason token is a trigger (Section 5.1): a repository could bind
`status:not_modified` to an action, firing policy on a condition the repository did not create and
cannot see, namely the freshness of the consumer's own cache. Reason tokens are the vocabulary a
repository writes policy against, and a consumer's caching state does not belong in it. The
argument for the reason token is real and is that a consumer branching on the envelope's `reason`
field learns the read was cheap without descending into `outputs`; it loses because the field it
would use is shared with the policy machine and this fact is not the policy machine's business.

## What an unsupporting backend does

The descriptor gains a field: whether the forge backend supports conditional reads. A backend that
does not declare it is supplied no validator and answers the full state, and `status` reports no
`pr_state_unchanged` output. Nothing else changes.

Specifically, this is **not** routed through `unsupported` (Section 4.3). That reason is for an
operation that requires a capability the backend does not declare — the operation cannot proceed.
Here the operation proceeds exactly as it does today; what is absent is a saving. A consumer's loop
is correct against either backend and cheap against one of them, which is the property that lets a
consumer write one loop rather than two.

## Reconsideration trigger

Reconsider if a forge appears whose conditional read is keyed to a *query* rather than to a
resource — a batched read answering for many pull requests at once. The validator here is
per-`work_branch`, because `pr_state` is, and a consumer watching thirty units of work would then
be making thirty cheap calls where one would do. That is a different capability with a different
shape, not a wider argument on this one, and its arrival is the evidence that this granularity was
the wrong unit.

Also reconsider if a `304` is observed to cost budget on some forge. The whole decision rests on
the accounting quoted above, which is GitHub's and is not a property of HTTP; a forge that returns
`304` and charges for it makes the validator a bandwidth saving rather than a budget one, and the
cadence argument in 0107 would then be carrying the whole load.

## Relationship to the other engine decisions

0107 makes the budget this saves visible; 0108 classifies the transient failures a poll loop must
tell apart from permanent ones; 0112 is the bounded loop that consumes all three. This decision is
usable without any of them — a consumer that polls `status` today gets a cheaper poll — which is
why it is recorded first and separately.
