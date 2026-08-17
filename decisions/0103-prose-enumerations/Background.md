# Background — 0103 Which prose enumerations are published, and the trigger vocabulary as data

## Context

Issue #54's follow-up comment reports three prose enumerations a conforming implementation must
spell and the registry does not publish — Section 14.1's nine failure classes, Section 7.1's six
orchestration states, Section 7.2's eleven run-attempt phases — and argues, correctly, that the
general answer is one decision rather than four.

Checking the three turned up a fourth set with a stronger case than any of them, an ownership
question an accepted decision had already answered, and a shape question the specification answers
two incompatible ways.

## The rule: publish by reader

Decision 0071 created the registry because a spelling transcribed by hand diverges silently: "an
event renamed upstream changes nothing downstream until someone reads a re-pin diff." So the
question for a candidate set is not whether it is an enumeration. It is **what reads the spelling,
and what happens when the reading is wrong.**

That test was applied without being named — every set in the first slice has such a reader — and
naming it is most of this decision's value, because it turns a deferral list from a place reasons go
stale into a list with one question against each entry that a later reader can re-ask.

**A prose enumeration is published when something outside the implementation's own source spells
it**: a repository author writing configuration, a Conformance Statement author filling a table, or
a conformance check asserting a value. Measured against the document, the candidates are not peers:

| Set | Reader | Cost of a divergence |
|-----|--------|----------------------|
| Section 11.6 run outcomes (5) | a **human** writing `repo.policy.toml` | **silent** — validates, never fires |
| Section 14.1 failure classes (9) | Conformance Statement rows named by class; Sections 17.2, 17.4, 18.1.4, 19 | shows at audit, not at build |
| Section 7.1 orchestration states (6) | Sections 17.4, 18.2 descriptively; absent from Section 13.3's snapshot | nothing catches it |
| Section 7.3 transition triggers (7) | none — internal lifecycle events | nothing catches it |
| Section 7.2 run-attempt phases (11) | none in Sections 17, 18 or 19 | nothing catches it |

Measured with one instrument, which a later reader can re-run:

```sh
python3 - <<'PY'
import re
lines = open('SPEC.md').read().splitlines()
heads = [(i+1, l) for i, l in enumerate(lines) if re.match(r'^#{2,4} \d', l)]
def sec(n):
    p = [h for h in heads if h[0] <= n]
    return p[-1][1].split()[1] if p else '0'
SETS = {
 '14.1': ["Workflow/Config Failures","Repository Provisioning Failures","Workspace Failures",
          "Agent Session Failures","Tracker Failures","Observability Failures",
          "Engine Invocation Failures","Node Provisioning Failures","Executor Bring-up Failures"],
 '7.1':  ["Unclaimed","Claimed","Provisioning","Running","RetryQueued","Released"],
 '7.2':  ["PreparingWorkspace","BuildingPrompt","LaunchingAgentProcess","InitializingSession",
          "StreamingTurn","Finishing","Succeeded","Failed","TimedOut","Stalled",
          "CanceledByReconciliation"],
}
for home, toks in SETS.items():
    hits = {}
    for i, l in enumerate(lines, 1):
        s = sec(i)
        if s.startswith(home): continue
        for t in toks:
            if f'`{t}`' in l: hits.setdefault(s, set()).add(t)
    print(home, len(toks), '->', {k: sorted(v) for k, v in sorted(hits.items())})
PY
```

Section 14.1 reaches four conformance surfaces; Section 7.1 reaches two, descriptively; Section 7.2
reaches none — Section 11.6's four mentions only *define* the run outcomes, so `Succeeded` never
leaves the document. The rest are definitional cross-references no implementation transcribes.

**Under the rule, Section 11.6's triggers and Section 14.1's classes are published, and Sections
7.1, 7.2 and 7.3 are recorded with the reader each lacks.** This decision applies the rule to
Section 11.6; Section 14.1 needs an anchor change and is decision 0104's.

## The strongest set is not among the three reported

Section 11.6 states **one closed vocabulary** of ten tokens with three origins, and a repository
wires its `tracker.transitions` from it. Five of them are the orchestrator-observed run outcomes:
`dispatched`, `pull_request_opened`, `run_succeeded`, `run_failed`, `retries_exhausted`.

