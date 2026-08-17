# Plan — 0117 The sandbox is stated over secrets, and the damage came from something else

## Scope

`SPEC.md`: Section 9.6 "Agent Sandbox and Execution Isolation" (a constructed environment), Sections
17.2, 18.1, 19.

## Steps

1. **`Agent Sandbox` — the environment is constructed.** Ensure Section 9.6 states that the agent's
   environment is composed from what the run needs rather than inherited wholesale from the
   orchestrator's process, and that variables the deployment intends are passed explicitly.
   Done-condition: a reader can tell that inheritance is the thing being replaced.

2. **`Agent Sandbox` — the prohibited class.** Ensure the text prohibits variables naming a location
   **outside the run's own workspace** — build output directory, cache root, toolchain or
   interpreter path, temporary directory — from reaching the run unless the deployment named them
   deliberately, and states the prohibition over what a variable *names* rather than over a list of
   names, because a list is per-ecosystem and obsolete before it is complete. Done-condition: an
   implementer can write the test (poison one such variable, assert the agent does not see it).

3. **`Agent Sandbox` — where such a location resolves.** Ensure the text states that where a run
   needs one it resolves inside the run's workspace (Section 9.1), so two concurrent runs cannot
   name the same one. Done-condition: the requirement says what to do, not only what to forbid.

4. **`Agent Sandbox` — the delegation.** Ensure the composed set is `Implementation-defined` and MUST
   be documented, the disposition the sandbox profile and egress policy already have.
   Done-condition: the obligation joins the ones Section 19 already collects.

5. **`Agent Sandbox` — why this is not a containment failure.** Ensure the text states that an
   inherited build-output variable is not a sandbox escape — the variable was legitimately
   inherited, the path legitimately reachable — so what the clause fixes is the environment's
   construction rather than the sandbox's strength. Done-condition: a reader does not expect a
   stronger containment profile to satisfy this.

6. **Sections 17.2, 18.1, 19.** Ensure the test matrix checks that a variable naming a location
   outside the workspace does not reach the agent; that a run needing such a location gets one
   inside its workspace; that the checklist carries the constructed environment; and that Section 19
   records the composed set. Done-condition: step 2 has a check that would fail if the step were
   reverted.

## Cross-cutting sync

Section 6.4's cheat sheet gains nothing — the composed set is documented rather than configured by a
key this specification names. Sections 17, 18 and 19 are covered by step 6.

## Anchor changes

None. No token or configuration key is added, renamed or removed.

## Status

Applied to `SPEC.md` (Sections 9.6, 17.2, 18.1, 19).
