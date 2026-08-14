# Plan — 0092 Backend, forge and tracker selection are the consumer's, read from a consumer config

## Scope

`VCSX-SPEC.md`: Sections 3.3 "Checkout Modes", 6.1 "File Discovery and `vcsx.toml` Merge", 6.2
`[engine]` (renamed), 6.10 "Validation", 8.1 "Entry Points and Arguments", 8.6 "Invocation
Preconditions", 9.3 "Capability Descriptors", 11 "Security and Trust Model", 13.1 "Test Matrix", 13.2
"Implementation Checklist", 13.3 "Conformance Statement".

`VCSX-CONTRACT.md`: Section 4 "`repo.policy.toml` (Config Surface)" and Section 10 "Trust Sourcing and
the Secret/Integrity Taxonomy" — both list "engine selection" as a section of the repository-owned
surface, so the surface changes and the shared token list changes with it.

`SPEC.md`: Sections 5 "Configuration Contracts", 5.3 "Configuration Schema", 5.6 "`repo.policy.toml`
(Repository Way of Working)", 6.4 "Core Config Fields Summary (Cheat Sheet)", 9.7 "Repository
Provisioning and the VCS Engine", 15.4 "Configuration Trust Sourcing and Hook Safety", 17 "Test
Matrix", 18 "Implementation Checklist", plus Section 5.2's design note.

`conformance/vcsx/vocabulary.json`.

## Tokens introduced

- `[requires]` — replaces the `[engine]` table, holding `version_floor` alone.
- `local_vcs` — the consumer-supplied VCS selection: which VCS backend the plugin layer loads, and
  the mode for a checkout the engine creates (decision 0093). REQUIRED on every invocation; for a
  checkout the engine did not create, `detect_mode()` answers the *mode* while this still names the
  backend. Amended by this decision's review finding on the deleted `[engine] vcs` selector, which
  the narrower form left unnamed.
- `local_vcs_missing` — the precondition reason for its absence (Section 8.6).
- "consumer configuration" as a prose term, not a filename: discovery is `Implementation-defined`.

## Steps

1. **`[engine]` is renamed (Section 6.2)** — ensure the table that held `version_floor`, `vcs`,
   `forge` and `remote` holds `version_floor` alone and is named `[requires]`, described as what the
   policy document requires of the engine reading it. Ensure `vcs`, `forge` and `remote` no longer
   appear as `repo.policy.toml` keys anywhere in the document. *Done when*
   `grep -n '\[engine\]' VCSX-SPEC.md VCSX-CONTRACT.md SPEC.md` matches nothing.

2. **The rationale paragraph is replaced (Section 6.2 / `[requires]`)** — ensure the paragraph
   beginning "The backend selection is read here in both standalone and embedded use" is gone, and
   that its place is taken by a statement of the bootstrap cycle: the values needed to obtain a
   repository cannot be configured inside it, so the forge selection, its access parameters, its
   credentials and the remote are the consumer's (Section 8.1), while `repo.policy.toml` holds what a
   clone inherits unchanged. *Done when* the words "which code host a repository targets is
   repository-owned" no longer appear in the document.

3. **Consumer configuration (Section 8.1)** — ensure the section states that the consumer-supplied
   values it names — the forge selection, the access parameters and extension bag, the credential
   pair (all Section 0091), the remote, and the forge repository coordinate (decision 0085) — MAY be
   read by the engine from a **consumer-owned configuration file**, distinct from `repo.policy.toml`
   and never sourced from the repository. Ensure its discovery is stated `Implementation-defined` with
   a MUST-document clause. Ensure the section states that the file MAY carry a credential directly or
   a reference the consumer resolves, and that the engine does not persist a credential beyond an
   invocation. *Done when* the file is described with its discovery clause and both credential forms.

4. **No overlap with `repo.policy.toml` (Section 6.1)** — ensure the section states that the consumer
   configuration and `repo.policy.toml` carry disjoint keys, so the existing "`repo.policy.toml` keys
   take precedence on conflict" rule governs `vcsx.toml` alone and needs no exception. *Done when*
   the disjointness is stated and the precedence sentence is unchanged.

