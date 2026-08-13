# Background — 0082 `[messages.squash] strategy` defaults to `merge`

## Context

Resolves issue #36, which is two reports whose answers meet.

**1. Section 8.6 defines the determinable half of `capability_unsupported` out of existence.**
Section 9.3 splits an undeclared capability at "determinable before the policy runs". Implementing
that split means enumerating the descriptor fields Sections 9.1 and 9.2 fix against the keys of
`repo.policy.toml`, and the enumeration has **exactly one row**: `[messages.squash] strategy`
against a forge's declared merge strategies, which is Section 9.3's own worked example. Section 8.6
then says

> A configuration error is a property of `repo.policy.toml` alone, detectable before any argument or
> checkout is in hand

which cannot be exactly true, because `capability_unsupported` is a row of Section 6.10's table and
is determined against the selected backend's descriptor. Two operative sentences of the same two
sections draw the line elsewhere — Section 8.6's own "refused before the policy runs where **the
invocation** determines it", and Section 9.3's "before the policy runs" — so one section says the
thing twice and differently. An engine that takes the "policy alone" sentence literally determines
nothing, satisfies "where determinable" vacuously, publishes that under Section 13.3, and fails the
only example Section 9.3 gives. The divergence is observable: one `repo.policy.toml` carrying
`strategy = "rebase"` against a forge declaring `merge` and `squash` is exit `2` before anything
runs on one engine and `merge:unsupported` at exit `20` on the day someone lands on the other. Both
cite Section 9.3.

**2. Section 6.8 states no default for `strategy`, and the default decides what a `land` writes.**
Three tokens, an example value, and no statement of what an absent key means. Section 13.3's
enumeration of the `Implementation-defined` behaviours a Statement MUST resolve carries "the
backend's default remote where `[engine] remote` is unset" and carries nothing for Section 6.8,
which is the evidence this is an omission rather than a silent delegation. Decision 0062 gave the
remote that treatment for a reason that applies here without change.

The second question decides the first: if the default is fixed, or is required to be published, the
engine holds it, so an **absent** key is determinable too.

## A correction to the report's own argument, and to this decision's first draft

The obvious argument for `merge` is that Section 11 says so:

> A `rebase` or `squash` merge strategy (Section 6.8) is not an exception: it writes to the base
> branch.

**That sentence does not say what it looks like it says.** It is scoping the *work-branch*
guarantee, not ranking the strategies. Its point is that the no-rewrite promise covers the work
branch and that a merge strategy touches a different branch, so a rebase or squash merge is not a
counter-example to the promise. Read as written it gives no argument that `merge` is the safer
default — all three write to the base branch. An implementer who reads Section 11 after reading a
decision that cited it this way finds it says the reverse.

**The real asymmetry is one step further in.** Of the three strategies, `merge` is the only one
under which the commits the engine wrote — each of them gated at `before:commit`, each attributed to
the caller-supplied identity (Section 10.1) — survive into durable history as they were written.
`rebase` re-parents them; `squash` collapses them into a commit the code host authors. Defaulting to
the strategy that preserves what the engine gated is consistent with the posture the document states
everywhere it states one: no operation that updates the work branch rewrites, drops or re-parents a
commit already on it, and an update that reconciles a divergence merges (Sections 4.1, 11).

That is an argument from the document's temperament rather than from a sentence in it, and it is
recorded as such. The specification will state the default and let Section 6.8's own field pattern
carry it, without citing Section 11 for a claim Section 11 does not make.

## Options considered

- **A — fix the default at `merge`; the check stays a configuration error (chosen).** Section 6.8
  gains `Default: merge`; Section 8.6's explanatory sentence is repaired so `capability_unsupported`
  is inside the definition rather than a counterexample to it; Section 9.3 keeps both halves.
- **B — publish the default; move the check to Section 8.6.** The default becomes
  `Implementation-defined` and MUST be documented, with a Section 13.3 row, exactly as decision 0062
  did for `[engine] remote`; `capability_unsupported` moves to the precondition registry where the
  invocation is in hand, and becomes entry-scoped as decision 0074 scoped the identity precondition
  — so a `ship` that never merges is not refused for a merge-strategy contradiction.

