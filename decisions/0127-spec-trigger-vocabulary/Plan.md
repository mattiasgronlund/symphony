# Plan — 0127 The section whose job is the vocabulary is the one where a missing member is the failure

## Scope

`SPEC.md`: Section 9.12 "The Action-Policy Machine" (the trigger list and the unmatched-policy
bullet), Section 8.10 "Autonomous Task Management" (who observes a task-state event), Sections 17.4,
18.1.

Depends on decision 0122, which removes the signal trigger kind from the engine.

## Steps

1. **The typed-result bullet names the operations that raise one.** Ensure Section 9.12's list is the
   operations whose results re-enter the machine — `commit`, `integrate`, `push`, `create_pr`,
   `merge`, `pull`, `status`, `diff`, `await_checks` — rather than five of them. Done-condition:
   Section 9.10's instruction to bind `await_checks:*` names a trigger the list contains.

2. **The two exclusions are stated where the list is.** Ensure the bullet states that `provision` and
   `load_policy` raise no `<op>:<reason>` trigger, and why: the edges that would route them are in the
   document they exist to obtain, so a gate on either would be present on one invocation and absent on
   the next. Done-condition: a later reader adding the eleventh and twelfth operations to the list
   finds the reason not to, in place.

3. **The signal clauses go.** Ensure the trigger list carries lifecycle positions and typed operation
   results, and that the unmatched-policy bullet no longer disposes of a signal — decision 0122 having
   removed the kind. Done-condition: the trigger list and the unmatched-policy bullet name the same
   kinds, which is the contradiction issue #75 reports.

4. **Where the milestone tokens live now.** Ensure Section 9.12 states, in one sentence, that an event
   Symphony observes — an agent milestone, a task-state event — selects a tracker transition (Section
   11.6) or an entry point through `[driver]` (Section 8.10), rather than entering the executor.
   Done-condition: a reader who came looking for `ready-for-review` is sent to the section that
   evaluates it rather than left to conclude it was dropped.

5. **`Autonomous Task Management` — who observes.** Ensure Section 8.10's computed-completion bullet
   names the consumer as what observes every implementation task closing and then runs `ship`, rather
   than describing a trigger that "fires". Done-condition: `SPEC.md` and `VCSX-SPEC.md` do not
   disagree about who matches.

6. **Sections 17.4, 18.1.** Ensure the test matrix's action-policy checks assert that a repository
   binding `await_checks:*` and `pull:*` reaches the same matching and `#class` fallback as
   `merge:*`, and that a policy naming a `provision:*` trigger is refused. Ensure the checklist's
   machine bullet names the trigger kinds Section 9.12 defines. Done-condition: steps 1, 2 and 3 each
   have a check.

## Cross-cutting sync

Section 6.4 gains nothing: no configuration key is involved. Section 14.1 gains nothing: no failure
class changes.

`VCSX-SPEC.md` and `VCSX-CONTRACT.md` are decision 0122's; this decision touches neither, and adds no
token either document does not already define.

## Anchor changes

None. Every operation this decision adds to `SPEC.md` Section 9.12's list is one `VCSX-SPEC.md`
Section 4.1 already defines, and the signal tokens it removes are removed by decision 0122, which
records them.

## Status

Applied to `SPEC.md` (Sections 8.10, 9.12, 11.6, 17.4, 18.1) and `conformance/vocabulary.json`.
