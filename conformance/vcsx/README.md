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

Two further keys appear on an entry rather than on a group, where the specification fixes structure
inside one:

- `fields` (array, OPTIONAL) — the fields the specification fixes inside an entry's record, for a key
  carrying structured data rather than a bare value. Either an array of strings, or an array of
  objects whose `name` is the field name and whose remaining keys are the properties the
  specification fixes about that field. Every `output_keys` entry carrying one uses the object form;
  `task_model`'s is the group-level field list of one of the two departures above and keeps the
  string form.
- `values_from` (string, OPTIONAL) — the group that closes a value space: carried on a `fields`
  member, or on the entry itself where the key is scalar. It is present **only** where
  `VCSX-SPEC.md` fixes that space to exactly one group, so a type generated for the field may close
  its enum at that group's entries. Its absence is not a claim that the space is open — a field whose
  space is a *subset* of a group, a composed grammar, a repository-authored token or an
  `Implementation-defined` value carries none, and the entry's `meaning` records which. A link the
  registry would need and the prose does not fix is `Precedence`'s trigger, not a link to invent
  (decision 0131).

`schema_version` is `2`. Adding a group is additive and did not bump it; promoting `fields` from
strings to objects is the first change to the shape of an existing field, and a consumer reading
`fields` as strings branches on the version.

## Normalizations

The registry is a faithful view, not a byte-for-byte transcription. Three places it normalizes:

- **`reasons`** is keyed one entry per `(operation, reason)`. Section 4.3's combined rows expand: the
  `status` / `diff` row to `status:ok` and `diff:ok`, the four universal rows to one entry per
  operation they cover — `failed` and `unsupported` for every operation the registry covers,
  `blocked` and `hook_unanswered` for every gated one, each marked `universal: true` — and the two
  `(any forge)` rows to one entry per operation whose forge call the condition prevented (`push`,
  `create_pr`, `merge`, `await_checks`), each marked `forge_universal: true`. So 44 table rows
  yield 75 entries. Section 4.3's `Default need` column expands with them: `blocked`'s one row
  becomes four entries carrying the same need, so 19 rows with a need yield 28 entries with one.
  The two markers are separate fields rather than one scope enum, because they answer different
  questions — whether a reason is defined for every operation the registry covers, and whether it
  is defined for the ones that reach a forge — and a consumer generating a per-operation enum
  reads both. What the
  registry covers is Section 4.3's own invariant: an operation whose every outcome the specification
  reports as a configuration error carries no reason there, which is `load_policy` and is why
  `reasons` has no entry for it. `provision` is covered.
- **`operations`** carries `lifecycle_position: null` for every operation Section 4.1 gives no
  position, rather than omitting the field. The null is what a generator reads to apply Section
  4.3's invariant from the other side: an operation with no `before:<op>` position carries neither
  `blocked` nor `hook_unanswered`, so which universal reasons an operation has follows from the
  field rather than from a list this file would have to keep current.
- **`reasons`** likewise carries `default_need: null` for every `done` and `error` entry, where
  Section 4.3's column reads `—`, rather than omitting the field — the same choice, for the same
  reason: a generated record has the property either way, and its absence would be indistinguishable
  from a transcription that missed it.

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

## What this registry publishes

`Precedence` above says the specification governs and this file is derived. What the derived view
*contains* is a separate question, and it is the one a report against this file turns on.

**The test (decision 0103): a prose enumeration is published when something outside the
implementation's own source spells it** — a repository author writing configuration, a Conformance
Statement author filling a table, or a conformance check asserting a value. Not whether the set is an
enumeration, but *what reads the spelling and what happens when the reading is wrong*: a set nothing
reads has no divergence to catch, and publishing it would make the registry an inventory rather than
a derived view. The test was introduced in `conformance/README.md` for the Symphony registry and
governs this one on the same terms.

Decision 0131 applied it here, prompted by a set that passes it and was carried only inside a
`meaning` string — `outputs.forge_unavailable_condition`'s three conditions, whose sibling set had
had `hook_conditions` all along. The file was swept rather than the one report answered: every
`meaning` and `note` scanned for a value set closed in prose and spelled nowhere as data. **Five
hits, four of them prose *about* sets the file already carries as data and one the reported gap**,
now published as `forge_unavailable_conditions`. The instrument is in that decision's `Background.md`
and is meant to be re-run — a hit published by nothing is a new instance of the same defect.

