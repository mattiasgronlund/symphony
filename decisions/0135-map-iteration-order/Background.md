# Background — 0135 The map a template can iterate, and the order it never had

## Context

Issue #93 was the only issue open on `mattiasgronlund/symphony`. It was filed by the `symphony-rs`
build, which met the gap implementing strict prompt rendering, raised it the day it was found, and
published its own answer as a `SPEC.md` Section 19 obligation in the meantime.

Section 12.2's Rendering Rules require the renderer to "Preserve nested arrays/maps (labels,
blockers, metadata) so templates can iterate", and no section in the document fixes the order
iterating one yields. Section 4.1.1 makes `metadata` a map — "Opaque, adapter-owned key/value pairs"
— while `labels` and `blocked_by` are lists, which have an order because they are lists. The `issue`
object is itself a second map, and a template may name it whole.

### The failure path

Section 5.4 makes the rendered body the agent's whole instruction for the run. One template and one
issue therefore produce two different instruction texts on two conforming implementations, and the
run's behaviour differs with them. It is not a formatting difference that a reader normalizes away:
the prompt is the input to a non-deterministic agent, so a reordered `metadata` block is a different
experiment.

It is worse than a difference between implementations. A map decoded from a tracker payload has no
insertion history worth preserving, so the two readings available under "Liquid-compatible" are both
unstable:

- Ruby Liquid, the reference implementation, iterates a `Hash` in **insertion** order — which is
  whatever order the tracker adapter happened to build the map in, and for a payload-decoded map
  that is a property of the JSON parser rather than of the issue.
- `liquid` 0.26.11 (Rust) iterates `std::collections::HashMap`. Verified in the crate source rather
  than taken from the report: `liquid-core-0.26.11/src/model/object/map.rs:22` declares
  `type MapImpl<K, V> = hash_map::HashMap<K, V>` and `Object` holds one, so the order is the
  default randomizing hasher's and varies per process. The reporter measured it: the same
  three-key map rendered in three different orders across six runs of one binary.

So the same implementation does not agree with itself between runs. That is the sharpest form of the
gap, and it is why "Liquid-compatible semantics are sufficient" (Section 5.4) does not settle it —
both engines are Liquid-compatible, and they disagree with each other and with themselves.

### Why it lands on the corpus

`render_prompt` is a `Daemon Conformance` function with a vector file
(`conformance/vectors/prompt-rendering.json`), and `iterate-labels` already establishes iteration as
in-contract. What no vector establishes is what iterating a *map* yields. The observable output of a
conformance-checked function was unspecified for an input the same corpus says must work.

## What was checked

Everything #93 claims about this repository holds; each was read rather than assumed.

- Section 12.2's fourth rendering rule is quoted exactly, and it is the whole of what the document
  says about iterating a nested structure.
- Section 4.1.1 makes `metadata` a map and `labels`/`blocked_by` lists; Section 5.4 fixes the engine
  no further than "Liquid-compatible semantics are sufficient" plus the two strict-failure MUSTs.
- `conformance/vectors/prompt-rendering.json` held seven vectors, of which `iterate-labels` iterates
  a list and none iterates a map.

Two things the report does not state were found by reading `liquid` 0.26.11 itself, and both bear on
the decision.

**The reach is bounded by the engine, and the bound is real.** The report says a value cannot both
survive materialization as an object — which field access needs — and iterate deterministically. The
mechanism is in the crate: `liquid-core-0.26.11/src/runtime/stack.rs` resolves a variable with
`crate::model::find(data.as_value(), path).map(|v| v.into_owned().into())`, so naming a variable
whole materializes it through `ValueView::to_value()`, and `liquid-lib-0.26.11`'s
`stdlib/blocks/for_block.rs::get_array` then iterates the resulting `Object`'s `HashMap`. An
implementation buys the order back by writing `to_value()` by hand — which is what `symphony-rs`
does — but a value whose `to_value()` returns an ordered pair array is no longer an object, and
`{{ b.identifier }}` after `{% for b in issue.blocked_by %}` needs the blocker to be one. A rule
written over *every map an implementation exposes* would therefore be unimplementable on at least
one Liquid-compatible engine. A rule written over the maps Section 12.2 names is implementable on
all of them, because `find` walks the path through `ObjectView::get` on the views and materializes
only what the path ends at.

**The rule is not free where it is implementable, and #93 does not say so.**
`liquid-lib-0.26.11/src/stdlib/tags/assign_tag.rs` evaluates its right-hand side and calls
`into_owned()`, so an object bound with `{% assign %}` is materialized by the same `to_value()` the
order was bought with: `{% assign i = issue %}{{ i.title }}` stops resolving and fails
`template_render_error`. Section 5.4 requires no aliasing, so an implementation paying that price is
still conforming — but the price is paid by anyone implementing on that engine, not only by the
reporter, and it belongs beside the rule rather than in a downstream build's notes.

The entry shape was checked the same way. `for_block.rs::get_array` maps an object's entries to
`Value::Array(vec![Value::scalar(k), v.to_value()])` — a two-element `[key, value]` entry, key first
— which is also what Ruby Liquid produces, a `Hash` iterating as its `to_a` pairs.

## Options considered

### Fix the order and its reach — chosen

Section 12.2 gains the order rule and one paragraph fixing which values it governs: the maps a
template names by path — the `issue` object and `metadata` — while a blocker ref is reached by
iterating `blocked_by`, read by field name, and its own fields are outside the iteration contract.

