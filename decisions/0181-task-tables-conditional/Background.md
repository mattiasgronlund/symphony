# Background — 0181 A REQUIRED item names the task tables only where the extension ships

## Context

Reported from `symphony-rs` as issue #177, against `86a2188`, found at that repository's roadmap D8d
while it was writing the first Conformance Statement that had to say, item by item, whether Section
18.1 is met. It is tracked there as decision 0011 R111. Section 18.1.4's action-policy item:

> The tables Symphony reads rather than the executor — `tracker.transitions`, `[tasks]`, `[driver]`
> — are matched by Symphony against its own trigger vocabulary (Sections 8.10, 11.6)

Section 18.1 is the REQUIRED checklist, and this item states no condition. `[tasks]` and `[driver]`
belong to Section 8.10, "An OPTIONAL extension of `Daemon Conformance`", whose own configuration
bullet says "Core conformance does not require these fields". Section 18.2 lists the extension as
owning them.

## The mechanism

The report argued from OPTIONAL against REQUIRED: an implementation that ships no Section 8.10
can't tell whether it is one item short of the group or meets it, so whether a conformance claim is
available at all depends on how the item is read.

**A second argument settles which reading is right.** Section 18.1's preamble: "`interactive-agent`
satisfies Sections 18.1.1, 18.1.2 and 18.1.4". Section 8.10, in its second sentence: "It is
daemon-only. Interactive sessions use `ship`/`land` and have no task manager." Read
unconditionally, the item requires every `interactive-agent` deployment to match tables the
specification defines it as not having. That is a contradiction inside the specification, not an
ambiguity for one implementer, and it rules out the unconditional reading. The condition has to be
"where Section 8.10 is implemented", which also limits it to `daemon`.

The only sign of a condition today is the trailing citation `(Sections 8.10, 11.6)`, and a citation
is not a condition.

## Options considered

- **State the condition in the item** (chosen). `tracker.transitions` is matched unconditionally,
  and `[tasks]` and `[driver]` where the implementation ships Section 8.10. The extension's Section
  18.2 entry gains the matching obligation, so whoever ships it finds the obligation in the
  extension's own row.
- **Move the task-table half to Section 18.2 entirely.** This is cleaner in that a REQUIRED item
  would name no extension surface at all. It loses because the rule is one rule: Symphony, not the
  executor, matches the tables it reads, against its own vocabulary. Splitting it would leave the
  REQUIRED item silent about who matches the extension's tables when they exist, and that is the
  part the item exists to say.
- **Make the tables REQUIRED.** No reading supports it, and it contradicts Section 8.10's
  "daemon-only" sentence.

## Decision and reasoning

The condition goes in place, in the item's own sentence. `symphony-rs` already reads it that way
and publishes the reading in its Conformance Statement, which can now cite the item directly. No
Conformance Statement template row is owed: the template's Section 1 lists checklist groups, not
individual items, and the decision adds no `Implementation-defined` value.

Noticed and not opened here: whether an `interactive-agent` deployment owes `tracker.transitions`
matching at all. Section 11.6's run outcomes are "observed by the orchestrator", and that topology
has no orchestrator. This decision keeps `tracker.transitions` unconditional because nothing yet
shows that to be wrong. `symphony-rs` noted the question on the thread without opening it.

**Reconsideration trigger:** a report showing that an `interactive-agent` deployment cannot match
`tracker.transitions` either. That would make the item's remaining unconditional half the next
contradiction, and the item would need a topology condition as well as an extension condition.
