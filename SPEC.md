# Symphony Service Specification

Status: Draft v1 (language-agnostic)

Purpose: Define a service that orchestrates coding agents to get project work done.

## Normative Language

The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`, `SHOULD NOT`, `RECOMMENDED`, `MAY`, and
`OPTIONAL` in this document are to be interpreted as described in RFC 2119.

`Implementation-defined` means the behavior is part of the implementation contract, but this
specification does not prescribe one universal policy. Implementations MUST document the selected
behavior.

## 1. Problem Statement

Symphony is a long-running automation service that continuously reads work from an issue tracker
(at least Linear and Forgejo), creates an isolated workspace for each issue, and runs a coding agent
session for that issue inside the workspace.

The service solves four operational problems:

- It turns issue execution into a repeatable daemon workflow instead of manual scripts.
- It isolates agent execution in per-issue workspaces so agent commands run only inside per-issue
  workspace directories.
- It keeps the workflow policy in-repo (`WORKFLOW.md`) so teams version the agent prompt and runtime
  settings with their code.
- It provides enough observability to operate and debug multiple concurrent agent runs.

Implementations are expected to document their trust and safety posture explicitly. This
specification does not require a single approval, sandbox, or operator-confirmation policy; some
implementations target trusted environments with a high-trust configuration, while others require
stricter approvals or sandboxing.

Important boundary:

- Symphony is a privileged broker: it performs all outward side effects (VCS remote operations,
  pull-request creation, and issue-tracker interaction) on the agent's behalf, holding the
  credentials those operations require.
- The coding agent runs sandboxed and credential-less. It supplies only the content of those
  operations (commit and pull-request text, comments, milestone signals) and requests them through a
  `symphony` broker CLI rather than acting on credentials directly.
- A successful run can end at a workflow-defined handoff state (for example `Human Review`), not
  necessarily `Done`.

## 2. Goals and Non-Goals

### 2.1 Goals

- Poll the issue tracker on a fixed cadence and dispatch work with bounded concurrency.
- Maintain a single authoritative orchestrator state for dispatch, retries, and reconciliation.
- Create deterministic per-issue workspaces and preserve them across runs.
- Run each coding-agent session inside a configurable sandbox so credentials and the host stay
  outside the agent's reach.
- Stop active runs when issue state changes make them ineligible.
- Recover from transient failures with exponential backoff.
- Load runtime behavior from a repository-owned `WORKFLOW.md` contract.
- Expose operator-visible observability (at minimum structured logs).
- Support tracker/filesystem-driven restart recovery without requiring a persistent database; exact
  in-memory scheduler state is not restored.

### 2.2 Non-Goals

- Rich web UI or multi-tenant control plane.
- Prescribing a specific dashboard or terminal UI implementation.
- General-purpose workflow engine or distributed job scheduler.
- Built-in product logic for *what* to write in tickets, PRs, or comments. Symphony brokers those
  operations and enforces authorization scope; the content is supplied by the agent and the workflow
  prompt.
- Mandating a single default approval, sandbox, or operator-confirmation posture for all
  implementations (the sandbox is REQUIRED but its profile is configurable; see Section 9.6).

## 3. System Overview

### 3.1 Main Components

1. `Workflow Loader`
   - Reads `WORKFLOW.md`.
   - Parses YAML front matter and prompt body.
   - Returns `{config, prompt_template}`.

2. `Config Layer`
   - Exposes typed getters for workflow config values.
   - Applies defaults and environment variable indirection.
   - Performs validation used by the orchestrator before dispatch.

3. `Issue Tracker Client`
   - Fetches candidate issues in active states.
   - Fetches current states for specific issue IDs (reconciliation).
   - Fetches terminal-state issues during startup cleanup.
   - Normalizes tracker payloads into a stable issue model.

4. `Orchestrator`
   - Owns the poll tick.
   - Owns the in-memory runtime state.
   - Decides which issues to dispatch, retry, stop, or release.
   - Tracks session metrics and retry queue state.

5. `Workspace Manager`
   - Maps issue identifiers to workspace paths.
   - Ensures per-issue workspace directories exist.
   - Runs workspace lifecycle hooks.
   - Cleans workspaces for terminal issues.

6. `Agent Runner`
   - Creates workspace.
   - Builds prompt from issue + workflow template.
   - Launches the coding agent app-server client.
   - Streams agent updates back to the orchestrator.

7. `Privileged Operation Broker`
   - Exposes the `symphony` CLI to the sandboxed agent over a per-run socket.
   - Performs VCS remote, pull-request, and issue-tracker operations using credentials the agent
     never sees.
   - Enforces per-run authorization scope on every brokered operation.

8. `Status Surface` (OPTIONAL)
   - Presents human-readable runtime status (for example terminal output, dashboard, or other
     operator-facing view).

9. `Logging`
   - Emits structured runtime logs to one or more configured sinks.

### 3.2 Abstraction Levels

Symphony is easiest to port when kept in these layers:

1. `Policy Layer` (repo-defined)
   - `WORKFLOW.md` prompt body.
   - Team-specific rules for ticket handling, validation, and handoff.

2. `Configuration Layer` (typed getters)
   - Parses front matter into typed runtime settings.
   - Handles defaults, environment tokens, and path normalization.

3. `Coordination Layer` (orchestrator)
   - Polling loop, issue eligibility, concurrency, retries, reconciliation.

4. `Execution Layer` (workspace + agent subprocess)
   - Filesystem lifecycle, workspace preparation, coding-agent protocol.

5. `Integration Layer` (Linear adapter)
   - API calls and normalization for tracker data.

6. `Observability Layer` (logs + OPTIONAL status surface)
   - Operator visibility into orchestrator and agent behavior.

### 3.3 External Dependencies

- Issue tracker API (at least Linear and Forgejo; selected by `tracker.kind`).
- Local filesystem for workspaces and logs.
- Git CLI and a VCS host API (GitHub or Forgejo) for repository provisioning, push, and pull
  requests.
- A supported coding agent (for example Codex or Claude Code) and its adapter (Section 10.9).
- Agent sandbox mechanism (for example `jai` on Linux, https://jai.scs.stanford.edu, or an
  equivalent on other platforms).
- Host environment authentication for the issue tracker and coding agent.

## 4. Core Domain Model

### 4.1 Entities

#### 4.1.1 Issue

Normalized issue record used by orchestration, prompt rendering, and observability output.

Fields:

- `id` (string)
  - Stable tracker-internal ID.
- `identifier` (string)
  - Human-readable ticket key (example: `ABC-123`).
- `title` (string)
- `description` (string or null)
- `priority` (integer or null)
  - Lower numbers are higher priority in dispatch sorting.
- `state` (string)
  - Current tracker state name.
- `branch_name` (string or null)
  - Tracker-provided branch metadata if available. OPTIONAL and tracker-dependent: an adapter whose
    tracker has no native branch metadata leaves it null or MAY synthesize one.
- `url` (string or null)
- `labels` (list of strings)
  - Normalized to lowercase.
- `blocked_by` (list of blocker refs)
  - OPTIONAL and tracker-dependent: an adapter whose tracker has no dependency model leaves it
    empty, and blocker-gated dispatch (Section 8.2) then observes no blockers.
  - Each blocker ref contains:
    - `id` (string or null)
    - `identifier` (string or null)
    - `state` (string or null)
- `created_at` (timestamp or null)
- `updated_at` (timestamp or null)
- `metadata` (map)
  - Opaque, adapter-owned key/value pairs carrying tracker-specific data the fields above do not
    capture (for example Jira custom fields or board columns); empty when the adapter has none. The
    orchestrator core does not interpret it. An adapter MAY use it to round-trip a provider write
    handle (for example a GitHub Projects v2 item id) instead of re-resolving it per write.

#### 4.1.2 Workflow Definition

Parsed `WORKFLOW.md` payload:

- `config` (map)
  - YAML front matter root object.
- `prompt_template` (string)
  - Markdown body after front matter, trimmed.

#### 4.1.3 Service Config (Typed View)

Typed runtime values derived from `WorkflowDefinition.config` plus environment resolution.

Examples:

- poll interval
- workspace root
- active and terminal issue states
- concurrency limits
- coding-agent executable/args/timeouts
- workspace hooks

#### 4.1.4 Workspace

Filesystem workspace assigned to one issue identifier.

Fields (logical):

- `path` (absolute workspace path)
- `workspace_key` (sanitized issue identifier)
- `created_now` (boolean, used to gate `after_create` hook)

#### 4.1.5 Run Attempt

One execution attempt for one issue.

Fields (logical):

- `issue_id`
- `issue_identifier`
- `attempt` (integer or null, `null` for first run, `>=1` for retries/continuation)
- `workspace_path`
- `started_at`
- `status`
- `error` (OPTIONAL)

#### 4.1.6 Live Session (Agent Session Metadata)

State tracked while a coding-agent subprocess is running. These are the neutral logical fields each
agent adapter normalizes its own protocol's session, turn, and usage identifiers into (Section
10.9). The `thread_id` / `turn_id` shapes shown are the Codex adapter's session identity (Section
4.2); another adapter supplies its own.

Fields:

- `session_id` (string, `<thread_id>-<turn_id>`)
- `thread_id` (string)
- `turn_id` (string)
- `pid` (string or null)
- `last_event` (string/enum or null)
- `last_timestamp` (timestamp or null)
- `last_message` (summarized payload)
- `input_tokens` (integer)
- `output_tokens` (integer)
- `total_tokens` (integer)
- `last_reported_input_tokens` (integer)
- `last_reported_output_tokens` (integer)
- `last_reported_total_tokens` (integer)
- `turn_count` (integer)
  - Number of coding-agent turns started within the current worker lifetime.

#### 4.1.7 Retry Entry

Scheduled retry state for an issue.

Fields:

- `issue_id`
- `identifier` (best-effort human ID for status surfaces/logs)
- `attempt` (integer, 1-based for retry queue)
- `due_at_ms` (monotonic clock timestamp)
- `timer_handle` (runtime-specific timer reference)
- `error` (string or null)

#### 4.1.8 Orchestrator Runtime State

Single authoritative runtime state owned by the orchestrator, held in memory. Each field has a
recovery class (Section 14.3) that governs its behavior across a process restart; class `Durable`
fields MAY additionally be backed by a durable store.

Fields (with recovery class):

- `poll_interval_ms` (current effective poll interval) — `Reconstructable` (re-read from config).
- `max_concurrent_agents` (current effective global concurrency limit) — `Reconstructable` (re-read
  from config).
- `running` (map `issue_id -> running entry`) — `Reconstructable` (rebuilt from tracker state and
  workspaces during reconciliation).
- `claimed` (set of issue IDs reserved/running/retrying) — `Reconstructable` (re-derived from
  `running` and `retry_attempts`).
- `retry_attempts` (map `issue_id -> RetryEntry`) — `Ephemeral` (timers are not restored; backoff
  restarts from the first attempt).
- `completed` (set of issue IDs; bookkeeping only, not dispatch gating) — `Ephemeral` (re-derived as
  empty; loss is harmless).
- `agent_totals` (aggregate tokens + runtime seconds) — `Ephemeral` for observability (resets to
  zero); becomes `Durable` when a budgeting extension enforces on it, and then MUST be
  Symphony-attributed rather than account-wide.
- `provider_rate_limits` (latest rate-limit snapshot from agent events) — `Cached external signal`;
  an absent value denotes `UNKNOWN` (distinct from any reading; in particular not `0`), and the
  policy on `UNKNOWN` is defined by the consuming provider-quota extension.

### 4.2 Stable Identifiers and Normalization Rules

- `Issue ID`
  - Use for tracker lookups and internal map keys.
- `Issue Identifier`
  - Use for human-readable logs and workspace naming.
- `Workspace Key`
  - Derive from `issue.identifier` by replacing any character not in `[A-Za-z0-9._-]` with `_`.
  - Use the sanitized value for the workspace directory name.
- `Normalized Issue State`
  - Compare states after `lowercase`.
- `Session ID`
  - Compose from the agent adapter's thread and turn identifiers. The Codex adapter composes them as
    `<thread_id>-<turn_id>`.

## 5. Configuration Contracts

Symphony reads configuration from two artifacts split on the sandbox boundary (Section 9.6):

- `WORKFLOW.md` — repository-owned and version-controlled. It contains only settings used *inside*
  the agent sandbox: the per-issue prompt template and in-sandbox hooks. Because anyone who can
  commit to the repository — including the agent — can edit it, it is treated as untrusted input and
  MUST NOT carry credentials, scope rules, or any setting Symphony uses outside the sandbox.
- Policy config — operator-owned and not modifiable by the repository or the agent. It contains
  everything Symphony uses outside the sandbox: credentials, authorization scope, the sandbox
  profile, tracker and VCS configuration, polling and concurrency, privileged setup hooks, agent
  selection, and the workflow state-machine. Its format and discovery path are
  `Implementation-defined` and MUST be documented. A single policy config MAY define multiple
  repositories managed by one instance, each with its own VCS and agent settings, plus the
  issue→repo routing for shared tracker polling (Section 8.7).

The dividing rule is mechanical: if Symphony uses a setting outside the sandbox, it belongs to the
policy config; only settings consumed inside the sandbox belong to `WORKFLOW.md`.

### 5.1 WORKFLOW.md Discovery and Path Resolution

Workflow file path precedence:

1. Explicit application/runtime setting (set by CLI startup path).
2. Default: `WORKFLOW.md` in the current process working directory.

Loader behavior:

- If the file cannot be read, return `missing_workflow_file` error.
- The workflow file is expected to be repository-owned and version-controlled.

### 5.2 File Format

`WORKFLOW.md` is a Markdown file with OPTIONAL YAML front matter.

Design note:

- `WORKFLOW.md` SHOULD contain only what the agent needs inside the sandbox: the prompt template and
  in-sandbox hooks. Privileged and orchestration settings (tracker, VCS, polling, concurrency, agent
  selection, sandbox profile, scope, state-machine) live in the operator-owned policy config, not in
  `WORKFLOW.md`.

Parsing rules:

- If file starts with `---`, parse lines until the next `---` as YAML front matter.
- Remaining lines become the prompt body.
- If front matter is absent, treat the entire file as prompt body and use an empty config map.
- YAML front matter MUST decode to a map/object; non-map YAML is an error.
- Prompt body is trimmed before use.

Returned workflow object:

- `config`: front matter root object (not nested under a `config` key).
- `prompt_template`: trimmed Markdown body.

### 5.3 Configuration Schema

This section documents the configuration keys. With the exception of in-sandbox `hooks` (Section
5.3.4), every key below belongs to the operator-owned policy config, because Symphony consumes it
outside the sandbox. `WORKFLOW.md` front matter carries only in-sandbox settings.

Top-level keys (policy config unless noted):

- `tracker`
- `polling`
- `workspace`
- `hooks` (split: policy-config setup hooks and in-sandbox `WORKFLOW.md` hooks; see Section 5.3.4)
- `agent`
- `codex`

Unknown keys SHOULD be ignored for forward compatibility.

Note:

- The configuration is extensible. Extensions MAY define additional top-level keys without changing
  the core schema above.
- Extensions SHOULD document their field schema, defaults, validation rules, whether they belong to
  the policy config or `WORKFLOW.md`, and whether changes apply dynamically or require restart.

#### 5.3.1 `tracker` (object)

Fields:

- `kind` (string)
  - REQUIRED for dispatch.
  - Supported values: `linear`, `forgejo`.
- `endpoint` (string)
  - Default for `tracker.kind == "linear"`: `https://api.linear.app/graphql`. The `forgejo` adapter
    uses the configured Forgejo instance API base.