### Fix the order alone, exactly as #93 asks

The smaller change, and it answers the ask: one sentence, ascending by key, nothing said about
reach. Its case is that the case which actually occurs is `metadata`, that no template anyone has
written iterates a blocker's fields, and that a specification is not obliged to enumerate what it
does not govern. On that reading the reach paragraph is words spent on a shape nobody uses.

It loses because the rule would not be true as written. Read literally it covers a blocker ref's own
fields, which is the one shape no implementation on `liquid` 0.26.11 can order — so a conforming
build would keep publishing a limit against a rule whose face already covers it, and the next
implementer would rediscover the same conflict from scratch. A rule stated wider than it can be met
is worse than one whose edge is named: the first makes conformance a judgement call, the second is
checkable.

### Take map iteration out of the contract instead of ordering it

Split the fourth bullet: nested arrays are preserved so templates can iterate, nested maps so
templates can read members by name. No order is owed because nothing in contract iterates a map,
nothing has to be bought on any engine, the blocker residue closes for free, and the contract
shrinks to exactly what the corpus can check. This is the option with the least machinery behind it,
and on a document that prizes checkability it deserved the hearing it got.

It loses on what it removes. `metadata` exists for "tracker-specific data the fields above do not
capture" (Section 4.1.1) and is adapter-owned, so a template cannot name its keys in advance —
iterating it is the only way a repository puts Jira custom fields or board columns in front of the
agent. Removing that leaves the field renderable only by a template that already knows what the
adapter put there, which is the case it was introduced to serve. It also walks back a sentence the
specification states today, for a gap whose repair costs one paragraph.

### Declare the order `Implementation-defined` and require it documented

Not offered as an option on the decision sheet, and recorded here because it is the obvious fourth
answer and it is worse than the three above. It documents the divergence rather than removing it —
decision 0134's finding, in its own words, that "the minimal repair … documents a divergence rather
than removing it" — and here it does not even buy reproducibility *within* one implementation, since
neither insertion order nor hash order is a function of the issue. It would also owe a
`CONFORMANCE-STATEMENT-TEMPLATE.md` row, which is a cost the three real options do not carry.

## Follow-up forks

**What "ascending" compares.** Fixed to the Unicode code point, with a `Note:` recording that the
result is independent of the host's locale, that no Unicode normalization form is applied, and that
comparing the keys' UTF-8 bytes yields the same order. The last clause is what makes the rule
implementable rather than aspirational: an implementation whose engine hands it an unordered map can
sort on the way out instead of carrying an ordered container. Leaving "ascending by key" unqualified
would have settled every ASCII key and reproduced the original defect on the first non-ASCII one,
and metadata keys are adapter-owned. That a collation is a different order rather than a theoretical
one is measured rather than asserted: over the three keys `iterate-metadata-map-non-ascii` carries,
`locale.strxfrm` under glibc's `en_US.UTF-8` and `sv_SE.UTF-8` both order `år` before `ärlig`, where
ascending by code point orders them the other way. Section 12.2's own "Convert issue object keys to
strings for template compatibility" is what makes a code-point comparison well defined at all, which
is also why an adapter with non-string keys is a reconsideration trigger below. The wording follows
Section 4.2's existing care for `Lowercase Normalization`, which states its locale- and
normalization-independence rather than leaving it to be derived.

**Whether Section 12.2 also fixes the entry shape.** It does: one two-element entry per pair, key
first. An order is only observable through a shape — with the shape left to the engine, a vector can
assert that two runs agree but not what they render, which is the difference between a checked rule
and a documented one. The cost is honest: this is one step further into template-engine semantics
inside a language-neutral document. It is bounded by being the shape both Liquid implementations
already produce, so it constrains no engine that Section 5.4's "Liquid-compatible" already admits.

**Whether the `issue` object's field set is closed.** The vector iterating the issue object needs an
answer, and Section 4.1.1 already gives one: it lists the normalized record's fields and gives
tracker-specific extras a home in `metadata`, which is only coherent if the surrounding set is
fixed. Section 5.4's "Includes all normalized issue fields" is read as naming that set, not as a
floor above which an implementation adds its own. No new sentence is written for this; the vector
rests on Section 4.1.1 as it stands, and the reach paragraph cites it.

## Reconsideration triggers

- **A Liquid-compatible engine that can order an object without destroying it.** The reach paragraph
  exists because `liquid` 0.26.11 cannot. An engine — or a later `liquid` — with an order-preserving
  object would make the blocker exclusion unnecessary rather than merely unmet, and the paragraph
  should then be re-argued rather than kept out of habit.
- **A repository that wants to iterate a blocker's fields.** The exclusion is stated on the ground
  that Section 12.2 asks for field access there, not iteration. A real template that needs both is
  the evidence that the shape, rather than the rule, is what should change.
- **A second implementation that pays the aliasing cost visibly.** `{% assign i = issue %}` failing
  is conformant but surprising. If it turns up as a repeated authoring error rather than a footnote,
  the answer is a sentence in Section 5.4 about aliasing, not a retreat from the order.
- **A tracker adapter whose metadata keys are not stable strings.** Ascending-by-code-point assumes
  keys that compare as strings. An adapter that wanted structured or numeric keys would be a reason
  to revisit Section 4.1.1's `metadata` type before revisiting this rule.
