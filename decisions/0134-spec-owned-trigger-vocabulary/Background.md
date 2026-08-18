# Background — 0134 A vocabulary two documents closed and one left the engine to extend

## Context

There were no open issues to work from: all 54 on `mattiasgronlund/symphony` were closed as
completed, #81 and #82 having closed when PR #87 landed. A fresh consistency review was run instead.
`scripts/validate_spec_consistency.py` stood at 0 errors and 3 warnings, and all three warnings had
already been investigated and recorded as non-gaps in `decisions/0132-derived-artifact-drift/Plan.md`.
The review therefore aimed at what the mechanical checks structurally cannot see — one document
against another, and prose against prose — and found three defects plus one derived-artifact
omission, filed as #88, #89 and #90.

### 1. The policy-visible trigger vocabulary is closed in two documents and open in the third

`VCSX-CONTRACT.md` Section 5.1 gave the lifecycle positions as a closed list of four with no escape
clause, and Section 7 called them "the fixed points". `SPEC.md`'s action-policy passage listed the
same four, closed, and named all eleven operations. `VCSX-SPEC.md` disagreed in three places:
Section 4.1 said "An engine MAY define additional operations and their `before:<op>` positions",
Section 5.1 wrote "(and any engine-defined `before:<op>`)" into the definition of a trigger, and
Section 6.11 judged `position_cycle` over "the `before:<op>` positions the engine defines".

The difference is observable rather than editorial. Section 6.11 refuses an edge whose `on` is not a
trigger the engine recognizes, with `unknown_trigger`, so a `repo.policy.toml` keyed on an
engine-defined position — or on an engine-defined operation's `<op>:<reason>` result — validates on
engine A and is refused on engine B, both conforming. That is what `VCSX-CONTRACT.md` Section 2 says
the contract exists to prevent: conformance is to the contract, not to a specific binary.

Nothing disclosed the extra vocabulary either. Section 13.3 required only the *backend capabilities*
an added operation needs, never the operation's own name or the position it introduces, so a
consumer holding two Conformance Statements could not read the two vocabularies out of them. That
was the sole gap in an otherwise complete pattern: an added reason token, an added configuration
reason and an added precondition reason each carried a MUST-document obligation *and* a template
row. The one addition that changes which policies validate was the one that was invisible.

### 2. `VCSX-CONTRACT.md` Section 6 was short three operations

It opened "Named operations **include**:" and listed eight. Section 4.1's set is eleven. `status`,
`diff` and `pull` were absent from the document whose Section 1 claims to fix "the engine operations
and their typed results" and whose Sections 1 and 12 require names identical with `SPEC.md` — which
names all eleven. `status` and `pull` were both reworked in the engine spec, by #69 and #8, without
the contract's list moving; the word *include* is what let it happen quietly, because an open list is
never wrong. The contract's only occurrence of the token `status` was the task model's field, so
grepping for it found an unrelated concept and reported a hit.

### 3. `VCSX-SPEC.md` Section 4.3 said "none of the four" where five qualify

It listed `integrate`, `pull`, `status` and `diff` as carrying neither `blocked` nor
`hook_unanswered`, while Section 4.1 states twice that `await_checks` is gated at no fixed position,
and `provision` carries none for the reason its own entry gives. The Section 4.3 registry already
carried exactly five `await_checks` rows with neither gate reason among them, so only the counted
prose was wrong — the third instance of this shape in as many decisions (0131, 0132, 0133), and the
fifth overall.

### 4. The registry published ten operations and omitted `load_policy`

`conformance/vcsx/vocabulary.json` carried ten `operations` entries. Section 4.1 defines eleven, and
the registry's own `entry_points` group already listed `load_policy`. Check 4 walks registry → prose
only: it errors when the registry publishes a token the prose lacks and never the reverse, so this
direction of drift was invisible to every check the repository had. It was filed as a note inside
#89 rather than as a fourth issue — the same enumeration, one artifact over.

## What the defects share

Findings 2, 3 and 4 are one shape: a set fixed in one place and restated in another, where the
restatement is complete against itself. Finding 1 is what makes the shape matter — the set in
question is the one a repository writes its policy against, so a disagreement about its membership
is a disagreement about which policies run.

## Options considered

### On finding 1: extend-and-disclose, or close the set

- **Minimal — keep the extension, close the disclosure gap.** Require an engine to document the
  operations and positions it adds and give `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` a row for them.
  This is the shape every other engine-added token already has, so it is the change with the least
  argument behind it. Trade-off: the observable divergence survives untouched. The policy still
  validates on one engine and is refused on the other; a consumer merely gets to read that in
  advance, from two documents it must obtain and compare.
- **Maximal — the operation set and the position set become spec-owned and versioned.** Extensible
  by a MINOR release of `VCSX-SPEC.md` Section 8.5 and never by an individual engine. Trade-off: an
  engine with a genuine extra operation now needs a specification release rather than a
  documentation line, which is a real cost paid by whoever holds that case.

**The maximal reading won**, because the minimal one documents a divergence rather than removing it,
and the thing it would document is the one a consumer cannot route around: `unknown_trigger` is a
refusal to run, so a policy that is portable in principle stops being portable in fact. Closing the
set turns `unknown_trigger` into a statement about a policy — a defect in the file — rather than a
statement about which engine is underneath. The cost is bounded by the extension route still
existing: a MINOR adds an operation or a position, so nothing is impossible, only versioned.

