# Symphony Conformance Data

Machine-readable conformance data for Symphony, derived from `SPEC.md`. Two artifacts with different
jobs:

- `vocabulary.json` — the token registry (decision 0071). What the names are.
- `vectors/*.json` — behavior vectors making the deterministic subset of `SPEC.md` Section 17's test
  matrix an objective pass/fail (decisions 0046, 0048). What Symphony does.

Both serve the shared enforcement the multi-implementation strategy needs: an implementation
generates or checks its token spellings from the registry and runs the corpus against its own
binary, reporting the result in its Conformance Statement (see
`CONFORMANCE-STATEMENT-TEMPLATE.md`, Section 7 evidence).

`SPEC.md` governs both artifacts. Every value is read from the sections its `spec_refs` cite;
where a value cannot be read, no entry is authored and the gap is recorded under "Surfaced findings"
below.

The engine's own conformance data derives from `VCSX-SPEC.md` and lives in `vcsx/`.

## Layout

- `vocabulary.json` — the token registry.
- `vectors/*.json` — one file per behavior, each a self-contained set of input/output vectors.

---

## Token Registry (`vocabulary.json`)

`SPEC.md` names token sets an implementation is expected to spell exactly — the emitted runtime
events (Section 10.4), the REQUIRED log context fields (Section 13.1), the neutral token-usage
record (Sections 4.1.6, 13.5), the usage-ledger entry fields (Section 13.6), the state recovery
classes and their per-field assignments (Sections 14.3, 4.1.8), and the configuration namespaces
(Sections 5.3, 18.2). Each was prose, so an implementation spelled them itself and an upstream
rename changed nothing downstream until someone read a re-pin diff.

`vocabulary.json` is those sets as data, so a spelling can be generated or checked instead of
transcribed. It is the same artifact `vcsx/vocabulary.json` is for the engine (decision 0051), on
the same terms.

### Precedence

**`SPEC.md` governs. This file is derived.**

Every entry is read from the sections its `spec_refs` cite; nothing here is invented, and no entry
restates a requirement's substance. Entries carry names and the properties the specification fixes
about them — a ledger field's type, a runtime-state field's recovery class, a namespace's owning
artifact — not the prose of the rules those properties feed.

Where this file and `SPEC.md` disagree, the specification is right and this file is a bug. If the
registry ever needs a property the prose does not fix, that is the signal it has stopped being a
derived view; move the concept into `SPEC.md` and re-derive rather than letting the registry lead.

### Schema

A single JSON object. Top-level keys are metadata (`artifact`, `schema_version`, `governed_by`,
`description`, `spec_refs`) plus one object per token group.

Each group carries:

- `spec_refs` (array of strings) — the sections the group is read from, verbatim.
- `note` (string, OPTIONAL) — a constraint the specification states about the group as a whole.
- `exhaustive` (boolean, OPTIONAL) — present and `false` where the specification states the set is
  open. A generated type for such a group MUST admit an unknown token rather than closing the enum.
- `key` (array of strings, OPTIONAL) — the fields the specification keys the record by.
- `entries` — the tokens. Either an array of strings, or an array of objects whose `token` field is
  the token and whose remaining fields are the properties the specification fixes about it.

In `config_namespaces`, `artifact` names the Section 5 configuration artifact a key belongs to:
`operator_policy_config`, `repo_policy_toml`, `workflow_md`, or `repository_owned` where the
specification splits one key across both repository-owned artifacts by trust (Section 15.4).

### Using it

- **An implementation** generates or checks its event enum, log-context fields, ledger schema, and
  recovery-class taxonomy from this file, so a token change upstream becomes a build failure rather
  than a silent divergence. Record in the Conformance Statement whether it was checked against, and
  at which revision.
- **A reviewer** of a change to `SPEC.md` verifies that every token added, renamed, or removed is
  reflected here in the same change.
- **A Conformance Statement author** reads `runtime_state_fields` for the "Spec default" column of
  its recovery-class table, and `config_namespaces` for the namespace column of its extensions
  table.

### What the slice covers

