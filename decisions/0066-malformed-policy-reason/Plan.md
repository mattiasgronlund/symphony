# Plan — 0066 A policy that is not well formed is `malformed_policy`

## Scope

`VCSX-SPEC.md`: Sections 6.10 "Validation" (the registry and its rules), 6.1 "File Discovery and
`vcsx.toml` Merge", 6.2 "`[engine]`", 6.5 "`[policy]` Edges", 13.1 "Test Matrix", and 13.2
"Implementation Checklist". `conformance/vcsx/vocabulary.json`,
`conformance/vcsx/vectors/policy-validation.json`, `conformance/vcsx/README.md`, and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` follow the new token.

No section is added and none is renumbered: `malformed_policy` joins an existing registry and the
three new conditions are rows in an existing table.

No edit to Section 8.2 "Result Envelope": it already fixes the envelope for a run in which the policy
did not run — `usage_or_config`, `op` and `class` null, `reason` carrying the configuration reason
(Section 6.10) — and a tenth configuration reason changes nothing about that shape. No edit to
Section 8.3 "Exit Codes" for the same reason: `2` already names `usage_or_config`. No edit to
Section 8.5 "Versioning and the Version Grammar": its major-stable bullet names "the configuration
reasons (Section 6.10)" as a set, so the new token is governed without being listed, and its `MINOR`
bullet already says a new configuration reason is absorbed through the unchanging `usage_or_config`
status. No edit to Section 8.6 "Invocation Preconditions": its dividing line against Section 6.10 is
what files these three conditions here, and it is stated correctly as it stands. No edit to
Section 13.3 "Conformance Statement": this decision creates no `Implementation-defined` site and no
new "MUST document" obligation, and Section 13.3's "any reason token the engine adds beyond a
registry" bullet already covers an engine that adds an eleventh.

No `VCSX-CONTRACT.md` edit: it enumerates no configuration reason, mentions no invocation status, and
its Section 11 defers "the field-level schema of `repo.policy.toml` and its sections" and the engine
invocation contract to `VCSX-SPEC.md`. The whole of this decision is on the deferred side.

No `SPEC.md` edit: decision 0044's `Engine Invocation Failures` class (Symphony's Section 12.1)
already lists "a usage or configuration result in which the policy did not run — for example an
invalid `repo.policy.toml`", which is precisely this case. The refusal becoming legible does not
change the classification, on the same reasoning decision 0056 recorded when it made the other nine
legible.

Vector corpus, partially: `policy-validation.json` asserts `validate_policy` over a policy **document**
(`given.policy` is already parsed), so the unparsable-file row is not assertable in that file — its
input would have to be file text. The other two rows are pure over the inputs the file already
supplies and gain vectors. The gap is recorded in the file's `notes`, in the shape the
`capability_unsupported` note already uses, rather than left to be inferred.

## Steps

1. **A discovered policy file that does not parse is a configuration error, said where the loader is
   described.** Ensure Section 6.1 "File Discovery and `vcsx.toml` Merge" carries a bullet stating that
   a discovered file that does not parse yields no policy to validate and is a configuration error
   (Section 6.10). Ensure the existing bullets — path resolution and the `Implementation-defined`
   discovery precedence, the `vcsx.toml` merge and its precedence, and the unknown-key rule — are
   unchanged. Done when an implementer writing the loader finds the failure answered in the section
   that assigns the read.
2. **`version_floor` states its grammar and what a value outside it does.** Ensure Section 6.2's
   `version_floor` bullet says the value is stated as a `MAJOR.MINOR` version (Section 8.5) and that a
   value that is not one is a configuration error (Section 6.10) rather than a floor the engine
   compares. Done when the question "what does `latest` do" is answered at the key.
3. **An edge MUST carry its action's arguments.** Ensure Section 6.5 "`[policy]` Edges" states, beside
   the existing requirement that an edge's `on` be a recognized trigger and that a duplicate
   `(from, on)` is a configuration error, that an edge MUST carry the arguments the action its `do`
   names needs in order to be dispatched — `op` for `run_op`, `hook` for `run` — and that an edge
   omitting one is a configuration error (Section 6.10). Done when the two arguments the section's own
   example labels are covered by a stated requirement.
4. **The registry gains `malformed_policy` with three rows.** Ensure Section 6.10's `| Condition |
   Reason |` table carries, ahead of the nine consistency conditions: a discovered `repo.policy.toml`,
   or a `vcsx.toml` merged into it, that does not parse (Section 6.1); a key whose value does not
   satisfy the constraints its section states, naming an `[engine] version_floor` that is not a
   `MAJOR.MINOR` version as the instance (Sections 6.2, 8.5); and an edge whose action cannot be
   dispatched from the arguments it carries, naming a `run_op` with no `op` and a `run` with no `hook`
   (Sections 5.2, 6.5). Each reports `malformed_policy`. Done when each of issue #12's three states has
   a row and the nine existing rows are unchanged.
5. **Well-formedness precedes consistency, and the ordering is stated.** Ensure Section 6.10 records
   that the well-formedness conditions come before the rest — a policy that does not parse yields no
   document for the remaining checks — and that validation therefore presupposes a document. Done when
   a reader can see why a file that never became a document is reported from this registry rather than
   from the checks it never reached.
6. **`malformed_policy` is the residual condition, not a competing one.** Ensure Section 6.10 states
   that it covers a well-formedness failure no other condition in the table names, and that where
   another names the state — a missing or malformed `prefixes` map is `base_unresolvable` (Section
   6.4) — that condition's reason is reported. Done when the new row cannot absorb an existing one, and
   the `Implementation-defined` multiple-condition rule is left to the case it was written for.
7. **The boundary against `version_floor_unmet` is explicit.** Ensure Section 6.10 states that
   `version_floor_unmet` names a floor the engine read and does not satisfy, that a floor it cannot
   read is `malformed_policy`, and that the refusal is the same either way — the engine runs only where
   the floor is demonstrably satisfied (Section 8.5) — while the two reasons name different repairs.
   Done when an implementer cannot read fail-closedness as choosing the reason as well as the refusal.
8. **The boundary against `unknown_operation` / `unknown_hook` is explicit.** Ensure Section 6.10
   states that those two name an argument the engine resolved and did not recognize, that an absent
   argument is `malformed_policy`, and that the condition is stated over the actions rather than per
   argument because `set_state` with no target has the same shape and no reason of its own. Done when
   an absent argument to any action has an answer, not only the two Section 6.5 illustrates.
9. **Section 6.1's forward-compatibility rule is scoped.** Ensure Section 6.10 states that the rule
   that an unknown key SHOULD be ignored covers a key the schema does not declare, not a declared key
   whose value the schema does not admit. Done when the new rows cannot be read as ignorable.
10. **The test matrix covers the three states.** Ensure Section 13.1's `Invocation contract` check
    states that a policy file that does not parse, a `version_floor` that is not a `MAJOR.MINOR`
    version, and an edge omitting the argument its action requires each refuse to run the policy and
    yield `usage_or_config` with `malformed_policy` and null `op`/`class` (Section 6.10), and that the
    existing fail-closed `version_floor` clause is preserved beside it. Done when each of the issue's
    three states is a testable line.
11. **The checklist names well-formedness.** Ensure Section 13.2's `repo.policy.toml` loader bullet
    includes refusing a policy that is not well formed. Done when the definition of done covers a file
    the loader cannot read.
12. **The vocabulary registry carries the token.** Ensure `conformance/vcsx/vocabulary.json`'s
    `config_reasons` group carries a `malformed_policy` entry whose meaning names the three conditions
    and its residual scope, positioned as the group's first entry to match the table. Ensure the
    group's `spec_refs` name Section 6.1 alongside Sections 6.10 and 9.3. Done when the registry and
    the table agree entry for entry.
13. **The corpus asserts what it can and records what it cannot.** Ensure
    `conformance/vcsx/vectors/policy-validation.json` carries vectors expecting `malformed_policy` for
    a `version_floor` that is not a version, for a `run_op` edge with no `op`, and for a `run` edge
    with no `hook`; and a note recording that the unparsable-file condition is not exercised because
    `given.policy` is a document rather than file text, which is a coverage gap and not a statement
    that the condition is unvalidated. Ensure the file's `spec_refs` name Section 6.1. Done when every
    assertable row of the new registry entry has a vector and the unassertable one has a reason.
14. **The corpus README's count and history stay true.** Ensure `conformance/vcsx/README.md`'s vector
    count and its parenthetical history include this decision's vectors. Done when the stated count
    matches the files.
15. **The template records the floor's shape and the loader's obligation.** Ensure
    `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 1 carries a REQUIRED-not-a-choice line for a
    `version_floor` that is not a `MAJOR.MINOR` version being refused as `malformed_policy` rather than
    compared, beside the existing below-floor line; and that Section 2's `repo.policy.toml` loader item
    names the refusal of a policy that is not well formed, mirroring Section 13.2. Done when an engine
    filling in the template declares both halves of the floor's behavior.

