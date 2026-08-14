# vcsx Engine Conformance Statement — TEMPLATE

Copy this file into your engine's own repository, rename it (for example `CONFORMANCE.md`), and fill
every `<...>` placeholder and `[ ]` box. This template is a *checklist of pointers* into
`VCSX-SPEC.md`; it restates no obligation's substance. Where a row cites a section, the citing
document is `VCSX-SPEC.md` unless another document is named. Section numbers are hints paired with
titles — resolve by title if numbering has shifted (see decision 0002).

The Conformance Statement is the single place an engine publishes the choices `VCSX-SPEC.md` leaves
open. It records **contract-visible** choices only — those a consumer, auditor, or peer engine can
observe. Purely idiomatic choices (concurrency model, error-handling idiom, libraries, project layout)
are *not* recorded here; the contract cannot see them and `VCSX-SPEC.md` is silent on them.

An engine embedded in a Symphony deployment is declared from the consumer's side as a version pin;
see `CONFORMANCE-STATEMENT-TEMPLATE.md` (`SPEC.md` Section 19). This Statement is the engine's own and
stands alone — an `engine-direct` deployment claims no Symphony profile (`SPEC.md` Section 3.4) and
publishes only this document.

---

## 0. Identity and Targeted Revisions

- Engine name: `<name>`
- Implementation language / runtime: `<language>`
- Maintainer / contact: `<contact>`
- Statement date: `<YYYY-MM-DD>`
- `VCSX-SPEC.md` revision targeted: `<revision or commit>`
- `VCSX-CONTRACT.md` revision targeted: `<revision or commit>`

## 1. Version and Major-Stable Surface

Section 8.5 "Versioning and the Version Grammar" fixes what may not change within a `MAJOR`: the
invocation envelope, the proto classes, the exit-code mapping, the `need` vocabulary, and the class of
every listed reason.

- Engine version (`MAJOR.MINOR`): `<x.y>`
- `vcsx_version` emitted in the result envelope (Section 8.2): `<value>`
- Lowest `version_floor` this build satisfies (Sections 6.2, 8.5): `<floor>`
- Below-floor behavior is fail-closed with a usage/config result (REQUIRED; not a choice): [ ] yes
- A `version_floor` that is not a `MAJOR.MINOR` version is refused as `malformed_policy` rather than
  compared (Sections 6.2, 6.10; REQUIRED, not a choice): [ ] yes

## 2. Required Surface Implemented

Section 13.2's implementation checklist is the definition of done; this section only declares the
claim. Mark each complete.

- [ ] One policy-graph executor run by both front-ends; `ship`, `land`, and the embedded-driver
      contract (Sections 7.1–7.3)
- [ ] The action-policy machine: triggers, actions, the `#class` fallback, fail-safe on an unmatched
      outcome, no-op on an unmatched signal, determinism (Section 5)
- [ ] The required operation set and the four required lifecycle positions (Section 4.1)
- [ ] The reason-token registry with its stable proto classes (Sections 4.2, 4.3)
- [ ] `repo.policy.toml` loader and validation, with the `vcsx.toml` merge, the refusal of a policy
      that is not well formed, base resolution, and execution-context labeling (Sections 3.2, 6)
- [ ] The invocation contract: result envelope, exit codes, escalation payload, versioning
      (Section 8)
- [ ] The plugin API with VCS and forge backends and their capability descriptors (Section 9)
- [ ] Message-formulation seams — `scan-content`, pull-request composition, `pr_to_squash` — with no
      built-in format (Section 10)
- [ ] Checkout-mode handling (git, jj, jj secondary workspace) and a pinned, never-forced push
      refspec (Sections 3.3, 9.1)

## 3. `Implementation-defined` and `MUST document` Resolutions

One row per obligation `VCSX-SPEC.md` leaves to the engine. Fill the resolution column with the
concrete choice; do not leave a row blank.

| Obligation | Section | Resolution |
|------------|---------|------------|
| Checkout-mode detection mechanism | 3.3 | `<how git / jj / jj secondary workspace are distinguished>` |
| Flow bound: the `run_op` count (at least 64), and any further bound imposed | 5.6 | `<count, plus any wall-clock or other bound>` |
| `repo.policy.toml` discovery precedence (explicit override, then repository default) | 6.1 | `<...>` |
| The backend's default remote where `[engine] remote` is unset, per backend | 6.2 | `<name each backend uses>` |
| Form of a hook's engine-invoked `run` unit | 6.6 | `<executable path / shell string / named task / …>` |
| Hook bound: how long the engine waits for a hook to answer (at least 600 s admitted) | 6.6 | `<duration, and whether a deployment may configure it>` |
| Which reason is reported when several configuration conditions hold | 6.10 | `<first found / a documented precedence / all of them>` |
| Entry-point argument encodings (argument *names* for shared concepts are fixed) | 8.1 | `<CLI flags / JSON on stdin / in-process struct / …>` |
| How a front-end derives the forge repository coordinate where it defaults one | 8.1 | `<from the resolved remote's URL / not defaulted, always supplied>` |
| `detail` field of an `outputs.unanswered_gates` entry | 8.2 | `<what the engine places there for a gate that gave no usable answer>` |
| Escalation `detail` field contents | 8.4 | `<what the engine places there>` |
| Where a backend writes its own bookkeeping state to answer a capability | 9.1 | `<which capabilities, and what they write>` |

## 4. Reason Tokens Beyond the Registries

Sections 4.3, 6.10 and 8.6 permit an engine to add reason tokens and require it to document them;
Section 8.5 permits new tokens in a `MINOR` release. Leave any table empty if the engine adds none.

