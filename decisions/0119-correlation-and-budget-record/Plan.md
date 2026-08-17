# Plan — 0119 A drain was found by catching it live, which is the defect

## Scope

`SPEC.md`: Section 13.1 "Logging Conventions" (the correlation field), Section 13.5 "Session Metrics
and Token Accounting" (the aggregate), Section 18.2 (the extension), Sections 17.6, 18.1.

`conformance/vocabulary.json`: the correlation field joins `log_context_fields`.

## Steps

1. **`Logging Conventions` — the correlation field.** Ensure a REQUIRED context field links a run
   attempt to the attempt whose failure produced it, naming the **origin** rather than the immediate
   predecessor, and state why: every attempt in a retry sequence then carries one value, so the
   sequence is a group rather than a linked list and a missing record loses one member instead of
   severing the tail. Done-condition: "everything that came from this run" is a filter on one field.

2. **`Logging Conventions` — never null.** Ensure the first attempt of a run is its own origin, so
   the field is always present. Done-condition: no consumer branches on absence, there being no
   condition for absence to mean.

3. **`Session Metrics` — the aggregate.** Ensure an OPTIONAL cross-session aggregate is defined:
   per bucket, keyed by **credential scope** (Sections 13.1, 15.3) rather than by repository, because
   a forge meters a credential and repositories sharing one are exhausting one bucket — a
   per-repository view shows several small numbers where an operator needs one large one.
   Done-condition: the key is argued from what the forge meters.

4. **`Session Metrics` — the two prohibitions.** Ensure buckets are never summed across scopes (two
   credentials' remaining counts add to a number describing nothing) and a difference between
   readings is never attributed as Symphony's spend where a credential has other holders (the forge
   reports what the credential has left, not what Symphony took). Done-condition: both are stated as
   prohibitions rather than left to be inferred.

5. **Requirement levels.** Ensure the correlation field is Core and the aggregate is an OPTIONAL
   extension of `Daemon Conformance`, with the split argued: the identifier is a value the
   orchestrator already holds when it schedules a retry and a single-issue deployment still retries,
   while the aggregate needs a store, a sink and a retention policy for a benefit that exists only
   above a certain scale. Done-condition: Section 18.2 lists the aggregate and Section 18.1 the
   field.

6. **Sections 17.6, 18.1, 18.2.** Ensure the test matrix checks that a retry carries its origin's
   correlation value and a first attempt carries its own; that the aggregate, where shipped, is keyed
   by credential scope and sums no buckets across scopes. Done-condition: steps 1, 2 and 4 each have
   a check.

7. **`conformance/vocabulary.json`.** Ensure `log_context_fields` carries the correlation field with
   what it is required for. Done-condition: the registry and Section 13.1 agree.

## Cross-cutting sync

Section 6.4 gains nothing: the extension's configuration is its sink and retention, which are
`Implementation-defined`. Sections 17 and 18 are covered by step 6; Section 19 records the aggregate
where shipped, as the other extensions' enablement already is.

## Anchor changes

New anchor: one log context field. No anchor is renamed or removed.

## Status

Applied to `SPEC.md` (Sections 13.1, 13.5, 17.6, 18.1, 18.2) and `conformance/vocabulary.json`.
