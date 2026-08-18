# Background — 0129 A matching axis the contract cannot transmit

## Context

Issue #77. `VCSX-SPEC.md` Section 5.4 keys the policy graph on `(from-context, trigger)`, Section 6.5
lets an edge carry an OPTIONAL `from` to scope it, Section 12.1's `match_edge` takes the from-context
as a parameter, Section 6.11 refuses a `duplicate_edge` on the composite key and judges
`position_cycle` over every context, and Sections 13.1 and 13.2 require the scoping be tested and
implemented.

Section 8.1 enumerates the invocation surface twice — the argument list and the consumer-configuration
keys — and neither carries a workflow state or anything an engine could derive one from. The
`execution context` in that list is Section 3.2's host-side / in-sandbox pair, a different axis.

Section 5.4's own unscoped-edge bullet says a front-end supplies one: "This is what keeps the same
`repo.policy.toml` yielding one operation flow under **a front-end that supplies a from-context** and
one that does not". Nothing does.

## What the defect does

Nothing in the text is strictly false. Section 5.4's *"where the engine models them … absent such a
model the key is the trigger alone"* is a real hedge, in the shape Section 9.3 uses for "where
determinable", and an engine that models no from-context is conforming: every key is the trigger
alone, a scoped edge is never selected, an unscoped one always is.

That is the defect. Two conforming engines given one `repo.policy.toml` produce different operation
flows — one where a `from`-scoped edge fires and one where it is dead text — and a repository author
cannot tell which they have, because the difference is a capability the contract never made
declarable. It is the property Section 5.4's unscoped-edge bullet claims to guarantee, stated over a
value the specification does not transmit.

The failure is quiet in the direction that matters. An author writes a `from`-scoped edge, the engine
validates it, `duplicate_edge` counts it against the determinism rule, and on an engine that models no
context it never fires. The policy reports success and routes differently than written.

## The one model Section 5.4 named is no longer the engine's

Section 5.4's parenthetical points at Section 6.7 — "a transition graph keyed on a workflow-state
`from`" — as its example of the engine modelling a from-context, and Section 6.5 still says `from` is
"used only by transition edges, Section 6.7". Checked against Section 6.7 as it reads today, after
decision 0122:

> This table is read by the **consumer**, not matched by the executor […] the condition `on` names is
> one the consumer observes in its own run […] What the engine matches is Section 5.1's two kinds,
> both of which it produces itself.

So the sole named model is a table the executor does not match, and Section 6.5's cross-reference
points a reader at it. This is current fact about the document rather than an inference from 0122's
ruling, which matters for the argument below: the load-bearing claim is what Section 6.7 *says now*,
not that a previous decision said to remove things.

## The measurement

Every `from`-carrying policy edge in the conformance corpus, `grep -n '"from"'
conformance/vcsx/vectors/*.json` at `abe3777`, discarding the `tracker.transitions` rows (which carry
`to`, not `do`):

```text
match-edge.json:228  { "from": "In Progress",  "on": "push:ok",           "do": "set_state", "target": "Human Review" }
match-edge.json:229  { "from": "Human Review", "on": "push:ok",           "do": "set_state", "target": "Done" }
match-edge.json:241  { "from": "In Progress",  "on": "push:ok",           "do": "set_state", "target": "Human Review" }
match-edge.json:266  { "from": "Human Review", "on": "push:ok",           "do": "set_state", "target": "Done" }
match-edge.json:279  { "from": "In Progress",  "on": "push:#needs_caller","do": "set_state", "target": "Blocked" }
policy-validation.json:96  { "from": "In Progress",  "on": "push:ok", "do": "set_state", "target": "Human Review" }
policy-validation.json:97  { "from": "Human Review", "on": "push:ok", "do": "set_state", "target": "Done" }
```

Seven edges across two files, and **every one uses `do: "set_state"`** — the consumer-effected action
whose own matching table `tracker.transitions` decision 0122 handed to the consumer, still keyed
`(from, on)` and still validated for determinism. `SPEC.md`, the one real consumer, writes no
`from`-scoped policy edge at all.

So the capability actually at stake is *scoping a non-`set_state` action by workflow state*, which
nothing in this repository does and no reported requirement asks for. Every demonstrated use of the
axis is a use the consumer already performs for itself, on a table that kept its own `from` key.

That measurement is what moves this from "either reading could be argued" to a recommendation. It does
not settle it on its own: absence of a user in a specification with no implementation is weak
evidence, and the axis was last examined because a real engine hit it (decision 0067, below).

## Decision

Remove the from-context from the engine's matching. The executor matches on the trigger alone; the
determinism key is the trigger; `from` leaves Section 6.5's prose and its TOML example; `match_edge`
drops the parameter. A policy that still carries a `from` on an edge is **ignored rather than
refused**, under Section 6.1's unknown-key rule — the precedent decision 0100 set when it removed an
edge's `context` key, so a policy written against the earlier version still loads. Two edges differing
only by `from` then collide as a plain `duplicate_edge`, which is the honest report.

Confirmed with the user through decision sheet `vcsx-from-context`, version `13ce1d6b`: direction
**B** (remove), stale key **ignored** under Section 6.1, decision 0067 marked **Superseded**, and the
corpus swept against Section 8.1 in the same branch (decision 0130).

## Options considered