| Group | Derived from |
|-------|--------------|
| `events`, `event_envelope_fields` | Sections 10.4, 10.7 |
| `log_context_fields` | Sections 13.1, 18.1.1 |
| `token_usage_fields` | Sections 4.1.6, 10.7, 13.5 |
| `ledger_entry_fields` | Section 13.6 |
| `recovery_classes` | Section 14.3 |
| `runtime_state_fields` | Sections 4.1.8, 14.3 |
| `config_namespaces` | Sections 5.3, 5.6, 18.2, and the extension section owning each key |

Two groups are explicitly **not** closed sets, and say so with `exhaustive: false`: `events`,
because Section 10.4 permits an adapter to emit events the specification does not name, and
`config_namespaces`, because Section 5.3 permits an extension to define additional top-level keys.
In both, the names the specification does state are fixed; it is the set that is open.

### Deferred to later slices

Token sets that are conformance-relevant but need their own derivation work, and are not authored
here rather than guessed at:

- **Error and category codes** — the workflow/config errors (Section 5.5), the transport-neutral
  tracker error categories (Section 11.4), the brokered-result reason codes including `scope_denied`
  (Section 10.8), and the agent-runner error mapping (Section 10.6). Several are RECOMMENDED rather
  than REQUIRED spellings, which is a distinction the registry would have to carry per entry.
- **Orchestration states and transition triggers** (Sections 7.1, 7.3, 11.6) — the trigger
  vocabulary is shared with the engine's action-policy machine, so the two registries would have to
  agree on which document owns each token.
- **Failure classes** (Section 14.1) — named in prose as classes rather than as tokens an
  implementation emits.
- **Snapshot and API response shapes** (Sections 13.3, 13.8.2) — RECOMMENDED baselines an
  implementation MAY extend, not a fixed vocabulary.

---

## Behavior Vectors (`vectors/*.json`)

The corpus grows in **slices**. Every slice so far covers only pure, host-independent behavior — no
sandbox, tracker, engine, filesystem, or network — so every implementation can run it on day one
with no harness infrastructure. Integration-dependent behaviors are deferred (see "Deferred" below).

## Vector file schema

Each file is a JSON object:

- `function` (string) — the behavior under test. The harness dispatches on this name.
- `profile` (string) — the Section 17 validation profile the behavior belongs to
  (`Core Conformance` or `Daemon Conformance`).
- `spec_refs` (array of strings) — the `SPEC.md` sections the expected outputs are derived from,
  verbatim. Expected values are never invented; they are read from these sections.
- `description` (string) — what the function computes.
- `given` / `expect` (strings at the file level) — the human-readable shape of a vector's input and
  output for this function.
- `vectors` (array) — each with:
  - `id` (string) — unique within the file.
  - `description` (string, OPTIONAL) — what the case demonstrates.
  - `given` (object) — the inputs.
  - `expect` (object) — the expected outputs: either the successful result, or `{ error: <class> }`
    naming the error class the behavior must raise for a failure vector.

## Harness contract (language-neutral)

A conforming harness is small and written in each implementation's own language. For every file and
every vector it MUST:

1. Invoke the implementation's realization of `function` with `given`.
2. Assert the result equals `expect` — or, when `expect` names an `error`, that the behavior fails
   and raises that error class.

Some functions carry an interpretation note beyond plain equality:

- `sort_for_dispatch` — `given.issues` is an unordered list; `expect.order` is the list of
  `identifier`s in the required dispatch order. Assert the produced order equals it.
- `resolve_config_defaults` — `expect.resolved` is a map of dotted config paths to values. Assert
  the resolved config equals each listed path; paths **not** listed are unconstrained (so
  Implementation-defined defaults are never pinned).
- `render_prompt` — `expect` is either `{ rendered: <string> }` (assert the rendered string equals
  it) or `{ error: <class> }` (assert rendering fails with that error class). Templates use
  Liquid-compatible syntax (Section 5.4).

The harness itself is not specified here — only the contract above. The corpus prescribes no test
framework, assertion library, or file-loading mechanism.

## What the corpus covers

Slice 1 — pure derivations (decision 0046):

