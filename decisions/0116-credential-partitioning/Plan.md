# Plan — 0116 One credential is a scope decision nobody made

## Scope

`SPEC.md`: Section 15.3 "Secret Handling" (the scope and its default), Section 8.7 "Multiple
Repositories and Shared Polling" (the contention argument), Section 6.4 (cheat sheet), Section 13.1
(the recorded scope), Sections 17, 18.2, 19.

## Steps

1. **`Secret Handling` — the scope is named.** Ensure the section states that the outward credentials
   have a **scope**, that an operator MAY configure them per repository, and that where none is
   configured for a repository the orchestrator-level credential applies. Done-condition: a reader
   can tell what scope a credential has without inferring it from the schema's shape.

2. **`Secret Handling` — the implementation obligation.** Ensure an implementation MUST support
   per-repository configuration even though an operator need not use it, and that a deployment
   serving repositories with different owners SHOULD partition. Done-condition: a multi-tenant
   operator's `SHOULD` is satisfiable on every conforming implementation.

3. **`Secret Handling` — what is not required.** Ensure the text states that per-agent or
   per-session credentials are **not** required, and why: the forge meters a credential, the observed
   unit of contention is the repository, and minting one per run would require an
   issuance/rotation/revocation lifecycle this specification does not define. Done-condition: the
   declined half of the filed item is explicit rather than silently omitted.

4. **`Secret Handling` — the two failures.** Ensure the text distinguishes budget contention from
   blast radius, and states that the secret-isolation invariant (Sections 9.6, 15.3) is orthogonal:
   it governs where a credential goes, not how much one is worth. Done-condition: a reader does not
   read this as a weakening or a restatement of that invariant.

5. **`Multiple Repositories and Shared Polling` — the contention.** Ensure Section 8.7 notes that a
   forge meters a credential rather than a repository, so repositories sharing one credential are
   one spender to the code host and a guard that pauses on a low bucket pauses every repository
   including those spending nothing (Section 8.11). Done-condition: the reason partitioning is the
   only separation is stated where multi-repository routing is.

6. **Configuration and the record.** Ensure Section 6.4 carries the per-repository credential keys,
   and Section 13.1's log context can attribute a call to the credential scope in effect.
   Done-condition: an operator can tell from the record which credential a call was made under.

7. **Sections 17, 18.2, 19.** Ensure the test matrix checks that a per-repository credential is used
   for that repository's calls and the orchestrator-level one where none is configured; that Section
   18.2 lists the partitioning as an extension whose *support* is REQUIRED; and that Section 19
   records whether a deployment partitions. Done-condition: steps 1, 2 and 6 each have a check.

## Cross-cutting sync

Section 6.4 (step 6), Sections 17 and 18.2 (step 7), Section 19 (step 7).

## Anchor changes

New anchors: the per-repository credential configuration keys and the credential-scope log field. No
anchor is renamed or removed; `vcs.git_credential` and `vcs.forge_credential` keep their meaning as
the orchestrator-level default.

## Status

Applied to `SPEC.md` (Sections 6.4, 8.7, 13.1, 15.3, 18.1, 19) and `conformance/vocabulary.json`.
