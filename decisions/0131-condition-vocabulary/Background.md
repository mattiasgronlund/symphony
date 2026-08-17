# Background — 0131 A value set closed in prose, and the field that points at it

## Context

Issue #78, from an implementation building the roadmap slice for decisions 0107–0110, reports that
`VCSX-SPEC.md` Section 8.2 fixes `outputs.forge_unavailable_condition` to one of three tokens —
`server_error`, `bound_elapsed`, `transport_failure` — and that `conformance/vcsx/vocabulary.json`
carries them **only inside the `meaning` prose** of that output key's entry. Their sibling set, the
three ways a unit the engine hands control to gives it no usable answer, has a group of its own
(`hook_conditions`) in the same file.

## What the defect does

A generator reads groups. An implementation that generates its vocabulary from the registry — which
is what `conformance/vcsx/README.md` says the registry is for, "so a token change upstream becomes a
build failure rather than a silent behavior change" — gets a type for `hook_conditions` and nothing
for these three, so it hand-writes them.

The two halves then fail differently on the same upstream event. Rename a hook condition and the
generated type changes, the hand-written match arm stops compiling, and the implementation is
stopped at build. Rename a forge-unavailable condition and nothing downstream moves: the engine
keeps emitting the old spelling, the consumer keeps branching on it, and the mechanism built to
catch exactly this reports green. The reporting implementation had already reached that conclusion
on its own and paid for it — its decision 0011 R63 extracts the three backticked tokens out of the
`meaning` sentence into a generated constant and compares a hand-written enum against it, so that a
**reword of an English sentence** fails a test. That workaround is the measurement: an implementation
was willing to parse prose rather than accept the silent case.

The failure is not hypothetical for this particular value, either. `forge_unavailable` is
`needs_caller` with `retry_after` (Section 4.3), so the condition is what a consumer reads to tell an
informed wait from an uninformed one; the three conditions are the ones a fault-injection harness
exists to produce (`conformance/vcsx/README.md`, "Fault-injection vectors"), and that harness is owed
by an implementation rather than carried here — so the divergence would land in the one family this
tree has already recorded as having no coverage.

## Publication: the reader test, applied

Decision 0103 fixed the rule this file's contents are judged by, and put it in
`conformance/README.md`: **a prose enumeration is published when something outside the
implementation's own source spells it** — a repository author writing configuration, a Conformance
Statement author filling a table, or a conformance check asserting a value. Not whether the set is an
enumeration, but what reads the spelling and what happens when the reading is wrong.

Two readers, both outside any implementation's source, and both checked in the document rather than
assumed:

| Reader | What it spells | Cost of a divergence |
|--------|----------------|----------------------|
| Section 13.1's network-bound row | `bound_elapsed` **by name**, as the value a forge call exceeding `network_bound_ms` carries in `outputs` | a conformance check asserting a token the engine no longer emits |
| `conformance/vcsx/README.md`'s fault-injection obligation | `forge_unavailable_condition` as an `outputs` key every fault-injection vector MUST assert | the assertion is owed by an implementation's harness, so the spelling crosses a repository boundary |

The second reader is the weaker of the two on its own — it obliges the key rather than the value. The
argument that carries this is **symmetry**, and it is the specification's own: Section 8.2 says of
these three that "it is the same arrangement `unanswered_gates` makes for its own three conditions,
and for the same reason". One of the two arrangements is published as a group and the other is not.
Under the reader test that difference has to be earned, and nothing in the document earns it — the
sets have the same shape, the same closedness, and Section 8.2 spells one of the tokens identically
in both on purpose.

### The scan: this is the last instance of its shape

A rule applied to one reported set and no others is a rule that goes stale, which is the failure
0103's `Background.md` counted four instances of. So the file was swept for the general case rather
than the reported one: every `meaning` and `note` string, checked for a value set closed in prose and
spelled nowhere as data. Python 3.13.5, run from the repository root:

