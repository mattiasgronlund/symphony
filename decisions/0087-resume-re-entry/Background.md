# Background — 0087 A resume re-enters the point that raised the need, and re-reads

## Context

Resolves issue #43. Section 5.5 gives the embedded driver a resolver and a resume:

> Embedded driver: the driver binds `escalate` to its own resolver — for example creating an
> agent-assigned task (Section 7.3) — and resumes the flow when the need is met.

Section 5.4 produces an escalation with no `escalate` action having run: the built-in default for the
`needs_caller` class is `escalate`. So a `before:commit` gate blocks with a `needs_caller` result,
Section 6.6 surfaces that as `commit:blocked`, no edge is bound to it, the default escalates, and a
driver resolves the need. **Where the flow carries on is written nowhere** — and not only for a gate.
The same silence covers every escalation the document produces, including the ones its own `ship`
routing raises: a `push:non_fast_forward` escalated to a driver that integrates and resumes has no
stated resume point either.

## What the defect does

The filing implementation resumed by dispatching the operation **without re-entering the position**,
so a resolved need ran a `commit` that a gate had refused and that no gate re-inspected. Nothing in
the specification told it that was wrong, which is why the report is a report rather than a changelog
entry. The failure is the one Section 6.6 exists to prevent one layer down: an operation that acted on
state no position inspected returns a `done`-class result for a run nothing gated, and the envelope
carries nothing that distinguishes it from a run that was gated.

## One candidate closed while the report was in flight

The report offers three destinations — end the run, dispatch the operation, or re-enter the position —
and it was written against `b9310967`. Decision 0078 has since put the position **inside** the
dispatch: Section 5.2 now says "Dispatching a gated operation runs its `before:<op>` position first
(Sections 4.1, 6.6), so an operation reached through an edge is gated exactly as one a front-end
sequence dispatches." So "dispatch the operation" and "re-enter the position" are one act, and the
behavior the report describes is no longer expressible through a dispatch at all: it would have to be a
resume landing *past* the position, which nothing in the document describes and which Section 6.6
forbids outright for `hook_unanswered` — "a gate that did not answer never yields a pass". Three
candidates are two.

This is worth recording rather than quietly using, because it is the second time 0078's relocation has
answered a question filed against the older shape, and a reader deciding whether to reopen this needs
to know the answer came from there and not from a fresh argument.

## Options

**A — A resume re-enters the point that raised the need (chosen).** Where an operation result raised
it, the resume re-dispatches that operation, which runs its `before:<op>` position first as any
dispatch does. Where an edge at a lifecycle position raised it — the case whose escalation carries a
null `op` (Section 8.4) — the resume re-enters that position. One rule for every escalation, not a
carve-out for gates, and the answer is the same for `blocked` and `hook_unanswered`: the gate is re-run
rather than bypassed, so a gate that blocked may now pass and a gate that never answered may now
answer, and neither yields a pass it did not give.

Two properties have to be stated with it, and neither is optional.

**The re-entry counts, and the count is over re-entry rather than over dispatch.** "A resume's
re-dispatch is a dispatch" covers the operation-result case and leaves the position case unbounded: a
`before:commit → escalate` edge re-enters a position *inside a dispatch whose count is already spent*,
so a resolver that always resolves loops there forever with nothing to stop it. Stating the rule over
any re-entry a resume causes puts both shapes on Section 5.6's bound, so both converge on
`flow_exhausted`. That is issue #4's property — a bounded traversal — held in the one place this
decision adds, and getting it wrong would have reintroduced the unbounded loop that decision won,
through a door #4 never had to consider because resumption had no stated semantics at all.

**A resume re-reads.** The value of re-entering the position is that the position's *reads* happen
again. Section 6.6 has a position take the identity of the state it inspected and hand it to the
operation — `expected_worktree` for `commit`, `expected_head` for `merge` — and an engine that cached
the expectation across a resume would hand a stale one to an operation, producing exactly the
condition decisions 0077 and 0079 exist to report rather than to produce. Without the sentence the
re-entry is satisfiable by re-running the gate's *edges* while keeping the earlier reads, which is a
reading of "re-enter the position" a conforming engine could take.

