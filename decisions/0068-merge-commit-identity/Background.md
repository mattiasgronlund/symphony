# Background — 0068 Every commit the engine writes carries the caller-supplied commit identity

## Context

Resolves issue #14, raised while building the first real `VCSX-SPEC.md` Section 9.1 VCS backend
(`vcsx-plugin-git`, against `06a3bc19`).

Section 10.1 splits a commit into content and identity and assigns the second — "The commit
author/committer **identity** is supplied by the consumer, distinct from content." Section 9.1
carries that through for one capability, `commit(message, identity)`, and not for the two others
that can write a commit. `integrate(remote, base)` writes a merge commit whenever the base does not
fast-forward, and decision 0061 made `pull(remote, work_branch)` merge the remote counterpart rather
than replay over it, so it writes one too. Neither takes an identity. Section 10.1 addresses this
exact case for the *message* — "A mechanical merge commit produced by `integrate` uses the backend's
default message" — and says nothing about who it is attributed to. A backend has to decide, and the
specification gives it nothing to decide from.

What makes this a conformance question rather than a tidiness one is what a backend does when left
to decide. Git auto-detects an identity from the username and the hostname, with two consequences:
the merge commit names whoever ran the engine, so the same repository under the same policy produces
different history on different machines; and where the hostname carries no domain — a container, a
CI runner — git refuses the address it auto-detected and aborts the merge. `integrate` then returns
`integrate:ok` on a developer's laptop and `integrate:failed` on a runner, from the same repository,
with nothing in the policy or the configuration differing. The filing implementation shipped that
and CI caught it on the first run against a runner, the suite having passed on two developer
machines that both had a domain in the hostname. An engine can implement Section 9.1 exactly as
written and have a required operation fail on a whole class of hosts.

The consumer-facing statement of the same gap is one layer up and reads the same way. `SPEC.md`
Section 9.8 has Symphony attempt a back-merge at the start of every run and configures the identity
as `vcs.author`, while its commit-message bullet says only that "A mechanical merge commit uses the
engine's default message" — so the commit the back-merge writes is the one commit in a Symphony run
whose author is not `vcs.author`, on a service that runs host-side in exactly the container the
failure mode above describes. `VCSX-CONTRACT.md` Section 9 carries the sentence in a shorter form —
"A mechanical merge commit uses the engine default" — which, with the word *message* dropped, is the
one place a reader could infer that the engine is entitled to choose an identity of its own.

Answering it exposed an adjacent hole. Section 8.1's common arguments list "the identity used to
derive the work branch (Section 6.3)" and no commit identity, while Section 8.6 has the engine
accept "the caller-supplied commit identity" and refuse the invocation when the backend judges it
malformed. Those are two distinct values — a work item, whose identity fills a
`symphony/<identifier>` pattern, and an author — named by one token in one list and distinguished
only in the other. The answer below has to say which of them a merge commit carries, and cannot
while the invocation contract lists one.

## Options considered

- **Option A — the commit identity reaches `integrate` and `pull` through their Section 9.1
  signatures** (chosen). The engine already accepts the identity for the invocation and already
  supplies it to `commit`; the two capabilities that can also write a commit take it in the same
  position, and Section 10.1 states that a mechanical merge commit carries it. Trade-offs: it
  changes two capability signatures a month after decision 0062 changed three — an anchor change
  against a surface an implementation is already building against — and it obliges a caller that
  runs `integrate` alone to supply an identity for an update that may turn out to fast-forward and
  write no commit.
- **Option B — the consumer's identity supplied once when the backend is opened** (the issue's
  meanwhile; rejected). Its merit is real and is the reason the issue proposes it: Section 9.1's
  signatures stay exactly as published, which matters to an implementation already built against
  them, and the identity genuinely is constant for an invocation. It is rejected on four counts. It
  routes a value the engine resolves to the backend through a channel that is not a capability
  signature, which is the correction decision 0058 made for `diff(base)` and decision 0062 made for
  `remote`, made twice already for smaller stakes. The channel does not exist: Section 9.1 specifies
  capabilities, not a backend lifecycle, and there is no `open` — so the meanwhile has to invent a
  plugin-instantiation step and make it the second place the engine hands a backend a resolved
  value, after which Section 9.1 no longer states what the engine supplies. It puts two identities
  in play with a precedence rule — the argument authoritative for `commit`, the stored one for the
  commits the specification hands no identity to — which a backend must implement correctly and
  which no result exposes when it does not. And the engine already judges the identity: Section 8.6
  refuses the invocation with `identity_invalid` when the backend calls it malformed, which means
  the engine holds the value and presents it, so backend-scoping would have the engine validate a
  value it does not supply.
- **Option C — an engine-defined identity, published under Section 13.3** (the issue's second offer;
  rejected). It closes the host-dependence, which is the half that aborts merges, and costs one
  sentence and one Statement row. It does not close the divergence: two engines write different
  authors into a repository's permanent history and both conform, which is the same shape decision
  0062 rejected for the remote. It also inverts Section 10.1 for one commit out of two — content is
  the caller's and identity is the consumer's for a `commit`, and identity is the engine's for the
  merge commit written seconds later on the same branch — while every consumer already holds an
  identity, since `commit` requires one.
- **Option D — leave it to the environment, as an `Implementation-defined` behavior** (rejected).
  This is the status quo with a label on it. `Implementation-defined` names a behavior an engine
  chooses and documents so a consumer can plan around it; the attribution here is not a property of
  the engine at all but of the host it happens to run on, which is the one thing the term cannot
  describe. An engine would document "the identity the environment supplies" and a consumer would
  learn nothing.
