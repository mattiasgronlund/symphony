# Symphony Conformance Data

Machine-readable conformance data for Symphony, derived from `SPEC.md`. Two artifacts with different
jobs:

- `vocabulary.json` — the token registry (decision 0071). What the names are.
- `vectors/*.json` — behavior vectors making the deterministic subset of `SPEC.md` Section 17's test
  matrix an objective pass/fail (decisions 0046, 0048). What Symphony does.

Both serve the shared enforcement the multi-implementation strategy needs: an implementation
generates or checks its token spellings from the registry and runs the corpus against its own
binary, reporting the result in its Conformance Statement (see `CONFORMANCE-STATEMENT-TEMPLATE.md`,
Section 7 evidence).

`SPEC.md` governs both artifacts. Every value is read from the sections its `spec_refs` cite; where
a value cannot be read, no entry is authored and the gap is recorded under "Surfaced findings"
below.

The engine's own conformance data derives from `VCSX-SPEC.md` and lives in `vcsx/`.

## Layout

- `vocabulary.json` — the token registry.
- `vectors/*.json` — one file per behavior, each a self-contained set of input/output vectors.

---

## Token Registry (`vocabulary.json`)

`SPEC.md` names token sets an implementation — or a repository author — is expected to spell
exactly: the emitted runtime events (Section 10.4), the REQUIRED log context fields (Section 13.1),
the neutral token-usage record (Sections 4.1.6, 13.5), the usage-ledger entry fields (Section 13.6),
the state recovery classes and their per-field assignments (Sections 14.3, 4.1.8), the configuration
namespaces (Sections 5.3, 18.2), the enumerated error tokens — the workflow and template error
classes (Section 5.5), the tracker error categories (Section 11.4) and the agent-runner error
categories (Section 10.6) — and the transition triggers a repository binds in `repo.policy.toml`
(Section 11.6). Each was prose, so whoever wrote the token spelled it themselves and an upstream
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
- `requirement_level` (string, OPTIONAL) — `REQUIRED` or `RECOMMENDED`, the level the specification
  states for the set as a whole. Present only where the specification states one. A `RECOMMENDED`
  group's names are a target vocabulary an implementation MAY diverge from, so a type generated from
  one MUST admit an unknown token whether or not the group carries `exhaustive`, and a check
  generated from it is advisory where a `REQUIRED` group's is a conformance check.
- `exhaustive` (boolean, OPTIONAL) — present and `false` where the specification states the set is
  open. A generated type for such a group MUST admit an unknown token rather than closing the enum.
- `key` (array of strings, OPTIONAL) — the fields the specification keys the record by.
- `entries` — the tokens. Either an array of strings, or an array of objects whose `token` field is
  the token and whose remaining fields are the properties the specification fixes about it.

In `config_namespaces`, `artifact` names the Section 5 configuration artifact a key belongs to:
`operator_policy_config`, `repo_policy_toml`, `workflow_md`, or `repository_owned` where the
specification splits one key across both repository-owned artifacts by trust (Section 15.4).

In the error groups and in `transition_triggers`, `condition` is the condition the specification
states the token names, carried only where it states one; `error_classes` additionally carries
`gating`, Section 5.5's dispatch gating behavior, valued `blocks_dispatch` or `fails_attempt`. As in
`config_namespaces`, `core: false` marks a token owned by an OPTIONAL extension rather than by the
core schema — in `transition_triggers` the two task-state events, which an implementation shipping
no task model never raises.

### Using it

- **An implementation** generates or checks its event enum, log-context fields, ledger schema,
  recovery-class taxonomy, and error classes from this file, so a token change upstream becomes a
  build failure rather than a silent divergence. Read `requirement_level` first: a `REQUIRED` group
  is a conformance check, a `RECOMMENDED` one is advisory. Record in the Conformance Statement
  whether it was checked against, and at which revision.
- **A repository author** — the one reader here who is not an implementer — checks each
  `tracker.transitions` entry's `on` value against `transition_triggers` before committing
  `repo.policy.toml`. A tooling author validating that file generates the check from this group; it
  is closed (`exhaustive: true`), so the check is total.
