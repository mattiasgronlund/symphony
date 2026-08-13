# Background — 0084 Every condition gets a home, and one exit code names "no result"

## Context

Resolves issue #38. Section 8.2 opens "Every invocation returns one structured result", and
Section 8.3 fixes four exit codes that mirror the four invocation statuses, adding that "the JSON
result is emitted regardless of exit code so a caller MAY always read structured detail". All four
statuses describe a run: three that executed the policy, and `usage_or_config` where the policy did
not run but the engine still composed an envelope carrying a Section 6.10 or Section 8.6 reason.
"Regardless of exit code" presumes a result. The paths that reach no envelope are not covered, and
each is a state a repository or an operator reaches:

- a repository unit that will not run, or that does not answer in the shape the engine fixed —
  Section 6.6 makes the form of a hook's `run` unit `Implementation-defined`, so a violation of it
  is outside every registry upstream owns by construction;
- `body_source = "template"` with no template unit bound — Section 10.2 makes the body "a repository
  template over the durable inputs", the engine ships no template engine, and Section 4.3's
  `unsupported` does not cover it, because Section 9.3 defines that for a plugin capability a
  backend does not declare and a template is neither a plugin nor a capability;
- a command line the front-end cannot read — Section 6.10 names conditions of the policy file and
  Section 8.6 names conditions of the arguments-and-checkout, and neither names a condition of the
  argument *encoding*, which Section 8.1 makes the engine's own;
