# Plan — 0062 The remote is named in `[engine]` and supplied to the capabilities that touch it

## Scope

`VCSX-SPEC.md`: Sections 3.2 "Execution Contexts (Trust)", 6.2 "`[engine]`", 9.1 "VCS Backend Plugin",
13.1 "Test Matrix", and 13.3 "Conformance Statement".
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` follows the new `Implementation-defined` value.

No new section and no renumbering: every edit lands in an existing subsection.

No `VCSX-CONTRACT.md` edit. Its Section 4 lists what `repo.policy.toml` holds at the altitude of
"engine selection" and defers "the field-level schema of `repo.policy.toml` and its sections" to
`VCSX-SPEC.md` (its Section 11), and it enumerates no `[engine]` key — not `vcs`, not `forge`, not
`version_floor`. Its Section 11 also defers "the plugin API for code-host backends", which is where the
capability signatures live. A new `[engine]` key and a changed capability signature are both on the
deferred side of that line.

No `SPEC.md` edit. Symphony supplies "the repository's remote" for *provisioning* (its Section 9.7),
which `VCSX-SPEC.md` Section 1.3 keeps outside the engine entirely; the engine's `remote` names a
remote the provisioned checkout already carries, so the two do not collide and Symphony's text stays
correct as written.

No vocabulary registry edit. `vocabulary.json` carries the tokens Section 14 requires spelled
identically in `VCSX-SPEC.md` and `VCSX-CONTRACT.md`; its `repo_policy_sections` group lists sections,
not keys, and no `[engine]` key appears there today.

No vector change. Whether a backend acts against the configured remote needs a repository and a
network, which `conformance/vcsx/README.md` already defers under "Plugin behavior".

## Steps

1. **Section 3.2's host-side list names `pull`.** Ensure the `Host-side` bullet's parenthetical reads
   `integrate, push, pull, create_pr, merge, host-side hooks`. Done when every operation Section 4.1
   defines as touching a remote appears in the list.
2. **`[engine]` carries `remote`.** Ensure Section 6.2 lists `remote` (string, OPTIONAL) after `forge`,
   described as the name of the remote the operations that touch one act against (`integrate`, `push`,
   `pull`), with a nested `Default:` bullet stating that unset means the backend's default remote for
   the checkout mode, which is `Implementation-defined` and MUST be documented (Section 13.3). Done
   when a repository can pin the push target from `repo.policy.toml` alone.
3. **The remote is repository-owned for the stated reason.** Ensure Section 6.2 records, after the
   existing backend-selection paragraph, that the remote is repository-owned on the same reasoning as
   the backend selection; that the engine resolves it once per invocation and supplies it to each
   capability that takes one (Section 9.1); and that a backend neither reads it from the policy itself
   nor infers it from the work branch's upstream binding, which need not exist because the work branch
   is engine-derived (Section 6.3) and MAY be absent from the checkout at the first push. Done when the
   two rejected derivations are refused in the text rather than only in this record.
4. **A remote the checkout does not carry has a stated disposition.** Ensure Section 6.2 states that the
   engine performs no repository provisioning (Section 1.3), so the named remote is one the provisioned
   checkout already carries, and that a name it does not carry is not a configuration error — Section
   6.10's validation reads the policy alone — but surfaces at first use as the operation's `failed`
   reason (Section 4.3). Done when an implementer does not have to choose between `usage_or_config` and
   an operation result for this case.
5. **Three capability signatures take the remote.** Ensure Section 9.1 reads `integrate(remote, base)`,
   `push(remote, work_branch)` and `pull(remote, work_branch)`, each keeping its existing qualifying
   clause. Done when a backend author reading Section 9.1 alone knows the remote is supplied rather
   than discovered.
6. **The host-side/local split is stated as one invariant.** Ensure Section 9.1 records, after the
   capability list, that `remote` is the resolved remote (Section 6.2) supplied by the engine, and that
   the capabilities taking one are exactly the version-control operations Section 3.2 places host-side.
   Done when the next capability added can be checked against Section 3.2 by reading Section 9.1.
7. **The test matrix covers the target.** Ensure Section 13.1's `Plugins` check states that the
   remote-touching operations act against the resolved remote (Section 6.2), a configured `remote`
   overriding the backend default. Done when the divergence the issue reports is a testable line.
8. **The Conformance Statement publishes the default.** Ensure Section 13.3's enumeration of
   `Implementation-defined` behaviors includes the backend's default remote where `[engine] remote` is
   unset (Section 6.2), placed in the section order the list already uses. Done when a consumer can
   read an engine's default remote without reading its source.
9. **The template has a row for it.** Ensure `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 3 lists
   the default remote in its `Implementation-defined` resolutions table, in section order. Done when an
   engine filling in the template records it without improvising a row.

## Cross-cutting sync

`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Step 9).

Section 6.10 needs no edit: no configuration reason is added, because the two failure modes a remote has
are either invisible to the loader (the name is absent from the checkout — Step 4) or absent entirely
(an unset key is the documented default, not an error).

Section 8.5 needs no edit: `[engine]` keys are not part of the enumerated major-stable surface, and
adding an OPTIONAL key with a defined default is compatible.

Section 11 needs no edit: its push bullet already pins the refspec and forbids a force push, and naming
the remote does not change either property. `SPEC.md`'s cross-cutting sections named in `CLAUDE.md` are
untouched; this decision changes `VCSX-SPEC.md`, whose counterparts are Sections 13.1 and 13.2, and
13.2's plugin bullet already covers the capability list at the altitude it uses.

## Anchor changes

Added: `remote` (an `[engine]` key).

Renamed: three Section 9.1 capability signatures —
`integrate(base)` → `integrate(remote, base)`,
`push(work_branch)` → `push(remote, work_branch)`,
`pull(work_branch)` → `pull(remote, work_branch)`.
The capability *names* are unchanged; only their parameter lists grow. `diff(base)`,
`ahead_behind(base)`, `derive_work_branch(pattern, identity)` and `commit(message, identity)` are
untouched.

## Out of scope

- **Separate read and write remotes** (a fork-and-upstream arrangement). Nothing in the current
  operation set needs it — `integrate` and `push` act on the one remote the work branch is published to
  — and it is the shape to reach for if the need appears, rather than a second override.
- **A per-invocation remote argument.** Recorded as Option E in `Background.md`: it would relocate the
  divergence the issue reports rather than close it.
- **Remote *URL* configuration.** The engine performs no provisioning (Section 1.3); a remote's URL is
  established before the engine sees the checkout.

## Status

Applied to `VCSX-SPEC.md` (Sections 3.2, 6.2, 9.1, 13.1, 13.3) and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.
