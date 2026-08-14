# Background — 0092 Backend, forge and tracker selection are the consumer's, read from a consumer config

## Context

Section 6.2 puts `vcs`, `forge` and `remote` in `repo.policy.toml` and defends the placement:

> The backend selection is read here in both standalone and embedded use. An embedding consumer
> supplies the *credential* the selected backend uses and the *forge repository coordinate* it acts
> against, not the selection — so which code host a repository targets is repository-owned, while the
> credential for it and the repository on it are the consumer's. The split is not arbitrary: the host
> a repository publishes to is a property of its Way of Working, while which repository a credential
> is presented to is a decision that belongs with the credential.

**The paragraph contradicts Section 11 of its own document**, which states the opposite in one
sentence: "The service the credential is presented to travels with the credential on the same
reasoning: the engine runs where both are already held." Section 6.2 says the host is the
repository's; Section 11 says it travels with the credential. Both are normative prose in one
specification. The paragraph also uses "host" for two different things one clause apart — "which code
**host** a repository targets" is the kind of forge software, "the **host** a repository publishes
to" is the instance — and defends a two-way split (kind against coordinate) over something that has
at least three parts, the third being the access parameters decision 0091 introduces.

## The argument that decides it

**Backend selection cannot live in `repo.policy.toml` because reading `repo.policy.toml` requires
having already used the backend selection.**

```
read repo.policy.toml   →  needs the repository
obtain the repository   →  needs the forge kind, its access parameters, and a credential
forge kind              →  read from repo.policy.toml
```

This is a bootstrap cycle, not a preference. No threat model is required to see it and no override
escapes it: an override that can only be applied after cloning does not help anyone clone. It reaches
`forge`, the Section 0091 access parameters, the credentials, the remote, and the tracker selection
alike — every value needed to obtain a repository — and it does not reach `[scope]`, `[base]`,
`[policy]`, `[hooks]`, `tracker.transitions`, `[messages]` or `[tasks]`/`[driver]`, none of which is
consulted before the repository exists.

**`SPEC.md` already contains the workaround in prose.** Section 9.7's configuration bullet reads:
"The engine reads it from `repo.policy.toml`; Symphony supplies the matching operator credential
(`vcs.api_key`) and, for provisioning (**which precedes reading the base revision**), the repository's
remote." The parenthesis is the cycle, noticed and routed around one value at a time. Section 6.4
states the consequence from the other end: `vcs.api_key` is "the credential for **the repository's
selected** code host" — the operator holds one credential and a file inside the repository decides
who receives it.

**`SPEC.md` Section 10.9 already applies the right test to the same question one domain over.** The
coding agent and its effort are "selected in the operator policy config, because agent choice carries
model credentials and sandbox shape". The test is not "is it about the repository?" but "does the
choice carry credentials and shape what runs with them?". Backend selection passes it twice: it
decides which plugin is handed the consumer's credential, and which API that credential is spoken to.
Answering the agent question one way and the backend question the other is the same test giving two
answers. This is offered as corroboration; the cycle above is the reason.

**One key is answering two questions.** `[engine] vcs` reads as "the VCS backend selector" and is
taken to answer both what drives the working copy and what is spoken to the remote. Those are
different facts with different owners. A jj checkout reaches its remote over git, so `vcs = "jj"`
answers the first and says nothing true about the second — and the document never names the second at
all: `protocol` occurs once in `VCSX-SPEC.md` (GNU grep 3.11), in Section 1's "invocation protocol".
Section 3.3's jj sentence, read closely, is about where the backend *reads a remote name from* in a
secondary workspace, not about what it then speaks.

## Options considered

- **A — repository-owned, as today.** Rejected on the cycle.
- **B — repository declares, operator overrides.** Steelmanned properly, because it is the strongest
  alternative and it defeats an argument this decision does *not* rest on. The fork objection decision
  0085 used against a repository-owned coordinate — "every fork and mirror carries a diff in the file
  whose purpose is to be inherited unchanged" — does not survive B: the mirror does not diff the file,
  the operator running the mirror overrides. B also preserves the genuine ergonomic point that made
  Section 6.2 repository-owned in the first place, that a repository plainly *is* a GitHub repository
  and ought to be able to say so. B loses to the cycle and to nothing else: the declaration it
  preserves is unreadable at the only moment it would be needed. Recording this matters, because if
  the cycle is ever broken — a consumer that obtains repositories some other way — B becomes live
  again and the fork objection will not be available to argue against it.
