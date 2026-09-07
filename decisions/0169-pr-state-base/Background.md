# Background — 0169 A clause with nothing to read

## Context

Reported from `symphony-rs` as issue #145, against `5a4fdf7`, found while building that repository's
roadmap D5f.

`SPEC.md` Section 9.10 (Forge Operations, Pull Requests, and Review Writes) states the
pull-request identity re-read as three clauses:

> the pull request still exists, still carries this run's work branch as its head, and still targets
> the resolved base. A mismatch MUST refuse the write.

Two are answerable. The third is not, because no conforming engine answer carries a base.
`VCSX-SPEC.md` Section 9.2 (Forge Backend Plugin):

> `pr_state(work_branch, known_validator)` → the work branch's pull request — its number, its state
> (open/closed/merged), the head it currently carries, and a **validator** …

Number, state, head, validator. No base. So a MUST is stated over a comparison the seam it names
cannot supply either side of.

## The mechanism

**Clause 2 is free and clause 3 is impossible, for the same reason.** The lookup is keyed on the
work branch as head, so "still carries this run's work branch as its head" holds by construction of
the read. Clause 3 asks about the other end of the pull request, and the read answers nothing about
it. The report's seam analysis is right and this half of it is not in question.

**Where the report goes wrong is in reading Section 9.2 as resisting the repair.** It offers adding
base to the output as one option and narrowing Section 9.10's clause as the other, and takes the
second partly because the first looks like it fights the contract. The sentence it is reading:

> The lookup is keyed on the work branch as head **whatever base the pull request targets**, because
> `create_pr:base_mismatch` exists to find one opened against a different base (Section 13.1) and a
> caller's own base therefore MUST NOT be substituted for the key.

That forbids using the caller's base as an **input** — narrowing the search to pull requests already
targeting the expected base, which would hide the retargeted one `create_pr:base_mismatch` exists to
find. It says nothing about **reporting** the base of whatever the head-keyed lookup returned. The
two are opposite directions: keying on base hides a mismatch, returning base makes one visible.
Adding it to the output serves the very purpose the sentence gives for keeping it out of the key.

**The value is already there and is already validated.** `symphony-rs` answered the question this
turned on before it was recorded:

> `crates/vcsx-plugin-forgejo/src/api.rs` parses `base.ref` out of the pull-request payload into its
> internal `ForgePr` … Note `ok_or_else` — base is a **required** field of the response as this
> plugin reads it. A payload without it is a refusal, not a `None`. So it is not merely available,
> it is already validated on every `pr_state` path.
>
> It is then dropped. `vcsx_engine::backend::PullRequest` … is `number`, `state`, `title`, `body`,
> `head`. No `base`. The value survives the HTTP boundary and dies at the contract boundary.

So the field costs no round trip, no rate-limit budget and no new failure mode: it is a member of a
record the backend is already building from a response it is already parsing.

**The precedent is one field over.** `head` is not original to that struct either — decision 0077
added it, and for the same shape of reason: a caller compares what it expected against what the
forge holds now, and acts only if they agree. That is what makes `expected_head` a conditionable
merge, and it is what clause 3 asks for at the other end of the pull request.

**Adding the field to `pr_state` alone would not fix the reported defect.** This is the part neither
the report nor the first reading of it contains, and it decides the scope. `pr_state` is a plugin
capability; a consumer does not call it. The operations that read it either act on the answer —
`push` on the state, `create_pr` on existence, `merge` on the head — or report it, and exactly one
reports it. `VCSX-SPEC.md` Section 4.1, `status`:

> the pull-request state when a forge is configured (number and open/closed/merged)

Number and state. Not head, and — with the field added to `pr_state` and nothing else changed — not
base either. Symphony's re-read would still have nothing to compare, and the repair would consist of
a value that reaches the contract boundary and dies one layer further out than it does today. So
`status`'s pull-request output has to carry the base too, or the fix does not fix.

## Options considered

- **Option A — add the base to `pr_state`'s answer, REQUIRED of every forge backend, and to
  `status`'s pull-request output**, so the value reaches the caller that has to compare it. Section
  9.10's three clauses stand.

  Trade-offs: it obliges every forge backend, including ones not yet written, and it widens an
  operation's output shape rather than only a plugin's.

