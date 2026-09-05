# Background — 0163 The prompt template contract is a cross-implementation contract

## Context

`conformance/README.md` carried two open findings, and they are the same finding:

> **Template syntax is a floor, not a mandate (open).** Section 5.4 says a "Liquid-compatible
> semantics are sufficient" engine, which pins the strict-failure MUSTs and the
> `template_render_error` class but leaves the concrete delimiter/filter syntax to the
> implementation. Because `WORKFLOW.md` is repository-owned and must render on any implementation
> Symphony targets, the template syntax is effectively a cross-implementation contract.

> **`attempt` "null or absent" versus strict mode (open).** Section 5.4 lists `attempt` as
> `null`/absent on the first run, but strict variable checking says unknown variables MUST fail.
> Whether a template that reads `attempt` on the first run renders empty (known-but-null) or fails
> (absent = unknown) is undetermined, so no first-run `attempt` vector is authored.

Measuring the one implementation while resolving them surfaced two more of the same kind. All four
are instances of one property: `WORKFLOW.md` is written by a repository author who does not know
which implementation will render it, and `SPEC.md` does not fix what it renders to.

## The mechanism

The prompt is not a document that gets read and shrugged at. Section 12.4 disposes of a rendering
failure by failing the run attempt, and Section 5.5 gives the failure a REQUIRED class,
`template_render_error`. So every question the specification leaves open about rendering has the
same two possible answers — a string, or a failed run — and the repository author cannot tell which
they will get.

Five things a `WORKFLOW.md` can do whose outcome `SPEC.md` does not fix:

**1. The syntax itself.** "Use a strict template engine (Liquid-compatible semantics are
sufficient)" fixes the failure semantics and nothing about the surface a template is written
against. An implementation choosing a different delimiter set conforms, and every `WORKFLOW.md` in
existence stops rendering on it.

**2. Filters.** "Unknown filters MUST fail rendering" is normative, and no section names a single
filter. The rule presupposes a table the document never states, so what counts as *unknown* is
whatever the implementation registered. `grep -n "filter" SPEC.md` returns thirteen sites at
`a4048bc`; none names a filter.

**3. `attempt` on a first run.** Section 4.1.5 says `attempt` is "(integer or null, `null` for first
run…)"; Section 5.4 says "`null`/absent on first attempt"; Section 12.1 says "OPTIONAL `attempt`
integer"; Section 12.3 says "first run (`attempt` null or absent)". Three of four admit *absent*,
and under strict variable checking absent means the run fails.

**4. An unknown member of a known object.** `{{ issue.assignee }}` — the singular typo for
`assignees` — is an unknown *field* of a known *variable*. Section 5.4 fixes the behavior for an
unknown variable and says nothing about this.

**5. What a timestamp prints.** Section 4.1.1 types `created_at`/`updated_at` as `timestamp`.
Section 4.2 defines no timestamp normalization — its five entries are the identifier and case rules
— and Section 11.3 fixes only the input side, "`created_at` and `updated_at` -> parse ISO-8601
timestamps". What `{{ issue.created_at }}` yields is unstated.

## Measured

**The corpus is already stricter than the specification it tests.**
`conformance/vectors/prompt-rendering.json` is `Daemon Conformance` and every `template` field in it
is Liquid source, so an implementation that satisfies Section 5.4 with a different syntax fails the
corpus today. The corpus also records the divergence it had to route around, in its own description:
"Templates are single-line and use delimiters rather than inter-token whitespace so the expected
output does not depend on an engine's whitespace-control behavior." That sentence is the measurement
that matters — the corpus found the unstable part of Liquid by hitting it, and the stable remainder
is the subset this decision states.

Of ten vectors, **none uses a filter** except `unknown-filter-fails`, whose filter (`screaming`) is
deliberately unknown. The portable surface the corpus exercises already has no filters in it.

**The one implementation answered all four open questions, and the specification made none of
them.** `symphony-rs` at `ee74fe7`, `crates/symphony-prompt`:

- Engine: `liquid = { version = "0.26.11", default-features = false }` with `liquid-lib = "0.26.11"`
  (workspace `Cargo.toml`). The same version decision 0102 measured for parse-time filter resolution
  and decision 0135 measured for randomized hash iteration order.