**B — An escalation ends the invocation (rejected).** `escalate` becomes what `park` is: a report both
front-ends surface, repaired out of band, picked up by the next invocation, which re-runs the position
rather than skipping it. This is what the filing implementation now does, and it is the strongest
rejected option: it is the simplest to specify, it removes a class of suspended state the engine would
otherwise carry across a resolver call, and it makes the two front-ends behave identically, which the
document repeatedly treats as a virtue.

It loses on what it costs Section 5.5. That section does not merely mention a resume — it makes the
resume the thing that distinguishes the embedded front-end, and Section 7.3 makes binding a resolver
part of the embedded-driver contract. Under B a driver that can genuinely meet the need — start the
daemon the gate checks for, provision the credential it looks up — cannot get the work done in the
invocation that asked, and must re-invoke. That is a rewrite of Section 5.5 rather than a completion of
it, and it collapses the distinction Section 8.4 draws between a need a front-end is expected to meet
and a hold it is not: under B, every need is released out of band, which is the definition Section 8.4
gives for a hold. The document would then be carrying `intervention` and `flow_exhausted` as a
separate category with nothing left to separate them from.

**C — The resume point is the driver's, bounded and documented (rejected).** Section 5.5 says a
front-end that resumes MUST re-enter at a point it documents and the engine MUST count the re-entry
against the flow bound. It loses in its own terms as well as against A: the whole purpose of Section
5.5 is to confine front-end divergence to a single point — which resolver is bound — and C widens that
point to include *where the executor resumes*, which is the executor's behavior rather than the
front-end's. Two drivers would then run the same `repo.policy.toml` through different operation flows,
which is the property Section 13.1 tests for and Section 5.5 claims.

## Verification

- The claim that Section 5.2 now runs the position inside the dispatch was checked against
  `VCSX-SPEC.md` at `e00ebb1`, in the `run_op` bullet, and against decision 0078's chapter in
  `DECISIONS.md`.
- The claim that Section 8.4 already admits an escalation with a null `op` at a lifecycle position was
  checked against Section 8.4 at `e00ebb1`: "The `op` is null where no operation produced the
  escalation — at a signal, at a lifecycle position where the gated operation has not run
  (Section 5.1), and at a bound the executor reached (Section 5.6)." That case is what makes the
  position half of the rule necessary rather than hypothetical.
- The claim that a position hands an identity to its operation was checked against Section 6.6's
  closing paragraphs at `e00ebb1`, which name `expected_head` (Section 9.2) and `expected_worktree`
  (Section 9.1) and the two reasons that report a state that moved.
- The word "resume" appears in `VCSX-CONTRACT.md` nowhere at `e00ebb1`, so this decision adds no
  contract surface and renames none.

## Reconsideration trigger

Reopen if a front-end appears that cannot hold a suspended flow across a resolver call — an engine
invoked as a stateless subprocess by a driver that resolves out of process, say. A resume point is only
meaningful for a front-end that can re-enter, and if the embedded contract stops implying that, B's
argument becomes the practical one rather than the minimal one.

Reopen also if a need is added whose remedy is *not* re-running the raising point — one met by
supplying something the flow reads at a later step. Every need in Section 8.4 today is met at or before
the point that raised it, which is why one rule covers them; a need that breaks that would need its own
resume point or its own reason for not having one.

## Relates to

0078 (which closed one of the report's three candidates before it was read), 0059 (the hold/request
split this preserves), 0060 and issue #4 (the bounded traversal the re-entry rule is stated to keep),
0077 and 0079 (the moved-state reports the re-read rule keeps honest), 0088 (the default's need, which
is what makes most resumable needs reachable at all).
