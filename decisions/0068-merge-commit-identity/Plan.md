# Plan — 0068 Every commit the engine writes carries the caller-supplied commit identity

## Scope

`VCSX-SPEC.md`: Sections 8.1 "Entry Points and Arguments", 8.6 "Invocation Preconditions", 9.1 "VCS
Backend Plugin", 10.1 "Commit", 13.1 "Test Matrix", and 13.2 "Implementation Checklist".
`conformance/vcsx/vocabulary.json` follows the widened precondition condition.

No new section and no renumbering: every edit lands in an existing subsection.

One `VCSX-CONTRACT.md` edit, in Section 9 "Message Formulation". No shared *name* changes, so this
is not a contract change under `VCSX-SPEC.md` Section 14: the capability signatures are on the
deferred side of its Section 11 ("the plugin API for code-host backends"), and no operation,
position, class, reason or `need` token is added or respelled. The edit is needed anyway because the
surface carries the sentence "A mechanical merge commit uses the engine default", which with the
word *message* absent is the one place a reader could infer an engine-chosen identity — the reading
this decision refuses.

Two `SPEC.md` edits, in Sections 9.8 "Git Automation and Work Branch" and 17.2 "Workspace Manager
and Safety". Symphony performs a back-merge at the start of every run and configures `vcs.author`,
so under this decision the merge commit that back-merge writes carries it; saying so is one clause
on an existing bullet. The failure mode is not hypothetical for Symphony, which runs host-side in a
container.

No `SPEC.md` Section 6.4 edit: `vcs.author` already appears in the cheat sheet as "identity mapping
for commits and the push/PR actor", and no configuration key is added or changed. No `SPEC.md`
Section 18 edit: its conformance checklist already requires "a `scope.branch_pattern`-derived work
branch and configurable authorship", which is this requirement at that altitude.

No `VCSX-SPEC.md` Section 13.3 edit and no `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` edit: nothing
becomes `Implementation-defined`. The attribution is fixed by this decision rather than published by
each engine, which is the difference between this answer and the one rejected as Option C.

No `VCSX-SPEC.md` Section 4.1 edit: it defines what `integrate` and `pull` do to the branch, and
Section 10.1 owns attribution for every commit the engine writes; stating it twice would leave two
places to keep in step.

No `VCSX-SPEC.md` Section 6.8 edit: the `[messages]` block already records that identity is supplied
by the consumer and distinct from content, which stays true.

No `VCSX-SPEC.md` Section 12.2 edit: the reference algorithm already elides the identity at
`run_op("commit", message)`, so threading it into `integrate` and not into `commit` would present
the elision as significant.

No vector change. `conformance/vcsx/README.md` already defers plugin behavior, and who a backend
writes into a merge commit needs a repository and a backend to observe.

## Steps

1. **The invocation contract names both identities.** Ensure Section 8.1's "Common arguments"
   sentence lists the identity the work branch is derived from (Section 6.3) and the commit identity
   commits are attributed to (Section 10.1) as two arguments rather than one, keeping the message
   input for `commit`/`create_pr` and the execution context. Done when a reader of the invocation
   contract alone cannot mistake the work-branch derivation input for the author.
2. **`integrate` and `pull` take the commit identity.** Ensure Section 9.1 reads
   `integrate(remote, base, identity)` and `pull(remote, work_branch, identity)`, each keeping its
   existing qualifying clause, and that `commit(message, identity)` is unchanged. Done when a
   backend author reading Section 9.1 alone knows the identity of a merge commit is supplied rather
   than discovered.
3. **The commit-identity invariant is stated once.** Ensure Section 9.1 records, beside the
   paragraph that does the same for `remote`, that `identity` is the commit identity (Sections 8.1,
   10.1) supplied by the engine, and that the capabilities taking one are exactly those that can
   write a commit. Done when the next capability added can be checked against this rule by reading
   Section 9.1.
4. **A mechanical merge commit carries that identity.** Ensure Section 10.1's mechanical-merge
   sentence covers a commit written by `integrate` or by `pull` (Section 4.1), states that it uses
   the backend's default message and carries the same identity the engine supplies to `commit`, and
   cites Section 9.1 for the supply. Done when the sentence that already answers the message
   question answers the attribution question beside it.
5. **A backend does not attribute from its environment.** Ensure Section 10.1 states that a backend
   MUST NOT attribute a commit to an identity it derives from its execution environment, and that
   attribution is therefore a property of the invocation rather than of the host — the same policy
   over the same checkout writes the same author on any machine. Done when the divergence the issue
   reports is refused in the text rather than only in this record.
6. **A forge merge is attributed by the code host.** Ensure Section 10.1 carries a `Note:` recording
   that a merge the forge performs (Section 9.2), including the commit a squash strategy writes
   (Section 10.3), is attributed by the code host to the account the consumer's credential names,
   and that the engine supplies no identity for it. Done when `land` taking no identity reads as a
   boundary rather than as the same omission one document over.
7. **The precondition covers every entry that can write a commit.** Ensure Section 8.6's
   precondition sentence reads that for an entry that can write a commit — `commit`, `integrate`,
   `pull`, and a front-end sequence that dispatches one — the engine accepts the caller-supplied
   commit identity (Section 10.1), keeping the existing clause that only the backend can judge its
   shape because the engine holds identity opaque. Done when a caller invoking `integrate` alone
   learns from Section 8.6 that the identity is required.
