# Symphony Conformance Statement — TEMPLATE

Copy this file into your implementation's own repository, rename it (for example
`CONFORMANCE.md`), and fill every `<...>` placeholder and `[ ]` box. This template is a *checklist of
pointers* into `SPEC.md`; it restates no obligation's substance. Where a row cites a section, the
citing document is `SPEC.md` unless another document is named. Section numbers are hints paired with
titles — resolve by title if numbering has shifted (see decision 0002).

The Conformance Statement is the single place an implementation publishes the choices `SPEC.md`
leaves open. It records **contract-visible** choices only — those a consumer, auditor, or peer
implementation can observe. Purely idiomatic choices (concurrency model, error-handling idiom,
libraries, project layout) are *not* recorded here; the contract cannot see them and `SPEC.md` is
silent on them.

---

## 0. Identity and Targeted Revisions

- Implementation name: `<name>`
- Implementation language / runtime: `<language>`
- Maintainer / contact: `<contact>`
- Statement date: `<YYYY-MM-DD>`
- `SPEC.md` revision targeted: `<Status line, e.g. Draft v1>`
- `VCSX-CONTRACT.md` revision targeted: `<revision or commit>`
- `VCSX-SPEC.md` revision targeted: `<revision or commit>`

## 1. Conformance Claim — Profiles and Topology

Name the layer profiles claimed and the deployment topology provided. Vocabulary is owned by Section
3.4 "Layers, the VCS Engine, and Deployment Topologies" and the Section 17 validation profiles; this
Statement only declares the claim.

- Layer profiles claimed:
  - [ ] `Broker Core Conformance`
  - [ ] `Daemon Conformance`
  - Engine conformance is deferred to `VCSX-SPEC.md` Section 13; see the engine pin in Section 3
    below.
