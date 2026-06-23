# Plan — 0004 Sandbox isolation and the per-run broker socket

## Scope

New material on agent sandboxing and the broker socket; edits to Non-Goals (Section 2.2) and Security
and Operational Safety (Section 15). Removes Appendix A "SSH Worker Extension". Depends on 0003 (the
broker boundary) and is depended on by 0005 (the sandbox boundary is the config/trust line) and
0006–0009.

## Steps

1. Ensure the spec REQUIRES the ability to wrap each agent run in a sandbox, with a configurable
   profile and a strict-by-default assumption referencing `jai` `Strict` (Linux) and an equivalent
   mechanism on other platforms. Done when a sandbox section states the requirement, the default, and
   cites `jai`.
2. Ensure each run is given a per-run broker socket that is the only privileged channel into the
   sandbox, and that the socket's existence binds the connection to one (repo, issue, branch) for
   scope enforcement. Done when the per-run socket and its identity binding are specified.
3. Ensure the execution model states the working tree is bind-mounted from the host and that Symphony
   runs credentialed git on the host against that tree with a Symphony-pinned pushed ref. Done when
   the shared-tree / host-side-push model is described (refspec details cross-referenced to 0007).
4. Ensure all secret-bearing environment variables are scrubbed before the sandbox starts (the
   in-sandbox half of 0003's secret rule). Done when the scrub requirement appears in the sandbox
   section.
5. Ensure the egress posture is stated as configurable with a strict default and a documented
   allowlist for model API and registries. Done when the egress clause appears.

## Cross-cutting sync

Non-Goals (2.2): drop "Mandating strong sandbox controls beyond what the coding agent and host OS
provide." Test matrix (17) and checklist (18): add sandbox and per-run-socket conformance rows; remove
the Appendix A / SSH-worker rows. Config cheat sheet (6.4): sandbox profile and egress keys land in
policy config (0005).

## Anchor changes

- Appendix A "SSH Worker Extension", `worker.ssh_hosts`, `worker.max_concurrent_agents_per_host` —
  removed (dropped for now; superseded by the sandbox/socket/broker execution model, to be reworked
  later).
- New anchors: Section 9.6 "Agent Sandbox and Execution Isolation", the sandbox profile concept, the
  per-run broker socket, and `jai` `Strict` as the reference default.

## Status

Applied to `SPEC.md` on branch `broker-rearchitecture-0003-0009`.
