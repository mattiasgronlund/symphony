# Background — 0103 Which prose enumerations are published, and what their token is

## Context

Issue #54's follow-up comment reports three more prose enumerations a conforming implementation must
spell and the registry does not publish — Section 14.1's nine failure classes, Section 7.1's six
orchestration states, Section 7.2's eleven run-attempt phases — and argues, correctly, that the
general answer is one decision rather than four: whether the registry grows a rule for prose
enumerations is a single question, and one instance does not show the pattern.

Checking the three turned up a fourth set with a stronger case than any of them, and a shape
question the specification already answers two different ways.

### The registry's own test, applied to each set

Decision 0071 created the registry because a spelling transcribed by hand diverges silently: "an
event renamed upstream changes nothing downstream until someone reads a re-pin diff." So the
question for a candidate set is not whether it is an enumeration. It is **what reads the spelling,
and what happens when the reading is wrong.** Ordered by that, the unpublished sets are not peers:

1. **Section 11.6's run outcomes** — `dispatched`, `pull_request_opened`, `run_succeeded`,
   `run_failed`, `retries_exhausted`. Written by a **human into `repo.policy.toml`**, drawn from a
   vocabulary Section 11.6 calls closed, in a repository-owned file that must work on any
   implementation Symphony targets. Section 11.6 makes a misspelling **silent**: "A trigger that
   fires with no matching `from`-state transition performs no transition." A repository author who
   writes `run_suceeded` gets a policy that loads, validates, and never fires — no error, no log
   line, no transition. Nothing else on this list has a failure mode that quiet, and nothing else is
   spelled by someone who is not an implementer.

2. **Section 14.1's nine failure classes** — `Workflow/Config Failures` … `Executor Bring-up
   Failures`. Transcribed into the Conformance Statement, whose template carries two rows *named by
   class* — the park-vs-retry disposition of `Repository Provisioning Failures` and of `Engine
   Invocation Failures` — and named in backticks by Sections 17.2, 17.4, 18.1.4 and 19. Divergence
   shows at audit rather than at build: the Section 17 checks assert **behaviour** — "skip that
   repository's dispatches, retry on a later tick" — and name the class descriptively, so the
   spelling is not measured the way Section 5.5's was by the corpus. A real reader, a slower signal.

3. **Section 7.1's six orchestration states** — `Unclaimed`, `Claimed`, `Provisioning`, `Running`,
   `RetryQueued`, `Released`. `Provisioning` is named in a Section 17.4 check and again in Section
   18.2, descriptively. Section 13.3's runtime snapshot does **not** expose them: it returns
   `running` and `retrying` row lists, not a state name. Internal claim state with no external
   reader.

4. **Section 7.3's seven transition triggers** — `Poll Tick`, `Worker Exit (normal)`, `Worker Exit
   (abnormal)`, `Agent Update Event`, `Retry Timer Fired`, `Reconciliation State Refresh`, `Stall
   Timeout`. Prose-titled internal lifecycle events. Despite the shared word, these are **not**
   Section 11.6's triggers and share no token with them.

5. **Section 7.2's eleven run-attempt phases** — `PreparingWorkspace` … `CanceledByReconciliation`.
   Asserted nowhere in Sections 17, 18 or 19. Section 11.6 names four (`Succeeded`, `Failed`,
   `TimedOut`, `Stalled`) only to *define* the run outcomes — "`run_succeeded` — the run attempt
   finished in `Succeeded`". The trigger a repository writes is `run_succeeded`; `Succeeded` never
   leaves the document. No reader that a divergence would reach.

Measured with the same instrument for each, which a later reader can re-run:

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

→ `14.1` is named outside its own section by Sections 9.7, 17.2, 17.4, 18.1.4 and 19 — the last four
being conformance surfaces. `7.1` by Sections 9.11, 11.6, 16.4, 17.4 and 18.2, of which only 17.4
and 18.2 are conformance surfaces, and none of the five is a wire value. `7.2` by Section 11.6
alone, and there only to define the run outcomes. The rest are definitional cross-references inside
the specification, which no implementation transcribes.

### The engine registry has already claimed half of the strongest set

Section 11.6 states one closed trigger vocabulary and splits it by origin. The agent-emitted half is
**already published** — `signals` in `conformance/vcsx/vocabulary.json` carries `ready-for-review`,
`blocked`, `done`, `tasks:all_closed` and `task:#needs_help`, derived from `VCSX-SPEC.md` Section
5.1. The orchestrator-observed half is published nowhere.

So the ownership question `conformance/README.md` defers the whole bullet behind — "the trigger
vocabulary is shared with the engine's action-policy machine, so the two registries would have to
agree on which document owns each token" — is already answered for the half that is shared, by the
artifacts rather than by argument: the engine owns what the agent emits. The run outcomes are the
orchestrator's, have no counterpart in the engine registry, and carry no ownership question at all.
They are deferred behind a blocker that is not about them.

That bullet also bundles three unrelated sets under one heading — Section 7.1's states, Section
7.3's internal lifecycle events, and Section 11.6's policy triggers — with one reason that fits part
of one of them. Decision 0102 repaired this shape once and then reproduced it; this is its third
recurrence, and the count is the useful part: a deferral list is where stale reasons accumulate
unread, because nothing re-derives a reason for not doing something.

### The shape question, which the document already answers twice

Section 14.1's nine are Title Case titles. Section 8.8 defines `token_budget_exceeded`, which
Section 14.1's own closing note names as a failure category outside the core list, and which a
Section 17.4 check asserts — and it is snake_case. So `SPEC.md` spells failure categories two ways
in one section, and there is no consistent answer to read off it. **A group cannot be derived until
the document has one**, because a registry that picks is a registry deciding what the prose left
open, which 0071 forbade and 0102 restated.