- **Option E — a repository-owned identity in `repo.policy.toml`, beside `remote`** (rejected).
  Section 6.2's line is that backend *selection* is repository-owned while the *credential* is the
  consumer's; Section 10.1 already puts identity on the consumer's side, and `SPEC.md` keeps
  `vcs.author` in operator policy config rather than in the repository's Way-of-Working file. Moving
  it would let a repository name the author of commits a consumer's automation writes under the
  consumer's credential — attribution sourced from one side and authorization from the other — which
  is a trust inversion rather than a convenience.
- **Option F — reuse the identity `derive_work_branch(pattern, identity)` already takes**
  (rejected). It needs no new argument and no signature change beyond the two. But a branch derived
  from `symphony/<identifier>` is filled from a work item, and `SPEC.md` Section 9.8 confirms the
  reading — "The work branch is derived deterministically from issue identity". Reusing that value
  would attribute commits to a work item. What the option is good for is showing that Section 8.1's
  single entry conflates two arguments, which is fixed here rather than left for the next reader.

## Decision and reasoning

`integrate` and `pull` take the commit identity: `integrate(remote, base, identity)` and
`pull(remote, work_branch, identity)`, in the position `commit(message, identity)` already uses.
Section 10.1 states that a mechanical merge commit — one `integrate` or `pull` writes when the
update it performs is a merge — uses the backend's default message and carries that same identity,
and that a backend MUST NOT attribute a commit to an identity it derives from its execution
environment. Section 8.1's common arguments name the two identities separately, and Section 8.6's
precondition covers every entry that can write a commit rather than only the one that always does.

The reasoning worth keeping is the invariant, in the shape decision 0062 left it: **the capabilities
that take the commit identity are exactly those that can write a commit.** Section 9.1 now carries
two sentences of that form, one per engine-resolved value — the capabilities that take a `remote`
are exactly the operations Section 3.2 places host-side, and the capabilities that take an
`identity` are exactly the ones that write commits — and each is what a reviewer checks when the
next capability is added. The second was the one the document could not have stated before this
decision, because it was false of `integrate` and `pull`.

The tension with decision 0062 is the part that had to be argued rather than assumed, because the
issue's meanwhile resolves it the other way. 0062, inheriting from 0058, states that every value an
operation needs, and that the engine resolves, MUST reach the backend through a capability
signature. A backend-scoped identity is that rule's plainest counter-example, and its justification
— the identity is constant across an invocation, so passing it per call is repetition — is true and
is not the point. **Constancy is an argument about where a value is supplied from, not about how it
reaches the backend.** The remote is equally constant across an invocation and is passed anyway, for
the reason 0062 gives: an answer settled anywhere other than the signature is an answer settled
somewhere other than where the implementer is reading. Bending the rule for the first constant value
would leave the rule stating something about frequency instead of about provenance, and the next
value would be argued on how often it changes.

The credential is the one value that does travel to a backend outside a signature, and it is worth
saying why identity is not like it. Section 11 keeps credentials out of the engine deliberately —
"The engine holds no long-lived credentials. A consumer supplies credentials to the plugins for an
invocation or runs the engine where they are already held" — so the engine neither holds nor
inspects one. It holds the identity: Section 8.1 lists it among the invocation's arguments and
Section 8.6 has the engine present it to the backend for judging and refuse the run on
`identity_invalid`. A value the engine already holds and already validates is one the signature
should carry; the credential is excluded from signatures precisely because the engine must not hold
it.

Two consequences are stated in the text rather than left to follow. A backend MUST NOT derive an
identity from its execution environment, which is what makes attribution a property of the
invocation rather than of the machine — the same policy over the same checkout writes the same
author, and an `integrate` no longer succeeds on a laptop and fails on a runner. And a merge the
forge performs is attributed by the code host to the account the consumer's credential names, the
commit a squash strategy writes included; the engine supplies no identity for it. Without that
second sentence the invariant reads as a claim about every merge commit in the repository's history,
and `land` would look like an omission rather than a boundary.

Requiring the identity for an `integrate` that may fast-forward is a deliberate small cost. The
engine cannot know in advance whether the update will merge, and refusing the invocation up front —
exit `2`, "the policy did not run; fix the invocation" — is better than discovering it after the
merge has been attempted, which is exactly the failure the issue reports. The `identity_invalid`
condition is widened to cover an identity that is absent where the entry requires one rather than
gaining a fourth token: decision 0065 bounded that registry deliberately, the condition is one
failure of one argument, and splitting it across two tokens would make a consumer branch twice on
the same fix.

What would make us reconsider: a backend that cannot be constructed without an identity — one
signing through a key held in an agent socket, say — which would argue for a plugin lifecycle with
an explicit open step. At that point the identity would travel with the lifecycle and the argument
would be about the lifecycle rather than about this parameter, which is the shape to reach for
rather than a second channel bolted beside the signatures. A deployment needing the author and the
committer to differ — a bot committing on a person's behalf — needs nothing here: the engine holds
identity opaque (Section 8.6), so the distinction lives inside the value.

Relates to 0062 (whose signatures this extends and whose invariant it applies a second time), 0058
(the source of that invariant), 0065 (whose precondition this widens, and whose registry bound it
respects), 0061 (which made `pull` merge, and so made `pull` a commit-writing capability), and 0032
(which authored the message-formulation split of content from identity that Section 10.1 states).
