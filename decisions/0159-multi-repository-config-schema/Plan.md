# Plan — 0159 The multi-repository configuration schema

## Scope

`SPEC.md`:

- Section 4.1.8 Orchestrator Runtime State — the `repository` member's value space and read-back.
- Section 4.2 Stable Identifiers and Normalization Rules — `Repository Key`.
- Section 5.3 Configuration Schema — the top-level key list, a new `repository` subsection, and the
  level annotations on `tracker` and `agent`.
- Section 5.6 `repo.policy.toml` (Repository Way of Working) — the pointer's key and default.
- Section 6.1 Configuration Resolution Pipeline — the pointer step and where inheritance is applied.
- Section 6.3 Dispatch Preflight Validation — the checks the enumeration adds.
- Section 6.4 Core Config Fields Summary (Cheat Sheet) — the repository-level rows.
- Section 8.1 Poll Loop — the tick's tracker step.
- Section 8.7 Multiple Repositories and Shared Polling — configuration, where rules live, keying.
- Section 9.1 Workspace Layout — one path form.
- Section 9.5 Safety Invariants — the repository path component.
- Section 9.7 Repository Provisioning and the VCS Engine — where the `vcs` object lives.
- Section 10.9 Agent Adapters and Selection — where selection is written.
- Section 15.3 Secret Handling — the per-repository credential's address.
- Section 16.4 Dispatch One Issue — `repo_of(issue)`.
- Sections 17.1, 17.2, 17.4, 18.1 — the cross-cutting rows.

`conformance/`:

- `conformance/vocabulary.json` — `config_namespaces` gains `repository`.
- `conformance/vectors/config-defaults.json` — which level its flat view is of.
- `conformance/vectors/issue-routing.json` — the note asserting the schema does not exist.
- `conformance/vectors/repository-inheritance.json` — new: the leaf-by-leaf fallback.
- `conformance/README.md` — the stale `vcs` finding, and this decision's finding.

`SPEC.md` Section 3.4 Layers, the VCS Engine, and Deployment Topologies is **cited, not edited**:
step 2's floor of one entry is what keeps the `interactive-agent` topology able to name the
repository its workspace path now always carries, and it is stated in Section 5.3 where the
enumeration is defined rather than in the topology list.

`CONFORMANCE-STATEMENT-TEMPLATE.md` — **no row is owed**, and it is named here so a reader checking
finds the answer rather than the absence (decision 0128). This decision fixes every value it
introduces and creates no `Implementation-defined` choice and no MUST-document obligation. The
encoding of the operator policy config is unchanged and stays covered by the template's existing
Section 4.1 row "Operator policy config format and discovery path", which cites `SPEC.md` Section 5.

## Steps

1. `SPEC.md` Section 5.3 Configuration Schema, the top-level key list: ensure `repository` is one of
   the operator-config keys. Post-condition: the list names `tracker`, `polling`, `workspace`,
   `vcs`, `agent`, `codex` and `repository`, the last annotated as the managed-repository
   enumeration.
   Done when the list has seven entries and the annotation on `vcs` — "per managed repository" —
   names the key that makes it one.