A `values_from` link is the same question one level down, over a field's value space rather than a
set, and is authored under the same discipline: only where the specification fixes that space to
exactly one group. `unperformed_intents`' `action` is the worked counter-example — its space is the
`effected_by: "consumer"` subset of `actions` rather than that group, and a subset is not a link
this registry can state without fixing a property the specification does not. `unanswered_gates`'
`position` was a second one until decision 0134: `lifecycle_positions` was the *required* set an
engine could add to, so a generator told to close that enum would have rejected a conforming
engine's own gate. The positions are now fixed by the specification at a version and extended only
by a MINOR release (Sections 4.1, 8.5), so the space is exactly that group and the link is authored.
Each field that lacks a link and might look as though it wants one says why in its entry's
`meaning`.

This section carries no deferral list. A bullet naming the reader a set lacks belongs to a set
actually derived, and deriving the full list for this specification is separate work.

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

**A `given` field naming an invocation input MUST use `VCSX-SPEC.md` Section 8.1's spelling for it.**
Section 8.1 enumerates the invocation surface twice — the arguments and the consumer-configuration
keys — and requires that "argument *names* for shared concepts MUST match this specification"; a
vector file is a derived view, so a second spelling here is drift in the one direction this tree
exists to catch, and a runner executing such a vector against a real engine has to invent the mapping.
A field naming anything else is not bound by the rule: an entry point, the policy document, a value
the engine derives or holds, or an envelope field is named by whatever the function under test calls
it. Decision 0130 records why the rule is here — twice a vector modelled an input the contract did not
carry, and once it renamed one the contract did.

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
| `vectors/policy-validation.json` | `validate_policy` | Sections 4.1, 5.4, 5.6, 6.1, 6.4, 6.6, 6.7, 6.11, 8.5, 10.2 |
| `vectors/identity-precondition.json` | `requires_commit_identity` | Sections 8.1, 8.6, 12.2, 12.3 |
| `vectors/base-precondition.json` | `requires_base_branch` | Sections 6.4, 8.1, 8.6, 12.3 |
| `vectors/policy-pin-precondition.json` | `establish_policy_pin` | Sections 4.1, 6.1, 8.1, 8.2, 8.6 |
| `vectors/resume-precondition.json` | `establish_resume` | Sections 5.5, 8.1, 8.6, 12.2, 12.3 |
| `vectors/compose-envelope.json` | `compose_envelope` | Sections 4.3, 5.2, 5.4, 8.2, 8.4 |
| `vectors/front-end-sequence.json` | `front_end_sequence` | Sections 5.2, 5.4, 5.6, 7.1, 7.2, 8.2, 12.1, 12.2, 12.3 |

147 vectors. All are pure over their inputs: no repository, network, forge, subprocess, or
filesystem. (The slice was authored at 49 and grew by four as decisions 0054–0056 resolved its
findings, each turning an unassertable behavior into an asserted one, by three more as decision
0057 added the universal reasons and redefined `merge:blocked`, by four more as decision 0066 gave
the well-formedness conditions a reason — the parse failure among them is judged from file text
rather than from a document and so has no vector, which `policy-validation.json`'s notes record —
by three more as decision 0067 pinned what an edge carrying no `from` does inside a from-context,
by twelve more as decision 0074 scoped the commit-identity precondition to the entry point, by
four more as decision 0080 drew the boundary between the cycle of lifecycle positions validation
refuses and the cycle through a typed operation result the flow bound holds, by two more as
decision 0081 made a hook declaring no unit to run a document defect while leaving whether the named
unit exists to the worktree, and by four more as decision 0084 gave a template body source with no
unit bound a reason and reserved an exit code for an invocation that produced no result, and by
fourteen more as decisions 0088–0090 gave the envelope an answer for a flow the policy failed, for a
result no action disposed of, and for an invocation whose arguments named no entry point — the
enumeration that found them ran every Section 5.2 disposition against every Section 4.2 class and
broke on three, so the file exists to keep those three asserted. It reached 99 there and the
enumeration stopped while the corpus did not, so the rest is reconstructed from the history rather
than from a running note: by one more as decision 0094 made `[base] branch` optional, by two more as
decision 0096 refused a policy branch equal to the resolved base, by three more as decision 0099 gave
a `[messages.squash]` transform its bound-unit condition, by one more as decision 0100 made an edge's
`context` key ignored rather than refused, and by sixteen more as decision 0101 scoped the base
precondition and base resolution to the policy source. Two decisions have taken vectors away: 0122
removed the five signal vectors and added `unknown_trigger_token_is_refused` in their place, and 0129
removed the five that exercised the from-context. Thirteen more arrived with decisions 0143 and
0152, which fixed where a substituted result lands in a front-end sequence and what such a sequence
must reach; that file is per *step* rather than per invocation, so it stays pure over its inputs
like the rest. Twenty-one more arrived with decisions 0141 and 0142: four in
`policy-validation.json` for the two operations that run outside the action-policy machine, and two
new files for the preconditions those decisions added — the policy-surface pin, and the resume
token's binding to the entry point that issued it. Both new files model an opaque engine-issued
value as a label, which is what a pure file can honestly assert about a value this specification
fixes no encoding for; each says so in its own notes.)

