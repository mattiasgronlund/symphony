# Background — 0088 An outcome no action disposed of takes the default, and the registry carries each need

## Context

Resolves issue #44. Section 5.4 fixes what an **unmatched** operation outcome does and says why:

> An unmatched **operation outcome** MUST be fail-safe: the executor parks or fails the flow with the
> operation's proto reason surfaced. It MUST NOT be silently dropped, because a dropped operation
> outcome would strand a flow.

Section 5.6 names what ends a flow — `escalate`, `park` and `fail` — and Section 5.2 makes the
consumer-effected actions emit once. Between them sits a third case neither covers: a result that
**matched** an edge whose action neither ends the flow nor re-enters the machine.

```toml
[[policy.edge]]
on = "push:non_fast_forward"
do = "notify"
channel = "releases"
```

Under a front-end sequence the next step is reached or the class stops it. Under Section 8.1's
single-operation entry points — `vcsx push`, or an embedded driver's `run_op` (Section 7.3) — there is
no sequence: the intent is emitted, the traversal has nowhere to go, and the invocation ends having
neither escalated, parked nor failed.

## What the defect does

Section 8.2 then requires three things that do not compose. The decisive result is
`push:non_fast_forward`, whose class is `needs_caller`, so the status is `needs_caller`, so an
escalation is REQUIRED — and no `escalate` ran, so nothing named a `need`, which Section 8.4's payload
requires. The filing implementation's envelope constructor holds Section 8.2's "exactly when" as an
invariant and **panicked**: fail-closed rather than wrong, and evidence of the shape. An
implementation that takes Section 8.2's invariants literally cannot represent this run, and the
specification asks for it. The `error` class has the same shape at a lower cost: `push:rejected →
notify` ends a run whose decisive result is an error and whose status nothing states.

Unlike the reports filed beside it, this question predates PR #40; nothing decision 0081 added created
it. It surfaced there because routing a gate's answer through the ordinary result path is what first
drove an actionable result into an edge that continues.

## The half that reaches further than the report

Section 5.4's built-in default for `needs_caller` is `escalate`, and Section 8.4 says an escalation
carries a `need`. **Nothing in the document says which need the default names for which reason.** That
is already true for the unmatched case Section 5.4 fixes; #44 only makes it reachable from a policy
edge as well as from silence.

Counted against the pinned registry at `e00ebb1`, and against the filing implementation:

| | |
|---|---|
| `needs_caller` results in Section 4.3 | 17 — 13 reason-specific rows, plus the universal `blocked` at each of the four gated operations |
| needs the document fixes | 2 — `push:non_fast_forward → integrate_then_retry` and `integrate:merge_conflicts → resolve_conflicts`, both written into Section 12.2's routing |
| the implementation invented | 6 — `await_checks` by the plain meaning of the token, `supply_identity` ×3 from decision 0074's reasoning, `resolve_conflicts` ×2 by analogy |
| the implementation defaulted to `human_review` | 9 |

So an engine derives 15 of 17 need tokens with no guidance, and Section 5.5 has a front-end **bind its
resolvers by exactly those tokens**. Two engines therefore offer one driver two different resolver keys
for the same condition — which is the failure the `need` vocabulary being "part of the public contract"
(Section 8.4) is supposed to exclude, arrived at through the one door the document left open.

## Where the mapping goes, and why not Section 8.4

