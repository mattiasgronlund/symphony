# Background — 0051 The engine token vocabulary as data

## Context

`VCSX-SPEC.md` Section 14 "Alignment with `VCSX-CONTRACT.md`" states the rule that keeps the engine's
two documents coherent: "Every token shared between the two — the operations, the lifecycle positions,
the trigger and action names, the proto classes, the reason and `need` vocabularies, the
`repo.policy.toml` sections, the task and message-formulation surfaces — MUST be spelled identically in
both. Changing a name is a contract change: update both documents in step."

That rule was written for two prose documents in one repository, where drift is at least visible in a
single diff. Decision 0049 puts the first engine implementation in a separate repository, which makes
the source a **third** spelling of the same vocabulary, in a second repository, maintained on its own
cadence. Nothing mechanical connects them. The rule's enforcement mechanism has been review, and review
across two repositories is where this class of drift survives longest — a renamed reason or a
mis-classified proto class produces no build failure anywhere, it just makes a policy edge stop firing.

The vocabulary is also unusually well suited to being data rather than prose. Section 4.3 is already a
26-row table of `(operation, reason, class, meaning)`; Section 4.1 is a closed list of eight operations
and four lifecycle positions; Section 4.2 has three proto classes; Section 5.2 has eight actions;
Section 8.3 has four exit codes. These are enumerations that happen to be typeset as prose, and their
correctness properties are exactly the kind a machine checks well: a reason's class must not change
within a major version (Section 8.5), and every reason must appear in the registry with a documented
class (Section 4.3).

Decision 0045 anticipated this. It considered "a machine-readable manifest schema" as its Option D and
*deferred* it — not rejected — on the grounds that it "over-commits to a wire format before an
implementation exists to shape it", naming as its trigger "once a second implementation or a
conformance harness creates demand". Decision 0049 is that trigger.

## Options considered

- **Option A — the vocabulary as a machine-readable artifact (chosen).** A JSON registry in the
  specification repository enumerating every token Section 14 names, each carrying the properties the
  specification fixes (a reason's proto class, an operation's lifecycle position and read-only status,
  an action's effecting party). Both documents are checked against it, and the Rust engine generates
  or checks its types from it. Trade-offs: makes the Section 14 rule mechanical rather than
  review-borne, and gives the separate implementation repository something concrete to consume across
  the repo boundary — the specific gap 0049 opened. Costs: one more artifact that must itself stay
  aligned with the prose, and the risk that it is treated as normative when the prose governs.
- **Option B — an extraction-and-diff checker.** A script that parses the token sets out of
  `VCSX-SPEC.md` and `VCSX-CONTRACT.md` and reports differences. Trade-offs: no new artifact to keep in
  sync, and it directly enforces the rule as written. But it is a parser over prose, which is brittle
  against ordinary editing, and it does nothing for the third spelling in the other repository — which
  is the part decision 0049 actually made worse.
- **Option C — prose discipline only.** Keep Section 14 as-is; the engine repository pins a
  specification revision and re-reads on bump. Trade-offs: zero machinery. But it leaves the rule
  enforced by review across two repositories, and the failure mode is silent: a mis-classified reason
  routes to the wrong `#class` edge and changes which policy fires, with no build or test failure in
  either repository to catch it.

## Decision and reasoning

Choose **Option A**. Publish the shared token vocabulary as `conformance/vcsx/vocabulary.json` in the
specification repository, with a `conformance/vcsx/README.md` defining its schema and its standing.

The decisive argument is the one 0049 created rather than any pre-existing weakness in Section 14. Two
prose documents in one repository can be held aligned by review; a third spelling in a second
repository cannot, and the failure is silent rather than loud. A single artifact that the engine
generates its reason enum, proto-class mapping, and exit-code mapping from converts the entire class
of drift into a compile error in the place it matters — which is precisely the reason decision 0049
chose a language with exhaustive matching in the first place. The two choices are the same argument
applied at different layers.

**The prose governs; the artifact is derived.** `VCSX-SPEC.md` remains the source of truth, exactly as
`SPEC.md` does for the Symphony corpus under decision 0046. The registry restates no requirement's
substance — it carries names and the properties the specification fixes about them, each row citing
the section it is read from. Where the two disagree, the specification is right and the registry is a
bug. This mirrors the corpus's discipline, where "expected values are never invented; they are read
from these sections".

The artifact lives under `conformance/` because it is machine-readable conformance data of the same
kind, but in its own `vcsx/` subtree with its own README rather than folded into the Symphony corpus:
the two derive from different specifications, have different schemas, and are consumed by different
implementations. The Symphony corpus is a set of behavior vectors; this is a vocabulary registry. They
share a parent directory and nothing else.

We would reconsider if the registry began accumulating properties the prose does not fix — the sign
that it has stopped being a derived view and started being a second specification. The remedy then is
to move the concept into `VCSX-SPEC.md` and re-derive, not to let the registry lead.

The decision is **Accepted** and applied: `conformance/vcsx/vocabulary.json` and
`conformance/vcsx/README.md` are created. Depends on 0049 (which created the third spelling) and 0045
(whose deferred Option D this takes up on its stated trigger); relates to 0046 (the corpus discipline
it reuses) and to `VCSX-SPEC.md` Section 14, whose rule it mechanizes without changing.

A conformance **corpus** for the engine — behavior vectors for the matching ladder and the fail-safe
rules of Section 5.3–5.4, in the shape decision 0046 established — is a natural successor and is
deliberately not taken here. This decision publishes the vocabulary; vectors that exercise the machine
*over* that vocabulary are a separate slice with its own derivation work.
