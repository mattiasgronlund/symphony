# Background — 0102 The enumerated error tokens as data, and a class that names its condition

## Context

Issue #54 reports that the five error classes Section 5.5 names have no group in
`conformance/vocabulary.json`, while `conformance/vectors/prompt-rendering.json` already asserts one
of them by name. That is one defect. Reading it against the sources, there are three, they fail
differently, and the one the issue raises last is the only one that breaks a correct implementation
today.

### The corpus measures a spelling the specification does not require

`prompt-rendering.json` states the contract in its own `description` — "an unknown variable and an
unknown filter MUST fail rendering with error `template_render_error`" — and two of its six vectors
assert `{ "error": "template_render_error" }`. It is the only MUST in that file that names a token.

Section 5.5 carries no RFC 2119 keyword at all. It says "Error classes:" and lists five. Section 5.1
spells one of them inside a behavioural rule — "If the file cannot be read, return
`missing_workflow_file` error" — and carries no keyword either. Section 17.1's four checks over these
conditions say "Missing `WORKFLOW.md` returns typed error", "Invalid YAML front matter returns typed
error", "Front matter non-map returns typed error", and "Prompt rendering fails on unknown variables
(strict mode)". Every one names the condition and no token, so every one is satisfied by any
spelling.

So an implementation is measured against a spelling the specification never asks for. That is the
derived-view rule of Section 17 running backwards: the corpus is supposed to be read *from* the
specification, and here it is the only artifact that fixes the token.

### The registry could not have carried the group anyway

The omission issue #54 reports was deliberate, and `conformance/README.md` says why, under "Deferred
to later slices":

> **Error and category codes** — the workflow/config errors (Section 5.5), the transport-neutral
> tracker error categories (Section 11.4), the brokered-result reason codes including `scope_denied`
> (Section 10.8), and the agent-runner error mapping (Section 10.6). Several are RECOMMENDED rather
> than REQUIRED spellings, which is a distinction the registry would have to carry per entry.

Decision 0071 also ruled that **the ruling belongs in the specification, not in the registry** — a
derived view cannot decide a property its source leaves open, which is why Section 10.4 gained its
`Note:` before the registry recorded `exhaustive: false`. The two together mean the registry gap is
*downstream* of the level gap: no group can be published until Section 5.5 states a level, and
publishing one without a level would be the registry deciding a question the prose left open.

The blocker as 0071 stated it is per **entry**. Deriving it shows it is per **group**: each of the
three sections states one level for its whole set, or would after this decision — Section 11.4 opens
"RECOMMENDED error categories", Section 10.6 opens "Error mapping (RECOMMENDED normalized
categories)", and Section 5.5 gains REQUIRED below. So the distinction costs one field per group
rather than a qualifier per token, and the slice is cheaper than the deferral assumed. That is not a
detail: a deferral whose stated blocker no longer holds is worse than no deferral, because the next
reader takes the reason on trust rather than re-deriving it.

### A class named by its condition, or by the pass that caught it

Section 5.5's five annotations are of two different kinds, and nothing says so:

- `template_parse_error` **(during prompt rendering)** — a *phase*.
- `template_render_error` **(unknown variable/filter, invalid interpolation)** — a *condition*.

The two mandatory strict failures of Section 5.4 need not surface in the same pass. A filter name is
resolved against the engine's own filter table, which is fixed before any data arrives; a variable
name is resolved against the render context, which arrives only at render. An engine with a
parse/render seam may therefore reject the unknown filter earlier than the unknown variable, and a
language-neutral specification cannot assume otherwise.

Measured, reproducing issue #54's report in a scratch crate (`liquid` 0.26.11, rustc 1.97.1,
`ParserBuilder::with_stdlib()`):

```text
  unknown-filter: PARSE  failed -> liquid: Unknown filter
unknown-variable: RENDER failed -> liquid: Unknown variable
       malformed: PARSE  failed -> liquid:  --> 1:6
```

The corpus expects `template_render_error` for both of the first two. That holds only if the class
names *what was wrong* rather than *which pass noticed*, leaving `template_parse_error` for the third
line — a body that is not well-formed template syntax at all. That reading makes Section 5.5 and the
corpus agree and is the one being implemented downstream; it is stated nowhere. Under the natural
misreading — parse-phase failure maps to `template_parse_error` — two of the six vectors in
`prompt-rendering.json` fail for an implementation that is otherwise correct, and nothing in the
documents tells its author they misread.