### Fault-injection vectors (schema only)

A second **kind** of vector file is fixed here and carries no data in this repository. Where a
pure-function file states a mapping any JSON reader can check, a fault-injection file states what a
conforming engine produces when a forge behaves badly — and asserting that requires something to
*be* a forge and return a chosen response at a chosen moment. That is a harness, and a harness is a
program in an implementation's language, not data derived from a specification.

So the halves are split where each can be stated authoritatively. **This repository fixes the
assertion**, read from `VCSX-SPEC.md` as every entry here is. **An implementation authors the
cases**, against the forge twin it owns; the fixture — the bytes a forge returns, which header
carries a reset, what a drifted payload looks like — is a property of a forge and of the backend
talking to it, and a GitHub twin and a Forgejo twin inject one condition through entirely different
responses.

A runner that cannot execute a fault-injection file MUST report it as **not run**, never as passed.
Every file under `vectors/` today is runnable by anything that reads JSON, and that property is what
makes "the corpus is green" mean one thing; a file whose execution needs a harness would otherwise
make it mean two, depending on the runner.

The injected conditions, each read from the section it is derived from:

| Injected condition | Derived from |
|--------------------|--------------|
| A rate-limited refusal | Sections 4.3, 9.2 |
| A server error | Sections 4.3, 8.2, 9.2 |
| An expired network bound | Sections 8.1, 9 |
| A transport failure | Sections 4.3, 8.2, 9 |
| A conditional read the forge reports unmoved | Sections 4.1, 8.1, 8.2, 9.2 |
| A response missing a field a capability depends on | Sections 9, 9.2 |

Each vector MUST assert all of:

- the **reason** the operation reports and its **proto class** — the difference between
  `rate_limited` and `failed` being the difference between a run that escalates and a run that ends
  (Sections 4.3, 5.4);
- the **need** and its **`retryable`** value (Section 8.4);
- the **`outputs` keys** that must be present — `forge_budget` on any forge-touching call,
  `forge_unavailable_condition` where the reason is that one, `pr_state_unchanged` on a satisfied
  conditional read (Section 8.2);
- for a drift case, that the answer is **undetermined** and distinguishable from the legitimate
  absent case (Sections 9, 9.2);
- and that the operation **did not act** — no second pull request, no push over a closed one, no
  merge on an unread head.

The last is stated separately because the others are all readable off an envelope while it is a
statement about the forge afterwards. A vector asserting only the envelope would pass for an engine
that reported `create_pr:failed` and created a pull request anyway, which is the failure the drift
case exists to catch.

`proto_class` has no vector file of its own. It is a lookup over the Section 4.3 registry, and
`vocabulary.json` already **is** that registry — a vector file would duplicate it with no added
assertion. Check a reason's class against `vocabulary.json`; `match_edge`'s vectors exercise the
lookup in composition.

### Deferred to later slices

Conformance-relevant but not deterministic from inputs alone, so they need fixtures or live services:

- **Front-end sequences** (`ship`, `land`; Sections 7.1–7.2, 12.2–12.3) — they run operations against
  a real repository and forge.
- **Provisioning** (`provision`, Sections 4.1, 9.1) — obtaining and refreshing a repository acts on
  a real remote and a real store, so none of the operation's results has a vector: `provision:ok`,
  `provision:unreachable`, and `provision:store_unsupported`, whose input is a capability descriptor
  no vector file supplies (Section 9.3). The tokens are in `vocabulary.json` under `reasons`. The
  operation's exemptions are on the same side for a different reason: that a `provision` is
  validated against no policy document and establishes no checkout-reading precondition (Sections
  6.1, 6.11, 8.6) is an absence of refusals, and a vector corpus asserts the reason a refusal
  carries rather than that none was carried.
