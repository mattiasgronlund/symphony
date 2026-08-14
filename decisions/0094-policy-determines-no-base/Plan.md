# Plan — 0094 A policy that determines no base

**Not to be executed while this decision is `Proposed`.** The steps below implement option C from
`Background.md`; they are written now so the option is costed rather than described. If option A or
B is taken instead, this plan is replaced rather than amended.

## Scope

`VCSX-SPEC.md`: Sections 6.1 "File Discovery and `vcsx.toml` Merge", 6.4 "`[base]` and Base
Resolution", 6.10 "Validation", 13.1 "Test Matrix", 13.2 "Implementation Checklist".

`conformance/vcsx/vocabulary.json` (`config_reasons`) and
`conformance/vcsx/vectors/policy-validation.json`.

`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`, if a reason token is minted rather than widened.

`SPEC.md`: Section 5.6 "`repo.policy.toml` (Repository Way of Working)" and the Section 6.4 cheat
sheet, only if step 2 makes `[base] branch` explicitly REQUIRED.

## Tokens introduced

- None, if `base_unresolvable` is widened (the recommended sub-answer). A minted token would be a
  `config_reasons` entry and would reach `vocabulary.json` and the Conformance Statement template.

## Steps

1. **An absent policy has a stated meaning (Section 6.1)** — ensure the bullet list that today names
   only "A discovered file that does not parse" also states what an undiscovered file means: the
   engine holds a policy that determines no base, which is the same state as a discovered policy
   whose `[base]` selects none, and both take the disposition step 3 fixes. *Done when* Section 6.1
   distinguishes "not discovered" from "does not parse" and routes both to Section 6.10.

2. **`[base] branch` is REQUIRED in its own words (Section 6.4)** — ensure the `branch` key states
   that it is REQUIRED rather than leaving the requirement to the absence of a `Default:` line, and
   that its absence names the Section 6.10 condition. *Done when* no reader has to infer a
   requirement from a missing default, and `grep -n 'branch. (string)' VCSX-SPEC.md` shows the
   REQUIRED marker.

3. **The condition is a configuration error, scoped to the entries that can reach a base
   (Section 6.10)** — ensure the table carries a row for a policy that selects no base branch,
   covering both the absent document and the absent key, and ensure the surrounding prose scopes the
   refusal to `ship`, `integrate` and `create_pr`, admitting `commit`, `push`, `pull`, `merge`,
   `land` and `provision`. Ensure an entry outside the set that reaches a base-needing operation
   through a `run_op` edge is stated to report that operation's own `base_unresolved` at the
   dispatch, which is the disposition Section 8.6 already gives `git_access`. *Done when* the row
   exists, the two sets are enumerated, and the `run_op` case is named.

4. **The sixth validation input is stated, not smuggled (Section 6.10)** — ensure "Validation is
   judged from five inputs and no others" becomes six, with the invoked entry point named and its
   availability argued: `arguments_unreadable` is established before validation (Section 8.6), and
   decoding the arguments is what names the entry point, so validation already runs with it known.
   Ensure the existing five keep their stated roles, in particular that `capability_unsupported`
   still turns on the consumer's selection (decision 0092's third input). *Done when* the count, the
   enumeration, and `conformance/vcsx/vocabulary.json`'s two "five inputs" notes agree.

5. **`status` and `diff` take an answer (Sections 4.1, 6.10)** — ensure the document says whether a
   read runs against a policy that selects no base. The recommended answer follows Section 4.1's
   existing rule that a read "reports no determinate value it did not establish": `status` is
   admitted and reports the base as null with an output saying so, alongside its existing
   `base_absent`; `diff`, which has no delta to produce, joins the refused set. *Done when* neither
   operation's behavior has to be inferred from the base-needing set alone.

## Cross-cutting sync

- **`VCSX-SPEC.md` test matrix (Section 13.1)** — a `ship` against a repository with no
  `repo.policy.toml` is refused at validation and publishes nothing, in particular running no
  `commit` and no `push`; a `commit` and a `push` against the same repository run; a policy carrying
  `[base]` with no `branch` is refused identically to no policy at all, the two being one state; an
  entry outside the refused set that routes to `integrate` through a `run_op` edge reports
  `integrate:base_unresolved` rather than a configuration reason.
- **`VCSX-SPEC.md` implementation checklist (Section 13.2)** — extend the policy-loader line with
  the absent-document case and the entry-scoped base refusal.
- **`conformance/vcsx/vectors/policy-validation.json`** — the corpus supplies `base.branch` in all
  32 vectors (`Background.md` records the measurement). Add vectors for the absent key and the
  absent document, and note in `given` that validation now takes the entry point, which no vector
  models today; vectors for the admitted entries belong with them or the corpus asserts only the
  refusals.
- **`conformance/vcsx/vocabulary.json`** — update both notes that read "Validation is judged from
  five inputs", and widen `base_unresolvable`'s meaning if step 3 reuses it.
- **`conformance/vcsx/README.md`** — the entry-point-dependent vectors are a new fixture-vs-vector
  boundary case; record which side they land on.
- **`SPEC.md`** — only if step 2 lands: Section 5.6's `repo.policy.toml` section list and the
  Section 6.4 cheat sheet both name the base branch, and a REQUIRED marker belongs in both.

## Anchor changes

None yet — this decision is `Proposed`. If step 3 mints a reason token rather than widening
`base_unresolvable`, record it here on acceptance; if step 2 changes `[base] branch`'s stated
optionality, that is a constraint change rather than an anchor change and needs no entry.

## Status

Proposed. Not applied. Opened from decision 0093's second review finding, which made `provision` the
one entry point that runs with no policy discovered and thereby exposed that no other entry point
had a stated answer.
