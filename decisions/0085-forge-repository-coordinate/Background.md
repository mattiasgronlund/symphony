# Background — 0085 The forge repository coordinate is the consumer's

## Context

Resolves issue #39. Section 6.2 makes the forge **selection** repository-owned and the
**credential** the consumer's, and nothing between them says how the selected backend learns it is
talking about one repository rather than another on the same host. Section 9.2's required
capabilities take a head, a base, a title, a body, a pull request, a strategy and a head — none
takes a repository. Section 8.1's common arguments name four things and a forge coordinate is not
among them. Section 7.3's embedded driver "supplies the execution context … and the credentials the
plugins use" and names nothing else.

Deriving it from the checkout is foreclosed twice: Section 1.3 has the engine perform no repository
provisioning, and Section 6.2 says a backend "does not infer it from the work branch's own upstream
binding, which need not exist". Section 9.1 has no capability that answers a remote URL, an owner or
a repository name. Section 3.3 uses the phrase "remote slug" for a jj secondary workspace, and
`slug` appears nowhere else in the document except Section 6.3's example branch pattern — so the one
place the document names the concept is a requirement with no capability behind it.

**The subprocess encoding is where this stops being theoretical.** Section 8 says the contract is
the same either way and only the encoding differs. An embedded driver can be handed a coordinate
through a constructor; a subprocess front-end has nothing to encode, because Section 8.1 fixes the
argument list and leaves only the encoding to the engine. The consequence is total rather than
partial: a repository that sets `[engine] forge = "github"` cannot be run by a conforming subprocess
front-end at all — not `create_pr`, not `merge`, not `ship` or `land`, and not `push` or `status`,
because Section 4.1 has both read the work branch's pull-request state where a forge is configured.
Six of the ten entry points, on any repository that configures a forge.

## The argument that decides it

The service root was settled first, and on a security argument: it is not derivable from a host name
— GitHub serves `api.github.com` for the public host and `<host>/api/v3` for an enterprise one, and
a self-hosted Forgejo can live under a path prefix — and a wrong answer there is an exfiltration
path rather than a misfire, because Section 3.2 leaves the sourcing rule to the consumer, so a root
read from a repository file a consumer sourced from the worktree is a credential presented to a host
the worktree named.

**That argument does not stop at the root.** Deriving the coordinate from the resolved remote's URL
reads it from the checkout's configuration rather than from tracked content, which is better
protected than a tracked file — but Section 3.2 makes the boundary the consumer's to place, and in
the sandboxed-agent topology it is the worktree, not the checkout. A consumer that exposes `.git` to
the agent has handed it `git remote set-url`, and the engine will then push the work branch and open
a pull request against whatever repository that names, with the consumer's credential attached.
Pinning the root to the credential bounds this to one host, and same-host redirection is still
presenting a credential to a repository its holder did not choose.

The credential and its target are one decision. What makes the hazard possible under a
backend-derived coordinate and under a repository-owned key alike is letting the two be made by
different parties.

## Options considered

- **A — backend-derived from the resolved remote, consumer-overridable.** A Section 9.1
  value-answering capability answers the resolved remote's coordinate, with an OPTIONAL Section 8.1
  override. Rejected on the argument above. Two things in it are worth keeping and are kept:
  - Its Section 3.3 argument is textual and is the strongest thing in the package. That sentence
    already presumes backend-derived slugs with no capability behind it, and the gap is real — so
    resolving this issue has to settle the sentence, whichever option lands, because it is the only
    place the concept appears and nothing says whether a "slug" is a remote name, a URL, or an
    owner/name forge coordinate.
  - If a capability ever answers this, it answers the resolved remote's **URL, opaquely**, and the
    forge backend interprets it. Parsing an owner and a name out of a remote URL is service-specific —
    SSH against HTTPS, ports, nested namespaces on Forgejo and GitLab — and a VCS backend has no
    business knowing a forge's URL grammar. As drafted, option A put forge knowledge in the VCS seam,
    which is the mixing Sections 9.1 and 9.2 are separate to prevent.
