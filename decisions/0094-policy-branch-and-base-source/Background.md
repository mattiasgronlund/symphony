# Background — 0094 The policy branch is not the base branch

## Context

This decision was opened narrowly and grew twice under review. It began as "what happens when
`repo.policy.toml` determines no base branch", became "where does the base branch come from", and
ends as "the branch the policy is read from is not the branch pull requests land on". The first
framing is preserved below because the path is the argument: each reframing was forced by a defect
the previous one exposed.

### The defect that decided it

`SPEC.md` Section 15.4, echoed verbatim in `VCSX-CONTRACT.md` Section 10, is the whole security
argument for anything the engine runs on the host:

> Host-side-executed Way of Working — host-side hooks, the operation flow, and the branch-name
> pattern (`repo.policy.toml`) — is read from the resolved **base revision**. The agent cannot push
> to the base branch (it is review-gated by branch protection), so it cannot alter host-side
> behavior from within a run. Way-of-Working trust equals base-branch trust.

`VCSX-SPEC.md` Section 6.4 puts `[base] branch` inside `repo.policy.toml` — the file that sentence
reads from the base revision. **To read the policy you need the base; to know the base you need the
policy.** No document says how that first read resolves.

It is not benign. The only way to break the cycle in place is to read the policy from whatever the
checkout currently holds, find the base there, and re-read — which lets an agent-editable revision
decide which revision is trusted, destroying the property the rule exists to provide.

This is the fourth instance of the cycle this branch has been chasing. Decision 0092 found that the
values needed to *obtain* a repository cannot be configured inside it; 0093's review found the same
shape in control flow (a policy gate cannot guard the operation that produces the policy) and in the
invocation pipeline (validation cannot read a repository that does not exist yet). This one is the
sharpest, because the other three cost availability and this one costs a security guarantee.

### The defect the repair exposed, which is worse

Stating the trust argument in full shows it standing on two legs, and only one of them holds.

**Leg one — the agent cannot push to the base branch.** True, and already guaranteed without any
configuration: `SPEC.md` Section 10.8's scope guard constrains every brokered operation to the run,
"push only to the run's work branch", and Section 9.9 pins the push refspec and refuses
agent-specified refs. A scope violation fails the run outright.

**Leg two — the base branch is review-gated by branch protection.** This is the weak one, and it is
weak specifically because of what Symphony is for. *Landing pull requests on the base branch is the
service's entire purpose.* The agent's work reaches the base branch through a merge Symphony itself
performs. So the trust root is a branch the service routinely writes to, and the only thing between
an agent-authored edit to a host-side hook and its execution with the operator's credentials is a
human noticing it in review. `SPEC.md` Section 9.8 already worries about the adjacent case,
requiring the push/PR actor be distinct from the approver so a pull request cannot be self-approved
— the same concern, one step short of this one.

**The measurement that shows nobody was looking at this.** All 32 vectors in
`conformance/vcsx/vectors/policy-validation.json` supply `base.branch`, including every vector whose
subject is something else — version floors, hooks, edge cycles. Re-run with:

```sh
python3 -c "import json; d=json.load(open('conformance/vcsx/vectors/policy-validation.json')); \
print(sum('branch' in v['given'].get('policy',{}).get('base',{}) for v in d['vectors']), 'of', len(d['vectors']))"
```

A required value supplied reflexively as scaffolding in tests that do not exercise it is how both
defects survived review.

### The decomposition

The configured base branch does two unrelated jobs:

- **Trust root** — the revision host-side policy is read from. Needed *before* the policy is read.
- **Pull-request target and merge source** — where pull requests land and what `integrate` brings
  into the work branch. Needed *after* the policy is read.

Only the first is circular, because only the first is needed to perform the read that would tell you
what it is. Separating them fixes the circularity *and* removes Symphony's own merges from the path
to the trust root, which is the larger of the two repairs.

## Options considered

**Option A — leave the base in `repo.policy.toml`; answer only the missing-value question.** The
decision's original scope. Rejected: it leaves both defects open, and the missing-value question is
not independently interesting once the value's home is wrong.

**Option B — move the single base value out of the policy to the consumer.** Fixes the circularity
and nothing else. Its steelman is real — one concept, one value, no new vocabulary, and it follows
0092's precedent exactly. It loses because the trust root remains a branch Symphony merges into, so
the guarantee still rests on reviewer vigilance rather than on structure. Fixing a cycle while
leaving the escalation path is the smaller half of the available repair.

