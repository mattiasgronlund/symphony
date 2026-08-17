# Background — 0120 A read that always completes still has to say which repair it needs

## Context

Issue #69. `VCSX-SPEC.md` Section 4.3 introduces `rate_limited` and `forge_unavailable` over a
general clause — "defined for every operation whose forge call the condition prevented" — and then
enumerates `push`, `create_pr`, `merge` and `await_checks`. `status` reads the forge through
`pr_state` (Section 9.1) and is in the clause but not the enumeration.

Section 9.2 states the permission over its whole capability list: "Any capability above MAY answer
`rate_limited` or `forge_unavailable`". `pr_state` is one of them. So a throttled `pr_state` on a
`status` invocation is permitted to answer a reason `status` has no registry entry for.

## What the defect does

`status` is the operation a consumer polls. It is read-only, needs no identity, needs no base
(Section 8.6), and is the cheapest way to learn whether a pull request exists — which makes it the
call a deployment makes most often against a forge, and therefore the one most likely to be the call
a throttle refuses.

Two dispositions are available today and each loses something the specification argues for
elsewhere.

`status:failed` is the universal `error` reason, which is the disposition Section 4.3 already
rejects for this condition: carrying a throttle under `failed` "ends a unit of work for a condition
that clears on its own, through the same path and with the same finality as a validation error that
never will". Nothing about that argument changes because the operation is read-only.

`status:ok` with the existing `pr_state_unavailable` output is the likelier reading, and it is the
one that motivated this decision. Section 4.3 divides the two transient reasons **by repair**:
`rate_limited`'s repair is informed, the exhausted bucket and its `resets_at` already in
`outputs.forge_budget`; `forge_unavailable`'s is uninformed, back off with no reset time to aim at.
Reporting both as `pr_state_unavailable` hands the caller one token for two repairs.

`outputs.forge_budget` does not recover the distinction, and this was checked against Section 8.2
rather than assumed. The key is "absent where the invocation reached no forge capability, and
equally where it reached one and the forge reported no budget" — one spelling for two events, stated
there deliberately. So its presence is not evidence of a throttle and its absence is not evidence
against one. A consumer cannot reconstruct which repair it has from what the envelope carries.

## The property that decides the shape of the repair

`status` completes. That is not incidental: Section 4.1 builds the whole operation around it. A base
the checkout does not hold is a `base_absent` **output** and the operation still completes, "because
an inspection that cannot see the base states that rather than failing". A field the read could not
establish is a `<field>_unavailable` output. A pull request that has not moved is
`pr_state_unchanged`. Three conditions, three outputs, one `ok`.

Making a throttled forge call the one condition that ends the operation would break that, and break
it at the least convenient point: a consumer calling `status` for the branch name and the dirty flag
would stop getting them because a forge it was only incidentally asking about was busy. The
version-control half of the read succeeded and has answers to report.

## Decision

A third output token, `pr_state_throttled`, beside `pr_state_unavailable`. `status` keeps `ok`, the
pull-request fields are null, and the token names the condition.

This is the arrangement Section 4.1 already reached once, when `pr_state_unchanged` was added beside
`pr_state_unavailable` rather than becoming a reason — three distinguishable pull-request conditions
"stated separately from the other two because the three carry different meanings". A fourth joins
them on the same terms. The precedent is cited as the shape rather than as the justification: the
justification is that `status` completes and a completing operation reports conditions in `outputs`.

`forge_unavailable` needs no counterpart output here. Its diagnosis already lives in
`outputs.forge_unavailable_condition`, and `pr_state_unavailable` continues to name it for `status`.
What was missing was the throttle, which is the one of the two whose repair is informed.

## Options considered

**Widen the `(any forge)` set to include `status`.** `status:rate_limited` and
`status:forge_unavailable` become defined, both `needs_caller`, and the enumeration matches its own
general clause. Steelmanned: it is the smallest edit, it makes one rule govern all five
forge-touching operations, and it means a consumer branching on `#needs_caller` catches a throttled
`status` without knowing the operation. It loses because it converts the operation that always
completes into one that sometimes does not, for a condition affecting one of six outputs — and a
`status` that escalates is a `status` whose version-control answers are discarded. The uniformity it
buys is uniformity across operations that do not otherwise resemble each other: the other four
*act*, and a throttle stops them from acting. `status` reports, and a throttle stops one field.

**Narrow Section 9.2's permission and say `status` reports `pr_state_unavailable`.** Also small, and
honest about what the enumeration meant. It loses because it settles the contradiction by choosing
the reading that discards information the engine already holds — the forge said "you are throttled",
the engine has the bucket, and the envelope spells it the same as an outage.

## Steelmanning the option not taken, in its own terms

The strongest case for widening is that a throttle is not really a property of one output. A forge
that throttles this call will throttle the next one, so a `status` reporting `ok` invites a consumer
to keep polling into a budget that is already refusing it — and `needs_caller` with the `retry_after`
need is exactly the signal that would stop it. That is a real argument and it identifies a real
hazard.

It does not carry, because the signal it wants is already in the envelope and is already required to
be: `outputs.forge_budget` carries the snapshot "reported whether or not any limit was reached", and
after this decision `pr_state_throttled` names the refusal explicitly. A consumer that polls into a
refusing budget with both of those in hand is not one a class change would have saved. And the
converse cost is unconditional: every `status` consumer would have to handle an escalation on a path
that today always returns data.

## Reconsideration trigger

Reconsider if a forge appears whose throttling is per-credential rather than per-call — so that a
refused `pr_state` is evidence the *next* version-control operation will also be refused. The output
token then reports a condition that is not about the field it is attached to, and the reason-level
treatment becomes the honest one. Nothing in the current forge model produces that: Section 9.2's
budget is observed per call and the version-control transport is outside it.

## Relationship to other decisions

It extends the `status` output vocabulary that 0106–0112 built out for conditional reads, and it
takes the by-repair division of the transient reasons as given rather than reopening it.
