# Background — 0094 A policy that determines no base

## Context

Decision 0093's second review finding made `provision` the one entry point that runs where no
`repo.policy.toml` has been discovered, because it is the operation that obtains the repository the
file is in. Stating that exposed what the document does not state: **what any other entry point does
when the policy determines no base.**

There are two ways to reach that state, and `VCSX-SPEC.md` handles neither.

**No document.** Section 6.1 resolves `repo.policy.toml`'s path "relative to the repository root"
and gives exactly one rule for a policy the engine cannot use: "A discovered file that does not
parse yields no policy to validate." A file that was never discovered is not a file that does not
parse. Section 6.10's table has no row for it.

**A document with no base.** Section 6.4 declares three keys. `resolve` carries `Default: fixed`
and `prefixes` is marked OPTIONAL; `branch` — "the base branch the pull request targets and
`integrate` pulls from" — carries neither. It is required by omission, which is the weakest way a
specification can require anything, and Section 6.10's table has no row for its absence either. The
one base row, `base_unresolvable`, is narrower than it looks: "A `by_prefix` base resolution with no
empty-prefix default, or a missing or malformed map." Both halves presuppose `resolve = by_prefix`.
Under the default `fixed` strategy with no `branch`, no condition in the table names the state.

The two are one question. In both the engine holds a policy that selects no base branch, and the
repair in both is to edit a document. What differs is only how much document there is.

**The measurement.** `conformance/vcsx/vectors/policy-validation.json` carries 32 vectors. All 32
supply `base.branch`, including every vector whose subject is something else entirely — the
`version_floor` vectors, the hook vectors, the edge-cycle vectors. Not one models a policy without a
base, and not one models an absent policy. Re-run with:

```sh
python3 -c "import json; d=json.load(open('conformance/vcsx/vectors/policy-validation.json')); \
print(sum('branch' in v['given'].get('policy',{}).get('base',{}) for v in d['vectors']), 'of', len(d['vectors']))"
```

That the corpus supplies the key reflexively in vectors that do not test it is the tell: the key is
treated as structurally present rather than as a value with an absence case, which is how a required
key with no stated disposition survives review.

**Which entries actually need a base.** Read off Sections 4.1, 12.2 and 12.3:

- Need one to do their work: `integrate` (brings the base into the work branch), `create_pr` (the
  pull request targets it), and `ship`, which dispatches `create_pr`.
- Degrade by design: `status` reports `ahead`/`behind` as null with a `base_absent` output rather
  than failing; `diff` reports `base_unavailable`. Both are written for a base the checkout does not
  *hold*, which is a different state from a base the policy does not *select*.
- Need none at all: `commit`, `push`, `pull`, `merge`, `provision`, and `land` — Section 12.3
  dispatches only `merge`, which reads the pull request and takes its base from there.

So a repository with no policy at all can still support a coherent session: commit, push, pull. That
is not hypothetical for this engine — Section 1.1 makes `vcsx` "usable on its own", and `SPEC.md`
Section 3.4's `engine-direct` topology is a human running it directly.

## Options considered

**Option A — the policy determines no base, so refuse every entry but `provision`.** One condition,
one reason, reported at validation. Total and cheap to state, and it cannot surprise anyone.

Its cost is what it denies. A consumer who wants `commit` and `push` in a repository that carries no
Way of Working is refused for the absence of a value neither operation reads. That is a refusal the
consumer cannot act on except by writing a base branch it does not need into a file it did not want,
which is a specification telling a user to satisfy a check rather than a requirement.

**Option B — an absent policy is an empty policy; let the base fail where it is needed.** `commit`
and `push` run; `integrate` and `create_pr` report `base_unresolved` at first use. Elegant in that
it invents nothing: absence is already the meaning of every OPTIONAL key, and `base_unresolved`
already means "the configured strategy selected none" (Section 4.3).

It loses on **where the refusal happens**, and it loses to an argument this repository has already
accepted. Decision 0084 rejected exactly this shape: Section 12.2's `ship` runs `commit`, then
`push`, then `create_pr`, so a policy that cannot compose a body "publishes a work branch and then
dies". A policy that determines no base fails at the same step for the same reason — the work branch
is on the remote and the pull request never opens. 0084 called that the strongest argument in its
own case and moved `template_unbound` to validation to prevent it; option B reintroduces it one key
over, and would have to argue against a decision already accepted rather than merely being
unattractive.

