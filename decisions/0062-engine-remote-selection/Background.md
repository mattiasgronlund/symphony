# Background — 0062 The remote is named in `[engine]` and supplied to the capabilities that touch it

## Context

Resolves part 1 of issue #9, raised while building the first real `VCSX-SPEC.md` Section 9.1 VCS
backend (`vcsx-plugin-git`, against `06a3bc19`).

`VCSX-SPEC.md` Section 9.1 gives the VCS backend `push(work_branch)` and `pull(work_branch)`, neither
carrying a remote. Section 6.2's `[engine]` table configures `version_floor`, `vcs` and `forge`, and no
remote name. Section 3.3 mentions a remote twice — a jj secondary workspace "derives the remote slug and
branch from jj rather than from a colocated git remote" — but only as a mode-detection consequence, not
as a value anything supplies. So a backend that talks to a remote at all has to pick one, and the
document nowhere says which.

The consequence is not a broken engine; it is a conformance hole with side effects. Two engines running
the same `repo.policy.toml` over the same checkout can push a repository's work branch to two different
places while both conform, and the divergence is invisible in the result envelope — both report
`push:ok`. Section 14 treats a name spelled differently in two places as a contract change; a *target*
chosen differently in two places is worse and had no rule at all.

The filing implementation's meanwhile-answer is `origin`, "because it is what `git clone` writes". It
also records why the obvious alternative is worse: reading the work branch's own upstream binding
(`branch.<name>.remote`) reads exactly the configuration that does not exist yet, because the work
branch is engine-derived per Section 6.3 and need not be present in the checkout at the first push.

Two adjacent defects surfaced while answering:

- **Section 3.2's host-side list omits `pull`.** It reads "(integrate, push, create_pr, merge,
  host-side hooks)", while Section 4.1 defines `pull` as "update the local work branch from its remote
  counterpart" — plainly an operation that touches the remote. The omission matters here because the
  answer below leans on that list being the authority on which operations reach the network.
- **A configured remote the checkout does not carry had no stated disposition.** Section 6.10's
  validation reads the policy file alone, so it cannot catch it, and nothing said what happens instead.

## Options considered

- **Option A — an OPTIONAL `remote` in `[engine]`, resolved by the engine and passed to the
  capabilities that take one** (chosen). `remote` sits beside `vcs` and `forge`, which is the same kind
  of thing: repository-owned backend-facing selection. The engine resolves it once per invocation and
  supplies it to `integrate`, `push` and `pull`, whose Section 9.1 signatures grow the parameter.
  Unset, the backend's default remote applies, `Implementation-defined` and published in the
  Conformance Statement. Trade-offs: it adds a config key and changes three capability signatures — an
  anchor change — and it does not by itself force two engines to agree where the key is unset. What it
  does is give the repository the means to decide, which is the half that was missing.