- **Plugin behavior** — checkout-mode detection, the pinned push refspec whose push never drops,
  rewrites or re-parents a commit already on the remote work branch (decision 0083), the
  history-preserving work-branch update, and both halves of the undeclared-capability case:
  `capability_unsupported` at validation and the operation's `unsupported` reason at first use
  (Sections 3.3, 9.1–9.3). The last two need a capability descriptor as input, which no vector file
  supplies — so a `[messages.squash] strategy` refused against a forge's declared strategies has no
  vector either, whether the policy states the strategy or takes the Section 6.8 default. The forge
  repository coordinate, the backend selection, the access parameters, `provision`'s store location
  and the base branch are on the same side: whether one was supplied is determined by the invocation
  (`forge_coordinate_missing`, `local_vcs_missing`, `policy_branch_missing`, `git_access_missing`,
  `forge_access_missing`, `store_location_missing`, `base_branch_missing` and
  `base_branch_not_permitted`, Section 8.6),
  which no vector file models. `base_branch_missing` is the near miss: `[base] branch` is one of its
  three sources and vectors do model policies, but the other two sources and the invoked entry point
  are not vector inputs, so the condition is not determined by a policy document alone.
- **Two of the four unusable-policy conditions** (Section 6.1) — `policy_source_unreadable` needs a
  source that cannot be read and `policy_not_found` needs a source that carries no file, and a
  vector file supplies a policy document rather than the place one was read from. Their two
  siblings, `malformed_policy` and the consistency reasons, are modelled here. The tokens are in
  `vocabulary.json` under `config_reasons`.
- **Invocation preconditions** (Section 8.6) — whether the work branch derives and whether a commit
  identity is well formed are judged against a real checkout by a real backend, through
  `accepts_branch_name` and `accepts_identity` (Section 9.1), so no vector file can supply the input.
  The reason tokens themselves are in `vocabulary.json` under `precondition_reasons`. The one half
  that is determined by the invocation alone — which entry points require an identity at all — is
  covered by `identity-precondition.json`; what a dispatch does where no identity was required
  (`identity_missing`, Section 4.3) needs a backend and stays here. `base-precondition.json` covers
  the same half for the base, which the policy source scopes rather than the entry point alone:
  under `target_branch` the base is what locates the policy, so every entry but `provision` requires
  one and requires it before validation (Sections 6.4, 8.6). `policy-pin-precondition.json` and
  `resume-precondition.json` cover the two judged wherever their argument is supplied whatever the
  entry, which is a comparison rather than a requirement: each models the engine-issued value it
  compares as a label, because both are opaque and this specification fixes no encoding for either
  (Sections 8.1, 8.6).
- **Base-ref resolution and the acquire/use split** (Sections 6.4, 9.1) — which copy of the base a
  checkout holds, whether it holds one at all, and whether an acquisition failed are properties of a
  real checkout with a real remote. That covers the multi-remote read, `base_unavailable` from a failed
  `fetch_base`, and `status`'s `base_absent` output. It covers the counterpart half on the same
  reasoning: whether the remote carries no counterpart or could not be reached at all is a property of
  that remote, so the two `pull` results those conditions carry — `ok` for the benign absence and
  `failed` for the acquisition that did not complete (decision 0075) — have no vector either. The
  reason tokens are in `vocabulary.json` under `reasons`; the base-resolution vectors cover the branch
  half only, which is the half a policy document determines.
- **A capability that could not determine its answer** (Section 9, decisions 0076, 0077) — whether a
  backend could read the checkout, whether a forge could be asked for a work branch's pull request, and
  whether a pull request's head advanced between the read and the merge are all properties of a live
  checkout, remote or forge, so none of the results those conditions carry has a vector:
  `checkout_unreadable`, the `push:failed` and `create_pr:failed` a `pr_state` that could not answer
  produces, `status`'s `pr_state_unavailable` output, the `commit:failed` an undetermined `is_dirty()`
  produces through `ship`'s guard, and `merge:head_moved`. The tokens are in `vocabulary.json` under
  `reasons` and `precondition_reasons`; what the corpus can check is that no engine spells any of them
  as the value's absent case, which needs the backend the vectors do not have.
