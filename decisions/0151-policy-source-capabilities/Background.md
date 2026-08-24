# Background — 0151 Reading and materializing the policy source

## Context

Issue #110, second of two decisions. Decision 0150 took `worktree_diff()`, which depends on nothing;
this one takes the two that turn on `load_policy` — and, like its sibling, the strongest form of the
finding is that an engine has already had to invent them. `read_at_source(remote, branch, path)` and
`export_source(remote, branch, into)` exist in the `symphony-rs` VCS backend trait
(`crates/vcsx-engine/src/backend.rs:576`, `:600`), arrived with that build's decision 0047, are
implemented by two backends, and are published under Section 13.3 as that engine's own. The
specification is being asked to name capabilities its own text requires, not to speculate about ones
it might.

## 1. Reading a file at a revision

Section 4.1, on `load_policy`:

> It reads `repo.policy.toml` from the policy source (Sections 6.1, 8.1), merges any `vcsx.toml`, and
> returns the surface … This is the operation that makes Section 3.2's "the consumer sources config by
> trust" literally true, and it is why no capability of Section 9.1 reads a file at a revision — one
> operation does it once, rather than a capability doing it per read.

That sentence explains why there is no *per-read* capability. It does not supply the one read the
operation makes. Section 8.1 makes the source a revision under the default mode — the policy branch
is "the revision the engine reads the host-side parts of `repo.policy.toml` from" — and under
`target_branch` it is the pull request's target. No capability in Section 9.1 reads a file at a
revision, and the list is closed enough to make that checkable: "The network-touching capabilities
are exactly `ensure_store`, `fetch_base`, `fetch_counterpart` and `push` … Every other capability
above is local to the checkout."

Section 9.1's realization paragraph maps `provision`, `integrate`, `pull`, `commit` and `status`
onto capabilities. **`load_policy` maps onto none** — not Section 9.1, not Section 9.2 — while
Section 4.1's opening sentence says "Operations are the unit `run_op` runs (Section 5.2). **Each is
realized through the plugin layer** and returns a typed result." Section 9.1's closing paragraph
makes the claim outright: "every operation Section 4.1 defines is realizable through it". It is
false, in the section the repair edits.

**Decision 0141 removes the premise the excuse rests on.** Under the fingerprint pin, `load_policy`
is an entry point and every invocation reads and validates the document itself rather than the
consumer holding a surface and supplying it onward. So `read_at_source` is not "the one read
`load_policy` makes"; it is the read **every entry point** makes, once per invocation — which is
precisely the per-read shape Section 4.1's sentence says does not exist. The case is written from
the post-0141 text, and the two sentences that become false go in the same commit: Section 4.1's "no
capability of Section 9.1 reads a file at a revision", and Section 9.1's "every operation Section
4.1 defines is realizable through it".

### The second half of the same read: `vcsx.toml` has no address

`load_policy` reads two files, and only one has a stated location. Section 6.1 fixes
`repo.policy.toml`'s path relative to the repository root and its discovery precedence as
`Implementation-defined` and MUST document. For `vcsx.toml` it states **no location and no discovery
rule at all** — only "An engine-native `vcsx.toml`, when present, is merged into the same surface".

So "read the policy at the revision" is one call or two, and the second has no addressable path. The
`symphony-rs` build answered it silently: `Source::read` reads `repo.policy.toml` and then
`vcsx.toml` through one capability with a `path` argument, and puts the second at the repository
root beside the first — "one constant next to another (`crates/vcsx-cli/src/source.rs:41-43`),
decided by nobody, documented nowhere, and unfalsifiable by a consumer".

**The harm is not a differing fingerprint.** An earlier statement of this on the issue thread said
"the same repository yields two different pins and neither engine is wrong", and that is not the
harm: two engines never compare pins, the value is opaque and engine-established, and the only party
that reads one is the engine that issued it. The harm is one layer up and worse — **two conforming
engines merge different documents from one revision and therefore execute different policies**, of
which a differing pin is a symptom nobody can see. The repair is therefore owed on Section 6.1's own
terms rather than as a dependency of the pin: a path fixed relative to the repository root,
discovery precedence `Implementation-defined` and MUST document, and a row modelled on the
template's existing `repo.policy.toml discovery precedence | 6.1`. That it surfaced through the pin
is worth recording; that it is a pin defect is not.

## 2. Materializing a revision

Section 6.6, on where a `host_side` unit comes from:

> A `host_side` unit resolves from the **same source the host-side policy was read from**, and MUST
> NOT resolve from the working tree. … The engine MUST NOT run a `host_side` unit with the working
> tree as its working directory; it supplies the working tree's location to the unit instead.

