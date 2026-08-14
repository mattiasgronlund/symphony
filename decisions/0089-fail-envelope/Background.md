# Background — 0089 `fail` gets the envelope `park` has, and `fail(reason)` is the repository's token

## Context

Resolves issue #45. Section 5.2 gives `fail` one sentence — "`fail(reason)` — end the flow as failed" —
and Section 8.2 has nowhere to put that ending unless an `error`-class result is already in hand. The
two rules that close the door are both exhaustive, in opposite directions:

> `op` / `reason` / `class` describe the decisive operation result. Where they are non-null, `class` is
> the class `status` reports — `done` under `ok`, `needs_caller` under `needs_caller`, `error` under
> `error` — because the status of a run that executed the policy is that result's proto class.

> All three are null where the run has no decisive operation result: a clean `ok` with no operation; a
> parked flow, which the policy stopped rather than an operation; and a flow stopped at its bound,
> which the executor stopped.

So `error` **naming a `needs_caller` result** is forbidden by the first, and `error` **with no result**
is not among the three cases the second lists. A `fail` edge is reportable only where the trigger that
reached it already carries an `error` result.

## What the defect does

The report enumerated every Section 5.2 disposition against every Section 4.2 class plus a lifecycle
position — 32 combinations. Three broke, all of them `fail`, and each broke differently:

| edge | what the flow has when `fail` runs | what the implementation did |
|---|---|---|
| `push:rejected → fail` | an `error` result | composed correctly |
| `#needs_caller → fail` | a `needs_caller` result | **panicked** — the envelope constructor holds Section 8.2's "exactly when" as an invariant |
| `before:push → fail` | no result at all (Section 5.1: a position has no outcome) | **panicked** |
| `push:ok → fail` | a `done` result | composed an **`ok`** envelope |

The third is the report on its own. The status had to follow the result's class, the class was `done`,
so a flow the policy had just failed was reported as a clean run: the specification's rules, taken
literally, produce a success envelope for a failure. The remaining 29 compose envelopes that satisfy
every Section 8.2 rule.

The two failing shapes are not exotic. "Never allow a commit in this repository" is `before:commit →
fail`, and "this repository never holds for a human, it fails instead" is `#needs_caller → fail`. Both
are the kind of thing Section 5.3's class rung exists to make writable, and `park` — introduced in the
same sentence of Section 5.2 — composes on every one of them.

## This was predicted, and its precondition was named

Decision 0059 closed `park`'s envelope and recorded `fail`'s as deliberately left open:

> Left open deliberately and recorded: `fail`'s mirror-image envelope — an explicit `do = "fail"` on a
> `done`-class trigger yields `error` with no `error`-class result — which cannot be settled before
> what `fail(reason)`'s argument *is* has an answer.

That is still true, so this decision answers both. `conformance/vcsx/vectors/match-edge.json` already
carries `fail` edges with a `reason` — `{"on": "push:#error", "do": "fail", "reason": "push_failed"}` —
so the argument exists in the corpus as a repository-authored string with no stated home.

## Options

**A — The fourth null case, scoped by the class that already governs the field (chosen).** Section
8.2's null list gains a flow the policy failed. The rule is stated over the class rather than over the
action, which is what keeps the two halves consistent: a `fail` reports the decisive result where the
run has one whose class is `error`, and nulls all three otherwise. `fail` on any other trigger — a
`needs_caller` or `done` result, or a lifecycle position, which has no outcome at all — has no result
whose class agrees, and nulls.

That preserves Section 8.2's invariant exactly as decision 0059 stated it, rather than carving an
exception into it. And it keeps an explicit `#error → fail` edge reporting what the built-in `error`
default reports for the same flow — which is itself a `fail` (Section 5.4). Nulling unconditionally
would make writing the default down explicitly report strictly *less* than leaving it implicit, which
is a difference no repository intends and none can see in the schema.

`fail(reason)`'s argument is a **repository-authored token**, surfaced in `message` as prose and in
`outputs.failed_by_policy` as data, carrying the `trigger` the edge fired on and the `reason` the edge
wrote. It is not reported in `reason`. That field carries an operation reason (Section 4.3), a
configuration reason (Section 6.10) or a precondition reason (Section 8.6), each from a registry a
consumer branches on and an engine MUST document additions to; a repository-invented value there is
indistinguishable from an engine one, and a consumer switching on `reason` would be switching over a
namespace no engine controls.

