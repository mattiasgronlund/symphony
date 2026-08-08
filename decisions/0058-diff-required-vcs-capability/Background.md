# Background — 0058 `diff(base)` is a required VCS backend capability

## Context

The third condition issue #2 raised. `VCSX-SPEC.md` Section 4.1 makes `diff` one of the required
operations — "the branch delta against the resolved base. Read-only." — and Section 8.1 lists it as an
entry point a driver may call directly. Section 9.1's "Required capabilities" for a VCS backend are:

> `detect_mode()`, `current_branch()`, `is_dirty()`, `is_conflicted()`, `ahead_behind(base)`,
> `derive_work_branch(pattern, identity)`, `commit(message, identity)`, `integrate(base)`,
> `push(work_branch)`, `pull(work_branch)`

There is no `diff`. `ahead_behind` returns counts, not content, so nothing in the specified plugin API
produces a branch delta: a conforming engine could not implement a required operation through the
required interface. Every other operation traces to a capability — `status` to `current_branch` /
`is_dirty` / `is_conflicted` / `ahead_behind` plus the forge's `pr_state`, `commit` / `integrate` /
`push` / `pull` to their like-named capabilities, `create_pr` and `merge` to Section 9.2 — which is what
makes the omission look like an oversight rather than a design.

The issue also raised the reading that resolves it without an edit: if "Required capabilities" is a
minimum rather than a maximum, an engine adds the capability and every plugin implements something the
specification never asked for. That works, and it is what an implementer would do. It is also exactly
the drift Section 14 exists to prevent — two engines would spell the same capability differently, and a
plugin written for one would not load in the other.

## Options considered

- **Option A — add `diff(base)` to Section 9.1's required capabilities (chosen).** Trade-offs: closes
  the gap with one bullet, in the shape the neighbouring capabilities already use, and every VCS backend
  must provide it. It makes the required capability set complete over the required operation set, which
  is the property the section implicitly claims.
- **Option B — leave Section 9.1 as it is and read the list as a minimum.** Trade-offs: no edit, and the
  specification is not literally wrong if the list is a floor. But a required operation would still have
  no specified way to be realized, and the capability's name, signature, and result token would be
  chosen independently by every engine — the case Section 14 calls a contract change and requires to be
  spelled identically.
- **Option C — express `diff` through the existing capabilities**, for example by widening
  `ahead_behind(base)` to return content. Trade-offs: no new capability. But it overloads a capability
  whose whole value is that it is cheap and countable, forces every backend to produce a diff whenever
  `status` asks for ahead/behind counts, and confuses two operations Section 4.1 keeps separate.
- **Option D — make `diff` an OPTIONAL operation, capability-gated like the forge's review-thread
  writes.** Trade-offs: consistent with how Section 9.2 handles capabilities not every forge has. But
  `diff` is not a capability some backends lack — a version-control system that cannot produce a delta
  between two states is not one the engine could drive at all — and demoting a required operation to
  close a gap in the plugin list would be fixing the wrong end.

## Decision and reasoning

Choose **Option A**. `diff(base)` → `diff:*` joins Section 9.1's required capabilities, returning the
branch delta against the resolved base (Section 6.4), read-only, in the same bullet shape as its
neighbours.

The reasoning is the invariant rather than the bullet: **every required operation MUST be realizable
through the required capabilities.** That is what Section 9.1 was already trying to say, and `diff` was
the one operation where it was not true. Stating the invariant is worth more than the missing bullet,
because it is the property a reviewer can check when the next operation is added.

The issue's minimum-versus-maximum question is answered directly rather than left to inference, since it
is the part an engine would otherwise resolve locally: the list is the **minimum** every VCS backend
MUST provide. An engine MAY define additional operations (Section 4.1), and where it does it MUST
document the capabilities they require of a backend in its Conformance Statement (Section 13.3) — so an
engine-specific capability is visible as engine-specific rather than mistaken for part of the shared
surface. That keeps Section 14's rule enforceable: what is in Section 9.1 is spelled identically
everywhere, and what an engine adds is declared as its own.

No proto-class or reason-token consequences follow. `diff` already has `diff:ok` (`done`), and decision
0057 gives it `diff:failed` and `diff:unsupported` at `error` along with every other operation, so a
backend that cannot produce a delta has a defined result. The descriptor fields in Section 9.1 are
unchanged: `diff` is required, so there is nothing to advertise.

We would reconsider if a checkout mode appeared whose delta could not be expressed against a single
resolved base, at which point the capability's signature — not its requiredness — would be the thing to
revisit.

The decision is **Accepted** and applied to `VCSX-SPEC.md` (Sections 9.1, 13.3) and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`. It resolves part 1c of issue #2; parts 1a and 1b are decision
0057. Relates to 0057 (which gives `diff` its `error`-class reasons) and to 0040 (which authored the
plugin API).