2. `SPEC.md` Section 5.3, a new final subsection: ensure the enumeration is documented in Section
   5.3's own field pattern, titled `` `repository` (map of objects) `` and numbered after `codex` so
   Sections 5.3.1–5.3.6 keep their numbers. Post-condition: each entry is keyed by the repository's
   name, which is Section 4.2's `Repository Key`, and carries
   - `policy` (path string, OPTIONAL) — the pointer to that repository's `repo.policy.toml`,
     resolved relative to the repository (Section 5.6). Default: `repo.policy.toml`;
   - `vcs` (object) — that repository's `vcs` block, fields documented in Section 9.7;
   - `agent` (object, OPTIONAL) — that repository's agent selection: `default_agent`,
     `default_effort` and `agent_by_label` (Section 10.9), and no other `agent` field;
   - `routing` (list of rules, OPTIONAL) — that repository's share of the issue→repository mapping
     (Section 8.7), each rule a conjunction of conditions over the normalized record's `project`,
     `team`, `labels`, `assignees` and `state`, a list-valued field read as membership and a scalar
     field as equality. Default: unset, which matches every issue;
   and the inheritance rule stated once: a key an entry does not carry takes the orchestrator-level
   value for the same key, resolved leaf by leaf rather than block by block, so an entry overriding
   `agent.default_effort` keeps the orchestrator-level `agent.default_agent`. Ensure the subsection
   also states the enumeration's floor: a deployment that manages a repository configures at least
   one entry, and an entry MAY carry nothing but its key, everything else inheriting — so the
   single-repository configuration is today's flat one plus the line that names the repository, and
   the `interactive-agent` topology (Section 3.4), which runs no dispatch preflight, still has the
   `Repository Key` the workspace path of step 13 always carries. Done when every OPTIONAL field
   carries a `Default:`, no other section states an inheritance rule of its own, and a deployment
   with one repository can be configured without writing a key twice.

3. `SPEC.md` Section 5.3.1 `tracker`: ensure the key's level is stated. Post-condition: one instance
   configures one tracker, and repositories drawing from it share it (Section 8.7). Done when
   Section 5.3.1 says so and steps 8 and 9 leave no section describing a second one.

4. `SPEC.md` Section 5.3.5 `agent`: ensure each field carries its level. Post-condition:
   `default_agent`, `default_effort` and `agent_by_label` are selection a `repository` entry MAY
   override; `max_concurrent_agents`, `max_concurrent_agents_by_state`, `max_turns` and
   `max_retry_backoff_ms` are orchestrator-level only, because Section 8.3 computes the concurrency
   limits over the instance's `running` map and Section 8.4's backoff is per issue. Done when all
   seven fields are marked and a per-repository concurrency limit is unwritable rather than ignored.

5. `SPEC.md` Section 4.2 Stable Identifiers and Normalization Rules: ensure `Repository Key` is
   defined beside `Workspace Key`. Post-condition: it is the name a `repository` entry is keyed by;
   permitted characters are `[A-Za-z0-9._-]`; a name outside that set fails configuration validation
   rather than being sanitized, so one value appears in the configuration, in the workspace path
   (Section 9.1) and in a running entry's `repository` (Section 4.1.8). Done when the identifier is
   defined once and Sections 9.1 and 4.1.8 cite it rather than restating it.

6. `SPEC.md` Section 4.1.8 Orchestrator Runtime State, the `running` bullet: ensure the entry's
   `repository` member has a stated value space. Post-condition: it holds a `Repository Key`, and
   the read-back from the workspace path after a restart is exact because the key is constrained
   rather than sanitized. Done when the bullet no longer needs the single-repository case to
   describe how the member recovers.

7. `SPEC.md` Section 5.6 and `SPEC.md` Section 6.1 Configuration Resolution Pipeline: ensure the
   pointer has a key and inheritance has a place in the pipeline. Post-condition: Section 5.6 names
   `repository.<name>.policy` as the pointer with its default; Section 6.1 step 1 resolves it by
   that name; and Section 6.1 resolves each `repository` entry against the orchestrator level
   **before** built-in defaults are applied, since a default filled into an entry first would shadow
   the orchestrator-level value the entry meant to inherit and would read as a choice the entry
   made. The resolved value is coerced and validated exactly as a written one. Done when no section
   names the pointer without a key, and when the pipeline's five steps still read as five steps.

8. `SPEC.md` Section 8.1 Poll Loop, the tick sequence: ensure step 3 describes one fetch per cycle
   from the configured tracker, with the returned issues routed to repositories (Section 8.7). Done
   when the step no longer implies a collection Section 5.3.1 cannot hold.