**Option C — scope the refusal to the entries that can reach a base (recommended).** The condition
is a configuration error reported at validation, and it is judged against the invoked entry point:
refused for `ship`, `integrate` and `create_pr`, admitted for `commit`, `push`, `pull`, `merge`,
`land` and `provision`. An entry outside the set that reaches a base-needing operation through a
`run_op` edge gets that operation's own `base_unresolved` at the dispatch.

Three things support it over A and B rather than merely balancing them.

It keeps 0084's guarantee exactly. `ship` is refused before `commit`, so nothing is published by an
invocation that cannot finish — which is the whole of what 0084 bought.

The shape already exists in the document. Section 8.6 scopes `git_access` this way verbatim: "For an
entry that can reach a remote — `provision`, `integrate`, `push`, `pull`, and a front-end sequence
that dispatches one — it is REQUIRED and its absence is refused here; an entry outside the set that
reaches such an operation through a `run_op` edge reports that operation's own `failed`." The
identity precondition is scoped the same way. This is that pattern applied to a value read from the
document instead of one supplied with the invocation.

And it survives the test this branch just wrote. Section 8.6 now separates the two registries by the
artifact at fault: "a configuration error names a defect a consumer repairs by editing a document; a
precondition failure names one it repairs by changing the invocation." A missing base is repaired by
editing a document, so it is a configuration error and belongs in Section 6.10 — not, despite the
entry-point scoping, in Section 8.6 alongside `git_access`.

Its cost is real and should not be minimised: Section 6.10 is currently judged from five inputs and
the entry point is not among them, so option C adds a sixth. The ordering permits it —
`arguments_unreadable` is established before validation (Section 8.6), and decoding the arguments is
what names the entry point, so validation already runs with the entry point known — but "judged from
five inputs and no others" is a sentence this decision would have to rewrite, and that sentence is
load-bearing for `capability_unsupported` and for decision 0092's third input. A sixth input is not
free.

## Decision and reasoning

Recommending **option C**, and leaving this decision `Proposed` rather than `Accepted`: the sixth
validation input is a change to what validation *is*, and that is the specification's owner's call
rather than a reviewer's.

Whichever option is taken, the two forms — no document, and a document with no `[base] branch` —
MUST take the same disposition and the same reason token. They are one state reached two ways, and
splitting them would give a consumer two things to handle where the repair is identical.

Three sub-questions option C still has to answer, recorded so acceptance is not mistaken for
completeness:

- **Which reason token.** Reusing `base_unresolvable` fits its name and would need its Section 6.10
  row and its `vocabulary.json` entry widened beyond the `by_prefix` case. Minting a second token
  distinguishes "no base configured" from "a by_prefix map that resolves nothing", which a consumer
  may not need to tell apart, since both are repaired in the same file.
- **What `status` and `diff` do.** Both are written for a base the checkout does not hold, not for
  one the policy does not select. `status`'s contract is that a read "reports no determinate value
  it did not establish" and still completes, which argues for admitting it with a null base and an
  output saying so; `diff` has no delta to produce at all. They may not take the same answer.
- **Whether `[base] branch` becomes explicitly REQUIRED** in Section 6.4, rather than staying
  required by omission. It should — the absence of a `Default:` line is not a requirement a reader
  can rely on — but that is a wording change with its own blast radius into the cheat sheet and
  `SPEC.md` Section 5.6.

**Reconsideration trigger.** Option C's entry-point scoping is worth reopening if a second
configuration condition turns out to need it, because two would mean validation is entry-scoped in
general and the five-input framing should be restated once rather than patched twice. It is worth
reopening in the other direction if a consumer reports being refused a `ship` in a repository whose
policy deliberately carries no base because its work never opens a pull request — that would be
evidence the base-needing set is drawn around operations rather than around what a repository
actually configures.

Relates to 0093 (whose second review finding exposed the gap), 0084 (whose refuse-before-publishing
argument is what option B loses to), 0092 (whose one-directional config/precondition boundary is
what places this in Section 6.10), and 0002 (anchor changes, if `base_unresolvable` is widened or a
token is minted).
