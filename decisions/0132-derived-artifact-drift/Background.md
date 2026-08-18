# Background — 0132 Nine derived artifacts, and the enumerations they drifted from

## Context

There were no open issues. A review pass was run instead, over the artifacts this repository derives
from its specifications: the two token registries, the two Conformance Statement templates, the
config cheat sheet, and the cross-references. Seven defects, filed as issues #83 (registries), #84
(template rows) and #85 (naming and citation). The checker this decision adds found two more before
it was finished, so nine are repaired here; the two it found are recorded below rather than filed,
having been fixed in the same change that found them.

Every one has the same shape. A specification sentence enumerates something — the token sets the
registry publishes, the obligations a Statement records, the namespace a config key lives in, the
section a claim rests on — and a second artifact restates that enumeration. The two disagree, and
nothing notices, because each artifact is complete against itself.

That shape is not new here. Decision 0128 exists because three decisions in a row added an
`Implementation-defined` obligation and no template row; decision 0103's `Background.md` counted four
bullets that went stale, "twice inside the decisions repairing it"; decision 0131 swept a whole file
rather than answer its one report, for the same reason. This is the fourth time the class has been
found by a person reading, and the reason a checker is part of this decision rather than a follow-up.

## What the defects do

### The registry is short by three, and by two more

`SPEC.md` Section 17 states what the registry carries as a closed list of ten token sets.
`conformance/vocabulary.json` carries thirteen groups. The three it does not name —
`event_envelope_fields`, `token_usage_fields`, `runtime_state_fields` — are not strays: all three are
in `conformance/README.md`'s "What the slice covers" table, sourced to real sections (10.4;
4.1.6/10.7/13.5; 4.1.8/14.3), and `runtime_state_fields` is named in that file's reader list as the
group **a Conformance Statement author reads for the "Spec default" column of its recovery-class
table**. So the registry and its README agree with each other, and the specification sentence that
governs both is the one that fell behind. That settles the direction of repair, which the derived-view
rule alone would have decided the other way.

Two further sets are named by neither. Section 19 requires a Statement to record

> The layer profiles claimed and the deployment topology provided, by the names Section 3.4 and the
> Section 17 validation profiles define (`Broker Core Conformance`, `Daemon Conformance`;
> `engine-direct`, `interactive-agent`, `daemon`).

"By the names … define" is the registry's trigger condition stated in the specification's own words.
And the reader is the one decision 0103's test names explicitly — "a Conformance Statement author
filling a table" — not an inference from it. `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 1 is that
table.

The failure is the one 0131 described, on a worse field. An implementation generating from the
registry gets a type for the transition triggers and nothing for the profile it claims, so it
hand-writes the string that says what it is claiming conformance to. A rename upstream diverges in
silence in the one field a reader consults to decide what the implementation asserts about itself.

### The engine registry publishes two names no document backs

`conformance/vcsx/vocabulary.json` publishes `task_model.fields` as six tokens, the last two spelled
`parent` and `tracker_link`. `VCSX-CONTRACT.md` Section 8 names four as tokens and the last two in
prose — "optional parent task", "optional tracker link" — and `VCSX-SPEC.md` matches. Neither string
appears in either document.

This is worse than the disagreement the derived-view rule resolves, and the rule is the reason:
"a disagreement is a bug here" presumes there is something to disagree *with*. Here a generator emits
two field names with no upstream, and the check built to catch divergence has nothing to compare
against — it cannot report red, and it cannot report green either. It reports nothing.

### Seven obligations a Statement has no room to answer

The templates are what a generator parses and what an implementer fills. An implementer who fills one
in and finds no gap has a complete Statement by the only test available to them.

Five Symphony obligations have no row: the composed environment set (Section 9.6), the per-issue
target carrier (Section 9.7), how no other write route to the policy branch is established and how a
host-side unit is resolved (both Section 15.4), and the aggregation sink and retention (Section 13.5).
Two engine obligations have no row: the bound a forge backend imposes on its pull-request search
(`VCSX-SPEC.md` Section 9.2) and `worktree_revision()`'s form and derivation (Section 9.1).

Two of the seven are provable against the documents' own closing sentences rather than against a
reading of them:

- Section 19 enumerates "the composed environment set an agent receives (Section 9.6)" and closes:
  "`CONFORMANCE-STATEMENT-TEMPLATE.md` … enumerates each obligation above as a row an implementation
  fills." It does not.
- `VCSX-SPEC.md` Section 13.3 enumerates "any bound a forge backend imposes on its search for a work
  branch's pull request (Section 9.2)" and closes with the same claim. It does not.

The other five are missing at both layers — the enumeration and the row — so the repair is two edits
each, and the enumeration is the one that matters: a template row added without the Section 19 clause
above it is the same drift, laid down fresh.

What goes unanswered is not incidental. Section 15.4's first obligation is the trust root of the
entire host-side hook category: how a deployment establishes that no route other than the two the
specification closes can write the policy branch. A Statement that never asks it is a Statement whose
reader cannot tell a protected branch from an unprotected one.