```sh
python3 - <<'PY'
import json, re

doc = json.load(open('conformance/vcsx/vocabulary.json'))
groups = {k: v for k, v in doc.items() if isinstance(v, dict) and 'entries' in v}

def members(g):
    """Every token this group spells as data, under whatever field name."""
    out = set()
    for e in groups[g]['entries']:
        if isinstance(e, str):
            out.add(e)
        elif isinstance(e, dict):
            out |= {v for v in e.values() if isinstance(v, str)}
    return out

def prose(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ('meaning', 'note') and isinstance(v, str):
                yield '/'.join(path + [k]), v
            else:
                yield from prose(v, path + [k])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from prose(v, path + [str(i)])

# A closed set spelled in prose: two or more backticked snake_case tokens
# joined by a final "or"/"and".
PAT = re.compile(r'(?:`[a-z_][a-z0-9_]*`, )+`[a-z_][a-z0-9_]*` (?:or|and) `[a-z_][a-z0-9_]*`')

for path, text in prose(doc, []):
    for m in PAT.finditer(text):
        toks = set(re.findall(r'`([a-z_][a-z0-9_]*)`', m.group(0)))
        pub = [g for g in groups if members(g) >= toks]
        print(f'{path}\n    {m.group(0)}\n    published by: {pub or "NOTHING"}')
PY
```

Five hits before this decision, and exactly one unpublished:

```text
reasons/note
    `blocked`, `failed` and `hook_unanswered`
    published by: ['reasons']
reasons/note
    `push`, `create_pr` and `merge`
    published by: ['operations', 'reasons', 'entry_points']
precondition_reasons/note
    `arguments_unreadable`, `local_vcs_missing`, `forge_coordinate_missing`, `git_access_missing`, `forge_access_missing` and `store_location_missing`
    published by: ['precondition_reasons']
precondition_reasons/entries/7/meaning
    `commit`, `push`, `pull`, `merge`, `land` and `provision`
    published by: ['entry_points']
output_keys/entries/5/meaning
    `server_error`, `bound_elapsed` or `transport_failure`
    published by: NOTHING
```

The four published hits are prose *about* sets the file already carries as data — how Section 4.3's
combined rows expand, which operations reach a forge, which preconditions are established before
validation, which entry points need no base — not value spaces of their own. `members()` reads every
string field of an entry rather than `token` alone, which is what makes the first hit come back
published: the bare reason names `blocked`, `failed` and `hook_unanswered` are carried in `reasons`
under the `reason` field of composed `<op>:<reason>` entries, so a generator can read them.

**So #78 is the last instance of its shape, not the first of many.** That is the durable part of the
measurement: a later reader re-runs the scan and gets a clean sheet, rather than re-deriving whether
one was missed.

## A group fixes the values, and not the link

Adding the group answers half of the report. The other half was found by asking what a generator
could do with the groups that already exist, and the answer is less than the file appears to promise.

`unfinished_hooks` and `unanswered_gates` both say "`condition` is a `hook_conditions` token" — **in
prose**, inside a `meaning` string. Their `fields` arrays are flat strings: `["hook", "trigger",
"condition"]`. So a generator emitting a record type for `unfinished_hooks` types `condition` as a
free string even though the group closing it sits in the same file, and an upstream rename of
`answer_unreadable` diverges silently on the field exactly as it would have on
`forge_unavailable_condition`. That is the reported defect one layer up, on keys the file already
treats as fixed — which is why this is one decision rather than two: publishing the values and
leaving the link in prose would answer the report and reproduce it.

`fields` is also **undocumented**. `conformance/vcsx/README.md`'s Schema section describes
`spec_refs`, `note` and `entries` and never mentions `fields`, which is part of why its shape was
free to be assumed rather than checked.

## Options considered

### How the values are published

**Option A — a `forge_unavailable_conditions` group in `hook_conditions`' exact shape.** Chosen. The
report's own suggestion, and the symmetry argument above is the reason: two sets the specification
calls the same arrangement should be the same arrangement in the derived view.

**Option B — publish nothing further, and let the `meaning` sentence stand.** The steelman, and it is
not empty: the values *are* in the prose an implementer reads, an implementer writing a `vcsx`
consumer reads Section 8.2 anyway, and a registry that grows a group per enumeration drifts toward
the inventory 0103 declined to make. It loses on the generator, which is the reader the registry was
created for and the one that cannot read prose. The report's own workaround is the disproof: an
implementation that had the prose in front of it still built a parser for the sentence, because
reading it once is not the problem — noticing that it changed is.

### `bound_elapsed` in two groups

The new group and `hook_conditions` share a token. That duplication is **paid, not avoided**, and the
reasoning is the specification's own.