9. `SPEC.md` Section 8.7 Multiple Repositories and Shared Polling, the *Configuration* bullet:
   ensure it names the key. Post-condition: `repository` enumerates the managed repositories, each
   entry carrying its `vcs` (Section 9.7), its agent selection (Section 10.9), its
   `repo.policy.toml` pointer and its `routing` rules; and Section 8.7's clause
   "and the trackers they draw work from" is gone, the instance having one tracker. Ensure the
   *Shared polling* bullet is unchanged in substance: several repositories drawing from the one
   configured tracker are polled once per cycle rather than once per repository. Done when the
   section's own claim is one the schema can express.

10. `SPEC.md` Section 8.7, the *Issue-to-repository routing* bullets: ensure the mapping is located
    without changing what it does. Post-condition: the mapping is the union of the entries'
    `routing` lists, so a rule cannot name a repository that is not configured and "what must be
    unique is the repository, not the rule that reached it" holds structurally; every existing rule
    survives unchanged — the key space is the record's own comparable fields, evaluation is after
    normalization, an issue more than one repository matches is not routed and the condition is
    reported, and routing is a standing condition of a dispatched run. Ensure an entry with no
    `routing` matches every issue, and that the section states the consequence: two such entries
    make every issue ambiguous and therefore unrouted, which is the existing reported condition and
    not a new one. Done when no routing rule is stated twice and none is lost.

11. `SPEC.md` Section 6.4 Core Config Fields Summary (Cheat Sheet): ensure the repository level is
    in the sheet. Post-condition: the keyless row "a `repo.policy.toml` pointer per managed
    repository (Section 5.6)" is replaced by keyed rows — `repository.<name>.policy`,
    `repository.<name>.vcs.*`, `repository.<name>.agent.*`, `repository.<name>.routing`; the
    section's introductory paragraph states the inheritance rule once; and the
    `vcs.git_credential` / `vcs.forge_credential` row cites that rule instead of stating its own
    two-level version, keeping the MUST that an implementation supports the per-repository form.
    Ensure the sheet spells every `repository.<name>.…` leaf that prose elsewhere names — Section
    15.3's `repository.<name>.vcs.git_credential` among them — rather than a `.*` standing for
    them: `scripts/validate_spec_consistency.py` check 3 tests a dotted token for occurrence in the
    Section 6.4 slice as a substring, so a wildcard row covers no leaf. Done when every dotted key
    this decision introduces appears in the sheet and `python3 scripts/validate_spec_consistency.py`
    reports no new warning.

12. `SPEC.md` Section 6.3 Dispatch Preflight Validation, the validation checks: ensure the
    enumeration is validated before dispatch. Post-condition: at least one `repository` entry is
    configured; every entry's key is a valid `Repository Key`; the existing routing check is
    reworded to address rules by their location rather than adding a check; and every entry resolves
    the `vcs` fields Section 9.7 requires *after* inheritance, so a deployment supplying no
    `vcs.local_vcs` for one repository fails configuration rather than defaulting one for it. Done
    when a misconfiguration this schema newly admits is refused at preflight rather than at first
    use.

13. `SPEC.md` Section 9.1 Workspace Layout and `SPEC.md` Section 9.5 Safety Invariants: ensure one
    path form and a constrained repository component. Post-condition: the per-issue workspace path
    is `<workspace.root>/<repo_key>/<sanitized_issue_identifier>` in every case, with the section
    stating why — under an enumeration the single-repository deployment is one entry rather than a
    distinct mode, and a layout that depends on the number of entries re-keys existing workspaces
    when an unrelated entry is added; Invariant 3 states that the repository component is a
    `Repository Key`, constrained at validation rather than sanitized, while the issue component is
    sanitized as it is today. Done when Invariant 2 holds without relying on sanitization of the
    repository component.