On Section 4.3's registry, as a `Default need` column. The registry is already keyed by `(operation,
reason)` and is already generated from — `conformance/vcsx/vocabulary.json` carries it as data
(decisions 0051, 0071) — so a column becomes a field on a generated record in every implementation that
generates from it, and an upstream rename becomes a compile error rather than a silent divergence. That
is the same property the condition tokens buy in decision 0086, and it is the difference between a
normative mapping and a normative suggestion. A table in Section 8.4 would be a second key over the
same pair, maintained by hand against the registry it duplicates. Section 8.4 stays the `need`
vocabulary — what the tokens are and which are holds — and the registry says which reason defaults to
which.

## The two rows with no good answer, and the token they get

`commit:worktree_moved` and `merge:head_moved` fall to `human_review` under any mapping built from the
existing vocabulary, and `human_review` is wrong for them in a way the others are not. The state moved
between the read and the write; the repair is to read it again and retry, not to fetch a person. Both
reach the default only through a bare `commit` or `merge` entry point, because the front-end sequences
route them internally — which is exactly why Section 12.3 says `merge:head_moved` "adds a reason token
and no `need` token", a sentence that stops being true the moment a driver calls `merge` directly
(Section 7.3).

They take a new need, `reread_then_retry`, spelled to match `integrate_then_retry` and glossed with the
recovery the registry already states for both reasons — "re-read then retry". It is meetable, and it is
meetable **because of decision 0087**: a resume re-enters the point that raised the need and the
position re-reads, so a driver meets this need by resuming and nothing else. Minted here rather than
deferred because a need no front-end can meet is a hold (Section 8.4), and this one would have been
filed as a hold purely for want of the resume semantics landing in the same change.

## Options

**A — Extend the fail-safe rule to any outcome no action disposed of, and put the default's need on the
registry (chosen).** An outcome is disposed of by an action that ends the flow or by a `run_op` whose
own result takes its place; the remaining actions emit an intent or run a hook and return, leaving the
traversal where an unmatched outcome leaves it, so they reach the same built-in default. In effect: a
matched edge that does not end the flow leaves the result to be disposed of as though nothing had
matched, because nothing did anything with it that ends a flow.

**B — Report it as a hold: null the operation fields and end at `intervention` (rejected).** Reuses
`park`'s machinery exactly, needs no mapping and no new token, and Section 8.2's null list already has
a case shaped like it. It loses on both halves of what it claims. It drops the decisive result, which
is the thing Section 5.4 forbids in the neighbouring case for a reason — a dropped outcome strands a
flow — that does not stop at whether an edge happened to match. And decision 0059's argument for
nulling a park's fields is that no operation asked the caller for anything; here one did. The envelope
would tell the caller the policy asked for a hold when the policy asked for a notification.

**C — Refuse the policy at validation (rejected).** A Section 6.10 rule: an edge on an actionable-class
trigger whose action neither ends the flow nor dispatches an operation is a configuration error. It is
statically judgeable — a `notify` edge has no successor at all — so it is a real option rather than a
wish, and this repository has accepted static refusal before where the refused policies were
unrepresentable or nonsense. These are neither. `push:rejected → notify` means something a repository
would want: notify the channel, then report the failure. And the obvious rewrite is not writable —
Section 5.4 allows at most one edge per `(from-context, trigger)`, so "notify, then fail" cannot be
expressed as two edges. C therefore removes a policy rather than repairing its report.

## A hole the repair exposes

Section 6.5's own example is `on = "#error"`, `do = "escalate"` with no `reason`, and
`conformance/vcsx/vectors/match-edge.json` carries the same shape. Once the default's need comes from
the registry, an explicit `escalate` that names no `reason` needs an answer too, and the registry's
column is scoped to `needs_caller`. It takes one sentence rather than a column over every row: such an
edge raises the trigger's default need where the trigger is a `needs_caller` result, and `human_review`
otherwise — an `error` or a `done` result a policy chose to escalate names no remedy of its own, and a
lifecycle position has no outcome to take one from. Recorded here rather than fixed quietly because it
is a hole this decision's own repair made visible, and a later reader tracing why Section 5.2 carries
that sentence should find it attributed.

## Verification

- The 17 was recounted against Section 4.3's table at `e00ebb1`: 13 rows carry class `needs_caller`
  (`commit:worktree_moved`, `commit:identity_missing`, `integrate:merge_conflicts`,
  `integrate:identity_missing`, `push:non_fast_forward`, `push:pr_closed`, `create_pr:conflict`,
  `merge:not_open`, `merge:checks_pending`, `merge:conflict`, `merge:head_moved`, `pull:conflict`,
  `pull:identity_missing`), and the universal `blocked` row is one row over four gated operations —
  `commit`, `push`, `create_pr`, `merge` — since Section 4.3 states `integrate`, `pull`, `status` and
  `diff` carry no `blocked`.
- The claim that only two needs are fixed by the document was checked by searching for each `need`
  token: `integrate_then_retry` and `resolve_conflicts` appear in Section 12.2's `ship` pseudocode;
  `supply_identity`, `await_checks` and `human_review` appear only in Section 8.4's enumeration of the
  vocabulary, which names them without binding any to a reason. `human_review` also appears in Section
  12.2 bound to `push:pr_closed`, which is a third fixed mapping in the routing rather than in the
  registry — recorded here because it makes the "2" a count of mappings the *registry* would have
  needed, not of every mapping written anywhere.
- The claim that an `escalate` edge with no `reason` is real rather than hypothetical was checked
  against `VCSX-SPEC.md` Section 6.5's example block and against the `bare_class_catches_otherwise_
  unmatched` and `op_class_beats_bare_class` vectors in
  `conformance/vcsx/vectors/match-edge.json`, which carry `{"on": "#error", "do": "escalate"}`.
- `reread_then_retry` appears nowhere in `VCSX-SPEC.md`, `VCSX-CONTRACT.md` or
  `conformance/vcsx/vocabulary.json` at `e00ebb1`.

## Reconsideration trigger

Reopen the column's *placement* if the registry gains a second per-reason policy field — a retry
disposition, a default `set_state` target — at which point the registry is carrying policy rather than
identity, and a separate mapping table stops being a duplicate key and starts being a separation of
concerns.

Reopen the mapping itself for any row where a front-end's built-in routing starts contradicting the
registry's default: the two must agree, and Section 12.2 fixing a different need for a reason the
registry maps elsewhere is the evidence that one of them is wrong.

## Relates to

0087 (which makes `reread_then_retry` meetable, and without which it would be a hold), 0059 (the
envelope invariants this decision is stated against, and whose `park` reasoning it declines to reuse),
0051 and 0071 (the registry as data, which is the argument for the column's placement), 0074 (whose
reasoning the filing implementation used to derive `supply_identity`), 0077 and 0079 (the moved-state
reasons whose need this decision mints).