These are the only tokens in this decision written by **someone who is not an implementer** — a
repository author, into a policy file that has to work on every implementation Symphony targets.

### Why a misspelling is silent, established rather than assumed

The claim that a misspelled trigger produces no diagnostic was checked against both specifications
and both registries, because a decision resting on a failure mode should not rest on an assumption
about one:

- **The engine cannot catch it.** `VCSX-SPEC.md` Section 5.1 defines three trigger kinds, and a bare
  token is syntactically a **signal**. The engine's `unknown_trigger` configuration reason — "an
  edge's `on` is not a trigger the engine recognizes" — therefore cannot fire on `run_suceeded`: it
  is a well-formed signal the engine does not know it will never receive, because Section 5.1 states
  that "the consumer raises the token the policy binds" and does not close the signal set.
- **Symphony does not catch it either.** Section 6.3's validation checks are enumerated — workflow
  loads, `tracker.kind` supported, `tracker.api_key` present for a `secret`-mode adapter,
  `tracker.project_slug` present, `set_state` capability declared when `tracker.transitions` is
  non-empty, `codex.command` non-empty. None validates an `on` value against the vocabulary.
- **And the runtime treats it as ordinary.** Section 11.6: "A trigger that fires with no matching
  `from`-state transition performs no transition." Correct for a real trigger nobody bound;
  indistinguishable, from outside, from a bound transition whose trigger name is misspelled.

So the policy loads, validates, dispatches, and the transition never fires. No error, no log line.
Nothing else on the list fails that quietly, which is what puts this set first under the rule.

## The ownership question was already answered

`conformance/README.md` defers Sections 7.1, 7.3 and 11.6 together behind one reason: "the trigger
vocabulary is shared with the engine's action-policy machine, so the two registries would have to
agree on which document owns each token."

It is answered, and not by argument. `VCSX-SPEC.md` Section 5.1 assigns the signal vocabulary to the
consumer outright — "the consumer raises the token the policy binds" — and decision 0055 states the
consequence in as many words, while resolving why a signal has no `#class` rung:

> unlike operation reasons, where Section 8.5 lets a `MINOR` add tokens an existing policy must
> absorb, the signal vocabulary is raised by the consumer, so a consumer never surprises its own
> policy — the `#class` fallback exists to absorb *upstream* additions, and **signals have no
> upstream**.

Symphony is the consumer. Its trigger vocabulary is its own. The engine registry's `signals` group
publishes the five tokens `VCSX-SPEC.md` names as examples of consumer-raised signals; that is the
engine documenting its own text, not a claim on the set.

So the bullet defers three unrelated sets behind a question a decision closed before it was written.
Decision 0102 repaired this shape one bullet over and reproduced it; with the ownership finding this
is its **fourth** instance, and the count is the useful part: nothing ever re-derives a reason for
*not* doing something, so a deferral list is exactly where a stale reason survives longest. The
reader test replaces per-bullet reasons with one re-askable question, which is the structural fix.

## Options considered

### What to publish

**Option A — publish by reader.** Chosen; reasoning above.

**Option B — publish all five sets.** The simple rule, with the honest argument that a reader
appearing later cannot be predicted — Section 7.2's phases would be covered before anything reads
them, and the day one does, the spelling is already fixed. It also removes the judgement call that
has now gone stale four times. It loses because publishing a set nothing checks the registry against
converts a derived view into an inventory, one step from 0071's reconsideration trigger, and it
forces Section 7.3's prose-title shape question as well as Section 14.1's for no reader at all.

**Option C — publish identifier-shaped enumerations only.** Mechanical, no judgement, and it dodges
the shape question by declining every set that raises it. It loses because it gets the two important
cases backwards: Section 14.1 is Title Case *with* a reader, Section 7.2 is identifier-shaped with
none. A rule that publishes what is easy rather than what is read is not the rule the registry was
created under.

**Option D — publish nothing further.** The reader analysis is the durable part regardless. It loses
on the run outcomes alone, whose silent failure mode is the worst on the list.

### How much of Section 11.6's vocabulary

**Option E — the whole closed set of ten, accepting that five are also published by the engine
registry.** Chosen.