**Cost, stated rather than hidden:** two shapes for `fail`, and decision 0059 rejected exactly that for
`park` — its option E, "report the parked-at trigger when its class agrees with the status", on the
grounds that a consumer must handle null regardless, so it adds a case without removing one and gives
two parks different shapes. The counter is that `fail` is not `park` on the point the argument turns
on. For `park`, reporting the result would have put a `done`-class reason under a `needs_caller`
status — a violation the null was introduced to avoid. For `fail` on an `error` result, the classes
agree, so reporting it violates nothing and withholding it loses the single most useful field in the
envelope. Option E added a case to *avoid a null a consumer needed anyway*; this adds a case to *keep a
field that is already there*, and the consumer's null handling is unchanged either way.

**B — Relax the class invariant (rejected).** Report the decisive result whatever its class and let
`status` be the policy's: `status: "error"` with `class: "needs_caller"` says exactly what happened,
every row above composes, and the same relaxation would let a park keep the result it currently
discards. This is the option with the most information in the envelope, and it is the one a
from-scratch design might pick, because it separates two things the document conflates in the common
case — what the run did, and what the last operation reported.

It loses on what it costs. Decision 0059 called the invariant "worth more than the case that motivated
it — it is what a reviewer checks the next time a terminal action is added", and this decision is
exactly that next time. Every consumer reading `class` as the class of the status breaks, and Section
8.5 makes the envelope major-stable, so it is a `MAJOR` change to fix a case a `MINOR`-compatible
clause covers. Relaxing an invariant to admit a case the invariant already accommodates by nulling is
paying the general price for the specific problem.

**C — Refuse the edge at validation (rejected).** Section 6.10 refuses a `fail` edge whose trigger
cannot carry an `error` result, judgeable from the document alone because the trigger fixes the answer.
It is what the filing implementation does meanwhile, and it names itself a meanwhile rather than a
proposal — chosen there because what those policies got instead was a crash for two shapes and a wrong
status for the third. As a normative answer it is an engine refusing policies another engine may run,
and it removes meaning rather than adding a report: `before:commit → fail` stops being expressible, and
the workaround is `park`, which reports `needs_caller` for something the repository said was a failure.

## Verification

- The three broken shapes and the 29 that compose were taken from the report's enumeration and
  re-derived against Section 8.2's two rules at `e00ebb1`: the non-null rule forbids a class that
  disagrees with the status, and the null list enumerates three cases, none of which is a failed flow.
- The claim that `fail` edges already carry a `reason` in the corpus was checked against
  `conformance/vcsx/vectors/match-edge.json` at `e00ebb1`: `op_class_beats_bare_class` and
  `class_edge_of_other_class_does_not_catch` both carry `{"do": "fail", "reason": "push_failed"}`, and
  `unmatched_signal_is_benign_noop` carries a `fail` edge with a `policy_*` reason. The vocabulary's
  `actions` group records `{"token": "fail", "effected_by": "engine", "args": ["reason"]}`.
- The claim that the built-in `error` default is itself `fail` was checked against Section 5.4, which
  is what makes the explicit-versus-implicit comparison in option A a real one.
- `failed_by_policy` appears nowhere in `VCSX-SPEC.md`, `VCSX-CONTRACT.md` or
  `conformance/vcsx/vocabulary.json` at `e00ebb1`.

## Reconsideration trigger

Reopen if a second field is proposed for `reason`'s namespace — anything that would have a
repository-authored token appear where a registry token appears. The argument for keeping
`fail(reason)` out of `reason` is that the field's namespace is engine-owned; a change that gives up
that property makes the `outputs` key redundant rather than protective.

Reopen the two-shapes decision if a consumer is found branching on `op` being non-null as a proxy for
"an operation was decisive". Under A that proxy holds for `fail` and, if a later terminal action takes
the same treatment, the set of shapes grows. The check is whether a reader can still state the
non-null rule in one sentence.

## Relates to

0059 (which left this open and named its precondition, and whose invariant and whose rejected option E
this decision is argued against), 0088 (the neighbouring question about a flow no operation ended,
settled in the same change), 0060 (the flow bound's null envelope, the third member of the null list).