- **A reviewer** of a change to `SPEC.md` verifies that every token added, renamed, or removed is
  reflected here in the same change.
- **A Conformance Statement author** reads `runtime_state_fields` for the "Spec default" column of
  its recovery-class table, `config_namespaces` for the namespace column of its extensions table,
  `layer_profiles` and `deployment_topologies` for the claim and topology its first section states,
  and `error_classes` to check that any class it defines beyond the five is resolved in the `MUST
  document` table. The profile and topology are the fields a consumer reads to learn what the
  implementation asserts about itself, which is why they are published rather than transcribed.

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
| `error_classes` | Sections 5.5, 5.1, 5.2, 5.4 |
| `tracker_error_categories` | Sections 11.4, 11.7, 11.8 |
| `agent_error_categories` | Section 10.6 |
| `transition_triggers` | Sections 11.6, 8.10, 9.12 |
| `failure_classes` | Sections 14.1, 14.2 |
| `layer_profiles`, `validation_profiles` | Sections 17, 18.1, 3.4 |
| `deployment_topologies` | Sections 3.4, 18.1 |

`transition_triggers` is the one *token* group carrying `exhaustive: true`: Section 11.6 states in
its own words that the trigger vocabulary is closed and that "a repository wires triggers to
transitions but
does not introduce new trigger names", and Section 6.3 rejects an `on` value outside it. A generated
type for it may close the enum, which is the point — the set exists so a `repo.policy.toml` `on`
value can be checked before dispatch. Symphony is its authority: `tracker.transitions` travels in
`repo.policy.toml` because the repository owns the wiring, but `set_state` is a consumer-effected
action over a tracker outside the VCS/forge domain, so the engine carries and validates the table
without matching its `on` (decision 0122). The engine's own trigger vocabulary is the two kinds it
produces itself — a lifecycle position, and a typed operation result — and it no longer publishes a
`signals` group.

The three conformance-vocabulary groups — `layer_profiles`, `validation_profiles` and
`deployment_topologies` — are closed too, and on the specification's own counting rather than on an
inference: Section 17 says `Core Conformance` "comprises two layer profiles" and Section 3.4 says
"Three deployment topologies compose the layers". They are listed apart from the token groups
because what they name is a claim rather than a value carried in a payload or a config file: their
reader is a Conformance Statement author, and a divergence shows up as an implementation describing
its own conformance in a spelling nothing else recognizes. `validation_profiles` carries
`requirement_level` per entry rather than for the group, its four members not sharing one.

Four groups are explicitly **not** closed sets, and say so with `exhaustive: false`: `events`,
because Section 10.4 permits an adapter to emit events the specification does not name;
`config_namespaces`, because Section 5.3 permits an extension to define additional top-level keys;
`error_classes`, because Section 5.5 permits an implementation to define additional classes for
conditions its five do not name; and `failure_classes`, because Section 14.1 permits an OPTIONAL
extension to define additional categories. In all four, the names the specification does state are
fixed; it is the set that is open — so an implementation shipping no such extension may still close
its own enum at the names it can produce.

`tracker_error_categories` and `agent_error_categories` carry no `exhaustive` key. Sections 11.4 and
10.6 do not state that their sets are open, and inferring it here would be the registry deciding a
question the prose left alone. The openness a generator needs follows from `requirement_level`
instead: both are `RECOMMENDED`, so a type generated from either must already admit an unknown
token.

### Deferred to later slices

**The test (decision 0103): a prose enumeration is published when something outside the
implementation's own source spells it** — a repository author writing configuration, a Conformance
Statement author filling a table, or a Conformance Statement or conformance check asserting a value.
Not whether the set is an enumeration, but *what reads the spelling and what happens when the
reading is wrong*: a set nothing reads has no divergence to catch, and publishing it would make the
registry an inventory rather than a derived view.

So each bullet below names **the reader it lacks**, which is one question a later reader re-asks,
rather than a reason that has to be re-derived. Decision 0103 introduced this after the previous
form — a bespoke reason per bullet — went stale four times without anyone noticing, twice inside the
decisions repairing it.