5. **Checkout mode is detected, not declared (Section 3.3)** — ensure the section states that the
   checkout *mode* is determined by the VCS backend's `detect_mode()` (Section 9.1) for a checkout
   the engine did not create, and carries no `repo.policy.toml` key. Ensure it also states that
   which *backend* does the detecting is the consumer's `local_vcs` (Section 8.1), REQUIRED on every
   invocation, so the two questions are separated rather than conflated. *Done when* Section 3.3
   names no policy key, `detect_mode()` is the only path stated for the mode of a checkout the
   engine did not create, and `local_vcs` is named as the backend selection.

6. **The remote (Sections 6.4 "`[base]` and Base Resolution", 8.1, 9.1)** — ensure the remote is the
   consumer-supplied value the repository was provisioned from, resolved once per invocation and
   supplied to each capability that takes one, preserving decision 0062's invariant that exactly the
   three network-touching Section 9.1 capabilities take it. Ensure base resolution still selects the
   copy of the base belonging to the resolved remote. *Done when* no `repo.policy.toml` key names a
   remote and the capability signatures are unchanged.

7. **Validation inputs (Section 6.10)** — ensure the "judged from four inputs and no others" passage
   is restated over five: the policy document with `vcsx.toml` merged in; what the engine holds
   independently of the invocation; **the consumer's selection and access configuration**; the actions
   the consumer can effect; and the repository units it bound. Ensure `capability_unsupported` is
   stated to turn on the descriptors of the **selected** backends. *Done when* the passage enumerates
   five inputs and the phrase "independently of the invocation" no longer covers the backend
   descriptors.

