# Background — 0118 A tool that is not there yet is a tool the workspace cannot use

## Context

Issue #62's provisioning item asks the specification to state whether provisioning recurses
submodules, to note that a tool distributed by submodule "arrives **empty** under a shallow
`git clone --depth 1`", to require that any workspace-dependency tool survive a bare shallow clone
with no extra install step, and to specify disk-full degradation. The cross-cutting item adds the
distribution rule: a released binary should be reachable through a pinned release or a vendored copy
rather than a submodule or an extension install.

The study's origin for this is Symphony's own provisioning defaults — `after_create` running
`git clone --depth 1` with no `--recurse-submodules`, against a host whose root filesystem "runs
chronically full".

## What the specification says, and the one place it says something wrong

Two of the three questions are simply unanswered. Section 9.7 and the `ensure_object_store`
algorithm (Section 16.5) show the engine obtaining and refreshing a store and deriving a tree, and
say nothing about submodules or about what happens when the disk fills.

The third is more interesting, because the specification has moved and the issue's framing has not.
Provisioning is **not** `after_create` any more. Section 9.3 states that "repository population and
synchronization are first-class Symphony behavior (Section 9.7), not an implementation-defined hook
concern", and Section 16.5 dispatches the engine's `provision`. The `git clone --depth 1` in a hook
that the study identifies as the root cause is a configuration the current specification has already
moved away from — hooks populate only non-VCS workspaces now.

That is worth recording rather than quietly fixing, because it changes what is owed. The clone depth
and the submodule flag are the **engine's** business (`VCSX-CONTRACT.md`, `VCSX-SPEC.md` Section 9.1
`ensure_store`), not a Symphony hook's. What Symphony owes is not a `--recurse-submodules` flag; it
is a statement of what a workspace is guaranteed to contain when an agent starts working in it, so
that a repository author can tell whether a tool they depend on will be there.

## The requirement stated over the guarantee, not the mechanism

The useful form is a property a repository author can check, and it is the inverse of the failure:

**A tool the workspace depends on MUST be usable from a workspace Symphony provisioned, with no step
the agent has to take first.**

That is checkable without knowing whether the engine cloned shallowly, recursed submodules, or
derived the tree from a shared store — all of which are the engine's determinations and vary by
backend and checkout mode. It also has an obvious test: provision a workspace from scratch, run the
tool, and see whether it works.

From it the submodule question answers itself. A tool distributed as a submodule is not usable from a
workspace whose provisioning did not populate that submodule, and whether provisioning does is the
engine's determination rather than something a repository can rely on — so **distributing a
workspace-dependency tool by submodule does not satisfy the guarantee**, and a deployment that needs
one distributes it as a pinned release the workspace resolves, or vendors it into the tree. That is
the cross-cutting item's recommendation, reached as a consequence rather than asserted as a
preference.

Symphony's part is the one thing the engine cannot state: which of the two halves of provisioning
ran. `ensure_object_store` maintains the store alone and `provision_for_issue` derives the tree
(Section 16.5), and a tool that lives in the repository is present only after the second. An
implementation MUST NOT start an agent session against a workspace whose tree derivation has not
completed — which sounds obvious and is exactly the ordering a failed-but-ignored provisioning step
breaks.

## Disk-full

`ENOSPC` is a provisioning failure and takes that class's disposition (`repository_provisioning_failures`,
Sections 14.1, 14.2): repo-scoped, skip new dispatches for the repository, retry on a later tick,
keep the service alive.

Two things are worth stating beyond the classification, because both are ways an implementation gets
it wrong while looking correct.

A partially written store or tree MUST NOT be presented as a usable one. Section 9.3 already permits
removing a partially prepared workspace and cautions against destructively resetting a reused one;
the addition here is that "the disk filled halfway through" is precisely the case where a directory
exists, looks plausible, and is not what the next step expects.

And the retry is the repo-scoped one that class already defines, not a per-worker backoff. A disk
that is full is not a condition one issue's retry clears, and Section 14.2 already forbids converting
this class into per-worker retries — this is a case where that existing rule is load-bearing rather
than a new requirement.

## Why this is not an extension

It adds no configuration and no mechanism: it states a property provisioning already either has or
does not, and one ordering requirement. There is nothing for an operator to enable, so there is
nothing to make optional — the split-by-cost test does not arise, because the cost is zero and the
alternative to stating it is leaving a repository author unable to tell what a workspace contains.

## Steelmanning: say nothing, because it is the engine's

The argument is that clone depth, submodule recursion and store sharing are all `VCSX-SPEC.md`
Section 9.1's business, and Symphony restating them would duplicate a contract it defers to — which
Section 3.4 and the deferral boundary are explicit about avoiding.

It is right about the mechanism and wrong about the guarantee. Symphony is what starts an agent in a
workspace and tells it to work, so the statement "a tool this workspace depends on is present" is
Symphony's to make or withhold; the engine cannot make it, because the engine does not know what the
repository depends on. Stating the guarantee while naming no flag is what keeps the deferral intact.

## Reconsideration trigger

Reconsider if a deployment satisfies the guarantee only by vendoring large binaries into every
repository, which would mean the pinned-release path is not actually workable and the guarantee is
forcing a bad distribution choice rather than describing a reachable one.

## Relationship to other decisions

It leans on the provisioning ownership 0093 established (the engine owns provisioning) by stating a
guarantee that names no mechanism, and it takes its failure disposition from 0104's failure classes
unchanged.