- **Brokered-result reason codes** (Section 10.8) — the one error set still deferred, and on a
  different reason from the three published in the error slice. Section 10.8 introduces its codes
  with "for example" and gives three illustrations (`non_fast_forward`, `pr_conflict`,
  `scope_denied`) rather than an enumeration, so there is nothing to publish that would not be
  invented. Reconsider when the codes are enumerated. The earlier deferral covered Sections 5.5,
  11.4 and 10.6 as well, on the ground that "several are RECOMMENDED rather than REQUIRED spellings,
  which is a distinction the registry would have to carry per entry"; deriving it (decision 0102)
  showed the distinction is per *group* — each section states one level for its whole set — so it
  costs the one `requirement_level` field documented above.
- **Orchestration states** (Section 7.1) — **no reader.** `Provisioning` is named in a Section 17.4
  check and in Section 18.2, but descriptively, and Section 13.3's runtime snapshot returns
  `running`/`retrying` row lists rather than a state name, so no state reaches a monitoring surface
  as a value. Reconsider when a snapshot, status surface, or API response exposes one. (The trigger
  vocabulary this bullet used to be bundled with is now published; see `transition_triggers`.)
- **Run attempt phases** (Section 7.2) — **no reader.** No Section 17, 18 or 19 check names one.
  Section 11.6 names four (`Succeeded`, `Failed`, `TimedOut`, `Stalled`) only to *define* the run
  outcomes — "`run_succeeded` — the run attempt finished in `Succeeded`" — so the trigger a
  repository writes is `run_succeeded` and `Succeeded` never leaves the document. Reconsider when
  anything outside Section 7.2 asserts a phase by name; decision 0103's `Background.md` carries the
  measurement that checks this.
- **Transition triggers, internal** (Section 7.3) — **no reader.** Seven prose-titled lifecycle
  events (`Poll Tick`, `Worker Exit (normal)`, …) that drive the orchestrator's own state machine
  and reach no configuration, wire, or conformance surface. Despite the shared word these share no
  token with Section 11.6's triggers, which are published.
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
- `profile` (string) — the Section 17 validation profile the behavior belongs to (`Core Conformance`
  or `Daemon Conformance`).
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

Non-ASCII code points inside `given` and `expect` are written as `\uXXXX` escapes, so the vector
files are pure ASCII. Two behaviors are deliberately sensitive to Unicode normalization form —
workspace-key sanitization (decision 0047) and state normalization (decision 0105) — and each has a
pair of vectors that differ only in that form. Written as literals they look identical on screen, so
an editor or authoring tool that re-composed one would turn it into a tautology that passes under
every reading, silently. The escapes make that impossible to do by accident and readable in review.

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
| `vectors/retry-fire-disposition.json` | `retry_fire_disposition` | Daemon | Sections 8.4, 16.7 |
| `vectors/available-slots.json` | `available_slots` | Daemon | Section 8.3 |
| `vectors/per-state-concurrency.json` | `per_state_concurrency_limit` | Daemon | Sections 8.3, 4.2 |
| `vectors/candidate-eligibility.json` | `should_dispatch` | Daemon | Sections 8.2, 16.2 |
| `vectors/dispatch-ordering.json` | `sort_for_dispatch` | Daemon | Sections 8.2, 16.2 |

Slice 2 — prompt rendering (decision 0048):

| File | Function | Profile | Derived from |
|------|----------|---------|--------------|
| `vectors/prompt-rendering.json` | `render_prompt` | Daemon | Sections 5.4, 5.5, 12.2 |

## Deferred to later slices

These behaviors are conformance-relevant but not purely deterministic from inputs alone; they need a
harness with fixtures or live services and belong with the `Real Integration Profile` (Section
17.8):

- Config **secret-provider resolution** and `$VAR` / `~` expansion (Section 17.1) — I/O-bound.
- **Workspace safety invariants** (Section 9.5, Invariants 1–2: cwd and root containment) —
  filesystem and process state.