14. `SPEC.md` Section 9.7 Repository Provisioning and the VCS Engine, `SPEC.md` Section 15.3 Secret
    Handling, and `SPEC.md` Section 10.9 Agent Adapters and Selection: ensure each names where its
    value is written. Post-condition: Section 9.7's Configuration bullet reads as the `vcs` object
    of a `repository` entry, with the orchestrator-level `vcs` supplying what an entry does not
    carry; Section 15.3's per-repository credential sentence names
    `repository.<name>.vcs.git_credential` and cites the general inheritance rule rather than
    restating one; Section 10.9's Selection bullets name `repository.<name>.agent`. Done when the
    Section 15.3 MUST is discharged by writing a key this document names.

15. `SPEC.md` Section 16.4 Dispatch One Issue: ensure `repo_of(issue)` is stated as returning the
    `Repository Key` the Section 8.7 mapping selects. No function body is added; this is the naming
    that keeps the reference algorithms and the routing rules describing one operation. Done when a
    reader of Section 16.4 can say what `repo_of` returns without leaving Section 16.

16. `conformance/vocabulary.json`, the `config_namespaces` group: ensure it publishes the namespace.
    Post-condition: a `repository` entry with `artifact: operator_policy_config`, `core: true` and
    the new Section 5.3 subsection as its `spec_ref`, noting that its entries hold the
    repository-level keys and that an unset one inherits; the `vcs` entry's note records that its
    fields are documented in Section 9.7 and that it exists at both levels. Done when `python3
    scripts/validate_spec_consistency.py` passes.

17. `conformance/vectors/config-defaults.json` and a new
    `conformance/vectors/repository-inheritance.json`: ensure the corpus says which level it is
    reading. Post-condition: the defaults vector's `description` states that its input is one
    repository's effective flat view — after inheritance, before secret resolution and cross-field
    validation — so the defaulting layer stays determinate under a two-level schema; the new vector
    exercises the fallback as a pure function of (orchestrator-level config, one entry), covering a
    key only the orchestrator level carries, a key only the entry carries, a key both carry, an
    entry overriding one `agent` leaf and inheriting its sibling, and an `agent` field an entry may
    not carry at all. Done when the leaf-by-leaf rule is checkable rather than only stated.

18. `conformance/vectors/issue-routing.json` and `conformance/vectors/standing-conditions.json`,
    their `notes`: ensure neither still asserts an absence this decision closes. Both carry the
    claim — issue-routing.json that the mapping's configuration schema is not fixed by `SPEC.md`
    and is deliberately not pinned there, standing-conditions.json that it is not fixed and is not
    pinned, each citing decision 0148. Post-condition: each note records that the rules are now
    located in `SPEC.md`'s `repository` entries, that the file still asserts the key space and the
    pure-function property rather than the configuration shape, and that a harness maps its own
    representation onto the rule shape as before. Done when no note in the corpus claims the
    repository-enumeration schema is owed a decision.
    (`conformance/vcsx/vectors/policy-validation.json` carries the same wording about a different
    subject — which reason a validation reports when several conditions hold — and needs no
    change.)

19. `conformance/README.md`, the *Surfaced findings* section: ensure its findings match the corpus.
    Post-condition: the open finding whose heading begins "`vcs` is not in Section 5.3's top-level
    key list" (at `be0ee6a`, `conformance/README.md:438`) is closed, naming what actually happened —
    `SPEC.md` Section 5.3 lists `vcs` today, and the `vcs.api_key` the finding cites left `SPEC.md`
    with the code-host relocation (`d2647a0`, decisions 0091–0093); and a finding for this decision
    is appended in that section's voice. Done when no finding there claims something the corpus
    contradicts.

## Cross-cutting sync

- `SPEC.md` Section 6.4 config cheat sheet: step 11.
- `SPEC.md` Section 17.1: a check that a repository-level key overrides the orchestrator-level one
  leaf by leaf while an unset one inherits; a check that a `Repository Key` outside `[A-Za-z0-9._-]`
  fails configuration; and the existing "Two repositories whose Ways of Working differ run under one
  operator policy config" row re-read against the enumeration it now names.