- `api_key` (string)
  - Resolved through the secret-provider interface (Section 15.3); a file provider is REQUIRED.
  - Environment variables MUST NOT be used as a secret channel into the agent. `$VAR_NAME`
    indirection is not used for this value.
  - If the resolved secret is empty, treat the key as missing.
- `project_slug` (string)
  - REQUIRED for dispatch when `tracker.kind == "linear"`.
- `required_labels` (list of strings)
  - Default: `[]`.
  - An issue MUST contain every configured label to dispatch or continue.
  - Matching ignores case and surrounding whitespace.
  - A blank configured label matches no issue.
- `active_states` (list of strings)
  - Default: `Todo`, `In Progress`
- `terminal_states` (list of strings)
  - Default: `Closed`, `Cancelled`, `Canceled`, `Duplicate`, `Done`
- `transitions` (list of `{from, on, to}` entries)
  - The workflow state-machine (Section 11.6): a directed graph over tracker workflow-state names.
    Each entry transitions an issue from state `from` to state `to` when trigger `on` fires — an
    agent milestone signal or an observed run outcome (Section 11.6).
  - Default: `[]` (no policy-driven transitions).

#### 5.3.2 `polling` (object)

Fields:

- `interval_ms` (integer)
  - Default: `30000`
  - Changes SHOULD be re-applied at runtime and affect future tick scheduling without restart.

#### 5.3.3 `workspace` (object)

Fields:

- `root` (path string or `$VAR`)
  - Default: `<system-temp>/symphony_workspaces`
  - `~` is expanded.
  - Relative paths are resolved relative to the directory containing the policy config.
  - The effective workspace root is normalized to an absolute path before use.

#### 5.3.4 `hooks` (object)

Hooks exist at two trust levels, distinguished by where they run:

- Policy-config hooks run on the host, outside the sandbox, and are trusted. They are for privileged
  setup that needs host access (for example dependency bootstrap that reaches credentialed mirrors).
- `WORKFLOW.md` hooks run inside the sandbox, without credentials, and are untrusted. They are for
  in-sandbox build/test/workspace preparation.

Both sets share the same lifecycle points. A lifecycle point MAY be defined in either artifact; when
both define it, the policy-config hook runs on the host and the `WORKFLOW.md` hook runs inside the
sandbox.

Fields:

- `after_create` (multiline shell script string, OPTIONAL)
  - Runs only when a workspace directory is newly created.
  - Failure aborts workspace creation.
- `before_run` (multiline shell script string, OPTIONAL)
  - Runs before each agent attempt after workspace preparation and before launching the coding
    agent.
  - Failure aborts the current attempt.
- `after_run` (multiline shell script string, OPTIONAL)
  - Runs after each agent attempt (success, failure, timeout, or cancellation) once the workspace
    exists.
  - Failure is logged but ignored.
- `before_remove` (multiline shell script string, OPTIONAL)
  - Runs before workspace deletion if the directory exists.
  - Failure is logged but ignored; cleanup still proceeds.
- `timeout_ms` (integer, OPTIONAL)
  - Default: `60000`
  - Applies to all workspace hooks.
  - Invalid values fail configuration validation.
  - Changes SHOULD be re-applied at runtime for future hook executions.

#### 5.3.5 `agent` (object)

Fields:

- `default_agent` (string)
  - The agent adapter used for the repository. Supported values: `codex`, `claude_code`.
  - Default: `Implementation-defined`.
- `default_effort` (adapter-native value)
  - Passed through to the selected agent as its native effort/reasoning value (Section 10.9).
  - Default: `Implementation-defined`.
- `agent_by_label` (map `label -> {agent, effort}`)
  - Per-issue override of `default_agent`/`default_effort`, keyed by tracker label.
  - Only mapped labels take effect; unmapped labels are ignored.
  - Default: empty map.
- `max_concurrent_agents` (integer)
  - Default: `10`
  - Changes SHOULD be re-applied at runtime and affect subsequent dispatch decisions.
- `max_turns` (positive integer)
  - Default: `20`
  - Limits the number of coding-agent turns within one worker session.
  - Bounds turns (orchestration-initiated prompt cycles, Section 10.3), not the agent's internal
    tool-call steps within a turn.
  - Invalid values fail configuration validation.
- `max_retry_backoff_ms` (integer)
  - Default: `300000` (5 minutes)
  - Changes SHOULD be re-applied at runtime and affect future retry scheduling.
- `max_concurrent_agents_by_state` (map `state_name -> positive integer`)
  - Default: empty map.
  - State keys are normalized (`lowercase`) for lookup.
  - Invalid entries (non-positive or non-numeric) are ignored.

#### 5.3.6 `codex` (object — Codex adapter)

This block configures the `codex` adapter. Each agent adapter owns its own configuration block; the
adapter selected by `agent.default_agent` reads the block named for it.

Fields:

For Codex-owned config values such as `approval_policy`, `thread_sandbox`, and
`turn_sandbox_policy`, supported values are defined by the targeted Codex app-server version.
Implementors SHOULD treat them as pass-through Codex config values rather than relying on a
hand-maintained enum in this spec. To inspect the installed Codex schema, run
`codex app-server generate-json-schema --out <dir>` and inspect the relevant definitions referenced
by `v2/ThreadStartParams.json` and `v2/TurnStartParams.json`. Implementations MAY validate these
fields locally if they want stricter startup checks.

- `command` (string shell command)
  - Default: `codex app-server`
  - The runtime launches this command via `bash -lc` in the workspace directory.
  - The launched process MUST speak a compatible app-server protocol over stdio.
- `approval_policy` (Codex `AskForApproval` value)
  - Default: implementation-defined.
- `thread_sandbox` (Codex `SandboxMode` value)
  - Default: implementation-defined.
- `turn_sandbox_policy` (Codex `SandboxPolicy` value)
  - Default: implementation-defined.
- `turn_timeout_ms` (integer)
  - Default: `3600000` (1 hour)
- `read_timeout_ms` (integer)
  - Default: `5000`
- `stall_timeout_ms` (integer)
  - Default: `300000` (5 minutes)
  - If `<= 0`, stall detection is disabled.

### 5.4 Prompt Template Contract

The Markdown body of `WORKFLOW.md` is the per-issue prompt template.

Rendering requirements:

- Use a strict template engine (Liquid-compatible semantics are sufficient).
- Unknown variables MUST fail rendering.
- Unknown filters MUST fail rendering.

Template input variables:

- `issue` (object)
  - Includes all normalized issue fields, including labels and blockers.
- `attempt` (integer or null)
  - `null`/absent on first attempt.
  - Integer on retry or continuation run.

Fallback prompt behavior:

- If the workflow prompt body is empty, the runtime MAY use a minimal default prompt
  (`You are working on an issue from the issue tracker.`).
- Workflow file read/parse failures are configuration/validation errors and SHOULD NOT silently fall
  back to a prompt.

Prompt authority:

- The prompt template advises the agent and tells it how to signal progress; it does not perform
  privileged operations and MUST NOT be relied on to enforce them. Commits, branch pushes,
  pull-request creation, and tracker transitions occur only through the broker (Section 10.8) and
  the policy-owned state-machine (Section 11.6) — never because the prompt instructs the agent.
- Because `WORKFLOW.md` is repository-owned and untrusted (Section 5.2), prompt text that directs a
  privileged side effect is a request, not an authorization: the broker still scopes every
  operation to the run's repository, issue, and work branch, and an instruction the agent cannot
  satisfy through the broker has no effect.
- The prompt SHOULD describe how the agent expresses intent — when to emit which milestone signal
  (Section 11.6) — rather than which tracker transitions to perform. Operators, not repositories,
  own the resulting transitions.

### 5.5 Workflow Validation and Error Surface

Error classes:

- `missing_workflow_file`
- `workflow_parse_error`
- `workflow_front_matter_not_a_map`
- `template_parse_error` (during prompt rendering)
- `template_render_error` (unknown variable/filter, invalid interpolation)

Dispatch gating behavior:

- Workflow file read/YAML errors block new dispatches until fixed.
- Template errors fail only the affected run attempt.

## 6. Configuration Specification

### 6.1 Configuration Resolution Pipeline

Configuration is resolved in this order:

1. Load the operator policy config and select the `WORKFLOW.md` path (explicit runtime setting,
   otherwise cwd default).
2. Parse the policy config and the `WORKFLOW.md` front matter into raw config maps.
3. Apply built-in defaults for missing OPTIONAL fields.
4. Resolve secrets through the secret-provider interface, and `$VAR_NAME` indirection for non-secret
   path values that explicitly contain `$VAR_NAME`.
5. Coerce and validate typed values.

Environment variables do not globally override YAML values. They are used only when a config value
explicitly references them.

Secret values are not resolved through `$VAR_NAME` indirection; they use the secret-provider
interface (Section 15.3). `$VAR` expansion applies only to non-secret path values.

Value coercion semantics:

- Path/command fields support:
  - `~` home expansion
  - `$VAR` expansion for env-backed path values
  - Apply expansion only to values intended to be local filesystem paths; do not rewrite URIs or
    arbitrary shell command strings.
- Relative `workspace.root` values resolve relative to the directory containing the policy config.

### 6.2 Dynamic Reload Semantics

Dynamic reload is REQUIRED:

- The software MUST detect changes to both configuration artifacts: `WORKFLOW.md` and the policy
  config.
- On change, it MUST re-read and re-apply the affected configuration and prompt template without
  restart. Live policy-config reload includes credentials, scope, and the workflow state-machine;
  implementations SHOULD apply such changes to future operations rather than disrupting in-flight
  runs.
- The software MUST attempt to adjust live behavior to the new config (for example polling
  cadence, concurrency limits, active/terminal states, codex settings, workspace paths/hooks, and
  prompt content for future runs).
- Reloaded config applies to future dispatch, retry scheduling, reconciliation decisions, hook
  execution, and agent launches.
- Implementations are not REQUIRED to restart in-flight agent sessions automatically when config
  changes.
- Extensions that manage their own listeners/resources (for example an HTTP server port change) MAY
  require restart unless the implementation explicitly supports live rebind.
- Implementations SHOULD also re-validate/reload defensively during runtime operations (for example
  before dispatch) in case filesystem watch events are missed.
- Invalid reloads MUST NOT crash the service; keep operating with the last known good effective
  configuration and emit an operator-visible error.

### 6.3 Dispatch Preflight Validation

This validation is a scheduler preflight run before attempting to dispatch new work. It validates
the workflow/config needed to poll and launch workers, not a full audit of all possible workflow
behavior.

Startup validation:

- Validate configuration before starting the scheduling loop.
- If startup validation fails, fail startup and emit an operator-visible error.

Per-tick dispatch validation:

- Re-validate before each dispatch cycle.
- If validation fails, skip dispatch for that tick, keep reconciliation active, and emit an
  operator-visible error.

Validation checks:

- Workflow file can be loaded and parsed.
- `tracker.kind` is present and supported.
- `tracker.api_key` is present after `$` resolution.
- `tracker.project_slug` is present when REQUIRED by the selected tracker kind.
- When `tracker.transitions` is non-empty, the selected tracker adapter declares the `set_state`
  capability (Section 11.7); otherwise configuration error.
- `codex.command` is present and non-empty.

### 6.4 Core Config Fields Summary (Cheat Sheet)

This section is intentionally redundant so a coding agent can implement the config layer quickly.
Extension fields are documented in the extension section that defines them. Core conformance does
not require recognizing or validating extension fields unless that extension is implemented.

Unless a field is marked as in-sandbox (`WORKFLOW.md`), it lives in the operator-owned policy config
(Section 5). A policy config MAY define multiple repositories, each with its own `vcs` and `agent`
settings, plus a tracker-specific issue→repo mapping (Section 8.7).

- `tracker.kind`: string, REQUIRED, `linear` | `forgejo`
- `tracker.endpoint`: string, default `https://api.linear.app/graphql` when `tracker.kind=linear`
- `tracker.api_key`: resolved via the secret-provider interface (file provider REQUIRED), not via `$VAR`/env (Section 15.3)
- `tracker.project_slug`: string, REQUIRED when `tracker.kind=linear`
- `tracker.required_labels`: list of strings, default `[]`
- `tracker.active_states`: list of strings, default `["Todo", "In Progress"]`
- `tracker.terminal_states`: list of strings, default `["Closed", "Cancelled", "Canceled", "Duplicate", "Done"]`
- `tracker.transitions`: list of `{from, on, to}` entries, default `[]` (workflow state-machine, Section 11.6)
- `polling.interval_ms`: integer, default `30000`
- `workspace.root`: path resolved to absolute, default `<system-temp>/symphony_workspaces`
- `vcs.kind`: string, `github` | `forgejo`
- `vcs.base_branch`: string, PR target and back-merge source
- `vcs.work_branch_template`: string, default `symphony/<identifier>`
- `vcs.author` / `vcs.actor`: identity mapping for commits and the push/PR actor
- `vcs.api_key`: resolved via the secret-provider interface (file provider REQUIRED), not via `$VAR`/env
- `hooks.after_create`: shell script or null
- `hooks.before_run`: shell script or null
- `hooks.after_run`: shell script or null
- `hooks.before_remove`: shell script or null
- `hooks.timeout_ms`: integer, default `60000`
- `agent.default_agent`: string, `codex` | `claude_code`, default implementation-defined
- `agent.default_effort`: adapter-native value passed through to the agent, default implementation-defined
- `agent.agent_by_label`: map `label -> {agent, effort}` (per-issue override), default `{}`
- `agent.max_concurrent_agents`: integer, default `10`
- `agent.max_turns`: integer, default `20`
- `agent.max_retry_backoff_ms`: integer, default `300000` (5m)
- `agent.max_concurrent_agents_by_state`: map of positive integers, default `{}`
- `codex.command` (Codex adapter): shell command string, default `codex app-server`
- `codex.approval_policy`: Codex `AskForApproval` value, default implementation-defined
- `codex.thread_sandbox`: Codex `SandboxMode` value, default implementation-defined
- `codex.turn_sandbox_policy`: Codex `SandboxPolicy` value, default implementation-defined
- `codex.turn_timeout_ms`: integer, default `3600000`
- `codex.read_timeout_ms`: integer, default `5000`
- `codex.stall_timeout_ms`: integer, default `300000`

