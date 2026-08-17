# Plan — 0122 A trigger kind nothing can raise is surface, not a feature

## Scope

`VCSX-SPEC.md`: Sections 5.1 "Triggers", 5.3 "Matching Algorithm and the `#class` Fallback", 5.4
"Unmatched Policy and Determinism", 6.5 "`[policy]` Edges", 6.7 "`tracker.transitions`", 6.9
"`[tasks]` and `[driver]`", 6.11 "Validation", 7.3 "The Embedded-Driver Contract", 8.4 "Escalation
Payload", 12.1 "Match a Trigger", 13.1, 13.2.

`VCSX-CONTRACT.md`: Sections 5.1 "Triggers", 5.4 "Unmatched Policy", 8 "Task Model and Broker Task
Verbs".

`SPEC.md` Section 9.12 is repaired by decision 0127, which depends on this one.

## Steps

1. **`Triggers` — two kinds.** Ensure Section 5.1 defines lifecycle positions and typed operation
   results and no third kind, and states in one sentence where the removed kind went: an event the
   consumer observes selects which entry point the consumer invokes (Sections 6.9, 8.1), rather than
   entering the executor as a trigger. Done-condition: no trigger kind is listed that no invocation
   can raise.

2. **The matching ladder.** Ensure Section 5.3 gives ladders for the two remaining kinds and Section
   12.1's `ladder()` has two arms. Done-condition: `ladder()` is total over the triggers Section 5.1
   defines.

3. **Unmatched policy.** Ensure Section 5.4's dispositions cover an unmatched lifecycle position (a
   benign no-op) and an undisposed operation outcome (fail-safe), and no longer a third case.
   Done-condition: the section's cases and Section 5.1's kinds correspond one to one.

4. **An edge's `on`.** Ensure Section 6.5's prose and its TOML comment admit a lifecycle position, an
   `op:reason`, an `op:#class` or a `#class`, and that Section 6.11's `unknown_trigger` row matches.
   Done-condition: the three statements of what `on` may be agree.

5. **`tracker.transitions` — named as consumer-read.** Ensure Section 6.7 states that the table is
   read by the consumer rather than matched by the executor, on the same footing as `[tasks]` and
   `[driver]`: `set_state` is consumer-effected and a tracker is outside the VCS/forge domain, so the
   condition `on` names is one the consumer observes and the vocabulary is the consumer's to publish
   (`SPEC.md` Section 11.6). Ensure the engine still validates the graph's determinism as part of the
   document it loads (`duplicate_transition`). Done-condition: nothing implies the executor matches
   `on`, and the worked example's `pull_request_opened` is glossed as a consumer-observed condition
   rather than removed.

   *(This step replaces a first attempt that re-grounded the trigger space on the engine's typed
   results; see the review finding in `Background.md` for why that was wrong.)*

6. **`[tasks]` and `[driver]` — read by the consumer.** Ensure Section 6.9 states that these tables
   are read by the consumer running the task model rather than matched by the executor, so
   `[driver]`'s `on` names an event the consumer observes and `run` the entry point it then invokes
   (Section 8.1). Ensure Section 7.3's task-model bullet describes the same flow. Done-condition:
   nothing implies the executor dispatches `[driver]`, and the tables keep their place in
   `repo.policy.toml`.

7. **The escalation `op`.** Ensure Section 8.4's rule for a null `op` names the two remaining cases —
   a lifecycle position where the gated operation has not run, and a bound the executor reached.
   Done-condition: every case the rule names is reachable.

8. **`VCSX-CONTRACT.md`.** Ensure Section 5.1's trigger kinds, Section 5.4's unmatched-policy rule and
   Section 8's task-model semantics match the full spec at the surface's altitude: the task model
   yields events the **consumer** acts on, and the `[driver]` wiring is where it names the entry point
   to run. Done-condition: no token is spelled in one document and absent from the other, which is
   Section 12's alignment rule.

9. **Sections 13.1, 13.2.** Ensure the test matrix's matching and undisposed-policy checks no longer
   assert a signal disposition, and gain one asserting that an edge whose `on` is not a position or a
   typed result is refused with `unknown_trigger` — so the removed vocabulary is refused at validation
   rather than accepted and ignored. Ensure the checklist's machine bullet drops
   "no-op-on-unmatched-signal". Done-condition: no check asserts behavior for a trigger kind that no
   longer exists, and a policy written against the old vocabulary fails loudly.

## Cross-cutting sync

Section 8.5 is unaffected in mechanism and affected in fact: removing a trigger kind is a change to
the major-stable surface, so it lands in the next `MAJOR`. Record that in the section's own terms
rather than as an exception.

Section 13.3 gains nothing.

`SPEC.md`: Section 9.12's trigger list is decision 0127's. Sections 8.10 and 11.6 need no normative
change — they already describe consumer-side wiring — but Section 8.10's "The `tasks:all_closed`
trigger [...] fires" is reworded to name the consumer as what observes it, so the two documents do not
disagree about who matches.

## Anchor changes

Removed anchors: the **signal** trigger kind, and with it the tokens `ready-for-review`, `blocked`,
`done`, `tasks:all_closed` and `task:#needs_help` as *engine triggers*. The last two survive as
`[driver]` `on` values the consumer reads, and the first three survive in `SPEC.md` Section 11.6 as
tracker transition triggers; neither survival is an engine trigger.

No anchor is removed from `tracker.transitions`: `pull_request_opened` and the rest of `SPEC.md`
Section 11.6's vocabulary keep their spellings and their meanings, the table being consumer-read.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.1, 5.3, 5.4, 6.5, 6.7, 6.9, 7.3, 8.4, 12.1, 13.1, 13.2),
`VCSX-CONTRACT.md` (Sections 4, 5.1, 5.4, 8), `conformance/vcsx/vocabulary.json`,
`conformance/vcsx/vectors/match-edge.json`, `conformance/vcsx/vectors/policy-validation.json`, and
the two conformance READMEs.