This is the sharpest of the three defects. The other two are drift risks that cost nothing today; this
one is a false negative in the corpus right now.

### Two things the derivation surfaced that this decision records rather than repairs

**Section 17.3 names four Section 11.4 tokens by name.** `tracker_unsupported_operation`,
`tracker_state_unreachable`, `tracker_state_conflict` and `tracker_pagination_error` all appear inside
`Core Conformance` checks — "an unsupported write surfaces `tracker_unsupported_operation` and is
never silently no-oped", "fails `tracker_state_unreachable` for an unreachable target, and
`tracker_state_conflict` on a concurrent state change", "a broken enumeration surfaces
`tracker_pagination_error`" — while Section 11.4 declares the whole set RECOMMENDED. It is the same
asymmetry as the corpus/Section 5.5 one, one section over and with the conformance profile attached,
so four of eleven RECOMMENDED spellings are in practice required of a conforming implementation. This
decision does not re-level Section 11.4; the finding is recorded in `conformance/README.md` because
the registry now publishes the level, and a reader comparing the group to Section 17.3 will find the
contradiction whether or not it is written down.

**Section 10.6 shares three spellings with Section 10.4.** `turn_failed`, `turn_cancelled` and
`turn_input_required` are each both an emitted runtime event the registry already publishes and a
normalized error category:

```sh
python3 -c "import json; d=json.load(open('conformance/vocabulary.json')); \
e={x if isinstance(x,str) else x['token'] for x in d['events']['entries']}; \
print(sorted(e & {'codex_not_found','invalid_workspace_cwd','response_timeout','turn_timeout', \
'port_exit','response_error','turn_failed','turn_cancelled','turn_input_required'}))"
```

→ `['turn_cancelled', 'turn_failed', 'turn_input_required']`. This is not a collision to repair: the
category is named after the event that produced it, which is the useful naming. But the registry
carried 59 tokens across 8 groups before this slice and will carry 84 across 11, and a generator
emitting one type per group now has three names in two enums. The relationship is stated in the
group's `note` rather than left for a code generator to trip over.

## Options considered

### Scope

**Option A — carve Section 5.5 out of the deferral alone.** Exactly what issue #54 asks for: one
`error_classes` group, and the deferral bullet narrowed to the other three sets. Its case is that the
issue names one set, one set is what the corpus measures, and a decision that changes only what is
demonstrably broken is the smallest reviewable unit. It loses because it leaves the deferral standing
on a reason that has just been shown wrong. The next reader of "a distinction the registry would have
to carry per entry" has no way to know it is per group, and the two remaining enumerated sets stay
deferred behind a blocker that costs one field.

**Option B — take the whole enumerated slice.** Chosen; reasoning below.

**Option C — fix the specification, leave the registry deferred.** The strongest of the three on
cost: Section 5.5 gains its level, its conditions and the condition-not-phase rule, Section 17.1
gains the tokens, and the registry gap becomes a fifth entry under `conformance/README.md`'s
"Surfaced findings" for a later decision that takes all four error sets at once. Everything that
breaks an implementation today is fixed, and the derivation work for Section 10.8 — which has no
enumeration to publish — is not forced by a decision that does not need it. It loses on the same
mechanism the whole registry exists for: with the level settled, the only thing standing between
Section 5.5 and a published group is the authoring, and deferring it leaves an implementation
transcribing five tokens by hand for the interval. Section 10.8 does not have to come along; it is
deferred here on its own reason, which is stronger than the one it inherits today.

### Requirement level

**Option D — REQUIRED for Section 5.5's five, Sections 11.4 and 10.6 unchanged.** Chosen.

**Option E — RECOMMENDED, matching the two sibling sets.** The conservative reading, and it has the
consistency argument: this document has never mandated an error spelling, and both neighbouring
error sets say RECOMMENDED out loud. It loses on its own consequence. If the spellings are
RECOMMENDED, the corpus is overreaching and its two failure vectors must stop asserting the token —
they would assert only that rendering fails, which deletes the sharpest check in the
prompt-rendering slice and leaves an implementation free to spell the one class a consumer branches
on however it likes. The consistency it buys is also thinner than it looks, since Section 17.3
already requires four of Section 11.4's RECOMMENDED tokens by name.

