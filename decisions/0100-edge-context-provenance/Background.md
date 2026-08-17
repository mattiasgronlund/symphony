# Background — 0100 An edge does not declare its execution context

## Context

Issue #52 reports that Section 6.5 makes an edge's `context` OPTIONAL and "defaulted per the action",
and that no default is stated for any action, in that section or anywhere else in the document.

### What the missing default costs

The label is not descriptive. Section 11 makes it part of the guarantee an embedding consumer relies
on — "An in-sandbox edge or hook MUST NOT receive credentials" — and Section 13.1 states the
consequence for a dispatch: "an edge declared `in_sandbox` receives no credential whatever it
dispatches, `provision` included".

So take a policy carrying one unlabelled edge:

```toml
[[policy.edge]]
on = "push:non_fast_forward"
do = "run_op"
op = "integrate"
```

An engine that defaults it host-side integrates. An engine that defaults it in-sandbox dispatches an
`integrate` that reaches the remote with no credential, and the invocation ends at the operation's
own `failed`. Same policy, same repository, same version — two conforming engines, two outcomes. The
repository cannot be blamed for it: the key is OPTIONAL, so a policy that omits it is well formed.

Section 13.3 is where a delegated choice would be published, and its list does not include this one.
The derivation is therefore neither stated by the specification nor declared `Implementation-defined`
and documented — an obligation with no rule and no publication requirement.

Section 8.5 makes it a forward problem as well as a present one. New operations MAY be introduced in
a `MINOR`. An operation added that way arrives with no context and no rule to derive one, so two
engines at the same `MINOR` can disagree about whether an edge dispatching it receives a credential,
and the disagreement is invisible until a policy uses it. The rule has to exist before the operation
does.

### The finding that decided it: 0098 stopped short for a reason that is not true

Decision 0098 removed `context` from hook declarations and derived it from the artifact. Its
`Background.md` says why it did not do the same for edges:

> Edge `context` is untouched: an edge's context participates in matching, a hook's does not, and
> collapsing the two would be a different decision with a different argument.

**An edge's execution context participates in no matching.** Section 5.3's ladder is over the trigger
alone. Section 5.4's determinism key is `(from-context, trigger)`, and that section says what its
"from-context" is: "a transition graph keyed on a workflow-state `from`, Section 6.7". Section 12.1's
reference algorithm is `match_edge(policy, from_context, trigger)`, and it reads `from` and the
trigger ladder and nothing else:

```text
edge = policy.lookup(from_context, key)   # an edge scoped to this from-context
```

Two different things are called a context on the same schema object — the `from` key's
workflow-state from-context, and the execution `context` of Section 3.2 — and that sentence collapsed
them. The capability 0098 believed it was preserving does not exist, and the argument it used to
remove the key from hooks was available for edges at the same time.

**Measurement.** The execution context is written 13 times in `VCSX-SPEC.md`. Exactly one declares an
edge's (Section 6.5) and exactly one consumes it (Section 13.1's matrix row above). The other eleven
are a *hook*'s context, which 0098 already derives. Re-run with:

```sh
grep -c 'host_side\|in_sandbox' VCSX-SPEC.md    # 13
grep -n 'host_side\|in_sandbox' VCSX-SPEC.md
```

An edge's execution context has one consumer in the whole document, and it is the credential
decision.

## Options considered

**Option A — derive the context from the artifact that declared the edge; remove the key.** Chosen;
reasoning below.

**Option B — a `context` field per operation in `conformance/vcsx/vocabulary.json`.** The issue's
first ask, and the strongest of the three it offers. It publishes the answer as data beside
`read_only` and `lifecycle_position`, so a peer engine reads a value instead of re-deriving Section
3.2's criterion, and — the part the issue does not say, and which is the better argument for it — a
*consumer* needs that same derivation to decide which edges it may accept from an untrusted worktree,
which only published data gives it.

It loses on what it answers. It labels the operation, and the question is about the edge: an
operation's context says what the dispatch *needs*, not what this edge *may cause*. Keeping the key
therefore keeps the combination the declared form admits — an edge the working tree supplied,
declaring `host_side`, drawing a credential. That is the same combination 0098 removed for hooks and
0095 had to forbid in prose, reappearing one schema object over. And the forward problem is deferred
rather than closed: an operation added in a `MINOR` carries a context only if the registry ships with
it, and nothing makes it.

**Option C — derive an operation's context from the capabilities it requires.** The issue's second
ask, made forward-safe, and the option that came closest to changing the outcome. Section 9.1 already
does most of the work: "The network-touching capabilities are exactly `ensure_store`, `fetch_base`,
`fetch_counterpart` and `push`... a capability's context is read off this list and never inferred
from its arguments." Section 13.3 already requires an engine to publish the capabilities any
operation it defines beyond Section 4.1 requires, so an operation added in a `MINOR` would classify
itself with no registry change and no new obligation.

