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
the neutral token-usage record (Sections 4.1.6, 13.5), the usage-ledger entry fields (Section
13.6), the state recovery classes and their per-field assignments (Sections 14.3, 4.1.8), the
configuration namespaces (Sections 5.3, 18.2), the enumerated error tokens — the dispatch preflight
reason tokens (Section 6.3), the workflow and template error classes (Section 5.5), the tracker
error categories (Section 11.4) and the agent-runner error categories (Section 10.6) — and the
transition triggers a repository binds in `repo.policy.toml` (Section 11.6). Each was prose, so
whoever wrote the token spelled it themselves and an upstream rename changed nothing downstream
until someone read a re-pin diff.

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
| `config_error_reasons` | Sections 6.3, 4.2, 9.7, 11.6, 11.7 |
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

Six groups are explicitly **not** closed sets, and say so with `exhaustive: false`: `events`,
because Section 10.4 permits an adapter to emit events the specification does not name;
`config_namespaces`, because Section 5.3 permits an extension to define additional top-level keys;
`error_classes`, because Section 5.5 permits an implementation to define additional classes for
conditions its five do not name; `failure_classes`, because Section 14.1 permits an OPTIONAL
extension to define additional categories; and `tracker_error_categories` and
`agent_error_categories`, because Sections 11.4 and 10.6 each permit an implementation to define
additional categories and require it to document one it defines. In all six, the names the
specification does state are fixed; it is the set that is open — so an implementation shipping no
such extension may still close its own enum at the names it can produce.

`tracker_error_categories` carries `requirement_level` per entry as well as for the group, which
`validation_profiles` above already does for a reason of its own. Four of its members —
`tracker_unsupported_operation`, `tracker_state_unreachable`, `tracker_state_conflict` and
`tracker_pagination_error` — are REQUIRED spellings, because Sections 11.2, 11.7 and 11.8 fail an
operation with them by name; the rest keep the group's `RECOMMENDED`. A generator therefore reads
the entry's level where it carries one and the group's otherwise, and the group level is not
evidence that every member is advisory. `agent_error_categories` is uniformly `RECOMMENDED`, no
rule in this specification branching on which of its categories a turn failed with.

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
  it) or `{ error: <class> }` (assert rendering fails with that error class). Templates are written
  in the REQUIRED minimal template subset (Section 5.4).

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
| `vectors/retry-fire-disposition.json` | `retry_fire_disposition` | Daemon | Sections 8.2, 8.3, 8.4, 16.7 |
| `vectors/worker-exit-disposition.json` | `worker_exit_disposition` | Daemon | Sections 8.5, 16.7 |
| `vectors/available-slots.json` | `available_slots` | Daemon | Section 8.3 |
| `vectors/per-state-concurrency.json` | `per_state_concurrency_limit` | Daemon | Sections 8.3, 4.2 |
| `vectors/candidate-eligibility.json` | `should_dispatch` | Daemon | Sections 8.2, 16.2 |
| `vectors/issue-routing.json` | `route_issue` | Daemon | Sections 4.1.1, 8.7 |
| `vectors/dispatch-ordering.json` | `sort_for_dispatch` | Daemon | Sections 8.2, 16.2 |
| `vectors/standing-conditions.json` | `standing_conditions_hold` | Daemon | Sections 4.2, 5.3.1, 8.2, 8.7, 16.3 |
| `vectors/reconcile-disposition.json` | `reconcile_disposition` | Daemon | Sections 4.2, 8.2, 8.5, 16.3 |

Slice 2 — prompt rendering (decision 0048):

| File | Function | Profile | Derived from |
|------|----------|---------|--------------|
| `vectors/prompt-rendering.json` | `render_prompt` | Daemon | Sections 5.4, 5.5, 12.2 |

Slice 3 — dispatch preflight reasons (decision 0164):

