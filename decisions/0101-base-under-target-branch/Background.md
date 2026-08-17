# Background — 0101 Under `target_branch` the base is an argument, not a policy key

## Context

Issue #51 reports that under `policy_source = "target_branch"` the base resolves from a source inside
the document the mode is trying to locate. It is decision 0094's bootstrap cycle, one mode over.

### The cycle

Section 6.4 gives the base three sources, the lowest being the repository's own: "the invocation's
`base_branch` wins, then the consumer configuration's, then this". Section 8.1 defines the mode as
reading host-side policy "from the pull-request target itself" — and the pull-request target is the
base.

So an invocation supplying no `base_branch`, against a consumer configuration supplying none, has
**no revision to read a policy from**, and the only remaining source is inside the unread policy.
Neither document says what happens.

The concrete path: `status` under `target_branch` with no base anywhere. Section 8.6 says `status`
"needs none and runs without one". Section 6.11 says the policy is validated before use. Section 8.1
says the policy is read from the target. The engine must read a document to learn where to read it
from, and each of the three candidate reasons describes something adjacent rather than this:
`policy_source_unreadable` says the source could not be read, where here it was never named;
`base_branch_missing` is scoped to entries that need a base, where this reaches every entry;
`policy_not_found` says the source held no file, which presumes a source.

### The second consequence, which is the sharper one

Section 8.6 scopes the base by the same rule as `git_access` — the entry point fixes the set — and
lists the entries outside it: "`commit`, `push`, `pull`, `merge`, `land` and `provision` need none and
run without one".

Under `target_branch` that sentence is false for the first five. An entry that needs no base to *do
its work* still needs one to *locate the policy that governs it*. Section 8.6 already makes exactly
this argument one argument over, for `policy_branch_missing`, and states it as the reason that reason
is established before validation rather than after:

> the policy document is the first of Section 6.11's five inputs and this argument is what says where
> to read it from. There is nothing to validate until it is known.

Under `target_branch` the argument that says where to read the policy from is the base. So the
before-validation set is mode-dependent rather than fixed, while the rest of the section's ordering
rule holds unchanged.

### The third consequence, which the issue does not name

The issue asks for `[base] branch`. The mechanism reaches the whole section. Section 12.4's
`resolve_base` reads `base_config.resolve` and `base_config.prefixes` — both keys of `[base]`, both
inside `repo.policy.toml`:

```text
else if base_config.resolve == "by_prefix":
    match = longest_prefix_match(work_branch, base_config.prefixes)
```

A repository using `resolve = "by_prefix"` under `target_branch` is in the same cycle by a second
route: resolving the base needs the prefix table, and reading the table needs the base. Qualifying
`branch` alone would leave the cycle half-open, so the rule is stated over `[base]` rather than over
one of its keys. This also settles a question that would otherwise be left hanging — whether the
policy, once read, may re-resolve a *different* operational base than the one that located it. It may
not: one invocation resolves one base.

### Why nobody was looking at this

Decision 0094's `Background.md` recorded that all 32 policy-validation vectors supplied `base.branch`
reflexively, and named that as how two defects survived review. The same instrument, pointed at the
mode:

```sh
python3 -c "import json; d=json.load(open('conformance/vcsx/vectors/base-resolution.json')); \
print(sum('policy_source' in json.dumps(v) for v in d['vectors']), 'of', len(d['vectors']))"
python3 -c "import json; d=json.load(open('conformance/vcsx/vectors/policy-validation.json')); \
print(sum('policy_source' in json.dumps(v) for v in d['vectors']), 'of', len(d['vectors']))"
```

0 of 9, and 0 of 38. The mode that creates the cycle is exercised by no vector in either file, so
every vector that resolves a base resolves it under the default mode. Decision 0097 introduced the
mode and 0098 gave it a further consequence (`[[branch]]` sections authored by whoever can land a
pull request); neither added a vector, and this defect is what that gap was hiding.

## Options considered

**Option A — qualify the source list, widen `base_branch_missing`.** Chosen; reasoning below.

**Option B — mint a distinct precondition reason** for "the mode's policy source has no revision to
resolve to". The case for it is the specification's own posture: Section 6.1 keeps four diagnoses
behind one disposition, and keeps them apart because "the **repair** differs: make the source
readable, commit the file, fix the syntax, fix the value". The causes here do differ — under the
default mode you supply a base because the entry needs one, under this mode because nothing else can
locate the policy — and Section 8.5 permits a new precondition reason in a `MINOR`, so the token is
available.

