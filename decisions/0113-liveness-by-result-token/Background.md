# Background — 0113 The specification already knows how to do this, in one place and not the other

## Context

Issue #61: an agent or subprocess success MUST be evidenced by a positive result token; a process
killed by seccomp, `SIGKILL` or the OOM killer that exits `0` spuriously MUST NOT be able to signal
success; and a backgrounded poller whose death is invisible is prohibited as a success signal. The
observed failure is recorded exactly: a backgrounded poller was killed by a sandbox seccomp filter,
exited `0`, "the parent read that as success and proceeded to merge incomplete work".

The study calls this the sharpest Symphony-specific lesson, and notes that Section 14.1 lists
`Subprocess exit` as a failure type while requiring no positive evidence of success.

## The fix is already written, for the engine

`VCSX-SPEC.md` Section 8.3 solves this problem completely, for the one subprocess Symphony invokes
that is specified in this repository:

> On every path that produces a result, stdout carries exactly one JSON object and nothing else.
> That is what lets a caller separate "no result" from "result" without parsing … An engine MUST NOT
> report an invocation status through a code outside the four, and MUST NOT exit `1` for an
> invocation that composed a result.

An engine's success is evidenced by a **composed envelope**, and the exit code is a redundant
encoding of a status the envelope already carries. `1` is reserved for "the invocation produced no
result at all", and any code outside the four status-bearing ones is read the same way — which makes
a caller's mapping total without enumerating the ways a process can die. A seccomp kill of a `vcsx`
invocation therefore produces no envelope, and a conforming consumer reads that as no result rather
than as any status at all.

Symphony's other subprocess — the coding agent, behind the Agent Runner (Section 10.7) — has no such
rule. The contract says `run_turn` returns "a result with its outcome" and that "on any error the
Agent Runner fails the worker attempt", and nothing anywhere says what makes an outcome a success.
Section 10.4 fixes the event vocabulary (`turn_completed`, `turn_failed`, `turn_ended_with_error`)
and requires an adapter to spell those conditions those ways, but it does not require that one of
them have **occurred** for a turn to be reported as complete.

So this is not a new mechanism. It is one the specification already relies on for the engine,
applied to the agent — and the record should say that plainly, because it makes the requirement
easy to reason about and hard to argue with: an implementer already builds this for `vcsx`.

## The failure path in Symphony's own terms

A turn is running. The agent process is killed — the sandbox's seccomp filter refuses a syscall, the
OOM killer takes it, a supervisor sends `SIGKILL`. The adapter's wrapper observes the process end
with status `0`, having emitted no terminal event.

Nothing in Section 10.7 makes that a failure. "On any error the Agent Runner fails the worker
attempt" — and no error was reported, because the thing that would have reported one is dead. The
adapter returns a result whose outcome is whatever it defaults to. The orchestrator advances the run
attempt (Section 7.2), and the work that never happened moves toward the merge.

The consequence is the one the report names, and it is the worst kind: not a run that fails, but a
run that **succeeds wrongly**. A failed run retries (Section 14.2). A run that reports success on an
agent that never finished proceeds to `ship` and `land` — and lands whatever was in the working tree
when the process died.

## What the rule is

Three clauses, and each is checkable without knowing which adapter is underneath.

**Success is evidenced, not inferred.** A turn is reported successful only where the adapter
observed the targeted protocol's terminal success signal, normalized to `turn_completed`
(Section 10.4). A turn whose process ended without any terminal signal is a failed turn, whatever
its exit status.

**Process exit status is not a turn outcome.** It is evidence a process ended and no evidence about
what it accomplished. This is the `VCSX-SPEC.md` Section 8.3 rule read the other way: there, an exit
code is permitted to *mirror* a status the envelope independently carries; here, there is nothing
for it to mirror, so it carries nothing.

**An unobserved death cannot report success.** An adapter MUST NOT report a turn successful on the
evidence that a process it backgrounded did not report a failure. Absence of a failure report from a
process whose liveness is not observed is not evidence of anything — which is the general form of
the specific failure the report describes.

The same rule extends to `hooks.after_create` and `hooks.before_run`, whose failure is fatal
(Section 9.4). A hook that is killed and exits `0` is currently a passed hook. Section 9.4's
contract is thinner than the agent's — a shell script has no event vocabulary — so what it gets is
the narrower half: a hook whose process was terminated by a signal is a failed hook. That is
checkable from the wait status and needs no protocol.

## Why this is Core and costs a single-tenant deployment nothing

The conformance stance chosen for this slice is to split by what a requirement costs a deployment
that runs one session at a time. This one costs nothing: an adapter already receives the terminal
events Section 10.4 names, because Section 10.7 already requires it to emit them. What changes is
that the outcome must be **derived from** them rather than from the process's exit. No new
configuration, no new dependency, no new operator obligation — and a single-tenant deployment gets
the same protection, since seccomp, the OOM killer and `SIGKILL` are not properties of concurrency.

A requirement that is free and prevents a merge of unfinished work has no business being optional.

## Steelmanning the alternative

The argument for leaving it is that Symphony deliberately defers success and failure to the agent
protocol (Section 10.7), and that a specification which starts adjudicating what counts as a
completed turn is reaching into a boundary it drew on purpose.

That is a real principle and this decision respects it: the rule does not say what a successful turn
*is* — that stays the protocol's — only that the adapter must have **observed** the protocol saying
so. The boundary is preserved and what changes is the burden of proof. An adapter still decides what
`turn_completed` means; it may no longer report one it did not see.

## Reconsideration trigger

Reconsider on an adapter for a protocol with **no** terminal signal — one whose only completion
evidence genuinely is the process ending. That protocol would make the rule unimplementable rather
than burdensome, and the answer would be a capability descriptor declaring it (Section 10.9) plus a
statement of what a deployment gives up by selecting such an adapter, rather than a weakening of the
rule for everyone.

## Relationship to other decisions

It generalizes the discipline `VCSX-SPEC.md` Section 8.3 already applies to the engine, and it is
the Symphony-side sibling of the answer-domain rule 0076 and 0110 apply to the engine's
capabilities: a value nobody established must not be reported as one that was.