The entry-scoping is genuinely attractive, and refusing a `ship` over a strategy only `land` uses is
real over-refusal. It is rejected on two grounds. First, decision 0074's scoping was right because
an identity is a **per-invocation input the caller supplies**; a merge strategy is a property of the
repository's way of working. Section 6.10 judges the document and Section 8.6 judges the invocation,
and B moves a document error into the invocation registry, blurring the distinction decision 0056
leaned on when it created the configuration registry at all. Second, B's cost is the one least worth
shipping: with the default `Implementation-defined`, two conforming engines write different durable
base-branch history from the same `repo.policy.toml`. Publishing that under Section 13.3 makes it
discoverable, not interoperable. Section 11 is explicit that the strategy writes to the base branch,
which is precisely why leaving the default unstated is worse than the over-refusal B fixes.
- **C — an absent key means the code host's own default.** Rejected twice over. It makes durable
  history depend on forge settings outside the repository's file, inverting Section 6.8's premise
  that merge policy is repository-owned Way of Working. And `request_merge(pr, strategy,
  expected_head)` gains an "unspecified" strategy — a capability argument that cannot say what it
  means, which is the same shape Section 9's answer-domain rule forbids one layer down (decision
  0076), reintroduced at a different seam.

## Decision and reasoning

**A**, with the premise corrected.

**Section 8.6's sentence, repaired rather than reversed.** A configuration error is judged from the
policy document together with what the engine holds independently of the invocation — the
descriptors its configured backends advertise (Section 9.3) and its own defaults; a precondition
failure needs the invocation's arguments and the checkout the engine was pointed at. Both operative
sentences already say "the invocation" and "before the policy runs", so this is the explanatory
sentence catching up with the rules around it rather than a change of rule. The repair also names
what stays on the other side: a descriptor field a backend can only answer once it has opened the
checkout is not something the engine holds independently of the invocation, so a policy requiring it
keeps Section 9.3's first-use disposition.

**The cost this decision concedes, and the overclaim it must not license.** Under A an absent
`strategy` becomes determinable — it means `merge`, and the descriptor either declares it or does
not — so among the **required** policy keys, Section 9.3's first-use half loses its only producer.
That undoes an asymmetry at least one implementation deliberately preserved (a written-out key can
be refused, an absent one cannot) specifically so `merge:unsupported` kept a real test rather than
becoming an argument. The asymmetry was always uncomfortable — it is odd that spelling out the
default changes whether you are refused — and it goes.

What follows is a documentation obligation rather than a shrug. Section 13.1 must not merely record
that the first-use half has no producer among the required keys today; it must say what a
Conformance Statement may claim. An implementation cannot demonstrate that half from the required
set at all, so a Statement claiming it names the engine-added operation or optional capability it
demonstrated it against. Without that, the result is the overclaim shape: a mechanism described by
one true sentence and read as a general guarantee.

**Cost, priced.** Fixing a default is a behaviour change for any engine that chose otherwise, inside
a `MAJOR`. `merge` is itself not guaranteed by a descriptor — Section 9.2 declares "the merge
strategies supported" — so a forge that cannot perform a plain merge now fails on a default nobody
wrote; the repaired check catches exactly that at validation rather than on the day someone lands,
which is the disposition Section 9.3 asks for.

## Review findings applied (PR #40)

One wording correction, no change of rule. `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` said a backend
that does not declare `merge` "refuses a policy" — the backend declares its strategies and the
**engine** refuses the policy at validation, which is the whole point of putting the check on the
configuration side rather than at first use. Restated so the actor is the engine.

Recorded here rather than fixed silently because the slip inverts this decision's own division of
labour, and the Statement is where a reader checks it.

Related, and logged in decision 0084 where the sentence lives: Section 6.10's enumeration of what
validation is judged from — the repair this decision's Section 8.6 rewrite leans on — was itself
stated as a closed list that omitted `version_floor_unmet`'s input. That is this decision's own
diagnosis recurring one section over, and it is corrected there.

## Reconsideration trigger

Reconsider if a required policy key is added whose contradiction with a descriptor is genuinely not
determinable before the policy runs, which would restore a producer for Section 9.3's first-use half
among the required set and make the Section 13.1 claim-scoping sentence unnecessary. Reconsider
separately if the wholesale refusal proves to cost operators working invocations — a `status`
refused for a merge strategy it would never reach — which is B's entry-scoping argument arriving as
evidence rather than as preference.

Relates to 0062 (whose treatment of `[engine] remote` is the shape declined here and taken for the
repair), 0074 (whose entry scoping option B would have extended), 0076 (whose answer-domain rule
option C would breach), 0056 (which created the configuration-reason registry) and 0070 (which put
the Section 13 resolutions in the Statement).