| File | Function | Profile | Derived from |
|------|----------|---------|--------------|
| `vectors/workspace-key.json` | `sanitize_workspace_key` | Core | Sections 4.2, 9.5 |
| `vectors/state-normalization.json` | `normalize_state` | Core | Section 4.2 |
| `vectors/config-defaults.json` | `resolve_config_defaults` | Core | Sections 6.4, 17.1 |
| `vectors/retry-backoff.json` | `retry_backoff_delay_ms` | Daemon | Section 8.4 |
| `vectors/available-slots.json` | `available_slots` | Daemon | Section 8.3 |
| `vectors/per-state-concurrency.json` | `per_state_concurrency_limit` | Daemon | Sections 8.3, 4.2 |
| `vectors/dispatch-ordering.json` | `sort_for_dispatch` | Daemon | Sections 8.2, 16.2 |

Slice 2 — prompt rendering (decision 0048):

| File | Function | Profile | Derived from |
|------|----------|---------|--------------|
| `vectors/prompt-rendering.json` | `render_prompt` | Daemon | Sections 5.4, 5.5, 12.2 |

## Deferred to later slices

These behaviors are conformance-relevant but not purely deterministic from inputs alone; they need a
harness with fixtures or live services and belong with the `Real Integration Profile` (Section 17.8):

- Config **secret-provider resolution** and `$VAR` / `~` expansion (Section 17.1) — I/O-bound.
- **Workspace safety invariants** (Section 9.5, Invariants 1–2: cwd and root containment) — filesystem
  and process state.
- **Tracker read/write** surfaces, candidate eligibility over live issues (Section 8.2, 11).
- **Action-policy machine** outcomes and **message formulation** (Sections 9.8–9.12) — engine-side,
  covered by `VCSX-SPEC.md`'s own matrix.

## Surfaced findings

Authoring vectors and registry entries exercises `SPEC.md` and surfaces under-specification. Per the
multi-implementation decision-log hygiene rule, a genuine gap becomes a decision rather than a
guessed-at vector or entry:

- **Non-ASCII workspace-key sanitization — resolved (decision 0047).** Section 9.5 Invariant 3 did
  not fix whether "character" is a byte, a Unicode code point, or a grapheme, so a precomposed vs.
  decomposed accented letter would sanitize differently and no non-ASCII vector could be authored.
  Decision 0047 fixes the unit to the **UTF-8 byte**: replace every UTF-8 byte not in
  `[A-Za-z0-9._-]` with `_` — identical in every language with no Unicode library.
  `vectors/workspace-key.json` now carries precomposed (`café-01` → `caf__-01`) and decomposed
  (`e`+U+0301 → `cafe__-01`) vectors.
- **Template syntax is a floor, not a mandate (open).** Section 5.4 says a "Liquid-compatible
  semantics are sufficient" engine, which pins the strict-failure MUSTs and the `template_render_error`
  class but leaves the concrete delimiter/filter syntax to the implementation. Because `WORKFLOW.md`
  is repository-owned and must render on any implementation Symphony targets, the template syntax is
  effectively a cross-implementation contract; the slice authors the reference vectors in Liquid
  syntax. Tightening "sufficient" to a normative shared syntax is a spec-clarification candidate.
- **`attempt` "null or absent" versus strict mode (open).** Section 5.4 lists `attempt` as
  `null`/absent on the first run, but strict variable checking says unknown variables MUST fail. Whether
  a template that reads `attempt` on the first run renders empty (known-but-null) or fails (absent =
  unknown) is undetermined, so no first-run `attempt` vector is authored; the slice tests `attempt`
  only with an integer value. A spec-clarification candidate.
- **`vcs` is not in Section 5.3's top-level key list (open).** Section 6.4's cheat sheet documents
  `vcs.author`, `vcs.actor`, and `vcs.api_key` as operator policy config, but Section 5.3's
  "Top-level operator-config keys" list names only `tracker`, `polling`, `workspace`, `agent`, and
  `codex`. `config_namespaces` carries `vcs` on Section 6.4's authority, since the key demonstrably
  exists; whether Section 5.3's list is meant to be complete is a spec-clarification candidate.
- **`server.*` is repository-owned by Section 13.8 (open).** Section 13.8 enables the HTTP server
  when `server.port` is present in `WORKFLOW.md` front matter, but Section 5 states that
  `WORKFLOW.md` carries only settings used inside the agent sandbox and MUST NOT carry any setting
  Symphony executes with host access — which binding a host port is. `config_namespaces` records
  Section 13.8's placement as written; reconciling the two is a spec-clarification candidate, and is
  why decision 0069 places `observability.*` in the operator policy config rather than following
  `server.*`.