## Cross-cutting sync

`conformance/vcsx/vocabulary.json` (Step 12), `conformance/vcsx/vectors/policy-validation.json`
(Step 13), `conformance/vcsx/README.md` (Step 14), and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`
(Step 15).

`VCSX-SPEC.md`'s own cross-cutting sections are Sections 13.1 and 13.2, handled in Steps 10 and 11.
Section 13.3 needs no edit (see Scope). The `SPEC.md` cross-cutting sections named in `CLAUDE.md` —
its config cheat sheet, test matrix and implementation checklist — are untouched, because this
decision changes `VCSX-SPEC.md` only.

## Anchor changes

None removed or renamed. Added: one configuration reason token, `malformed_policy` (Section 6.10).

`version_floor_unmet`, `unknown_operation` and `unknown_hook` keep both their spelling and their
conditions; this decision states what they do *not* cover rather than narrowing what they do.

## Out of scope

- **A repository with no `repo.policy.toml` at all.** Recorded in `Background.md`: answering it means
  deciding whether a policy-less repository is a valid input, which touches the defaults of `[base]`,
  `[engine]` and `[scope]` together. `malformed_policy` is scoped to a file the engine discovered and
  could not parse.
- **An I/O failure reading a discovered file** (permissions, a vanished path). It is a property of the
  host rather than of the policy's text, so it does not sit inside Section 6.10's contract that its
  conditions are statically determinable; naming it needs the same decision as the absent file.
- **A token per state** (`malformed_version_floor`, `missing_argument`, `malformed_config`). Option C
  in `Background.md`; reconsider if a caller is found that branches between them rather than surfacing
  `message` to a human.
- **An enumerated table of each action's required arguments.** The row is keyed on dispatchability
  instead, which covers the actions Section 5.2 lists without asserting a required-argument set that
  Section 6.5's own bare `do = "escalate"` example would contradict.
- **A vector for the unparsable file.** It needs file text as input, which `validate_policy`'s vector
  shape does not supply; recorded in the vector file's `notes` rather than left to inference.

## Status

Applied to `VCSX-SPEC.md` (Sections 6.1, 6.2, 6.5, 6.10, 13.1, 13.2), `conformance/vcsx/`
(`vocabulary.json`, `vectors/policy-validation.json`, `README.md`), and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.
