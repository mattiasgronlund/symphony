# Background — 0052 `notify` with no consumer that can effect it

## Context

`VCSX-SPEC.md` Section 5.2 splits the action vocabulary by who performs each action: `run_op` and `run`
are the engine's own, while `create_task`, `set_state`, and `notify` "are effected by the consumer,
because they touch systems (a task model, an issue tracker, a notification channel) outside the
VCS/forge domain; the engine emits the intent and the consumer performs it."

A consumer is not obliged to be able to effect any of them. Section 1.3 states plainly that "a consumer
may be a human at an interactive prompt or an automation service", and Section 7.3 makes the task model
something an embedded driver *MAY* run. So the interactive front-end's ordinary consumer — a person —
has no task model, no tracker binding, and no notification channel, and every policy that uses these
actions runs through a consumer that cannot perform them.

The specification resolves that case for two of the three actions, and does so **inconsistently**:

- `create_task` — "a no-op when the consumer runs no task model" (Section 5.2). Resolved, and silent.
- `set_state` — "a `set_state`/transition binding without a consumer that can apply it" is a
  configuration error, caught at validation, and the engine refuses to run (Section 6.10). Resolved,
  and loud.
- `notify` — unresolved. Section 5.2 says only "emit a notification through the consumer", and nothing
  anywhere states what happens when there is no consumer that can deliver it.

Decision 0049 makes the gap live rather than theoretical. It schedules the `engine-direct` topology
first, per 0042 — and `engine-direct` is precisely the deployment "run directly by an operator who
holds the credentials" (`SPEC.md` Section 3.4). The first thing built therefore runs every policy
through the least capable consumer the specification admits.

The asymmetry between the two resolved actions is worth reading before adding a third, because it is
coherent rather than accidental. A dropped `set_state` strands control flow: a workflow state never
advances, and the omission is invisible to everyone. A task model is explicitly optional to the driver,
so a policy creating tasks against a consumer without one is a degradation rather than a break.
`notify` sits with `create_task`: a missed notification is observability, not control flow.

What is missing is therefore narrow — a statement for `notify`, and a rule about whether a no-op is
reported. Section 5.4 already fixes the analogous question one level down, for operation outcomes: an
unmatched outcome "MUST NOT be silently dropped, because a dropped operation outcome would strand a
flow." An intent the engine emitted and no consumer performed is the same hazard one level up.

## Options considered

- **Option A — `notify` is a benign no-op that MUST be surfaced (chosen).** Name the
  consumer-that-cannot-effect-it case explicitly, classify `notify` with `create_task` as a benign
  no-op, and require both no-op intents to be reported in the result envelope rather than dropped.
  Trade-offs: the smallest edit that closes the gap; keeps the existing per-action split, which is
  coherent; and adopts Section 5.4's established anti-dropping principle rather than inventing one.
  It does not make the three actions uniform, so a reader must still consult each.
- **Option B — uniform intent emission.** The engine always emits every consumer-effected intent into
  the envelope in every front-end, and a consumer that cannot effect one simply performs none.
  Trade-offs: the most uniform model, and it makes the executor's behavior provably identical across
  front-ends. But it is a larger Section 8.2 change, it alters what a *capable* consumer receives as
  well, and it would put `set_state` on the emission path in tension with Section 6.10's existing
  refusal to run at all.
- **Option C — every consumer-effected action without a consumer is a configuration error.** Align
  `notify` and `create_task` with `set_state`. Trade-offs: strictest and most deterministic — no
  policy silently degrades. But it directly contradicts Section 5.2's existing "a no-op when the
  consumer runs no task model", so it is a change to settled behavior rather than a gap-filling, and it
  would make a policy that legitimately degrades on a lesser consumer refuse to run instead.

## Decision and reasoning

Choose **Option A**.

`notify` is classified where its failure mode puts it. Losing a notification costs observability;
losing a `set_state` strands a workflow. The specification already draws that line, and `notify` falls
on the `create_task` side of it, so the resolution is to state the existing logic rather than to
introduce a new rule.

The surfacing requirement is the part that is genuinely added, and it is imported rather than invented:
Section 5.4 already forbids silently dropping an unmatched operation outcome, on the grounds that a
dropped outcome strands a flow. An emitted intent that no consumer performed is the same failure with
the same remedy — report it. Surfacing is extended to `create_task` as well as `notify`, because
special-casing `notify` would leave exactly the same silent-drop hazard in place for the other no-op
action, for no reason a reader could reconstruct. `set_state` never reaches this path: Section 6.10
catches it at validation.

The intents are reported in the result envelope under `outputs`, in a named key rather than as an
`Implementation-defined` representation. Pinning the key avoids adding a sixth `Implementation-defined`
site to a specification whose whole surface is five, makes the requirement mechanically checkable, and
follows how Section 8.2 already names `outputs` sub-structures by example.

**This does not create a second point of front-end divergence.** Section 5.5 says `escalate` "is the
single point at which their behavior legitimately differs", and that stays true: the *engine's*
behavior here is identical in both front-ends — it emits the intent and records that nothing performed
it. What varies is the consumer's capability, which is not the engine's behavior. `escalate` remains
the only place the engine itself branches on which front-end is running.

We would reconsider if a further consumer-effected action were added whose omission strands control
flow the way `set_state`'s does; such an action belongs with `set_state` at validation, not with the
surfaced no-ops. We would also reconsider if a consumer emerged that can effect some intents but not
others dynamically rather than statically, since Section 6.10's validation-time check assumes the
capability is known before the policy runs.

The decision is **Accepted** and applied to `VCSX-SPEC.md` (Sections 5.2, 8.2). No `VCSX-CONTRACT.md`
edit is required: Section 11 of that document defers "the engine invocation contract (result envelope,
exit codes, escalation payload)" to `VCSX-SPEC.md` Section 8, and no shared token is added, renamed, or
removed. Depends on 0049 (which made the gap live); relates to 0030 (the action-policy machine) and
0042 (the `engine-direct`-first sequencing that surfaces it).