- **C — operator-owned, no overrides (chosen).**
- **D — declare-and-cross-check**, the repository declaring and the engine refusing a mismatch.
  Rejected: it adds a configuration reason and a second writer for one fact, and the declaration is
  still unreadable during provisioning, so the check can only run after the moment it would protect.

On transport, once the values are the consumer's:

- **E — invocation arguments only**, as decision 0085 does for the coordinate. Steelmanned: it is the
  smallest possible addition, the engine reads no consumer file, nothing needs discovery rules, and
  Symphony passes values it already holds in memory. It loses on `engine-direct`. That topology is
  named in `SPEC.md` Section 3.4 and has no Symphony and no operator policy config, so under E the
  specification would describe how the values reach the engine and be silent on where a human keeps
  them — leaving the only topology with a human operator dependent on an unspecified wrapper.
- **F — the engine reads a consumer-owned config file (chosen).**
- **G — a file with arguments overriding it.** Rejected: a precedence chain, chosen immediately after
  rejecting precedence chains. Its ergonomic benefit is reachable under F by letting the consumer
  point the engine at a file it composed.

## Decision and reasoning

**C and F.** The forge kind, the Section 0091 access parameters and credentials, the remote, and the
tracker selection are the consumer's. There are no overrides: one owner per axis. The engine reads
them from a **consumer-owned configuration file** whose discovery is `Implementation-defined` and
MUST be documented.

**`repo.policy.toml` loses `[engine] vcs`, `[engine] forge` and `[engine] remote`.** What remains in
the file is exactly what a clone inherits unchanged and nothing that is needed to obtain the clone.
`[engine]` is then a table holding `version_floor` alone — a statement about what the policy document
requires of its reader rather than a selection of anything — and is renamed accordingly, because a
table named `[engine]` that selects no engine misleads every subsequent reader.

**"No overrides" is what makes this cheap.** Because the keys leave `repo.policy.toml` entirely
rather than being shadowed, Section 6.1's "`repo.policy.toml` keys take precedence on conflict" needs
no exception: after this decision there is no key that both files can carry. A design with overrides
would have had to invert that sentence for some keys and not others.

**The local VCS is nobody's to declare.** For an existing checkout, detection is authoritative:
`detect_mode()` is a required Section 9.1 capability, the engine already consults it before the first
dispatch, and `checkout_unreadable` already covers the undetermined answer. The one moment a choice
genuinely exists is when a checkout is *created*, because there is nothing to detect until then —
and today the engine never creates one, so detection covers every case this decision has to serve.
The creation-time input is named in decision 0093, which is where creation exists at all.

**The remote is the one the repository was provisioned from.** The operator names it once, to obtain
the repository, and the same value is what the three network-touching Section 9.1 capabilities act
against. This supersedes decision 0062's placement while keeping its invariant intact — the
capabilities that take a remote are exactly the operations Section 3.2 places host-side — and it
survives 0062's own objection to derivation, which was that the work branch "is engine-derived and
MAY be absent from the checkout at the first push, so the configuration read is exactly the one that
does not exist". A provisioning remote exists before anything else does. What 0062 was filed to fix
stays fixed: two conforming engines given the same configuration push to the same place. What is lost
is the fork case 0062 left explicitly out of scope — a repository that pushes work branches to a fork
while pulling base from upstream — which now needs a read/write remote pair rather than a
repository-owned key, and is out of scope here for the same reason it was there.

**The tracker selection does not move.** `tracker.kind` is already operator-owned and stays so; the
cycle reaches it (a tracker credential and endpoint are needed before any repository file is read)
and confirms the existing placement rather than changing it. Recorded because the question was asked:
a repository-owned tracker declaration was considered and rejected, so it is not reopened by noticing
that `tracker.transitions` sits in `repo.policy.toml`. Transitions are a Way of Working; which tracker
service to authenticate against is not.

**Assumption recorded, because it is the sensitive part.** The consumer configuration file MAY carry
a credential directly *or* a reference the consumer resolves. `SPEC.md` Section 15.3 requires
`vcs.api_key` to resolve through the secret-provider interface and forbids environment variables as a
secret channel, so a file that could only hold a literal secret would force Symphony to materialize a
resolved secret to disk — the step Section 15.3 exists to avoid. Admitting both forms keeps
`engine-direct` ergonomic, where a token in one's own configuration is ordinary, without imposing
that on a service with a secret provider. Section 11's "the engine holds no long-lived credentials of
its own" narrows to: the engine does not persist a credential beyond an invocation.