- `SPEC.md` Section 17.2: a check that the per-issue workspace path is repository-qualified for a
  single-repository instance as well as a multi-repository one.
- `SPEC.md` Section 17.4: the existing routing rows re-read against rules located in the entry; a
  row that an entry with no `routing` matches every issue, and that two such entries leave every
  issue unrouted and reported.
- `SPEC.md` Section 18.1: the multi-repository row names the enumeration and the inheritance rule;
  the credential row (Sections 8.7, 13.1, 15.3) names where the per-repository value is written.
- `CONFORMANCE-STATEMENT-TEMPLATE.md`: no row owed (see Scope).

## Ordering

Steps 1–2 first: every later step addresses keys that subsection introduces. Step 5 before steps 6
and 13, which cite the identifier rather than restating it. Steps 16–18 last, since the derived
artifacts read the prose.

## Out of scope, and owed separately

**Two trackers in one instance.** `SPEC.md` Sections 8.1 and 8.7 imply it today and Section 5.3.1
cannot express it; this plan makes them agree on one tracker rather than building the other half.
What that half needs is not schema: Section 4.2's `Issue ID` is unqualified and Section 4.1.8 keys
`running`, `claimed` and `completed` by it, so two trackers minting one id collide in orchestrator
state; Section 6.3's four singular "selected tracker adapter" checks become per-tracker; Section
11.7's capability descriptor is consulted per adapter; and Section 13.1's log context would carry
the tracker. Recorded so the next reader does not mistake step 3 for a narrowing that closed the
question.

**Per-repository scheduling limits.** Step 4 places existing fields; it does not add a
per-repository `max_concurrent_agents` or `max_turns`. Either is a capability with its own
accounting rule in `SPEC.md` Section 8.3 and is owed a decision of its own if a deployment needs it.

## Anchor changes

New anchors:

- `repository` — top-level operator-config key (`SPEC.md` Section 5.3), and its subsection titled
  `` `repository` (map of objects) ``.
- `repository.<name>.policy`, `repository.<name>.vcs`, `repository.<name>.agent`,
  `repository.<name>.routing` — the repository-level keys.
- `Repository Key` — stable identifier (`SPEC.md` Section 4.2).

Removed:

- `SPEC.md` Section 6.4's keyless row for the `repo.policy.toml` pointer, superseded by
  `repository.<name>.policy`.
- `SPEC.md` Section 9.1's single-repository path form, superseded by the repository-qualified form.
- `SPEC.md` Section 8.7's clause naming the trackers a repository draws work from, with no
  successor: the instance has one tracker (Section 5.3.1).

No code token is renamed. `repo_key` keeps its spelling and gains a definition.

## Status

Applied. `SPEC.md` Sections 4.1.8, 4.2, 5.3 (key list and the new 5.3.7), 5.3.1, 5.3.5, 5.6, 6.1,
6.3, 6.4, 8.1, 8.7, 9.1, 9.5, 9.7, 10.9, 15.3, 16.4, 17.1, 17.2, 17.4 and 18.1;
`conformance/vocabulary.json`, `conformance/vectors/config-defaults.json`,
`conformance/vectors/issue-routing.json`, `conformance/vectors/standing-conditions.json`, the new
`conformance/vectors/repository-inheritance.json`, and `conformance/README.md`. No row was owed in
`CONFORMANCE-STATEMENT-TEMPLATE.md` and none was added. `python3
scripts/validate_spec_consistency.py` reports `0 error(s), 0 warning(s)`; `python3
scripts/check_plan_anchors.py <this file> --rev be0ee6a` reports no finding.

One claim in this plan did not survive implementation and is corrected above: step 7 first said
inheritance is applied *after* built-in defaults. It has to run before them, or the default filled
into an entry shadows the orchestrator-level value the entry meant to inherit. Recorded in
`Background.md` and logged as a `retro` against the P lens.
