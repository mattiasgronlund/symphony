# Background — 0108 A throttle is not a failure, and retryable is a property of the need

## Context

Issue #58's third primitive: a 429, a 5xx, a network timeout and a TLS error are retryable-transient
and MUST be reason-classified distinctly from a permanent 4xx such as a 422 validation failure,
"each carrying a machine `retryable` signal, so the consumer retries the right things and never the
wrong ones".

## What a throttled forge does to a run today

The registry has no transient axis, so a forge that refused because a budget was exhausted takes the
universal `failed` (Section 4.3). `failed` is class `error`. And an `error`-class result that no
policy edge disposes of reaches the built-in default, which **fails the flow** (Section 5.4).

So the defect is not that a consumer cannot tell a 429 from a 422. It is that a condition which
would clear on its own in sixty seconds **ends the unit of work**, through the same path and with
the same disposition as a validation error that will never clear. A repository that wrote
`#error → fail` — the disposition the built-in default already applies — gets a run failed by
throttling, and the envelope it is failed with says only `failed`.

The mirror defect is on the other side of the same missing axis. A consumer that decides to retry
`error`-class results, having learned the hard way that some of them clear, now retries the 422 as
well — forever, since a malformed pull-request title does not become well formed on the ninth
attempt. Both consumers are behaving reasonably against a registry that gave them one token for two
conditions with opposite repairs.

Issue #58 reports the observed form of this as "two divergent throttle implementations disagreeing
on coverage" and a 429 that "risks landing as an unrelated reason like `checks_pending`". The
second is the more alarming: `checks_pending` is class `needs_caller` with the need `await_checks`,
so a throttled `merge` misreported that way sends a consumer into a check-watch poll loop against a
forge that just told it to stop calling.

## The class is the fix, and it is not `error`

`rate_limited` and `forge_unavailable` are class `needs_caller`.

That follows from Section 4.2's own definition — `needs_caller` is an operation that cannot proceed
without a decision or action from the caller, and is "not a failure of the engine" — and waiting is
an action the caller takes. It is also the only class that produces the right disposition: a
`needs_caller` result escalates rather than failing the flow (Section 5.4), so a throttled run
returns to the consumer with a need instead of ending.

It matters that this is argued from the disposition rather than from taxonomy. One could reasonably
call a 503 a failure in ordinary speech. What the class decides here is whether a unit of work
survives a forge hiccup, and that is the question the registry is being asked.

## Two reasons, not four, and not one

Issue #58 names four conditions: 429, 5xx, network timeout, TLS. This decision defines **two**
reasons, and the split is by repair rather than by cause.

- `rate_limited` — the forge refused because a budget was exhausted. Its repair is informed: the
  bucket that ran out and the time it refills are already in `outputs.forge_budget` (decision 0107),
  so a consumer knows both how long to wait and which kind of work to hold back.
- `forge_unavailable` — the forge did not answer, or answered that it is temporarily unable. Its
  repair is uninformed: back off and try again, with no reset time to aim at.

Collapsing the two loses a real distinction: a consumer that can read `resets_at` should wait
exactly that long, and one that cannot must guess. Splitting `forge_unavailable` further does not
gain one, because a 503, a timed-out connection and a rejected TLS handshake carry the same repair
in the same shape.

That is the reasoning decision 0104 recorded when `hook_unanswered` took one token for three
conditions — `bound_elapsed`, `not_started`, `answer_unreadable` — with the condition reported in
`outputs` because "the repair is the same shape in each case" and which one occurred "is diagnosis
rather than routing". The same split applies here and produces the same arrangement: routing on the
reason, diagnosis in `outputs`, with the condition spelled as a token so both halves are branchable.

The argument for four reasons is that a consumer may want to alarm differently on a TLS failure than
on a 503 — a rejected handshake is more likely to be a misconfiguration than a hiccup. That is real,
and it is served by the diagnostic token in `outputs` without spending four entries in a registry a
repository writes policy against, where the four would all need identical edges.

## `retryable` is a property of the need

The issue asks for "a machine `retryable` signal". The question is what it is a property *of*, and
the answer is the `need`, not the reason.

`retryable` means: **re-invoking the same entry point with the same arguments, after a delay and
with no further action by the caller, MAY succeed.** Read that against Section 8.4's vocabulary and
it is decided entirely by what the need asks for. `integrate_then_retry` is not retryable, because
the caller must run an `integrate` first — re-invoking unchanged reproduces the same
`push:non_fast_forward` forever. `reread_then_retry` *is*, because the re-read is what a
re-invocation does. `resolve_conflicts` and `supply_identity` are not; `await_checks` is; the two
holds are not, by construction.

So the field is defined once over the need vocabulary rather than as a column on the reason
registry. That placement is not cosmetic: it means a reason's retryability follows from its default
need (Section 4.3's column), which is already REQUIRED for every `needs_caller` reason, so the two
cannot disagree. A column would have let them.

The field exists at all — rather than leaving a consumer to derive it from the need — because
Section 8.5 permits new `need` tokens in a `MINOR` release. A consumer that hard-codes a
need-to-retryability mapping is correct until the release that adds one, and then silently wrong in
whichever direction its default guessed. Carrying the bit makes a new need absorbable, which is the
same job the `#class` fallback does for new reasons (Section 5.3). It joins the major-stable surface
for the same reason a reason's class is on it: a consumer branches on it, and a value that changed
within a `MAJOR` would change what a correct consumer does.

## What this does not cover

The version-control transport. A `push`, `integrate` or `pull` whose git remote times out still
reports the reason it reports today, and gains no transient token here.

That is a deliberate scope, not an oversight, and it is worth naming because the gap is real. Two
things separate the transports. A git remote publishes no budget and no reset time, so
`rate_limited`'s informed repair has nothing to be informed by. And `provision:unreachable` already
occupies the adjacent ground on the git side: it is `needs_caller` precisely because "the endpoint,
the credential, or the network between them" are the invocation's own arguments (Section 4.3), so a
condition a caller repairs by changing them is already routed away from `failed`. Adding a token one
word from `unavailable` to the same registry is the hazard `base_unresolved` / `base_unavailable`
already demonstrates costs care to keep straight.

The consequence stands recorded: a git fetch that times out during an `integrate` is still
`error`-class and still fails the flow. If that is observed in practice, it is the trigger below.

## Reconsideration trigger

Reconsider on a report of a git-transport timeout ending a unit of work — the gap named above,
arriving. The repair would be a transient token on the version-control side, and the work is
choosing a name that does not collide with `unreachable` rather than deciding whether the condition
deserves one.

Reconsider also if `forge_unavailable`'s three diagnostic conditions turn out to be routed on rather
than logged — a repository binding `create_pr:forge_unavailable` and then branching on the condition
inside a hook would mean the repair is *not* the same shape in each case, and that the split into
two reasons was one too few.

## Relationship to the other engine decisions

0107 supplies the `resets_at` that makes `rate_limited`'s repair informed rather than a guess; 0109
makes the timeout that produces `forge_unavailable` a bound a consumer sets rather than one the
engine hard-codes; 0112's bounded loop is the consumer that branches on `retryable`.