- **Message formulation** — `scan-content`, pull-request composition, and the `pr_to_squash` transform
  (Section 10), whose formats are repository-owned by construction.
- **Hook execution** and the execution-context split (Sections 3.2, 6.6) — process and trust-boundary
  behavior. Whether a lifecycle position ran is observed the same way, so decision 0078's rule that a
  gated operation's position runs as part of every dispatch — including a `[policy]` `run_op` edge's —
  has no vector: the check is that a hook bound at `before:commit` ran, which needs the hook. Decision
  0079's rule that an operation acts on the state its position inspected needs the same fixtures for
  the other direction — a live working tree that can change between the two — so `commit:worktree_moved`
  has no vector either, as `merge:head_moved` has none. Both tokens are in `vocabulary.json` under
  `reasons`. Decision 0081's bound on the engine's wait for a hook is deferred on the same
  reasoning: what a bound produces — `hook_unanswered` for a gate, an `outputs` entry for a
  result-triggered hook — is observed by running a unit that does not answer, so only the document
  half has vectors (a hook declaring no unit to run, refused at validation).

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
  *(Later: decision 0122 removed the signal trigger kind entirely — nothing in the invocation contract
  could raise one, so the whole kind was surface with no producer. Both vectors are removed, and
  `unknown_trigger_token_is_refused` replaces them: a token that is neither a position nor a typed
  result is now refused at validation rather than matched exactly. The `#class` fallback stays scoped
  to typed results, which is the half of this finding that survives.)*
- **Configuration errors carry no reason token — resolved (decision 0056).** Section 6.11 enumerated
  five conditions and Section 8.3 mapped them to exit `2`, but named no token, so a caller could tell
  *that* a policy was refused but not *why* without parsing `message`. Section 6.11 now carries a
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
  *(Later: decision 0129 removed the from-context from the engine's matching entirely — Section 8.1
  carries no argument supplying one, so the axis this repair pinned the behavior of was one no
  invocation could ever set. All five from-context vectors are removed, including the three added
  here, and `edges_differing_only_by_from_are_one_duplicate_edge` in `policy-validation.json` replaces
  the vector that asserted the opposite: a `from` is now an ignored unknown key, so two edges
  differing only by it collide on one trigger. What survives of this finding is its diagnosis of the
  corpus — that the vectors modelled a context the contract never transmitted — which is the evidence
  0129 turned on.)*

A fifth arrived from a downstream consumer's failures rather than from the corpus or an engine, and
is the reason the fault-injection kind exists at all.

- **A green corpus over an untested family — resolved in shape, deferred in data.** Every vector in
  this tree passed while the transient family — a rate-limited refusal, a server error, an expired
  bound, a transport failure, a conditional read, a response missing a depended-on field — had no
  coverage whatever. The failures that reached a downstream consumer were drawn entirely from that
  family, which is what makes a green corpus weak evidence about it: the corpus was not failing to
  assert these behaviors incorrectly, it was not addressing them. The shape of the assertion is now
  fixed above and the cases are owed by whichever implementation owns a forge twin, so the gap is
  recorded and assignable rather than invisible. Until those cases exist, nothing in this tree
  exercises a forge that misbehaves.

A sixth is about this tree rather than about `VCSX-SPEC.md`, and was found by sweeping the corpus
instead of by writing a vector.

- **A `given` field naming an invocation input under its own spelling — resolved (decision 0130).**
  Three times a vector file has modelled an engine input the invocation contract did not define under
  that name: `consumer_capabilities` for an input Section 8.1 did not carry at all (issue #68,
  repaired by decision 0121 as `effectable_actions` and `bound_units`), `from_context` for another
  (issue #77, resolved by decision 0129 by removing the axis), and — found by the sweep 0129
  authorised — `consumer_capabilities` still standing in all 38 `policy-validation.json` vectors after
  0121 named the concept, alongside `supplied_base` in `base-resolution.json` for what Section 8.1
  calls `base_branch`. The first two were gaps in the contract; this one is a gap in the
  reconciliation, the corpus having been written from what the Section 12 algorithms take and Section
  8.1 from what a caller sends. Both fields now use Section 8.1's spelling. The specification needed
  one repair rather than none: `resolve_base` (Section 12.4) read `supplied_base` as a free name its
  signature never bound, so the corpus was mirroring a gap rather than a parameter, and the signature
  now carries `base_branch`. The rule under "Vector file schema" above is the standing check, placed
  where a vector author meets it before writing a field name.
