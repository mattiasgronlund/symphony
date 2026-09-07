# Background — 0176 A constraint with no operand, and a verb with no stated arguments

## Context

Reported from `symphony-rs` as issue #168, against `5a4fdf7`, found while building that repository's
Stage D7 broker path and tracked there as decision 0011 R108.

Section 10.8 requires the broker to constrain a pull-request write against the configured base, and
does not say where the broker learns that base from. The evidence is inside one section, four
bullets apart. *Channel*, on what the binding supplies:

> The socket is bound to exactly one run, so the broker attributes every request to that run's
> **repository, issue, and work branch** without trusting any identifier supplied by the agent.

*Authorization scope*, on what must be constrained:

> Each brokered operation MUST be constrained to the current run: for example, push only to the
> run's work branch, write only to the assigned issue, and **open or update only the pull request
> for that issue against the configured base**.

The base is in the requirement and absent from the enumeration of what the binding carries.

## The mechanism

**The agent is not a resolution source, and that much is settled by the text.** Section 9.7:

> The **pull-request target** … resolves from three sources, most specific first: 1. the issue …
> 2. `vcs.base_branch` … 3. the base branch in `repo.policy.toml` …

and it closes the set — "Where no source supplies a target, the operations that need one are refused
before the run does anything". Three sources, complete, and the agent is in none of them.

**What that does not settle is whether the verb carries one, and this is the defect.** An
agent-named base can be a *confirmation the broker checks* rather than a source it resolves from.
Measured at `6b42942`: nothing in `SPEC.md` enumerates the `pr` verb's arguments. Section 10.8 names
the verbs — `push`, `back-merge`, `pr`, `request-merge` — and constrains them without saying what
they carry.

So two conforming implementations can differ on whether an agent names a base, and Section 10.8's
authorization sentence is a live check in one and a no-op in the other. That is not a hypothetical
divergence: it happened, between the two parties to this issue, from the same sentence.

**`symphony-rs` reads it as a check, and built the operand.** Their in-sandbox client takes the base
as a required positional argument — `symphony pr <base>`, refused without it and pinned by a test
named `pr_with_no_base_is_refused` — travelling the socket as `WireVerb::Pr { base, title, body }`,
becoming `EngineVerb::Pr { base, content }`, and compared by `authorize_base` against a
`RunBinding.base` they had to invent because the specification names no source for it.

**This specification's own session read it as a guarantee holding by construction**, and published
that reading on the issue before the implementation corrected it. Both readings are supported by the
text, which is the finding.

**The three constraints in one sentence are three different mechanisms.** That is why one sentence
produced two implementations:

- *push only to the run's work branch* — the work branch is derived from the binding, and a request
  naming another ref is refused by the scope guard (Sections 9.8, 15.4, 17.2). The agent can express
  the wrong thing and is refused.
