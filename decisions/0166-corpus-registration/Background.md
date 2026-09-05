# Background — 0166 A vector file registered in neither list

## Context

Reported from `symphony-rs` as issue #154, against `5a4fdf7`. Held there since it was found while
building that repository's roadmap D1e and recorded as its decision 0011 R85, then submitted with
the rest of that build's open ledger.

`conformance/README.md`'s harness contract tells a harness to assert the result equals `expect`,
then lists the functions carrying an interpretation note beyond plain equality: `sort_for_dispatch`,
`resolve_config_defaults`, `render_prompt`. Three. `resolve_repository_config` —
`conformance/vectors/repository-inheritance.json`, added by decision 0159 — has an interpretation
note and is not among them.

## The mechanism

**The unlisted note is the only negative assertion in either corpus.** Measured at `5a69193`:

```
$ grep -rl '"absent"' conformance/
conformance/vectors/repository-inheritance.json
$ python3 -c "import json; d=json.load(open('conformance/vectors/repository-inheritance.json')); \
  print(len(d['vectors']), sum(1 for v in d['vectors'] if 'absent' in json.dumps(v)))"
7 7
```

One file, all seven of its vectors, nothing else in `conformance/vectors/` or
`conformance/vcsx/vectors/`. Its file-level `expect` reads:

```
{ resolved: object, absent: Array<string> }  // each dotted path in resolved MUST equal the
resolved view at that path; each path in absent MUST NOT be present in it; unlisted paths are
unconstrained
```

Every other note in the README's list refines *which* equality to assert. This one asks for
something no other vector asks for: that a key is **not** there. `absent` is a key of `expect` that
is not a field of the result, so a harness that does not know about it has nothing to fail on — it
reads a key it does not recognize and asserts nothing.

**What that costs is not a failed run but a passed one.** Section 6.1 step 3 fixes the resolution
order and states its own reason:

> Resolve each `repository` entry against the orchestrator-level blocks, leaf by leaf, and then
> apply built-in defaults for missing OPTIONAL fields (Section 5.3.7). In that order: a default
> filled into an entry before resolution would shadow the orchestrator-level value the entry meant
> to inherit.

An implementation that defaults **first** produces a superset of the correct answer. It has every
path the correct resolution has, with the same values, plus the ones a premature default filled in.
So it satisfies every path in `expect.resolved` — the positive half cannot separate the two orders,
because the wrong order does not produce a wrong value at any path the right order produces at all.
Only `absent` reaches the difference.

A harness built from the README's list therefore implements plain equality for
`resolve_repository_config`, and reports the ordering defect this file exists to catch as a pass.
That is the failure this is worth a decision over: not a harness author who is confused, but one who
is confident and wrong.

**The file is missing from the vector table too, which is what settles the cause.** Found while
confirming the report rather than in it. Measured at `5a69193`:

```
$ ls -1 conformance/vectors/ | wc -l
16
$ grep -c '^| `vectors/' conformance/README.md
15
$ for f in $(ls -1 conformance/vectors/); do \
    grep -q "^| \`vectors/$f\`" conformance/README.md || echo "NO TABLE ROW: $f"; done
NO TABLE ROW: repository-inheritance.json
```

The README tabulates its vector files in three slice tables — 13 rows for slice 1, one for slice 2
(`prompt-rendering.json`), one for slice 3 (`config-preflight.json`). Fifteen rows against sixteen
files, and the file with no row is the same one with no note. Its only appearances anywhere in
`conformance/README.md` are two prose mentions in the rationale section.

## Options considered

- **Option A — register the file in both places**: add the fourth interpretation-note bullet, and
  add the missing vector-table row under a slice heading for decision 0159.

  Trade-offs: two edits rather than one. Leaves `config-defaults.json` carrying its note both inline
  and in the README, which is a duplication someone may later read as accidental.

- **Option B — declare the README's list illustrative**, on the rule that notes live inline and the
  README samples them, and remove `config-defaults.json`'s duplicate entry so the list stops looking
  like a registry.

  Trade-offs: also one coherent answer, and the report offers it as such. It costs nothing to state
  and removes a duplication rather than adding an entry.

## Decision and reasoning

**Option A.** The missing table row is what decides it, and it decides it cleanly.

Option B is a claim about a *notes* policy: that a note belongs in the file it describes, and the
README's list is a sample rather than a registry. Grant that entirely and it still does not explain
a missing row in the **vector file table**. That table is not a notes list. No policy about where
interpretation notes live has any bearing on whether a file appears in the index of files, and the
same file is missing from both.

One cause explains both omissions: decision 0159 added `repository-inheritance.json` and registered
it nowhere. Two causes would be needed to keep Option B alive — a deliberate notes policy *and* a
separate accidental table omission — and the second of those is the same oversight Option A already
posits, so Option B buys nothing and costs an explanation.

`config-defaults.json`'s duplication is therefore left alone. Under Option A the list is a registry,
and a registry restating a note the file also carries is the intended shape rather than an
accident.

**Reconsideration trigger.** Reopen if a later slice adds a vector file and deliberately leaves it
out of the README's tables — for example, a file whose function is exercised only through another
file's vectors. That would make the table something other than an index of files, and the argument
above rests on it being an index. A second trigger is a second negative-assertion key appearing in a
different file: `absent` being unique is what makes its note the one most likely to be missed, and
two of them would suggest the schema wants a general statement about negative assertions rather than
a per-function bullet.