- **Tracker read/write** surfaces, and the adapter's fetch of the candidate set (Sections 8.2,
  11). Section 8.2's eligibility predicate itself is no longer deferred: over an
  already-normalized record (Section 4.1.1) and a resolved configuration it is a pure function,
  pinned by `vectors/candidate-eligibility.json`. What needs a live tracker is producing the
  record, not judging it.
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
- **The error class named its detection phase — resolved (decision 0102).** Section 5.5 annotated
  `template_parse_error` "(during prompt rendering)", a phase, and `template_render_error` "(unknown
  variable/filter…)", a condition. A strict template engine resolves filter names against its own
  filter table and variable names against the render context, so it may reject an unknown filter
  while parsing and an unknown variable while rendering (measured: `liquid` 0.26.11 does exactly
  that), while `vectors/prompt-rendering.json` expects `template_render_error` for both. Under the
  phase reading, two of six vectors failed for an implementation that was otherwise correct. Section
  5.5 now states that a class names the condition rather than the stage that detected it, annotates
  all five by condition, and makes the spellings REQUIRED; the corpus gained a
  `template_parse_error` vector so the rule is checked rather than only stated.
- **Section 14.1 spelled failure categories two ways — resolved (decision 0104).** Nine Title Case
  titles (`Workflow/Config Failures`) and one snake_case category, `token_budget_exceeded`, which
  Section 14.1's own note calls a failure category and a Section 17.4 check asserts. No consistent
  token could be read off the section, so no group could be derived: a registry that picked would
  have been deciding what the prose left open. Section 14.1 now gives each of the nine a token
  beside its prose name, and states why an extension-defined category is spelled differently — the
  nine partition *where* a failure arose, while an extension elevates one *condition*. The
  `_failures` suffix is kept rather than trimmed because `workspace`, `tracker` and `observability`
  would otherwise collide exactly with `config_namespaces` entries.
- **Section 14.2 did not name the classes it disposed of — resolved (decision 0104).** Its bullets
  carried their own descriptive headings ("Dispatch validation failures", "Worker failures"), and
  the mapping onto Section 14.1 is not one-to-one, so the correspondence was inferable but unstated
  — which meant the registry could not carry a recovery disposition without inventing the mapping.
  Each bullet now names its classes. Two facts the mapping made visible: `workspace_failures` and
  `agent_session_failures` share one disposition, and `tracker_failures` takes two, because what a
  tracker failure costs depends on where it occurred. The disposition itself is still not carried in
  the registry — it is the prose of a rule rather than a property Section 14.1 fixes about a token.
- **A misspelled transition trigger was caught by nothing — resolved (decision 0103).** Section 11.6
  states a closed trigger vocabulary a repository binds in `repo.policy.toml`, but nothing rejected
  a name outside it. The engine cannot: to `vcsx` a bare token is a well-formed **signal**, and
  `VCSX-SPEC.md` Section 5.1 leaves the signal set open because "the consumer raises the token the
  policy binds", so `unknown_trigger` could not fire on a typo. Section 6.3's enumerated preflight
  checks did not cover `on` values either, and Section 11.6's "a trigger that fires with no matching
  `from`-state transition performs no transition" made the result indistinguishable from a real
  trigger nobody bound. So a policy loaded, validated, dispatched, and the transition silently never
  fired. Section 6.3 now rejects an `on` outside the vocabulary, which is what makes the REQUIRED
  spelling observable.
  *(Later: decision 0122 removed the signal trigger kind from the engine, so the reason the engine
  could not catch a typo has changed — a bare token is now no trigger at all rather than a well-formed
  signal. The repair stands and is now the only thing that catches one, since `tracker.transitions`
  is matched by Symphony and the engine validates the table without reading its `on`.)*
- **The trigger-ownership question had already been answered — resolved (decision 0103).** The
  deferral bullet held Sections 7.1, 7.3 and 11.6 behind "the two registries would have to agree on
  which document owns each token". `VCSX-SPEC.md` Section 5.1 assigns the signal vocabulary to the
  consumer, and decision 0055 states the consequence outright — "the signal vocabulary is raised by
  the consumer … and signals have no upstream". Symphony is the consumer; the question was closed
  before the bullet was written, and nothing re-derives a reason for *not* doing something, which is
  why it survived. This is the finding that motivated replacing per-bullet reasons with the reader
  test.
