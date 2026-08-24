# Background — 0140 A dispatch condition no configuration and no record could supply

## Context

Issue #100 was filed by the `symphony-rs` build against `SPEC.md` Section 8.2. The third bullet of
its dispatch-eligibility list is two conditions in one sentence:

> - It is routed to this worker by the configured assignee and contains every label in
>   `tracker.required_labels`.

The second half is fully specified. Section 5.3.1 defines `tracker.required_labels`, gives it
`Default: []`, and states its matching rule — matching "ignores surrounding whitespace on both
sides, and compares under `Lowercase Normalization`", and "A blank configured label matches no
issue".

The first half has none of that. There is no configured assignee anywhere in the document:

- Section 5.3.1's `tracker` object is `kind`, `endpoint`, `api_key`, `project_slug`,
  `required_labels`, `active_states`, `terminal_states` and `transitions`. None names an assignee.
- Section 6.4's cheat sheet carries eight `tracker.*` rows and no `tracker.assignee`.
- Section 4.1.1's normalized issue record is `id`, `identifier`, `title`, `description`, `priority`,
  `state`, `branch_name`, `url`, `labels`, `blocked_by`, `created_at`, `updated_at` and `metadata`.
  There is no assignee field. `metadata` is not the intended channel: Section 4.1.1 says in its own
  words that "the orchestrator core does not interpret it".
- The word `assignee` occurs three times in `SPEC.md`, and only one of them is a field: Section
  4.1.9's **task** assignee, which belongs to Section 8.10 Autonomous Task Management — an OPTIONAL
  extension, and a different entity from an issue.

## The failure path

Section 8.2 is `Daemon Conformance` and Section 17.4 checks candidate selection, so this is a
condition a conformance suite is meant to exercise. Nothing pins it. Section 16.2 calls
`should_dispatch(issue, state)` and Section 16 defines no body for it — one of the forty-two names
decision 0138 counted — and `conformance/vectors/` holds nine files, none of them a
candidate-eligibility file. What an implementation does with the bullet is therefore whatever it
reads into the sentence, and three readings are faithful to the text and mutually incompatible:

- **treat it as always true**, so every fetched candidate is routed to every worker — which is what
  a single-repository deployment silently gets, and which is correct there;
- **invent a configuration key**, at which point two implementations disagree about its name and
  about what an assignee is compared as: a provider id, a login or a display name, under `Lowercase
  Normalization` or exactly;
- **read `metadata`**, which Section 4.1.1 forbids the core to interpret.

What ships broken is visible in the implementation that reported it. `should_dispatch` there checks
the eight bullets in Section 8.2's own order and returns *which* one refused; the routing half
arrives as `Eligibility::routed_here: bool` — supplied evidence rather than a computed value,
because nothing in Section 4.1.1 or Section 5.3.1 can compute it. A bullet that looks implemented
and is not, in the predicate that decides what the service works on.

### The sharpening that decides where the repair goes

The bullet is wrong twice, and the second defect is what rules out repairing it in place. Section
8.2 is evaluated at candidate selection, **before** dispatch. A `worker` in this document is the
per-issue task `dispatch_issue` spawns (Sections 7.2, 16.4 `spawn_worker`), so at the moment the
predicate is evaluated the subject of "routed to this worker" does not exist yet. It was never a
predicate over a record; it was a query-scope statement written at record altitude, and the subject
it meant is the deployment.

## Decision

Specify it, parallel to `required_labels` at every step:

- **Section 4.1.1 gains `assignees` (list of strings).** OPTIONAL and tracker-dependent — the shape
  `branch_name` and `blocked_by` already use — so an adapter whose tracker has no assignee model
  leaves it empty and the condition does not gate. Normalized with `Lowercase Normalization` as
  `labels` are. A list rather than a scalar, because Forgejo's assignee is plural.
- **Section 5.3.1 gains `tracker.assignee` (string), `Default: null`** — no assignee filter. Matched
  as `required_labels` is: surrounding whitespace ignored, compared under `Lowercase Normalization`,
  a blank configured value matching no issue. An issue matches when its `assignees` contain it.
- **Section 8.2's bullet splits into two conditions**, each fully specified from configuration and
  record. Section 5.3.1's existing "An issue MUST contain every configured label to dispatch **or
  continue**" covers the assignee by extension rather than by a new rule.
- **Section 11.2's Linear clause extends by one clause**: candidate and issue-state refresh queries
  include assignees, filtered after normalization, for the reason already written beside it.
- **Section 11.7's descriptor declares whether the adapter populates `assignees`**, and a configured
  `tracker.assignee` against an adapter that does not is a Section 6.3 dispatch-preflight
  configuration error. That is the shape Section 11.7 and Section 6.3 already carry together twice —
  for `tracker.api_key` under a `secret`-mode adapter, and for a non-empty `tracker.transitions`
  against an adapter that does not declare `set_state`. It is what keeps a configured filter from
  silently matching nothing.
