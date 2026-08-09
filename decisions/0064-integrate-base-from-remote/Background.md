# Background — 0064 `integrate` resolves the base against the remote; the read-only operations do not

## Context

Resolves part 3 of issue #9, raised while building the first real `VCSX-SPEC.md` Section 9.1 VCS
backend (`vcsx-plugin-git`, against `06a3bc19`).

`VCSX-SPEC.md` Section 4.1 defines `integrate` as "bring the resolved base into the work branch (a
merge/update-branch)". Section 6.4 resolves the base to a *branch name*. Whether that name means the
branch as the checkout holds it or as the remote currently holds it is not stated, and the same question
applies to `ahead_behind(base)` and `diff(base)`, which take the same resolved name.

The document already decides it, in two places that do not mention each other:

- **For `integrate`, against the remote.** Section 12.2 routes `push:non_fast_forward` to `integrate`
  and retries the push. That loop converges only if what `integrate` brings in is the base as the remote
  holds it. Integrating a stale local copy leaves the push non-fast-forward on every attempt, so a
  correct policy against a base branch that moved once would run until decision 0060's flow bound ended
  the invocation at `needs_caller` with the `flow_exhausted` need — a hold, on a flow that was one fetch
  away from succeeding.
- **For the read side, not against the remote.** Section 4.1 marks `status` and `diff` "Read-only", and
  acquiring the base needs the network and writes refs.

So the answer exists, distributed across a reference algorithm and a two-word label, and an implementer
reading Section 4.1's `integrate` bullet finds neither.

Decision 0060 sharpened the stakes rather than creating them. Before the flow bound, a stale-base
`integrate` produced an engine that spun; after it, the same engine terminates and reports a plausible
`flow_exhausted`, which reads as "the graph does not converge or the remote outruns the engine" when the
truth is that the engine never fetched. The failure became quieter, not louder.

The filing implementation's meanwhile-answer is exactly this split, derived the same way.

## Options considered

- **Option A — `integrate` resolves the base against the remote; `ahead_behind` and `diff` against the
  checkout's copy** (chosen). It states each half where it is read and names the asymmetry as
  deliberate. Trade-offs: `status`'s `ahead`/`behind` counts and `diff`'s delta MAY be stale, which a
  caller must know; the alternative is worse (Option C).
- **Option B — the checkout's copy for everything** (rejected). It is the reading that makes every
  operation local and credential-free, which is attractive against Section 3.2's trust split. It breaks
  Section 12.2's built-in routing: `push:non_fast_forward → integrate → push` cannot converge, so the
  document's own default policy would be wrong for the case it exists to handle. Rescuing it would mean
  adding a fetch step to the operation set that every policy must remember to route, which is the
  opposite of the "the policy is written against neutral operations" goal (Section 2.1).
- **Option C — the remote's copy for everything, including `ahead_behind` and `diff`** (rejected). It
  removes the asymmetry, which is its only virtue. Section 4.1 marks `status` and `diff` "Read-only",
  and acquiring the base needs the network and a credential — so a read-only operation would become
  credentialed, and a consumer running it in-sandbox (Section 3.2) could not run it at all. It would
  also make `status`, the cheapest operation in the set, the one that touches the network.
- **Option D — make it configurable** (rejected). Nothing about it is a Way of Working. One answer makes
  Section 12.2's built-in routing converge and the other does not, so a repository choosing the second
  would be choosing a broken engine; a configuration key whose wrong value is never correct is a defect
  surface, not a policy surface.
- **Option E — state it only for `integrate` and leave the read side to "Read-only"** (the issue's own
  position: "the read side is already settled and needs nothing"; rejected as insufficient). It is true
  that "Read-only" settles it. It is also true that the same word settled it before this issue was
  filed, and the issue was filed anyway — by someone who had read the document closely enough to derive
  the answer and still wanted it said. Stating one half and leaving the other to inference invites the
  next reader to re-derive it, and the derivation is only obvious once you know which way it comes out.

## Decision and reasoning

`integrate` brings in the base as the configured remote holds it (Sections 6.2, 6.4), acquired rather
than read from the checkout's copy. `status` and `diff` are read-only and report against the base as the
checkout already holds it, so their `ahead`/`behind` counts and their delta MAY be stale where the
remote has moved.

The reasoning worth keeping is that **the asymmetry is not a compromise between freshness and cost — it
follows from Section 3.2's trust split, and the operations divide exactly along it**. An operation that
acquires the base is host-side because it needs the network and a credential; an operation that does not
can run in-sandbox. Once that is said, no separate rule is needed for either half, and the same test
answers the next operation added: if it acquires, it is host-side, it takes the remote (decision 0062),
and Section 3.2's list must name it.

That framing is what makes Option C's cost visible. Making the read side fetch does not merely add
latency, it moves `status` and `diff` across the trust boundary, and Section 3.2's whole purpose is that
a consumer can split one policy across it. A read-only operation that needs a credential is a category
error in this document, not just an expensive call.

The convergence argument stands on its own and is recorded in the text at Section 12.2, where the loop
is: the retry converges because `integrate` acquires the base, and against a stale copy the push would
stay non-fast-forward until the flow bound ended the invocation. Stating it there means the next reader
of the algorithm does not have to reconstruct why the loop terminates in the good case.

The staleness this leaves on the read side is real and is stated rather than hidden: a caller that needs
current figures runs `integrate` first. That is a worse ergonomic than a fetching `status`, and it is
the price of keeping `status` runnable without credentials. It is also the same price Section 4.1
already pays by marking the operation read-only, so the decision changes nothing about what an engine
does — only about whether an implementer has to guess.

`pull` is unaffected and needs no clause: Section 4.1 already defines it as updating "from its remote
counterpart", which says where it reads from, and decision 0061 fixed how it applies what it finds.

What would make us reconsider: a checkout mode whose base is not meaningfully "local" or "remote" — a
virtual filesystem checkout, say, where the distinction has no cost — which would make the asymmetry
pointless rather than wrong. Or a consumer for which a stale `ahead`/`behind` is actively harmful, which
would argue for an OPTIONAL fetching variant of `status` rather than for changing this one.

Relates to 0062 (which supplies the remote this decision has `integrate` resolve against), 0060 (whose
flow bound is what a stale-base `integrate` now trips), and 0061 (the other operation that reaches the
remote, constrained on a different axis).