It loses on Section 6.1's own test, read exactly. The rule keeps reasons apart where the *repair*
differs, and the repair here is identical to `base_branch_missing`'s: supply `base_branch` on the
invocation, or in the consumer configuration. A token that names a different cause behind an
identical fix spends part of a major-stable surface — which every conforming engine must then report,
and which cannot be withdrawn inside a `MAJOR` — to tell a consumer something it can already read off
`policy_source`, which it configured itself. The reporting implementation reached the same place from
the other side: it widened one registry row rather than mint a token no peer engine would report, and
published the widening as a deviation.

**Option C — remove the mode.** The strongest of the three on the merits of the cycle itself: delete
`policy_source` and `target_branch`, let a deployment that wants the pull-request target as its trust
root name it as `policy_branch`, and the policy is then always located by an argument and never by
itself. Section 11's conditional guarantee becomes unconditional, the base keeps three sources under
one rule, and the escape hatch already exists in the specification's own words — under this mode "a
`policy_branch` equal to the target is the configuration rather than an error in it", which is very
nearly a statement that the mode is sugar for that configuration.

It loses on what a consumer can tell. Section 8.1 names it a mode rather than a flag deliberately:
"the trust properties Section 11 states are conditional on it, and a conditional guarantee is worth
stating only where a consumer can tell which state holds". Collapsing it into a value of
`policy_branch` puts a reader back to comparing two strings to learn which trust regime is in force,
and turns `policy_branch_is_target` from a refusal 0094 added deliberately into an opt-in. `SPEC.md`
Section 15.4 states what the mode gives up as a property of the mode — the merge path to the trust
root reopening, and per-branch sections becoming authorable by whoever can land a pull request; that
statement would have to be rewritten as a property of a coincidence between two configured values,
which is where an operator stops noticing it. The cost is also the largest of the three, across two
specifications and four `SPEC.md` sections, for a defect that is a missing qualification.

## Decision and reasoning

**Under `target_branch`, `[base]` contributes nothing to the base.** The base has two sources under
that mode — the invocation's `base_branch`, then the consumer configuration's — because every key
that could contribute the third lives in the document being located. This is Section 8.1's existing
sentence about the policy branch, applied to the argument that plays its role under the other mode: a
branch named inside the policy cannot select the revision the policy is read from.

**Where neither supplies one, `base_branch_missing`, whatever the entry, established before
validation.** That is the place `policy_branch_missing` occupies under the default mode, and it is
there for the same shape of reason: the argument is what says where the policy is read from, and
there is nothing to validate until it is known. So Section 8.6's before-validation set becomes
mode-dependent — `arguments_unreadable` and `local_vcs_missing` always, then `policy_branch_missing`
under `policy_branch` and `base_branch_missing` under `target_branch` — and the ordering rule for
every other reason in the registry holds unchanged.

**`provision` keeps its exemption.** Section 6.1 already makes it the one entry point that runs where
no policy could be read, because it is the operation that obtains the repository the file is in, and
Section 8.6 already establishes for it only the reasons judged from the invocation's arguments,
listing them exhaustively without this one. A `provision` refused for want of a base would be refused
for a policy read it does not perform. The exemption is therefore restated rather than created, which
is the right size: two exemptions resting on one sentence, made visibly the same sentence.

**Widening rather than minting** costs nothing in the major-stable surface. No token is added, the
`usage_or_config` status is unchanged, and a consumer already branching on `base_branch_missing`
absorbs the wider scope without changing. What changes is the reason's *scope*, which the registry
entry states.

**All four copies of the three-source list move together** — Section 6.4, Section 8.6's table row,
and `SPEC.md` Sections 9.7 and 18.1 — because a reader reaching any of them first would otherwise get
the unqualified version. `SPEC.md` Section 15.4 gains the same qualification where it states what the
mode gives up, since needing an operator-supplied base is now part of what choosing the mode costs.

**Reconsideration trigger.** Reopen the token question if a consumer must distinguish "this entry
needs a base" from "nothing says where to read the policy from" *in automation* — the evidence is a
consumer branching on `base_branch_missing` and having to read `policy_source` back to know what to
do next. That is the point at which the repair genuinely differs and Option B earns its token. Reopen
the mode itself if a deployment configures `target_branch` and then supplies an operator-level base
on every invocation anyway, since it is then paying for a mode whose only convenience — not naming a
branch — it is no longer using.

Relates to 0094 (whose cycle this is, one mode over, and whose measurement instrument this reuses),
0097 (which introduced the mode), 0098 (which gave the mode a further consequence and likewise added
no vector for it), and 0002.