- **Option B — narrow the clause instead** (the report's second option): Section 9.10 asks for the
  two conditions the seam exposes, and states that base retargeting is caught only where a
  `create_pr` intervenes.

  Trade-offs: no backend obliged, nothing added to any output, and the residue is small and
  documentable — the report is candid that what stays uncaught is "a base retarget ahead of
  `request-merge` alone, with no intervening `pr` call". It loses on two counts. Section 9.10 names
  base retargeting as a condition the rule exists to catch — "a pull request closed by a human
  between two runs, **or retargeted to a different base**, is the same mismatch, and the rule
  refuses that write too" — so Option B deletes that sentence's second clause rather than clarifying
  it. And the residue is worse than it reads: Section 9.10 derives the squash subject from the pull
  request at `before:merge` and `request_merge(pr, strategy, expected_head)` conditions on head
  alone, so a pull request retargeted from the base the run resolved merges the run's work into
  something else with `expected_head` matching throughout, and nothing refuses it.

- **Option C — capability-gate the field**, as the review writes and the conditional merge are
  gated (Section 9.3).

  Trade-offs: it is the conservative shape for anything a code host might lack, and it would let a
  minimal backend ship without it. It loses because the gates in Section 9.3 exist for forge
  *features* — review writes, a conditionable merge — and a pull request without a base is not a
  thing any forge has. Gating manufactures an optional case no backend needs, and every consumer
  then writes the absent branch for a condition that never arises.

- **Option D — also refuse the merge on a base mismatch**, with a `merge:base_mismatch` reason
  paralleling `create_pr:base_mismatch`, so the engine checks what it read at `before:merge` before
  handing the merge to the backend.

  Trade-offs: this is the strongest alternative and it has Section 9.2's own words behind it —
  `expected_head` exists because "a merge that cannot be conditioned merges content no lifecycle
  position inspected", which is as true of the base. It is taken up under the trigger below rather
  than here, for the reason the next section gives.

## Decision and reasoning

**Option A**, and the two things worth recording are what it does *not* do and why the Conformance
Statement obligation this decision was expected to carry turns out not to exist.

**What Option A closes, precisely.** It makes Section 9.10's clause 3 dischargeable at the seam that
clause names: Symphony re-reads, gets a base, and refuses `pr_identity_mismatch` on a mismatch. That
is the long window — from the moment the run establishes the pull request to the moment it writes —
and it is the one the report filed on.

**What it does not close, and a correction to the thread.** `symphony-rs` wrote that Option B "would
have left `request_merge` conditionable on head and not on base, so a retarget between the Section
12.3 read and the merge would still land", offering that as a reason Option B is worse. Option A
does not remove that residue either, and saying so is more useful than letting the agreement stand
on a wrong premise. `request_merge` stays conditioned on head alone. It cannot be conditioned on
base by the mechanism `expected_head` uses, because that mechanism is the forge's — Section 9.2:
"a backend whose forge offers no means of conditioning the merge does not declare the capability" —
and no forge offers a merge conditioned on the base. Any base check is therefore engine-side and
non-atomic, which is Option D.

Option D is deferred rather than rejected, on the ground that it narrows the same window Section
9.10 already declares open and unclosable:

> "immediately before" bounds the pair … and **narrows** the window rather than closing it. Symphony
> cannot make the pair atomic; what the rule converts is a silent overwrite into a detected refusal
> wherever the competing write lands outside the pair.

An engine-side check at `before:merge` is a second narrowing of that same pair, one layer down, and
it costs a reason token in a registry whose additions are version-gated (Section 11). The case it
uniquely covers is a consumer that has no Section 9.10 layer of its own — the `engine-direct` and
`interactive-agent` topologies, where a human runs `land` and nothing re-reads the base. That case
is real and is what the trigger below watches for; it is not what this issue reports, and folding it
in would decide an engine-behaviour question inside a decision about an output shape.

**No engine Conformance Statement template row is owed**, which corrects what was published on the
issue. The call said the template "get[s] the corresponding row, since this adds a backend
obligation". That reasoning is wrong on decision 0128's rule: the templates record the choices the
specification leaves open — `Implementation-defined` values and MUST-document obligations — and a
REQUIRED field is neither. Checked against the template's own structure: Section 2 declares broad
required surfaces and already carries the plugin API as one item; Section 3 is the
`Implementation-defined` table; Section 6.2's forge table records *capabilities declared*, not field
shapes. A row for a field every backend MUST answer would be a row whose only possible value is
"yes", which is what Section 13.2's checklist already asserts. The obligation is a checklist and
test-matrix item, and that is where it goes.

## Reconsideration trigger

Reopen for Option D if a forge offers a merge conditioned on the pull request's base, which would
make the check atomic rather than advisory and put it on exactly the footing `expected_head` stands
on. The evidence is a forge API accepting an expected base on its merge call.

A second trigger, and the likelier one: a consumer with no Section 9.10 layer observed merging into
a retargeted base — a `land` run under the `engine-direct` or `interactive-agent` topology. Option A
gives that consumer the value and nothing that reads it, so the first such report is the occasion to
take Option D rather than to widen this one.

A third: if `status` grows a caller that needs the head as well, the asymmetry this decision leaves
— `status` reporting number, state and base but not head — becomes a gap of its own. It is not one
today, because clause 2 holds by construction of the head-keyed lookup and no operation reports a
head it did not condition on.