- a hook that exceeded a bound, which exists as a condition at all only because Section 6.6 was
  silent about bounds (issue #35, decision 0081).

Section 8.3's stated purpose is a caller branching **without parsing**, and that purpose fails for
exactly these cases, differently on each engine. There is precedent for upstream caring which code
leaves the process: issue 9's fourth question offered "confirm that these belong to the invocation
contract rather than the Section 4.3 registry" as a sufficient answer, and decision 0065 declined it
and built Section 8.6 instead, reasoning about the code itself — `error`/`20` "invites a retry
against a state that no retry changes", while `2` says the policy did not run, fix the invocation.
That argument applies unchanged to a condition where nothing ran at all, and it currently has
nowhere to land.

## Why absorbing the conditions is a correctness change, not registry hygiene

The report presents absorption as the most work and the most likely to be right where it applies. It
is stronger than that for at least one member of the set, and the strength is where the refusal
happens rather than which registry names it.

Section 12.2's `ship` sequence runs `commit`, then `push`, then `create_pr`. A `body_source =
"template"` with no unit bound is not discovered until `create_pr` composes a body — so today that
misconfiguration **publishes a work branch and then dies with empty stdout**. Section 6.10 refuses
`set_state_unbound` before anything runs, and this is the same shape one seam over: a policy naming
a seam no consumer can effect. Moving the refusal to validation removes a side effect an operator
then has to reason about, and neither of the cheaper options does that.

## One token across two issues, and where the boundary falls

The report's own disposition for a hook that will not run — and this decision's first draft — was to
read it as a hook that blocked with an `error` result, so Section 6.6's existing rule surfaces
`<op>:failed`. That is refused, because it reintroduces the conflation decision 0081 exists to undo:
**a block is something the hook did**, and a hook that never started, or whose answer the engine
could not read, decided nothing — the engine did. A repository routing `commit:failed → park` would
then be unable to tell a gate that ran and refused from a gate that is broken.

So this decision mints no hook reason. Decision 0081's `hook_unanswered` is defined over all three
conditions — the bound elapsed, the unit could not be started, the answer could not be read — and
this report's hook case is served by it. One addition to the registry across both issues rather than
one each, and the two answers stay coherent.

One case splits off and is a configuration error rather than a runtime reason: a hook declared in
`[hooks]` with no `run` unit at all is judgeable from the document. That is recorded in decision
0081, which owns Section 6.6.

## What `template_unbound` needs that `set_state_unbound` did not

`set_state_unbound` is judged from the consumer-supplied Section 5.2 actions: the engine knows
whether a consumer can apply a state transition because the consumer told it. A template unit is a
Section 10.2 **repository unit**, not an action — so the input Section 6.10 judges from has to carry
bound repository units too, or the condition is not judgeable at validation at all.

That has to be **stated**, not left implicit. If it is not, implementations will diverge on whether
the condition is determinable before the policy runs, which is precisely the ambiguity issue #36
exists to close one section over (decision 0082). It is cheap to say and expensive to leave to
inference.

## Options considered

- **A — give the conditions homes, then reserve one code for the residue (chosen).**
- **B — the channel rule alone.** One paragraph in Section 8.3: a code outside the four means the
  engine produced no Section 8.2 result, stdout is empty, the diagnostic is on stderr. Genuinely
  elegant, and total for a consumer; if the question were only about the channel it would win. It is
  rejected on its own stated cost — each engine still decides which conditions are faults, which
  leaves a Conformance Statement unable to say anything useful here — and because it keeps the
  published-then-abandoned branch above.
- **C — reserve a code and stop there.** B plus a number. Rejected on the same ground, plus an exit
  code spent to distinguish a deliberate fault report from a crash, a distinction whose repair is
  identical either way: read stderr.

## Decision and reasoning

**A**, in four parts.

1. **`template_unbound` joins Section 6.10**, with Section 6.10's judgement input stated to carry
   the repository units a consumer bound as well as the actions it can effect.
2. **The hook conditions take decision 0081's `hook_unanswered`.** This decision adds no reason for
   them.
3. **A command line the front-end cannot read produces a real envelope** — `usage_or_config`, exit
   `2`, `op` and `class` null, `reason` carrying `arguments_unreadable`. It is a Section 8.6
   precondition reason under that section's repaired boundary (decision 0082): it is judged from the
   invocation's arguments and nothing else. It is the one precondition established **before**
   validation rather than after it, because an engine that cannot decode its arguments cannot locate
   the policy it would validate, and Section 8.6 states that carve-out rather than leaving the
   ordering rule to be contradicted silently. This also removes the reporting engine's own
   invention, where exit `2` carried two cases separated only by whether stdout held JSON — an
   invention that was itself evidence of the hole.
4. **Section 8.3 reserves exit `1`** for an invocation that produced no Section 8.2 result: stdout
   carries nothing, the diagnostic goes to stderr, and **any other code means the same thing**. The
   "any other code" clause is the load-bearing half: it covers a panic, a signal and an
   out-of-memory kill without the specification predicting every way a process can die, so a
   consumer's mapping is total. Section 8.3 additionally states the property that makes the rest
   safe — on every path that produces a result, stdout carries exactly one JSON object and nothing
   else — which is what lets a caller separate "no result" from "result" without parsing, and what
   keeps a shell pipeline from breaking on a fault. That property was the reporting engine's own
   rule 7 and nothing in Sections 8.2 or 8.3 required it.

**Cost, priced.** One configuration reason, one precondition reason and one exit code, all permanent
within a `MAJOR`. Section 8.5 admits a new configuration reason and a new precondition reason in a
`MINOR`, and Section 6.10 states that such a reason is absorbed by the `usage_or_config` status
without needing an existing class edge, so no consumer changes to receive either. The exit code is
the only genuinely new surface, and it is spent on making the mapping total rather than on a
distinction.

**What is deliberately not enumerated.** The membership of the set of ways a repository unit can
violate the engine's own contract stays the engine's, because Section 6.6 makes that contract
`Implementation-defined`. Only the disposition is fixed. The ask was about the channel, and the
answer does not take a surface upstream should not own.

## Review findings applied (PR #40)

Four findings against the follow-through. The chosen option is unchanged in all four.

**The judgement input was stated as a closed list that excluded one of its own table's rows.** "Four
inputs and no others" named the policy document, what the engine holds independently of the
invocation, the actions a consumer can effect and the units it bound — and `version_floor_unmet` is
judged against the **running engine version**, which none of them named. That is precisely the shape
decision 0082 diagnoses in the sentence it repairs: Section 8.6's "a property of `repo.policy.toml`
alone" defined `capability_unsupported` out of existence, and a closed enumeration omitting
`version_floor_unmet`'s input reproduced the failure one section over. The engine's own version now
sits in the second bullet beside the descriptors and the defaults. Widening the input list was this
decision's contribution; closing it too tightly was this decision's error.

**Two artifacts carried two incompatible closed lists.** `policy-validation.json`'s `given` named the
running engine version and not the descriptors, while Section 6.10 named the descriptors and not the
version — both authoritative, both introduced here. The vector file now states the same four and says
which of them it models, leaving the descriptor input to the coverage note already there.

**Section 8.5 did not say the reserved exit code was permitted.** It makes "the exit-code mapping"
major-stable and enumerates what a `MINOR` may introduce without naming exit codes, so a reader
checking whether exit `1` was allowed found nothing that said so, and this decision priced it only as
"permanent within a `MAJOR`". Section 8.5 now states that reserving a code for a condition that is
not an invocation status is a `MINOR` addition and is not a change to the mapping: the four
status-bearing codes and the statuses they map from are untouched, and Section 8.3's
any-other-code rule already made a consumer's mapping total.

**Section 8.6's opening sentence was false for one row of its own table.** It claims the engine
establishes preconditions between validating the policy and running it, which `arguments_unreadable`
is not. The carve-out was stated three paragraphs down; the exception is now named where the claim is
made. Leaving it was the same defect 0082 reports against Section 8.6 — one section saying the thing
twice and differently — and inviting that report back.

**Second round: the Section 8.5 sentence was circular for its own first application.** As written it
argued that a consumer written against an earlier `MINOR` absorbs a reservation without changing,
which leans on Section 8.3's any-other-code rule — introduced in the same revision. For every future
reservation the argument is exact; for exit `1` there is no earlier `MINOR` in which a consumer was
total. Nothing breaks, since such a consumer had to treat an unrecognized code as unknown anyway, but
the sentence claimed more than it could. It now reads "any `MINOR` from the one that states that rule
onward", which is true as written.

**Downstream cost recorded rather than absorbed.** The `no_result_is_one` vector supplies
`{"status": null}`, which a signature of the shape `exit_code_for_status(status) -> code` cannot
express without an optional or a separate path, and a help table built by mapping over the statuses
cannot list `1` at all. That is the correct friction rather than a modelling error: exit `1` is not a
status, this specification says so, and a total mapping from what an invocation produced to what
leaves the process is what the reservation buys. The vector's `given` already states the domain as
the status or none.

## Reconsideration trigger

Reconsider if an engine is found for which exit `1` collides with a runtime it cannot control — a
host that reserves `1` for its own aborts in a way that makes the reserved meaning unreadable — in
which case the "any other code" clause still holds and only the reservation is at issue. Reconsider
separately if `template_unbound` proves to need a checkout to judge after all, which would mean the
Section 6.10 judgement input was widened in the wrong direction and the condition belongs in Section
8.6.

Relates to 0081 (whose `hook_unanswered` serves this report's hook conditions), 0082 (whose repair
of Section 8.6's boundary is what lets `arguments_unreadable` sit in that registry), 0065 (which
built Section 8.6 rather than concede the exit-code question), 0056 (the configuration-reason
registry) and 0075/0076 (the absorptions this one follows in shape).