- Deployment topology provided (a declared composition of the above):
  - [ ] `engine-direct` — a conforming engine alone
  - [ ] `interactive-agent` — `Broker Core Conformance` + a conforming engine
  - [ ] `daemon` — `Broker Core Conformance` + `Daemon Conformance` + a conforming engine (under the
        remote-operation condition of Section 18.1's VCS Engine group)
- Secret-isolation invariant upheld (REQUIRED; not a choice): [ ] yes. How it is enforced (the
  per-run broker socket, scope guard, and scrubbed environment; Sections 1, 9.6, 10.8, 15.3):
  `<one or two sentences>`

## 2. OPTIONAL Extensions Shipped

Mark each extension shipped or not, with its config namespace (Section 18.2). An unchecked extension
is not part of the conformance claim and its rows in Section 4 below may be marked `n/a`.

| Extension | Section | Shipped | Config namespace |
|-----------|---------|---------|------------------|
| Token budget guards | 8.8 | [ ] | `budget.*` |
| Provider quota backpressure | 8.9 | [ ] | `quota.*` |
| Autonomous task management | 8.10 | [ ] | `[tasks]` / `[driver]` |
| Human-readable status surface | 13.4 | [ ] | `observability.*` |
| Per-execution usage ledger | 13.6 | [ ] | `observability.ledger.*` |
| Node-scheduler remote adapter | 9.11 | [ ] | `compute.*` |
| HTTP status/control server | 13.8 | [ ] | `server.*` |
| Durable state store | 14.3 | [ ] | `<namespace>` |
| `<other>` | `<section>` | [ ] | `<namespace>` |

## 3. Version Pins

- Engine `version_floor` required / validated against (repo-owned in `repo.policy.toml`; the value
  this implementation was validated against and refuses below — `VCSX-SPEC.md` Section 8.5): `<floor>`
- Agent-runner protocol minimum floor advertised/accepted at bring-up (Section 10): `<floor>`
- Bundled or expected engine identity (which engine, and whether bundled or externally pinned;
  Section 3.4, decision 0042): `<engine + how pinned>`

## 4. `Implementation-defined` and `MUST document` Resolutions

One row per obligation `SPEC.md` leaves to the implementation. Core rows MUST be resolved.
Extension rows are `n/a` unless the extension is shipped (Section 2). Fill the resolution column with
the concrete choice; do not leave a core row blank. The rows are pre-enumerated from `SPEC.md` but
are not exhaustive — Section 19 introduces its own list with "including" — so add a row for any
obligation not listed here rather than omitting its resolution.

### 4.1 Core

| Obligation | Section | Resolution |
|------------|---------|------------|
| Operator policy config format and discovery path | 5 | `<...>` |
| Workflow/template error classes defined beyond Section 5.5's five | 5.5 | `<token + dispatch gating behavior for each, or none>` |
| `agent.default_agent` default | 5.3.5 | `<which agent>` |
| `agent.default_effort` default | 5.3.5 | `<native effort value>` |
| Agent sandbox profile | 9.6 | `<jai Strict / container / VM / …>` |
| Effective egress policy for the sandbox and broker socket | 9.6 | `<...>` |
| Approval, sandbox, and operator-confirmation policy | 10.5 | `<...>` |
| Targeted-protocol user-input-required signal handling | 10.5 | `<...>` |
| Tracker adapter result hard-cap / pagination limitation | 11 | `<cap, or none>` |
| Tracker adapter `metadata` contents | 11 | `<what the adapter places there>` |
| Required-transition-input default-or-fail behavior | 11 | `<documented default, or fail>` |
| Log sink or sinks, and behavior when one of them fails | 13.2 | `<stderr / file / remote sink; and the disposition on sink failure>` |
| Human-readable presentation of rate-limit data | 13.5 | `<how it is presented, or none>` |
| Repository Provisioning Failures — persistent park-vs-retry | 14.2 | `<park after N / retry indefinitely>` |
| Engine Invocation Failures — persistent park-vs-retry | 14.2 | `<park after N / retry indefinitely>` |
| Durable-store degradation when no store is configured | 14.3 | `<decline enforcement / fall back to Ephemeral / …>` |
| Secret-redaction mechanism and substituted marker for captured subprocess text | 15.3 | `<known-value replacement + marker; any matching added above the floor>` |
| Object store path location (host-side) | 16.5 | `<path policy, e.g. sibling of workspace root>` |

### 4.2 Extension-scoped (resolve only if shipped)

| Obligation | Section | Resolution |
|------------|---------|------------|
| Quota backpressure — out-of-band usage-poller credential source and refresh subprocess (documented and bounded) | 8.9 | `<... / n/a>` |
| Cost extension — how pricing is sourced and kept current | 8.x | `<... / n/a>` |
| Node-scheduler — node attribute vocabulary (nodes opaque to Symphony) | 9.11 | `<... / n/a>` |
| Node provisioning failures — persistent park-vs-retry | 9.11 | `<... / n/a>` |
| Compute provider — variant catalog, pool sizing, billing | 9.11 | `<... / n/a>` |
| Human-readable status surface — what it is and what it draws from | 13.4 | `<... / n/a>` |
| `<other>` | `<section>` | `<... / n/a>` |

## 5. State Recovery-Class Assignments

Section 14.3 requires every Orchestrator Runtime State field (Section 4.1.8) — and any state a
shipped extension introduces — to be assigned exactly one recovery class and the assignment
documented. Classes: `Reconstructable`, `Ephemeral`, `Cached external signal`, `Durable`. The
"Spec default" column is the assignment `SPEC.md` states; fill "As implemented" and note any
divergence in Section 7.

| State field (Section 4.1.8) | Spec default | As implemented |
|-----------------------------|--------------|----------------|
| `poll_interval_ms` | `Reconstructable` | `<...>` |
| `max_concurrent_agents` | `Reconstructable` | `<...>` |
| `running` | `Reconstructable` | `<...>` |
| `claimed` | `Reconstructable` | `<...>` |
| `retry_attempts` | `Ephemeral` | `<...>` |
| `completed` | `Ephemeral` | `<...>` |
| `agent_totals` | `Ephemeral` (`Durable` under a budgeting extension) | `<...>` |
| `provider_rate_limits` | `Cached external signal` | `<...>` |
| `<extension state field>` | `<n/a>` | `<class>` |

## 6. Trust and Safety Posture

`SPEC.md` (Sections 1, 9.6, 15) requires the trust and safety posture to be documented explicitly.
Summarize it here (the sandbox mechanism, the secret-provider realization, and the
approval/confirmation stance are cross-referenced from Sections 1–4 above; state the overall posture
and the environment it targets).

`<trusted-environment high-trust / stricter-approval / sandboxed — and why>`

## 7. Conformance Evidence and Known Deviations

- Shared conformance corpus (when one exists): [ ] all vectors pass · [ ] partial · vectors/version
  run: `<id>`
- Real Integration Profile (Section 17.8): [ ] run · [ ] skipped · environment: `<...>`
- Known deviations from `SPEC.md` (should be empty for a clean claim; record any divergence with its
  rationale, and open a decision upstream if it reflects a genuine spec gap — decision 0045):
  - `<none, or: field/behavior — divergence — rationale>`
