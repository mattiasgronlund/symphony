# Background — 0116 One credential is a scope decision nobody made

## Context

Issue #62's first item: Symphony MUST allow — and for multi-tenant deployments SHOULD default to —
scoping forge credentials per repository or per agent, "so one repo's load can't starve another's
budget and a leaked token has a bounded blast radius". The study records the single shared token as
"the structural root of the quota contention".

## What the configuration says today, read carefully

Section 5.3's operator policy config carries `vcs.git_credential` and `vcs.forge_credential`, both
resolved through the secret-provider interface (Section 15.3). Section 8.7 routes many repositories
through one orchestrator.

Nothing says those credentials are *one*. Nothing says they are per repository either. The
configuration is a flat key, and how it composes with the multi-repository routing of Section 8.7 is
simply not stated — which in practice means one, because a flat key has one value.

So this is not a case of the specification choosing a shared credential and being wrong. It is a
case of the specification never asking the question, and a single value being the answer that falls
out of the schema. That distinction matters for what the fix is: the requirement is not to *change*
a policy but to make the scope an explicit, configurable decision, with a default the specification
is willing to defend.

## The two failures a shared credential produces

They are different and only one of them is about security.

**Budget contention.** The forge meters a credential, not a repository. Two repositories under one
orchestrator spending against one credential are one spender as far as the code host is concerned,
so a repository with a runaway loop exhausts the budget of every repository beside it. Decision
0107's snapshot makes this observable and 0115's guard can act on it — but neither can *separate*
the budgets, because they are not separate. A guard that pauses on a low bucket pauses everyone,
including the repository that was spending nothing. Partitioning is the only thing that turns a
shared failure into a local one.

**Blast radius.** A credential that reaches every repository the orchestrator serves is a credential
whose compromise reaches every repository the orchestrator serves. Symphony's secret-isolation
invariant (Sections 9.6, 15.3) is strong about where a credential goes — never into the agent
sandbox, only into the executor's broker context — and says nothing about how much a credential is
worth. Those are independent properties, and the invariant holding perfectly does not bound what a
single leaked value unlocks.

## What the rule is

The credential pair becomes scopable, and the scope is named rather than implied:

- An operator MAY configure the outward credentials per repository, and an implementation MUST
  support that configuration. Where none is configured for a repository, the orchestrator-level
  credential applies — which is the behavior every existing deployment already has, so nothing that
  works today stops working.
- The scope in effect for a repository is recorded, so an operator can tell from the record which
  credential a call was made under (Section 13.1) without inferring it from configuration.
- Per-**agent** or per-**session** credential scoping is explicitly not required. The forge meters a
  credential and the unit of contention observed is the repository; a per-session credential would
  mean minting one per run, which is a credential-lifecycle mechanism — issuance, rotation,
  revocation — that this specification does not have and should not grow as a side effect of a
  budget-isolation requirement.

That last exclusion is the part of the filed item this decision declines, and it is worth being
explicit rather than quietly narrowing: issue #62 asks for "per repo / per agent" and this delivers
per repo.

## Why an extension rather than Core

The stance for this slice is to split by what a requirement costs a deployment running one session
at a time, and this one costs something real. An operator provisioning one token now provisions
several, and each needs its own creation, storage, rotation and revocation. For a single-tenant
deployment — one repository, one token — the partition is a partition of one, and the requirement
buys nothing while imposing schema surface.

That is the same test that put 0113's liveness rule and 0114's identity check in Core: those cost
nothing and protect everyone. This one costs and protects only deployments with something to
partition.

But the *support* is Core-adjacent in a specific way worth stating: an implementation MUST support
the configuration even though an operator need not use it. Otherwise the requirement is unusable —
a multi-tenant operator would have a `SHOULD` they cannot satisfy on a conforming implementation
that chose not to build it. So the split is: **supporting** per-repository scope is REQUIRED of an
implementation, **using** it is the operator's, and the specification SHOULD-recommends it wherever
one orchestrator serves repositories with different owners.

## Steelmanning Core

The argument for making it Core is that "a leaked token has a bounded blast radius" is a security
property, and security properties are poor candidates for optionality — an operator who most needs
the partition is the least likely to read the extension list.

It is a good argument and what defeats it is that Core would have to mean *mandating separate
credentials*, since a Core requirement an operator can decline is what this decision already
proposes. Mandating them would make a single-repository deployment provision a credential per
repository it does not have, and would put this specification in the business of credential
lifecycle. The recommendation is therefore pitched at the deployments that can act on it, and the
implementation obligation ensures they can.

## Reconsideration trigger

Reconsider if the per-repository unit turns out to be the wrong grain because contention is observed
*within* one repository — many concurrent issues in one repository exhausting its own credential.
Partitioning per repository does nothing for that, and the answer would be pacing (0115's guard)
rather than a finer partition, so the arrival of that report is evidence about which mechanism is
load-bearing rather than a reason to subdivide further.

## Relationship to other decisions

It bounds what 0107 makes visible and 0115 can act on, and it is orthogonal to the secret-isolation
invariant (Sections 9.6, 15.3): that invariant governs where a credential goes, and this governs how
much one is worth.
