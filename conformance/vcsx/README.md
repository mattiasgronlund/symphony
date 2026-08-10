# vcsx Engine Conformance Data

Machine-readable conformance data for the `vcsx` engine, derived from `VCSX-SPEC.md`. Two artifacts
with different jobs:

- `vocabulary.json` — the shared token registry (decision 0051). What the names are.
- `vectors/*.json` — behavior vectors making the deterministic subset of `VCSX-SPEC.md` Section 13.1's
  test matrix an objective pass/fail (decision 0053). What the engine does.

This tree is separate from the Symphony conformance corpus in the parent directory. The two derive
from different specifications, have different schemas, and are consumed by different implementations;
they share a parent directory and nothing else.

`VCSX-SPEC.md` governs both artifacts. Every value is read from the sections its `spec_refs` cite;
where a value cannot be read, no entry is authored and the gap is recorded under
"Surfaced findings" below.

---

## Token Vocabulary (`vocabulary.json`)

`VCSX-SPEC.md` Section 14 "Alignment with `VCSX-CONTRACT.md`" requires every token shared between the
engine specification and its contract surface — the operations, the lifecycle positions, the trigger
and action names, the proto classes, the reason and `need` vocabularies, the `repo.policy.toml`
sections, and the task and message-formulation surfaces — to be spelled identically in both, and makes
changing a name a contract change.

`vocabulary.json` is that vocabulary as data. It exists because an engine implementation in its own
repository (decision 0049) is a **third** spelling of the same tokens, on its own cadence, with
nothing mechanical connecting it to the two documents. Drift in this vocabulary is silent: a reason
carrying the wrong proto class routes to a different `#class` edge and changes which policy fires,
with no build or test failure anywhere to catch it.

This tree is separate from the Symphony conformance data in the parent directory. The two derive
from different specifications, have different schemas, and are consumed by different implementations;
they share a parent directory and nothing else. The parent directory now carries a registry of its
own on the same terms (`../vocabulary.json`, decision 0071); the two are not merged, for the same
reason the vector corpora are not.

## Precedence

**`VCSX-SPEC.md` governs. This file is derived.**

Every entry is read from the sections its `spec_refs` cite; nothing here is invented, and no entry
restates a requirement's substance. Entries carry names and the properties the specification fixes
about them — a reason's proto class, an operation's lifecycle position, an action's effecting party —
not the prose of the rules those properties feed.

Where this file and `VCSX-SPEC.md` disagree, the specification is right and this file is a bug. If the
registry ever needs a property the prose does not fix, that is the signal it has stopped being a
derived view; move the concept into `VCSX-SPEC.md` and re-derive rather than letting the registry lead
(decision 0051).

## Schema

A single JSON object. Top-level keys are metadata (`artifact`, `schema_version`, `governed_by`,
`description`, `spec_refs`) plus one object per token group.

Each group carries:

- `spec_refs` (array of strings) — the sections the group is read from, verbatim.
- `note` (string, OPTIONAL) — a constraint the specification states about the group as a whole, such
  as membership of the major-stable surface.
- `entries` — the tokens. Either an array of strings, or an array of objects whose `token` field is
  the token and whose remaining fields are the properties the specification fixes about it.

Two groups depart from that shape because the specification does: `trigger_kinds` describes forms
rather than tokens, and `task_model` is a record of field, value, and verb sets rather than a flat
entry list.

## Normalizations

The registry is a faithful view, not a byte-for-byte transcription. Two places it normalizes:

- **`reasons`** is keyed one entry per `(operation, reason)`. Section 4.3's combined rows expand: the
  `status` / `diff` row to `status:ok` and `diff:ok`, and the three universal rows to one entry per
  operation they cover — `failed` and `unsupported` for every operation, `blocked` for every gated one,
  each marked `universal: true`. So 32 table rows yield 50 entries.
- **`operations`** carries `lifecycle_position: null` for the operations Section 4.1 gates at no fixed
  position (`integrate`, `pull`) and for the read-only ones (`status`, `diff`), rather than omitting
  the field.

## Using it

- **An engine implementation** generates or checks its reason enum, proto-class mapping, exit-code
  mapping, and action set from this file, so a token change upstream becomes a build failure rather
  than a silent behavior change. Record in the engine's Conformance Statement whether it was checked
  against, and at which revision (`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`, Section 8).
- **A reviewer** of a change to either engine document verifies that every token added, renamed, or
  removed is reflected here in the same change, which is Section 14's rule made checkable.
- **A consumer** writing `repo.policy.toml` reads the reason and class columns to know which `#class`
  edges absorb which outcomes.