| File | Function | Profile | Derived from |
|------|----------|---------|--------------|
| `vectors/config-preflight.json` | `validate_dispatch_config` | Daemon | Sections 6.3, 4.2, 9.7, 11.6, 11.7 |

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
  pinned by `vectors/candidate-eligibility.json`. Section 6.3's dispatch preflight checks are the
  same shape: the adapter's capability descriptor is static data rather than a runtime call
  (Section 11.7), so judging it against a resolved configuration needs no live tracker either,
  pinned by `vectors/config-preflight.json`. What needs a live tracker is producing the record and
  the descriptor, not judging either.
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
- **The record grew and the vector enumerating it did not — resolved (decision 0154).**
  `iterate-issue-object` was authored under decision 0135 as a derived enumeration of Section 4.1.1,
  its `Plan.md` requiring that "its `given.issue` carries every Section 4.1.1 field and no other".
  Decision 0140 then added `assignees` and decision 0148 added `project` and `team`, and neither
  re-derived the vector: the cross-cutting sync rules name Sections 6.4, 17 and 18 and the
  Conformance Statement template, and nothing named the corpus. The vector was left expecting
  thirteen keys where the record has sixteen, so a build following Section 12.2 failed it and a
  build passing it withheld three fields from the template context — reported from `symphony-rs` as
  issue #120, which could satisfy one or the other and not both. Both halves were stale, not only
  the expectation: `given.issue` carried thirteen too, which is what made the vector's outcome
  depend on whether a harness maps the input into its own record type or renders the decoded object
  verbatim, the one vector in the corpus that can tell those apart. Both now carry the sixteen
  fields, and `scripts/validate_spec_consistency.py` check 7 compares Section 4.1.1's field bullets
  against the vector's supplied keys, its expected keys and their ascending order, so the next field
  added to the record fails the check rather than the corpus.
- **Section 17.3 requires four RECOMMENDED tracker categories by name — resolved (decision
  0162).** Section 11.4 declared its error categories RECOMMENDED as one group, but Section 17.3's
  `Core Conformance` checks named `tracker_unsupported_operation`, `tracker_state_unreachable`,
  `tracker_state_conflict` and `tracker_pagination_error` as the values a conforming implementation
  surfaces — four required in practice while the set was declared advisory, the same asymmetry
  decision 0102 resolved for Section 5.5, one section over. Measurement found the finding
  understated it: the four are spelled into Section 11.4's own normative neighbours — Section
  11.2's completeness guarantee, Section 11.7's capability descriptor, and Section 11.8's
  `set_state` semantics — while the remaining categories occur only in the bullet that defines
  them, two of them also in Section 11.4's illustrative Linear note. What the level cost: a caller
  told to branch on a name the specification permitted to differ — the orchestrator's differing
  response to `tracker_state_unreachable` versus `tracker_state_conflict` being exactly such a
  branch. Section 11.4 now states the four as REQUIRED spellings and the rest RECOMMENDED, with
  the predicate that selects them; Section 17.3 states which of its checks assert a name and which
  assert behavior only; Section 18.1.2 names the level beside each token; and Section 19 and
  `CONFORMANCE-STATEMENT-TEMPLATE.md` gained the matching MUST-document obligation for a category
  defined beyond the set. `tracker_error_categories` now carries the four REQUIRED levels per entry
  rather than one level for the group.
- **Sections 10.6 and 10.4 share three spellings (recorded, not a defect).** `turn_failed`,
  `turn_cancelled` and `turn_input_required` are each both an emitted runtime event and a normalized
  agent-runner error category, so a generator emitting one type per group has three names in two
  enums. The category is named after the event that produced it, which is the useful naming;
  `agent_error_categories` states the relationship in its `note` rather than leaving a generator to
  discover it. Section 10.6 gained an openness clause under decision 0162, mirroring Section 5.5's:
  an implementation MAY define additional categories and MUST document any it defines (Section 19).