## Options considered

### What to publish

**Option A — publish by reader: the run outcomes and the failure classes; record the rest with the
reader analysis.** Chosen; reasoning below.

**Option B — publish all five sets.** The simple rule, and it has the honest argument that a reader
appearing later is not something the registry can predict — Section 7.2's phases would be published
before anything reads them, and the day one does, the spelling is already fixed. It also removes the
judgement call entirely, which is worth something in a list that has just been shown to accumulate
stale reasoning. It loses because publishing a set with no reader converts the registry from a
derived view into an inventory: 0071's reconsideration trigger is "a registry accumulating
properties the prose does not fix", and an inventory of every enumeration is one step from that,
since each set published without a reader is a set nothing checks the registry against. The cheap
insurance is cheaper than it looks — the Section 7.2 phases are already stable and their divergence
risk is carried by `run_succeeded`/`run_failed`, which this decision does publish.

**Option C — a rule keyed on enumeration shape rather than on reader**: publish every closed
enumeration whose members are identifier-shaped, leave Title Case prose alone. Mechanical, needs no
judgement, and it dodges the shape question entirely by declining every set that raises it. It loses
because it gets the two most important cases backwards: Section 14.1's classes are Title Case and
have the Conformance Statement transcribing them, while Section 7.2's phases are identifier-shaped
and have no reader at all. A rule that publishes what is easy to publish rather than what is read is
not the rule the registry was created under.

**Option D — publish nothing further; record the reader analysis and close the question.** The
minimal answer, and the analysis above is the durable part of this decision whatever is published.
It loses on the run outcomes alone: a human writes them into a policy file, a misspelling is silent
by Section 11.6's own rule, and that is the single worst failure mode in the document that a
published token set would remove.

### What the token is where the prose has none

**Option E — `SPEC.md` gains an identifier-shaped token for each of Section 14.1's nine, and the
registry publishes those.** Chosen.

**Option F — publish the titles verbatim and let each implementation slugify.** Faithful to the
document, invents nothing, and needs no spec change. It loses on the mechanism the registry exists
for: two implementations slugifying `Workflow/Config Failures` independently produce
`workflow_config_failures`, `workflow/config_failures`, or `WorkflowConfigFailures`, and the
divergence the registry was created to remove is reintroduced one layer down, now with the
registry's authority behind the ambiguity.

**Option G — the registry mints the slugs.** Cheapest, and no `SPEC.md` change. It loses on 0071's
ruling, restated by 0102: the ruling belongs in the specification, not in the registry. A derived
view that mints a token is leading its source, and the next reader cannot tell which tokens
`SPEC.md` fixed and which the registry decided.

## Decision and reasoning

**Proposed, not applied.** What follows is the recommendation; `Plan.md` is written against it and
`SPEC.md` is unchanged until this is accepted.

**Publish by reader.** The registry publishes a prose enumeration when something outside the
implementation's own source spells it: a repository author writing configuration, a Conformance
Statement author filling a table, or a conformance check asserting a value. That test is the one
0071 already applied without naming — every set in the first slice has such a reader — and stating
it turns the deferral list from a place reasons go stale into a list with a question against each
entry that a later reader can re-ask. Under it: **Section 11.6's five run outcomes** and **Section
14.1's nine failure classes** are published; Sections 7.1, 7.2 and 7.3 are recorded with the reader
that is missing, so the entry that would change the answer is named rather than left to be
re-derived.

**The run outcomes first, and separately from the signals.** They are the only tokens in this
decision a non-implementer writes, and the only ones whose misspelling produces no diagnostic at
all. The group is `transition_triggers` and carries the run outcomes only, with a note that the
agent-emitted half of Section 11.6's vocabulary is published by the engine registry as `signals` and
is not restated here — the ownership split follows the origin Section 11.6 already states, and
neither registry duplicates the other.

**`SPEC.md` gains the failure-class tokens.** Section 14.1's nine get an identifier-shaped token
each, keeping the Title Case titles as their prose names, which also makes the section consistent
with the `token_budget_exceeded` it already defines. This is the largest cost in the decision and
the reason it is proposed rather than applied: it touches Sections 14.1, 14.2, 17.2, 17.4, 18.1.4
and 19 plus `CONFORMANCE-STATEMENT-TEMPLATE.md`, and it is an anchor change, so it wants a decision
of its own to be accepted against rather than to arrive inside a registry slice.

**`exhaustive: false` on the failure classes**, on the evidence rather than on the reading: Section
8.8's `token_budget_exceeded` is a category outside the nine, so the set is open in fact. This does
not contradict a consumer closing its own enum at nine — 0071 settled that shape for `events`,
openness is a property of the set and not of the names — and issue #54's reporter, who closed
theirs, is right to have done so for a build shipping no such extension.

**Reconsideration triggers.** Reopen Section 7.2 when anything outside Section 7.2 asserts a phase
by name — the measurement above is the check, and it returns `11.6` alone today. Reopen Section 7.1
when a snapshot, status surface or API response exposes an orchestration state as a value, which
Section 13.3 does not today. Reopen the reader test itself if a set with a reader turns out to need
a property `SPEC.md` does not fix, which is 0071's trigger unchanged.

Depends on 0071 (whose test this names) and 0102 (whose deferral-list repair this completes, and
whose recurrence of the bundling defect this records for the third time). Relates to 0051, 0056,
0045 and 0002.
