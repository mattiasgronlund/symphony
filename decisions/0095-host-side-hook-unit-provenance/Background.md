# Background — 0095 A host-side hook's unit comes from the trusted source

## Context

Decision 0094 established that host-side Way of Working is read from a branch the agent cannot
reach. Reviewing what that actually secured turned up that it secures the **declaration** and not
the **program the declaration names**.

Two sentences, both older than 0094, put the executable back in the agent's hands.

`SPEC.md` Section 15.4, in the hook implications:

> Hooks run with the workspace directory as their working directory.

That is all hooks, both execution contexts. So a host-side hook's working directory is the per-issue
workspace — the working tree the agent edits and commits in.

`VCSX-SPEC.md` Section 8.6, explaining what validation cannot judge:

> Whether the unit a `run` names exists and can be started is **a property of the worktree** rather
> than of the document.

So the specification does not merely permit a host-side hook to execute repository content. It
locates the unit in the worktree and points the hook's working directory at it.

**The chain, with no attacker cleverness in it.** An operator writes, on the policy branch:

```toml
[hooks.build-check]
context = "host_side"
run = "./scripts/check.sh"
```

`./scripts/check.sh` resolves in the workspace. The agent writes that file. It executes on the host,
outside the sandbox, in the operator's context.

No branch is manipulated, no pull request merges, no reviewer is fooled. And it is not a contrived
misconfiguration: a relative path into the repository is the obvious way to write a host-side hook,
and Section 6.6's own example is `run = "..."` with no statement of where the unit lives.

**Why this outranks the other open findings.** The fallout review left four. Three of them —
`policy_branch == base_branch` unrefused, no which-copy rule, no `policy_branch_missing` — require
either a misconfiguration or a specific checkout arrangement before they bite. This one requires
only that a deployment use a host-side hook at all, which is the normal case, and it defeats the
entire trust argument rather than weakening it.

**What 0094 changed.** Nothing, mechanically — both sentences predate it. What changed is
legibility: 0094 is what established that host-side declarations are trusted, and securing a
declaration whose unit is untrusted is what makes the gap visible. Recording it here rather than as
a 0094 review finding, because 0094's reasoning is sound and complete for what it decided; this is
an adjacent defect its repair exposed.

## Options considered

**Option A — forbid a host-side hook from touching the repository.** Total, and trivially checkable
if the workspace is simply not mounted where the hook runs. It loses on what host-side hooks are
*for*: a content scan or a build check exists to read the working tree, and a rule that forbids
reading it removes the reason to have the category. The distinction that matters is not access but
**whether the tree is read as data or executed as code**, and option A cannot express it.

**Option B — leave it to deployment hardening.** Section 15.5 already advises implementations to
harden the harness and evaluate their own risk profile. Its steelman is that hook execution
environments genuinely vary, and a specification that fixes one may not fit. It loses because
Section 15.5 is SHOULD-level guidance about a deployment's own risk appetite, while this is a
property the specification's own trust argument depends on: Section 15.4 concludes "Way-of-Working
trust equals policy-branch trust", and that conclusion is false unless the unit is policy-branch
sourced. A guarantee stated in one section and left to guidance in another is not a guarantee.

**Option C — constrain the unit's provenance and the hook's working directory (chosen).** Four
parts, because the hole has two halves and each needs both a rule and a way to check it:

- the unit resolves from the trusted source, never from the working tree;
- a host-side hook's working directory is not the workspace;
- the workspace path is supplied to the hook as an argument or environment value;
- an implementation MUST document how it resolves a host-side unit.

The third is what keeps option A's cost off: the scan still gets pointed at the tree it inspects.
The second is what stops the first being defeated by accident — a lifecycle hook's body is an inline
shell string, so it is trusted when policy-branch-sourced, but a relative invocation inside it
reaches agent content unless the working directory moves. The fourth is what makes the other three
checkable, since the unit's form is already `Implementation-defined`.

## Decision and reasoning

Option C, with the rule stated in both documents and neither borrowing the other's vocabulary.

**The engine states it without branches.** `VCSX-SPEC.md` Section 3.2 is deliberate that the engine
labels context and the consumer does sourcing: "`vcsx` labels each policy edge and hook with its
context but does not itself enforce the sourcing rule; the consumer sources config by trust." So the
engine says a host-side hook's unit resolves from *the same source the host-side policy came from*.
That is branch-free, correct in `engine-direct` where there is no sandbox, and does not put a
Symphony concept in the engine's vocabulary.

**`SPEC.md` names the source.** For Symphony that source is the policy branch, so Section 15.4
states it there, where the policy branch exists.

The context keeps its existing names, `host_side` and `in_sandbox`. Naming it for its provenance —
`policy_branch` — was considered and rejected on the layering above: the engine has no notion of
branches, and the name would be meaningless in the topology that has no sandbox to be outside of.

**Recorded as considered and not done: a rule against conditioning credentialed work on an
in-sandbox gate.** The argument for one was that a `before:*` hook's outcome is a trigger, the
action-policy machine is trusted, and `run_op` can dispatch operations the broker does not expose —
so an agent controlling a gate could cause credentialed work it could not request.

Checking the broker's verb set defeats the argument. `SPEC.md` Section 10.8 exposes `push`,
`back-merge`, `pr`, `request-merge` and the optional review writes. Those cover `push`, `integrate`,
`create_pr` and `merge` — every credentialed operation of Section 4.1 except `pull`, and
`provision`, which the broker MUST NOT carry and which an in-sandbox edge is already denied
credentials for. So an agent that steers a gate obtains almost nothing it could not obtain by
asking, and a rule forbidding the pattern would forbid `commit:ok → run_op push`, which is the
ordinary flow.

What survives is narrower and is not an escalation: an agent that neuters an in-sandbox gate defeats
a **hygiene control** rather than reaching credentialed work. Section 15.4 already characterizes
that correctly — the agent controls the sandbox, so a gate there was never a control against the
agent. The residue worth watching is the *contributor* path: a merged change to an in-sandbox hook's
unit neuters the scan for later runs, which is a quality regression bounded by review of the output.

Reconsider if an engine defines a credentialed operation beyond Section 4.1 that no broker verb
covers, or if a deployment narrows its broker verb set below Section 10.8's floor; either makes the
gap between what policy can dispatch and what the agent can request wide enough for the rejected
rule to earn its cost.

**Reconsideration trigger for the decision itself.** Reopen if a hook execution model appears in
which the trusted source is not addressable at hook-invocation time — an engine that streams a
policy in rather than resolving it from a revision would have nowhere to resolve the unit from, and
the repair would then be to carry the unit's content rather than its location.

Relates to 0094 (whose repair exposed this), 0093 (whose broker verb set is what defeats the
in-sandbox argument), and 0002.
