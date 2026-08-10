# Background — 0075 A failed counterpart acquisition is `pull:failed`

## Context

Resolves issue #26, raised while implementing Section 9.1's capability split against `1a36ebe7`.

Decision 0073 split `pull` into `fetch_counterpart` and `merge_counterpart`, and concluded in as many
words that the operation gains no reason token: "no built-in sequence retries it, so `pull:failed`
remains sufficient, and an absent counterpart stays a benign `pull:ok`". Section 9.1's realization of
that split does not carry the conclusion through. `fetch_counterpart(remote, work_branch)` answers "the
ref of the work branch's remote counterpart, or none where the remote carries none" — two answers for
three conditions:

| Condition at the remote | The capability answers | The engine reports |
|---|---|---|
| The counterpart exists | the ref | `pull:ok` / `conflict`, through `merge_counterpart` |
| The remote carries none | none | `pull:ok`, a benign no-op |
| The acquisition failed | none, there being nothing else | `pull:ok`, class `done`, exit `0` |

The third row is the defect. A fetch that failed — the remote unreachable, the credential refused, the
configured remote name absent from the checkout — is not "the remote carries none", and the answer that
would say so is spoken for. An engine composing `pull` as Section 9.1 describes reads the absent answer
as "nothing to merge", and **a run that pulled nothing reports success**.

What is missing is not a reason. `pull:failed` is in the registry, class `error`, and has been since
decision 0057 made `failed` universal; it is *unreachable*, because nothing in the invocation
distinguishes the condition that raises it. The usual report says the specification has no word for a
condition. This one says it has the word and no path to it.

Two things sharpen it beyond the implementation that filed it.

**Two normative sections disagree.** Section 6.2 states that a configured remote the checkout does not
carry is not a configuration error and "surfaces at first use as the operation's `failed` reason
(Section 4.3)". For `pull`, first use *is* `fetch_counterpart`, and Section 9.1's answer domain makes
that surfacing impossible. Section 6.2 promises an outcome Section 9.1 forecloses, so this is a
contradiction inside the document rather than a trap an implementation happened to fall into.

**The conformance matrix cannot catch it.** Section 13.1 asks for the failed-acquisition check on one
side of the split — "an `integrate` whose acquisition fails yields `base_unavailable` rather than
retrying to the flow bound" — and asks nothing of `pull`. The filing implementation shipped the bug
green through a full gate, because its tests encoded the same assumption its code did; a conforming
engine would have had no matrix row telling it otherwise.

A third gap is smaller and is fixed alongside: that an absent counterpart is a benign `pull:ok` is
recorded in decision 0073's `Background.md` and nowhere in `VCSX-SPEC.md`. The three conditions and
their three results have never all been stated in one place.

## The report's second shape is unsound, and the reporter has withdrawn it

Issue #26 offers two shapes and calls the second smaller and preferable: give `pull` one combined
counterpart-side token covering both non-ref conditions, "as `base_unavailable` covers both for
`integrate`", at which point the two-valued answer is sufficient here for the same reason it is
sufficient there. It cannot be built, and the reason is worth keeping because it is what makes the
`integrate`/`pull` asymmetry legitimate rather than accidental.

A reason carries exactly one proto class (Section 4.2), and that class is frozen within a `MAJOR`
(Section 8.5). `base_unavailable` combines two conditions that are **both failures** — the branch has no
copy in the checkout, or acquiring it failed — so one class serves both and one word can mean both. The
counterpart's two non-ref conditions straddle the class boundary: "the remote carries none" is the
ordinary state before the first push and its correct result is *success*, while "could not reach it" is
a failure. A combined token at class `error` makes every first push report an error — the direction the
issue itself rejects when it refuses to treat an absent answer as a failure. At class `done` it is
today's defect wearing a new name.

So the three-valued answer is not one of two options; it is the floor under both. The second shape is
the first plus a name, not a different shape, and the choice this decision actually faces is only how
the third condition is *named*.

## Options considered

- **Option A — the capability distinguishes the three conditions, and the failure is `pull:failed`
  (chosen).** Section 9.1 gives `fetch_counterpart` a third answer; Sections 4.1 and 4.3 state the
  three-way mapping; Section 13.1 gains the check. No token, no `vocabulary.json` change, nothing added
  to the major-stable surface.
- **Option B — Option A, plus a registered `pull` / `counterpart_unavailable`, class `error`
  (rejected).** The sound version of what the issue asks for, and the only one worth weighing: it lets a
  policy escalate an unreachable remote without also catching a failed merge, and it makes the registry
  read symmetric beside `integrate` / `base_unavailable`. Rejected on 0073's own test for minting a
  token, below.
- **Option C — a combined counterpart token, leaving the two-valued answer as it is (rejected).** The
  issue's stated preference. Rejected as unsound: no single reason can carry a benign absence and a
  failure, per the class collision above. Recorded rather than dropped, because the issue proposes it
  and a later reader will find it there.
