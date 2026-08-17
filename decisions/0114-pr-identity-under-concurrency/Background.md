# Background — 0114 One pull request per issue is a rule about which one

## Context

Issue #62's second item: a mutating forge operation MUST target an explicit pull request and head,
resolved and re-verified immediately before the write, refusing on mismatch, "so concurrent sessions
can't overwrite each other's PR via an ambient branch". The observed failure is specific: a
concurrent session overwrote another's pull-request title and body, and a later merge squashed the
hijacked title into history.

## Where the ambient branch comes from

Section 9.10 says Symphony "maintains one pull request per issue", created on first push and updated
on later runs, with "the head is the work branch". Section 8.3's concurrency control is `Core
Conformance` and keeps two workers off the same issue.

What neither says is **how the update finds the pull request it updates**. The engine's
`create_or_update_pr` is required to maintain one per work branch, and `pr_state(work_branch)` looks
it up keyed on the work branch as head (`VCSX-SPEC.md` Section 9.2). So the identity of the thing
being written is derived, at write time, from a branch name.

That is the ambient input. A branch name is not a pull request; it is a key that resolves to one,
and what it resolves to depends on the forge's state at the moment of the lookup rather than on
anything the session established. Section 8.3 prevents two Symphony workers from running the same
issue — it says nothing about a second session that is not Symphony's worker at all: another
Symphony deployment against the same repository, an interactive `vcsx ship` a developer ran, an
agent skill invoking the engine directly, or the same operator's second checkout. The reported
hijack came from concurrent sessions sharing a checkout, which is exactly the population Section 8.3
does not cover.

The failure is then mechanical. Session A resolves the work branch to pull request 42 and composes a
title. Session B, whose work branch resolves the same way, writes its own title to 42. A's next
update — or its merge — reads 42 again and acts on it. Nothing detects anything, because every step
did what it was told: the lookup succeeded, the pull request existed, the write applied.

And the damage outlives the run. Section 9.10's squash message is derived from the pull request
"title verbatim", so a hijacked title is what enters history at the merge. The report records
exactly that sequence.

## The engine already solved the harder half

`merge` does not have this problem. Decision 0077 requires `request_merge(pr, strategy,
expected_head)` to refuse where the head is no longer the one read at `before:merge`, reporting
`merge:head_moved`, and `VCSX-SPEC.md` Section 9.2 states that a backend whose forge cannot condition
the merge does not declare the capability at all, "because a merge that cannot be conditioned merges
content no lifecycle position inspected".

So the discipline exists, at the sharpest point, and this decision is the observation that it was
applied to **what** is merged and not to **which** pull request is written. `expected_head` pins the
content; nothing pins the identity. A hijacked title passes every head check, because the head never
moved.

## What the rule is

A mutating forge operation names the pull request it acts on and re-verifies it immediately before
the write:

- Symphony resolves the pull request for an issue to an explicit identity — the forge's own pull
  request number — and carries that identity, not the work branch, into every subsequent mutating
  operation for the run.
- Immediately before a mutating write, the identity is re-read and checked against what the run
  established: the pull request still exists, still has this run's work branch as its head, and still
  targets the resolved base. A mismatch refuses the write.
- A refusal is not a retry. It means another writer is acting on the same pull request, and the
  repair is an operator's — retrying re-reads a state a second writer is still changing, and the
  second attempt is as likely to overwrite as the first.

"Immediately before" is doing real work and is stated as a bound rather than a mood: the re-read and
the write are the closest pair the forge's interface allows, with no intervening operation of
Symphony's own. That does not make the pair atomic, and the record should not pretend otherwise —
this narrows a window that the forge alone can close. What it converts is a silent overwrite into a
detected refusal, in every case where the competing write lands outside the pair. A forge offering a
conditional update closes the window entirely, and a backend that has one SHOULD use it, which is the
same shape `expected_head` already has.

## Why Core, and what it costs a single-tenant deployment

Nothing, which is the test this slice applies. A deployment running one session at a time resolves
the pull request once, re-reads it before writing, finds it unchanged, and writes. The cost is one
read per mutating operation — and after decision 0106 that read is conditional where the forge
supports one, so on the common path it is a `304`.

The protection is also not only against concurrency. A pull request closed by a human between two
Symphony runs, or retargeted to a different base, is the same mismatch, and today the second run
writes to it regardless. So the rule is not a multi-tenant feature with a single-tenant cost; it is
a correctness rule whose most visible failure happens to need concurrency to reproduce.

## The concurrency-stress tier

Issue #62's cross-cutting item asks for a conformance tier running N concurrent sessions against
shared resources. This decision adds the Symphony half: a `Concurrency Stress` validation profile,
RECOMMENDED rather than REQUIRED, asserting that concurrent sessions against one repository and one
pull request produce no hijack — every write either applies to the identity its session established
or is refused.

It is RECOMMENDED for the reason Section 17.8's real-integration profile already is: it needs a live
forge and real concurrency, so it is environment-dependent in a way the deterministic corpus is not.
Making it REQUIRED would make conformance depend on a test harness this specification cannot
describe — the same boundary decision 0111 drew for the engine's fault-injection vectors, reached
here for the same reason.

## Steelmanning the alternative

The argument against is that Section 8.3's concurrency control is already `Core Conformance` and
covers the case this decision worries about, so what is being added is a guard against writers
Symphony does not manage — which is arguably outside its remit. If another tool writes to a
repository Symphony is orchestrating, the argument goes, the operator has a coordination problem
that no clause here fixes.

It loses on scope. Section 8.3 bounds Symphony's own workers, and every population in the reported
failure is outside it: a second deployment, a developer's interactive invocation, a skill-driven
agent — the last of which is a consumer this repository is actively specifying for (issue #60). A
guarantee about "one pull request per issue" that holds only when Symphony is the sole writer is a
guarantee about a configuration rather than about the system, and it is not the one Section 9.10's
sentence appears to make.

## Reconsideration trigger

Reconsider if refusals appear in normal operation without a competing writer — that would mean the
re-verification is reading something that legitimately changes between the read and the write (a
forge that rewrites titles, a bot that retargets bases), and the check is pinned to the wrong fields.

## Relationship to other decisions

It extends 0077's conditional-write discipline from the merged content to the written identity, and
consumes 0106's conditional read to make the extra read cheap.