- **Option B — a sentence saying the remote is the backend's to determine, published under Section
  13.3** (the issue's second offer; rejected). It costs one sentence and no schema. It also leaves the
  remote *unconfigurable*: a repository whose work branches go to a fork rather than to upstream, or
  that carries more than one remote, cannot say so, and the interoperability hole the issue names stays
  open by design rather than by omission. Section 6.2's own rationale — "which code host a repository
  targets is repository-owned, while the credential for it is the consumer's" — applies with equal
  force to which remote at that host.
- **Option C — name `origin` normatively as the default** (rejected). It is a git convention, and this
  specification names no VCS's conventions normatively (Section 2.1's "the same policy runs across
  code hosts and checkout modes without policy changes"). Section 3.3 already admits a jj secondary
  workspace with no colocated git remote, where `origin` names nothing. A literal default would be
  wrong for a backend whose own default is spelled otherwise, and right only by accident for the rest.
- **Option D — derive the remote from the work branch's upstream binding** (rejected, on the filing
  implementation's own reasoning). The work branch is engine-derived (Section 6.3) and MAY be absent
  from the checkout at the first push, so the configuration that would be read is exactly the one that
  does not exist. It is also a git-specific mechanism appearing in neutral text.
- **Option E — a `remote` argument on the invocation rather than in the policy** (rejected). Section
  6.2 draws the line at repository-owned versus consumer-supplied and puts backend *selection* on the
  repository's side; the remote is selection, not credential. Making it an argument would also let two
  invocations of the same policy against the same checkout target different remotes, which is the
  divergence the issue reports, relocated rather than closed.

## Decision and reasoning

`[engine]` gains `remote` (string, OPTIONAL). The engine resolves it once per invocation and supplies
it to the VCS capabilities that act against a remote, whose signatures become `integrate(remote, base)`,
`push(remote, work_branch)` and `pull(remote, work_branch)`. Unset, the backend's default remote for the
checkout mode applies; that default is `Implementation-defined`, MUST be documented, and is published in
the Conformance Statement (Section 13.3).

The reasoning worth keeping is not the key but the invariant it makes checkable: **the capabilities that
take a `remote` are exactly the version-control operations Section 3.2 places host-side, and every other
capability in Section 9.1 is local to the checkout** — it reads or writes the worktree and the history
already held, acquires nothing over the network, and needs no credential. That single sentence answers
three questions at once that the document previously answered in three places or not at all: which
operations need a remote, which need a credential, and which a consumer may run in-sandbox (Section
3.2). It is also what a reviewer checks the next time an operation is added — if the new capability
takes a remote, Section 3.2's host-side list must name it, and if it does not, it must be runnable
without one.

That invariant is what forced Section 3.2's list to be corrected: with `pull` missing, the invariant
would have been false the moment it was written. Correcting the list is the smaller half of the change
and the one most likely to have gone on being overlooked, because nothing depended on that list being
complete until now.

Passing the remote rather than letting the backend read it from the policy follows the document's
existing habit with the other configuration-resolved value: the base is resolved by the engine
(Section 6.4) and reaches the backend as a parameter — `integrate(base)`, `diff(base)`,
`ahead_behind(base)`. A `remote` key with no way to reach the backend would repeat this issue's own
complaint, settling the answer somewhere other than where the implementer is reading. It is the same
correction decision 0058 made for `diff(base)`, and the same invariant restated: every value an
operation needs, and that the engine resolves, MUST reach the backend through a capability signature.

A remote name the checkout does not carry is stated as an operation failure rather than a configuration
error. Section 6.10 is judged from `repo.policy.toml` alone and a remote's existence is a property of
the checkout, so the loader cannot see it; it surfaces at first use as the operation's `failed` reason,
which decision 0057 made universal and therefore available at every operation without a new token.

What would make us reconsider: a deployment that legitimately needs to push to one remote and read the
base from another — a fork-and-upstream arrangement — which would turn the single key into a pair and
is the shape to reach for rather than a second, argument-level override. Nothing in the current
operation set needs it: `integrate` and `push` both act on the one remote the work branch is published
to.

Relates to 0058 (the same "a required value MUST reach the backend through the required interface"
correction, one operation over), 0064 (which says what `integrate` does with the remote it now
receives), and 0061 (which constrains how `pull` updates the branch, not where it reads from).

## Re-evaluation, 2026-08-14 — superseded in placement by 0092

This decision put the remote in `repo.policy.toml` and supported the placement by citing Section
6.2's rationale: "§6.2's own rationale that 'which code host a repository targets is
repository-owned' applies with equal force to which remote at that host." Decision 0092 retires that
rationale, and on a mechanism this decision did not have available.

The mechanism is a bootstrap cycle. Reading `repo.policy.toml` requires having the repository;
obtaining the repository requires the forge kind, its access parameters and a credential; those were
configured in `repo.policy.toml`. Option E here — "a per-invocation `remote` argument", rejected
because "it relocates the divergence rather than closing it, and Section 6.2 puts backend *selection*
on the repository's side" — was rejected against a premise that no longer holds. The half of the
rejection that stands is the one about divergence, and 0092 answers it differently from option E: the
remote is not a free per-invocation argument but the single value the repository was provisioned
from, so two conforming engines given the same configuration still push to the same place. The
conformance hole this decision was filed to close stays closed.

What survives unchanged is the part worth keeping: **the capabilities that take a `remote` are
exactly the version-control operations Section 3.2 places host-side, and every other Section 9.1
capability is local to the checkout.** Decision 0093 extends that enumeration with the provisioning
capabilities rather than contradicting it. The 0058 correction restated here — every value an
operation needs, and that the engine resolves, MUST reach the backend through a capability signature
— is likewise untouched; only the value's source changes.

The reconsideration trigger recorded above has also become live rather than being resolved: the
fork-and-upstream arrangement is still unaddressed, and 0092 explicitly leaves it out of scope for
the same reason this decision did. It is now a read/write remote pair in the consumer's
configuration rather than a pair of repository-owned keys.
