# Plan — 0091 Forge access parameters, and the credential pair

## Scope

`VCSX-SPEC.md`: Sections 8.1 "Entry Points and Arguments", 8.6 "Invocation Preconditions", 9.1 "VCS
Backend Plugin", 9.2 "Forge Backend Plugin", 11 "Security and Trust Model", 13.1 "Test Matrix", 13.2
"Implementation Checklist". `conformance/vcsx/vocabulary.json`.

No `VCSX-CONTRACT.md` change: the invocation contract and the plugin API are deferred to
`VCSX-SPEC.md` (`VCSX-CONTRACT.md` Section 11), and this decision renames no shared token. The
parameters are consumer-supplied arguments rather than a `repo.policy.toml` section, which is the
only class of addition that reaches the surface.

No `SPEC.md` change **here**. Symphony must supply these values, but the operator-config keys that
hold them land with the rest of the operator surface in decision 0092, so that `SPEC.md`'s ownership
prose is edited once rather than twice.

## Tokens introduced

Spelled identically in every document (Section 14 alignment rule):

- Invocation inputs: `git_access`, `forge_access`, `forge_parameters` (OPTIONAL extension bag),
  `git_credential`, `forge_credential` (Default: `git_credential`).
- Precondition reasons: `git_access_missing`, `forge_access_missing`.

## Steps

1. **Common arguments (Section 8.1)** — ensure the common-argument list carries the **git-access
   parameter** and the **forge-API-access parameter**: where the version-control operations reach the
   remote, and where the forge operations reach the code host. Ensure each is stated REQUIRED under
   the condition that uses it — the git-access parameter where any operation that touches a remote
   may run, the forge-API parameter where a forge is configured — and that both are held opaque by
   the engine, as the forge repository coordinate, the commit identity and the base ref are. *Done
   when* both parameters appear in the common-argument list with their conditions and the opacity
   sentence.

2. **Extension bag (Section 8.1)** — ensure the section states that a consumer MAY supply an
   OPTIONAL per-backend parameter set, carried to the selected backend uninterpreted, and that a
   backend MUST document the keys it reads. Ensure the section states that a key the backend does not
   recognize is the backend's own disposition rather than an engine-judged shape. *Done when* the bag
   is described with its MUST-document clause and the engine's non-interpretation is explicit.

3. **The credential pair (Section 8.1)** — ensure the section states that the consumer supplies a
   **git credential** and a **forge credential**, and that the forge credential defaults to the git
   credential where unset. Ensure the section states that credentials reach the plugins for the
   duration of an invocation (Section 1.3) rather than being retained. *Done when* the pair and its
   `Default:` are stated in the same place as the parameters they are used with.

4. **`forge_access_missing` (Section 8.6)** — ensure the precondition table carries a row for a
   configured forge with no forge-API-access parameter supplied, and a row for an operation that
   touches a remote with no git-access parameter supplied, each refused before the policy runs with
   the `usage_or_config` status. Ensure the prose places them with the other preconditions judged
   from the invocation's arguments, and states that a parameter the backend cannot use is that
   backend's first-use `failed` rather than a precondition, because the engine judges no shape.
   *Done when* the rows exist and the boundary against a first-use failure is stated.

5. **Forge Backend Plugin (Section 9.2)** — ensure the paragraph that states every capability acts
   against the consumer-supplied coordinate also states that every capability acts against the
   consumer-supplied forge-API-access parameter under the forge credential, supplied by the engine to
   the backend. *Done when* the sentence names coordinate, parameter and credential together and
   parallels Section 9.1's `remote` sentence.

6. **VCS Backend Plugin (Section 9.1)** — ensure the three network-touching capabilities are stated
   to act against the git-access parameter under the git credential, and that every other capability
   of the section takes neither, because it is local to the checkout. *Done when* the parameter and
   credential are bound to exactly the three capabilities decision 0062 enumerated.

7. **Security and Trust Model (Section 11)** — ensure the sentence "the service the credential is
   presented to travels with the credential" is replaced by a statement over the parameters this
   decision adds: each credential is supplied with the access parameter it is used against, both from
   the consumer, so the credential and the endpoint it reaches are one decision made by one party.
   Ensure the section states the defaulting rule's bounded failure: a forge credential defaulted from
   the git credential is presented to the consumer's own configured endpoint, so a mismatch is an
   authentication refusal rather than a credential reaching an unchosen host. *Done when* Section 11
   states the pairing over named parameters and no longer relies on ambient context for the service.

## Cross-cutting sync

- **Test matrix (Section 13.1)**, under "Invocation contract" / "Plugins" — an invocation against a
  configured forge with no forge-API-access parameter yields `usage_or_config` and runs no operation;
  two engines given the same policy, coordinate and parameters reach the same instance; a forge
  credential left unset is presented as the git credential; an extension-bag key no backend declares
  reaches the backend and is that backend's disposition.
- **Implementation checklist (Section 13.2)** — extend the invocation-contract line with the
  parameter pair, the bag and the credential pair; extend the plugin line with the engine supplying
  each parameter to the plugin that uses it.
- **Conformance Statement (Section 13.3)** — add a row for the extension-bag keys a backend reads,
  which are `Implementation-defined` per backend. The core parameters need no row: they are named and
  REQUIRED, and their *encoding* is covered by the existing entry-point argument-encodings row.
- **`conformance/vcsx/vocabulary.json`** — add the new precondition reason(s) to
  `precondition_reasons` with their meanings.
- **`conformance/vcsx/vectors/`** — no vector: the conditions need a configured forge and an
  invocation, which is outside the deterministic, host-independent subset the corpus carries
  (Section 13.1).

## Anchor changes

- Section 11's phrase **"the service the credential is presented to travels with the credential"** is
  removed, superseded by the named access parameters. A plan or report locating text by it should
  locate Section 11's credential bullet instead.

## Status

Applied to `VCSX-SPEC.md` (Sections 8.1, 8.6, 9.1, 9.2, 11, 13.1, 13.2, 13.3) and
`conformance/vcsx/vocabulary.json`. The `SPEC.md` operator keys carrying these values landed with
decision 0092, as this plan's Scope states.