It loses on the same point as B — it labels the operation rather than the edge — and it carries a
wrinkle worth recording, because it is a fact about the operation set rather than about the option.
Section 9.1: `status` "reads through `detect_mode`, `current_branch`, `is_dirty`, `is_conflicted` and
`ahead_behind`, with the forge's `pr_state` where one is configured". Every required forge capability
touches the network (Section 11), so a strict capability rule makes `status` host-side wherever a
forge is configured, and in-sandbox otherwise. That is defensible — a `status` that queries the forge
really does reach the network — but it contradicts both Section 3.2's reading and the classification
the reporting implementation published, and it makes one operation's context depend on whether a
forge is configured. The wrinkle is evidence for the decision taken rather than against C alone: it
is what an operation *needs*, and what an operation needs is not what an edge may cause.

**Option D — declare it `Implementation-defined` and add it to Section 13.3.** The issue's third ask,
and it calls it the weakest itself: it makes the divergence visible without removing it. Two engines
would still integrate and fail on the same policy, and a consumer would have to read two Conformance
Statements to predict which. Rejected.

## Decision and reasoning

**The `context` key is removed from `[policy]` edges.** An edge's execution context is fixed by the
artifact that declared it: one declared in `repo.policy.toml` is host-side, one declared in the
consumer's in-sandbox artifact is in-sandbox. The engine still receives a context for every edge,
because it is handed one merged surface and never sees two artifacts (Section 3.2) — the consumer
tags each edge while assembling that surface, which is the same act as sourcing it by trust, and the
same act 0097's `load_policy` already performs for every hook.

Three things follow, and the first is the one that answers the issue.

**The question stops being askable.** "What does an unlabelled edge default to" presumes a field to
omit. There is none, so there is no default to state, none to publish under Section 13.3, and no
divergence for two engines to have. That is a stronger repair than any rule filling the gap, because
a rule can be misread and a missing field cannot be.

**The guarantee stops resting on the author's honesty.** Under the declared form, Section 11's
promise held only for an edge that labelled itself truthfully; an edge from the working tree claiming
`host_side` drew a credential by saying so. Under derivation that is not a rule to enforce but a
thing that cannot be written, because a host-side edge is one the working tree did not declare. This
is 0098's own argument, and this decision is that argument reaching the object 0098 left out.

**The forward problem closes completely.** An operation introduced in a `MINOR` needs no context,
because no context is derived from an operation. What Sections 3.2 and 9.1 say about which operations
touch the remote stays true and keeps its job: it says what an operation *needs*, which is exactly
why an in-sandbox edge dispatching `push` fails at the dispatch rather than succeeding quietly.

**A policy still carrying `context` on an edge has it ignored**, per Section 6.1's "Unknown keys
SHOULD be ignored for forward compatibility" — no new reason, no carve-out, and the same disposition
0098 left the removed hook `context` with. The alternative considered was `malformed_policy`, which
would tell a repository that its label is now inert instead of silently substituting the consumer's
tag; it was rejected because it carves an exception out of the forward-compatibility rule and refuses
documents that were conforming, and because the substituted tag is the safe one in the case that
matters — an edge from the working tree that claimed `host_side` becomes in-sandbox, not the reverse.

### What this gives up

One capability, and it is worth naming precisely because it is close to vacuous. Today one artifact
can declare a host-side edge and an in-sandbox edge side by side. Under derivation an in-sandbox edge
must live in the in-sandbox artifact. The reason this costs little: a `run` edge's hook already
carries its own context (0098), so an edge's label never decided where a hook ran; the six
consumer-effected and flow-control actions receive neither the worktree nor a credential, so it
decides nothing for them; and for `run_op` the only edge it forbids is a trusted-artifact edge that
wants a *credential-free* dispatch of an operation that needs no credential anyway.

**Reconsideration trigger.** Reopen this if a repository needs an edge in the trusted artifact to
dispatch an operation *without* the credentials the engine holds — a trusted policy deliberately
dropping a credential for one dispatch. Under derivation that is inexpressible. The answer then is
probably not to restore `context`, but a per-edge assertion about credentials, because at that point
the two questions have genuinely come apart: where this text came from, and what this dispatch may
hold.

Relates to 0098 (whose derivation this completes, and whose stated reason for stopping short does not
survive Section 12.1), 0095 (whose unit-provenance rule this makes structural one object over), 0097
(whose `load_policy` is where the consumer tags a context), and 0002.
