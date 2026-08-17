# Plan — 0121 A validation input with no carrier is a verdict each engine reaches on its own

## Scope

`VCSX-SPEC.md`: Section 8.1 "Entry Points and Arguments" (the two arguments and the
consumer-configuration list), Section 6.11 "Validation" (the two inputs now name their carrier),
Section 8.2 "Result Envelope" (`unperformed_intents` is computable from the declared set),
Sections 13.1, 13.2.

`VCSX-CONTRACT.md`: Section 4, where the consumer configuration's contents are listed at the surface.

## Steps

1. **`effectable_actions`.** Ensure Section 8.1 defines an OPTIONAL consumer-supplied argument naming
   which of the consumer-effected actions (`create_task`, `set_state`, `notify`, Section 5.2) the
   consumer can perform, with `Default: empty`. State the default's direction and why: a default
   admitting every action validates a `set_state` policy against a consumer that cannot advance a
   state, which is the stranding `set_state_unbound` exists to refuse. Done-condition: the argument
   exists with its default stated and argued.

2. **`bound_units`.** Ensure Section 8.1 defines an OPTIONAL consumer-supplied argument naming the
   repository unit names the consumer bound, with `Default: empty`, and states that it is what a
   `[messages.pr]` `body_source = "template"` and a `[messages.squash]` `transform` are checked
   against (Sections 6.8, 10.2, 10.3). Done-condition: the argument exists and both checks name it.

3. **The consumer-configuration list.** Ensure both arguments join the enumeration of values the
   engine MAY read from the consumer configuration, on the same footing as the backend selection and
   the access parameters — they are facts about the consumer rather than about one invocation, and
   are stable across invocations in the way `pr_state_validator` is explicitly not. Done-condition:
   the list names both, and the `pr_state_validator` exception paragraph still reads as the one
   exception.

4. **`Validation` — the fourth and fifth inputs name their carrier.** Ensure the five-input list
   points each of the last two at the argument that supplies it, as the third already points at
   Section 8.1's selection and access configuration. Done-condition: every one of the five inputs
   names where it arrives from.

5. **`Validation` — the ordering sentence.** Ensure the paragraph that traces when the engine holds
   the third input covers these two on the same terms: both are decoded with the invocation's
   arguments, so both are held by the time the checks run. Done-condition: no input is judged before
   the engine is stated to hold it.

6. **The asymmetry among the three actions.** Ensure Section 5.2's dispositions are stated against
   the declared set: an action outside `effectable_actions` is `set_state_unbound` for `set_state`
   and a reported intent for `create_task` and `notify`. Done-condition: the existing
   configuration-error-versus-benign-no-op split is preserved and now turns on a value the engine
   holds.

7. **`unperformed_intents` is computable.** Ensure Section 8.2's entry states that an intent naming an
   action outside `effectable_actions` is unperformed by construction, so the key is composed from
   what the engine holds rather than from a report the consumer returns — which is what makes it
   readable under the subprocess encoding as under the in-process one (Section 8). Done-condition: the
   key needs no runtime answer from the consumer.

8. **`VCSX-CONTRACT.md` Section 4.** Ensure the consumer configuration's description at the surface
   names what the two arguments carry, in the surface's altitude — what the consumer can effect and
   which repository units it bound — without restating the field-level schema, which Section 11
   defers. Done-condition: the surface and the full spec name the same two inputs.

9. **Sections 13.1, 13.2.** Ensure the test matrix checks that a `set_state` edge against a consumer
   declaring no `set_state` is refused with `set_state_unbound` before any operation runs; that a
   `create_task` edge against the same consumer validates, emits, and reports the intent in
   `unperformed_intents`; that a `template` body source and a `transform` naming a unit outside
   `bound_units` are refused with their own reasons before a push and before a merge respectively;
   and that a consumer supplying neither argument is refused for all three rather than deferring to
   first use. Ensure the checklist's validation bullet names both inputs. Done-condition: steps 1, 2,
   6 and 7 each have a check.

## Cross-cutting sync

Section 13.3 gains nothing: both arguments are fully specified and the encoding obligation Section
8.1 already states for every argument covers them. Section 8.6 gains no precondition row — an absent
argument is an empty set rather than a missing value, which is what the defaults are for.

`SPEC.md`: Symphony is a consumer that runs the task model and the tracker, so it declares all three
actions and binds its own units. No normative change; Section 9.7's `vcs` configuration gains nothing,
these being properties of the deployment rather than per-repository operator policy.

## Anchor changes

New anchors: the `effectable_actions` and `bound_units` arguments. No anchor is renamed or removed;
`set_state_unbound`, `template_unbound` and `transform_unbound` keep their spellings and their
meanings, and gain a stated input.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.2, 6.11, 8.1, 8.2, 13.1, 13.2) and `VCSX-CONTRACT.md` (Section
4).