- Filters: none. The crate's own header states it as a property held by construction — "The `date`
  filter and the partial-reading tags are absent from the registered set (`parser`), and `liquid`'s
  `stdlib` feature is off in the manifest so `with_stdlib()` does not exist to be reached for by
  accident." The reasoning given is Tier 0 determinism — "No clock, no I/O, no randomness" — not
  portability. The implementation and this decision arrive at the same filter set from unrelated
  premises, and nothing in `SPEC.md` connects them.
- `attempt` on a first run: `a_first_attempt_renders_the_null_rather_than_failing` asserts
  `render_prompt("Attempt [{{ attempt }}].", &fixtures::issue(), None) == Ok("Attempt [].")`. The
  test's name is the finding: the implementation had to decide, and decided.
- Nullable issue fields: `an_absent_issue_field_renders_the_null` asserts `[][][][][][]` over
  `description`, `priority`, `branch_name`, `url`, `created_at` and `updated_at` — the
  generalization to Section 4.1.1's nullable fields, made by an implementation from a specification
  that discusses only `attempt`.
- Unknown member: `an_unknown_field_of_a_known_object_fails` asserts that `{{ issue.assignee }}`
  fails with `ErrorClass::TemplateRenderError`, and says outright that this is beyond the contract —
  "The variable set is closed, which `§5.4` does not require and which is the behaviour to want."
- Timestamp: `a_timestamp_renders_as_milliseconds_since_the_epoch` asserts `1770000000000`, with
  "`§4.1.1` fixes no rendering for one and this build publishes this one (`SPEC §19`)". The
  implementation routed the gap to the Conformance Statement, which is the correct response to an
  `Implementation-defined` obligation — except that `SPEC.md` creates no such obligation here, so
  nothing would have told a second implementation to publish anything.

Four gaps, four judgments, all sound, none of them the specification's. A second implementation
reading the same text could choose `template_render_error` for a first-run `attempt`, empty text for
`issue.assignee`, and RFC 3339 for a timestamp, and be conformant. The same `WORKFLOW.md` would then
render three different prompts across two conforming implementations, one of which is a failed run.

## Why this is the same argument decision 0160 made

Decision 0160 refused to leave `WORKFLOW.md`'s discovery `Implementation-defined`, "because a
repository author writes the file without knowing which implementation will run it and needs to know
whether an edit is honored, and because it converts a checkable property into an asserted one."
Discovery decides whether the file is read. Syntax decides whether reading it produces a prompt or a
failed attempt. The argument is the same one and it is stronger here, because the failure mode is
not "the edit was ignored" but "the run failed on a construct that worked on the author's machine".

## Options considered

- **Option A — a REQUIRED minimal subset, stated in Liquid spelling, with everything beyond it
  implementation-defined and documented.** Trade-offs: pins exactly what the contract needs and no
  more, so a repository author has a surface they can rely on and an implementation keeps room to
  offer more. It costs a new normative surface to maintain: a subset is a thing that can be
  under-specified in its own right, and every construct in it needs a vector or it is back to being
  asserted.

- **Option B — mandate Liquid outright.** Trade-offs: it is the simplest sentence, it matches the
  corpus exactly, and it matches the one implementation. It is not a foil — if "Liquid" named a
  single normative artifact this would be the right answer, and the edit would be one line. It loses
  on measurement: there is no such artifact. `liquid` 0.26.11 rejects an unknown filter while
  parsing where the reference implementation rejects it while rendering (decision 0102 measured
  exactly this and had to re-state Section 5.5 around it), and iterates a hash in a randomizing
  hasher's order where the reference iterates in insertion order (decision 0135, three orders across
  six runs of one binary). The corpus has already had to write around Liquid's whitespace control. A
  MUST to "render Liquid" would be a MUST against a target that two of this repository's own
  decisions were spent discovering the edges of.

- **Option C — keep the floor and add only the missing obligation: `Implementation-defined` syntax,
  MUST document, Conformance Statement row.** Trade-offs: honest, small, and it ratifies what
  `symphony-rs` already did for the timestamp. Against it: it documents the divergence rather than
  removing it, and documentation does not help the party that needs help. The Conformance Statement
  is read by "a consumer, auditor, or peer implementation" (Section 19); the repository author
  writing `WORKFLOW.md` is none of the three, and their file has to render on a deployment they may
  never see. It also leaves the corpus asserting more than the specification requires, which is the
  state that produced these findings.