A revision is not a directory, so an engine that runs a host-side hook has to make one from that
revision. Section 6.6 delegates the mechanism — "How an engine resolves a `host_side` unit is
`Implementation-defined` and MUST be documented (Section 13.3)" — and the mechanism needs the
backend, because getting a tree out of a revision is the backend's knowledge. Section 9.1's
`derive_working_tree(store_location, tree_location)` derives from the store `ensure_store`
maintains, takes no revision, and nothing else comes close.

The `into` argument earns its place for a reason the specification cannot derive and an
implementation can: `git` and `jj` materialize a revision differently enough that the engine cannot
own the mechanism, but both can be handed a location to put it. That is the same reason Section 6.6
delegates the mechanism today, stated one layer down where a backend can answer it.

### It is OPTIONAL, and the condition is per engine rather than per unit

Section 6.6 fixes the unit's form as `Implementation-defined`. An engine whose `run` form is a
registered task the consumer named, or a shell string carrying its own text, resolves a `host_side`
unit from the declaration itself — the text came from the trusted revision — and materializes
nothing. So a **required** capability would be one a conforming engine never calls, which is worse
surface than no capability.

The shape that fits is an **OPTIONAL capability with a descriptor field**, exactly parallel to
Section 9.1's existing "whether it can derive more than one working tree from one store". A backend
that cannot export declares so; a merged surface declaring a `[hooks.engine]` unit against such a
backend is refused at validation with `capability_unsupported`. That lands on Section 9.3's
*determinable* half — the backend declaration is static and the hook declaration is in the document,
both held before the policy runs — so it creates no new first-use producer and leaves the template's
Section 6.2 demonstration table alone.

**The condition is stated over the engine, not over the unit.** Scoping it to "unit forms that
resolve to paths in the source" is not decidable: a unit form that is a command line — the
`symphony-rs` engine's is `Hook { run: Option<String> }`
(`crates/vcsx-config/src/policy.rs:258-260`) — may or may not name a path in the trusted revision,
and nothing in the string says which. A per-unit condition therefore cannot be evaluated from the
specified configuration, which is the test issue #100 turned on, one document over. A **per-engine**
one can: the engine's declared unit form is static and published under Section 13.3, and it pairs
with the backend's descriptor field to make the refusal determinable before the policy runs.

So an engine whose unit form is a command line declares the capability and **always calls it** — the
`symphony-rs` build materializes wherever the policy declares any `[hooks.engine]` unit and not
otherwise, and states the cost rather than hiding it: "a repository declaring a hook pays one export
of the policy source per invocation, whether or not the flow reaches an edge that runs one". The
objection "a required capability a conforming engine never calls is worse surface than no
capability" reaches a registered-task form and does not reach a shell-string form. That is the
argument for OPTIONAL, stated over the right thing.

Section 9.3's "What remains on the first-use side is an OPTIONAL capability (Section 9.2)" widens
with it: this is the first OPTIONAL capability in Section 9.1, and that sentence names Section 9.2
only because that is where the only OPTIONAL capabilities are today.

## The ordering check that has to be written down rather than implied

Both capabilities read a copy the checkout already holds, take neither the access parameter nor the
credential, and acquire nothing — so Section 9.1's network enumeration stays at four. That is right
**conditionally**, in a way Section 9.1 cares about, because it says a capability's context is "read
off this list and never inferred from its arguments":

A read of the policy branch is credential-free **only because `provision` precedes it**. Section 4.1
places `provision` "before everything the engine reads out of the repository", so the copy Section
8.1 requires — "it resolves to the copy belonging to the resolved `remote`", never a local branch of
that name — is already in the store. The consequence is already accepted elsewhere: Section 13.1
records that "a change to the policy source after that does not take effect until the next unit of
work".

Write the ordering down when the capabilities are added, or the next reader has to re-derive why a
capability that reads a trusted revision takes no `git_access`. It holds for the materialization as
well as for the read, and for the same reason.

## What the addition buys

While these stay engine-private, each engine names its own and a consumer reads three different
tables. Once they are Section 9.1 capabilities they come under Section 9.3's descriptor discipline
and Section 6.11's `capability_unsupported`, so a backend lacking one produces a **reported refusal
at validation** instead of an engine-defined failure at first use. In an engine whose Section 6.1
backend table is generated from its own configuration and asserted against each plugin's descriptor
by a test, a capability arriving in Section 9.1 stops being a row of prose and becomes a declared
field with a test behind it. That is the difference worth having, and it is why decision 0149's
reworded row is a bridge rather than a destination.

## Options considered

### Record deliberately that the two stay engine-private

The status quo plus decision 0149: the reworded `Required by` row makes each engine's requirement
visible, and the specification says nothing. It is the smallest possible answer and it is honest —
the row does tell a backend author that the capability is load-bearing.