**The validation boundary is redrawn at the checkout.** Section 6.10 currently judges validation from
"what the engine holds independently of the invocation", which is what `capability_unsupported` turns
on, and Section 8.6 draws its boundary against that phrase. Once the backend selection is a consumer
input, that phrase is false: `[messages.squash] strategy` remains repository-owned, and Section 9.3
refuses at validation a strategy no configured forge declares, so the check now reads a repository key
against a consumer-selected backend's descriptor. The seam is already in the document — Section 8.6
establishes `arguments_unreadable` *before* validation, "because an engine that cannot decode its
arguments cannot locate the policy it would validate", so the invocation's inputs are decoded by the
time validation runs. The boundary becomes: a configuration error is judged from the policy document,
what the engine holds, the consumer's bindings **and the consumer's selection**; a precondition is
what needs **the checkout**. `capability_unsupported` stays a configuration error, refused before
anything is published, which is decision 0084's argument.

## Reconsideration trigger

Reconsider if the bootstrap cycle is ever broken — a topology in which repositories arrive by some
route that does not consult the forge configuration. Option B then becomes live again, and the fork
objection recorded above will *not* be available to argue against it, so the argument would have to be
made afresh. Reconsider the transport half separately if a second engine implementation and a
front-end diverge in where they look for the consumer configuration despite the MUST-document clause;
the repair is then a named search order, not a move back across the ownership boundary.

Relates to 0091 (which defines the parameters this decision assigns an owner), 0093 (which adds the
creation-time local-VCS input this decision defers), 0062 (superseded in placement, its invariant
kept), 0085 (whose "one decision, one party" principle this extends from the coordinate to the
selection, and whose fork objection is recorded here as considered and not load-bearing), and 0002
(whose anchor-change rule governs the `[engine]` rename).

## Review finding, 2026-08-14 — the boundary repair reproduced the failure it repaired

Found while applying this decision to `conformance/vcsx/vocabulary.json`, before the specification
change landed.

**The shape of the defect.** The reasoning above redraws the Section 6.10 / Section 8.6 boundary as a
two-sided claim: a configuration error is judged from five inputs none of which is the checkout, and
"a precondition is what needs **the checkout**". The second half is false. Four of the eight entries
in the precondition registry need no checkout at all — `arguments_unreadable`,
`forge_coordinate_missing`, and the two `git_access_missing` / `forge_access_missing` that decision
0091 adds. Each is judged from the invocation's arguments alone. Written as stated, the boundary
would reclassify half its own registry.

**It is a recurrence, and this decision caused the count to grow.** The wording being repaired was
already loose in the same direction: Section 8.6 said "a precondition failure needs the invocation's
arguments **and** the checkout", a conjunction already false for `arguments_unreadable`. That went
unnoticed because the *config* side carried the distinguishing work — "independently of the
invocation" was true and sufficient, so nothing depended on the precondition side being exact. This
decision moves the invocation's selection to the config side, which makes the config side stop
distinguishing anything on its own, and then restates the precondition side as the thing that
distinguishes — promoting a clause that was incidentally loose into one that is load-bearing and
wrong. Entries misdescribed: one before, four after. The repair reproduced the failure it was
repairing, one register up.

**The repair.** State the boundary **one-directionally**, on the config side only: a configuration
error is judged without reading the checkout. Do not characterize the precondition side as a
conjunction or as "needs the checkout"; let each entry say what it is judged from, as the registry
already does per row.

What then separates the two registries, for the entries where both are checkout-free, is not the
input but the artifact at fault: **a configuration error names a defect the consumer repairs by
editing a document; a precondition failure names one it repairs by changing the invocation.** That is
checkable by a consumer without knowing the engine's internal ordering, which the input-based
formulation only appeared to be. The existing ordering rule is unaffected — validation precedes
precondition establishment, `arguments_unreadable` excepted — and so is Section 9.3's disposition for
`capability_unsupported`, which turns on the config side alone.

`Plan.md` step 8 is amended accordingly; step 7's five-input restatement stands unchanged, since the
config side was never the false half.