- *write only to the assigned issue* — the issue is derived from the binding, and an identifier the
  agent supplies is not trusted (Section 10.8's own Channel bullet). The agent's value, if any, is
  ignored rather than checked.
- *against the configured base* — under this decision, the verb carries no base at all. The
  constraint is satisfied by **absence**: there is nothing for the agent to name, so nothing to
  check and nothing to ignore.

Listing three mechanisms as one kind of check is what invited an implementer to supply the operand
the third one lacks.

## Review finding: the call published on this issue was wrong, and would have removed a live guard

Recorded here rather than left in the thread, because it is the strongest evidence for what the
ambiguity costs.

The call posted on issue #168 from this repository stated that the agent names no base *as a fact
about the specification*, and concluded that `symphony-rs`'s guard was unnecessary and its reported
capability hole self-inflicted. The first half was an assertion past the evidence and the second
followed from it.

**The shape of the error.** Section 9.10's content-seam bullet — "The agent supplies pull-request
**text** across the sandbox boundary through a credential-free content seam" — is a sentence about
how text crosses the boundary without credentials. It was read as an exhaustive statement of what
crosses. It says nothing about other arguments. `VCSX-SPEC.md` Section 6.4's "An operation reads the
resolved base; it never accepts a base from untrusted content" was leaned on as the second support;
its neighbouring sentence is "Base resolution is configuration, not a hook", so the untrusted content
it forbids is the policy document and hook output. Section 8.1's `base_branch` is an invocation
argument the *consumer* supplies and the engine accepts — which is how sources 1 and 2 reach it at
all.

**What it would have cost.** Implemented as published, the comparison would have been removed while
the argument still stood: a fail-closed design becoming an unconstrained one, in a commit that reads
as a simplification. `symphony-rs` held its broker surface and reported the CLI signature instead,
which is why this is a near miss rather than an incident.

**The ordering constraint is theirs and is load-bearing.** An implementation that carries an
agent-supplied base removes it in this order: the client's positional argument, the wire field, the
engine-verb field, the binding, and the comparison **last**. The comparison is the only thing
standing between a mandatory agent-supplied operand and the operation for as long as that operand
exists. It is recorded in this decision rather than only in the issue because a later implementer
reading this chapter is the one who needs it.

**On the pattern.** This is the third correction from the same implementation in this round of work
— after a merge-base premise and a `fail_worker` arm that would have routed a class-7 failure to the
worker's disposition. Each was a reason that read as principled and did not survive being checked
against the artifact, and each was caught by the consumer checking the artifact rather than the
argument.

## Options considered

- **Option A — the `pr` verb carries no base.** Section 10.8 states what the verb carries, and says
  how each of its three constraints holds. The base is the resolved pull-request target (Section
  9.7), supplied by Symphony and never named by the agent.

  Trade-offs: it obliges an implementation carrying the argument to remove it, and the removal is
  order-sensitive in a way a careless reading of this decision could get backwards. It also makes
  Section 10.8's list less uniform to read, three mechanisms being harder to hold than one rule.

- **Option B — the agent may name a base as a confirmation**, and the broker holds the resolved base
  to check it against. Issue #168 then stands exactly as filed: the binding needs the base, and the
  source-3 value has to reach it.

  Trade-offs: this is what the only implementation built, on a reading the text supports, and it
  fails closed. Its case is that a confirmation makes the agent's assumption explicit and catches a
  confused agent before the operation. It loses on what the check costs and on what it catches. The
  cost is that every implementation must plumb the resolved base into the broker binding, and where
  the base comes from Section 9.7's third source that value is repository-owned — so the check is
  paid for by piercing the boundary Section 5.6 states, for a value the agent had no business
  supplying. What it catches is nothing a resolved base does not already prevent: an agent that
  cannot name a base cannot express the confusion the confirmation exists to detect.

- **Option C — clarify Section 10.8's sentence and leave the verb's arguments unspecified.**

  Trade-offs: the smallest edit, and no implementation must change. It loses because unspecified
  arguments are the status quo that produced two opposite implementations from one sentence.
  Clarifying which constraint is a check without saying whether there is an operand leaves the
  divergence exactly where it is.

## Decision and reasoning

**Option A.**

**The deciding consideration is where the cost falls.** Both arms are buildable. Option B's cost is
architectural and permanent — a data dependency from Symphony onto a repository-owned value, in
every conforming implementation, to check something the agent should not be sending. Option A's cost
is a one-time removal in implementations that carry the argument, of a surface that was never a
resolution source in any reading of Section 9.7.

**The `pr` verb's arguments are stated, not merely constrained.** That is the part that closes the
defect rather than the symptom. Section 10.8 gained its authorization sentence without ever saying
what the verbs carry, and a constraint over an unstated argument list is a constraint two readers
will discharge differently. Section 5.6's omission of `[base]` from `repo.policy.toml`'s sections is
fixed in the same edit — it is not the authority for the report, but it is plausibly why the hole
went unnoticed, and it is wrong on its own terms while Section 9.7 depends on that section as
resolution source 3.

**Section 9.10 is unchanged in substance** and gains one clause on its content-seam bullet, so a
reader learning what the agent supplies learns what it does not.

## Reconsideration trigger

Reopen if a deployment needs the agent to select among several permitted bases — a repository whose
`vcs.base_branch_allowed` admits more than one, where the choice is properly the agent's rather than
the operator's. Section 9.7 resolves the target before the run starts and gives the agent no say; if
that changes, the verb needs a base and Option B's binding question returns with it. The evidence
would be a deployment that has to encode the choice in the issue because the agent cannot make it.

A second trigger: an implementation found relying on the broker's base comparison to enforce
something other than the target — a policy-branch refusal duplicated there, say. Section 9.10
enforces that ahead of the operation and Section 9.7 refuses such a configuration before anything
runs, so the duplicate is redundant; but a build that had one would lose it when the argument goes,
and that is worth knowing before rather than after.

## The second trigger, checked and answered

`symphony-rs` ran it against the only implementation that has the guard, and did so **before**
removing anything rather than at removal time, which is when the answer is still inspectable. The
answer is negative: every use of `binding.base` and `authorize_base` there is the target comparison
itself, its violation variant, and two test fixtures. Nothing else reads the field.

The duplicate the trigger was written for does exist, and it is on the other verb. Their
policy-branch refusal is a **push** case resolving against the work branch, not against the base —
and their reason for putting it there is this specification's: the policy branch is never the run's
work branch (Section 9.7), so naming it is the ordinary any-other-ref case. It survives the
argument's removal untouched.

**Which is a third confirmation of this decision's conclusion, from a direction it did not argue
from.** Section 5 defines the guard itself:

> The **work-branch-only / assigned-issue-only** scope guard is a Broker Core built-in (Sections
> 3.4, 10.8), enforced regardless of any configuration

Two dimensions, branch and issue. No base. So the base was never one of the guard's dimensions in
the specification's own definition of it, and Section 10.8's authorization sentence had been reading
as though it were a third. That sentence was the whole of the ambiguity, and Section 5 disagreed
with the reading all along.

**The decision leaves no residue, which `symphony-rs` states more sharply than this chapter had.**
Half of issue #168 was that the broker could not *know* the base under Section 9.7's third source,
and their build denies a `pr` verb whose base it cannot establish. After this decision "there is
nothing to not know", so that arm becomes dead code and comes out with the rest: the fail-closed
guard was guarding a question the specification has dissolved rather than answered. That is the
outcome to want from a decision of this shape, and it is worth stating because a guard removed
without it would look like a loss of safety rather than the removal of a question.
