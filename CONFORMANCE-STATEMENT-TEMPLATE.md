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
| Identifier the tracker adapter publishes in `assignees` | 4.1.1 | `<which identifier — login / handle / opaque id — and how it distinguishes the tracker's principals under Lowercase Normalization>` |
| Identifier the tracker adapter publishes in `project` and `team` | 4.1.1 | `<which identifier — key / slug / opaque id — and how it distinguishes the tracker's containers under Lowercase Normalization>` |
| `run_id` derivation for a run attempt | 4.1.5 | `<how the value is composed, and how no two run attempts in the deployment share one, including across restarts>` |
| Process identity `run_id` composes from | 16.1 | `<how the value is derived, and how it differs from that of any previous process of the same deployment>` |
| Operator policy config format and discovery path | 5 | `<...>` |
| Workflow/template error classes defined beyond Section 5.5's five | 5.5 | `<token + dispatch gating behavior for each, or none>` |
| Tracker error categories defined beyond Section 11.4's set | 11.4 | `<token + condition for each, or none>` |
| Agent-runner error categories defined beyond Section 10.6's set | 10.6 | `<token + condition for each, or none>` |
| `agent.default_agent` default | 5.3.5 | `<which agent>` |
| `agent.default_effort` default | 5.3.5 | `<native effort value>` |
| Agent sandbox profile | 9.6 | `<jai Strict / container / VM / …>` |
| Effective egress policy for the sandbox and broker socket | 9.6 | `<...>` |
| Composed environment set an agent's run receives | 9.6 | `<the variables passed through, and how a location outside the run's own workspace is kept out>` |
| Carrier by which an issue names its pull-request target | 9.7 | `<label the operator maps / tracker field / tracker-specific / not offered>` |
| Approval, sandbox, and operator-confirmation policy | 10.5 | `<...>` |
| Targeted-protocol user-input-required signal handling | 10.5 | `<...>` |
| Tracker adapter result hard-cap / pagination limitation | 11 | `<cap, or none>` |
| Tracker adapter `metadata` contents | 11 | `<what the adapter places there>` |
| Required-transition-input default-or-fail behavior | 11 | `<documented default, or fail>` |
| Log sink or sinks, and behavior when one of them fails | 13.2 | `<stderr / file / remote sink; and the disposition on sink failure>` |
| Human-readable presentation of rate-limit data | 13.5 | `<how it is presented, or none>` |
| `repository_provisioning_failures` — persistent park-vs-retry | 14.2 | `<park after N / retry indefinitely>` |
| `engine_invocation_failures` — persistent park-vs-retry | 14.2 | `<park after N / retry indefinitely>` |
| `engine_invocation_failures` — unusable-policy per-repository backoff schedule | 14.2 | `<schedule>` |
| Additional failure categories defined by a shipped extension | 14.1 | `<token + recovery disposition for each, or none>` |
| Durable-store degradation when no store is configured | 14.3 | `<decline enforcement / fall back to Ephemeral / …>` |
| `Cached external signal` degradation when no store backs the field | 14.3 | `<what governs decisions until the first reading of a new process arrives>` |
| Secret-redaction mechanism and substituted marker for captured subprocess text | 15.3 | `<known-value replacement + marker; any matching added above the floor>` |
| How it is established that no route beyond the two Section 15.4 closes can write the policy branch | 15.4 | `<branch protection / repository permissions / a mirror the service alone writes>` |
| How a host-side hook's unit is resolved from the policy branch | 15.4 | `<how the unit is addressed; what working directory it is given>` |
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
| Rate-limit aggregation — the sink it aggregates into, and the retention | 13.5 | `<... / n/a>` |
| `<other>` | `<section>` | `<... / n/a>` |

## 5. State Recovery-Class Assignments (Section 14.3)

Section 14.3 requires every Orchestrator Runtime State field (Section 4.1.8) — any state a shipped
extension introduces, and any state Core behavior requires beyond the fields Section 4.1.8
enumerates — to be assigned exactly one recovery class and the assignment documented. The
enumeration is not closed: a park record for either park-versus-retry choice Section 14.2 leaves
open, a counter satisfying the generation non-reuse requirement (Section 8.4), and the process
identity and per-process counter `run_id` composes from (Sections 4.1.5, 16.1),
are Core state this specification creates without listing, and each belongs in the table below if
the implementation holds it. Classes: `Reconstructable`, `Ephemeral`, `Cached external signal`, `Durable`. The
"Spec default" column is the assignment `SPEC.md` states; fill "As implemented" and note any
divergence in Section 7.

Two "Spec default" cells are dual-valued, because `SPEC.md` gives the field one class in Core and
another under a named OPTIONAL extension. A dual-valued cell is not a claim that the implementation
holds both: "As implemented" MUST name **which one of the two this implementation ships**, and a
consumer or generator reading the row takes that cell — never the "Spec default" cell — as the
field's class.

Section 14.3 also requires the **reset consequence** of each `Ephemeral` field to be documented —
what a restart costs, for example that retry backoff restarts from the first attempt. Fill the last
column for every field whose implemented class is `Ephemeral`; leave it `n/a` for the others.

| State field (Section 4.1.8) | Spec default | As implemented | Reset consequence (`Ephemeral`) |
|-----------------------------|--------------|----------------|----------------------------------|
| `poll_interval_ms` | `Reconstructable` | `<...>` | `<n/a>` |
| `max_concurrent_agents` | `Reconstructable` | `<...>` | `<n/a>` |
| `running` | `Reconstructable` | `<...>` | `<n/a>` |
| `claimed` | `Reconstructable` | `<...>` | `<n/a>` |
| `retry_attempts` | `Ephemeral` | `<...>` | `<...>` |
| `completed` | `Ephemeral` | `<...>` | `<...>` |
| `agent_totals` | `Ephemeral` (`Durable` under a budgeting extension) | `<...>` | `<...>` |
| `repository_backoff` | `Ephemeral` | `<...>` | `<...>` |
| `provider_rate_limits` | `Ephemeral` (`Cached external signal` under a provider-quota extension) | `<...>` | `<...>` |
| `<additional state field — Core or extension>` | `<n/a>` | `<class>` | `<... / n/a>` |

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
