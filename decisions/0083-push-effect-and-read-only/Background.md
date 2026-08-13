# Background — 0083 The push guarantee is quantified over the effect

## Context

Resolves issue #37. Section 3.3 names `jj` as a checkout mode a backend "detects and adapts to";
Section 9.1 is the surface it adapts through, and until a second backend exists nothing tests
whether that surface is VCS-neutral or is git's mechanics written down as a plugin API. Writing one
against jj 0.44.0 produced two clauses with the same shape: each is an absolute, jj cannot satisfy
either literally, each is satisfied in the effect the clause exists for, and the document does not
say which is required.

**The push.** Section 9.1 pins the refspec "and never a force push", and Section 11 restates it as a
property a consumer's scope guard relies on. `jj git push` always leases: it spawns git with
`--force-with-lease=refs/heads/<branch>:<what jj last fetched>` on the create path and the update
path alike, and offers no non-forcing mode — observed on the argv rather than recalled, by pointing
jj's `git.executable-path` at a logging shim. The obvious consumer mediation for "never a force
push" — refuse a push carrying a force flag — refuses **every** push a jj backend makes, so the
reading decides whether a conforming engine can drive a jj repository at all, and it decides it in
the section a mediating consumer implements against.

**The reads.** Section 4.1 marks `status` and `diff` "Read-only", and Section 9.1 makes `is_dirty()`
a predicate about the worktree. jj snapshots the working copy into the working-copy commit at the
start of every command, `jj status` included; `--ignore-working-copy` skips the snapshot and
therefore answers about a working-copy commit that may no longer describe the worktree, which is the
wrong answer to the question Section 9.1 asks, because a stale answer of "clean" makes a caller skip
a `commit` that had something to capture.

## The lease does not satisfy the effect guarantee, and the report was wrong to say it did

The report recorded the push clause as "satisfied in effect and not literally". This decision's
first draft agreed and proposed to write it into the specification — that a lease is a
compare-and-swap which "refuses exactly where a plain push refuses". **That is false, and the case
where it fails is the case the guarantee exists for.**

The two mechanisms refuse on different predicates:

- a plain push refuses when the update is not a fast-forward — that is, exactly when commits would
  be dropped;
- `--force-with-lease=<ref>:<expected>` refuses when the remote ref is not at `expected` — that is,
  when the remote moved.

They coincide in the common case and diverge in one that matters:

1. The engine observes the remote work branch at `X`, so the lease value is `X`.
2. The local bookmark sits at `W`, an ancestor of `X` — something outside the engine rewound it.
   Section 11 guarantees the engine never does this; it does not guarantee nobody does.
3. The remote is still at `X`, so the lease matches.
4. The push succeeds and force-updates `X` → `W`, dropping every commit between them.

A plain push refuses step 4. The lease permits it. So the divergence is precisely the destruction of
remote history on the work branch, which is what a consumer relying on Section 11 believes cannot
happen — and a specification that blessed the lease would have blessed that.

The reporting implementation recorded the hole and under-weighted it, noting a locally rewound
bookmark would be published over the remote while still writing "satisfied in effect". Under the
effect formulation's own sentence, it is not. It is a live hazard: the jj plugin has no ancestry
guard and relies on the lease plus parsing jj's stderr.

## Why the neighbouring formulations do not rescue it

**Quantifying over observation.** "A push MUST NOT succeed where the remote work branch carries a
commit the engine did not observe" is testable and asserts nothing false, and it is more precise
than the phrase it would replace. It also permits step 4 — the engine *did* observe `X`. It is
quantified over observation where the hazard is about destruction, and those are not the same
property. It trades an absolute for something narrower than what consumers rely on, so it is not the
stronger statement it looks like.

**Declaring the mechanism.** Keeping "never a force push" and adding a descriptor field naming the
push transport encodes an absolute in prose and a conditional in data, which is the pattern issue
#36 reports one section over. It also relocates the burden: every consumer would have to read a
descriptor field to learn whether its remote history is safe, and the consumers that do not read it
are exactly the ones the guarantee existed for. A guarantee you have to opt into checking is not
one.

## Options considered

- **A — quantify over the effect, and say nothing about mechanism (chosen).** The engine MUST NOT
  cause a push that drops, rewrites or re-parents a commit already on the remote work branch. The
  phrase "force push" leaves the document, in Section 9.1 and in Section 11 alike, so nothing has to
  rule on whether a lease is one and no backend can argue from flags.
