# Background — 0069 `observability.*` is the configuration namespace for observability settings

## Context

Resolves part 2 of issue #15, raised while deciding what `SPEC.md` Section 13 means for an
implementation (against `06a3bc19`).

Section 18.2 carries the specification's own TODO: "Make observability settings configurable in
workflow front matter without prescribing UI implementation details." Nothing in Section 5.3 or the
Section 6.4 cheat sheet defines a namespace for one. Every other extension owns one — `budget.*`
(Section 8.8), `quota.*` (Section 8.9), `compute.*` (Section 9.11), `server.*` (Section 13.8),
`[tasks]` / `[driver]` in `repo.policy.toml` (Section 8.10) — each stated in the same sentence shape:
"The extension owns its configuration under the `X.*` namespace, documented with it."

Section 13.6 then requires the per-execution usage ledger to own its configuration "under its own
namespace, documented with the extension" **without saying what that namespace is**. That is the gap
at its sharpest: an obligation to use a namespace, with no namespace named.

The consequence is not abstract. The first implementation to make a sink, a level, or a ledger path
configurable invents a top-level key; the second invents a different one. Both are configuring the
same deployment concern, and — because `WORKFLOW.md` is repository-owned and has to render on any
implementation Symphony targets — a repository that configures one cannot be read by the other. The
cost of leaving this open rises with every implementation written before it is closed, and nothing
about it is hard: it is a name.

Answering it exposed that the TODO's own premise is stale. It says "in workflow front matter", but
Section 5 has since split configuration into three artifacts by owner and trust: `WORKFLOW.md` is
repository-owned and in-sandbox, "contains only settings used *inside* the agent sandbox", and MUST
NOT carry "any setting Symphony executes with host access". A log sink path, a ledger storage
location, and a retention policy are exactly settings Symphony executes with host access. Under
Section 15.4's trust sourcing, honoring them from the worktree would let anyone who can commit —
including the agent — choose where the daemon writes on the operator's host.

## Options considered

- **Option A — `observability.*` in the operator policy config, with the ledger under
  `observability.ledger.*` (chosen).** One namespace for the Section 13 surfaces, named in Section
  18.2 in the shape the other extensions use, placed in the operator policy config because the
  settings have host-side effects. Trade-offs: it overrules the TODO's stated artifact, and it
  reserves a namespace whose fields the specification does not define — a reader may expect a schema
  and find a name.
- **Option B — `logging.*`** (rejected). Narrower and more conventional. It is the wrong name for
  what has to fit in it: the ledger (Section 13.6) is not logging, nor is a status surface (Section
  13.4) or a humanized event summary (Section 13.7). A namespace that has to be widened later is
  worse than a wide one now, because widening it is a rename and a rename is what a namespace exists
  to prevent.
- **Option C — a namespace per surface (`log.*`, `status.*`, `ledger.*`)** (rejected). It follows
  the letter of "the extension owns its configuration under its own namespace" for each Section 13
  extension separately. But it multiplies top-level keys for what an operator experiences as one
  concern, and Section 5.3's core key list is deliberately short. Section 13's surfaces are
  variations on one thing; `observability.ledger.*` gives the ledger its own namespace *within* the
  concern, satisfying Section 13.6 without a third top-level key.
- **Option D — follow the TODO and put it in `WORKFLOW.md` front matter** (rejected). It is what the
  document literally asks for and matches `server.*`'s placement in Section 13.8. It is refused on
  Section 5's own rule: `WORKFLOW.md` is untrusted, in-sandbox, and MUST NOT carry a setting Symphony
  executes with host access, which a sink path and a ledger location plainly are. The TODO predates
  the three-artifact split; following it now would re-open the trust boundary decisions 0005 and 0029
  drew.
- **Option E — define the fields as well as the namespace** (rejected, and drawn as this decision's
  scope line). It would answer the TODO in full. But Section 13.2 makes the sink
  `Implementation-defined` and Section 13.4 makes the status surface OPTIONAL and
  implementation-defined, so there is no cross-implementation field to define — only per-
  implementation ones, which Section 5.3 already governs ("Extensions MAY define additional top-level
  keys"; "Extensions SHOULD document their field schema"). Picking field names here would prescribe
  the UI details the TODO itself rules out.
- **Option F — leave the TODO** (rejected). Zero surface, honest about there being nothing
  configurable today. But the TODO has been read once already by an implementation that then had to
  invent a key, which is the failure the namespace prevents; and a TODO is not a decision anyone can
  build against.

## Decision and reasoning

Choose **Option A**. Section 18.2's TODO bullet is replaced by a bullet naming `observability.*` as
the config namespace for the Section 13 surfaces — the log sink (13.2), a human-readable status
surface (13.4), humanized event summaries (13.7), and the usage ledger's storage location and
retention under `observability.ledger.*` (13.6) — stating that it belongs to the operator policy
config, and stating explicitly that the specification names the namespace, not the fields.

**The specification owes the place, not the settings.** That is the division worth keeping. A
namespace is a cross-implementation contract: two implementations reading the same configuration
must agree on where these keys live, or the configuration is not portable. The individual settings
are not a cross-implementation contract, because Sections 13.2 and 13.4 make the sink and the surface
implementation-defined in the first place — an implementation that writes to a journal and one that
writes to a file do not have the same fields, and forcing them to would be exactly the UI
prescription the TODO warns off. So naming the namespace discharges the TODO rather than deferring
it: what remained after the name was never the specification's to define.

**Artifact placement follows trust, not the TODO's wording.** Section 5's dividing rules are
explicit: settings consumed inside the sandbox go in `WORKFLOW.md`, the repository's Way of Working
goes in `repo.policy.toml`, and "everything else Symphony uses outside the sandbox that is an
*operator or deployment* concern" goes in the operator policy config. Observability is the third:
the operator, not the repository, decides where their daemon's logs go. `compute.*` is the precedent
in both shape and placement — "The extension owns its configuration under the `compute.*` namespace
(Section 6.4), in the operator policy config."

Nesting the ledger as `observability.ledger.*` is what makes Section 13.6's existing sentence true
without weakening it. The ledger keeps a namespace of its own, documented with the extension; it is
simply a namespace inside the observability one rather than a fourth top-level key.

One thing is recorded as noticed and not fixed: **`server.*` is placed in `WORKFLOW.md` front matter
by Section 13.8**, which is in tension with Section 5's rule for the same reason Option D is
rejected — binding a host port is host access. That is a defect in Section 13.8, not a precedent, and
it is why this decision follows Section 5 rather than the nearest neighbour. Reconciling it is its
own change; it is recorded in `conformance/README.md`'s surfaced findings so it is not lost.

We would reconsider if a genuinely cross-implementation observability field appears — a log level or
a sink URI that means the same thing everywhere — in which case the specification should define that
field under this namespace rather than leaving it implementation-defined. We would also reconsider
the placement if Section 13.8's `WORKFLOW.md` enablement is affirmed rather than corrected, since a
consistent document cannot put one observability extension in each artifact.

The decision is **Accepted** and applied to `SPEC.md` Sections 6.4, 13.6, and 18.2. Relates to 0005
and 0029 (the configuration trust split whose rule decides the artifact), 0011 (the execution ledger,
whose unnamed namespace this names), 0045 (the Conformance Statement, which publishes the namespaces
an implementation ships), and 0070 (whose template rows carry `observability.*` in the namespace
column).