**Option F — REQUIRED, and re-level Sections 11.4 and 10.6 to match.** One rule for every enumerated
error token in the document, which would also retire the per-entry blocker outright and make the
level field unnecessary. It loses on what the two sets are: mappings onto a foreign surface. Section
11.4 says so in its own opening — "each adapter maps its transport's failures onto them" — and what a
transport lets an adapter distinguish is not Symphony's to fix. Requiring a spelling there is
requiring a *distinction*, and an adapter over a transport that reports a malformed payload and a bad
status the same way cannot make it. Section 10.6 is the same shape over a coding agent's protocol.

## Decision and reasoning

**The five Section 5.5 classes are REQUIRED spellings; Sections 11.4 and 10.6 stay RECOMMENDED, and
the registry carries the level per group.** The split is not a compromise between the two options,
it is the line the mechanism draws: **whether a spelling can be required turns on who owns the
condition.** Section 5.5's five conditions are Symphony's own — a file it resolves cannot be read,
front matter it delimits does not parse, front matter it requires to be a map is not one, a body it
renders is not well-formed, a variable or filter it supplies cannot be resolved. Every implementation
faces exactly those five, because the specification defines the artifacts they are conditions on.
Sections 11.4 and 10.6 are categories an adapter maps a foreign failure onto, and the foreign surface
decides what is distinguishable. A REQUIRED spelling over the first set costs an implementation
nothing it was not already doing; over the second it would be a requirement on a distinction an
adapter may be unable to compute.

**The set is open, and Section 5.5 says so rather than the registry inferring it.** REQUIRED plus a
group with no `exhaustive` flag reads as closed, and closing the set would forbid an implementation
from ever naming a workflow-loading condition these five do not cover — a substantive new restriction
adopted by omission, which is precisely the Section 10.4 failure 0071 was created to fix. Section 5.5
states that an implementation MAY define additional classes, MUST document any it defines, and MUST
assign each one of the two dispatch gating behaviors; the registry then records `exhaustive: false`,
in that order.

**A class names the condition, not the stage at which it is detected.** Stated in Section 5.5 as a
rule, with all five classes given a stated condition in Section 11.4's annotation shape rather than
the current mix of one phase and one condition. Annotating the five is what makes the rule
self-evidencing: `template_parse_error`'s only annotation today is "(during prompt rendering)", a
phase, which is the sentence that invites the misreading in the first place. Replacing it with the
condition it actually names — a body that is not well-formed template syntax — closes the gap even
for a reader who skips the rule.

The clause is stated over the loader and the renderer failing with a class, not over which pass an
engine performs the check in, so it is checkable by running the corpus against an implementation
without knowing what template engine is underneath. Naming a phase in normative text would have been
the mechanism-shaped version of the same guarantee, and would have re-created the defect one level
up.

**`gating` is carried per entry.** Section 5.5 already fixes the split — the first three block new
dispatches until the file is repaired, the last two fail only the affected run attempt — and Sections
6.2 and 12.4 are where a consumer acts on it. It is a property the specification states about each
token, which is the test an entry field has to pass, and it is the same shape as
`runtime_state_fields` carrying each field's `recovery_class`. A generated consumer that has to
re-derive the split from prose is in the position the registry exists to remove.

**`requirement_level` is a group field, not an entry field.** Each section states one level for its
whole set, so the property is genuinely the group's. If a single entry ever needs a different level
from its group's, the level has stopped being a property of the section and the ruling has to move
back into the prose before the registry can carry it — that is the shape of 0071's reconsideration
trigger applied to this field.

**Section 10.8 stays deferred, on its own reason.** Its reason codes are introduced by "for example"
with three illustrations and no enumeration, so there is nothing to publish that would not be
invented. That is a different and stronger reason than the one it inherits from the shared bullet
today, and the README states it separately.

**Reconsideration triggers.** Reopen the Section 11.4 level when a second tracker adapter lands and
Section 17.3's four named tokens are asserted against it — that is the evidence the set is REQUIRED
in practice and the declaration is stale, and it arrives as a conformance failure rather than as a
reading. Reopen the level field itself on the trigger above: an entry needing a level its group does
not state. Reopen Section 10.8 when its reason codes are enumerated rather than illustrated, which is
the condition its deferral now names.

Depends on 0071 (whose registry this extends and whose deferral it retires in part) and 0048 (which
authored the two vectors that assert `template_render_error`). Relates to 0056, which resolved the
same shape one layer down for the engine — enumerated conditions with no token for the error class a
caller most needs to act on — and to 0045, 0046 and 0002.