- **A′ — the same requirement, plus a sentence blessing leases.** Rejected on the counterexample
  above. This was the drafted recommendation and it was wrong.
- **B — quantify over observation.** Rejected: it permits the one case that matters, for the reason
  above.
- **C — keep the mechanism absolute and declare the transport in the descriptor.** Rejected on the
  relocation-of-burden argument and on the prose/data split.

## Decision and reasoning

**A.** Section 9.1's `push` entry keeps the pinned refspec and drops "never a force push";
Section 11 keeps the pinned refspec as the consumer's fixed target and states the effect requirement
in place of "never force-pushes". Nothing in the document names a flag, so a backend either meets a
testable rule or does not.

**Who pays, stated plainly.** This makes an unconditional lease a **genuine non-conformance** rather
than a concession, and that is the right outcome, because the repair is cheap and belongs to the
backend: before invoking `jj git push`, check that the local bookmark is a descendant of the
observed remote bookmark, and report `push:non_fast_forward` without spawning where it is not. That
restores the effect guarantee whatever the transport does underneath, and `push:non_fast_forward`
already routes to `integrate` and retries within the flow bound (Sections 5.6, 12.2), so no
machinery is added.

**The cost, and why it is small.** The guarantee is no longer readable off the argv, so a mediating
consumer trusts the backend where it could previously inspect a flag. Section 11 already directs the
guard at the pinned refspec rather than at the absence of a flag, and a guarantee readable off the
argv was never the guarantee — it was a proxy that held while git was the only backend, which is
exactly what a second backend was going to reveal.

## The reads: one repair, not a choice

Section 9.1 already carries the answer's shape for exactly one capability, `worktree_revision()`,
which MAY derive its identity "by writing to its own staging or bookkeeping state", MUST NOT thereby
change the content a `commit` would capture, and MUST document the effect where it writes. The
capabilities that realize `status` do not have it, and a rule that holds for one capability and not
for its neighbour is the next report — the shape issues 26 and 28 both had.

The repair is to state the allowance over the capability list rather than inside one entry, and to
define what Section 4.1's "Read-only" quantifies over: the history, the remote, and the content a
`commit` would capture. The "MUST document the effect where it writes" obligation travels with the
generalization, so a backend that snapshots to answer a read says so under Section 13.3. This is
recorded as part of this decision rather than as an option, because no alternative was offered: the
wording exists in the document already and is scoped one capability too narrow.

## Review finding applied (PR #40)

**The read allowance introduced a new undefined absolute in the place this decision had just removed
one.** As first written, the generalized allowance said a backend writing bookkeeping state "MUST NOT
write to the history or the remote", and Section 4.1's definition said a read "writes nothing to the
history". `history` is nowhere defined in this document — nine uses, all informal — and the
motivating case defeats the literal reading: `jj status` snapshots the working copy into the
working-copy commit, which writes a commit object and moves a ref. This decision's own Background
argues that is jj's staging equivalent, and the argument holds, but the specification did not say so.
A jj backend author arriving at the repaired clause would have met exactly the question this decision
exists to end — an absolute that cannot be satisfied literally, with no statement of which reading is
required.

Both ends are now quantified over the same three things, named rather than gestured at: the content a
`commit` would capture, the commits reachable from the work branch or the resolved base, and what the
remote holds. Section 9.1 states the carve-out positively — a backend MAY record the working tree as
a commit where its checkout mode requires one — and gives the reason the object store is not the
measure: a commit no branch the engine named reaches is not observable through this specification's
operations, because what `status` and `diff` report against, and what a `push` publishes, are
branches.

The finding is the same shape as the report this decision answers, one iteration in: a guarantee
stated in one VCS's vocabulary, met by an implementer who then has to choose between conforming and
working. It is recorded rather than quietly fixed because the recurrence is the point — the first
draft of a repair for that failure reproduced it.

## Reconsideration trigger

Reconsider if a VCS backend appears whose transport can satisfy the effect requirement only by a
mechanism the document would need to name — the argument for C arriving as evidence rather than as
preference. Reconsider separately if "Read-only" quantified over the history, the remote and the
committed content proves too permissive for a consumer that mediates by filesystem observation,
which would mean the definition needs a fourth clause rather than a narrower one.

Relates to 0073 (which enumerated the network-touching capabilities a consumer mediates), 0079
(which established that an operation acts on the state its position inspected), 0076 (the
answer-domain rule the read allowance is stated beside) and 0063 (which made `is_dirty()` `commit`'s
predicate).