**Option C — separate the two jobs (chosen).** The operator names a **policy branch**, which the
policy's host-side parts are read from and which no pull request Symphony creates or merges ever
targets. The **pull-request target** becomes an ordinary configuration question, answerable from
three sources, because reading the policy no longer depends on it.

C costs a concept: two branch-shaped values where there was one, and a policy that lives on its own
branch cannot be reviewed alongside the code change that needs it, and can drift from the main line.
That cost is accepted because it is the cost of the guarantee — a trust root that cannot be reviewed
alongside a code change is a trust root a code change cannot alter.

## Decision and reasoning

Option C, with the shape below.

**The policy branch.** Operator config names it. It is REQUIRED with no default. The specification
states that no pull request Symphony creates or merges targets it — stated as a property of what
Symphony does rather than as a constraint on the configuration, so a consumer can check it through
the operations rather than by inspecting a config file. It MUST be a branch the agent cannot write
to; how an implementation establishes that is `Implementation-defined` and MUST be documented, since
branch-protection state is not uniformly exposed across forges. The scope guard already makes the
agent's *push* path impossible, so the documented obligation covers the paths the guard does not:
who else can write to it, and by what route.

**The pull-request target.** Three permitted sources, in precedence order: **the invocation**, then
**operator config**, then **`repo.policy.toml`**. Most specific wins, which is how the specification
resolves layered configuration elsewhere. The policy keeps a legitimate say — including the existing
`by_prefix` track-aware mapping — because reading it no longer depends on the value.

**The bound.** An operator MAY state which targets an invocation may name. An invocation naming one
outside the bound is refused. This is weaker than the trust-root case and deliberately so: a badly
chosen target reaches the in-sandbox parts, which run without credentials and without host access,
rather than host-side hooks running with them. The bound exists because the operator should be able
to say "release branches only", not because the alternative is an escalation.

**The carrier.** How a Symphony ticket names a target is `Implementation-defined` and MUST be
documented — a label mapped by operator config, a dedicated field, or something tracker-specific.
The specification fixes that a per-issue target MAY be supplied and MUST be bounded, not the shape
of the field, which is the same treatment `SPEC.md` gives other tracker-shaped variation.

**When nothing supplies one.** Refused before anything runs, and only for the entry points that need
a target — `ship`, `integrate`, `create_pr`. `commit`, `push`, `pull`, `merge`, `land` and
`provision` run normally, none of them reading it. This is a **precondition** failure rather than a
configuration error, and the reframing is what makes that clean: Section 8.6's own test asks what
the caller must change, and a target absent from an invocation is repaired by changing the
invocation. The original framing would have made it a configuration error and forced validation to
take the entry point as a sixth input — the change to what validation *is* that left this decision
`Proposed` through two drafts. That cost is gone; Section 8.6 already scopes preconditions by entry
point.

Refusing up front rather than at first use preserves decision 0084's guarantee. Section 12.2's
`ship` runs `commit`, then `push`, then `create_pr`, and the target is not read until the third, so
a run-time failure means the work branch is already published. 0084 called that its strongest
argument and moved a check earlier to prevent it.

**Assumption recorded.** The decision sheet's question on whether the policy branch should carry a
default was left unanswered. It is taken as REQUIRED with no default, because the answer given to
the primary question chose "the trust root is never a merge target" over the variant that defaults
the policy branch to the operator's main branch — and any default resolving to the main branch makes
the trust root a merge target, voiding that guarantee. If the intent was the gentler adoption path,
this is a one-key change and the guarantee becomes opt-in.

**Reconsideration triggers.** Reopen the policy branch's REQUIRED status if operators report the
two-branch workflow unworkable for small repositories — the evidence being policy branches that have
drifted far enough from the main line that host-side hooks no longer match the code they run
against. Reopen the three-source precedence if a deployment needs the operator to *override* rather
than be overridden by an invocation, which would mean the bound is doing work the precedence should
do. Reopen the whole decomposition if a forge appears whose protection model makes a
non-merge-target branch harder to secure than a protected merge target.

Relates to 0092 (whose consumer configuration receives the policy branch and the target default),
0093 (whose review exposed the original gap), 0084 (whose refuse-before-publishing argument fixes
where the refusal lands), 0085 (the same consumer-owns-the-coordinate reasoning one value over), and
0002 (anchor changes).
