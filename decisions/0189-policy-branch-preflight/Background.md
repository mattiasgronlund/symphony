# Background — 0189 Check 3 reaches `vcs.policy_branch`, and the corpus says so

## Context

Reported from `symphony-rs` as issue #189, at pin `c9f031f`. Its decision 0162 and decision 0011
R117 record the same problem from the implementation side.

The spec text is unambiguous:

- Section 6.3's third check is "The `vcs` fields Section 9.7 requires are resolved for every
  `repository` entry", and it fails with `missing_vcs_field`.
- Section 9.7 makes `vcs.policy_branch` "REQUIRED under `policy_source = "policy_branch"`, and it
  has no default there".
- `vcs.policy_source` defaults to `policy_branch` (Sections 6.4, 9.7).

So a configuration in the default mode with no `vcs.policy_branch` fails check 3.

`conformance/vectors/config-preflight.json` does not model the key. Its input shape is
`vcs: { local_vcs, base_branch_allowed? }`, and every vector that has a repository configures `vcs`
as `{ "local_vcs": "git" }`. Neither `policy_branch` nor `policy_source` occurs anywhere in the
file. Each artifact is complete against itself, and the two disagree. That is the shape
`scripts/validate_spec_consistency.py` exists to catch, but no check reads a vector's `given`
against the fields Section 9.7 requires.

## The failure path, and how far it reaches

The issue reported the six valid vectors as invalid by the prose. Checking the file against Section
6.3's order rule showed the reach is wider. Where several conditions hold, an implementation "MUST
report the reason of whichever is first in the table's order", and `missing_vcs_field` is third.
Every vector configuring `{ "local_vcs": "git" }` holds check 3's failure as well as whatever its id
names. Measured against the file at `c9f031f`, by listing each vector's `vcs` and `expect.reason`
(`python3 -I`, reading `conformance/vectors/config-preflight.json`):

- **20 vectors** carry an expectation the prose contradicts:
  - The 6 valid ones: `valid-minimal-config`, `valid-config-capabilities-satisfied`,
    `valid-none-mode-adapter-requires-no-key`, `valid-base-branch-patterns`,
    `base-branch-allowed-empty-list`, and `base-branch-pattern-escaped-bang-is-literal`. Each should
    be invalid.
  - The 14 refusing ones whose condition comes after check 3: three `invalid_base_branch_pattern`,
    nine tracker, capability, routing and agent-command vectors, and two `order-*` vectors. Each
    should expect `missing_vcs_field`.
- **2 more** keep their expectation but hold a second failing condition, against the file's own note
  that "each refusing vector holds exactly one failing condition":
  - `invalid-repository-key` fails check 2 first.
  - `missing-vcs-field` fails check 3 on `local_vcs` and on `policy_branch` under one token.
- **2 are untouched**, having no repository entry: `no-repository-configured` and
  `order-repository-before-agent-command`.

`symphony-rs` first counted 23 and agreed to 24 when the missing vector was named. What kept all 20
green there is a harness placeholder (`HARNESS_POLICY_BRANCH`,
`crates/symphony-conformance/src/lib.rs:1167`). That placeholder is the symptom: an implementation
reading the prose has to add a value the corpus does not carry to pass the corpus.

What ships broken without a fix, either way:

- An implementation that follows the corpus accepts a default-mode configuration with no policy
  branch. It finds out at the first host-side read instead of at startup. Check 3 exists to prevent
  exactly that, and Section 9.7 gives the reason the key has no default: "every default that
  resolves to the pull-request target would make the trust root a branch Symphony merges into".
- An implementation that follows the prose fails 20 vectors.

## Decision

**Check 3 covers `vcs.policy_branch` under the default mode.** This is a reading, not a change: the
prose already says it. Section 6.3 gains the conditional field next to its `vcs.local_vcs` example,
so the reading no longer depends on following three cross-references. Under
`policy_source = "target_branch"` the key is "neither required nor consulted" (Section 9.7), and
check 3 does not reach it.

**A required `vcs` field is unresolved when absent or empty, for check 3 as a whole.** A value with
any character in it is resolved, and a malformed one is judged wherever its value is used.

- **The argument doesn't depend on the field.** A whitespace-only value is a malformed name for
  whichever field it fills, never a missing one. For `local_vcs`, `" "` is a backend nobody
  supports, the same as `"hg"` on an engine without one. For `policy_branch`, it is a name that
  resolves to no branch. Reporting either as `missing_vcs_field` gives the operator a cause they did
  not have.
