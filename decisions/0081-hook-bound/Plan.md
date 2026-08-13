# Plan — 0081 A hook bound is a bound on a unit, and an unanswered hook is the operation's reason

## Scope

`VCSX-SPEC.md`: Sections 4.3 "Reason-Token Registry", 5.6 "Flow Bound and Termination", 6.6
`[hooks]`, 6.10 "Validation", 8.2 "Result Envelope", 13.1 "Test Matrix", 13.2 "Implementation
Checklist", 13.3 "Conformance Statement". `conformance/vcsx/vocabulary.json` and
`conformance/vcsx/vectors/`. `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.

No `VCSX-CONTRACT.md` change: the concrete reason registry and the field-level `[hooks]` schema are
both deferred to this document (`VCSX-CONTRACT.md` Section 11).

## Steps

1. **`[hooks]` (Section 6.6)** — ensure the section states that an engine MUST bound the time it
   waits for a hook to answer; that the bound's value is `Implementation-defined` and MUST be
   documented (Section 13.3); and that it MUST admit a configured value of at least 600 seconds,
   with the same gloss Section 5.6 gives its own floor (the value is arbitrary, that it is fixed is
   not). *Done when* `[hooks]` carries a REQUIRED bound with a stated floor and a Section 13.3
   reference.

2. **`[hooks]` (Section 6.6)** — ensure the section states that `run` is REQUIRED for a declared
   hook, so a `[hooks.<name>]` table carrying no `run` is judgeable from the document. *Done when*
   the `run` key is marked REQUIRED and Section 6.10 names the condition (step 6).

3. **`[hooks]` (Section 6.6)** — ensure the bound's disposition is stated over the division the
   section already draws: a `before:*` hook that does not answer within the bound is killed and the
   gated operation reports `hook_unanswered`; an `after`/result-triggered hook that does not answer
   within it is killed, the flow continues unchanged, and the fact is reported in `outputs`
   (Section 8.2). Ensure the same paragraph states that the bound is the consumer's, that `[hooks]`
   carries no key for it, and that a `timeout_ms` a repository writes is ignored under Section 6.1,
   with Section 3.2's sourcing argument as the reason.
   *Done when* both hook kinds have a stated outcome and the ownership sentence cites Sections 3.2
   and 6.1.

4. **`[hooks]` (Section 6.6)** — ensure the section states the bound's limit: killing the unit does
   not end what the unit started, so a hook that leaves a grandchild holding the pipes is read from
   until the bound elapses; the invocation is bounded and the machine is not.
   *Done when* the limit appears as a `Note:` in the section's existing aside style.

5. **`hook_unanswered` (Section 4.3)** — ensure the registry carries a row `(any gated)` /
   `hook_unanswered` / `error` glossed as the hook giving the engine no usable answer — the bound
   elapsed, the unit could not be started, or its answer could not be read (Section 6.6). Ensure the
   sentence introducing the universal reasons counts **four** rather than three, and that a
   paragraph states the boundary against its neighbours: `blocked` is a gate that answered and
   refused, `failed` a gate that answered with an `error` result, and `hook_unanswered` a gate that
   answered nothing — which of the three conditions occurred is `outputs`, not a token. *Done when*
   the row exists, the count reads four, and the boundary paragraph names all three reasons.

6. **Validation (Section 6.10)** — ensure the table names a `[hooks.<name>]` declaring no `run` unit
   and maps it to `malformed_policy`, grouped with the well-formedness conditions rather than the
   consistency ones. Ensure the prose states that whether the named unit exists is a property of the
   worktree rather than of the document, so it is `hook_unanswered` at first use and not a
   configuration error.
   *Done when* the row exists with `malformed_policy` and the boundary sentence cites Section 6.6.

7. **Flow Bound and Termination (Section 5.6)** — ensure the closing paragraph's "further bounds"
   are scoped to bounds on a **running flow**, which stop the executor and end the invocation, and
   that it states a hook bound (Section 6.6) is not one of them: it bounds one unit at one position
   inside a dispatch, the flow is not stopped, and the gated operation's result re-enters the
   machine. *Done when* the paragraph distinguishes the two kinds of bound and cross-references
   Section 6.6.

8. **`outputs` (Section 8.2)** — ensure `outputs` is stated to carry the result-triggered hooks the
   engine killed at the bound, each naming its hook and the position or result that ran it, on the
   same principle that keeps `unperformed_intents` (Section 5.4: an intent the engine emitted and no
   consumer performed is reported).
   *Done when* the `outputs` bullet names the key beside `unperformed_intents` and states when it is
   absent.

## Cross-cutting sync

- **Test matrix (Section 13.1)** — add, under "Gate blocking": a `before:<op>` hook that does not
  answer within the engine's bound yields `<op>:hook_unanswered` rather than `<op>:blocked`,
  `<op>:failed` or a `flow_exhausted` hold; a hook that could not be started and one whose answer
  could not be read yield the same reason; a gate that answered with an `error` result still yields
  `<op>:failed`, so the two are distinguishable; a result-triggered hook that does not answer within
  the bound leaves the flow unchanged and is reported in `outputs`; a `[hooks.<name>]` with no `run`
  is refused at validation with `malformed_policy`.
- **Implementation checklist (Section 13.2)** — extend the `repo.policy.toml` loader line with the
  refusal of a hook declaring no `run`, and the operation-set line with the bounded-hook
  requirement.
- **Conformance Statement (Section 13.3)** — add the hook bound's value to the enumeration of
  `Implementation-defined` resolutions, beside the form of a hook's engine-invoked `run` unit.
- **`conformance/vcsx/vocabulary.json`** — add `hook_unanswered` to `reasons`.
- **`conformance/vcsx/vectors/policy-validation.json`** — add a vector for a `[hooks.<name>]` with
  no `run` refused as `malformed_policy`, and one for a well-formed hook table accepted.
- **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`** — add a row for the hook bound.

## Anchor changes

None. `hook_unanswered` is a new code token; no existing anchor is renamed or removed.

## Status

Applied to `VCSX-SPEC.md`.