`bound_elapsed` is one token for one event on two kinds of unit, deliberately. Section 9 states it
outright, of a forge call that reaches the bound `network_bound_ms` sets (Section 8.1): it is "the
same spelling Section 6.6 fixes for a unit still running when its bound elapsed, **reused
deliberately**, since one event on two kinds of unit should not diagnose differently by which program
the engine happened to be waiting on."

**Option E′ — carry the token in both groups, with the sharing recorded in each note.** Chosen.
**Option F′ — carry it in `hook_conditions` alone and have the new group name only the two tokens
that are its own, with a note pointing at `hook_conditions` for the third.** This is the orthodox
move: no token appears twice, and the split follows the provenance the specification states.

F′ loses on the reader the group exists for. A generator emitting a type for
`forge_unavailable_condition` needs **one** group whose members are exactly that field's value space;
a group carrying two of three tokens and a prose pointer for the third is precisely the defect
reported — a value closed in a sentence — reintroduced inside the repair. This is decision 0103's
Option E on the same terms: it published Section 11.6's whole set of ten knowing five are also
published by the engine registry, because "a repository author validating a `tracker.transitions`
entry has **one** field to check against **one** vocabulary", and splitting by provenance serves the
ownership model rather than the person doing the reading.

The cost is the same cost 0103 took on, and is paid the same way — in the group note. The new group's
note records that `bound_elapsed` is also a `hook_conditions` token, that Section 6.6 is where the
spelling is fixed and is the authority for it, and that Section 9 reuses it deliberately.
`hook_conditions`' note gains a one-clause pointer back, so the sharing is discoverable from either
side rather than only from the group that arrived second.

### How the field→group link is expressed

**Option C — promote `fields` from flat strings to objects `{"name": …}`, carrying `values_from`.**
Chosen. It follows the promotion `conformance/vcsx/README.md` already documents for `entries`
("either an array of strings, or an array of objects…") and that `envelope_fields` already took, and
it keeps one shape across `output_keys` rather than a mix of two.

**Option D — a parallel `field_values_from` map keyed by entry and field name, leaving `fields`
alone.** Additive, non-breaking, and no `schema_version` bump. It loses on its failure mode: it names
the same fields in two places, so a field renamed in `fields` and not in the map diverges silently —
which is the exact defect this decision exists to remove, reintroduced by the mechanism meant to
remove it.

### Where a link is authored

The rule adopted: **only where the specification fixes the field's value space to *exactly* one
group.** Each candidate was checked against its cited section before the link was written, and one
of the four candidates failed.

Authored:

- `forge_unavailable_condition` → `forge_unavailable_conditions`. Scalar, so the link is at entry
  level. Section 8.2: "the condition that occurred — `server_error`, `bound_elapsed` (Section 8.1) or
  `transport_failure` — absent for every other reason". Closed, no allowance to add.
- `unfinished_hooks.condition` → `hook_conditions`. Section 8.2 names the three; Section 6.6 fixes
  them with no allowance to add.
- `unanswered_gates.condition` → `hook_conditions`. Section 8.2: "the `condition` — the same three
  tokens".

**Not authored — `unanswered_gates.position` → `lifecycle_positions`, and the verification is the
finding.** The link looked obvious and fails the rule. Section 5.1 defines the kind as
"`before:commit`, `before:push`, `before:create_pr`, `before:merge` (and any engine-defined
`before:<op>`)", and Section 4.1 states outright that "an engine MAY define additional operations and
their `before:<op>` positions". The group's own note already says so — "The required positions" — so
`lifecycle_positions` is the required set and not the value space. A generator told to close
`position` at four tokens would **reject a conforming engine's own gate**, which is this decision's
defect pointed the other way: a link is a claim about closedness, and an unchecked one is worse than
no link, because it is machine-readable and wrong. `values_from` is therefore authored from the
prose's closedness rather than from the existence of a plausibly-matching group.

Also not linked, each for a reason of its own:

- **`unperformed_intents.action` — the subset case, and the registry has no way to state it.**
  Section 8.2 reports "the consumer-effected intents (Section 5.2) the engine emitted and no consumer
  performed". The value space is the `effected_by: "consumer"` subset of `actions` —
  `create_task`, `set_state`, `notify` — not `actions`. `values_from: "actions"` would be false, and
  a generator would admit `run_op` as an unperformed intent. The honest options are a subset
  expression (`values_from` plus a filter predicate) or nothing, and a filter predicate is a property
  `VCSX-SPEC.md` does not fix — which is `conformance/vcsx/README.md`'s named trigger for the
  registry having stopped being a derived view: "move the concept into `VCSX-SPEC.md` and re-derive
  rather than letting the registry lead". So the case is left unstated rather than approximated. The
  fact a generator needs is already in the file as `effected_by`, one group over.