8. **`identity_invalid` covers an absent identity.** Ensure Section 8.6's registry row for
   `identity_invalid` reads that the caller-supplied commit identity is absent where the entry
   requires one, or malformed as the VCS backend judges it (Section 10.1). Ensure the registry still
   holds three rows, and that Section 13.1's `Invocation contract` check names the same widened
   condition where it lists the three precondition failures. Done when the argument this decision
   makes required has a stated outcome when it is not supplied, without a fourth token.
9. **The vocabulary registry follows.** Ensure `conformance/vcsx/vocabulary.json`'s
   `precondition_reasons` entry for `identity_invalid` states the same widened condition as
   Section 8.6. Done when the registry and the section say the same thing about the same token.
10. **The test matrix covers attribution.** Ensure Section 13.1's `Message formulation` check states
    that every commit the engine writes carries the supplied commit identity, the mechanical merge
    commit an `integrate` or a `pull` writes included, on a host whose environment supplies no
    usable identity of its own. Done when the case CI caught is a testable line.
11. **The checklist names attribution.** Ensure Section 13.2's message-formulation bullet names
    commit attribution from the supplied identity alongside the seams it already lists. Done when
    the definition of done includes writing an attributed merge commit.
12. **The contract's merge-commit sentence is unambiguous.** Ensure `VCSX-CONTRACT.md` Section 9's
    commit bullet states that a mechanical merge commit uses the engine's default *message* and
    carries the same configured identity. Done when the surface an embedding consumer reads cannot
    be read as licensing an engine-chosen author.
13. **Symphony's `vcs.author` covers its back-merge commit.** Ensure `SPEC.md` Section 9.8's
    `Identity:` bullet states that `vcs.author` attributes every commit Symphony's automation
    writes, the mechanical merge commit of a back-merge included, so attribution does not vary with
    the host the service runs on. Done when the one commit in a run that Section 9.8 did not account
    for is accounted for.
14. **Symphony's test matrix covers it.** Ensure `SPEC.md` Section 17.2's back-merge check states
    that the merge commit a back-merge writes carries `vcs.author` rather than a host-derived
    identity, in the row's existing `(VCS Engine)` shape. Done when the consumer-side statement of
    the same failure is testable too.

## Cross-cutting sync

`conformance/vcsx/vocabulary.json` (Step 9), `VCSX-CONTRACT.md` (Step 12), `SPEC.md` (Steps 13, 14).

`VCSX-SPEC.md`'s counterparts of the cross-cutting sections `CLAUDE.md` names are Sections 13.1 and
13.2, handled in Steps 10 and 11; Section 13.3 needs no edit because no `Implementation-defined`
behavior is added.

`SPEC.md`'s cheat sheet (Section 6.4) and checklist (Section 18) need no edit for the reasons
recorded in `Scope`; its test matrix (Section 17) is Step 14.

Section 8.5 needs no edit: no reason token, `need` token, status or exit code is added, and a
widened condition on an existing precondition reason does not change the token's meaning for a
consumer branching on it.

Section 11 needs no edit: the identity is not a credential, and the engine holding it for an
invocation is what Sections 8.1 and 8.6 already describe.

## Anchor changes

Renamed: two Section 9.1 capability signatures —
`integrate(remote, base)` → `integrate(remote, base, identity)`,
`pull(remote, work_branch)` → `pull(remote, work_branch, identity)`.
The capability *names* are unchanged; only their parameter lists grow, as in decision 0062.
`commit(message, identity)`, `derive_work_branch(pattern, identity)`, `diff(base)` and
`ahead_behind(base)` are untouched.

No token added or removed. `identity_invalid` keeps its spelling and its class-free status; only the
condition it names widens.

## Out of scope

- **Renaming `derive_work_branch(pattern, identity)`'s second parameter** so the token `identity`
  names one value throughout. The two uses are distinguished where the arguments are listed (Step
  1), which is what this decision needs; a rename is an anchor change on a capability this issue
  does not touch and should be argued on its own, against how a consumer supplies the work-item
  identity.
- **The mechanical merge commit's *message*.** Section 10.1 assigns it to the backend's default and
  this decision leaves it there. Making it configurable, or `Implementation-defined` with a
  Statement row, is a message-formulation question and no divergence in it has been reported.
- **An author distinct from the committer.** The engine holds identity opaque (Section 8.6), so the
  distinction lives inside the value and needs no signature change.
- **A backend lifecycle with an explicit open step.** Recorded in `Background.md` as the
  reconsideration trigger; a backend that cannot be constructed without an identity would need one,
  and the identity would travel with it.
- **A repository-owned author key in `repo.policy.toml`.** Rejected as Option E: it would source
  attribution from the repository and authorization from the consumer.

## Status

Applied to `VCSX-SPEC.md` (Sections 8.1, 8.6, 9.1, 10.1, 13.1, 13.2),
`conformance/vcsx/vocabulary.json`, `VCSX-CONTRACT.md` (Section 9), and `SPEC.md` (Sections 9.8,
17.2).