### A key spelled the one way its own rule forbids

Section 5.3.4 fixes the namespace and says why: "The namespace is `hooks.workspace` rather than
`hooks` … Prefixing them is what keeps a lifecycle point and a named unit of the same name from
colliding, and what stops a loader having to infer which schema owns an entry from whether it is a
scalar or a table." Section 6.4's cheat sheet follows it.

Section 9.4 — the section an implementer builds the hook layer from — lists `hooks.after_create`,
`hooks.before_run`, `hooks.after_run`, `hooks.before_remove` and takes its timeout from
`hooks.timeout_ms`. Section 18's checklist, the definition of done, repeats `hooks.timeout_ms`.

The collision is not hypothetical: `hooks.engine.<name>` is a live sibling namespace whose entries are
tables where these are scalars, and a loader built from Section 9.4 is exactly the loader Section
5.3.4 says must not have to guess.

### A citation to a section that does not exist

Section 9.7 sources the `target_branch` base-resolution consequence to "`VCSX-CONTRACT.md`, Section
15.4". That document has twelve numbered sections, and the strings `policy_source` and
`target_branch` appear in it zero times — it is the deferral layer, and this is one of the things it
defers. The claim's home is `VCSX-SPEC.md` Sections 6.4 and 8.1, the ground issue #51 covered.
`SPEC.md` has its own Section 15.4, which is the likely origin of the slip: the right number against
the wrong document.

## Measurements

Python 3.13.5, run from the repository root. Each is the check that found the defect, and each is now
in `scripts/validate_spec_consistency.py` so a later reader re-runs it rather than trusting this.

**Registry entries with no upstream in the governing document** — one hit, and it is the whole of the
`task_model` finding:

```sh
python3 -c "
import json
d = json.load(open('conformance/vcsx/vocabulary.json'))
spec = open('VCSX-SPEC.md').read() + open('VCSX-CONTRACT.md').read()
for k, v in d['task_model'].items():
    if isinstance(v, list) and k != 'spec_refs':
        miss = [e for e in v if isinstance(e, str) and e not in spec]
        if miss: print(k, '->', miss)
"
```

```text
fields -> ['tracker_link']
```

`tracker_link` alone, because `parent` occurs in `VCSX-SPEC.md` as an English word — "re-parents a
commit", eight times. A substring check is what a registry-versus-prose comparison can honestly do,
so it under-reports, and the second name was found by reading the cited section rather than by the
tool. That limit is recorded in the checker and is the reason its failure is a warning to be read
rather than a count to be trusted.

**Cross-document section references that do not resolve** — one hit, `SPEC.md:1845`. Within-document
references resolve everywhere in all three files; the two apparent hits are a citation of the Unicode
Standard's Section 3.13 and a legitimate reference to `SPEC.md` Section 15.4 from `VCSX-SPEC.md`.

**Config keys used outside the cheat sheet** — six hits, five of them the `hooks.` finding and one
(`server.port`) correct, being an OPTIONAL extension field the cheat sheet says it excludes by design.

**Obligation sites against template rows** — 29 `Implementation-defined` and 14 "MUST document" sites
in `SPEC.md`, 23 and 12 in `VCSX-SPEC.md`, resolved to their enclosing sections and matched against
the Section column of each template's obligation table. Five and two respectively with no row.

## Two more the checker found, which is the argument for having built it

The seven above were found by a person reading. The checker was written to stop the eighth. It found
the eighth and the ninth before it was finished.

**`SPEC.md` Section 5 cites `VCSX-CONTRACT.md` Section 3.4**, in the sentence "Symphony consumes it
through the VCS engine contract (`VCSX-CONTRACT.md`, Section 3.4)". That document's Section 3 has no
subsections; the target is Section 4, "`repo.policy.toml` (Config Surface)", which is what the
sentence is about. Same defect as the Section 9.7 citation, in the same document, and the review pass
missed it — the pass caught the one whose surrounding prose read oddly, and this one reads fine.

**Section 14.3 requires the reset consequence of every `Ephemeral` field to be documented** — "for
example, retry backoff restarts from the first attempt" — and the template had nowhere to record it.
Three fields carry that class by default. This one surfaced in the *warning* tier rather than the
error tier: Section 14.3 had rows, just fewer than it had obligations, which is precisely the case a
zero-row check cannot see and the case a reviewer's eye slides over.

That is the measurement this decision rests on. Two of nine instances were invisible to a careful
person reading for them, in a sweep whose entire subject was this defect class, and both fell out of
a check in under an hour. It is also why the warning tier stays: had it been dropped for producing
noise, the ninth would still be open.

## Options considered

### The scope of the decision

**Option A — one decision naming the class, repairing all seven, and adding a checker.** Chosen.

**Option B — three decisions grouped by artifact, no tooling.** The steelman, and it is the repo's
established rhythm: each finding gets its own `Background.md`, the reasoning stays close to the
artifact it concerns, and the PRs stay small enough to review in one sitting. It also avoids adding a
second script to a repository whose `CLAUDE.md` says there is nothing to build or test yet.