- **Section 4.2 did not say which lowercase — resolved (decision 0105).** "Compare states after
  `lowercase`" over a value that is a comparison key: `active_states`/`terminal_states` membership,
  the `max_concurrent_agents_by_state` lookup whose miss falls back to the global limit silently,
  and Section 11.6's duplicate `(from, on)` rule, where the reading decides whether a
  `repo.policy.toml` loads at all. `İ` (U+0130) separates the readings — unchanged under an
  ASCII-only lowercasing, `i` + U+0307 under the Unicode default mapping, and bare `i` under a
  Turkish tailoring, which also maps `In Progress` to `ın progress`. The existing four vectors did
  not settle it, and the sharper statement is that `title-case-two-words` **does** fail under the
  Turkish tailoring: the corpus
  checked the dangerous reading conditionally on the locale of the machine that ran it, so a green
  result on a CI runner was not evidence about the deployment host. Section 4.2 now defines
  `Lowercase Normalization` once — Unicode Default Case Conversion, full mappings, no
  language-specific tailoring, no Unicode normalization form applied — and every case-insensitive
  comparison in the document cites it. Three vectors pin it: `İ` separates all three readings on any
  host, `ẞ` → `ß` separates lowercasing from case folding, and a decomposed input pins the
  no-normalization-form rule.
- **`SPEC.md` Section 12.2 made a map iterable and fixed no iteration order — resolved (decision
  0135).** The rendering rules required nested maps to be preserved "so templates can iterate", and
  no section said what order iterating one yields. `labels` and `blocked_by` have an order because
  they are lists; `metadata` is a map and the issue object is another. Section 5.4's
  "Liquid-compatible semantics are sufficient" does not settle it — the reference Liquid iterates a
  hash in insertion order, which for a payload-decoded map is a property of the decoder, and
  `liquid` 0.26.11 iterates a hash map whose order is a randomizing hasher's, measured at three
  orders across six runs of one binary. So `render_prompt`, whose `iterate-labels` vector already
  established iteration as in-contract, had an unspecified output for an input the same corpus says
  must work. Section 12.2 now fixes the order (ascending by key, keys compared as strings by
  Unicode code point), the entry shape (a two-element key/value pair, key first) and the rule's
  reach. Three vectors pin it: `iterate-metadata-map`, `iterate-issue-object`, and
  `iterate-metadata-map-non-ascii`, whose keys separate code-point order from a locale collation —
  measured, `en_US.UTF-8` and `sv_SE.UTF-8` both collate them in the other order.
- **Section 17.3 requires four RECOMMENDED tracker categories by name (open).** Section 11.4
  declares its eleven error categories RECOMMENDED, but Section 17.3's `Core Conformance` checks
  name `tracker_unsupported_operation`, `tracker_state_unreachable`, `tracker_state_conflict` and
  `tracker_pagination_error` as the values a conforming implementation surfaces. Four of eleven are
  therefore required in practice while the set is declared advisory — the same asymmetry decision
  0102 resolved for Section 5.5, one section over. `tracker_error_categories` records Section 11.4's
  level as written and names the four in its `note`; re-levelling Section 11.4 is a
  spec-clarification candidate, and the evidence that would force it is a second tracker adapter
  asserted against those checks.
- **Sections 10.6 and 10.4 share three spellings (recorded, not a defect).** `turn_failed`,
  `turn_cancelled` and `turn_input_required` are each both an emitted runtime event and a normalized
  agent-runner error category, so a generator emitting one type per group has three names in two
  enums. The category is named after the event that produced it, which is the useful naming;
  `agent_error_categories` states the relationship in its `note` rather than leaving a generator to
  discover it.
- **Template syntax is a floor, not a mandate (open).** Section 5.4 says a "Liquid-compatible
  semantics are sufficient" engine, which pins the strict-failure MUSTs and the
  `template_render_error` class but leaves the concrete delimiter/filter syntax to the
  implementation. Because `WORKFLOW.md` is repository-owned and must render on any implementation
  Symphony targets, the template syntax is effectively a cross-implementation contract; the slice
  authors the reference vectors in Liquid syntax. Tightening "sufficient" to a normative shared
  syntax is a spec-clarification candidate.