That a MINOR may add a *position* where it may not add a trigger **kind** or a key component is
Section 8.5's own argument run in the opposite direction. Its second bullet reasons from what a
repository can observe: a `MINOR` that added a kind or a key component would change which edge fires
for a policy whose text did not change. An added position cannot do that, because a policy keyed on
a position the running version does not define was already refused with `unknown_trigger` — there is
no previously-firing edge to move. A *removal* is the other half of the same shape, leaving an edge
that validated and never fires, and stays MAJOR.

### Follow-up fork A: does the *position* set close too, or only the operation set?

Closing the operation set alone would have been enough for finding 2, and positions could have been
argued to be the engine's business because a position gates the engine's own dispatch. **Both close.**
A position is half of the trigger vocabulary a `repo.policy.toml` is keyed on, and Section 6.11
refuses an unrecognized position with the same `unknown_trigger` it refuses an unrecognized result
with. Closing one half would have left the portability claim true of results and false of positions,
which is worse than leaving it uniformly false: a consumer would have to know which half of its
policy is portable.

### Follow-up fork B: is the reverse prose→registry check part of this decision?

Finding 4 could have been repaired by adding `load_policy` and stopping — the registry would then be
correct, and the class of drift would remain undetectable. **The check is added.** Finding 4 is the
fourth artifact in four decisions to drift in exactly this direction, and the argument decision 0132
made for check 4 applies unchanged to its mirror: an artifact complete against itself is where a
missing member hides, and the missing member is invisible precisely because nothing looks for it.
The check is deliberately **narrow** — a table of two groups, `operations` and `lifecycle_positions`
— because closedness is a property of the prose that no general rule reads off it, and a group the
table does not name stays unchecked in that direction, as every group was before this decision.

### On the Section 14.2 warning: repair the document, or the detector?

The warning has stood since decision 0132, which checked it by hand and recorded it as a non-gap:
the fourth obligation is `node_provisioning_failures`' park-versus-retry choice, rowed under Section
9.11, the extension that defines it. **The validator is fixed rather than the document**, because
the document is right — the obligation belongs to the extension, and the template files it there.
What was wrong was `covers()` matching only downward, so a row citing `9.11` could not answer an
obligation the checker had filed under `14.2`. The repair **re-homes** the obligation rather than
aliasing the two sections: scanning back to the enclosing column-0 bullet and reading its
"OPTIONAL extension, Section N.M" declaration attributes the obligation where the template already
puts it, and leaves `covers()` as tight as it was. The Section 6.6 warning is the same judgment on a
different mechanism: an obligation inside a fenced example is a restatement by construction, so
fenced regions are excluded rather than the example being reworded.

## Recorded, not repaired

- **`VCSX-SPEC.md` Section 4.3's universal claim does not hold for `load_policy`.** Section 4.3 says
  "Every operation therefore has at least one `done` reason and at least one `error` reason", and
  `load_policy` has none: Section 4.1 routes its four failures to Section 6.1's configuration
  reasons. This predates the decision — `load_policy` has been an operation with no registry rows
  since it was introduced — and adding it to the registry's `operations` group makes the asymmetry
  visible where it was previously only true. It is left alone because repairing it means deciding
  whether `load_policy` gains reason tokens or Section 4.3's sentence gains an exception, which is a
  decision about the operation rather than about the vocabulary this one closes.
- **`conformance/vcsx/vocabulary.json`'s `reasons` note is short one operation.** It says the two
  `(any forge)` rows "expand to one entry per operation whose forge call the condition prevented —
  `push`, `create_pr` and `merge`", where Section 4.3 names four and the registry's own entries
  carry four, `await_checks` included. This is finding 3's shape again, one artifact over. It is not
  repaired here because a sweep for further instances of that class is out of scope by the same
  reasoning decision 0133 used: the general case is open, and a dedicated pass is a decision of its
  own rather than a rider on this one.
- **`VCSX-SPEC.md` Section 8.4's residual warning** — 2 obligations, 1 row. The second is the `need`
  vocabulary's own spec-level stability clause rather than an engine choice, and the template
  answers it with a whole section whose heading carries no citation to count. Recorded as a non-gap
  in 0132 and carried forward in this decision's `Plan.md`. No detector is worth writing for it: no
  general rule separates a spec-level MUST-be-documented from an implementation one.

## Reconsideration triggers

- **An engine with a real operation the specification does not have.** The maximal reading's cost is
  paid by whoever holds that case, and it has no holder today. A concrete one — an operation a
  backend family needs and the spec cannot generalize — is the argument for reopening fork A, most
  likely as a namespaced extension vocabulary rather than as a return to the open set.
- **A MINOR that adds a position and finds the argument does not hold.** The claim that an addition
  cannot change which edge fires rests on an unknown position being refused at validation. A future
  matching rule that made an unrecognized position a no-op instead would break it and make an added
  position MAJOR after all.
- **A third group that wants check 6.** Two entries is a table; a third is the point at which a
  per-group notion of closedness is worth stating in the corpus rather than in the checker.
