# Background — 0055 Signals are matched exactly; the `#class` fallback is result-only

## Context

Decision 0053 surfaced this while authoring the engine conformance corpus. `VCSX-SPEC.md` Section 5.3's
matching ladder gave signals a fallback rung:

> For a **signal / task-state event** `s`: try `s` → (for a `#class`-shaped event token such as
> `task:#needs_help`) its class form → the unmatched-signal default (Section 5.4).

The rung is not resolvable. `needs_help` is not one of the three proto classes (`done`, `needs_caller`,
`error`, Section 4.2), so `task:#needs_help` is not a `#class` form in the sense Section 5.3 uses two
bullets earlier. If it is instead the class form of some *concrete* task event, no mapping from a
concrete event to its class form is defined anywhere, and no vector for the rung could be authored —
the corpus covers only exact-match signal cases.

Section 12.1's `ladder()` carried the same unresolvable step (`return [ s, class_form(s) if any ]`),
with `class_form` undefined.

Two facts bound the resolution. First, the proto class is a property of an *operation result*
(Section 4.2 defines it on `<op>:<reason>`); a consumer-raised signal has no operation and therefore no
class, so the `#class` machinery has nothing to compute over. Second, Section 7.3 puts the task model
outside the engine entirely — "The task model, its durability, and its materialization into an external
tracker are the driver's; `vcsx` only consumes the resulting events" — so defining a class taxonomy for
task events would have the engine specifying the shape of a subsystem it explicitly does not own.

## Options considered

- **Option A — drop the fallback; signals match exactly (chosen).** A signal is matched exactly and
  has no class form; `tasks:all_closed` and `task:#needs_help` are ordinary tokens the consumer raises,
  and the `#` in the latter names a condition across tasks rather than a proto class. Trade-offs:
  removes an unresolvable mechanism rather than defining one, and aligns the ladder with what a proto
  class actually is. Loses a generalization for grouping signals — but nothing uses it, and a consumer
  wanting per-task granularity can raise a concrete token the policy binds exactly.
- **Option B — define an event-class vocabulary for task events.** Give task events their own class
  taxonomy parallel to the proto classes, with a defined concrete-to-class mapping. Trade-offs: keeps
  the fallback and makes it work. But it invents a second class system for a subsystem Section 7.3
  assigns to the driver, and the engine would have to fix the concrete event vocabulary — the exact
  coupling Section 7.3 avoids by consuming only the resulting events.
- **Option C — let the consumer declare each signal's class form.** The consumer raising a concrete
  event supplies its class form alongside it. Trade-offs: keeps the fallback without the engine owning
  the taxonomy. But it adds schema to the consumer boundary and a validation surface for a mechanism
  with no current use, and it makes matching depend on data supplied per invocation rather than on the
  policy alone.

## Decision and reasoning

Choose **Option A**. Signals and task-state events are matched exactly; the `#class` fallback applies
to typed operation results alone.

The decisive fact is that a proto class is a property of an operation result, so the fallback has
nothing to compute for a trigger with no operation. That reading also makes Section 5.3's three bullets
consistent for the first time: a lifecycle position has no class form because there is no outcome to
classify (decision 0054), a signal has none for the same reason, and a typed result has one because it
is the only trigger kind that carries a class. What looked like an inconsistent special case in the
signal bullet was the ladder reaching for a property that only one trigger kind has.

`task:#needs_help` keeps its spelling — no token is renamed — but the specification now says what the
`#` means there: a condition *across tasks*, raised once when any task needs human help, rather than a
class rung over per-task events. That reading matches `VCSX-CONTRACT.md` Section 8, where the task
surface's events are the two aggregate ones (`tasks:all_closed` driving computed completion, and
`need-help` producing a human-assigned task that parks), not a per-task stream.

The cost is accepted deliberately: a policy that wants to react to several distinct task conditions
must bind each token rather than one class edge. That is the same cost the specification already
accepts for agent milestone signals (`ready-for-review`, `blocked`, `done` are three separate
bindings), and unlike operation reasons — where Section 8.5 lets a `MINOR` release add tokens that
existing policies must absorb — the signal vocabulary is raised by the consumer, so a consumer never
surprises its own policy with a token it did not choose to raise. The `#class` fallback exists to
absorb *upstream* additions; signals have no upstream.

We would reconsider if a consumer's signal vocabulary grew large enough that grouping became a real
need, or if the engine ever began raising signals of its own — at which point the absorption problem
the `#class` fallback solves would exist for signals too, and a class form would have somewhere to come
from.

The decision is **Accepted** and applied to `VCSX-SPEC.md` (Sections 5.1, 5.3, 12.1), the vocabulary
registry (`trigger_kinds`), and the corpus (`match-edge.json` gains
`hash_shaped_task_event_is_an_ordinary_token` and `signal_takes_no_class_fallback`). Depends on 0053,
which surfaced it; relates to 0030 (the action-policy machine), 0031 (autonomous task management), and
0054 (the sibling clarification that makes Section 5.3's three bullets consistent).
