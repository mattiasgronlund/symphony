# Background — 0099 The edge is the binding, and a unit at a position that says nothing

## Context

Issue #49 reports two gaps in Section 10.4 and files them together because they are "one section read
twice": a commit diff is scanned and no key says with which profile, and neither the `scan-content`
check nor the `pr_to_squash` transform has a stated disposition when the unit gives no usable answer.
Tracing both through the mechanism produced three findings, and they do not line up one-to-one with
the two reported. One ask is larger than filed, one is already covered, and one supporting premise is
wrong.

### A scan is bound to a unit two ways, and the document reconciles them nowhere

The issue asks for a third key beside `title_scan` and `body_scan`. The prior question is how any of
the three reaches a program, and the document answers it twice.

**As a hook.** Section 6.5's own worked edge example is the scan:

```toml
[[policy.edge]]
on = "before:commit"
do = "run"                     # run a hook
hook = "scan-content"          # a hook name (Section 6.6)
```

and Section 10.1 calls it "the repository's `scan-content` hook (Section 6.6)". Under this reading the
edge is the binding, the commit diff needs no key at all, and `title_scan`/`body_scan` are the
anomaly.

**As a profile.** Section 6.8 declares `title_scan = "strict"` and `body_scan = "relaxed"`, and
Section 10.4 says profiles "are names a repository binds to its own checks". Nothing states how
`strict` resolves to a unit, and nothing states who dispatches it. Under this reading the diff is
missing a key, which is what the issue reports.

Both readings are supported by the text and neither is written down, which is what makes the reported
fix insufficient rather than merely small: a repository writing `diff_scan = "strict"` would still
have no stated way to make `strict` mean anything, and no answer to whether a scan runs at a position
no edge binds — which Section 5.4 currently calls a benign no-op.

Measured against the document on 2026-08-16 with `grep -rn "title_scan\|body_scan"` (GNU grep 3.11):
five occurrences outside `decisions/` — two in Section 6.8's example block, one in Section 10.2's
prose, and two token entries in `conformance/vcsx/vocabulary.json` under
`kind: "scan_profile_binding"`. No occurrence states a resolution rule. `grep -rn "template_unbound"`
returns eight, three of them in `conformance/`, which is the comparison that made the retirement cost
of the generalizing option concrete.

### The scan half of the second gap is already covered

The issue argues `hook_unanswered` is unavailable to a scan because Section 10.4 positions title/body
scanning "during `create_pr`", not at a `before:` hook that could block, so borrowing the token "would
report a gate that never ran".

The premise does not survive the next paragraph of the same section, which says "the title and body
scanned **at `before:create_pr`**". Section 10.1 places the commit scan at `before:commit`, Section
6.5 dispatches it with a `run` edge, and Section 6.6's bound is stated over hooks. A scan is a
`before:<op>` hook, so the bound, `hook_unanswered` and `outputs.unanswered_gates` all reach it
already. What is defective is one sentence: "during `create_pr`" where the surrounding text means the
position, in a clause that is really about execution context rather than about position.

That costs the second ask half its scope, and is worth stating plainly rather than quietly
implementing the larger version.

### The transform is genuinely uncovered, and one argument for it does not hold

`pr_to_squash` is named by `[messages.squash]` `transform`, is called "a repository unit" in Section
10.3, and is never called a hook. Section 6.6's bound is stated over hooks, so **nothing bounds the
transform**: an engine that waits forever for one is conforming. The issue does not name this half,
and it is the worse one — an unbounded wait holds the invocation open where a stated disposition at
least terminates.

One supporting argument in the issue does not hold. It says a fallback to the pull request's own body
would publish "into the one place Section 11 says no operation rewrites afterwards". Section 11's
guarantee is over the **work branch**, and it says in as many words that a squash strategy "is not an
exception: it writes to the base branch". The case for a stated disposition stands without that
citation and is made below on its own terms.

### A configured unit bound to nothing already has a home the issue does not use

The issue lists "a configured profile with no unit bound" among the conditions a scan cannot
distinguish, and the reporting implementation blocks on it at runtime. Section 6.11 already refuses
the same shape for the `template` body source, as `template_unbound`, and gives the reason: a template
is a repository unit rather than an action, so an engine judging only the document would defer it to
first use — and a policy that cannot compose a body would then publish a work branch before saying so.
The fifth validation input it turns on is already general: "the repository units the consumer bound".

A transform is a repository unit in exactly that sense and its first use is **later** than the
template's — the `merge` a `land` reaches only after the pull request is open — so the argument
Section 6.11 makes for the template applies to the transform with more of the flow already published
behind it, not less.

## Options considered

**For the binding — complete the table, or remove it.** Completing it is the issue's own shape: add
`[messages.commit] diff_scan`, and write the missing resolution rule. It keeps `VCSX-CONTRACT.md`
Section 9's per-field claim — "the title is scanned strictly; the body is scanned with the tracker-key
relaxation the code host's integration needs" — expressible as schema, which is a real property: a
reader of `repo.policy.toml` sees which profile guards which content without opening a unit. That is
the strongest thing to be said for it, and it is not nothing.

It loses on two counts. It gives one kind of unit two dispatch mechanisms, where every other unit the
engine hands control to at a position is reached by an edge. And it puts an exception into Section
5.4: a position no edge binds would still run a scan, so "an unmatched lifecycle position is a benign
no-op" would need a carve-out written for one key family. The capability it preserves survives the
removal in any case — a repository that wants strict titles and relaxed bodies writes one unit at
`before:create_pr` that applies each, which Section 10.4 already assigns to the repository when it
says the engine ships no scan rules. What is lost is the declaration, not the behavior.