- **Option D — close the four value questions and leave the syntax open.** Trade-offs: it fixes the
  four instances that were measured and is a much smaller edit. It loses because the instances are
  not the defect: they are what fell out of one implementation being read for an afternoon. The
  syntax question is the one that generates them, and answering the children while leaving the
  parent is what `conformance/README.md` has now recorded four times in other sections.

## Decision and reasoning

**Option A.** The prompt template's rendered output is a contract between a repository author and
whichever implementation renders it, and `SPEC.md` states it.

- **A REQUIRED minimal subset**, in Liquid spelling: `{{ path }}` interpolation with dotted member
  access; `{% for x in seq %}…{% endfor %}` over a list and over a map; two-element key/value pair
  indexing for a map entry, which Section 12.2 already requires and which `iterate-metadata-map`
  already spells as `kv[0]`/`kv[1]`. Anything beyond it — whitespace control, conditionals,
  assignment, additional tags — is `Implementation-defined`, MUST be documented, and a `WORKFLOW.md`
  using it is not portable.

- **No portable filters.** The subset defines none. An implementation MAY offer filters and MUST
  document those it offers; a template using one is outside the portable surface. Section 5.4's
  "Unknown filters MUST fail rendering" is kept and now has a table to be unknown against: the empty
  one, in the portable subset.

- **`attempt` is bound and null on a first run.** Strict variable checking is a rule about unknown
  *names*, and `attempt` is a name Section 12.1 defines, so it is never unknown. "absent" and
  "OPTIONAL" leave Sections 5.4, 12.1 and 12.3, aligning them on Section 4.1.5's existing wording.

- **A bound null renders as the empty string**, stated over every nullable value the template
  context carries rather than over `attempt` alone — Section 4.1.1's six nullable fields and its
  blocker-ref fields included.

- **The issue object's member set is closed to Section 4.1.1's fields.** Naming a member outside
  them is `template_render_error`. `metadata` is carved out: it is adapter-owned and open by
  definition (Section 4.1.1), so member access under `metadata` stays permissive and a missing key
  there is a bound null.

- **A timestamp renders as RFC 3339 in UTC.** The form Section 11.3 already parses.

Three consequences are stated rather than left derivable:

- **The closed member set is already mechanized.** `scripts/validate_spec_consistency.py` check 7
  compares Section 4.1.1's field bullets against `iterate-issue-object`'s supplied and expected
  keys, so the set this rule closes over is the set a check already holds to Section 4.1.1. The rule
  adds a consumer for a property the corpus was already enforcing.
- **Closing the member set is what makes the null rule safe.** Under an open member set a misspelled
  field and a genuinely null one both render empty, so the null rule would erase the only signal a
  prompt author has that they mistyped. The two rules are one decision: empty means null, and a name
  that is not a field is an error rather than a null.
- **The timestamp choice is load-bearing on the filter choice.** With no portable filters, an author
  handed `1770000000000` has no portable way to make it a date. RFC 3339 is the only rendering that
  leaves the value usable in the artifact it exists for — a prompt read by a coding agent. The `_ms`
  convention elsewhere in the document governs durations and monotonic instants in configuration and
  runtime state, which are read by implementations rather than printed into prose.

**Obligations created.** The syntax beyond the subset, and the filters an implementation offers, are
`Implementation-defined` and MUST be documented, so `CONFORMANCE-STATEMENT-TEMPLATE.md` owes rows.

**Reconsideration triggers.**

- A second implementation whose engine cannot express the subset — most plausibly the map-entry pair
  indexing, which is the one construct that is Liquid-shaped rather than universal. That is evidence
  for restating the subset over a neutral iteration form rather than for reopening the floor.
- A repository author reporting that the portable surface is too thin to write a real prompt in —
  specifically, a prompt that needs a conditional. `{% if %}` was deliberately left out because
  nothing in the corpus or the specification needs it, and it is the first thing to add if that
  turns out to be wrong.
- An agent runner that consumes a timestamp rather than reading it, which would make the epoch
  integer the useful rendering after all. The argument above turns on the prompt's reader being a
  language model.
- A tracker whose `metadata` keys collide with Section 4.1.1 field names, which would make the
  carve-out ambiguous at the point where the two member sets meet.