**Option F — the run outcomes only, with a note pointing at the engine's `signals`.** This was the
draft's proposal and it is the more orthodox one: no token is duplicated, and the split follows the
origin Section 11.6 already states. It loses on the reader the group exists for. A repository author
validating a `tracker.transitions` entry has **one** field to check against **one** vocabulary the
specification calls closed; splitting the answer across two registries by provenance serves the
ownership model rather than the person writing the file, and provenance is a property that consumer
has no use for. The duplication cost is real and is paid in the group note, which names the engine
registry as the authority for the five it also carries.

**Option G — all ten with a per-entry origin field.** Rejected as the machinery for a property no
generator uses. Note that **`core` is carried per entry regardless** and is not the same thing: the
two task-state events are the OPTIONAL task-management extension's, so an implementation shipping no
task model never raises them, and `config_namespaces` already carries exactly this distinction as
`core`. Provenance is where a token came from; `core` is whether it exists at all in a given build.

### The requirement level

**Option H — REQUIRED.** Chosen. It passes 0102's test — whether a spelling can be required turns on
who owns the condition, and these conditions are Symphony's own run mechanics, faced identically by
every implementation. It is also the only level under which the closed-vocabulary sentence can be
read literally: a closed set whose spellings are optional is not closed in any way a repository
author can rely on, and a `repo.policy.toml` would be non-portable by design.

**Option I — RECOMMENDED**, consistent with the two error sets 0102 left advisory. Rejected: those
are adapter mappings onto a foreign transport, where what is distinguishable varies. Nothing varies
here.

## Decision and reasoning

**The reader test is the rule, and it lives in `conformance/README.md`.** It governs what a derived
view contains, not what the specification requires of an implementation — no conformance claim turns
on it — so it does not need to be normative, and keeping it in the README lets it be revised as the
registry learns. This is a deliberate departure from 0071, which put the registry's *precedence*
rule in Section 17's own text; precedence decides which artifact wins a disagreement, which an
implementation does act on, while a publication test decides only what the registry contains.

**Section 11.6's whole vocabulary is published as `transition_triggers`, REQUIRED, closed.** Ten
tokens, `core` marking the two the OPTIONAL task extension owns, and a note naming the three origins
and recording that the engine registry also publishes the five signals and is the authority for
them.

**A consequence not on the sheet, added because the level is otherwise unobservable.** Making the
spellings REQUIRED changes nothing a consumer can check unless something rejects a token outside the
set — and, established above, nothing does today. So Section 6.3 gains a validation check: a
`tracker.transitions` entry whose `on` is not in the vocabulary is a configuration error, caught at
the same preflight that already rejects a duplicate `(from, on)`. **Symphony has to be the one to
catch it**, because the engine cannot: the engine does not close the signal set, by design, and
Section 5.1 gives the consumer the vocabulary precisely so the consumer can fix it. This is the
whole practical content of the REQUIRED level, and stating the level without it would have been the
kind of guarantee that reads well and changes nothing.

**Section 14.1 is decision 0104's**, and is recorded in the deferral list as pending that decision
rather than as lacking a reader — a distinction the list has not previously drawn, and the reason it
accumulated stale entries. The rule says publish it; the anchor change across seven documents is
what wants its own decision to be accepted against.

**Sections 7.1, 7.2 and 7.3 are recorded with the reader each lacks**, so what would change the
answer is named: a snapshot, status surface, or API response exposing an orchestration state as a
value (Section 13.3 exposes none today), or anything outside Section 7.2 asserting a phase by name
(the measurement above is the check, and returns Section 11.6 alone).

**Reconsideration triggers.** Reopen Section 7.2 when the measurement returns a conformance surface.
Reopen Section 7.1 when a monitoring surface exposes a state as a value. Reopen the reader test
itself on 0071's trigger — a published set needing a property `SPEC.md` does not fix. Reopen Option
F if the five duplicated signal tokens ever drift between the two registries, which is the cost this
decision knowingly took on.

Depends on 0071 (whose test this names) and 0102 (whose deferral-list repair this completes).
Relates to 0055 (which settled the ownership), 0051, 0056 and 0002. Successor: 0104, which applies
the same rule to Section 14.1.