**A — Carry it: add a from-context argument to Section 8.1.** This is the option with the best claim,
and it is the move decision 0121 made two decisions earlier for exactly this shape of gap: validation
took two inputs the contract did not carry, and 0121 gave them argument names (`effectable_actions`,
`bound_units`) rather than removing the checks. Taken here it makes every clause above true as
written, leaves 0067 standing unmodified, gives the corpus's `from_context` field a contract behind
it, and preserves a capability the specification currently promises. It is also the option that keeps
faith with an author who has already written a scoped edge.

It loses on two things. First, the argument's *shape*: the engine would take a value whose vocabulary
it declares outside its own domain — a tracker's workflow states — so the argument has to be an opaque
scope token compared only for equality. That is coherent, and the engine already holds several values
opaque, but each of those is a value the engine *hands to a plugin*; this one it would **match on**,
which is the thing the engine does in its own terms. Second, and decisively, it re-opens at the
argument level a question that is settled at the table level: the party that effects the action owns
the matching. Every scoped edge in evidence effects `set_state`, and `set_state`'s matching table is
the consumer's, keyed `(from, on)` by the consumer, for the consumer to walk. Carrying the axis into
the engine would give the engine a second, parallel scoping mechanism for the one action whose
scoping the consumer already performs — bought for a capability with no demonstrated user.

**C — Neuter it: state that the engine models no from-context and let `from` be an ignored key.** The
smallest edit, and it keeps every existing policy loading unchanged. It loses because it leaves
Section 5.4's determinism key describing a composite whose first component never has two values, and
it keeps a policy surface an author can write that will never fire. That is the precise shape decision
0122 removed a trigger kind over, and the reason for preferring removal is the same: a surface that
validates and never fires reports success. The half of C worth keeping is kept — the ignored-key rule
is how the stale `from` is disposed of.

## Why this is not decision 0122 cited as precedent

0122's *principle* — the party that effects the action owns the matching — is load-bearing in the
argument against A, and it is stated there as a principle to be re-derived rather than as an
authority. The argument itself stands on two things a later reader can check without accepting 0122:

- Section 6.7 is consumer-read **as a matter of the document's current text**, quoted above. Whatever
  put it there, that is what it says, and it is what makes Section 6.5's `from` cross-reference point
  at a table the executor does not match.
- The corpus measurement: seven scoped edges, all `set_state`, and no scoped edge in `SPEC.md`.

A decision justified by "a previous decision said to" preserves no reasoning that survives the
precedent being revisited. If 0122 were reopened tomorrow, the measurement above would still hold and
would still have to be answered.

## Reconsideration trigger

A repository — or the `vcsx-policy` engine — wanting a **non-`set_state`** action scoped by workflow
state. That is the requirement whose arrival reopens this: an `#error` catch-all that should escalate
in one workflow state and park in another, or a `run_op` that should route differently depending on
where the ticket sits. Nothing in evidence asks for it today, and the seven measured edges are
uniformly the case the consumer already handles. Should that requirement arrive, option A is the
answer, and the work it needs is the argument's shape — an opaque equality-compared scope token in
Section 8.1, with the ordering rule 0067 worked out reinstated.

## Relationship to decision 0067

0067 ("An edge with no `from` is unscoped") is superseded by this decision, and it is worth saying why
it was sound rather than merely retiring it. It answered a real question, raised by a real engine
implementation (`vcsx-policy`, issue #13) that had to pick a reading to compile: Section 5.4's "absent
such a model the key is the trigger alone" settled the two all-or-nothing configurations and not the
**mixed** one. Its ruling — an unscoped edge is a candidate in every context, a scoped edge outranks
an unscoped one for the same key, and the ladder selects the key first — was the right answer to the
question as posed, and the failure mode it avoided was real: under the rejected reading, adding the
first transition edge silently disables the routing that made a policy work.

What makes it moot is that its motivating scenario was "a repository running a transition graph", and
that is the scenario 0122 moved out of the executor. With the transition graph consumer-read, the
mixed configuration 0067 exists to adjudicate cannot arise in the executor at all. Its reasoning stays
readable and its analysis of the ordering — that the from-context sits *inside* the ladder rather than
around it — is the part option A would need again. Its ruling stops applying.

Decision 0033 is the precedent for the state.

## Review finding: 0122's own template row was missed

The plan for this decision required confirming, rather than assuming, that
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` needs no row — `CLAUDE.md` records that three decisions in a
row missed the template before decision 0128 caught it. Confirmed: Section 13.3 carries no
from-context obligation and the template's Section 3 needs no row, this decision adding no
`Implementation-defined` answer and removing none.

The check found something else. The template's Section 2 mirror of Section 13.2's action-policy-machine
item still reads:

> The action-policy machine: triggers, actions, the `#class` fallback, fail-safe on an unmatched
> outcome, **no-op on an unmatched signal**, determinism (Section 5)

Decision 0122 removed the signal trigger kind and updated Section 13.2's own bullet to
"no-op-on-unmatched-position", but not the template's copy of it. So an engine filling in a Statement
today declares conformance to a behavior for a trigger kind that no longer exists.

This is the fourth instance of the pattern 0128 named, and the first since 0128 extended `CLAUDE.md`'s
cross-cutting rule to cover the templates — which is the useful part of the finding, because 0128's
repair addressed obligations landing in Section 13.3 and this miss is in Section 2, a *checklist*
mirror rather than an obligations table. The rule caught it here only because this decision edits the
same Section 13.2 bullet. It is repaired in this branch rather than filed, being one line in a
document this decision already has to touch, and it is recorded here rather than fixed quietly because
the recurrence is what the count is for.