- **A publication clause.** The identifier an adapter publishes in `assignees` MUST distinguish the
  tracker's principals under `Lowercase Normalization`; an adapter whose stable identifier does not
  — a case-significant opaque id — publishes the login or handle instead, and documents which.

The publication clause is a review finding against this decision's own first draft, and it is the
one place the design could still fail silently. That draft said `assignees` is "normalized with
`Lowercase Normalization` as `labels` are" *and* that which identifier the adapter publishes is
`Implementation-defined`. Those two clauses together re-import, one layer down, the hazard that was
raised against the Core field in the first place: Section 4.2's normalization is not a comparison an
adapter opts into — "Every case-insensitive comparison in this specification is defined over this
operation" — so an adapter publishing a case-significant opaque id gets it lowercased by the core,
two principals differing only in case become one, a configured `tracker.assignee` matches an issue
assigned to someone else, and the symptom is a dispatched issue rather than an error. Stating the
requirement over the **publication** rather than over the comparison leaves Section 4.2's sentence
true and puts the obligation where the adapter author can check it.

## Options considered

### Reword Section 8.2 so the routing half leaves Core — recommended first, and reversed

The routing half becomes adapter-side candidate scope: Core keeps only the label condition, Section
11.2 states beside the enumeration-completeness rule that scope beyond the configured project and
active states is adapter-side and tracker-dependent, and an adapter that narrows by nothing reports
every issue the project and states select, so the condition does not gate.

It has a real case, and it is the case for keeping every candidate-scoping decision in one place:

- **Project scoping is already there and is invisible to Section 8.2.** Section 11.1 defines
  `fetch_candidate_issues()` as returning "all matching issues in the configured active states for a
  configured project". `project_slug` is a Section 5.3.1 key and appears in neither Section 8.2's
  eight conditions nor Section 4.1.1's record.
- **Section 8.7 already owns assignee routing and deliberately does not normalize it.** "Routing
  uses an explicit, tracker-implementation-specific mapping in the policy config. For example, the
  `linear` adapter maps by project, team, label, or assignee."
- **Identity semantics are a real cost of the Core field.** Only the adapter knows whether its
  tracker's identifier is a login or an opaque id, and Section 4.2 fixes one answer for both.

It loses on three counts, and the first is the argument rather than the altitude:

1. **Section 11.2 answers the same question for the sibling half of the same bullet, and answers it
   against query scope.** "Candidate and issue-state refresh queries include issue labels. Required
   label filtering happens **after normalization** so refresh can observe label removal and stop or
   release existing work." The adapter fetches broadly, the value rides the record, and the core
   filters — precisely so the value stays visible on the refresh. Labels are the correct comparison
   for a per-issue attribute that can change while a run is in flight; `project_slug` is a
   container, and comparing to it was comparing the wrong thing.
2. **A scope key has no sanctioned home.** Section 5.3's extension mechanism admits "additional
   top-level keys", and Section 5.3 tells a reader "Unknown keys SHOULD be ignored for forward
   compatibility". So an adapter reading a scope key under `tracker` reads a key the schema says
   SHOULD be ignored, and an operator cannot distinguish a scoping adapter from one that ignored
   their scope. A repair for a duplication that creates a second one is not a repair.
3. **The continue side would be foreclosed, not deferred.** Under query scope, a running issue
   reassigned away is simply *absent* from the enumeration — and Section 16.3's
   `reconcile_running_issues` iterates `for issue in refreshed`, while Section 8.5 Part B enumerates
   three cases (terminal / active / neither) and has **no absent branch at all**. So the issue
   reaches none of them, and "reassigned away releases the claim" would later need the Section 5.3.1
   key after all: the same defect one layer down. Avoiding a foreclosure is worth more than
   recording one.

The identity cost survives the reversal and is answered rather than dismissed — by the device the
document already uses for labels: the adapter normalizes (Section 11.3), which identifier it
publishes is `Implementation-defined` and documented, and the publication clause above bounds that
choice so the core's comparison stays sound.

### Leave the bullet as it stands

The status quo, and it costs nothing today: a single-repository deployment reads the condition as
always true and is right to. It loses because Section 8.2 is `Daemon Conformance`. A condition that
cannot be evaluated from the specified configuration and the specified record is not a requirement,
and the divergence it admits is invisible in exactly the deployments where it does no harm.

## Out of scope, and false

The report's premise was that assignee routing "is what makes Section 8.7's shared-tracker
deployment safe" and that the divergence "only shows when two workers poll one tracker". Recorded
here because it is the premise a re-reader is most likely to re-litigate on, and it does not hold:

- Section 8.7 is **one instance managing several repositories**, and its mapping routes issues to
  repositories rather than to workers.
- Two *instances* sharing a tracker is not a deployment this specification describes, and the bullet
  would not make it safe if it were: `running` and `claimed` are `Reconstructable` in-memory fields
  of one orchestrator's runtime state (Section 4.1.8), so two instances share no claim at all. An
  assignee filter partitions work statically; it does not coordinate.