It loses on the recurrence, which is the fact this decision turns on. Three groupings produce three
records of three symptoms and no record of the disease, and the disease has now been diagnosed four
times by four people reading carefully. The next instance will be found the same way — or not found.
`scripts/validate_workflow_bundle.py` is the precedent that settles the "no tooling here" objection:
this repository already ships a validator for its own scaffolding, and this is the same kind of thing
pointed at the artifacts that carry normative content.

**Option C — repair what is wrong as written and defer the completeness gaps.** Rejected on the
sheet by the choice to take all seven, and it would have deferred exactly the two findings (the
missing template rows) whose whole failure mode is that nobody notices them.

### The direction of the Section 17 repair

**Extend the enumeration to name all thirteen.** Chosen, and it is the reading the artifacts support:
`conformance/README.md` already covers all thirteen and names a Conformance Statement author as
`runtime_state_fields`' reader, so the three groups have a documented purpose and a documented reader.

**Drop the three groups.** The steelman is the registry's own words — "a disagreement is a bug here"
— and it is a rule worth defending, since a registry that grows a group whenever one seems useful is
the inventory decision 0103 declined to build. It loses because the rule allocates *authority*, not
*direction*: it says the specification decides what is true, not that the prose list is always the
current one. Applied mechanically here it would delete the group a Statement author is documented as
reading, to satisfy a sentence that predates it.

### Whether the layer names are a token set

**Not published.** `Broker Core`, `VCS Engine` and `Autonomous Daemon` are backticked in Section 3.4
and look like the same kind of thing as the profiles. They are not: Section 19 makes a Statement
record "the layer profiles claimed and the deployment topology provided", and the profile names —
`Broker Core Conformance`, `Daemon Conformance` — are the strings that appear in the table. No reader
outside an implementation's own source spells the layer name, so under 0103's test there is no
divergence to catch. This is the verification 0131 recorded as its most useful finding, run again: a
plausibly-matching set, checked against what actually reads it, and declined.

### The spellings for the two task-model fields

**Fix them in the documents.** Chosen. Section 8 backticks four of six fields and writes the other two
in prose because it was describing *optionality*, not because the names are open — the list is one
list. Making them tokens is the smaller change and leaves the registry deriving rather than leading.

**Drop them from the registry.** The steelman, and it has a real argument: the registry's own note says
"the task model is the consumer's; the engine consumes only the resulting task-state events", so the
engine documents arguably should not fix these names at all, and publishing them is the registry
leading — which `conformance/vcsx/README.md` names as its own trigger for moving a concept into
`VCSX-SPEC.md` instead. It loses on the other four: `id`, `description`, `status` and `assignee` are
already fixed as tokens on the same consumer-owned model, so dropping two would leave one list
published in two registers, and the boundary between them would rest on nothing.

### What the checker asserts

The four checks above, and deliberately not a fifth. An obligation-to-row check can only match on the
*section* an obligation sits in, so a section with three obligations and two rows is caught while a
section with one obligation and one row that answers a different question is not. That limit is
written into the script's docstring rather than left for a later reader to discover, and it is why the
checker's output is a report a person reads rather than a gate that certifies completeness.

## Findings recorded and not repaired

- **Section 9.7 claims a parallel obligation Section 9.8 does not carry.** "…is `Implementation-defined`
  and MUST be documented, as the `branch_name` hint's treatment is (Section 9.8)." Section 9.8 states
  only that "a tracker-provided `branch_name` is at most a hint" — no obligation. The 9.7 half is
  repaired here because it is one of the missing rows; whether 9.8 should gain the obligation the
  sentence attributes to it, or the sentence should drop the comparison, is a question about the
  hint's treatment rather than about template rows, and answering it inside this decision would be
  deciding a normative question under cover of a consistency sweep.
- **Seven registry groups carry no `requirement_level`**, though `conformance/README.md` instructs a
  reader to "read `requirement_level` first". The seven are the field-list groups. Assignable as it
  stands; folding it in would widen this decision from the enumerations to the group schema.
- **`hook_conditions`' first `spec_ref` still cites a stale section title**, recorded by 0131 and
  still open. Left where 0131 left it.

## Reconsideration triggers

- **Re-run `scripts/validate_spec_consistency.py` after any decision** that adds an obligation, a
  registry group, a config key, or a cross-document citation. A new hit is a new instance of this
  class.
- **Reopen the checker's obligation rule** if a per-section count ever produces a false pass that
  matters — the fix is to give each obligation a stable identity the row can cite, which is a change
  to both templates and worth its own decision.
- **Reopen the layer-name question** if a Statement, a config key, or a conformance check ever spells
  a layer name, which today none does.
- **Reopen the Section 17 direction** if the registry ever grows a group with no reader outside an
  implementation's own source; the answer then is 0103's test, not this decision's precedent.

Depends on 0103 (the reader test), 0051 (the registry and its derived-view rule) and 0128 (the
template-row rule this decision generalizes). Relates to 0131, whose sweep-rather-than-answer method
this follows, and to 0002, whose stable-anchor rule the citation repair applies.