## What the plan review changed (2026-08-28)

Running `python3 scripts/check_plan_anchors.py` on the plan before its first edit found one
conflated quotation, one site the plan had not reached, and one site it had to say it was *keeping*.

- **A quotation assembled from two documents.** The step restating
  `conformance/vectors/prompt-rendering.json`'s description quoted it as saying "in Liquid syntax…
  and an engine that is not Liquid-compatible maps these to its equivalent". The second half is the
  file's; the first is `conformance/README.md`'s open finding, which says "the slice authors the
  reference vectors in Liquid syntax". The step now quotes the file's own words and names the
  README's separately, which matters because the two are rewritten by different steps.
- **A site the plan had not reached, in the file it was already editing.** `conformance/README.md`'s
  harness contract describes `render_prompt` with "Templates use Liquid-compatible syntax (Section
  5.4)" — a floor, stated where a harness author meets the function rather than in the findings
  section the plan was rewriting. It gained its own step. This is the same lens decision 0161's
  review applied to Section 14.5: the plan reached every site that argued the decision and missed
  the one where a reader would look for the answer.
- **A site that has to survive, recorded as such.** Section 5.4's "Liquid-compatible semantics are
  sufficient" is quoted by `conformance/README.md`'s *resolved* decision-0135 entry. Had the subset
  step removed the phrase rather than adding a surface beside it, that entry would have gone stale —
  a finding recorded as closed citing prose that no longer exists. The plan now states that the
  phrase survives and why, in `Sites checked, no change needed`.
- Two `Sites checked` bullets quoted `SPEC.md` without naming it, so the checker bound Section
  4.1.5's and Section 11.3's text to `conformance/README.md`. Both now name their document.

## What applying the plan repaired (2026-08-28)

Applying step 9 — adding "a member of the `issue` object outside the field set Section 4.1.1
defines" as a fourth `template_render_error` condition in `SPEC.md` Section 5.5 — found a site the
plan's `Scope` did not name: `conformance/vocabulary.json`'s `error_classes` registry restates the
same condition list under its own `template_render_error` entry ("an unknown variable, an unknown
filter, or an invalid interpolation"), and that restatement is free text. `check_registries`
(`scripts/validate_spec_consistency.py`) only pulls a registry entry's `token` field into what it
checks against `SPEC.md`; `condition` is prose no check reads, so the registry would have kept
naming three conditions for a class Section 5.5 now names four for, and nothing in the corpus's own
validation would have caught the drift. The entry's `condition` now names the fourth one too, citing
Sections 5.4 and 12.2 as Section 5.5's own parenthetical does. The shape matches the plan review's
earlier finding at `conformance/README.md`'s harness contract: a restatement living beside the
function or registry entry a reader meets first, one hop from the section the step was written
against.

## What reviewing the Statement rows changed (2026-08-28)

`scripts/validate_spec_consistency.py` check 2 errors only on a section with obligations and
**zero** rows, and warns on a count shortfall. It cannot tell whether a row asks the question its
obligation answers, and the script says so in its own stated limits. Reading the four rows this
decision and 0162 add against the obligations they cite found one thin.

The filters row asked `<filter names, or none>`. A name is not what the obligation is for. Section
19 exists "so a consumer, auditor, or peer implementation can determine what the implementation does
without reading its source", and a peer reading `truncate` learns that a name exists, not its
semantics or its arity. The row this one was modelled on — "Workflow/template error classes defined
beyond Section 5.5's five" — asks for "token + dispatch gating behavior for each", a name *and* what
it does, and the filter case needs that more rather than less: a filter is a construct a repository
author **invokes**, so the Statement is what tells them whether `{{ x | truncate: 20 }}` runs and
what it produces. The row now asks for the name, what each filter does, and the arguments it takes.

The other three stand. The tracker row asks for a token and a condition, which is the shape Section
11.4's own entries and the registry's `condition` field already carry. The constructs row asks which
constructs are supported, which is the whole of that obligation. The agent-runner row asks for a
token and a condition where Section 10.6's nine entries are bare tokens and `agent_error_categories`
models no `condition` — an inconsistency recorded rather than repaired, because asking a condition
of a newly defined token is the better question and the mismatch is in Section 10.6's presentation
of its own nine, which this decision does not touch.
