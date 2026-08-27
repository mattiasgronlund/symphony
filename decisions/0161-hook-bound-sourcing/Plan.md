# Plan — 0161 Who sets the bound on a workspace hook

## Scope

`SPEC.md`, by section title: Section 5 (Configuration Contracts) — the `WORKFLOW.md` bullet and the
dividing rules; Section 5.3.4 (`hooks.workspace`); Section 5.6 (`repo.policy.toml`); Section 6.4
(the config cheat sheet); Section 9.4 (Workspace Hooks); Section 14.5 (Operator Intervention
Points); Section 15.4 (Configuration Trust Sourcing and Hook Safety); Sections 17.1 and 17.2 (test
matrix); Section 18.1.2 (Broker Core Conformance checklist).

`conformance/vocabulary.json` (the `config_namespaces` entry whose `token` is `hooks`) and
`conformance/README.md`.

No new section, no removed section, no renamed token. The change is one key's artifact assignment
and the sentences that assignment makes true or false.

## Steps

1. **`SPEC.md`, `hooks.workspace.timeout_ms` in Section 5.3.4.** Ensure the field bullet states, in
   the field documentation pattern the section already uses: `Default: 60000`; that the key is
   declared in `repo.policy.toml` and read from the policy source with that artifact's other
   host-side parts (Section 15.4); that a `timeout_ms` in `WORKFLOW.md` front matter MUST NOT be
   honored; that the value bounds both halves of every lifecycle point (Section 9.4); that invalid
   values fail configuration validation; and that a change takes effect for work started after it,
   through the per-unit-of-work read (Section 6.2). Done when the bullet names both artifacts — one
   as its source and one as the artifact whose value is not honored — and no sentence under it
   implies a watch or a reload of the value.

