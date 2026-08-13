# Plan — 0085 The forge repository coordinate is the consumer's, named in Section 8.1

## Scope

`VCSX-SPEC.md`: Sections 3.3 "Checkout Modes", 6.2 `[engine]`, 7.3 "The Embedded-Driver Contract",
8.1 "Entry Points and Arguments", 8.6 "Invocation Preconditions", 9.2 "Forge Backend Plugin", 11
"Security and Trust Model", 13.1 "Test Matrix", 13.2 "Implementation Checklist".
`conformance/vcsx/vocabulary.json`.

No `VCSX-CONTRACT.md` change: the invocation contract and the plugin API are deferred to this
document (`VCSX-CONTRACT.md` Section 11), and no shared token is renamed. The coordinate is an
argument rather than a `repo.policy.toml` section, which is the only class of addition that would
reach the surface.

## Steps

1. **Common arguments (Section 8.1)** — ensure the common-argument list carries the **forge
   repository coordinate**: which repository on the code host the forge operations act against
   (Section 9.2), REQUIRED where a forge is configured (Section 6.2) and absent otherwise. Ensure
   the section states that the engine holds it opaque, as it holds the commit identity and the base
   ref opaque: it takes one, supplies it to the forge backend, and does not interpret it, so its
   shape is the backend's. *Done when* the coordinate appears in the common-argument list with its
   condition and the opacity sentence.

2. **Front-end defaulting (Section 8.1)** — ensure the section states that a front-end MAY derive
   the argument from the resolved remote and supply it, because Section 8.1 already makes encodings
   the front-end's business — so the requirement costs an interactive caller nothing, and the
   derivation stays on the credential-holding side of the boundary (Section 11). *Done when* the
   permission is stated and cites Section 11.

3. **`forge_coordinate_missing` (Section 8.6)** — ensure the precondition table carries a row for a
   configured forge with no coordinate supplied, mapped to `forge_coordinate_missing`, and that the
   prose places it with the other preconditions judged from the invocation's arguments. Ensure a
   coordinate the backend cannot use is stated to be that backend's first-use `failed` rather than a
   precondition, because the engine holds the coordinate opaque and judges no shape.
   *Done when* the row exists and the boundary against a first-use failure is stated.

4. **Security and Trust Model (Section 11)** — ensure the section states that the forge repository
   coordinate is supplied by the consumer with the credential it is used under, that the engine
   derives neither from the checkout, and that this is what keeps the credential and the repository
   it is presented to one decision made by one party. Ensure the service root is named as travelling
   with the credential rather than as an engine argument, on Section 11's existing "runs the engine
   where they are already held". *Done when* Section 11 carries the coordinate beside the credential
   and states the one-party rule.

5. **Forge Backend Plugin (Section 9.2)** — ensure the section states that every capability acts
   against the forge repository coordinate the consumer supplied (Section 8.1), which the engine
   supplies to the backend as it supplies the resolved remote to the version-control capabilities
   (Section 9.1) — so no capability signature takes a repository and none infers one.
   *Done when* the sentence exists and parallels Section 9.1's `remote` sentence.

6. **The Embedded-Driver Contract (Section 7.3)** — ensure the driver's list of what it supplies
   carries the forge repository coordinate beside the execution context and the credentials.
   *Done when* the bullet names it.

7. **Checkout Modes (Section 3.3)** — ensure the `jj` entry no longer uses the undefined term
   "remote slug": in a secondary workspace the backend resolves the remote (Section 6.2) and the
   work branch from jj rather than from a colocated git remote. Ensure the section states that the
   forge repository coordinate is not derived from the checkout in any mode (Sections 8.1, 11).
   *Done when* `grep -n "slug" VCSX-SPEC.md` matches only Section 6.3's example branch pattern.

8. **`[engine]` (Section 6.2)** — ensure the paragraph that assigns the selection and the credential
   also states that the coordinate is the consumer's, so the section that draws the
   repository/consumer line for the forge draws all of it.
   *Done when* Section 6.2's sentence names all three: selection, credential, coordinate.

## Cross-cutting sync

- **Test matrix (Section 13.1)**, under "Invocation contract" / "Plugins" — an invocation against a
  repository configuring a forge, with no coordinate supplied, yields `usage_or_config` with
  `forge_coordinate_missing` and runs no operation; the same invocation with a coordinate supplied
  runs; a front-end that defaults the coordinate from the resolved remote and one that is given it
  explicitly reach the same forge repository; no forge capability infers a repository from the
  checkout.
- **Implementation checklist (Section 13.2)** — extend the invocation-contract line with the
  coordinate, and the plugin line with the engine supplying it to the forge backend as it supplies
  the resolved remote to the VCS backend.
- **Conformance Statement (Section 13.3)** — no new row: the argument is REQUIRED and named rather
  than `Implementation-defined`. Its *encoding* is already covered by the entry-point argument
  encodings row (Section 8.1).
- **`conformance/vcsx/vocabulary.json`** — add `forge_coordinate_missing` to `precondition_reasons`.
- **`conformance/vcsx/vectors/`** — no vector: the condition needs a configured forge and an
  invocation, so it is outside the deterministic, host-independent subset the corpus carries
  (Section 13.1).

## Anchor changes

- Section 3.3's phrase **"remote slug" is removed**, superseded by the resolved remote (Section 6.2)
  and the work branch. Any plan or report locating text by it should locate the `jj` checkout-mode
  entry instead.

## Status

Applied to `VCSX-SPEC.md`.
