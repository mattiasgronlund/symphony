# Background — 0119 A drain was found by catching it live, which is the defect

## Context

Issue #62's observability item: a correlation id linking a retry to its origin run, plus per-bucket
budget and quota metrics aggregated across concurrent sessions, "so a drain or a hang is traceable
after the fact, not only caught live".

The last clause is the finding. The study records that the GraphQL drain "was only found by catching
a live poll process" — an operator noticed a process running and inferred the cause. Everything
needed to explain it afterwards was absent, so the investigation depended on someone being present
while it was still happening.

## What the log record can and cannot answer

Section 13.1 requires `issue_id`, `issue_identifier` and `session_id`, and Section 13.5 accumulates
token usage. That is enough to answer "what did this session do".

It is not enough to answer either question an after-the-fact investigation asks.

**Which run caused this one?** Section 8.4 converts a worker failure into a retry, and Section 7.2's
run-attempt lifecycle runs attempts in sequence. Each attempt gets a session, and each session gets
its own `session_id`. Nothing links attempt 3 to the attempt that failed and produced it. So a
sequence of retries is, in the record, a sequence of unrelated sessions against the same issue —
which is exactly the shape a retry storm has, and exactly the shape a coincidence has.

**Who spent the budget?** After decision 0115, each session records what its calls observed. But a
credential is shared across the repositories that did not partition it (decision 0116), so the
question "which repository drained this bucket" is answered by comparing readings across sessions
that each saw a different moment. No single record answers it, and the aggregate that would does not
exist.

## Correlation: the origin, not a chain

A correlation identifier links a run attempt to the attempt whose failure produced it.

The important design point is that it names the **origin** rather than the immediate predecessor. A
chain of predecessors is reconstructable by walking backwards, which is fine until one link is
missing from the record — and the record is where things go missing. Naming the origin makes every
attempt in a retry sequence carry the same value, so the sequence is a group rather than a linked
list, and a gap loses one member instead of severing the tail.

It is also the form that answers the question actually asked. "Show me everything that came from
this run" is a filter on one field; "show me the chain" is a traversal.

The first attempt of a run is its own origin, so the field is always present and never null — which
matters more than it looks. A nullable field invites a consumer to branch on absence, and there is no
condition here for the absence to mean.

## The budget aggregate

Per-bucket, per-credential-scope, across concurrent sessions.

The scope is what makes it useful and it is the part that would be easy to get wrong. Aggregating
per repository would answer "how much did this repository spend", which is the wrong question when
several repositories share a credential — the bucket they are exhausting is one bucket, and a
per-repository view shows several small numbers where the operator needs to see one large one. So
the aggregate is keyed by the credential scope decision 0116 introduced, which is the thing the forge
actually meters.

Two properties are stated as prohibitions because both are the obvious mistake:

- Buckets are **not** summed across scopes. Two credentials' remaining counts add to a number
  describing nothing, because they are counts against separate limits.
- A difference between two readings is **not** attributed as Symphony's spend where a credential has
  other holders. The forge reports what the credential has left, not what Symphony took, and a
  human running `gh` against the same token appears in the reading as Symphony's consumption.

The second is the one an implementation is most likely to get wrong while producing a chart that
looks right.

## Requirement level: recording is Core, aggregating is not

The same split decision 0115 drew, applied one layer out, and for the same reason.

The correlation identifier is Core: it is a value the orchestrator already has at the moment it
schedules a retry, and carrying it into the next attempt's log context costs a field. A deployment
running one issue at a time still retries, so it is not a multi-tenant feature.

The cross-session aggregate is an extension. It needs somewhere to aggregate *into* — a store, a
metrics sink, a retention policy — and a single-session deployment reading one session's records has
the whole picture already. That is a real cost imposed for a benefit that only exists above a certain
scale, which is the definition this slice has been using for an extension.

## Steelmanning: no new field, use the existing identifiers

The argument is that `issue_identifier` plus timestamps already lets an investigator group a retry
sequence — the attempts are the records for one issue, in order — so the correlation field adds a
column for something reconstructable.

It holds for the simple case and breaks where the investigation matters. An issue that failed, was
retried, succeeded, and was later reopened and retried again produces two sequences under one
`issue_identifier`, distinguishable only by reading timestamps and inferring where one ended.
Reconstruction that depends on inference is what fails at 2 a.m., and the study's finding is
precisely that reconstruction was not available.

## Reconsideration trigger

Reconsider if operators end up correlating across *repositories* — a failure in one repository's run
causing a retry in another's. Nothing in the current model produces that, and if it starts happening
the identifier is scoped too narrowly.

## Relationship to other decisions

It records what 0115 made available and keys the aggregate by the scope 0116 introduced. Its Core /
extension split follows the same cost test as both.