- **Check 3 has one predicate.** It is stated with one word, "resolved", over every field it reads.
  A rule for one key would give check 3 two presence tests the prose doesn't distinguish, and every
  field later added to the required set would reopen which applies.
- **It matches the spec's existing rules.** Two rules state the empty case without trimming:
  `tracker.api_key` ("If the resolved secret is empty, treat the key as missing", Section 5.3.1) and
  `missing_agent_command` ("absent or empty", Section 6.3).
- **Consequence, accepted on the issue:** a whitespace-only `local_vcs` passes preflight and is
  refused where an unsupported backend is refused, at the engine, as `"hg"` is today. Whether
  preflight should check that `local_vcs` names a supported backend is a separate question, and
  this decision does not raise it.

`symphony-rs` trimmed (`crates/symphony-config/src/validate.rs:343`, with one helper serving every
field check 3 reads). It will narrow that helper to absent-or-empty for both fields.

**The corpus carries the key.**

- The input shape becomes
  `vcs: { local_vcs, policy_source?, policy_branch?, base_branch_allowed? }`. An absent
  `policy_source` means `policy_branch`.
- The 22 vectors above state `policy_branch: "policy"`, so each holds exactly the condition its id
  names.
- Three vectors are added:
  - `missing-vcs-policy-branch`: default mode, no branch → `missing_vcs_field`.
  - `empty-vcs-policy-branch`: `policy_branch: ""` → `missing_vcs_field`.
  - `valid-target-branch-mode-without-policy-branch`: `policy_source: "target_branch"`, no branch →
    valid. This pins the conditional, so an implementation that requires the key in every mode fails
    it.

Decision 0190 (issue #191) changes the third vector. It adds the input `supported_policy_sources`,
and gives an implementation the right to decline `target_branch`. Until 0190 lands, this vector
reads Section 18.1.4 as it stands, under which both modes are required.

## Options considered

- **A. Check 3 does not cover the key; the corpus is right.** The steelman: preflight stays a
  shallow presence check over the fields that select a backend, and the engine refuses a missing
  branch anyway, with `policy_branch_missing` (`VCSX-SPEC.md` Section 8.6), so nothing runs without
  one. It loses because the prose already says otherwise in three places, and because the engine
  refuses at the first invocation of a dispatched issue, not at startup. Check 3's own example names
  the difference: "fails configuration rather than defaulting one for it". Adopting this option
  would be a spec change narrowing check 3, made to match a corpus that never modelled the key.
- **B. Treat whitespace-only as missing (`symphony-rs`'s trimming).** The steelman: an operator who
  leaves `" "` in a configuration probably meant to leave the key unset, and reporting it at startup
  is kinder than an engine refusal later. It loses because `missing_vcs_field` would then name a
  cause the operator did not have. The kinder report belongs to a well-formedness check that names
  the real cause, the way `invalid_base_branch_pattern` does, and that is a separate question.
- **C. An empty-only rule for `policy_branch` alone.** The steelman: it is the narrowest change that
  answers the issue, and it leaves `local_vcs` as it stands. It loses on check 3's single predicate,
  argued above. `symphony-rs` confirmed that a per-key rule would also have meant two tests in its
  code.
- **D. Require `policy_source` on every vector.** The steelman: it is explicit, and no harness
  applies the wrong default. It loses because the file already treats optional inputs as defaulting
  when absent (`base_branch_allowed?`), and requiring the field would add a line unrelated to the
  test to every vector.

## Review findings

The issue thread corrected the proposal twice, and both corrections are recorded here.

- The proposal said `symphony-rs` already applied the empty-only reading. It did not, because its
  test trims. That claim was about another repository and was not checked before it was made.
- The implementation's count of affected vectors (23) missed `invalid-repository-key`. The count was
  repaired by listing every vector's `vcs` and `expect.reason`, which is the measurement above,
  rather than by grouping from the ids.

## Reconsideration triggers

- Section 9.7 adds a field to the required set whose empty value is meaningful. Check 3's rule would
  then need an exception, and the single predicate would need restating.
- Operators routinely leave whitespace-only values where they mean unset, so that an engine refusal
  lands where a startup refusal was expected. That is the case for a preflight well-formedness
  check, which this decision leaves open.

Relates to 0164 (Section 6.3's reason table and this corpus), 0159 (resolution against the
orchestrator level), and 0190 (the `policy_source` row and `supported_policy_sources`).