8. **The precondition boundary (Section 8.6)** — ensure the paragraph separating this registry from
   Section 6.10's states the boundary **one-directionally**: a configuration error is judged without
   reading the checkout. Ensure it does **not** characterize the precondition side as needing the
   checkout, since four entries — `arguments_unreadable`, `forge_coordinate_missing`,
   `git_access_missing`, `forge_access_missing` — are judged from the invocation's arguments alone
   (see this decision's review finding). Ensure the section states what separates the two registries
   where both are checkout-free: a configuration error names a defect the consumer repairs by editing
   a document, a precondition failure one it repairs by changing the invocation. Ensure the existing
   ordering rule survives — validation precedes precondition establishment, `arguments_unreadable`
   excepted — and that Section 8.6's closing sentence no longer cites `[engine]` for "the selection
   alone". *Done when* the boundary is stated over the config side only, the document/invocation
   distinction is stated, and no `[engine]` citation remains.

9. **Capability descriptors (Section 9.3)** — ensure "where determinable" is restated against the new
   boundary: a capability a backend declares statically follows from the consumer's selection, which
   the engine holds before it validates, so `capability_unsupported` remains a configuration error.
   *Done when* the section cites the consumer's selection rather than Section 6.2.

10. **Security and Trust Model (Section 11)** — ensure the section states that the selection, the
    access parameters, the credentials, the remote and the coordinate all come from the consumer, so
    which backend receives a credential and which endpoint it reaches are one decision made by one
    party. *Done when* the one-party statement covers the selection and not only the coordinate.

11. **`VCSX-CONTRACT.md` Sections 4 and 10** — ensure "engine selection" is removed from the list of
    `repo.policy.toml` sections and from the host-side-sourced Way-of-Working list, that `[requires]`
    takes its place in the Section 4 list so the contract and `SPEC.md` Section 5.6 enumerate the
    same sections, and that the surface names the consumer configuration as the engine's other input.
    *Done when* neither section lists engine selection as repository-owned and the two documents'
    section lists agree.

12. **`SPEC.md` operator surface (Sections 5.3, 6.4, 9.7)** — ensure the operator policy config's
    top-level key list includes `vcs` (absent today though Sections 6.4 and 9.7 document it), and that
    the per-repository `vcs` object carries the forge selection, the Section 0091 access parameters
    and extension bag, and the credential pair, alongside `author`/`actor`. Ensure Section 9.7 no
    longer says the engine reads the code host from `repo.policy.toml`. *Done when* `vcs` appears in
    Section 5.3's top-level list and Section 9.7's configuration bullet names the operator as the
    source of the selection.

13. **`SPEC.md` ownership prose (Sections 5, 5.2, 5.6, 15.4)** — ensure every list naming "engine
    selection" as base-revision-sourced Way of Working drops it, and that Section 5's dividing rules
    place the selection and its access configuration with the operator. Ensure Section 5.6's
    "Configuring Symphony therefore needs no knowledge of a repository's Way of Working" is narrowed
    to the policy machine, hooks, transitions and branch pattern, since the operator now names the
    host. *Done when* `grep -n "engine selection" SPEC.md VCSX-CONTRACT.md` matches nothing.

14. **`SPEC.md` cheat-sheet grouping (Section 6.4)** — ensure an operator-policy-config heading
    precedes `agent.default_agent`, so the `agent.*`, `codex.*` and `compute.*` fields no longer sit
    under the "Workspace hooks (repository-owned…)" heading. *Done when* every field under a
    repository-owned heading is repository-owned.

## Cross-cutting sync

- **`VCSX-SPEC.md` test matrix (Section 13.1)** — a policy carrying a removed key is ignored per
  Section 6.1's forward-compatibility rule rather than refused; a `[messages.squash] strategy` no
  selected forge declares is refused at validation with `capability_unsupported`; two consumers with
  the same consumer configuration and the same policy reach the same backend and remote.
- **`VCSX-SPEC.md` implementation checklist (Section 13.2)** — extend the policy-loader line with the
  consumer configuration as a second, disjoint input.
- **`VCSX-SPEC.md` Conformance Statement (Section 13.3)** — add a row for the consumer
  configuration's discovery precedence.
- **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`** — the template is the engine-side counterpart of
  Section 13.3 and drifts silently, since nothing validates it against the spec. Retire the
  `[engine] remote` row, add rows for the consumer configuration's discovery precedence and the
  `forge_parameters` keys each forge backend reads, and correct Section 4.3's preamble, which states
  the two-directional precondition boundary step 8 replaced.
- **`SPEC.md` cheat sheet (Section 6.4)**, **test matrix (Section 17)** and **checklist (Section 18)**
  — reflect the moved keys, the added `vcs` object fields, and the narrowed Way-of-Working claim.
- **`conformance/vcsx/vocabulary.json`** — update the `config_reasons` note, which currently records
  "Validation is judged from four inputs (Section 6.10)" and enumerates them.

## Anchor changes

- `repo.policy.toml` keys **`[engine] vcs`, `[engine] forge` and `[engine] remote` are removed**,
  superseded by consumer-supplied values (Section 8.1).
- The table **`[engine]` is renamed to `[requires]`**, retaining `version_floor`.
- `SPEC.md`'s phrase **"engine and code-host selection"** is removed from the `repo.policy.toml`
  section lists; the concept is now operator config.
- `SPEC.md` operator key **`vcs.api_key` is removed**, superseded by `vcs.git_credential` and
  `vcs.forge_credential` (decision 0091's credential pair). Recorded here rather than in 0091 because
  the `SPEC.md` operator surface is this decision's scope.
- `SPEC.md` gains operator keys `vcs.forge`, `vcs.git_access`, `vcs.forge_access`,
  `vcs.forge_parameters`, `vcs.remote` and `vcs.local_vcs`, and names `[requires]` as a
  `repo.policy.toml` section (it never named `[engine]`, so there was no rename to make).
- `VCSX-SPEC.md` gains the precondition reason **`local_vcs_missing`** (Section 8.6), added by this
  decision's review finding so that `local_vcs`'s REQUIRED status has a stated failure mode.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`'s row **"The backend's default remote where
  `[engine] remote` is unset"** is retitled to name the consumer-supplied `remote` and cites
  Section 8.1 rather than 6.2.

## Status

Applied to `VCSX-SPEC.md`, `VCSX-CONTRACT.md`, `SPEC.md`, `conformance/vcsx/vocabulary.json` and
`conformance/vcsx/vectors/policy-validation.json` (whose seven `[engine]` policy inputs the rename
would otherwise have left asserting a refusal the engine no longer makes). Step 8 was applied in the
amended, one-directional form recorded in this decision's first review finding.

Steps 5, 11 and the template sync bullet were applied in the amended form recorded in this decision's
second review finding: `local_vcs` is the VCS backend selection and not only a creation-time mode,
`[requires]` replaces "engine selection" in `VCSX-CONTRACT.md`'s Section 4 list rather than leaving a
gap, and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` is brought back into line with Section 13.3.