Removing the bullet would therefore have removed no guarantee, and adding the field adds none.
Cross-instance coordination is its own gap, its own issue and its own decision.

## What was checked

At `97617c2`, against the working tree:

- Section 8.2 lists eight conditions and fixes **no precedence among them**; Section 5.3.1 lists
  eight `tracker` fields; Section 4.1.1 lists thirteen; Section 6.4 carries eight `tracker.*` rows.
- `should_dispatch` occurs once in `SPEC.md`, at `SPEC.md:3946`, as a call.
  `validate_dispatch_config` occurs twice, at `SPEC.md:3907` and `SPEC.md:3928`, both calls. Neither
  is defined — the second is one of decision 0138's forty-two, which is why the Section 6.3
  preflight check lands as a *check* in a prose list rather than as a function body.
- `conformance/vectors/` holds nine files; there is no `candidate-eligibility.json`.
- `conformance/README.md` defers "**Tracker read/write** surfaces, candidate eligibility over live
  issues (Section 8.2, 11)" as "not purely deterministic from inputs alone".
- Section 19 enumerates the same obligations `CONFORMANCE-STATEMENT-TEMPLATE.md` tabulates, in prose
  — the pull-request-target carrier among them — so the new obligation is owed in two places rather
  than one. Found by `scripts/check_plan_anchors.py`'s reach check rather than by reading.
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## On the vectors

Section 8.2 fixes no precedence among its eight conditions, so a vector whose `expect` names the
**refusing condition** rather than a boolean pins the answer without pinning an evaluation order the
section does not state. The precedent is already in the corpus, in
`conformance/vcsx/vectors/policy-validation.json`'s notes: "Each failing vector holds exactly one
condition, so the reported reason is determined. Which reason is reported when several conditions
hold is Implementation-defined and is deliberately not exercised here." One condition per vector,
eight after the split, with the blank-configured-label case among them.

The two assignee cases split across two files, which is worth stating so neither goes missing:
configured-and-absent is an eligibility refusal and belongs in the new file; a configured
`tracker.assignee` against an adapter that populates no `assignees` is a Section 6.3 failure and
belongs with config validation, since it is not a predicate over a normalized record.

**Only the first half is pinned by this decision, and the reason belongs here rather than in a
corpus that is one file short.** There is no function for the second to be a case of:
`validate_dispatch_config` is called twice and defined nowhere, and `config-defaults.json` pins
`resolve_config_defaults`, which *defaults* a configuration rather than judging one. So the
preflight case gets its Section 17.4 row here and its vector in the decision that gives that
function a body. Inventing a corpus function for an undefined one would pin a shape the
specification has not chosen.

`conformance/README.md`'s deferral is amended in the same decision rather than later: the adapter's
fetch is genuinely not deterministic from inputs alone, and Section 8.2's predicate over an
already-normalized record plus resolved config is.

## Two notes on the publication clause, recorded after the draft

**It is an injectivity requirement rather than a case-insensitivity one, and the specification
supplies the counterexample.** Section 4.2 defines `Lowercase Normalization` as the Unicode Default
Case Conversion "using the full mappings rather than the simple ones" and states the consequence
itself: "the mapping is not one-to-one, so `İ` (U+0130) normalizes to `i` followed by U+0307". So a
clause worded "two principals differing only in case" is falsified by the example in the definition
it depends on — two identifiers can collide after normalization while differing in length before
it. Phrasing the clause over the operation ("MUST distinguish the tracker's principals under
`Lowercase Normalization`") catches that; the case-worded version reads as equivalent and is not.
Keeping the wording is therefore checkable against the document rather than a matter of care.

**The reverse direction is inherited, not introduced, and is deliberately not closed here.** Section
4.2 also says "No Unicode normalization form is applied ... two spellings of the same name that
differ only in normalization form do not compare equal". That is one principal spelled two ways,
matching nothing — the same exposure `tracker.required_labels` has carried since it was written,
where a configured label copied out of a tracker UI in another normalization form matches no issue
today. Closing it means changing `Lowercase Normalization` for every comparison in the document,
which is a decision about Section 4.2 rather than about the assignee. Recorded so a later reader
finds the answer rather than the question.

## Reconsideration triggers

- **A tracker whose assignee is not comparable as a string at all** — an assignment expressed as a
  group, a rotation or a query. `assignees` as a list of strings would then be the wrong shape, and
  the descriptor bit would have to carry more than "populated / not populated".
- **A second Symphony instance sharing a tracker becoming a deployment the specification
  describes.** The out-of-scope note above is what would be reopened, and the answer would not be
  this field: it would be a claim mechanism outside one orchestrator's memory.
- **`should_dispatch` gaining a body in Section 16.** The eight conditions would then have a stated
  evaluation order, and the one-condition-per-vector discipline could be relaxed — or would become
  wrong, if the order it states disagrees with what the vectors assume.
- **A third per-issue attribute arriving with the same shape** (a team, a component, a saved query).
  Three parallel copies of the `required_labels` pattern is the point at which a general
  "tracker-dependent match field" is cheaper than a fourth.
