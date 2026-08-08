# Background — 0057 Universal operation reasons: `blocked`, `failed`, `unsupported`

## Context

Issue #2 against the specification repository raised three conditions `VCSX-SPEC.md` requires an answer
for while supplying no token to answer with. Two of them are one defect seen twice, and this decision
takes both; the third is decision 0058.

The defect: **Section 4.3's registry is enumerated per operation, while Sections 6.6 and 9.3 state
rules quantified over operations.** An enumeration that was written operation by operation cannot
satisfy a rule written "for every operation", and it does not.

Section 6.6 says a `before:*` hook "MAY block by returning a `needs_caller` or `error` result with a
stable reason; the engine surfaces it as the operation's `blocked`/`failed` reason". That presupposes a
`blocked`/`failed` pair at each of the four required lifecycle positions. Only `commit` had one:

| Gated operation | `needs_caller` block | `error` block |
|---|---|---|
| `commit` | `commit:blocked` | `commit:failed` |
| `push` | — | `push:rejected`, which means *the remote* rejected |
| `create_pr` | — | — |
| `merge` | — | `merge:blocked`, at class `error` |

So a repository that gates `create_pr` could express the block at neither class, and Section 10.4
specifically scans a title with `title_scan` and a body with `body_scan` *during* `create_pr`, blocking
"with a stable reason" that did not exist. A repository gating `push` had to borrow `push:rejected` and
report the remote as the cause of its own gate's refusal.

`merge:blocked` was worse than missing. It carried the gate word at class `error` while `commit:blocked`
carried it at `needs_caller` — the same reason spelled identically at two classes, in a design where
policy branches on class through the `#class` fallback (Section 5.3). One `#needs_caller → escalate`
edge escalated a blocked commit and failed a blocked merge, and an implementer reading the registry
could not tell that from a decision.

Section 9.3 has the same shape of problem: an undeclared capability "yields an `error`-class result
rather than a silent no-op", surfaced "at validation (Section 6.10) where determinable, otherwise at
first use". Neither Section 4.3 nor Section 6.10's table named a token for either half. For three
operations the requirement was not merely awkward but unsatisfiable: `status`, `diff` and `pull` had **no
`error`-class reason at all**, so a conforming engine could not return an `error`-class result for them
without adding a token — and Section 8.5 makes a reason token part of the major-stable public surface,
so adding one is exactly what a second engine would spell differently.

The general form is worth naming, because it is what makes this a specification defect rather than an
omission of three tokens: Section 4.1 lets an engine define additional operations and their
`before:<op>` positions, so **the set of operations is open while the registry was closed**. Any rule
stated over all operations was going to outrun an enumeration.

## Options considered

### Making the rules satisfiable

- **Option A — universal reasons defined for every operation (chosen).** `failed` (`error`) and
  `unsupported` (`error`) for every operation, `blocked` (`needs_caller`) for every gated one, stated
  once rather than repeated per operation. Trade-offs: makes Sections 6.6 and 9.3 total by construction,
  including for an operation an engine adds later, which is the property an enumeration cannot have.
  Costs a redefinition of `merge:blocked` (below) and grows the registry from 27 entries to 45 once
  normalized per operation.
- **Option B — add the missing tokens one at a time**, as the issue proposed: `push:blocked`,
  `create_pr:blocked`, `create_pr:failed`. Trade-offs: the smallest edit, and it closes today's gap. But
  it leaves the registry closed against an open operation set, so an engine adding an operation is in
  the same position tomorrow; it leaves `status`, `diff` and `pull` with no `error` reason, since the
  issue's list does not reach them; and it does not resolve the `merge:blocked` class collision, which
  is the part an implementer cannot infer.
- **Option C — a separate gate-reason namespace**, `<op>:gate_blocked` / `<op>:gate_failed`.
  Trade-offs: leaves `merge:blocked` untouched and makes a gate block self-describing at the token
  level. But it contradicts Section 6.6's own wording, which names the pair `blocked`/`failed`, and it
  forces a rename of `commit:blocked` — already the gate reason — for uniformity. It trades one rename
  for another and adds a second vocabulary for one concept.

### The `merge:blocked` collision

- **Option D — the gate meaning wins; the forge refusal is renamed `merge:rejected` (chosen).**
  `blocked` becomes uniformly the gate reason at `needs_caller`, and the branch-protection/forge-policy
  refusal keeps class `error` under a name parallel to `push:rejected`. Trade-offs: an anchor change and
  a class change on a listed reason, which Section 8.5 forbids within a `MAJOR`. It is affordable now
  and not later: decision 0049's engine is not written, so there is no implementation to migrate — the
  same reasoning decision 0056 used for the `usage_or_config` status.