- **Option D — state an answer-domain invariant over Section 9.1 as a whole (not taken here).** Every
  capability either answers the operation's typed result or has each of its non-answers mapped to a
  reason in Section 4.3 or a precondition reason in Section 8.6, with Section 9.1 stating the mapping.
  The observation behind it is real and worth recording: Section 9.1 mixes capabilities that answer
  `<op>:*` with capabilities that answer a bare value without ever saying so, and of the three
  network-touching capabilities, `push` answers a result while both fetches answer a value — exactly
  where a transport failure has nowhere to go. `fetch_base` survives only because Section 4.3 happens to
  map its absent answer to `base_unavailable`. Not taken: an invariant quantified over the capability
  list sits at a different altitude than Section 9.1's prose, and the enumeration it would generalize is
  one decision old. It is the repair to reach for if a second capability repeats this.

## Decision and reasoning

`fetch_counterpart` answers three ways rather than two — the counterpart ref, none where the remote
carries none, or that the acquisition failed — and the engine reports the third as `pull:failed`. No
reason token is added.

**Why no token, on 0073's own test rather than on size.** 0073 earned `base_unavailable` operationally,
not as bookkeeping. Section 12.2 routes `push:non_fast_forward` to `integrate` and retries the push, so
a failed acquisition could not converge: the run burned the flow bound (decision 0060) and surfaced as
`flow_exhausted`, which tells a caller "the graph does not converge or the remote is moving" rather than
"your remote is down" — 0064's complaint that "the failure got quieter, not louder". The token exists
because a **built-in loop was misdiagnosing**. Neither Section 12.2 nor Section 12.3 dispatches `pull`
(decision 0074 notes the same in passing), so there is no loop to misdiagnose, and the universal
`failed` is doing precisely the job Section 4.3 defines it for. "Defined for every operation" is the
specified answer for an operation that failed, not a fallback taken where a better token was
unavailable.

Section 8.5 makes every reason permanent shared surface, and decision 0066 already ruled against this
engine's instinct to reach for a specific token where a wider one fits: three distinguishable states
with one owner, one repair and no caller that branches between them got one token, not three. Minting
`counterpart_unavailable` here is that mistake pointed the other way — a narrow token where the wide one
is the specified answer.

**Why the symmetry argument that carried 0073's split does not carry a token.** 0073 split `pull` for
symmetry alone, on the reasoning that "a naming rule that holds for `integrate` and not `pull` is the
next report", and the issue reads the missing token as that same asymmetry one layer down. It is not.
The two operations differ because **a base is required to exist and a work branch's counterpart is
not**: the base's non-ref answers collapse to one class and the counterpart's do not. The asymmetry is
in the subject, not in the naming, so the fix is to state it rather than to remove it — which is why
Section 4.3 gains a sentence and not a row.

**What the fix costs.** `pull:failed` covers both halves of the split, so a policy cannot bind a failed
acquisition apart from a failed merge, and a consumer handling one real-world condition across both
operations writes two shapes: `integrate:base_unavailable` on one side, `pull:failed` on the other. That
is accepted rather than argued away. Separating the two conditions is also work for a backend rather
than free: the git realization distinguishes them with `git ls-remote --exit-code`, whose exit `2` means
"no matching ref" and whose other non-zero codes mean transport — a documented contract, where reading
`git fetch`'s stderr prose would make git's wording part of the engine's behavior. The specification
states the required distinction and leaves the mechanism to the backend, as it does everywhere else.

**What would make us reconsider**, named rather than left implicit: a consumer that must tell an
unreachable remote from a failed merge **in order to act differently** — retry later versus escalate to
a person. Symphony is plausibly that consumer at the point it classifies what a failure means for
recovery (`SPEC.md` Section 14.3). Section 8.5 admits a new reason token in a `MINOR` release and
existing consumers absorb it through the `#class` fallback, landing on the `error` edge they already
have, so deferring costs a later minor bump and nothing else. That asymmetry — cheap to add later,
permanent once added — is the whole case for waiting, and it is why this decision states the
reconsideration trigger instead of closing the question.

Relates to 0073 (whose conclusion this carries into Section 9.1, and whose realization it repairs
without disturbing the decision itself), 0057 (whose universal `failed` is the answer, and whose defect
— a registry enumerated per operation against rules quantified over operations — this is the mirror
image of: a rule the registry states and a capability cannot reach), 0066 (whose "the wider token where
it fits" ruling this follows), 0062 and 0064 (whose remote and acquisition semantics fix what "failed"
means here), 0060 (whose flow bound is what `base_unavailable` was minted to stop misreporting), and
0074 (which established that `pull` is reachable only through a policy edge).
