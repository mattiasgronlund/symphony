# Background — 0065 Invocation preconditions are `usage_or_config`, with a registry of their own

## Context

Resolves part 4 of issue #9, raised while building the first real `VCSX-SPEC.md` Section 9.1 VCS
backend (`vcsx-plugin-git`, against `06a3bc19`).

Decision 0057 made `failed`, `blocked` and `unsupported` universal, so every operation can now report an
`error`-class outcome. That closed the case where a capability fails *during* an operation. It left the
case where one fails *before any operation runs*.

Section 6.3 has the engine derive the work branch from the pattern and the caller-supplied identity,
which means calling a Section 9.1 capability during invocation setup — `derive_work_branch`, or
`current_branch` where no pattern is configured. Three real states fail there:

- **The checkout has no current branch** (a detached HEAD). Section 6.3 pins a work branch every later
  capability names; there is nothing truthful to return.
- **The derived name is not a legal branch name** for the VCS. Section 6.3 does not let the engine
  substitute a branch of its own choosing, so it cannot clean the name up.
- **The supplied commit identity is malformed.** Section 10.1 keeps identity opaque to the engine
  because a signature's shape is the VCS's business, so only the backend can tell.

There is no operation to attach `<op>:failed` to: Section 8.1 makes `ship`, `land` and the individual
operations the entry points, and this is before the first of them. Section 4.3's registry is keyed by
operation and has nothing to say about a state in which none ran.

Answering it exposed two adjacent holes.

**The `usage_or_config` status has an empty half.** Section 8.2 defines it as the status "for a run in
which the policy did not run", and every reference to it points at Section 6.10 — the validation of
`repo.policy.toml`. Its name promises usage *and* configuration; only configuration ever had a registry.
A malformed caller identity is the plainest usage error the contract can have, and there was no token
for it.

**Section 6.3's `branch_pattern` has no stated default.** The issue's own framing assumes one — "or
`current_branch` where no pattern is configured" — and Section 6.3 lists `branch_pattern` (string) with
no `OPTIONAL` marker and no `Default:`. So the configuration state in which a detached HEAD is fatal is
a state the document does not admit exists, and the reason for it would have been unreachable as
written.

The practical stake is the one the issue names: a driver branching on exit code needs to know whether
"this checkout has a detached HEAD" arrives as `2` or as `20`.

## Options considered

- **Option A — `usage_or_config` (exit `2`), with a precondition registry in its own subsection of
  Section 8** (chosen). Preconditions are established between validating the policy and running it;
  failing one refuses the run and reports the existing status with a new reason token. Trade-offs: it
  adds a third reason registry to the document, and it puts a table in Section 8 that a reader might
  expect in Section 6.
- **Option B — `error` (exit `20`) with a null `op`** (rejected). It is what an implementer reaching for
  the nearest failure status would pick. It reports a failure with no operation that failed, which
  decision 0059 refused for exactly this shape: Section 8.2 defines `error` as the decisive operation
  result's proto class, and a null triple under it is indistinguishable from an engine that dropped the
  result. It also mis-signals recovery — `20` invites a retry against a state that no retry changes,
  while `2` says "the policy did not run; fix the invocation", which is the truth.
- **Option C — fold the reasons into Section 6.10** (rejected). It adds no section and reuses a
  registry with the right status. It is refused because Section 6.10 is validation of
  `repo.policy.toml`, judged from the policy file alone and before any argument or checkout is in hand;
  a detached HEAD is not a property of that file. Filing it there would reproduce this issue's own
  complaint — the answer settled somewhere other than where the implementer is reading — and would
  quietly break Section 6.10's contract that its conditions are statically determinable.
- **Option D — a fifth invocation status** (rejected, on decision 0059's reasoning). Section 8.5 freezes
  the status values and the exit-code mapping for a whole `MAJOR`; that is a steep price when an
  existing status already means "the policy did not run" and already carries a class-free reason.
- **Option E — define a `setup` pseudo-operation so the failures become `setup:failed`** (rejected). It
  would let the existing registry cover them and give the policy machine something to route. But
  Section 8.1's entry points are the front-ends and the operations, and a `setup` operation is neither —
  it would add a trigger surface (`setup:failed`, `before:setup`) that no repository could usefully bind
  because the failure happens before the policy is consulted, and Section 5.1's trigger vocabulary would
  gain an entry that never matches anything a policy can act on.
- **Option F — leave it `Implementation-defined`** (rejected). It is the one shape the issue explicitly
  rules out by asking: the exit code is the contract's coarsest branch point, and two engines returning
  `2` and `20` for the same checkout is precisely the divergence a driver cannot absorb.

## Decision and reasoning

Section 8 gains a subsection stating that the engine establishes the invoked entry point's preconditions
between validating the policy and running it, and that a precondition it cannot establish refuses the
run and returns `usage_or_config` (exit `2`) with `op` and `class` null and `reason` carrying one of
three new tokens: `no_current_branch`, `work_branch_invalid`, `identity_invalid`. Section 6.3's
`branch_pattern` becomes OPTIONAL with a stated default — unset, the work branch is the checkout's
current branch — which is what makes `no_current_branch` reachable.

The reasoning worth keeping is the dividing line, not the tokens. **A configuration error is a property
of `repo.policy.toml` alone, detectable before any argument or checkout is in hand; a precondition
failure needs the invocation's arguments and the checkout the engine was pointed at.** Both refuse to
run the policy and both report `usage_or_config`, which is why the status names usage and configuration
together — it was always a two-part status with one part populated. That line is what a reviewer applies
to the next such condition: ask what it is judged from, not which table has room.

Deriving the answer from the envelope rather than from intuition is what makes it stable. Section 8.2
already fixes the shape for a run in which the policy did not run — no operation result, `op` and
`class` null, `reason` carrying a class-free token — so a precondition failure needed no new envelope
rule, only a registry to draw its `reason` from. Decision 0059's invariant (where `op`/`reason`/`class`
are non-null, `class` is the class `status` reports) survives untouched, which is the check that
Option B fails and this option passes.

One boundary is stated explicitly because it is the way this could rot: an engine MUST NOT report a
precondition reason for a condition an operation could have reported. Once an operation is dispatched,
its failure is that operation's own reason (Section 4.3). Without that clause the new registry becomes a
convenient place to send any awkward failure, and the `error` status starts emptying out.

The `branch_pattern` default is the part of this decision that goes beyond the question asked, and it is
included because the answer is incoherent without it. The issue assumes the fallback; the document does
not state it; and a reason token for "the checkout has no current branch" describes a situation that,
read strictly, cannot arise. Stating the default costs one nested bullet and makes the registry entry
true.

Three tokens is the whole registry, deliberately. Each corresponds to a Section 9.1 capability the
engine calls before the policy runs, and the set grows only if that set of calls grows — which is a
better bound than "anything that goes wrong early". An engine that adds one documents it (Section 13.3),
on the same rule Sections 4.3 and 6.10 already impose.

What would make us reconsider: an entry point whose preconditions are genuinely optional — a `status`
that a caller wants to succeed on a detached HEAD, reporting the detachment rather than refusing. That
would argue for `status` reporting the state in its outputs instead of the engine refusing, and would
narrow the precondition to the entries that write.

Relates to 0057 (which made operation failure total and left this the residue), 0059 (whose null-triple
invariant this reuses and whose reasoning against Option B it borrows), 0056 (which created
`usage_or_config` and gave configuration errors their registry — this fills the other half), and 0044
(whose `Engine Invocation Failures` class covers only runs in which the policy never ran, which is
exactly this case).
