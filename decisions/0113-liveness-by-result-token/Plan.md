# Plan — 0113 The specification already knows how to do this, in one place and not the other

## Scope

`SPEC.md`: Section 10.7 "Agent Runner Contract" (the evidence rule), Section 10.6 "Timeouts and
Error Mapping" (the exit-status clause), Section 9.4 "Workspace Hooks" (the signal clause), Section
14.1 "Failure Classes" (the condition under `agent_session_failures`), Sections 17.5, 18.1.

`conformance/vocabulary.json`: no new token — the condition is reported under an existing failure
class and the events already exist.

## Steps

1. **`Agent Runner Contract` — success is evidenced.** Ensure Section 10.7 states that a turn is
   reported successful only where the adapter observed the targeted protocol's terminal success
   signal, normalized to `turn_completed` (Section 10.4), and that a turn whose process ended
   without any terminal signal is a failed turn whatever its exit status. Done-condition: a reader
   can tell what evidence a successful `run_turn` result requires, rather than only what an error
   does.

2. **`Agent Runner Contract` — the boundary is preserved.** Ensure the text states that what a
   terminal signal *means* remains the protocol's and the adapter's; what this fixes is that the
   adapter must have observed one. Done-condition: the clause does not adjudicate turn semantics.

3. **`Timeouts and Error Mapping` — exit status is not an outcome.** Ensure Section 10.6 states that
   a process's exit status is evidence the process ended and no evidence of what it accomplished, so
   it MUST NOT be read as a turn outcome in either direction. Done-condition: an exit `0` with no
   terminal event maps to a failed turn.

4. **`Agent Runner Contract` — an unobserved death cannot report success.** Ensure the text states
   that an adapter MUST NOT report a turn successful on the evidence that a process it backgrounded
   did not report a failure. Done-condition: the general form of the reported failure is prohibited,
   not only the reported instance.

5. **`Workspace Hooks` — the narrower half.** Ensure Section 9.4's failure semantics state that a
   hook whose process was terminated by a signal is a failed hook, whatever its exit status. Ensure
   the text notes this is the narrower rule because a shell script carries no event vocabulary.
   Done-condition: a killed `after_create` is fatal to workspace creation as a failing one already
   is.

6. **`Failure Classes` — the condition.** Ensure `agent_session_failures` names the condition
   alongside `Subprocess exit`: a turn that ended with no terminal signal. Done-condition: the class
   lists the condition an implementation classifies to, and no new class or token is introduced.

7. **Sections 17.5 and 18.1.** Ensure the test matrix checks that a turn whose agent process is
   killed and exits `0` fails the attempt rather than completing it, that a hook terminated by a
   signal is fatal where its failure would be, and that no turn outcome is derived from exit status
   alone. Ensure the checklist carries the evidence rule. Done-condition: each of steps 1, 3 and 5
   has a check that would fail if the step were reverted.

## Cross-cutting sync

Section 6.4's config cheat sheet gains nothing: no configuration key changes. Sections 17 and 18 are
covered by step 7. Section 19's Conformance Statement gains nothing — the rule leaves no
implementation choice to record.

## Anchor changes

None. No token, event, class or configuration key is added, renamed or removed; the decision adds
requirements to existing anchors.

## Status

Applied to `SPEC.md` (Sections 9.4, 10.6, 10.7, 14.1, 17.5, 18.1).
