# Background — 0174 Four Core checks against a document the specification declines to pin

## Context

Reported from `symphony-rs` as issue #151, against `5a4fdf7`, found while building the Codex adapter
and its ledger rows (their roadmap D5c).

Four of Section 17.5's Core Conformance checks assert conformance to the Codex app-server protocol.
Section 10's intro declines to pin that protocol, deliberately:

> Implementations MUST consult the targeted agent's documentation or generated schema instead of
> treating this specification as a protocol schema.

Both are right, and together they leave a conforming implementation with four Core checks it cannot
discharge.

## The mechanism

**The report's discrimination is the part that makes this a specification defect rather than a
testing inconvenience, and it is exact.** Measured at `5920773`, Section 17.5 names the targeted
protocol in **six** bullets, not four:

```
$ awk '/^### 17\.5 /,/^### 17\.6 /' SPEC.md | grep -c 'targeted'
6
```

Two of the six are claims that the implementation *extracts* something — "Thread and turn identities
exposed by the targeted protocol are extracted", "Usage and rate-limit telemetry exposed by the
targeted protocol is extracted". Those are checkable against any transcript, including a twin. The
report does not flag them.

The four it does flag are claims that the implementation's behaviour is **valid**, **correct**, or
**according to** an external document: startup "follows" the protocol; payloads are "valid when" it
requires them; framing "required by" it is handled correctly; signals are "interpreted according to"
it. That line — between "we do X" and "X conforms to a document we do not pin" — is where the defect
lives.

**These are unfalsifiable rather than merely unverified.** The report states the epistemics
correctly: an implementation can build a twin of the protocol and test against it, but a twin built
from its own reading of the protocol cannot falsify that reading — it can only agree with it. So the
evidence available to a self-contained conformance run is not weak evidence for these four bullets;
it is not evidence for them at all.

**Section 17.8 does not rescue them**, and the report's reading of it is confirmed. Its header
exempts checks needing "credentials, network access, or external service permissions", and every
bullet under it names tracker apparatus — `LINEAR_API_KEY`, isolated test identifiers, tracker
artifact cleanup. A missing third-party binary is none of those three things; it is a build-time
dependency on someone else's program.

## Options considered

- **Option A — restate the four as claims about the implementation's own behaviour** (the report's
  reading 3), with the unpinnable half moved into a **documented target**.

  Trade-offs: it creates a new MUST-document obligation, which costs a Section 19 entry and a
  template row, and it weakens what the checks assert — an implementation that documents a version
  and targets it consistently passes even if its reading of that version is wrong.

- **Option B — move the four out of Core**, into Section 17.8 or a new profile beside it, and widen
  Section 17.8's header (the report's reading 1, which it calls the smallest change).

  Trade-offs: it is the smallest change, it matches what Section 17.8 exists for, and it stops a
  conforming implementation reporting four rows unmet forever. It loses because **skippable is not
  the problem**. A check that says "our startup follows the protocol" does not become checkable by
  being marked OPTIONAL; it becomes an optional unfalsifiable check. An implementation that ran it
  against a live `codex` would still be asserting conformance to a document this specification
  declines to pin, and two implementations targeting different app-server versions would both pass
  while doing different things — which is the comparison a Conformance Statement exists to support.

- **Option C — name the artifact** (the report's reading 2): pin an app-server version, a published
  schema, or a captured transcript corpus.

  Trade-offs: this is the option that would make the four checks mean what they currently say, and
  it is the one to take if the specification were willing to pin a protocol version. It is not, and
  the refusal is deliberate rather than an omission: Section 10's intro exists to keep protocol
  truth in the other document. Pinning would put this specification in the business of tracking
  someone else's release cadence, and the pin would go stale between revisions of a document it does
  not own — at which point every conforming implementation is validating against a version the
  agent's publisher has moved past.

## Decision and reasoning

**Option A.**

**It is this specification's existing answer, not a new mechanism.** Where behaviour legitimately
varies, the pattern is `Implementation-defined` plus a MUST-document clause — the sandbox profile,
the effective egress policy and the composed environment set in Section 9.6, the park-versus-retry
and backoff choices in Section 14.2. A targeted protocol version is exactly that shape: the
specification cannot choose one, and a consumer needs to know which was chosen. Restating the four
checks against a documented target keeps them Core, keeps the intent that an adapter is held to a
real protocol, and gives an implementation something its own evidence can discharge.

**What Option A gives up, stated plainly.** The four checks no longer assert that the
implementation's reading of the protocol is right. They assert that it names the version it targets,
composes what that version requires, validates against a published schema where one exists, and
documents which. An implementation whose reading is wrong still passes. That is not a weakness
introduced here — it is the state the specification was already in, since nothing in a self-contained
run could have caught it; what changes is that the checks now say so, and that a consumer comparing
two Statements can see the two targets differ instead of reading two identical claims of conformance.

**Consequences carried in the same edit.** The restatement creates a MUST-document obligation, so
Section 19 gains it and `CONFORMANCE-STATEMENT-TEMPLATE.md` gains the matching rows. Decision 0128
records what happens otherwise: an obligation with no row is invisible to every check, the table
being complete against itself, and three decisions in a row missed it before it was caught
downstream. Section 18.1.2's agent-runner item names the documented target too, so the definition of
done and the test matrix agree.

**Section 10's intro is unchanged**, and it is the reason this reading is correct rather than a
workaround. The specification defers protocol truth; the checks now defer with it instead of
asserting past it.

**The obligation is not weakened, and Sections 10.1–10.3 are the evidence.** Found while running
`scripts/check_plan_anchors.py` over this decision's plan, which reported three further sites
carrying the same phrasing:

```
SPEC.md:2891 (Section 10.1): the protocol transport required by the targeted Codex app-server version
SPEC.md:2918 (Section 10.2): Startup MUST follow the targeted Codex app-server contract
SPEC.md:2955 (Section 10.3): processes app-server updates according to the targeted Codex app-server protocol
```

Those are **requirements**, and they stay verbatim. An adapter is still held to the real protocol;
what changes is only what a Section 17 check may assert, a self-contained conformance run being
unable to discharge a claim about a document this specification does not pin. Separating the
requirement from the check is the whole of the change, and reading it as a relaxation would be
reading it backwards. That the anchor checker surfaced these rather than a human reading is worth
noting: the three sites are in a different section from the four bullets and share only a phrase.

## Reconsideration trigger

Reopen if the Codex app-server — or another targeted agent protocol — publishes a versioned schema
under a stable identifier that this specification could cite without tracking a release cadence: a
schema URL keyed by protocol version rather than by product release, say. Option C becomes available
then, and the four checks could assert conformance rather than a documented target. The evidence is
a schema an implementation can name in its Statement *and* a consumer can fetch by that name years
later.

A second trigger: two implementations documenting the same targeted version and behaving
incompatibly. That would mean the documented target is not carrying the information a consumer needs
from it, and the answer would be to require the composed payloads themselves to be published rather
than the version they were composed against.