- **Option E — the forge meaning keeps `merge:blocked` at `error`, and merge alone has no
  `needs_caller` gate reason.** Trade-offs: no rename. But a `before:merge` gate returning
  `needs_caller` would then have to surface at `error`, which contradicts Section 6.6's class-preserving
  surfacing and loses the caller-fixable distinction precisely where a repository is most likely to gate
  (a squash transform rejecting a body). The rule would be defined at three positions out of four.
- **Option F — keep both meanings on `merge:blocked` and let the class vary with the origin.**
  Trade-offs: no new token. But a reason whose class depends on how it arose destroys the `#class`
  fallback for that reason, which is the one property Section 8.5 freezes for a whole `MAJOR`.

## Decision and reasoning

Choose **Option A** and **Option D**.

Three reasons are defined for every operation, stated once at the head of Section 4.3's registry rather
than repeated per operation:

- `failed` (`error`) — the operation failed, including when a `before:<op>` hook blocked it with an
  `error` result.
- `blocked` (`needs_caller`) — a `before:<op>` gate or scan blocked the operation. Defined for gated
  operations only; `integrate` and `pull` are gated at no fixed position and the read-only operations
  carry no lifecycle position at all (Section 4.1).
- `unsupported` (`error`) — the operation requires a plugin capability the backend does not declare.

`merge:blocked` is redefined as the gate block at `needs_caller`, and the forge refusal it used to name
becomes `merge:rejected` at `error`. The parallel with `push:rejected` is the argument for the name: in
both, the code host said no for a reason outside the engine's control, and in both the engine cannot
proceed. That also answers the issue's question about whether `merge:blocked` at `error` was a decision
or an accident — it was an accident *of naming*. The class was right for the meaning the token carried;
the word was wrong, because `blocked` was already spoken for as the gate reason.

The registry gains a property it did not have and that is worth stating in the specification directly:
**every operation has at least one `done` reason and at least one `error` reason**, so an `error`-class
result is always expressible, including for `status` and `diff`. The issue asked whether their absence
was deliberate. It was not; it was the artifact of enumerating outcomes an engine had already thought
of, and read-only operations fail — a corrupt repository, an unreachable backend, a base that will not
resolve.

For Section 9.3 the pair of tokens follows the section's own two cases: `capability_unsupported` joins
Section 6.10's configuration-reason registry for the case determinable before the policy runs, and
`<op>:unsupported` covers first use. This keeps decision 0056's boundary intact — a refused policy
reports a configuration reason under `usage_or_config` and carries no proto class; a policy that ran and
hit an undeclared capability reports an operation result that does.

Section 12.2's `ship` sequence needed a corresponding fix, and it is the kind of defect that only shows
up once a class gains a new member. Its push loop named `push:non_fast_forward` and `push:pr_closed`,
then failed on `error` and otherwise broke out of the loop — exhaustive only because those two were the
only `needs_caller` reasons `push` had. With `push:blocked` added, a gate-blocked push would have fallen
through to `create_pr`. The loop now returns any non-`done` result through `result_of`, which routes it
by the Section 5.4 built-in default for its class.

The accepted costs are two. First, the registry is larger: 45 normalized entries where there were 27,
though the specification text grows by three rows and two paragraphs because the universal reasons are
stated once. Second, a redefinition of a major-stable token, taken deliberately and only because no
engine exists yet to break; the anchor change is recorded in `Plan.md`.

We would reconsider Option C if a repository's gate reasons ever needed to be distinguished from the
engine's own failures at the token level rather than through `outputs`. We would reconsider the
universal `unsupported` reason if capability gaps proved to be exclusively determinable at validation,
at which point the configuration reason alone would carry the whole case and the operation reason would
be dead surface.

A related gap this decision deliberately does **not** close, recorded so it is not lost: Section 6.6
requires a blocking hook to return "a stable reason", and the envelope's single `reason` field now
carries the *operation's* token (`blocked` / `failed`). Where the hook's own reason is exposed — a
structured `outputs` key, or only `message` — remains unspecified. It is a separate question about the
envelope rather than about the registry, and folding it in would have mixed two surfaces in one
decision.

The decision is **Accepted** and applied to `VCSX-SPEC.md` (Sections 4.3, 6.6, 6.10, 9.2, 9.3, 10.4,
12.2, 13.1), the vocabulary registry, and the corpus. It resolves parts 1a and 1b of issue #2; part 1c
is decision 0058. Relates to 0051 (the registry the new tokens join), 0056 (whose configuration-reason
registry `capability_unsupported` joins, and whose precedent for fixing major-stable surface before an
engine exists this decision follows), and 0049 (the engine whose absence makes the redefinition
affordable).