2. **`SPEC.md`, the two-trust-levels paragraph in Section 5.3.4** (locate by "Hooks exist at two
   trust levels"). Ensure it says what the artifact split assigns: the four lifecycle script bodies,
   each running where its artifact places it. Ensure it says that `timeout_ms` is not one of them —
   it is Symphony's wait rather than a body that runs — and points at the bullet in step 1 for its
   source. Done when a loader reading only this paragraph knows which keys of the namespace the
   split governs and which it does not.

3. **`SPEC.md`, the `WORKFLOW.md` bullet in Section 5** (locate by "MUST NOT carry credentials,
   authorization scope"). Ensure the prohibition also covers a setting that governs Symphony's own
   behavior outside the sandbox, and names the hook bound as the instance (Sections 5.3.4, 15.4).
   Done when the clause enumerates that kind alongside the three it already names.

4. **`SPEC.md`, the dividing rules in Section 5** (locate by "If a setting is consumed *inside the
   sandbox*"). Ensure the rule notes that the bound on a workspace hook is not such a setting, so no
   reading of the three rules routes `hooks.workspace.timeout_ms` to `WORKFLOW.md`. Done when the
   rules assign the key to `repo.policy.toml` on their own terms rather than by elimination in a
   reader's head.

5. **`SPEC.md`, `repo.policy.toml`'s section list in Section 5.6** (locate by "Sections:"). Ensure
   the list names `hooks.workspace` — the host-side halves of the workspace lifecycle hooks and the
   `timeout_ms` that bounds both halves (Section 5.3.4) — and states that the namespace is
   Symphony's rather than the engine's, whose named units are `hooks.engine.<name>`
   (`VCSX-CONTRACT.md`). Done when every `hooks.workspace` key this specification assigns to the
   artifact is accounted for by Section 5.6's own list.

6. **`SPEC.md`, the timeout bullet in Section 9.4 "Execution contract"** (locate by "Hook timeout
   uses"). Section 9.4's "The bound applies to each half, not to the pair" is kept as it stands.
   Ensure the bullet also names the source — `hooks.workspace.timeout_ms` from `repo.policy.toml`,
   read from the policy source (Sections 5.3.4, 15.4) — and states why one artifact's value governs
   both halves: the executor runs both trust levels and waits on both from outside the sandbox
   (Section 3.1). Done when the bullet says whose value the bound is without a reader leaving
   Section 9.4.

7. **`SPEC.md`, the in-sandbox sourcing bullet in Section 15.4** (locate by "An agent edit there is
   harmless"). Ensure the harmlessness claim is stated over the parts it holds for — the prompt
   body, the in-sandbox hook bodies, and the `hooks.engine` units the gate runs, all of which run in
   the sandbox — rather than over the artifact as a whole, and that the bullet's enumeration of the
   worktree-sourced parts names the in-sandbox hook *bodies* rather than the `hooks.workspace`
   namespace entire. Done when the sentence no longer asserts anything about a value the host acts
   on, and no enumeration in Section 15.4 places `hooks.workspace.timeout_ms` in the worktree.

8. **`SPEC.md`, a hook-implications bullet in Section 15.4** (locate by "Hook timeouts are REQUIRED
   to avoid hanging the orchestrator"). Ensure a bullet states the bound rule with its reasoning:
   the bound is read from the policy source for both halves and is not a `WORKFLOW.md` key; a bound
   declared in the worktree would be one the bounded thing sets; the executor waits on the
   in-sandbox half from the host as it does on the host-side one, so the wait is the host's at both
   trust levels; and a one-millisecond bound would time out a host-side `after_run` or
   `before_remove` half whose failure Section 9.4 logs and ignores, so a trusted control would not
   run and nothing would fail. Ensure it records that the engine refuses the equivalent repository
   key outright (`VCSX-SPEC.md`), and that Symphony keeps the key because it reads each artifact
   from exactly one revision — the fact the engine states it does not have. Done when the bullet is
   self-contained enough that an implementer who reads only Section 15.4 refuses the worktree value
   for the stated reason.

9. **`SPEC.md`, the cheat sheet in Section 6.4.** Its group heading is located by "Workspace hooks
   (repository-owned". Ensure that heading no longer implies that every key under it follows the
   per-half artifact split, and that the `hooks.workspace.timeout_ms` row reads `integer, default
   60000`, declared in `repo.policy.toml` and read from the policy source, with a value in
   `WORKFLOW.md` not honored (Sections 5.3.4, 15.4). Done when `python3
   scripts/validate_spec_consistency.py` reports `0 error(s), 0 warning(s)` and the row names its
   artifact.

10. **`SPEC.md`, Section 14.5 (Operator Intervention Points).** The list names editing `WORKFLOW.md`
    and editing the operator policy config, and names no third artifact — so an operator looking for
    where the hook bound is now changed finds neither it nor the artifact holding it. Ensure the
    list also names editing a repository's `repo.policy.toml` (its Way of Working, including the
    host-side hook halves and the bound on every half), with the same disposition the `WORKFLOW.md`
    bullet carries: repository-owned, not watched, in effect for work started after the change
    reaches the policy source (Sections 5.6, 6.2, 15.4). Done when each of the three configuration
    artifacts appears in the list with the way its changes take effect.

11. **`SPEC.md`, Section 17.1.** Ensure a check states that a `hooks.workspace.timeout_ms` in
    `WORKFLOW.md` front matter does not change the bound in force: the value read from the policy
    source governs, and the workflow file's is not honored (Sections 5.3.4, 15.4). Done when the row
    exists and is phrased as an observable check in the section's voice.

12. **`SPEC.md`, Section 17.2.** Ensure a check exercises the behavior rather than the parse: with a
    one-millisecond `hooks.workspace.timeout_ms` in the workspace's `WORKFLOW.md`, both halves of a
    lifecycle point still run under the policy source's bound, so a host-side `after_run` half runs
    to completion rather than being timed out into a failure Section 9.4 discards. Done when the row
    exists and names the ignored-failure semantics it protects.

13. **`SPEC.md`, Section 18.1.2.** Ensure the "Hook timeout config" bullet names the source and the
    artifact whose value is not honored (`hooks.workspace.timeout_ms`, default `60000`, read from
    the policy source, not honored from `WORKFLOW.md`; Sections 5.3.4, 15.4). Done when the
    checklist bullet can be implemented without opening Section 5.3.4.

14. **`conformance/vocabulary.json`.** Ensure the `config_namespaces` entry whose `token` is `hooks`
    carries a `note` that also states the bound's assignment: in-sandbox hooks in `WORKFLOW.md`,
    host-side hooks in `repo.policy.toml`, and `hooks.workspace.timeout_ms` in `repo.policy.toml`
    only, bounding both halves (Sections 5.3.4, 15.4). Done when the note distinguishes the bodies
    from the bound and `python3 scripts/validate_spec_consistency.py` still passes.

15. **`conformance/README.md`.** Ensure a finding entry records the resolution in the file's own
    voice: the key was documented once for two artifacts at two trust levels, the worktree-sourced
    one could name the host's wait on a policy-branch-trusted half, and the corpus could not have
    caught it because `vectors/config-defaults.json` asserts the default through a flat view that
    abstracts over artifact ownership. Done when the entry names what was checking (nothing) and
    what checks now (Section 5.3.4's assignment plus the vocabulary note).

## Sites checked, no change needed

Recorded so a later reader does not re-derive them. Checked against `1e33468`.

- Section 6.1's pipeline step 2 already names each artifact's source — host-side sections of
  `repo.policy.toml` from the policy branch, its in-sandbox gate from the worktree — so the bound
  arriving with the host-side sections needs no new step there.
- Section 6.2's sentence about what is in force for a run already carries the bound, the bound being
  part of the policy. It is the surviving producer for the runtime-change sentence step 1 restates.
- Section 16.6's `run_hook` and `run_sandbox_hook` call sites take no bound parameter, so the
  reference algorithm is unaffected by which artifact supplies one.
- Section 5.5's error classes are unaffected: a key that is not honored is not a load or render
  failure, and Section 5.3's rule on unknown keys is the disposition. Section 6.3 is unaffected for
  the reason decision 0160 gave — dispatch preflight does not read `WORKFLOW.md`.
- Section 5.2's design note says the file should carry only what the agent needs inside the sandbox,
  which is the criterion this decision applies rather than a claim it contradicts; it produces the
  outcome and is left as written. Section 3.2's component sentence says the front matter supplies
  the in-sandbox hook halves, which stays true of the halves' bodies. Section 5.1's loader bullet
  names what is in force for a run and does not name the bound.
- `SPEC.md:230` (Section 3.4) and `SPEC.md:2362` (Section 9.7) use "Repository Way of Working" as
  the concept rather than as Section 5.6's title; the concept is unchanged.
- Neither engine document changes. `VCSX-SPEC.md:3632` carries "the bound applies to" about
  `network_bound_ms`, an unrelated bound; `VCSX-SPEC.md:996` carries the engine's own unknown-key
  rule, which is its disposition for the `[hooks] timeout_ms` it refuses; `VCSX-SPEC.md:2624` and
  `VCSX-CONTRACT.md:117` describe the engine's trusted revision. The engine's hook bound is already
  the consumer's and neither document carries a key for it.

## Cross-cutting sync

- Section 6.4 cheat sheet: step 9.
- Section 17 test matrix: steps 11 and 12.
- Section 18 checklist: step 13.
- Conformance Statement templates: **no row is owed**. The decision creates no
  `Implementation-defined` choice and no MUST-document obligation — it removes one degree of
  freedom rather than adding one — so neither `CONFORMANCE-STATEMENT-TEMPLATE.md` nor
  `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` changes.

## Anchor changes

None. `hooks.workspace.timeout_ms` keeps its spelling and its default; what narrows is the set of
artifacts that may declare it. No section is renamed, added, or removed.

## Status

Applied to `SPEC.md` (Sections 5, 5.3.4, 5.6, 6.4, 9.4, 14.5, 15.4, 17.1, 17.2, 18.1.2),
`conformance/vocabulary.json` and `conformance/README.md` on branch
`apply-0161-hook-bound-sourcing`.