Adding a reason or `need` token is permitted in a `MINOR` release (Section 8.5); changing a listed
reason's class within a `MAJOR` is not. The `class` column is therefore the load-bearing one.

---

## Behavior Vectors (`vectors/*.json`)

`VCSX-SPEC.md` Section 13.1's test matrix is prose. These vectors make its deterministic, host-
independent subset an objective pass/fail, identical in every implementation language — the same job
decision 0046's corpus does for `SPEC.md`.

The engine has **no conformance profiles**: decision 0043 deferred engine conformance rather than
defining profiles for it, so a vector file carries no `profile` field and is scoped by its `spec_refs`
alone.

### Vector file schema

Each file is a JSON object:

- `function` (string) — the behavior under test. The harness dispatches on this name.
- `spec_refs` (array of strings) — the `VCSX-SPEC.md` sections the expected outputs are derived from,
  verbatim. Expected values are never invented; they are read from these sections.
- `description` (string) — what the function computes.
- `given` / `expect` (strings at the file level) — the human-readable shape of a vector's input and
  output for this function.
- `notes` (array of strings, OPTIONAL) — interpretation the harness needs beyond plain equality.
- `vectors` (array) — each with `id` (unique within the file), OPTIONAL `description`, `given`
  (the inputs), and `expect` (the expected outputs, or `{ "error": <class> }` for a failure vector).

The success-or-error union in `expect` is decision 0048's convention, reused here unchanged.

### Harness contract

Identical in shape to the Symphony corpus. For every file and every vector:

1. Invoke the implementation's realization of `function` with `given`.
2. Assert the result equals `expect` — or, when `expect` names an `error`, that the behavior fails and
   raises that error class.

Two interpretation notes apply:

- **Keys absent from `expect` are unconstrained.** This is the convention `resolve_config_defaults`
  already uses in the Symphony corpus, and it lets a vector pin the specified part of a behavior
  without pinning an unspecified one.
- **`match_edge` derives the proto class itself.** A vector supplies a trigger token, not its class,
  because `VCSX-SPEC.md` Section 12.1's algorithm calls `proto_class(op, reason)` — so a vector
  exercises the registry and the ladder together, as the engine does.

### What the slice covers

| File | Function | Derived from |
|------|----------|--------------|
| `vectors/match-edge.json` | `match_edge` | Sections 5.3, 5.4, 6.5, 12.1 |
| `vectors/base-resolution.json` | `resolve_base` | Sections 6.4, 12.4 |
| `vectors/exit-codes.json` | `exit_code_for_status` | Sections 8.2, 8.3, 8.5 |
| `vectors/policy-validation.json` | `validate_policy` | Sections 5.4, 6.1, 6.4, 6.7, 6.10, 8.5 |
| `vectors/identity-precondition.json` | `requires_commit_identity` | Sections 8.1, 8.6, 12.2, 12.3 |

75 vectors. All are pure over their inputs: no repository, network, forge, subprocess, or
filesystem. (The slice was authored at 49 and grew by four as decisions 0054–0056 resolved its
findings, each turning an unassertable behavior into an asserted one, by three more as decision
0057 added the universal reasons and redefined `merge:blocked`, by four more as decision 0066 gave
the well-formedness conditions a reason — the parse failure among them is judged from file text
rather than from a document and so has no vector, which `policy-validation.json`'s notes record —
by three more as decision 0067 pinned what an edge carrying no `from` does inside a from-context,
and by twelve more as decision 0074 scoped the commit-identity precondition to the entry point.)

`proto_class` has no vector file of its own. It is a lookup over the Section 4.3 registry, and
`vocabulary.json` already **is** that registry — a vector file would duplicate it with no added
assertion. Check a reason's class against `vocabulary.json`; `match_edge`'s vectors exercise the
lookup in composition.

### Deferred to later slices

Conformance-relevant but not deterministic from inputs alone, so they need fixtures or live services:

- **Front-end sequences** (`ship`, `land`; Sections 7.1–7.2, 12.2–12.3) — they run operations against
  a real repository and forge.
- **Plugin behavior** — checkout-mode detection, the pinned never-forced push refspec and the
  history-preserving work-branch update, and both halves of the undeclared-capability case:
  `capability_unsupported` at validation and the operation's `unsupported` reason at first use
  (Sections 3.3, 9.1–9.3). The last two need a capability descriptor as input, which no vector file
  supplies.
