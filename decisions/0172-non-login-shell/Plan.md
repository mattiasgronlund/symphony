# Plan — 0172 The launch contract mandates what the environment clause forbids

## Scope

`SPEC.md` only: Section 10.1 (Launch Contract), the `command` field of the agent configuration
(Section 5.3.5), Section 9.6 (Agent Sandbox and Execution Isolation) and Section 17.5 (Coding-Agent
Adapters).

Section 9.4 (Workspace Hooks) is deliberately unchanged; see the trigger in `Background.md`.

## Steps

1. **The agent is launched through a non-login shell.** Ensure Section 10.1's invocation line reads
   `bash -c <codex.command>`, so `codex.command` still gets a shell — pipelines, redirections, `&&`
   — without sourcing `/etc/profile`, `/etc/profile.d/*.sh` or the user's profile files.
   Done when Section 10.1 names a non-login shell and `bash -lc` does not appear in it.

2. **Section 10.1 states why**, since a reader who does not know will restore the flag. Ensure the
   notes give both reasons: a profile is free to write to the same stdout the protocol stream is
   parsed from, so a login shell is a framing hazard rather than a convenience; and profile sourcing
   is a construction step running after Symphony's, which re-populates the composed environment
   (Sections 9.6, 10.4).
   Done when Section 10.1 names the stdout reason first and cites Section 9.6.

3. **The `command` field's own note matches.** Ensure the `command` field documentation, which
   restates the invocation, says the runtime launches the command via a non-login shell.
   Done when that bullet no longer says `bash -lc`.

4. **The composed set names what resolves the command.** Ensure Section 9.6's constructed-environment
   bullets require that, where the agent command is resolved by name rather than by absolute path,
   the composed set include the search path that resolves it — the same deliberate naming the
   section already requires of every other location-bearing variable, applied to the one the launch
   contract depends on.
   Done when Section 9.6 states that requirement.

5. **The Core check moves with it.** Ensure Section 17.5's launch check asserts a non-login shell,
   and asserts what the change is for: a profile that writes to stdout does not enter the protocol
   stream, and a profile that assigns a location-bearing variable does not reach the agent.
   Done when Section 17.5 no longer pins `bash -lc` and names both consequences.

## Cross-cutting sync

- **Section 6.4 (Configuration Cheat Sheet)** — verify the `command` entry, if it restates the
  invocation, and bring it with step 3. No key is added, removed or renamed.
- **Section 17** — step 5. **Section 18** — no item names the invocation; confirm and leave.
- **Conformance Statement templates** — no row owed. Section 9.6's composed set is already
  `Implementation-defined` and MUST be documented, and already has its row; step 4 constrains that
  set's content rather than adding a separate obligation. A deployment's search-path choice becomes
  visible through the row that already exists.
- **`VCSX-SPEC.md`** — unaffected. The agent launch is not the engine's.
- **Conformance corpus** — unaffected. A subprocess launch is host-dependent and outside the
  deterministic subset.

## Anchor changes

None. No code-token identifier is renamed or removed and no section is retitled. `bash -lc` is a
literal in prose rather than an anchor, but it is searched for as one, so this plan records that
three of its four occurrences change and the fourth (Section 9.4's hook shell) deliberately does
not.

## Status

Not started.