- **B — consumer-supplied, named in Section 8.1 (chosen).**
- **C — repository-owned, as `[engine] remote` became in decision 0062.** Rejected before the
  worktree-sourcing hazard is even reached, on the fork objection: a remote *name* is checkout-local
  and identical in every clone, while an owner/name coordinate is not, so every fork and mirror
  carries a diff against upstream in the file whose entire purpose is to be inherited unchanged. The
  analogy to 0062 is weaker than it looks for exactly that reason.

## Decision and reasoning

**B.** The forge repository coordinate is a Section 8.1 common argument, REQUIRED where a forge is
configured, supplied by the consumer on the same side of the boundary as the credential.

**B's stated cost is real and does not belong in the specification.** "A human at a prompt supplies
it every invocation" assumes the front-end cannot default it. It can — from the resolved remote,
exactly as option A would — and doing it there keeps the derivation on the credential-holding side
of the boundary. Section 8.1 already makes encodings the front-end's business, so an interactive
front-end that reads the remote and fills the argument in is conforming, while a consumer that needs
to be explicit stays explicit. Section 1.1's "usable without any particular consumer" is satisfied
either way, because an interactive front-end *is* a consumer.

So this is option B's contract with option A's ergonomics, and the difference between them is only
who derives: under A the engine derives from a value the checkout carries and the consumer never
sees; under B the consumer derives and the engine is told. That is not a cosmetic distinction — it
is the whole of the security argument.

**Section 3.3's sentence is settled as part of the answer.** The phrase "remote slug" is replaced by
the terms the document defines: in a secondary workspace the backend resolves the **remote**
(Section 6.2) and the work branch from jj rather than from a colocated git remote. The forge
repository coordinate is not derived from the checkout in any mode, which the section states so the
concept has one meaning rather than an unresolved one.

**Absence is a precondition, not a first-use failure.** A forge configured with no coordinate
supplied is refused before the policy runs, with the `usage_or_config` status and a precondition
reason of its own. That is Section 8.6's own boundary — judged from the invocation's arguments — and
it refuses the invocation rather than letting it publish a work branch and fail at `create_pr`,
which is the same argument decision 0084 makes for `template_unbound` one seam over.

**The engine holds the coordinate opaque**, as it holds the commit identity (Section 10.1) and the
base ref (Section 6.4) opaque: it takes one, supplies it to the forge backend, and does not
interpret it. Its shape is the forge backend's, so a coordinate a backend cannot use is that
backend's first-use `failed` rather than a shape the engine judged.

**The credential and the service root stay out of the argument list**, for the reason the report
gave for excluding the credential: Section 11 has the engine run "where they are already held", so a
front-end reading them from its own environment is the consumer's arrangement rather than a gap in
this contract. What is added is the one fact that is neither a secret nor the operator's ambient
state, and that the specification twice forbids deriving from the checkout.

**Disclosure, recorded because it should be discounted for.** B is also the cheapest outcome for the
implementation that filed the report — its forge plugin already receives the coordinate at
construction, so B is a front-end gaining an argument and unblocking six of ten entry points, while
A would need a new Section 9.1 capability, both plugins implementing it, and a contract-suite case.
The reporter raised this rather than leaving it to be noticed. The recommendation and the
convenience point the same way, and the argument above stands on the sandbox boundary rather than on
the cost.

## Reconsideration trigger

Reconsider if a topology appears in which the consumer genuinely cannot know the coordinate it
provisioned — which would be a consumer that provisioned nothing, and therefore outside Section
1.3's division of labour rather than an argument against B. Reconsider separately if front-ends
diverge in practice on how they default the argument from the remote, since the divergence B pushes
into the front-end is the one thing option A would have standardized; the repair then is a
RECOMMENDED defaulting rule in Section 8.1, not a move of the coordinate back across the boundary.

Relates to 0062 (whose repository-owned remote is the analogy option C rests on and which does not
carry), 0065 (which built the precondition registry this reason joins), 0073 (which enumerated what
a consumer mediates) and 0084 (whose refuse-before-publishing argument this one shares).