- **Invocation preconditions** (Section 8.6) — whether the work branch derives and whether a commit
  identity is well formed are judged against a real checkout by a real backend, through
  `accepts_branch_name` and `accepts_identity` (Section 9.1), so no vector file can supply the input.
  The reason tokens themselves are in `vocabulary.json` under `precondition_reasons`. The one half
  that is determined by the invocation alone — which entry points require an identity at all — is
  covered by `identity-precondition.json`; what a dispatch does where no identity was required
  (`identity_missing`, Section 4.3) needs a backend and stays here.
- **Base-ref resolution and the acquire/use split** (Sections 6.4, 9.1) — which copy of the base a
  checkout holds, whether it holds one at all, and whether an acquisition failed are properties of a
  real checkout with a real remote. That covers the multi-remote read, `base_unavailable` from a failed
  `fetch_base`, and `status`'s `base_absent` output. It covers the counterpart half on the same
  reasoning: whether the remote carries no counterpart or could not be reached at all is a property of
  that remote, so the two `pull` results those conditions carry — `ok` for the benign absence and
  `failed` for the acquisition that did not complete (decision 0075) — have no vector either. The
  reason tokens are in `vocabulary.json` under `reasons`; the base-resolution vectors cover the branch
  half only, which is the half a policy document determines.
- **Message formulation** — `scan-content`, pull-request composition, and the `pr_to_squash` transform
  (Section 10), whose formats are repository-owned by construction.
- **Hook execution** and the execution-context split (Sections 3.2, 6.6) — process and trust-boundary
  behavior.

## Surfaced findings

Authoring vectors exercises `VCSX-SPEC.md` and surfaces under-specification. Per the decision-log
hygiene rule (decision 0045), a genuine gap becomes a decision rather than a guessed-at vector.

All three findings from the first slice are now resolved.

- **Unmatched lifecycle position — resolved (decision 0054).** Section 5.4 fixed the built-in default
  for an unmatched *operation outcome* and for an unmatched *signal*, but said nothing about a
  lifecycle position with no edge — the ordinary case, since a policy binds whichever positions it
  needs. Section 5.4 now states that an unmatched position is a benign no-op and the operation
  proceeds, with the distinction that makes it coherent: an operation outcome is a result requiring
  disposition, a position is an offered interposition point. `lifecycle_position_has_no_class_fallback`
  now asserts the outcome, and `unbound_lifecycle_position_proceeds` is added.
- **Class form of a concrete task-state event — resolved (decision 0055).** Section 5.3's signal ladder
  fell back to "its class form" for a `#class`-shaped event token such as `task:#needs_help`, but
  `needs_help` is not a proto class and no concrete-to-class mapping existed. The rung is removed
  rather than defined: a proto class is a property of an *operation result*, so a consumer-raised
  signal has none. Signals are matched exactly, the `#class` fallback is scoped to typed results, and
  the `#` in `task:#needs_help` is documented as naming a condition across tasks.
  `hash_shaped_task_event_is_an_ordinary_token` and `signal_takes_no_class_fallback` cover both halves.
- **Configuration errors carry no reason token — resolved (decision 0056).** Section 6.10 enumerated
  five conditions and Section 8.3 mapped them to exit `2`, but named no token, so a caller could tell
  *that* a policy was refused but not *why* without parsing `message`. Section 6.10 now carries a
  nine-token registry. Resolving it exposed a second defect fixed in the same decision: Section 8.2
  defined `status` as three proto-class values with none corresponding to Section 8.3's exit `2`, so
  the two sections could not both be satisfied — `usage_or_config` is now a fourth invocation status.
  Every failing `validate_policy` vector names its reason.

A fourth finding arrived from the other direction — an engine implementation reading the corpus
rather than an author writing it — and is resolved the same way.

- **An unscoped edge inside a from-context — resolved (decision 0067).** Every `match_edge` vector
  but the two from-context ones passed `"from_context": null`, and both of those exercised edges
  that *carry* `from`, so the combination an implementation meets first — an ordinary edge with no
  `from`, fired while the consumer is in a context — was untested. Section 5.4's "absent such a
  model the key is the trigger alone" settled the all-or-nothing configurations and not the mixed
  one, which is the only configuration a repository running a transition graph is in. Section 5.4
  now states that an edge carrying no `from` is unscoped and is a candidate in every from-context;
  that a scoped edge is selected over an unscoped one for the same trigger key, the two being
  distinct keys rather than a duplicate; and that the ladder selects the key before the from-context
  selects among its edges. `unscoped_edge_matches_inside_a_from_context`,
  `scoped_edge_wins_over_unscoped_edge_in_its_context`, and `ladder_outranks_the_from_context` cover
  the three.