- **Template syntax is a floor, not a mandate — resolved (decision 0163).** Section 5.4's
  "Liquid-compatible semantics are sufficient" pinned the strict-failure MUSTs and the
  `template_render_error` class but left the concrete syntax to the implementation, so a
  `WORKFLOW.md` its repository author writes could not be known to render on the implementation
  that runs it. Measuring `symphony-rs` at `ee74fe7` found the one implementation had already
  answered this question and three more of the same shape — filters, `attempt` on a first run (the
  next entry), an unknown member of a known object, and what a timestamp prints — while the
  specification answered none of them:
  `a_first_attempt_renders_the_null_rather_than_failing`,
  `an_absent_issue_field_renders_the_null`, `an_unknown_field_of_a_known_object_fails`, and
  `a_timestamp_renders_as_milliseconds_since_the_epoch`. The corpus was already stricter than the
  specification it tests — every `template` in `prompt-rendering.json` is Liquid source — and had
  recorded, in its own description, the divergence it routed around ("single-line and use
  delimiters rather than inter-token whitespace so the expected output does not depend on an
  engine's whitespace-control behavior"); of ten vectors, none used a filter but the
  deliberately-unknown one. Section 5.4 now states a REQUIRED minimal subset beside the
  Liquid-compatible-semantics floor — `{{ }}` interpolation with dotted member access, `{% for %}`
  iteration over a list and a map, and the map-entry pair indexing Section 12.2 already required —
  with a construct beyond it `Implementation-defined`, documented, and not portable, and states
  that the subset defines no portable filters. Two of the four gaps — the closed `issue` member set
  and the timestamp — were found by reading the implementation rather than by authoring a vector;
  Section 12.2 now closes the `issue` object's member set to Section 4.1.1's fields and fixes a
  timestamp's rendering to RFC 3339 in UTC. Four new vectors pin the value rules, and
  `unknown-filter-fails`'s description is restated for the now-stated empty filter table.
- **`attempt` "null or absent" versus strict mode — resolved (decision 0163).** Closed by the
  decision above: `attempt` is now always bound and `null` on a first run rather than absent,
  because strict variable checking is a rule about names the render context does not define and
  `attempt` is a name this specification defines (Sections 5.4, 12.1). `attempt-null-renders-empty`
  pins a first-run `attempt` rendering as the empty string rather than failing.
- **`vcs` was not in Section 5.3's top-level key list — resolved, and stale before it was closed
  (decision 0159).** The finding recorded that Section 5.3's "Top-level operator-config keys" named
  only `tracker`, `polling`, `workspace`, `agent` and `codex`, so `config_namespaces` carried `vcs`
  on Section 6.4's authority alone. Section 5.3 lists `vcs` today, and one of the three keys the
  finding cited as evidence — `vcs.api_key` — left `SPEC.md` with the code-host relocation
  (`d2647a0`, decisions 0091–0093) and survived only here, in the text describing it. Nothing was
  checking: check 3 reads dotted tokens against the Section 6.4 sheet and check 4 reads registry
  tokens against the corpus, and neither reads this file's prose, which is where the claim lived.
  The entry keeps its Section 6.4 `spec_ref`, since Section 5.3 lists the key and defers its fields
  to Section 9.7, and now carries a note saying so and that the key exists at both configuration
  levels (Section 5.3.7).
- **`server.*` was repository-owned by Section 13.8 — resolved (decision 0160).** Section 13.8
  enabled the HTTP server when `server.port` was present in `WORKFLOW.md` front matter, while
  Section 5 states that `WORKFLOW.md` carries only settings used inside the agent sandbox and MUST
  NOT carry any setting Symphony executes with host access — which binding a host port is. The
  finding is worth keeping for what the registry measured: of the sixteen `config_namespaces`
  entries, `server` was the **only** one assigned to `workflow_md`, so the single key the corpus
  placed in the untrusted artifact was the one that opened a network listener. Decision 0160 moved
  it to the operator policy config, on the reasoning decision 0069 had already applied to
  `observability.*` — which is why that namespace never followed `server.*` in the first place. The
  same decision made `WORKFLOW.md` per repository (`repository.<name>.workflow`, Section 5.3.7),
  which turned the placement from a trust contradiction into an unanswerable question: which
  repository's front matter would have bound the instance's port. The entry now carries
  `"artifact": "operator_policy_config"` and a note recording both.
- **A reference algorithm called a function no section defined — resolved (decision 0138).** Section
  16 defined eight functions and called forty-three it did not. Three were gaps rather than
  primitives: `schedule_retry`, which had five call sites (`dispatch_issue` once, `on_worker_exit`
  twice, `on_retry_timer` twice) and no body outside Section 8.4's two prose bullets;
  `terminate_running_issue`, called twice by `reconcile_running_issues`; and `reconcile_stalled_runs`.
  The consequence was reachable rather than cosmetic: `on_worker_exit` had no `if missing` guard
  where `on_retry_timer`, eleven lines away, had one, and two paths reached it with the entry
  already gone — a stall (Section 8.5 Part A terminates and queues a retry, then the terminated
  worker's own exit queues a second) and a terminal issue (Part B terminates, and the abnormal exit
  queues a retry for an issue the tracker has closed, which holds that issue's claim — and so skips
  it on every tick — until the retry fires, up to `agent.max_retry_backoff_ms`; a claim is not a
  running entry and costs no concurrency slot, so no other issue's dispatch is affected, which is
  the magnitude decision 0144 corrected here and in decision 0138's own chapter). Section 8.5 now
  states that reconciliation owns the runs it terminates and that an exit for an issue with no
  running entry is a no-op — which decision 0146 later made the narrow case of a rule over run
  identity, no entry still meaning no match, and pinned in
  `vectors/worker-exit-disposition.json`. This decision's own repairs owe no vector: both fix which
  state transition happens and in what order, not a value computed from inputs, and every file in
  `vectors/` is a one-shot pure function. Found while checking issue #95; reported by neither open
  issue.
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
- **Standing conditions went unevaluated at reconciliation — resolved (decision 0155).** Section
  8.5 Part B and Section 16.3's `reconcile_running_issues` tested a running issue's tracker state
  alone — terminal, active, or neither — and never `tracker.required_labels`, `tracker.assignee`,
  or routing. Section 5.3.1 already required the first two "to dispatch or continue", a Core MUST,
  but nothing downstream of dispatch read that clause a second time: Section 8.2 tested both once,
  at candidate selection, and Part B tested neither on any later tick. The rule that did state the
  behavior lived in Section 11.2, inside the **Linear adapter's** own requirements — an obligation
  every adapter had to satisfy, stated in one adapter's section rather than in the general
  reconciliation rule every adapter is dispatched through. Section 17.3 compounded it with a
  checklist row, "Issue state refresh by ID returns minimal normalized issues", that licensed
  exactly the partial refresh the rule needed forbidden: a checklist row is a target an implementer
  builds toward, so an adapter returning the smallest conforming issue was conformant. This is a
  second instance of the class decision 0137 named — Core behavior requiring state or a condition
  `SPEC.md`'s own model had no room for — here a condition Core already required going unevaluated
  at the one site meant to keep re-evaluating it, rather than 0137's missing state. Section 8.2 now
  states which of its conditions are standing and which are dispatch-time only, Section 8.7 states
  routing as a standing condition over the run, and Section 8.5 Part B and Section 16.3 evaluate
  them. Section 11.2 carries a general Refresh completeness obligation in place of the
  Linear-specific sentence, and `conformance/vectors/standing-conditions.json` exercises the
  predicate. Issue #121.
- **The refresh record was scoped to one caller, and an absent id had no branch — resolved
  (decision 0156).** Section 11.1 constrained `fetch_issue_states_by_ids`'s **use** and not its
  **result**: its entry read only "Used for active-run reconciliation." Decision 0155's Refresh
  completeness block then obliged only the fields the standing conditions read, because it was
  written from Part B's needs. Part B is not the only consumer. Section 16.6's worker calls the
  same operation after every turn and renders the next continuation prompt from what comes back,
  under Section 12.2's strict variable checking — so a record narrowed to reconciliation's fields
  fails the next turn with `template_render_error` (Section 5.5) and so the run attempt (Section
  12.4), against an adapter that broke no rule. Section 8.5 Part B and Section 16.3 disagreed on
  which collection Part B iterates — "For each running issue" against `for issue in refreshed` —
  so an id absent from the refresh had two readings and the document picked neither. That
  disagreement was cited as an **argument** by decisions 0140 and 0148 (both describing Part B as
  having no absent branch at all) and repaired by neither, because in both the absent case was a
  consequence of a design being rejected rather than of the one accepted. What now holds it:
  Section 11.1 states the result's shape, Section 11.2's Refresh completeness block is over the
  whole record, Part B iterates the running ids and disposes of an unanswered one by leaving the
  run untouched, and `conformance/vectors/reconcile-disposition.json` pins all six of Part B's
  outcomes. Issue #121.
- **A retry fire dispatched what a poll tick would have refused — resolved (decision 0157).** The
  third site the answer to issue #120 named, after the two decision 0155 reached. Section 8.4's
  "Retry handling behavior" required a fire to dispatch an issue "found and still
  candidate-eligible", and Section 7.3's `Retry Timer Fired` trigger required it a second time —
  "Re-fetch active candidates and attempt re-dispatch, or release claim if no longer eligible";
  Section 16.7's `on_retry_timer` tested membership in the candidate set and
  `available_slots`, and nothing else — so a backoff of up to `agent.max_retry_backoff_ms`, default
  `300000`, outlived the eligibility that armed it, and a fire re-dispatched an issue whose required
  label was removed, whose configured assignee was unassigned, or whose blocker reopened while it
  waited. Two more followed from the same two lines. `available_slots` is Section 8.3's global
  computation alone, so a fire dispatched past `max_concurrent_agents_by_state` while the poll tick
  held that limit on every cycle. And the fire entered `dispatch_issue` still holding the claim
  `schedule_retry` took, with its retry entry already removed, so the `ensure_object_store` early
  return left a claim no site could remove — `state.claimed.remove` appears at two places in Section
  16 and neither is reachable for that issue again — against Section 8.5's own statement that the
  branch "leaves the issue unclaimed so a later tick retries it". Section 8.2 now states that both
  dispatch sites evaluate its conditions whole; the fire releases the claim with the entry it
  consumes rather than excepting the `claimed` condition, which is what lets the conditions be
  evaluated whole and what makes Section 8.5's bullet true of both callers; and Section 8.3 names
  `dispatch_slot_available` for the pair of limits, whose want of a name is why one site tested one
  of two. `vectors/retry-fire-disposition.json` widens from the generation match to the fire's whole
  disposition, distinguishing a re-arm from a release rather than collapsing both into one
  not-dispatched outcome. Issues #120, #121.
- **The repository dimension had no configuration key — resolved (decision 0159).** Section 5.3's
  top-level operator keys were six singletons while six other places described a configuration with
  a repository dimension. Section 6.1's first pipeline step resolved a `repo.policy.toml` pointer no
  key named, and Section 6.4's row for it was the only row in that section naming no key — which is
  also why check 3 could not see it, since that check tests a dotted token for occurrence in the
  sheet and a row with no token is not a token. Section 15.3's "An implementation MUST support the
  per-repository configuration" was a two-level schema rule with fallback at the leaf, stated for
  one field pair in a document that had no second level. And `repo_key`, the path component Section
  4.1.8 reads a running entry's `repository` back out of after a restart, was defined nowhere, while
  the only sanitization rule in the document is byte-wise and deliberately lossy — so the rule that
  would have made the name safe would have made the read-back name a different repository. This
  corpus carried the gap as data in two places, `vectors/issue-routing.json` and
  `vectors/standing-conditions.json`, both recording that the schema was owed a decision and both
  citing decision 0148; a decision closing it and updating one would have left the other asserting
  the gap, which is what a cross-reference living in a prose note costs. Section 5.3.7 now
  enumerates the repositories, keyed by `Repository Key` (Section 4.2), each entry resolving against
  the orchestrator level leaf by leaf and before defaulting. `vectors/repository-inheritance.json`
  pins that resolution and `config-defaults.json` says which level its flat view is of; the two
  layers are separable only because Section 6.1 states the order between them, which is the one
  place an implementation defaulting first would silently shadow an inherited value.
- **One hook per lifecycle point, on every surface that executes one — resolved (decision 0158).**
  Decision 0025's re-evaluation recorded the gap and did not close it: Section 5.3.4 states the hook
  split as configuration and Section 15.4 states it as trust, while Section 9.4's execution
  contract, Section 9.2's creation step, Section 16.6's `run_hook` calls, and Section 17.2's rows
  all
  modelled one hook per lifecycle point — the shape the document had before the split existed. The
  execution surface therefore contradicted the configuration surface, and Section 9.4's "with the
  workspace directory as `cwd`" was not merely false for the host-side half but defeated the control
  Section 15.4 states it for: a policy-branch-trusted body invoking a relative command would have
  reached agent-written content with host access. Two consequences had no producer once the halves
  were separated, and the decision states both rather than leaving them derivable: an in-sandbox
  `after_run` is reachable only because the sandbox is scoped to the run attempt and outlives
  `release(continuation_ref)` (Sections 9.6, 10.7), and an in-sandbox `before_remove` is valid
  configuration that no removal path this specification defines supplies a run context for, both
  removal paths — startup cleanup (Section 8.6) and reconciliation teardown (Section 16.3) — running
  the host-side half alone. This vector's own drift is the same class decision 0132 named:
  `config-defaults.json` resolved `hooks.timeout_ms`, a path `SPEC.md` never defined, against the
  `hooks.workspace.timeout_ms` of Sections 5.3.4, 6.4 and 9.4.
- **One `hooks.workspace.timeout_ms` for two artifacts at two trust levels — resolved (decision
  0161).** Section 5.3.4 documented the key once for both repository artifacts and Section 9.4 spent
  it on both halves, so the bound Symphony waits by could be named in `WORKFLOW.md` — read from the
  working tree the run acts in, where an agent's edit is honored. It is the one member of the
  namespace that is not a hook body: nothing in the sandbox reads it, and the executor waits on both
  halves from outside the sandbox (Section 3.1), so a worktree value would have set the ceiling on
  the host's own wait and a one-millisecond one would have timed out the host-side `after_run` or
  `before_remove` half, whose failure Section 9.4 logs and ignores. `VCSX-SPEC.md` had already
  refused the equivalent `[hooks] timeout_ms` for the engine, on the same reasoning plus a
  limitation Symphony does not share — the engine never learns which revision a value came from,
  where Symphony reads each artifact from exactly one. Nothing here was checking and nothing here
  could have: `vectors/config-defaults.json` asserts the default through a flat view that abstracts
  "over which of the three artifacts owns each field", which is the property that made
  `repository-inheritance.json` separable and is the same property that hides an ownership defect.
  The key is now `repo.policy.toml`'s alone (Section 5.3.4), and `config_namespaces`' `hooks` entry
  distinguishes the bodies from the bound in its `note`.
- **Three reason tokens named no condition, and the condition was in a different section — resolved
  (decision 0164).** `unsupported_tracker_kind`, `missing_tracker_api_key` and
  `missing_tracker_project_slug` each occurred once in the whole of `SPEC.md`, in the Section 11.4
  bullet list that named them, and `tracker_error_categories`'s own note recorded the symptom
  without the cause: "The first three entries carry no `condition` because Section 11.4 states
  none." The cause was that their conditions were never Section 11.4's — they were Section 6.3's,
  whose ten checks each ended "otherwise configuration error" and named no token at all. On the
  path that matters, dispatch preflight's per-tick validation skips dispatch every tick while
  reconciliation keeps running (Section 6.3), so the daemon stayed healthy and idle behind a single
  undifferentiated refusal an operator could only read as a message string. Measured at `ee74fe7`:
  `symphony-rs` raises two of the three as `FaultReport::of::<ConfigInvalid>` in
  `crates/symphony-orchestrator/src/step.rs`, comparing the fault's reason as a string, while its
  generated `TrackerErrorCategory` (from `conformance/vocabulary.json`) carries all three as
  tracker variants — both faithful to a specification that put the token in one section and the
  condition in another. Section 6.3 now carries a condition-to-reason table of twelve tokens
  modeled on `VCSX-SPEC.md` Section 6.11's, states the evaluation order where several conditions
  hold, and the three orphans moved with their conditions. What checks now: check 6
  (`scripts/validate_spec_consistency.py`) closes `config_error_reasons` against Section 6.3's
  table in both directions, and `vectors/config-preflight.json` pins each of the twelve tokens plus
  the stated order.