It loses on portability and on the refusal. Three engines name one requirement three ways, and a
consumer comparing two Statements cannot tell that they are the same capability. And a backend
missing one gets an engine-defined failure at first use, where Section 6.11's
`capability_unsupported` at validation is exactly the disposition the specification already defines
for this shape.

### Make `export_source` REQUIRED rather than OPTIONAL

Simpler: no descriptor field, no widening of Section 9.3's sentence, one fewer refusal path. It
loses on the case it would impose: an engine whose unit form is a registered task never calls it,
and every backend would carry a capability that engine's policies never reach. A required capability
a conforming engine never calls is surface with no reader.

Field cost, from the implementation reply to PR #114: both of that engine's plugins implement
`export_source` as required today, so the OPTIONAL form with a descriptor field is the one shape
change this decision asks of that build — reported there as small, and buying a
`capability_unsupported` raised at validation rather than a failure at first use. The option is
rejected on the surface-with-no-reader argument rather than on cost; the cost is now measured rather
than assumed. The reply also confirms the two signatures this decision names, `read_at_source`'s
three answers included.

### State the export condition per unit rather than per engine

"Materialization is required only for unit forms that resolve to paths in the source" — narrower,
and it would let one engine materialize for some hooks and not others. It loses because it is not
decidable from the specified configuration: a command-line unit form carries no statement of whether
it names a path in the revision. That is issue #100's test, and failing it is what makes a condition
a wish rather than a rule.

### Give `read_at_source` a revision parameter the engine names

Rather than `(remote, branch, path)`. It loses because the document holds branch names opaque
(Section 8.1 says so three times) and hands a backend no revision today; the natural signature takes
the policy source as the document already describes it — a remote and a branch — and a path.

### Fold this into decision 0150

Rejected there for the same reason it is rejected here: the two halves rest on different premises,
and folding them records `worktree_diff()`'s reasoning as a rider on a Background about
`load_policy`.

## What was checked

At `22b5194`, against the working tree:

- Section 4.1's `load_policy` bullet carries the "no capability of Section 9.1 reads a file at a
  revision" sentence verbatim; Section 9.1's realization paragraph names `provision`, `integrate`,
  `pull`, `commit` and `status` and does not name `load_policy`; Section 9.1's closing paragraph
  carries "every operation Section 4.1 defines is realizable through it".
- Section 6.1 fixes `repo.policy.toml`'s path relative to the repository root with
  `Implementation-defined` discovery precedence, and says of the sibling only "An engine-native
  `vcsx.toml`, when present, is merged into the same surface; `repo.policy.toml` keys take
  precedence on conflict."
- Section 6.6's host-side resolution rule and its `Implementation-defined` delegation are verbatim
  as quoted; `derive_working_tree(store_location, tree_location)` derives from the store and takes
  no revision.
- Section 9.1's descriptor fields are "supported modes, whether `merge_base` can reuse recorded
  conflict resolutions, whether the backend can operate in a workspace with no colocated remote, and
  whether it can derive more than one working tree from one store" — the last being the OPTIONAL
  precedent this decision follows.
- Section 9.1's network enumeration and its "read off this list and never inferred from its
  arguments" sentence are verbatim as quoted; `resolve_base_ref(remote, branch)` is the existing
  local capability taking a `remote`.
- Capabilities are **not** a group in `conformance/vcsx/vocabulary.json`; `CLOSED_GROUPS` in
  `scripts/validate_spec_consistency.py` closes `operations` and `lifecycle_positions` only. Nothing
  is owed the registry.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 6.1's backend table carries four declaration
  columns, the last being "Derives >1 working tree from one store".
- `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## On vectors

No vector is added, for the reason decision 0150 records: capability behaviour is not vector-shaped
here, and the Section 9.3-plus-`capability_unsupported` half is what makes the addition checkable.
The `vcsx.toml` location, by contrast, is checkable in Section 13.1 as a property of the merged
surface.

## Reconsideration triggers

- **An engine that reads policy without `provision` preceding it.** The credential-free placement of
  both capabilities rests on the store already holding the copy; a consumer that reaches a revision
  directly would move them onto the network side, and the enumeration would have to move with them.
- **A unit form that makes the export condition decidable per unit** — a declared form that states
  whether it names a path in the source. That would make the per-engine scoping coarser than
  necessary, and the narrower condition would deserve a second hearing with the decidability
  objection answered.
- **A second OPTIONAL capability in Section 9.1.** The widening of Section 9.3's first-use sentence
  is written for one; a second would be the point to state the rule over the class rather than over
  the instance.
- **`vcsx.toml` gaining a role beyond the merge** — a per-engine surface with its own precedence
  rules. The fixed location is stated as the minimal repair on `repo.policy.toml`'s precedent; a
  larger role would need its own discovery reasoning rather than the sibling's.