A third option was considered and rejected as the largest: keep one `scan-content` hook per position
and pass the configured profile name and content kind *to* it as arguments, `diff_scan` completing the
argument set. It preserves both the single dispatch mechanism and the schema-level declaration. It
costs an argument-passing surface the specification does not have — Section 6.6 fixes what a hook may
not receive (credentials, integrity values) and says nothing about what it does receive — which is a
larger addition than either alternative, in the section hardest to keep language-neutral.

**For the transform's disposition — reuse the reason, mint one, or leave it Implementation-defined.**
Minting `merge:transform_unanswered` keeps `hook_unanswered` meaning "a gate" and lets a repository
binding an edge tell a broken gate from a broken laundering step; they are different units and the
repairs point at different files. Section 4.3 argues the other way for its own three conditions — one
reason where the repair is the same shape, the condition carried as diagnosis — and the shape here is
the same: the engine got no usable answer from a unit it ran at a position, and the condition token
already says which way.

Leaving it `Implementation-defined` with only a prohibition on falling back to the pull request's own
content is the cheapest and closes the case that corrupts. It leaves two conforming engines differing
on whether the merge fails or the flow parks, leaves a repository unable to bind an edge to the
condition, and leaves the bound gap open unless stated separately.

**For the unbound unit — a reason per condition, one generalized reason, or first use.** Generalizing
to `unit_unbound` and retiring `template_unbound` has the better abstract argument, the same one
Section 4.3 makes: one reason where the repair is the same shape. It was rejected on cost and on what
the token buys. `template_unbound` appears in `VCSX-SPEC.md`, `conformance/vcsx/vocabulary.json` and a
`policy-validation` vector, and the generalization would make a consumer branch on a reason that no
longer says which unit is missing, moving that into `message` — which Section 8.2 reserves for prose
nothing parses. Leaving it to first use was rejected on Section 6.11's own argument, which the
transform strengthens rather than weakens.

## Decision and reasoning

**The edge is the binding.** `title_scan` and `body_scan` are removed. A scan is declared as a hook
and run by a `[policy]` edge at a lifecycle position, exactly as every other unit the engine hands
control to at a position is, and `[messages]` carries no scan key. The commit diff therefore gets no
key: the gap closes by removing the asymmetry rather than by completing it, and the three contents are
bound alike. An edge naming a hook nothing declares is already `unknown_hook`, so no new configuration
reason is needed for a scan.

Section 10.4 gains the sentence that was missing under either reading — what the engine supplies at
each position, mirroring Section 10.3's "the engine supplies only the position and the pull-request
content": the commit message and the diff the commit would record at `before:commit`, the composed
title and body at `before:create_pr`.

**The transform is a unit at a position and reports `hook_unanswered`.** Section 6.6's bound is
restated to reach every unit the engine runs at a lifecycle position and waits on, which is what makes
the transform terminate at all; Section 4.3's gloss widens from "a `before:<op>` hook" to a unit the
engine ran at a `before:<op>` position. A transform that gives no usable answer yields
`merge:hook_unanswered` and **the operation does not act** — stated as the effect a consumer can check
through `pr_state`, that the pull request is not merged, rather than as "the forge is never asked",
which is a claim about a call and readable only from the engine's own trace. The `spec-guarantee` test
is what rejected the second phrasing; the issue and the reporting implementation both use it.

The prohibition on falling back to the pull request's own title and body is deliberately **not**
stated as a separate MUST NOT. It is subsumed: an operation that does not act publishes no message, so
a second clause would restate the first in a weaker, later-checkable form. Both ends quantify over the
same thing.

**`transform_unbound` joins `template_unbound`.** A `[messages.squash]` `transform` naming a unit the
consumer bound nothing to is refused at validation, judged from the fifth input that already exists
for the template. A `[messages.squash]` naming no transform is not this condition and is not refused —
it names no unit, so nothing is unbound, and the code host composes the squash message.

**What this decision does not close, verified rather than assumed.** Section 9.2's merge capability is
`request_merge(pr, strategy, expected_head)` and takes **no message**. Nothing in Section 9.2, the
descriptor fields, or Section 12.3 carries the transform's output to the forge, so the seam Section
10.3 describes has no route to the operation that would use it. That is a defect in the plugin API
rather than in the scan or the disposition, it predates this issue, and closing it raises questions
this decision has no answer for — whether a message accompanies a non-squash strategy, and whether a
forge that cannot set a squash subject declares the capability at all. It is recorded here and left
open rather than smuggled in, and the disposition above is unaffected by it: a transform that gives no
usable answer leaves the pull request unmerged whether or not a usable one could have been delivered.

**Reconsideration triggers.** Reopen the binding if a repository is found that needs a scan profile
named in configuration rather than in a unit — the evidence is an operator who must read a repository
program to learn which content is guarded, in a deployment where reading that program is the thing the
trust boundary is meant to avoid. Reopen the single reason if a repository binds an edge to
`merge:hook_unanswered` and needs to route a broken transform differently from a broken gate, which is
the one case the shared token cannot express. Reopen `transform_unbound` if the merge capability gains
a message parameter and the transform stops being optional, since a required unit and an optional one
are refused on different terms.

Relates to 0081 and 0086 (which minted the bound, `hook_unanswered` and the three condition tokens
this extends), 0098 (whose derived hook context is what makes a scan's context follow its artifact),
0057 (which introduced the universal reasons) and 0002.