### 4.1 Operation Reasons (Section 4.3)

A consumer absorbs these through the `#class` fallback, so the proto class is the load-bearing column.

| Operation | Reason | Proto class | Meaning |
|-----------|--------|-------------|---------|
| `<op>` | `<reason>` | `done` / `needs_caller` / `error` | `<...>` |

### 4.2 Configuration Reasons (Section 6.10)

These carry no proto class and are reported under the `usage_or_config` status, which absorbs new
tokens without a class edge.

| Reason | Condition |
|--------|-----------|
| `<reason>` | `<...>` |

### 4.3 Precondition Reasons (Section 8.6)

These likewise carry no proto class and are reported under `usage_or_config`. They differ from
Section 4.2's by what they are judged from: a precondition failure needs the invocation's arguments
and the checkout, so it is not statically determinable from `repo.policy.toml`.

| Reason | Condition |
|--------|-----------|
| `<reason>` | `<...>` |

## 5. `need` Vocabulary Emitted

Section 8.4 makes the `need` vocabulary part of the public contract, documented and stable within a
major version. List every `need` this engine can emit, including the registry-named ones it uses.

| `need` | Emitted by (`op`, position, action, or bound) | Meaning to the resolver |
|--------|-----------------------------------------------|-------------------------|
| `integrate_then_retry` | `<...>` | `<...>` |
| `reread_then_retry` | `<...>` | `<...>` |
| `resolve_conflicts` | `<...>` | `<...>` |
| `supply_identity` | `<...>` | `<...>` |
| `await_checks` | `<...>` | `<...>` |
| `human_review` | `<...>` | `<...>` |
| `intervention` | `park` (Section 5.2) | `<...>` |
| `flow_exhausted` | the flow bound (Section 5.6) | `<...>` |
| `<other>` | `<...>` | `<...>` |

Every conforming engine can emit `intervention` and `flow_exhausted`: `park` is an action any
`repo.policy.toml` may write, and Section 5.6 requires the flow bound, so both are listed rather than
left to the `<other>` row. They are the two needs no front-end resolves (Section 8.4); record how this
engine surfaces each hold.

The rest are reachable from the registry rather than from a policy alone: Section 4.3 gives every
`needs_caller` reason a default `need`, and the built-in default raises it where nothing in the policy
named one, so an engine defining the required operation set can emit each of the six. Record the
`<other>` row for a need this engine adds — including the default need of any reason it adds beyond
the registry.

## 6. Plugin Capability Descriptors

Section 9.3 requires the executor to read a descriptor before invoking a capability and forbids
invoking an undeclared one; Section 6.10 makes a policy requiring an unsupported capability a
configuration error. Declare what each shipped backend advertises.

### 6.1 VCS Backends (Section 9.1)

| Backend | Supported modes | Recorded-resolution reuse | Operates with no colocated remote |
|---------|-----------------|---------------------------|-----------------------------------|
| `<git / jj / …>` | `<...>` | [ ] | [ ] |

Section 9.1's required capabilities are a minimum. If this engine defines operations beyond Section
4.1, list what it additionally requires of a VCS backend; leave empty if it defines none.

| Capability | Required by (operation) | Signature and result |
|------------|-------------------------|----------------------|
| `<...>` | `<...>` | `<...>` |

### 6.2 Forge Backends (Section 9.2)

| Backend | PR create/update | Merge strategies | Review-thread writes | Native issue linking |
|---------|------------------|------------------|----------------------|----------------------|
| `<github / forgejo / …>` | [ ] (REQUIRED) | `<merge / squash / rebase>` | [ ] | [ ] |

A policy that states no `[messages.squash] strategy` is refused against a backend that does not
declare `merge`, because the Section 6.8 default is `merge` and the engine holds it — which is one
half of Section 9.3's split. The other half, an unsupported capability reported at first use, has no
producer among the required operation set and policy keys (Section 13.1), so an engine claiming it
names what the claim was demonstrated against:

| First-use `unsupported` demonstrated against | Operation | Capability |
|----------------------------------------------|-----------|------------|
| `<engine-added operation / OPTIONAL capability, or "not claimed">` | `<...>` | `<...>` |

## 7. Consumer-Effected Actions

Section 5.2 makes `create_task`, `set_state`, and `notify` the consumer's to perform; the engine emits
the intent. The dispositions below are fixed by the specification, not chosen — record how this engine
realizes each, and note any divergence in Section 8.

| Action | Behavior with no consumer that can effect it | As realized |
|--------|---------------------------------------------|-------------|
| `create_task` | benign no-op, surfaced in `outputs.unperformed_intents` (Sections 5.2, 8.2) | `<...>` |
| `set_state` | configuration error at validation (Section 6.10) | `<...>` |
| `notify` | benign no-op, surfaced in `outputs.unperformed_intents` (Sections 5.2, 8.2) | `<...>` |

## 8. Conformance Evidence and Known Deviations

- Section 13.1 test matrix: [ ] all covered · [ ] partial — gaps: `<...>`
- Shared vector corpus (`conformance/vcsx/vectors/`, Section 13.1): [ ] all vectors pass ·
  [ ] partial · [ ] not run · corpus revision: `<id>`
- Shared token vocabulary (`conformance/vcsx/vocabulary.json`, decision 0051): [ ] checked against ·
  [ ] not checked · revision: `<id>`
- Known deviations from `VCSX-SPEC.md` (should be empty for a clean claim; record any divergence with
  its rationale, and open a decision in the specification repository's log if it reflects a genuine
  specification gap — decision 0045's decision-log hygiene):
  - `<none, or: behavior — divergence — rationale>`