## 7. Orchestration State Machine

The orchestrator is the only component that mutates scheduling state. All worker outcomes are
reported back to it and converted into explicit state transitions.

### 7.1 Issue Orchestration States

This is not the same as tracker states (`Todo`, `In Progress`, etc.). This is the service's internal
claim state.

1. `Unclaimed`
   - Issue is not running and has no retry scheduled.

2. `Claimed`
   - Orchestrator has reserved the issue to prevent duplicate dispatch.
   - In practice, claimed issues are either `Running` or `RetryQueued`.

3. `Running`
   - Worker task exists and the issue is tracked in `running` map.

4. `RetryQueued`
   - Worker is not running, but a retry timer exists in `retry_attempts`.

5. `Released`
   - Claim removed because issue is terminal, non-active, missing, or retry path completed without
     re-dispatch.

Important nuance:

- A successful worker exit does not mean the issue is done forever.
- The worker MAY continue through multiple back-to-back coding-agent turns before it exits.
- After each normal turn completion, the worker re-checks the tracker issue state.
- If the issue is still in an active state, the worker SHOULD start another turn on the same live
  coding-agent thread in the same workspace, up to `agent.max_turns`.
- The first turn SHOULD use the full rendered task prompt.
- Continuation turns SHOULD send only continuation guidance to the existing thread, not resend the
  original task prompt that is already present in thread history.
- Once the worker exits normally, the orchestrator still schedules a short continuation retry
  (about 1 second) so it can re-check whether the issue remains active and needs another worker
  session.

### 7.2 Run Attempt Lifecycle

A run attempt transitions through these phases:

1. `PreparingWorkspace`
2. `BuildingPrompt`
3. `LaunchingAgentProcess`
4. `InitializingSession`
5. `StreamingTurn`
6. `Finishing`
7. `Succeeded`
8. `Failed`
9. `TimedOut`
10. `Stalled`
11. `CanceledByReconciliation`

Distinct terminal reasons are important because retry logic and logs differ.

### 7.3 Transition Triggers

- `Poll Tick`
  - Reconcile active runs.
  - Validate config.
  - Fetch candidate issues.
  - Dispatch until slots are exhausted.

- `Worker Exit (normal)`
  - Remove running entry.
  - Update aggregate runtime totals.
  - Schedule continuation retry (attempt `1`) after the worker exhausts or finishes its in-process
    turn loop.

- `Worker Exit (abnormal)`
  - Remove running entry.
  - Update aggregate runtime totals.
  - Schedule exponential-backoff retry.

- `Agent Update Event`
  - Update live session fields, token counters, and rate limits.

- `Retry Timer Fired`
  - Re-fetch active candidates and attempt re-dispatch, or release claim if no longer eligible.

- `Reconciliation State Refresh`
  - Stop runs whose issue states are terminal or no longer active.

- `Stall Timeout`
  - Kill worker and schedule retry.

### 7.4 Idempotency and Recovery Rules

- The orchestrator serializes state mutations through one authority to avoid duplicate dispatch.
- `claimed` and `running` checks are REQUIRED before launching any worker.
- Reconciliation runs before dispatch on every tick.
- Restart recovery is tracker-driven and filesystem-driven: `Reconstructable` and `Ephemeral`
  state (Section 14.3) is rebuilt or reset, and no durable orchestrator database is REQUIRED. An
  OPTIONAL extension MAY introduce `Durable` state, which is then the only state restored from a
  store across a restart.
- Startup terminal cleanup removes stale workspaces for issues already in terminal states.

## 8. Polling, Scheduling, and Reconciliation

### 8.1 Poll Loop

At startup, the service validates config, performs startup cleanup, schedules an immediate tick, and
then repeats every `polling.interval_ms`.

The effective poll interval SHOULD be updated when workflow config changes are re-applied.

Tick sequence:

1. Reconcile running issues.
2. Run dispatch preflight validation.
3. Fetch candidate issues from each tracker (once per tracker) and route them to repositories
   (Section 8.7).
4. Sort issues by dispatch priority.
5. Dispatch eligible issues while slots remain.
6. Notify observability/status consumers of state changes.

If per-tick validation fails, dispatch is skipped for that tick, but reconciliation still happens
first.

### 8.2 Candidate Selection Rules

An issue is dispatch-eligible only if all are true:

- It has `id`, `identifier`, `title`, and `state`.
- Its state is in `active_states` and not in `terminal_states`.
- It is routed to this worker by the configured assignee and contains every
  label in `tracker.required_labels`.
- It is not already in `running`.
- It is not already in `claimed`.
- Global concurrency slots are available.
- Per-state concurrency slots are available.
- Blocker rule for `Todo` state passes:
  - If the issue state is `Todo`, do not dispatch when any blocker is non-terminal.
  - An adapter that does not populate `blocked_by` reports no blockers, so this rule does not gate.

Sorting order (stable intent):

1. `priority` ascending (1..4 are preferred; null/unknown sorts last)
2. `created_at` oldest first
3. `identifier` lexicographic tie-breaker

### 8.3 Concurrency Control

Global limit:

- `available_slots = max(max_concurrent_agents - running_count, 0)`

Per-state limit:

- `max_concurrent_agents_by_state[state]` if present (state key normalized)
- otherwise fallback to global limit

The runtime counts issues by their current tracked state in the `running` map.

### 8.4 Retry and Backoff

Retry entry creation:

- Cancel any existing retry timer for the same issue.
- Store `attempt`, `identifier`, `error`, `due_at_ms`, and new timer handle.

Backoff formula:

- Normal continuation retries after a clean worker exit use a short fixed delay of `1000` ms.
- Failure-driven retries use `delay = min(10000 * 2^(attempt - 1), agent.max_retry_backoff_ms)`.
- Power is capped by the configured max retry backoff (default `300000` / 5m).

Retry handling behavior:

1. Fetch active candidate issues (not all issues).
2. Find the specific issue by `issue_id`.
3. If not found, release claim.
4. If found and still candidate-eligible:
   - Dispatch if slots are available.
   - Otherwise requeue with error `no available orchestrator slots`.
5. If found but no longer active, release claim.

Note:

- Terminal-state workspace cleanup is handled by startup cleanup and active-run reconciliation
  (including terminal transitions for currently running issues).
- Retry handling mainly operates on active candidates and releases claims when the issue is absent,
  rather than performing terminal cleanup itself.

### 8.5 Active Run Reconciliation

Reconciliation runs every tick and has two parts.

Part A: Stall detection

- For each running issue, compute `elapsed_ms` since:
  - `last_timestamp` if any event has been seen, else
  - `started_at`
- If `elapsed_ms > codex.stall_timeout_ms`, terminate the worker and queue a retry.
- If `stall_timeout_ms <= 0`, skip stall detection entirely.

Part B: Tracker state refresh

- Fetch current issue states for all running issue IDs.
- For each running issue:
  - If tracker state is terminal: terminate worker and clean workspace.
  - If tracker state is still active: update the in-memory issue snapshot.
  - If tracker state is neither active nor terminal: terminate worker without workspace cleanup.
- If state refresh fails, keep workers running and try again on the next tick.

### 8.6 Startup Terminal Workspace Cleanup

When the service starts:

1. Query tracker for issues in terminal states.
2. For each returned issue identifier, remove the corresponding workspace directory.
3. If the terminal-issues fetch fails, log a warning and continue startup.

This prevents stale terminal workspaces from accumulating after restarts.

### 8.7 Multiple Repositories and Shared Polling

One Symphony instance MAY manage multiple repositories.

Configuration:

- The policy config enumerates the managed repositories, each with its own VCS configuration
  (Section 9.7) and agent selection (Section 10.9), and the trackers they draw work from.

Issue-to-repository routing:

- Each polled issue is routed to exactly one repository. An issue maps to one repository only;
  cross-repository changes are handled as separate issues.
- Routing uses an explicit, tracker-implementation-specific mapping in the policy config. For
  example, the `linear` adapter maps by project, team, label, or assignee; the `forgejo` adapter
  maps by repository and issue tags/state. Routing MUST NOT depend on untrusted free-form issue
  content beyond what the mapping names.

Shared polling:

- When several repositories draw work from the same tracker, the tracker is polled once per cycle
  and the returned issues are routed to repositories via the mapping, rather than polling per
  repository. This minimizes redundant background polling.

Keying:

- Workspace identity, the per-repository object store (Section 9.7), and concurrency accounting are
  keyed by `(repository, issue)`.

### 8.8 Token Budget Guards (OPTIONAL)

An OPTIONAL extension that bounds token spend. The unit of account is tokens; a cost/currency layer
is deferred (see below). Budgets are enforced against Symphony-attributed cumulative usage
(Section 13.5), not provider account totals.

Budget scopes and exhaustion semantics:

- A per-session cap and a per-issue cap, when exceeded, abort the running worker and requeue that
  one issue as a budget failure (below); other issues are unaffected, preserving throughput.
- A global cap (for example, a rolling window across all issues), when exceeded, pauses new dispatch
  while in-flight runs continue. The pause is a dispatch gate composing with Concurrency Control
  (Section 8.3): a paused scope contributes zero available slots; running workers are not
  terminated. Dispatch resumes when the scope is back under its cap.

Failure disposition:

- Budget exhaustion is its own failure category, `token_budget_exceeded`. It is parked, not retried:
  the run is aborted and the issue is moved to the policy's blocked disposition (Section 11.6)
  rather than scheduled for exponential-backoff retry (Section 8.4). An implementation SHOULD record
  why the issue was parked.

Soft warning:

- Each cap MAY define a soft warning threshold, `<cap>_warning_pct` (Default: `80`), that emits a
  one-shot warning signal when crossed. Crossing the warning threshold does not abort or pause.

Durable, idempotent counters:

- Budget counters are class `Durable` (Section 14.3). They MUST be re-seeded from durable spend —
  for example, by replaying the per-execution usage ledger (Section 13.6) — before any enforcement
  decision, and re-applying a usage report MUST be idempotent (keyed by an absolute snapshot), so a
  restart neither grants a partially-spent issue a fresh budget nor double-counts. With no durable
  store configured, the extension degrades as documented for class `Durable`.

Constrained recovery (OPTIONAL):

- On a cap breach, an implementation MAY allow one constrained continuation: retry once through a
  narrow handoff prompt if the workspace shows fresh local progress, otherwise park. A second breach
  without new progress parks terminally.

Tripwire semantics:

- A cap is evaluated against observed cumulative usage and therefore MAY be overshot by roughly one
  agent report before it trips; it bounds runaway spend rather than pre-authorizing it.
  Estimate-based pre-authorization (gating a dispatch on a projected cost) is a separate, advisory
  option and is not REQUIRED here.

Deferred cost layer:

- Budgets here are denominated in tokens. A cost/currency overlay — dollars as the unit, with an
  `Implementation-defined` per-model pricing table converting token counts to currency — is a future
  layer over this extension. If added, it MUST document how pricing is sourced and kept current and
  the policy for an unpriced model (fail-open vs fail-closed).

Configuration:

- The extension owns its configuration under the `budget.*` namespace, documented with it. Caps
  default to disabled (no limit); `<cap>_warning_pct` defaults to `80`. Core conformance does not
  require these fields.

### 8.9 Provider Quota Backpressure (OPTIONAL)

An OPTIONAL extension that pauses taking on new work when the underlying provider account is near a
usage limit. It governs account headroom, which is distinct from Symphony's own token budgets
(Section 8.8): account-wide quota MUST NOT be summed into Symphony-attributed consumed-token totals
or budgets.

Normalized quota snapshot:

- Heterogeneous provider quota is normalized into one snapshot with fields:
  - `provider` (which provider the snapshot describes)
  - `source` (how it was obtained — see ingestion below)
  - `fetched_at` (when the value was last successfully obtained)
  - `stale_after_ms` (the age past which the snapshot is treated as `UNKNOWN`)
  - `buckets` (one or more named usage buckets, each with a `used_percent` in `0`–`100` and an
    OPTIONAL `resets_at`)
  - OPTIONAL `error` (set when the most recent refresh failed)
- Bucket identity is opaque: bucket names are provider-specific and unstable, so the gate only
  compares each `used_percent` against a threshold and never depends on a specific bucket name.

Ingestion (two paths, one shape):

- In-band: the rate-limit payloads already tracked per Section 13.5 are normalized into the snapshot
  for providers that report quota on their turn stream.
- Out-of-band (OPTIONAL): a poller queries a provider usage interface and normalizes the result into
  the same snapshot. The poller's credential source and any refresh subprocess are
  `Implementation-defined` and MUST be documented and bounded.

Recovery semantics:

- The snapshot is class `Cached external signal` (Section 14.3): the last-known-good value is
  carried across a failed refresh and a process restart; once older than `stale_after_ms` it becomes
  `UNKNOWN`, which is distinct from any `used_percent` value, including `0`.

Dispatch gate:

- When any bucket's `used_percent` is at or above `dispatch_pause_percent`, the extension pauses new
  dispatch. Running workers and reconciliation are not affected. Resume is implicit: the gate is
  re-evaluated each tick and there is no dedicated paused state.
- On `UNKNOWN`, behavior follows a configured policy: fail-open (proceed) or fail-closed (pause). A
  permanently `UNKNOWN` signal (a provider/agent that exposes no quota interface) SHOULD default to
  fail-open; a transiently `UNKNOWN` one (a temporary block) MAY fail-closed.

Configuration:

- The extension owns its configuration under the `quota.*` namespace, documented with it:
  `enabled` (Default: `false`), `dispatch_pause_percent` (Default: `95`), `stale_after_ms`
  (Default: `180000`), and a poller `refresh_ms` for the out-of-band path. Core conformance does not
  require these fields.

## 9. Workspace, VCS, and Safety

### 9.1 Workspace Layout

Workspace root:

- `workspace.root` (normalized absolute path)

Per-issue workspace path:

- `<workspace.root>/<repo_key>/<sanitized_issue_identifier>` when one instance manages multiple
  repositories; `<workspace.root>/<sanitized_issue_identifier>` for a single-repository instance.

Workspace persistence:

- Workspaces are reused across runs for the same issue.
- Successful runs do not auto-delete workspaces.

VCS-backed workspaces:

- When the issue's repository is managed by a VCS adapter (Section 9.7), the per-issue workspace is
  a git worktree of that repository's shared object store, not a bare directory. The path layout
  above is unchanged.

### 9.2 Workspace Creation and Reuse

Input: `issue.identifier`

Algorithm summary:

1. Sanitize identifier to `workspace_key`.
2. Compute workspace path under workspace root.
3. Ensure the workspace path exists as a directory.
4. Mark `created_now=true` only if the directory was created during this call; otherwise
   `created_now=false`.
5. If `created_now=true`, run `after_create` hook if configured.

Notes:

- For VCS-managed repositories, workspace creation provisions a worktree of the repository's shared
  object store (Section 9.7) rather than only an empty directory.