- **`trigger` on `unfinished_hooks` and `failed_by_policy`** — composed `<op>:<reason>` or a
  `before:<op>` position, so it is a grammar rather than a flat group.
- **`failed_by_policy.reason`** — the entry already states it "belongs to no registry in this file",
  being repository-authored.
- **`detail` (`Implementation-defined`), `hook`, `arguments`, `buckets`, `observed_at`** — free
  values.

### `schema_version`

Bumped `1` → `2`. Prior group additions did not bump it, correctly: adding a group is additive, and a
consumer that does not know the group ignores it. Changing the shape of an existing field is the
first non-additive change this file has made — a consumer reading `fields` as an array of strings
breaks on an array of objects — so the version is what tells it to look. The Symphony registry
(`conformance/vocabulary.json`) is a separate artifact with its own schema and stays at `1`.

### Naming

`values_from` pairs with the file's existing `values` — an inline closed set, on
`message_formulation`'s `body_source` and `strategy` — and sits in the register of `bound_by`,
`effected_by`, `raised_by`, `default_need`: a field naming where a property is answered rather than
restating the answer.

## The specification change, and why it is not cosmetic

The registry is a derived view, so a REQUIRED spelling in it must rest on a sentence in
`VCSX-SPEC.md`. Section 6.6 carries one for its three — "The three conditions are named tokens, so
the diagnosis a consumer reads is spelled the same on every engine" — and Section 8.2's
`forge_unavailable_condition` bullet carries no counterpart. Its nearest sentence claims something
else: "both spell the condition as a token so one consumer branch reads both" is **cross-key**
uniformity, an argument about `unanswered_gates` and this key agreeing with each other, where a group
generated into a shared type rests on **cross-engine** portability. So the sentence is added rather
than assumed, in Section 6.6's own words and pointing at it.

It adds no obligation, no RFC 2119 keyword and no `Implementation-defined`, which is why it can be
added at all without a Conformance Statement row.

**A consequence not on the sheet, added because the level is otherwise unobservable.** The new
sentence changes nothing anything can check unless a conformance surface asserts the tokens by name,
and Section 13.1's transient-forge row asserts only that "a `forge_unavailable` result carries its
condition in `outputs`". So that row is changed to name the three, in the shape the hook rows in the
same section already use ("`outputs.unanswered_gates` naming which of `bound_elapsed`, `not_started`
and `answer_unreadable` occurred"). This is the same move decision 0103 recorded under the same
heading, and it is called out here rather than folded into the edit so that a reader can see a test
matrix row changed for a reason the report did not ask for.

## Findings recorded and not repaired

- **`hook_conditions`' first `spec_ref` cites a stale section title.** It reads `Section 6.6
  "`[hooks]`"`; the heading is `### 6.6 `[hooks.engine]``, and `repo_policy_sections` carries the
  current spelling. Left alone: it is a real defect in a derived view and it is not this report's,
  and folding an unrelated citation repair into a decision about value spaces is how a scoped change
  stops being reviewable. Assignable as it stands.

## Reconsideration triggers

- **Reopen the subset case** if a second field turns out to need one, or if `VCSX-SPEC.md` ever fixes
  the consumer-effected actions as a named set — at which point the answer is a group in the
  specification's terms, not a predicate in the registry's.
- **Reopen `unanswered_gates.position`** if `VCSX-SPEC.md` closes the position set, which today it
  explicitly does not.
- **Reopen `values_from` itself** on `conformance/vcsx/README.md`'s standing trigger: a link the
  registry needs and the prose does not fix.
- **Re-run the scan** after any decision that adds a `meaning` or `note` enumerating values; a hit
  published by `NOTHING` is a new instance of #78.

Depends on 0103 (whose reader test this applies, and whose Option E precedent covers the duplicated
`bound_elapsed`) and 0051 (which created the registry and its derived-view rule). Relates to 0107–0110,
whose slice the reporter was building, and to 0128, whose template-row rule was checked against this
change and is not triggered.
