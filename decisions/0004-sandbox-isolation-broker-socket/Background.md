# Background — 0004 Sandbox isolation and the per-run broker socket

## Context

Today's spec defers sandboxing to "whatever the coding agent and host OS provide" (Non-Goals, Section
2.2; Section 15.1). The broker model (0003) only delivers its security value if the agent actually
runs inside an isolation boundary whose single hole is the broker socket: credentials and the host
live outside, the agent and its working tree live inside, and the per-run socket is the controlled
channel between them. This decision defines that boundary and the socket mechanics.

## Options considered

### Network egress posture

- **Open egress, no creds.** Easy for the agent, weak against exfiltration and injected fetches.
- **Default-deny + allowlist.** Strong, but operators must curate the allowlist (model API,
  registries, docs).
- **Configurable, strict by default (chosen).** The sandbox is REQUIRED and configurable; the assumed
  default profile is a strict containment profile. The reference baseline is `jai`
  (https://jai.scs.stanford.edu) in its `Strict` mode — a Stanford Secure Computer Systems containment
  tool for AI agents on Linux ("Don't YOLO your filesystem!"), with `Casual`/`Strict`/`Bare` modes. On
  non-Linux hosts an equivalent containment mechanism is used. We note jai's own framing that it is a
  "casual sandbox" that reduces rather than eliminates risk, so hardened deployments layer additional
  controls.

### Binding a socket connection to a run (for scope enforcement)

- **Shared socket + run token.** Fewer sockets, but a token becomes a (scoped, non-credential) secret
  inside the sandbox to protect.
- **Shared socket + OS peer identity.** No token, but relies on platform-specific peer-credential
  mechanisms that vary across Linux/macOS/Windows.
- **Per-run socket (chosen).** Each sandbox gets its own socket whose existence binds it to exactly
  one (repo, issue, branch). Unforgeable from inside the sandbox and needs no in-sandbox secret;
  Symphony manages N sockets and mounts the right one into each sandbox.

### Where the agent's commits meet the credentials

- **Separate authoritative clone with a sync step.** Strong remote-config isolation, more machinery.
- **Shared tree, host-side privileged git (chosen).** The working tree is a host directory
  bind-mounted into the sandbox; Symphony runs privileged git (fetch/push) on the host against that
  same tree, with the pushed ref pinned by Symphony. Simplest; the agent may read `.git` but cannot
  authenticate or change which ref is pushed.

## Decision and reasoning

Symphony MUST be able to wrap each agent run in a sandbox; the assumed default is a strict containment
profile (`jai` `Strict` on Linux, an equivalent mechanism elsewhere), and the profile is configurable.
Each run gets a per-run broker socket mounted into the sandbox as the only privileged channel. The
working tree is bind-mounted from the host, and Symphony performs credentialed git on the host against
it. All secret-bearing environment variables are scrubbed before the sandbox starts (the in-sandbox
half of 0003's secret rule).

Problems to watch: a strict egress profile collides with the agent's genuine need to reach its model
API and package registries, so the allowlist is operationally load-bearing and must be documented;
jai is Linux-only and a self-described casual sandbox, so the non-Linux story and any
stronger-isolation needs are implementation-defined; and the shared-tree model means Symphony must
treat agent-side `.git` state as untrusted when it performs network operations.

This decision also obsoletes the existing SSH Worker Extension (Appendix A): remote execution must now
carry the sandbox, per-run socket, and credential-broker boundary to the remote host, which is more
than the appendix specifies. We drop it for now (recorded in Anchor changes) and may reintroduce a
reworked remote-execution extension later.