- Additional workspace preparation (for example dependency bootstrap, build, or code generation) is
  handled via in-sandbox hooks (Section 5.3.4).

### 9.3 Workspace Population

For VCS-managed repositories, repository population and synchronization are first-class Symphony
behavior (Section 9.7), not an implementation-defined hook concern. For non-VCS workspaces,
implementations MAY still populate or synchronize using hooks (for example `after_create` and/or
`before_run`).

Failure handling:

- Workspace population/synchronization failures return an error for the current attempt.
- If failure happens while creating a brand-new workspace, implementations MAY remove the partially
  prepared directory.
- Reused workspaces SHOULD NOT be destructively reset on population failure unless that policy is
  explicitly chosen and documented.

### 9.4 Workspace Hooks

Supported hooks:

- `hooks.after_create`
- `hooks.before_run`
- `hooks.after_run`
- `hooks.before_remove`

Execution contract:

- Execute in a local shell context appropriate to the host OS, with the workspace directory as
  `cwd`.
- On POSIX systems, `sh -lc <script>` (or a stricter equivalent such as `bash -lc <script>`) is a
  conforming default.
- Hook timeout uses `hooks.timeout_ms`; default: `60000 ms`.
- Log hook start, failures, and timeouts.

Failure semantics:

- `after_create` failure or timeout is fatal to workspace creation.
- `before_run` failure or timeout is fatal to the current run attempt.
- `after_run` failure or timeout is logged and ignored.
- `before_remove` failure or timeout is logged and ignored.

### 9.5 Safety Invariants

This is the most important portability constraint.

Invariant 1: Run the coding agent only in the per-issue workspace path.

- Before launching the coding-agent subprocess, validate:
  - `cwd == workspace_path`

Invariant 2: Workspace path MUST stay inside workspace root.

- Normalize both paths to absolute.
- Require `workspace_path` to have `workspace_root` as a prefix directory.
- Reject any path outside the workspace root.

Invariant 3: Workspace key is sanitized.

- Only `[A-Za-z0-9._-]` allowed in workspace directory names.
- Replace all other characters with `_`.

### 9.6 Agent Sandbox and Execution Isolation

Each coding-agent run MUST be runnable inside a sandbox that isolates the agent from the host and
from Symphony's credentials. The sandbox profile is configurable; a strict containment profile is
the assumed default.

Sandbox profile:

- The reference baseline is `jai` (https://jai.scs.stanford.edu) in its `Strict` mode on Linux — a
  containment tool for AI agents — with an equivalent local mechanism on other platforms. The
  selected profile is `Implementation-defined` and MUST be documented.
- `jai` describes itself as a casual sandbox that reduces rather than eliminates risk, so
  deployments needing stronger isolation SHOULD layer additional controls (container, VM, or network
  policy).

Privileged channel:

- The per-run broker socket (Section 10.8) is the only privileged channel into the sandbox. It is
  mounted into the sandbox and bound to exactly one run, so the broker attributes every request to
  that run's repository, issue, and work branch.
- No credentials are present inside the sandbox. Every secret-bearing environment variable MUST be
  scrubbed before the sandbox starts (Section 15.3).

Working tree:

- The per-issue working tree is a host directory bind-mounted into the sandbox. The agent edits and
  runs local git there; Symphony performs credentialed git (fetch, push) on the host against the
  same directory, with the pushed ref pinned by Symphony. The agent can read repository git state
  but cannot authenticate to a remote or change which ref Symphony pushes.

Network egress:

- Egress policy is configurable. Under the strict default, egress is denied except for an
  operator-maintained allowlist (for example the agent's model API and package registries) plus the
  broker socket. Implementations MUST document the effective egress policy.

### 9.7 VCS Adapter and Repository Provisioning

Symphony owns all interaction with the version-control remote through a VCS adapter. At least two
adapters are defined: `github` and `forgejo`. The adapter backs the broker's git and pull-request
verbs (Section 9.9); the agent never holds VCS credentials.

Repository provisioning:

- Symphony keeps one fetched object store per repository on the host. Each issue's working tree is a
  worktree (or reference clone) of that store, created under the workspace root and bind-mounted
  into the sandbox (Section 9.6). Sharing objects keeps provisioning fast and disk-efficient as the
  number of repositories and concurrent issues grows.
- Fetch and other network git operations run on the host with credentials the agent never sees.
  Local git in the worktree is available to the agent.

Configuration (policy config, `vcs` object):

- `kind` (string) — `github` or `forgejo`.
- `base_branch` (string) — the branch pull requests target and back-merges pull from.
- `work_branch_template` (string) — template for the deterministic work branch (Section 9.8).
  Default: `symphony/<identifier>`.
- `author` / `actor` (objects) — identity mapping for commits and for the push/PR actor (Section
  9.8).
- `api_key` (string) — resolved through the secret-provider interface (Section 15.3).

### 9.8 Git Automation and Work Branch

Division of labor:

- The agent uses local git in the worktree, including `git commit`, and resolves conflicts. Symphony
  performs every operation that touches the remote: fetch, branch, back-merge, push, and
  pull-request management.
- The agent's high-value contributions are commit and pull-request *messages* and *conflict
  resolution*; Symphony automates the surrounding git mechanics.

Work branch:

- The work branch is derived deterministically from issue identity using `vcs.work_branch_template`
  (Default: `symphony/<identifier>`). It does not depend on agent input; a tracker-provided
  `branch_name` is at most a hint.
- Because the branch is fixed and Symphony-derived, the broker can enforce "push only to the work
  branch" (Section 10.8).

Push:

- The agent commits locally and requests a push through the broker. Symphony pushes the work branch
  from the host with the refspec pinned to the work branch; it does not push agent-specified refs.

Back-merge and conflict handoff:

- At the start of a run, Symphony attempts to bring the work branch up to date with
  `vcs.base_branch`. If the update applies cleanly it is taken; if it would conflict, it is
  postponed so the agent is not interrupted up front.
- Conflict resolution is required only when a push is rejected as non-fast-forward. Symphony then
  stages the back-merge in the worktree, hands the conflicted tree to the agent (via continuation
  guidance) to resolve, and completes the merge once the agent signals done.

Identity:

- The commit author/committer and the push/pull-request actor are configurable per repository
  (`vcs.author`, `vcs.actor`). Where branch protection requires review, the actor SHOULD be distinct
  from the approver so a pull request cannot be self-approved.

### 9.9 Pull Requests and Broker Git/PR Verbs

Pull requests:

- Symphony maintains one pull request per issue. It is created on first push and updated (new
  commits, refreshed title/body) on later runs, and reused across retries and continuations. The
  agent supplies the title and body; the base is `vcs.base_branch` and the head is the work branch.

Broker git/PR verbs:

- The broker exposes a fixed neutral core of git and pull-request verbs over the per-run socket
  (Section 10.8), identical across `github` and `forgejo`: for example `push`, `back-merge`, `pr`
  (create/update), and `request-merge`. Adapters or policy MAY extend this set.
- Each verb returns a structured result with a stable reason code on failure (for example
  `non_fast_forward`, `pr_conflict`, `scope_denied`). Ordinary failures are returned to the agent to
  adapt to; `scope_denied` fails the run (Section 10.8).

## 10. Agent Runner Protocol (Coding Agent Integration)

This section defines Symphony's agent-neutral responsibilities for running a coding agent. Symphony
supports more than one agent (at least Codex and Claude Code) through per-agent *adapters*: each
adapter implements the same neutral runner contract over its agent's own protocol, which is the
source of truth for that agent's protocol schemas, message payloads, transport framing, and method
names.

Sections 10.1–10.6 describe these responsibilities using the Codex adapter as the worked example;
another adapter (for example Claude Code) provides the same responsibilities over its own protocol.
Section 10.9 defines the neutral contract, the available adapters, and how an agent is selected.

Protocol source of truth:

- Implementations MUST send messages that are valid for the targeted agent adapter's protocol
  version.
- Implementations MUST consult the targeted agent's documentation or generated schema instead of
  treating this specification as a protocol schema.
- If this specification appears to conflict with the targeted agent's protocol, that protocol
  controls protocol shape and transport behavior.
- Symphony-specific requirements in this section still control orchestration behavior, workspace
  selection, prompt construction, continuation handling, and observability extraction.

### 10.1 Launch Contract

Subprocess launch parameters:

- Command: `codex.command`
- Invocation: `bash -lc <codex.command>`
- Working directory: workspace path
- Transport/framing: the protocol transport required by the targeted Codex app-server version

Notes:

- The default command is `codex app-server`.
- Approval policy, sandbox policy, cwd, prompt input, and OPTIONAL tool declarations are supplied
  using fields supported by the targeted Codex app-server version.

RECOMMENDED additional process settings:

- Max line size: 10 MB (for safe buffering)

### 10.2 Session Startup Responsibilities

Reference: https://developers.openai.com/codex/app-server/

Startup MUST follow the targeted Codex app-server contract. Symphony additionally requires the
client to:

- Start the app-server subprocess in the per-issue workspace.
- Initialize the app-server session using the targeted Codex app-server protocol.
- Create or resume a coding-agent thread according to the targeted protocol.
- Supply the absolute per-issue workspace path as the thread/turn working directory wherever the
  targeted protocol accepts cwd.
- Start the first turn with the rendered issue prompt.
- Start later in-worker continuation turns on the same live thread with continuation guidance rather
  than resending the original issue prompt.
- Supply the implementation's documented approval and sandbox policy using fields supported by the
  targeted protocol.
- Include issue-identifying metadata, such as `<issue.identifier>: <issue.title>`, when the targeted
  protocol supports turn or session titles.
- Advertise any implemented in-protocol client-side tools using the targeted protocol. Privileged
  operations are not exposed this way; they are performed through the broker CLI (Section 10.8).

Session identifiers:

- Extract `thread_id` from the thread identity returned by the targeted Codex app-server protocol.
- Extract `turn_id` from each turn identity returned by the targeted Codex app-server protocol.
- Emit `session_id = "<thread_id>-<turn_id>"`
- Reuse the same `thread_id` for all continuation turns inside one worker run

### 10.3 Streaming Turn Processing

A *turn* is one orchestration-initiated prompt-to-completion cycle on the live agent thread:
Symphony sends a prompt (the full task prompt on the first turn, continuation guidance on later
turns) and the adapter streams the targeted protocol's updates until that cycle terminates. A turn
is the targeted protocol's own turn unit; the Codex adapter maps it to one `turn_id` (Section 10.2).

Within a turn the coding agent autonomously conducts any number of internal *steps* (model
inferences and the tool calls they drive) to satisfy the prompt. Steps are agent-internal: Symphony
neither initiates nor counts them, and `agent.max_turns` bounds turns, not steps. An adapter MAY
enforce its own per-turn step limit (for example a native `--max-turns`-style control); that limit
is adapter-owned and distinct from Symphony's `agent.max_turns`, and a breach of it is surfaced to
Symphony as a turn-ending signal, not as a step count. A worker *run* (Section 7.2) is the full
sequence of turns for one issue attempt, so a run contains one or more turns and each turn
contains one or more steps.

The client processes app-server updates according to the targeted Codex app-server protocol until
the active turn terminates.

Completion conditions:

- Targeted-protocol turn completion signal -> success
- Targeted-protocol turn failure signal -> failure
- Targeted-protocol turn cancellation signal -> failure
- turn timeout (`turn_timeout_ms`) -> failure
- subprocess exit -> failure

Continuation processing:

- Continuation state is carried in an opaque `continuation_ref` returned by each turn (Section
  10.7). If the worker decides to continue after a successful turn, it starts another turn passing
  that `continuation_ref` and continuation guidance rather than the original prompt.
- Keeping the app-server subprocess alive across continuation turns is the Codex adapter's way of
  realizing a warm `continuation_ref`; the contract does not require it. Another adapter MAY resume
  from a token or re-establish the session (Section 10.9).

Transport handling requirements:

- Follow the transport and framing rules of the targeted Codex app-server version.
- For stdio-based transports, keep protocol stream handling separate from diagnostic stderr
  handling unless the targeted protocol specifies otherwise.

### 10.4 Emitted Runtime Events (Upstream to Orchestrator)

The app-server client emits structured events to the orchestrator callback. Each event SHOULD
include:

- `event` (enum/string)
- `timestamp` (UTC timestamp)
- `pid` (if available)
- OPTIONAL `usage` map: the neutral token-usage record (`input_tokens`, `output_tokens`,
  `total_tokens`; Section 13.5), with any adapter-specific counts (for example cache tokens) in an
  opaque extras field
- payload fields as needed

Important emitted events include, for example:

- `session_started`
- `startup_failed`
- `turn_completed`
- `turn_failed`
- `turn_cancelled`
- `turn_ended_with_error`
- `turn_input_required`
- `approval_auto_approved`
- `unsupported_tool_call`
- `notification`
- `other_message`
- `malformed`

### 10.5 Approval, Tool Calls, and User Input Policy

Approval, sandbox, and user-input behavior is implementation-defined.

Policy requirements:

- Each implementation MUST document its chosen approval, sandbox, and operator-confirmation
  posture.
- Approval requests and user-input-required events MUST NOT leave a run stalled indefinitely. An
  implementation MAY either satisfy them, surface them to an operator, auto-resolve them, or
  fail the run according to its documented policy.

Example high-trust behavior:

- Auto-approve command execution approvals for the session.
- Auto-approve file-change approvals for the session.
- Treat user-input-required turns as hard failure.

Unsupported dynamic tool calls:

- Supported dynamic tool calls that are explicitly implemented and advertised by the runtime SHOULD
  be handled according to their extension contract.
- If the agent requests a dynamic tool call that is not supported, return a tool failure response
  using the targeted protocol and continue the session.
- This prevents the session from stalling on unsupported tool execution paths.

Privileged operations:

- Privileged, outward-facing operations (VCS remote actions, pull-request creation, issue-tracker
  reads and writes) are not exposed as in-protocol tools. They are performed through the broker CLI
  described in Section 10.8, which the agent invokes as an ordinary command inside its sandbox.
- This supersedes the former `linear_graphql` client-side tool: raw tracker access is no longer an
  in-protocol tool but a brokered operation subject to authorization scope.

User-input-required policy:

- Implementations MUST document how targeted-protocol user-input-required signals are handled.
- A run MUST NOT stall indefinitely waiting for user input.
- A conforming implementation MAY fail the run, surface the request to an operator, satisfy it
  through an approved operator channel, or auto-resolve it according to its documented policy.
- The example high-trust behavior above fails user-input-required turns immediately.

### 10.6 Timeouts and Error Mapping

Timeouts:

- `codex.read_timeout_ms`: request/response timeout during startup and sync requests
- `codex.turn_timeout_ms`: total turn stream timeout
- `codex.stall_timeout_ms`: enforced by orchestrator based on event inactivity

Error mapping (RECOMMENDED normalized categories):

- `codex_not_found`
- `invalid_workspace_cwd`
- `response_timeout`
- `turn_timeout`
- `port_exit`
- `response_error`
- `turn_failed`
- `turn_cancelled`
- `turn_input_required`

Note:

- A turn stopped early (timeout, stall, or operator/budget interruption) is cancelled through
  the contract's `cancel` operation (Section 10.7). A `turn_timeout` reached without a clean
  interrupt-then-drain leaves the underlying turn still running, so the session is not safely
  resumable and the turn fails; an adapter that can drain cleanly MAY instead yield a resumable
  `continuation_ref`.

### 10.7 Agent Runner Contract

The `Agent Runner` is the neutral, turn-centric contract between the orchestrator and an agent
adapter. It is keyed by the selected adapter (Section 10.9) and exposes these operations:

- `run_turn(workspace, prompt, issue, continuation_ref, on_event)` — run one turn (Section 10.3),
  returning a result with its outcome, normalized token usage (Section 13.5), session/turn identity,
  and a new `continuation_ref`. The first turn passes `continuation_ref = null` and the full task
  prompt; later turns pass the prior turn's `continuation_ref` and continuation guidance. There is
  no separate session-start operation: an adapter establishes whatever session or process it needs
  lazily on the first `run_turn`.
- `cancel(continuation_ref)` — every adapter MUST support cancelling an in-flight turn. The adapter
  SHOULD interrupt the turn, drain to the targeted protocol's real terminal signal within a bounded
  secondary timeout, and yield a resumable `continuation_ref`; if it cannot drain cleanly it MUST
  still terminate, in which case the turn fails (Section 10.6).
- `release(continuation_ref)` — free any warm resources (a live subprocess, a session handle) when
  the worker run is ending.

`continuation_ref` is an opaque, adapter-owned token that is the contract-level continuation state.
An adapter MAY realize it as a live warm session handle (the Codex adapter keeps the app-server
subprocess alive, Section 10.3), a resume token, or declare it non-resumable through its capability
descriptor (Section 10.9).

Each adapter MUST emit the neutral event vocabulary (Section 10.4) and normalize usage into the
neutral token-usage record (`input_tokens`, `output_tokens`, `total_tokens`; Section 13.5), carrying
raw protocol payloads opaquely and any adapter-specific counts in an extras field. On any error the
Agent Runner fails the worker attempt and the orchestrator retries.

Behavior outline:

1. Create/reuse workspace for issue.
2. Build prompt from workflow template.
3. `run_turn` with the threaded `continuation_ref`; forward emitted events to the orchestrator.
4. `cancel` an in-flight turn on timeout/stall/interruption; `release` warm resources at run end.
5. On any error, fail the worker attempt (the orchestrator will retry).

Note:

- Workspaces are intentionally preserved after successful runs.

### 10.8 Privileged Operation Broker (`symphony` CLI)

Symphony performs all privileged, outward-facing side effects on the agent's behalf. The agent is
sandboxed and holds no credentials; it requests every side effect — VCS remote operations,
pull-request creation, and issue-tracker interaction — by invoking a `symphony` command-line tool
that is the only privileged channel out of the sandbox.

Channel:

- The agent reaches the broker through a per-run socket (a Unix domain socket on Linux, or an
  equivalent local IPC mechanism on other platforms). The socket is bound to exactly one run, so the
  broker attributes every request to that run's repository, issue, and work branch without trusting
  any identifier supplied by the agent.
- Credentials are never placed in the sandbox: not in its environment, not on its filesystem, and
  not in the broker channel. The broker executes operations using credentials held by the
  orchestrator process outside the sandbox.

Authorization scope:

- The broker enforces authorization scope, not only credential confidentiality. Each brokered
  operation MUST be constrained to the current run: for example, push only to the run's work branch,
  write only to the assigned issue, and open or update only the pull request for that issue against
  the configured base.
- The brokered operations are a fixed neutral core, identical across VCS and tracker backends, plus
  an extension mechanism for adapter- or policy-specific operations. The core verbs are defined
  alongside the VCS and issue-tracker integration contracts.

Result contract:

- Every brokered operation returns a structured result with at least a success/failure status and,
  on failure, a stable reason code (for example `non_fast_forward`, `pr_conflict`, `scope_denied`).
  Ordinary failures are returned to the agent so it can adapt, for example resolve a conflict and
  retry.
- A `scope_denied` result is treated as a policy violation: the run MUST fail rather than allowing
  the agent to retry around the boundary.

Note:

- The broker supersedes in-protocol client-side tools (such as the former `linear_graphql` tool) as
  the way the agent effects change. Performing privileged operations through a CLI keeps them
  independent of the coding-agent protocol.

### 10.9 Agent Adapters and Selection

Symphony integrates each coding agent through an adapter implementing the neutral runner contract
of Section 10.7: `run_turn` (threading an opaque `continuation_ref`), `cancel`, and `release`,
emitting the neutral event vocabulary (Section 10.4) and normalized token usage (Section 13.5).

Each adapter encapsulates one (agent, transport) pairing and defers to its agent's own protocol as
the source of truth (Section 10 intro). Two transports for the same agent are two adapters; an
implementation MUST NOT require a non-native agent to impersonate another agent's protocol. At least
two adapters are defined: `codex` (the Codex app-server, the worked example in Sections 10.1–10.8)
and `claude_code`.

Capability descriptor:

- Each adapter advertises a static capability descriptor (data, not a runtime call), declaring at
  least: `resume` mode (`warm_session`, `resume_token`, or `none`), whether it streams turn updates,
  whether it enforces a native per-turn step limit (Section 10.3), and its accepted `effort` values.
- The orchestrator reads the descriptor to drive behavior: `resume = none` means it re-feeds context
  or treats each turn as fresh; a native step-limit breach is a turn boundary, not a failure.

Selection:

- The agent and its effort are selected in the operator policy config, because agent choice carries
  model credentials and sandbox shape. Each repository has a `default_agent` and `default_effort`.
- A per-issue override is expressed as an explicit policy table mapping tracker labels to an
  `{agent, effort}` pair (`agent.agent_by_label`); only mapped labels take effect.

Effort:

- `effort` is passed through to the selected agent as that agent's native value. Each adapter MUST
  document the values it accepts; a value is not portable across adapters, which is why the label
  mapping pairs an agent with its effort.

Observability normalization:

- Each adapter normalizes its protocol's session and turn identifiers and its usage payloads into
  the neutral logical session fields (Section 4.1.6) and token-usage record (Section 13.5). The
  `thread_id` / `turn_id` identity shown there is the Codex adapter's (Section 4.2); another adapter
  supplies its own.

## 11. Issue Tracker Integration Contract

Symphony performs all issue-tracker reads and writes through a tracker adapter; at least the
`linear` and `forgejo` adapters are defined. Reads feed scheduling and reconciliation; writes
(comments, state transitions, pull-request links) are performed by the broker (Section 10.8) with
content supplied by the agent. The agent never holds tracker credentials.

### 11.1 REQUIRED Operations

Every tracker adapter MUST support the read operations below. The write operations are
capability-gated: each adapter declares which of them it supports through its capability descriptor
(Section 11.7), and the orchestrator does not invoke an undeclared write.

Read operations (REQUIRED of every adapter):

1. `fetch_candidate_issues()`
   - Return issues in configured active states for a configured project.

2. `fetch_issues_by_states(state_names)`
   - Used for startup terminal cleanup.

3. `fetch_issue_states_by_ids(issue_ids)`
   - Used for active-run reconciliation.

Write operations (performed by the broker, Section 10.8; the agent supplies the content; supported
per the capability descriptor, Section 11.7):

4. `add_comment(issue_id, body)`
5. `set_state(issue_id, target_state)`
6. `link_pull_request(issue_id, pr_ref)`

### 11.2 Adapter Semantics

Each tracker adapter implements the read and write operations over its own API; the normalized
outputs MUST match the domain model in Section 4. The `forgejo` adapter uses the Forgejo issues API
and maps issue tags and open/closed status to the normalized states.

Linear-specific requirements for `tracker.kind == "linear"`:

- `tracker.kind == "linear"`
- GraphQL endpoint (default `https://api.linear.app/graphql`)
- Auth token sent in `Authorization` header
- `tracker.project_slug` maps to Linear project `slugId`
- Candidate issue query filters project using `project: { slugId: { eq: $projectSlug } }`
- Candidate and issue-state refresh queries include issue labels. Required
  label filtering happens after normalization so refresh can observe label
  removal and stop or release existing work.
- Issue-state refresh query uses GraphQL issue IDs with variable type `[ID!]`
- Pagination REQUIRED for candidate issues
- Page size default: `50`
- Network timeout: `30000 ms`

Important:

- Linear GraphQL schema details can drift. Keep query construction isolated and test the exact query
  fields/types REQUIRED by this specification.

A non-Linear implementation MAY change transport details, but the normalized outputs MUST match the
domain model in Section 4.

### 11.3 Normalization Rules

Candidate issue normalization SHOULD produce fields listed in Section 4.1.1.

Additional normalization details:

- Label names are trimmed and lowercased.

- `labels` -> lowercase strings
- `blocked_by` -> for `linear`, derived from inverse relations where relation type is `blocks`; an
  adapter whose tracker has no dependency model leaves it empty
- `branch_name` -> tracker-provided when available, otherwise null or adapter-synthesized
- `priority` -> integer only (non-integers become null)
- `created_at` and `updated_at` -> parse ISO-8601 timestamps
- `metadata` -> adapter-defined; an implementation MUST document what its adapter places there
  (`Implementation-defined`)

### 11.4 Error Handling Contract

RECOMMENDED error categories. These are transport-neutral; each adapter maps its transport's
failures onto them:

- `unsupported_tracker_kind`
- `missing_tracker_api_key`
- `missing_tracker_project_slug`
- `tracker_unsupported_operation` (write not in the adapter capability descriptor, Section 11.7)
- `tracker_api_request` (transport or connection failure)
- `tracker_api_status` (unsuccessful response status, for example non-2xx HTTP)
- `tracker_backend_errors` (backend-reported errors in a well-formed response, for example a
  GraphQL `errors` array)
- `tracker_payload_invalid` (unexpected or unparseable response payload)
- `tracker_pagination_error` (pagination integrity failure, for example a missing continuation
  cursor)

Note: the Linear adapter, being GraphQL over HTTP, reports a non-2xx response as
`tracker_api_status`, a GraphQL `errors` array as `tracker_backend_errors`, and a missing page
cursor as `tracker_pagination_error`.

Orchestrator behavior on tracker errors:

- Candidate fetch failure: log and skip dispatch for this tick.
- Running-state refresh failure: log and keep active workers running.
- Startup terminal cleanup failure: log warning and continue startup.

### 11.5 Tracker Writes (Broker Boundary)

Issue-tracker writes are performed by the privileged broker (Section 10.8), not by the
orchestrator's scheduling logic and not by the agent using its own credentials.

- Ticket mutations (state transitions, comments, pull-request links) are requested by the agent
  through the `symphony` CLI and executed by the broker using Symphony's configured tracker auth.
  The agent supplies the content; it never holds tracker credentials.
- Workflow-specific success often means "reached the next handoff state" (for example
  `Human Review`) rather than tracker terminal state `Done`.

### 11.6 Workflow State Machine and Transition Triggers

Symphony drives ticket lifecycle; the agent supplies content and signals progress.

State machine:

- Ticket state transitions are governed by a workflow state-machine defined in the operator policy
  config (`tracker.transitions`, Section 5.3.1). Because transitions are privileged tracker writes
  performed outside the sandbox, the state-machine is operator-owned, not part of `WORKFLOW.md`.
- The state-machine is a directed graph over tracker workflow-state names — the `active_states` and
  `terminal_states` of Section 5.3.1, plus any intermediate handoff states such as `Human Review` or
  `Merging`. Each transition is a `{from, on, to}` entry: in state `from`, when trigger `on` fires,
  Symphony performs `set_state(issue_id, to)` (Section 11.1).
- The graph is defined over neutral state names only. The adapter maps each state name to its
  provider representation (Section 11.2); the state-machine MUST NOT name provider-specific
  representations.
- A trigger that fires with no matching `from`-state transition performs no transition.
- The graph MUST be deterministic: at most one transition per `(from, on)` pair. A duplicate
  `(from, on)` is a configuration error (Section 6.3).

Triggers:

Each transition's `on` value is drawn from one closed vocabulary with two origins. Operators wire
triggers to transitions but do not introduce new trigger names.

- Milestone signals, emitted by the agent through the broker CLI to express intent, optionally with
  content:
  - `ready-for-review`
  - `blocked`
  - `done`
- Run outcomes, observed by the orchestrator from run mechanics; the agent does not emit these:
  - `dispatched` — the orchestrator has claimed the issue and started its first turn (Sections 7.1,
    7.3).
  - `pull_request_opened` — a pull request was opened for the issue during the run.
  - `run_succeeded` — the run attempt finished in `Succeeded` (Section 7.2).
  - `run_failed` — the run attempt finished in a failure terminal reason (`Failed`, `TimedOut`, or
    `Stalled`; Section 7.2).
  - `retries_exhausted` — the retry path completed without re-dispatch (Section 7.1 `Released`,
    Section 8.4).

Process authority:

- The repository-owned prompt (Section 5.4) shapes how the agent works and which milestone signal it
  emits; it does not define the state-machine and cannot grant a trigger a transition the graph does
  not define. Run outcomes are orchestrator-emitted and not influenceable by prompt wording. Process
  authority is operator-owned (Sections 5.2, 5.3): no prompt wording widens the set of transitions
  an agent can cause.

### 11.7 Adapter Capability Descriptor

Tracker write support varies by backend, so writes are declared rather than universally mandated.
This mirrors the agent adapter capability descriptor (Section 10.9).

- Each tracker adapter advertises a static capability descriptor (data, not a runtime call),
  declaring which write operations it supports: `add_comment`, `set_state`, and `link_pull_request`
  (Section 11.1). The three read operations are REQUIRED of every adapter and are not part of the
  descriptor.
- The descriptor MAY depend on resolved config and is fixed for the run. For example, a tracker on a
  plan tier without a comment API declares `add_comment` unsupported, determined once at adapter
  initialization.
- The orchestrator reads the descriptor before invoking a write and MUST NOT invoke an undeclared
  write. An optional write the adapter does not support (for example `link_pull_request`) is skipped
  and logged, not failed. An undeclared write invoked anyway returns `tracker_unsupported_operation`
  (Section 11.4).
- An unsupported write MUST NOT be silently treated as success, no-oped, or replaced by a
  synthesized substitute (for example appending a comment into a description field). Capability gaps
  are explicit.
- A non-empty `tracker.transitions` (Section 5.3.1, Section 11.6) requires the `set_state`
  capability; dispatch preflight (Section 6.3) treats configured transitions on a tracker that does
  not support `set_state` as a configuration error.

## 12. Prompt Construction and Context Assembly

### 12.1 Inputs

Inputs to prompt rendering:

- `workflow.prompt_template`
- normalized `issue` object
- OPTIONAL `attempt` integer (retry/continuation metadata)

### 12.2 Rendering Rules

- Render with strict variable checking.
- Render with strict filter checking.
- Convert issue object keys to strings for template compatibility.
- Preserve nested arrays/maps (labels, blockers, metadata) so templates can iterate.

### 12.3 Retry/Continuation Semantics

`attempt` SHOULD be passed to the template because the workflow prompt can provide different
instructions for:

- first run (`attempt` null or absent)
- continuation run after a successful prior session
- retry after error/timeout/stall

### 12.4 Failure Semantics

If prompt rendering fails:

- Fail the run attempt immediately.
- Let the orchestrator treat it like any other worker failure and decide retry behavior.

## 13. Logging, Status, and Observability

### 13.1 Logging Conventions

REQUIRED context fields for issue-related logs:

- `issue_id`
- `issue_identifier`

REQUIRED context for coding-agent session lifecycle logs:

- `session_id`

Message formatting requirements:

- Use stable `key=value` phrasing.
- Include action outcome (`completed`, `failed`, `retrying`, etc.).
- Include concise failure reason when present.
- Avoid logging large raw payloads unless necessary.

### 13.2 Logging Outputs and Sinks

The spec does not prescribe where logs are written (stderr, file, remote sink, etc.).

Requirements:

- Operators MUST be able to see startup/validation/dispatch failures without attaching a debugger.
- Implementations MAY write to one or more sinks.
- If a configured log sink fails, the service SHOULD continue running when possible and emit an
  operator-visible warning through any remaining sink.

### 13.3 Runtime Snapshot / Monitoring Interface (OPTIONAL but RECOMMENDED)

If the implementation exposes a synchronous runtime snapshot (for dashboards or monitoring), it
SHOULD return:

- `running` (list of running session rows)
- each running row SHOULD include `turn_count`
- `retrying` (list of retry queue rows)
- session and retry rows SHOULD include the tracker-provided issue URL when available
- `agent_totals`
  - `input_tokens`
  - `output_tokens`
  - `total_tokens`
  - `seconds_running` (aggregate runtime seconds as of snapshot time, including active sessions)
- `rate_limits` (latest coding-agent rate limit payload, if available)

RECOMMENDED snapshot error modes:

- `timeout`
- `unavailable`

### 13.4 OPTIONAL Human-Readable Status Surface

A human-readable status surface (terminal output, dashboard, etc.) is OPTIONAL and
implementation-defined.

If present, it SHOULD draw from orchestrator state/metrics only and MUST NOT be REQUIRED for
correctness.

### 13.5 Session Metrics and Token Accounting

Each agent adapter normalizes its protocol's usage payloads into the neutral token-usage record
(`input_tokens`, `output_tokens`, `total_tokens`; Section 4.1.6). The payload names mentioned below
(`thread/tokenUsage/updated`, `total_token_usage`, `last_token_usage`) are Codex-adapter examples.

Token accounting rules:

- Agent events can include token counts in multiple payload shapes.
- Prefer absolute thread totals when available, such as:
  - `thread/tokenUsage/updated` payloads
  - `total_token_usage` within token-count wrapper events
- Ignore delta-style payloads such as `last_token_usage` for dashboard/API totals.
- Extract input/output/total token counts leniently from common field names within the selected
  payload.
- For absolute totals, track deltas relative to last reported totals to avoid double-counting.
- Do not treat generic `usage` maps as cumulative totals unless the event type defines them that
  way.
- Accumulate aggregate totals in orchestrator state.

Runtime accounting:

- Runtime SHOULD be reported as a live aggregate at snapshot/render time.
- Implementations MAY maintain a cumulative counter for ended sessions and add active-session
  elapsed time derived from `running` entries (for example `started_at`) when producing a
  snapshot/status view.
- Add run duration seconds to the cumulative ended-session runtime when a session ends (normal exit
  or cancellation/termination).
- Continuous background ticking of runtime totals is not REQUIRED.

Rate-limit tracking:

- Track the latest rate-limit payload seen in any agent update.
- Any human-readable presentation of rate-limit data is implementation-defined.
- The OPTIONAL provider quota backpressure extension (Section 8.9) normalizes these payloads into a
  provider-quota snapshot (class `Cached external signal`, Section 14.3) and MAY pause new dispatch.

### 13.6 Per-Execution Usage Ledger (OPTIONAL)

An OPTIONAL durable, append-only record of per-execution token usage, suitable for audit, for
debugging an expensive or looping run, and for cost attribution. It is also the RECOMMENDED
realization of the `Durable` recovery class (Section 14.3): replaying the ledger yields the
cumulative total and re-seeds an enforcement counter idempotently, so a budgeting extension (when
present) MAY source its durable spend from it. The `Durable` contract stays abstract — a non-ledger
durable counter also conforms.

If implemented:

- The ledger is append-only and durable. Each entry is a full absolute snapshot of one session's
  token usage at one observation, consistent with the token accounting rules in Section 13.5
  (absolute totals, never deltas).
- Entries are keyed by `(issue_identifier, session_id)`.

Entry fields:

- `schema_version` (integer)
  - Readers MUST skip entries whose version they do not recognize.
- `observed_at` (timestamp)
- `final` (boolean)
  - `true` for the end-of-session snapshot; `false` for a live observation during the session.
- `issue_id` (string or null)
- `issue_identifier` (string)
  - REQUIRED; an entry without it is invalid and MUST be skipped on read.
- `session_id` (string)
  - REQUIRED; an entry without it is invalid and MUST be skipped on read.
- `turn_count` (integer)
- `input_tokens` (integer)
- `output_tokens` (integer)
- `total_tokens` (integer)
  - Absolute cumulative totals for the session, not per-turn deltas (Section 13.5).
- `source_event` (string)
  - The agent event (or `session_final`) that produced the observation.

Summarization (read side):

- Take the maximum `total_tokens` (and the corresponding `input_tokens` / `output_tokens`) per
  `(issue_identifier, session_id)` — the high-water mark — then sum those per-session maxima.
- Never sum every observed entry. The high-water-mark rule is what makes repeated appends idempotent
  under retries, reconnects, and the end-of-session snapshot, and is what lets the ledger re-seed a
  `Durable` counter without double-counting.

I/O discipline:

- A write failure MUST be logged and MUST NOT crash orchestration.
- Readers MUST tolerate and skip truncated, malformed, or unrecognized-`schema_version` lines (a
  torn final line is normal for an append-only artifact).

Scope and configuration:

- The ledger is observability data, not a billing surface: the entry schema carries no pricing,
  cost, or `model` field. Post-hoc cost attribution would require adding a `model` field, so its
  omission is a deliberate boundary.
- The ledger owns its configuration (for example, a storage location and a retention policy) under
  its own namespace, documented with the extension. Core conformance does not require these fields.

### 13.7 Humanized Agent Event Summaries (OPTIONAL)

Humanized summaries of raw agent protocol events are OPTIONAL.

If implemented:

- Treat them as observability-only output.
- Do not make orchestrator logic depend on humanized strings.

### 13.8 OPTIONAL HTTP Server Extension

This section defines an OPTIONAL HTTP interface for observability and operational control.

If implemented:

- The HTTP server is an extension and is not REQUIRED for conformance.
- The implementation MAY serve server-rendered HTML or a client-side application for the dashboard.
- The dashboard/API MUST be observability/control surfaces only and MUST NOT become REQUIRED for
  orchestrator correctness.

Extension config:

- `server.port` (integer, OPTIONAL)
  - Enables the HTTP server extension.
  - `0` requests an ephemeral port for local development and tests.
  - CLI `--port` overrides `server.port` when both are present.

Enablement (extension):

- Start the HTTP server when a CLI `--port` argument is provided.
- Start the HTTP server when `server.port` is present in `WORKFLOW.md` front matter.
- The `server` top-level key is owned by this extension.
- Positive `server.port` values bind that port.
- Implementations SHOULD bind loopback by default (`127.0.0.1` or host equivalent) unless explicitly
  configured otherwise.
- Changes to HTTP listener settings (for example `server.port`) do not need to hot-rebind;
  restart-required behavior is conformant.

#### 13.8.1 Human-Readable Dashboard (`/`)

- Host a human-readable dashboard at `/`.
- The returned document SHOULD depict the current state of the system (for example active sessions,
  retry delays, token consumption, runtime totals, recent events, and health/error indicators).
- It is up to the implementation whether this is server-generated HTML or a client-side app that
  consumes the JSON API below.

#### 13.8.2 JSON REST API (`/api/v1/*`)

Provide a JSON REST API under `/api/v1/*` for current runtime state and operational debugging.

Minimum endpoints:

- `GET /api/v1/state`
  - Returns a summary view of the current system state (running sessions, retry queue/delays,
    aggregate token/runtime totals, latest rate limits, and any additional tracked summary fields).
  - Suggested response shape:

    ```json
    {
      "generated_at": "2026-02-24T20:15:30Z",
      "counts": {
        "running": 2,
        "retrying": 1
      },
      "running": [
        {
          "issue_id": "abc123",
          "issue_identifier": "MT-649",
          "issue_url": "https://tracker.example/issues/MT-649",
          "state": "In Progress",
          "session_id": "thread-1-turn-1",
          "turn_count": 7,
          "last_event": "turn_completed",
          "last_message": "",
          "started_at": "2026-02-24T20:10:12Z",
          "last_event_at": "2026-02-24T20:14:59Z",
          "tokens": {
            "input_tokens": 1200,
            "output_tokens": 800,
            "total_tokens": 2000
          }
        }
      ],
      "retrying": [
        {
          "issue_id": "def456",
          "issue_identifier": "MT-650",
          "issue_url": "https://tracker.example/issues/MT-650",
          "attempt": 3,
          "due_at": "2026-02-24T20:16:00Z",
          "error": "no available orchestrator slots"
        }
      ],
      "agent_totals": {
        "input_tokens": 5000,
        "output_tokens": 2400,
        "total_tokens": 7400,
        "seconds_running": 1834.2
      },
      "rate_limits": null
    }
    ```

- `GET /api/v1/<issue_identifier>`
  - Returns issue-specific runtime/debug details for the identified issue, including any information
    the implementation tracks that is useful for debugging.
  - Suggested response shape:

    ```json
    {
      "issue_identifier": "MT-649",
      "issue_id": "abc123",
      "status": "running",
      "workspace": {
        "path": "/tmp/symphony_workspaces/MT-649"
      },
      "attempts": {
        "restart_count": 1,
        "current_retry_attempt": 2
      },
      "running": {
        "session_id": "thread-1-turn-1",
        "turn_count": 7,
        "state": "In Progress",
        "started_at": "2026-02-24T20:10:12Z",
        "last_event": "notification",
        "last_message": "Working on tests",
        "last_event_at": "2026-02-24T20:14:59Z",
        "tokens": {
          "input_tokens": 1200,
          "output_tokens": 800,
          "total_tokens": 2000
        }
      },
      "retry": null,
      "logs": {
        "agent_session_logs": [
          {
            "label": "latest",
            "path": "/var/log/symphony/agent/MT-649/latest.log",
            "url": null
          }
        ]
      },
      "recent_events": [
        {
          "at": "2026-02-24T20:14:59Z",
          "event": "notification",
          "message": "Working on tests"
        }
      ],
      "last_error": null,
      "tracked": {}
    }
    ```

  - If the issue is unknown to the current in-memory state, return `404` with an error response (for
    example `{\"error\":{\"code\":\"issue_not_found\",\"message\":\"...\"}}`).

- `POST /api/v1/refresh`
  - Queues an immediate tracker poll + reconciliation cycle (best-effort trigger; implementations
    MAY coalesce repeated requests).
  - Suggested request body: empty body or `{}`.
  - Suggested response (`202 Accepted`) shape:

    ```json
    {
      "queued": true,
      "coalesced": false,
      "requested_at": "2026-02-24T20:15:30Z",
      "operations": ["poll", "reconcile"]
    }
    ```

API design notes:

- The JSON shapes above are the RECOMMENDED baseline for interoperability and debugging ergonomics.
- Implementations MAY add fields, but SHOULD avoid breaking existing fields within a version.
- Endpoints SHOULD be read-only except for operational triggers like `/refresh`.
- Unsupported methods on defined routes SHOULD return `405 Method Not Allowed`.
- API errors SHOULD use a JSON envelope such as `{"error":{"code":"...","message":"..."}}`.
- If the dashboard is a client-side app, it SHOULD consume this API rather than duplicating state
  logic.

## 14. Failure Model and Recovery Strategy

### 14.1 Failure Classes

1. `Workflow/Config Failures`
   - Missing `WORKFLOW.md`
   - Invalid YAML front matter
   - Unsupported tracker kind or missing tracker credentials/project slug
   - Missing coding-agent executable

2. `Workspace Failures`
   - Workspace directory creation failure
   - Workspace population/synchronization failure (implementation-defined; can come from hooks)
   - Invalid workspace path configuration
   - Hook timeout/failure

3. `Agent Session Failures`
   - Startup handshake failure
   - Turn failed/cancelled
   - Turn timeout
   - User input requested and handled as failure by the implementation's documented policy
   - Subprocess exit
   - Stalled session (no activity)

4. `Tracker Failures`
   - API transport errors
   - Non-200 status
   - GraphQL errors
   - malformed payloads

5. `Observability Failures`
   - Snapshot timeout
   - Dashboard render errors
   - Log sink configuration failure

Note: an OPTIONAL extension MAY define additional failure categories outside this core list. For
example, the token budget guards extension (Section 8.8) defines `token_budget_exceeded`, which is
parked rather than retried (Section 14.2).

### 14.2 Recovery Behavior

- Dispatch validation failures:
  - Skip new dispatches.
  - Keep service alive.
  - Continue reconciliation where possible.

- Worker failures:
  - Convert to retries with exponential backoff.

- Token budget exhaustion (OPTIONAL extension, Section 8.8):
  - Park the issue (`token_budget_exceeded`); do not convert to a backoff retry.

- Tracker candidate-fetch failures:
  - Skip this tick.
  - Try again on next tick.

- Reconciliation state-refresh failures:
  - Keep current workers.
  - Retry on next tick.

- Dashboard/log failures:
  - Do not crash the orchestrator.

### 14.3 State Recovery Classes

Every field of the Orchestrator Runtime State (Section 4.1.8) — and any state introduced by an
OPTIONAL extension — MUST be assigned exactly one recovery class, and the assignment MUST be
documented. The class governs what happens to the value across a process restart and when a current
value is unavailable.

- `Reconstructable` (`R`)
  - An authoritative source of truth lives outside the orchestrator (config, tracker state, the VCS,
    or the workspace). The value is rebuilt at startup by reconciliation and polling.
  - MUST NOT be persisted as a primary copy: the external source is authoritative, and a stored copy
    risks diverging from it.
- `Ephemeral` (`E`)
  - No external source of truth, but loss is harmless or self-correcting. The value is reset at
    startup.
  - The reset consequence MUST be documented (for example, retry backoff restarts from the first
    attempt).
- `Cached external signal` (`C`)
  - The authoritative source is an external, account-wide provider interface that is not exposed by
    every agent and is only intermittently reachable.
  - The most recent successfully fetched value (the last-known-good) MUST be carried across both a
    failed refresh and a process restart.
  - A value carries an age; once it is older than its configured staleness bound it is promoted to
    an explicit `UNKNOWN`. `UNKNOWN` MUST be represented distinctly from any in-band value — in
    particular it MUST NOT be modeled as `0`.
  - Behavior on `UNKNOWN` is a configured policy: fail-open (proceed) or fail-closed (pause). An
    implementation MAY distinguish a permanently `UNKNOWN` signal (the agent exposes no such
    interface) from a transiently `UNKNOWN` one (a temporary block); a permanently `UNKNOWN` signal
    SHOULD default to fail-open.
- `Durable` (`D`)
  - Symphony-attributed accounting with no external source, where resetting the value is harmful
    (for example, it would grant a partially-spent issue a fresh budget).
  - The value MUST be persisted and restored before any decision that enforces on it. Re-applying a
    usage report MUST be idempotent — keyed by an absolute snapshot rather than added
    incrementally — so a restart can neither double-count nor lose spend.
  - Durable storage is OPTIONAL. When no store is configured, the implementation MUST document its
    degradation (for example, decline enforcement, or fall back to `Ephemeral` with the stated risk
    that the counter resets on restart).

`Reconstructable` and `Ephemeral` are the default character of the service; `Durable` is the narrow
exception that an OPTIONAL accounting or budgeting extension introduces, and `Cached external
signal` is introduced by an OPTIONAL provider-quota extension. Core conformance requires only that
every runtime-state field has a documented class; it does not require any durable store.

### 14.4 Partial State Recovery (Restart)

Scheduler state is `Reconstructable` or `Ephemeral` (Section 14.3) and is therefore held in memory:
it is rebuilt or reset at startup rather than restored from a durable store. Only `Durable` state
introduced by an OPTIONAL extension is restored across a restart.
Restart recovery means the service can resume useful operation by polling tracker state and reusing
preserved workspaces. It does not mean retry timers, running sessions, or live worker state survive
process restart.

After restart:

- No retry timers are restored from prior process memory.
- No running sessions are assumed recoverable.
- Any `Durable` state (Section 14.3) configured by an OPTIONAL extension is restored from its store
  before that extension enforces on it; with no store, the extension degrades as documented.
- Service recovers by:
  - startup terminal workspace cleanup
  - fresh polling of active issues
  - re-dispatching eligible work

### 14.5 Operator Intervention Points

Operators can control behavior by:

- Editing `WORKFLOW.md` (prompt and most runtime settings).
- `WORKFLOW.md` changes are detected and re-applied automatically without restart according to
  Section 6.2.
- Changing issue states in the tracker:
  - terminal state -> running session is stopped and workspace cleaned when reconciled
  - non-active state -> running session is stopped without cleanup
- Restarting the service for process recovery or deployment (not as the normal path for applying
  workflow config changes).

## 15. Security and Operational Safety

### 15.1 Trust Boundary Assumption

Each implementation defines its own trust boundary.

Operational safety requirements:

- Implementations SHOULD state clearly whether they are intended for trusted environments, more
  restrictive environments, or both.
- Implementations SHOULD state clearly whether they rely on auto-approved actions, operator
  approvals, stricter sandboxing, or some combination of those controls.
- Workspace isolation and path validation are important baseline controls, but they are not a
  substitute for whatever approval and sandbox policy an implementation chooses.
- The coding agent runs inside the sandbox defined in Section 9.6, and credentials stay outside it;
  privileged side effects happen only through the broker (Section 10.8).

### 15.2 Filesystem Safety Requirements

Mandatory:

- Workspace path MUST remain under configured workspace root.
- Coding-agent cwd MUST be the per-issue workspace path for the current run.
- Workspace directory names MUST use sanitized identifiers.

RECOMMENDED additional hardening for ports:

- Run under a dedicated OS user.
- Restrict workspace root permissions.
- Mount workspace root on a dedicated volume if possible.

### 15.3 Secret Handling

- Secrets are resolved through a secret-provider interface. A file provider (reading from a
  permission-restricted path) is REQUIRED; additional providers (OS keyring, external secret
  managers) MAY be offered as extensions. Environment variables MUST NOT be used as a secret channel
  into the agent.
- Secrets MUST NOT cross into the agent sandbox: not through its environment, its filesystem, or the
  broker channel. Symphony MAY consume standard credential mechanisms (including environment
  variables and tool-native credential files) in its own process, but MUST scrub every
  secret-bearing environment variable before starting the agent sandbox.
- `$VAR` indirection is retained only for non-secret path values, not for secrets.
- Do not log API tokens or secret values.
- Validate presence of secrets without printing them.

### 15.4 Hook Script Safety

Hooks exist at two trust levels (Section 5.3.4).

Implications:

- Policy-config hooks are operator-owned, trusted, and run on the host outside the sandbox.
- `WORKFLOW.md` hooks are repo-owned, untrusted, and MUST NOT be granted credentials or host access;
  they run inside the sandbox (Section 9.6).
- Hooks run with the workspace directory as their working directory.
- Hook output SHOULD be truncated in logs.
- Hook timeouts are REQUIRED to avoid hanging the orchestrator.

### 15.5 Harness Hardening Guidance

Running coding agents against repositories, issue trackers, and other inputs that can contain
sensitive data or externally-controlled content can be dangerous. A permissive deployment can lead
to data leaks, destructive mutations, or full machine compromise if the agent is induced to execute
harmful commands or use overly-powerful integrations.

Implementations SHOULD explicitly evaluate their own risk profile and harden the execution harness
where appropriate. This specification intentionally does not mandate a single hardening posture, but
implementations SHOULD NOT assume that tracker data, repository contents, prompt inputs, or tool
arguments are fully trustworthy just because they originate inside a normal workflow.

Possible hardening measures include:

- Tightening the selected adapter's approval and sandbox settings described elsewhere in this
  specification instead of running with a maximally permissive configuration.
- Adding external isolation layers such as OS/container/VM sandboxing, network restrictions, or
  separate credentials beyond the adapter's built-in policy controls.
- Filtering which Linear issues, projects, teams, labels, or other tracker sources are eligible for
  dispatch so untrusted or out-of-scope tasks do not automatically reach the agent.
- Constraining brokered tracker operations to the intended project/issue scope, rather than exposing
  general workspace-wide tracker access (the broker enforces authorization scope by default; see
  Section 10.8).
- Reducing the set of client-side tools, credentials, filesystem paths, and network destinations
  available to the agent to the minimum needed for the workflow.

The correct controls are deployment-specific, but implementations SHOULD document them clearly and
treat harness hardening as part of the core safety model rather than an optional afterthought.

## 16. Reference Algorithms (Language-Agnostic)

### 16.1 Service Startup

```text
function start_service():
  configure_logging()
  start_observability_outputs()
  start_workflow_watch(on_change=reload_and_reapply_workflow)

  state = {
    poll_interval_ms: get_config_poll_interval_ms(),
    max_concurrent_agents: get_config_max_concurrent_agents(),
    running: {},
    claimed: set(),
    retry_attempts: {},
    completed: set(),
    agent_totals: {input_tokens: 0, output_tokens: 0, total_tokens: 0, seconds_running: 0},
    provider_rate_limits: null
  }

  state = restore_cached_and_durable_state(state)

  validation = validate_dispatch_config()
  if validation is not ok:
    log_validation_error(validation)
    fail_startup(validation)

  startup_terminal_workspace_cleanup()
  schedule_tick(delay_ms=0)

  event_loop(state)
```

`restore_cached_and_durable_state` overlays class `Cached external signal` and `Durable` fields
(Section 14.3) from their store when an OPTIONAL extension configures one; otherwise the zero/null
defaults above stand.

### 16.2 Poll-and-Dispatch Tick

```text
on_tick(state):
  state = reconcile_running_issues(state)

  validation = validate_dispatch_config()
  if validation is not ok:
    log_validation_error(validation)
    notify_observers()
    schedule_tick(state.poll_interval_ms)
    return state

  issues = tracker.fetch_candidate_issues()
  if issues failed:
    log_tracker_error()
    notify_observers()
    schedule_tick(state.poll_interval_ms)
    return state

  for issue in sort_for_dispatch(issues):
    if no_available_slots(state):
      break

    if should_dispatch(issue, state):
      state = dispatch_issue(issue, state, attempt=null)

  notify_observers()
  schedule_tick(state.poll_interval_ms)
  return state
```

### 16.3 Reconcile Active Runs

```text
function reconcile_running_issues(state):
  state = reconcile_stalled_runs(state)

  running_ids = keys(state.running)
  if running_ids is empty:
    return state

  refreshed = tracker.fetch_issue_states_by_ids(running_ids)
  if refreshed failed:
    log_debug("keep workers running")
    return state

  for issue in refreshed:
    if issue.state in terminal_states:
      state = terminate_running_issue(state, issue.id, cleanup_workspace=true)
    else if issue.state in active_states:
      state.running[issue.id].issue = issue
    else:
      state = terminate_running_issue(state, issue.id, cleanup_workspace=false)

  return state
```

### 16.4 Dispatch One Issue

```text
function dispatch_issue(issue, state, attempt):
  worker = spawn_worker(
    fn -> run_agent_attempt(issue, attempt, parent_orchestrator_pid) end
  )

  if worker spawn failed:
    return schedule_retry(state, issue.id, next_attempt(attempt), {
      identifier: issue.identifier,
      error: "failed to spawn agent"
    })

  state.running[issue.id] = {
    worker_handle,
    monitor_handle,
    identifier: issue.identifier,
    issue,
    session_id: null,
    pid: null,
    last_message: null,
    last_event: null,
    last_timestamp: null,
    input_tokens: 0,
    output_tokens: 0,
    total_tokens: 0,
    last_reported_input_tokens: 0,
    last_reported_output_tokens: 0,
    last_reported_total_tokens: 0,
    retry_attempt: normalize_attempt(attempt),
    started_at: now_utc()
  }

  state.claimed.add(issue.id)
  state.retry_attempts.remove(issue.id)
  return state
```

### 16.5 Worker Attempt (Workspace + Prompt + Agent)

```text
function run_agent_attempt(issue, attempt, orchestrator_channel):
  workspace = workspace_manager.provision_for_issue(issue)  # VCS worktree or bare dir
  if workspace failed:
    fail_worker("workspace error")

  # Bring the work branch up to date with base; postpone if it would conflict (resolved later
  # only if a push is rejected). See Section 9.8.
  vcs.attempt_clean_backmerge(issue, workspace)

  if run_hook("before_run", workspace.path) failed:
    fail_worker("before_run hook error")

  max_turns = config.agent.max_turns
  turn_number = 1
  continuation_ref = null  # first turn establishes the session lazily (Section 10.7)

  while true:
    # During each turn the agent uses the symphony broker CLI for privileged operations
    # (push, pull request, tracker writes); Symphony executes them host-side (Sections 10.8, 9.9).
    # First turn: full task prompt; continuation turns: continuation guidance (Section 10.3).
    prompt = build_turn_prompt(workflow_template, issue, attempt, turn_number, max_turns)
    if prompt failed:
      agent.release(continuation_ref)
      run_hook_best_effort("after_run", workspace.path)
      fail_worker("prompt error")

    turn_result = agent.run_turn(
      workspace=workspace.path,
      prompt=prompt,
      issue=issue,
      continuation_ref=continuation_ref,
      on_event=(msg) -> send(orchestrator_channel, {agent_update, issue.id, msg})
    )

    if turn_result failed:
      agent.release(continuation_ref)
      run_hook_best_effort("after_run", workspace.path)
      fail_worker("agent turn error")

    continuation_ref = turn_result.continuation_ref

    refreshed_issue = tracker.fetch_issue_states_by_ids([issue.id])
    if refreshed_issue failed:
      agent.release(continuation_ref)
      run_hook_best_effort("after_run", workspace.path)
      fail_worker("issue state refresh error")

    issue = refreshed_issue[0] or issue

    if issue.state is not active:
      break

    if turn_number >= max_turns:
      break

    turn_number = turn_number + 1

  agent.release(continuation_ref)
  run_hook_best_effort("after_run", workspace.path)

  exit_normal()
```

### 16.6 Worker Exit and Retry Handling

```text
on_worker_exit(issue_id, reason, state):
  running_entry = state.running.remove(issue_id)
  state = add_runtime_seconds_to_totals(state, running_entry)

  if reason == normal:
    state.completed.add(issue_id)  # bookkeeping only
    state = schedule_retry(state, issue_id, 1, {
      identifier: running_entry.identifier,
      delay_type: continuation
    })
  else:
    state = schedule_retry(state, issue_id, next_attempt_from(running_entry), {
      identifier: running_entry.identifier,
      error: format("worker exited: %reason")
    })

  notify_observers()
  return state
```

```text
on_retry_timer(issue_id, state):
  retry_entry = state.retry_attempts.pop(issue_id)
  if missing:
    return state

  candidates = tracker.fetch_candidate_issues()
  if fetch failed:
    return schedule_retry(state, issue_id, retry_entry.attempt + 1, {
      identifier: retry_entry.identifier,
      error: "retry poll failed"
    })

  issue = find_by_id(candidates, issue_id)
  if issue is null:
    state.claimed.remove(issue_id)
    return state

  if available_slots(state) == 0:
    return schedule_retry(state, issue_id, retry_entry.attempt + 1, {
      identifier: issue.identifier,
      error: "no available orchestrator slots"
    })

  return dispatch_issue(issue, state, attempt=retry_entry.attempt)
```

## 17. Test and Validation Matrix

A conforming implementation SHOULD include tests that cover the behaviors defined in this
specification.

Validation profiles:

- `Core Conformance`: deterministic tests REQUIRED for all conforming implementations.
- `Extension Conformance`: REQUIRED only for OPTIONAL features that an implementation chooses to
  ship.
- `Real Integration Profile`: environment-dependent smoke/integration checks RECOMMENDED before
  production use.

Unless otherwise noted, Sections 17.1 through 17.7 are `Core Conformance`. Bullets that begin with
`If ... is implemented` are `Extension Conformance`.

### 17.1 Workflow and Config Parsing

- Workflow file path precedence:
  - explicit runtime path is used when provided
  - cwd default is `WORKFLOW.md` when no explicit runtime path is provided
- Workflow file changes are detected and trigger re-read/re-apply without restart
- Invalid workflow reload keeps last known good effective configuration and emits an
  operator-visible error
- Policy config and `WORKFLOW.md` load as separate artifacts; `WORKFLOW.md` carries only in-sandbox
  settings (prompt and in-sandbox hooks)
- Policy-config changes are detected and re-applied without restart, with last-known-good on invalid
  reload
- Missing `WORKFLOW.md` returns typed error
- Invalid YAML front matter returns typed error
- Front matter non-map returns typed error
- Config defaults apply when OPTIONAL values are missing
- `tracker.kind` validation enforces currently supported kind (`linear`)
- `tracker.api_key` resolves through the secret provider (file provider)
- Secret-provider resolution works for tracker auth; `$VAR` resolution works for non-secret path
  values only
- `~` path expansion works
- `codex.command` is preserved as a shell command string
- Per-state concurrency override map normalizes state names and ignores invalid values
- Prompt template renders `issue` and `attempt`
- Prompt rendering fails on unknown variables (strict mode)

### 17.2 Workspace Manager and Safety

- Deterministic workspace path per issue identifier
- Missing workspace directory is created
- Existing workspace directory is reused
- Existing non-directory path at workspace location is handled safely (replace or fail per
  implementation policy)
- OPTIONAL workspace population/synchronization errors are surfaced
- `after_create` hook runs only on new workspace creation
- `before_run` hook runs before each attempt and failure/timeouts abort the current attempt
- `after_run` hook runs after each attempt and failure/timeouts are logged and ignored
- `before_remove` hook runs on cleanup and failures/timeouts are ignored
- Workspace path sanitization and root containment invariants are enforced before agent launch
- Agent launch uses the per-issue workspace path as cwd and rejects out-of-root paths
- Agent launch wraps the session in the configured sandbox (strict profile by default)
- The per-run broker socket is mounted into the sandbox and bound to one run; without it the broker
  is unreachable
- Secret-bearing environment variables are scrubbed before the sandbox starts
- VCS-managed workspaces are provisioned as worktrees of a shared per-repo object store
- The agent does local git including commit; Symphony performs fetch/branch/back-merge/push/PR
- The work branch is Symphony-derived (`symphony/<identifier>`) and the push refspec is pinned to it
- Back-merge is attempted at run start and postponed on conflict; conflict resolution is required
  only on push-reject
- One pull request per issue is created then updated; the agent supplies title/body, base from
  policy

### 17.3 Issue Tracker Client

- At least the `linear` and `forgejo` tracker adapters implement the read and write operations
- Tracker writes (`add_comment`, `set_state`, `link_pull_request`) are performed by the broker with
  agent-supplied content
- Writes are gated by a static adapter capability descriptor (reads REQUIRED); an unsupported write
  surfaces `tracker_unsupported_operation` and is never silently no-oped; non-empty
  `tracker.transitions` without the `set_state` capability is a preflight configuration error
- Tracker transitions follow a deterministic policy graph (`tracker.transitions`) keyed on milestone
  signals and observed run outcomes; an unmatched trigger transitions nothing and a duplicate
  `(from, on)` is a configuration error
- Candidate issue fetch uses active states and project slug
- Linear query uses the specified project filter field (`slugId`)
- Empty `fetch_issues_by_states([])` returns empty without API call
- Pagination preserves order across multiple pages
- Blockers are normalized from Linear inverse relations of type `blocks`; `blocked_by`/`branch_name`
  are tracker-dependent, and an empty `blocked_by` applies no blocker gating
- Labels are normalized to lowercase
- `metadata` carries adapter-defined provider-specific fields the flat model does not capture
- Issue state refresh by ID returns minimal normalized issues
- Issue state refresh query uses GraphQL ID typing (`[ID!]`) as specified in Section 11.2
- Error mapping covers transport failures, unsuccessful status, backend-reported errors, and
  malformed payloads (the transport-neutral categories of Section 11.4)

### 17.4 Orchestrator Dispatch, Reconciliation, and Retry

- One instance can manage multiple repositories; each issue routes to exactly one repository via the
  policy mapping
- A tracker shared by several repositories is polled once per cycle and its issues are routed
- Workspace and concurrency identity are keyed by (repository, issue)
- Dispatch sort order is priority then oldest creation time
- `Todo` issue with non-terminal blockers is not eligible
- `Todo` issue with terminal blockers is eligible
- Active-state issue refresh updates running entry state
- Non-active state stops running agent without workspace cleanup
- Terminal state stops running agent and cleans workspace
- Reconciliation with no running issues is a no-op
- Normal worker exit schedules a short continuation retry (attempt 1)
- Abnormal worker exit increments retries with 10s-based exponential backoff
- Retry backoff cap uses configured `agent.max_retry_backoff_ms`
- Retry queue entries include attempt, due time, identifier, and error
- Stall detection kills stalled sessions and schedules retry
- Slot exhaustion requeues retries with explicit error reason
- If a snapshot API is implemented, it returns running rows, retry rows, token totals, and rate
  limits
- If a snapshot API is implemented, timeout/unavailable cases are surfaced
- Every Orchestrator Runtime State field has a documented recovery class (`Reconstructable` /
  `Ephemeral` / `Cached external signal` / `Durable`, Section 14.3)
- If a `Durable` or `Cached external signal` extension is implemented, restart restores its state
  before enforcement, `UNKNOWN` is never represented as `0`, and the last-known-good value
  survives a restart
- If token budget guards are implemented, a per-session/per-issue cap aborts and requeues only that
  issue while a global cap pauses new dispatch without terminating running workers
- If token budget guards are implemented, a `token_budget_exceeded` outcome is parked rather than
  retried via backoff, the durable counter is re-seeded idempotently on restart, and the soft
  warning fires once
- If provider quota backpressure is implemented, a bucket at or above `dispatch_pause_percent`
  pauses new dispatch only, leaving running workers and reconciliation untouched, with implicit
  resume
- If provider quota backpressure is implemented, the quota snapshot is normalized across providers,
  `UNKNOWN` is never represented as `0`, last-known-good survives a restart, and the `UNKNOWN`
  policy (fail-open vs fail-closed; unsupported vs blocked) is honored

### 17.5 Coding-Agent Adapters

- At least the `codex` and `claude_code` adapters implement the neutral runner contract
- Agent and effort are selected from policy (`default_agent`/`default_effort`); `agent_by_label`
  overrides per issue, and `effort` is passed through as the agent's native value
- `run_turn` threads an opaque `continuation_ref` (first turn full prompt; continuation turns
  guidance); there is no separate session-start operation
- `cancel` stops an in-flight turn; a clean interrupt-then-drain yields a resumable
  `continuation_ref`, otherwise the turn fails; `release` frees warm resources at run end
- Each adapter advertises a capability descriptor (`resume` mode, native step cap, accepted
  `effort` values)
- Emitted usage is normalized to the neutral token-usage record (`input_tokens`, `output_tokens`,
  `total_tokens`)
- An adapter encapsulates one (agent, transport) pairing; no non-native agent impersonates another's
  protocol
- Launch command uses workspace cwd and invokes `bash -lc <codex.command>`
- Session startup follows the targeted Codex app-server protocol.
- Client identity/capability payloads are valid when the targeted Codex app-server protocol requires
  them.
- Policy-related startup payloads use the implementation's documented approval/sandbox settings
- Thread and turn identities exposed by the targeted protocol are extracted and used to emit
  `session_started`
- Request/response read timeout is enforced
- Turn timeout is enforced
- Transport framing required by the targeted protocol is handled correctly
- For stdio-based transports, diagnostic stderr handling is kept separate from the protocol stream
- Command/file-change approvals are handled according to the implementation's documented policy
- Unsupported dynamic tool calls are rejected without stalling the session
- User input requests are handled according to the implementation's documented policy and do not
  stall indefinitely
- Usage and rate-limit telemetry exposed by the targeted protocol is extracted
- Approval, user-input-required, usage, and rate-limit signals are interpreted according to the
  targeted protocol
- The `symphony` broker CLI is reachable from the sandbox over the per-run socket and is unreachable
  without it
- Brokered operations return structured results with stable reason codes
- A `scope_denied` result fails the run rather than being retried around
- Privileged operations are not exposed as in-protocol client-side tools

### 17.6 Observability

- Validation failures are operator-visible
- Structured logging includes issue/session context fields
- Logging sink failures do not crash orchestration
- Token/rate-limit aggregation remains correct across repeated agent updates
- If a human-readable status surface is implemented, it is driven from orchestrator state and does
  not affect correctness
- If humanized event summaries are implemented, they cover key wrapper/agent event classes without
  changing orchestrator behavior
- If a per-execution usage ledger is implemented, appends are idempotent under retries, reconnects,
  and the end-of-session snapshot via high-water-mark summarization per `(issue_identifier,
  session_id)`
- If a per-execution usage ledger is implemented, write failures are logged without crashing
  orchestration and reads skip truncated/malformed/unrecognized-`schema_version` lines

### 17.7 CLI and Host Lifecycle

- CLI accepts a positional workflow path argument (`path-to-WORKFLOW.md`)
- CLI uses `./WORKFLOW.md` when no workflow path argument is provided
- CLI errors on nonexistent explicit workflow path or missing default `./WORKFLOW.md`
- CLI surfaces startup failure cleanly
- CLI exits with success when application starts and shuts down normally
- CLI exits nonzero when startup fails or the host process exits abnormally

### 17.8 Real Integration Profile (RECOMMENDED)

These checks are RECOMMENDED for production readiness and MAY be skipped in CI when credentials,
network access, or external service permissions are unavailable.

- A real tracker smoke test can be run with valid credentials supplied by `LINEAR_API_KEY` or a
  documented local bootstrap mechanism (for example `~/.linear_api_key`).
- Real integration tests SHOULD use isolated test identifiers/workspaces and clean up tracker
  artifacts when practical.
- A skipped real-integration test SHOULD be reported as skipped, not silently treated as passed.
- If a real-integration profile is explicitly enabled in CI or release validation, failures SHOULD
  fail that job.

## 18. Implementation Checklist (Definition of Done)

Use the same validation profiles as Section 17:

- Section 18.1 = `Core Conformance`
- Section 18.2 = `Extension Conformance`
- Section 18.3 = `Real Integration Profile`

### 18.1 REQUIRED for Conformance

- Workflow path selection supports explicit runtime path and cwd default
- `WORKFLOW.md` loader with YAML front matter + prompt body split
- Typed config layer with defaults, secret-provider resolution, and `$` expansion for non-secret
  paths
- Two configuration artifacts: operator-owned policy config (privileged) and repo-owned
  `WORKFLOW.md` (in-sandbox only); dynamic watch/reload/re-apply for both
- Polling orchestrator with single-authority mutable state
- Issue tracker client with candidate fetch + state refresh + terminal fetch
- Workspace manager with sanitized per-issue workspaces
- Workspace lifecycle hooks at two trust levels (policy-config hooks on the host; `WORKFLOW.md`
  hooks in the sandbox)
- Hook timeout config (`hooks.timeout_ms`, default `60000`)
- Neutral agent runner contract with at least the `codex` and `claude_code` adapters (Codex
  app-server JSON line protocol as the worked example)
- Turn-centric contract: `run_turn` threads an opaque `continuation_ref` (no separate start),
  `cancel` does interrupt-then-drain to a resumable state or fails the turn, `release` frees warm
  resources; adapters emit the neutral event vocabulary and token-usage record (`input_tokens`,
  `output_tokens`, `total_tokens`) and advertise a capability descriptor (resume mode, native step
  cap, accepted effort); one adapter per (agent, transport) with no protocol impersonation
- Agent and effort selected from policy (`default_agent`/`default_effort`) with `agent_by_label`
  per-issue overrides
- VCS adapter (`github`, `forgejo`) owning provisioning, push, back-merge, and one-PR-per-issue,
  with a Symphony-derived work branch and configurable authorship
- Tracker adapter (`linear`, `forgejo`) with reads and writes; Symphony-driven lifecycle via a
  policy-owned transition graph (`tracker.transitions`) keyed on agent milestone signals and
  observed run outcomes; each adapter advertises a static write-capability descriptor and an
  unsupported write surfaces `tracker_unsupported_operation` rather than a silent no-op
- Multiple repositories per instance with tracker-specific issue→repo routing and shared per-tracker
  polling; workspace/concurrency keyed by (repository, issue)
- Privileged Operation Broker (`symphony` CLI) over a per-run socket, with authorization scope and
  structured results (`scope_denied` fails the run)
- Per-run agent sandbox with a configurable profile (strict default), secret-bearing env scrubbed
  before start, and the broker socket as the only privileged channel
- Codex adapter launch command config (`codex.command`, default `codex app-server`)
- Strict prompt rendering with `issue` and `attempt` variables
- Exponential retry queue with continuation retries after normal exit
- Configurable retry backoff cap (`agent.max_retry_backoff_ms`, default 5m)
- Reconciliation that stops runs on terminal/non-active tracker states
- Every Orchestrator Runtime State field is assigned and documented as a recovery class
  (`Reconstructable` / `Ephemeral` / `Cached external signal` / `Durable`, Section 14.3)
- Workspace cleanup for terminal issues (startup sweep + active transition)
- Structured logs with `issue_id`, `issue_identifier`, and `session_id`
- Operator-visible observability (structured logs; OPTIONAL snapshot/status surface)

### 18.2 RECOMMENDED Extensions (Not REQUIRED for Conformance)

- HTTP server extension honors CLI `--port` over `server.port`, uses a safe default bind host, and
  exposes the baseline endpoints/error semantics in Section 13.8 if shipped.
- Durable state across restarts is governed by the recovery-class taxonomy (Section 14.3): the retry
  queue stays `Ephemeral` (backoff restarts after a restart), and durably persisting session
  accounting is the `Durable` class an OPTIONAL budgeting extension provides rather than a core
  requirement.
- Per-execution usage ledger extension (Section 13.6): an append-only, durable record of token usage
  keyed by `(issue_identifier, session_id)` and summarized by high-water mark, doubling as the
  RECOMMENDED realization of the `Durable` recovery class (Section 14.3).
- Token budget guards extension (Section 8.8): per-session / per-issue / global token caps with
  distinct exhaustion semantics (abort-and-requeue vs pause-dispatch), a parked
  `token_budget_exceeded` category, durable idempotent counters, and a deferred cost/currency layer.
- Provider quota backpressure extension (Section 8.9): a normalized provider-quota snapshot (class
  `Cached external signal`) fed in-band or by an OPTIONAL poller, with a dispatch-only pause above a
  threshold, implicit resume, and a configurable fail-open/closed policy on `UNKNOWN`.
- TODO: Make observability settings configurable in workflow front matter without prescribing UI
  implementation details.

### 18.3 Operational Validation Before Production (RECOMMENDED)

- Run the `Real Integration Profile` from Section 17.8 with valid credentials and network access.
- Verify hook execution and workflow path resolution on the target host OS/shell environment.
- If the OPTIONAL HTTP server is shipped, verify the configured port behavior and loopback/default
  bind expectations on the target environment.