- **`attempt` "null or absent" versus strict mode (open).** Section 5.4 lists `attempt` as
  `null`/absent on the first run, but strict variable checking says unknown variables MUST fail.
  Whether a template that reads `attempt` on the first run renders empty (known-but-null) or fails
  (absent = unknown) is undetermined, so no first-run `attempt` vector is authored; the slice tests
  `attempt` only with an integer value. A spec-clarification candidate.
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
- **A reference algorithm called a function no section defined — resolved (decision 0138).** Section
  16 defined eight functions and called forty-three it did not. Three were gaps rather than
  primitives: `schedule_retry`, which had five call sites (`dispatch_issue` once, `on_worker_exit`
  twice, `on_retry_timer` twice) and no body outside Section 8.4's two prose bullets;
  `terminate_running_issue`, called twice by `reconcile_running_issues`; and `reconcile_stalled_runs`.
  The consequence was reachable rather than cosmetic: `on_worker_exit` had no `if missing` guard
  where `on_retry_timer`, eleven lines away, had one, and two paths reached it with the entry
  already gone — a stall (Section 8.5 Part A terminates and queues a retry, then the terminated
  worker's own exit queues a second) and a terminal issue (Part B terminates, and the abnormal exit
  queues a retry for an issue the tracker has closed, which holds a claim, and therefore a
  concurrency slot, for up to `agent.max_retry_backoff_ms`). Section 8.5 now states that
  reconciliation owns the runs it terminates and that an exit for an issue with no running entry is
  a no-op. No vector is owed: both repairs fix which state transition happens and in what order, not
  a value computed from inputs, and every file in `vectors/` is a one-shot pure function. Found while
  checking issue #95; reported by neither open issue.
- **A retry timer fire could not name the arming it came from — resolved (decision 0136).** Section
  8.4 required retry entry creation to "Cancel any existing retry timer for the same issue", which
  makes cancel-then-replace in-contract; Section 16.7 then identified an arriving fire by `issue_id`
  alone and guarded it with `if missing`. That guard tests presence, and a replaced entry is present
  — so a cancelled timer that fired anyway consumed the *new* entry and dispatched at once,
  discarding a `due_at_ms` that was holding a backoff. Reachable through a stall: Part A of Section
  8.5 queues a retry, the terminated worker's exit queued a second (decision 0138), and the second
  cancelled the first's timer. `RetryEntry` gains `generation`, Section 8.4 requires the fire to
  carry it and forbids reusing a value for an issue while the process lives, and `on_retry_timer`
  became get-compare-remove rather than pop-then-test — a comparison that fails after the pop has
  already taken the entry the fire must not touch. `vectors/retry-fire-disposition.json` pins all
  three cases, and `entry_retained` on `fire-generation-stale` is what a pop-then-test implementation
  fails. Issue #95.
- **Core behavior held state the state model had no room for — resolved (decision 0137).** Section
  14.2 requires that where an engine policy could not be used at all, retry is "backed off per
  repository rather than attempted every tick", and lets persistent failures of both
  `repository_provisioning_failures` and `engine_invocation_failures` be parked. Section 4.1.8's
  eight fields held nothing keyed by repository, and Section 14.3 required a recovery class of every
  Section 4.1.8 field "and any state introduced by an OPTIONAL extension" — exhaustive over the
  wrong set, admitting extensions and leaving Core's own additions out. The same construct was
  therefore blessed on the extension path (`node_provisioning_failures` carries an identical park
  MAY) and homeless on the Core path. What broke was the Conformance Statement rather than the
  daemon: a Statement generated from the template was complete against its own table and silently
  missing the restart behaviour of the one piece of state an operator most needs it for. Section
  4.1.8 gains `repository_backoff` (`Ephemeral`), Section 14.3 admits Core-introduced state on the
  same terms as an extension's, and Sections 19, 18.1.1 and 18.1.3 carry the widened obligation —
  three further sites of the extension-only framing, two of which the decision's first plan did not
  name and `scripts/check_plan_anchors.py` found. No vector is owed: a recovery class is an
  assignment, not a function of inputs. Issue #96.
