# Background — 0072 Captured subprocess text is redacted where it enters the process

## Context

Resolves issue #16, raised while deciding the observability seam against `06a3bc19` and recorded there
as resolution R20 of that implementation's own decision 0011. It is filed apart from the other Section
13 gaps because those are supporting artifacts being incomplete and this is a substantive conflict
between two sections: both can be followed as written while the implementation publishes a secret.

Section 15.3 is unambiguous in two bullets — "Do not log API tokens or secret values" and "Validate
presence of secrets without printing them". Section 13.8.2 describes a JSON API whose per-issue
response carries `last_message` and `recent_events[].message`. Both are agent-produced free text,
served over HTTP, and neither carries a redaction requirement. Section 13.1's only nearby rule is to
avoid logging large raw payloads, which is a size rule and not a content one.

The defence that would ordinarily close this — make a secret a distinct type that cannot be printed or
serialized — carries none of it. An agent that echoes a credential into its own message produces an
ordinary string: by the time the value reaches the process there is no type to attach a rule to,
because it did not come from the secret provider, it came back out of a subprocess as prose. So
Section 15.3's guarantee stops exactly where Section 13.8.2's surface begins, and the result is an
implementation that ships Section 13.8 faithfully, honours Section 15.3 everywhere the specification
names it, and still serves a token to anyone who can reach the status API over the network.

Two facts about the surrounding document shaped the answer more than the API shape did.

**The API is not the only consumer, and it is OPTIONAL.** The same string is written into `last_message`
(Section 4.1.6) and into the emitted event (Section 10.4); from there it reaches the log sinks (Section
13.2), the runtime snapshot (Section 13.3), any human-readable status surface (Section 13.4), any
humanized summary (Section 13.7), and the agent-session transcript that Section 13.8.2's own response
links by path or URL. A deployment that ships no HTTP server holds the same value in the same places. A
rule written at the serving boundary would fix the surface the reporter could see and leave every other
one, and it would place a security requirement inside an OPTIONAL extension.

**Nothing downstream computes on the text.** Section 13.4 has a status surface draw from orchestrator
state and forbids it being REQUIRED for correctness; Section 13.7 forbids orchestrator logic from
depending on humanized strings; Section 13.8 says the same of the dashboard and API. These fields are
observability data, so rewriting them at ingest cannot change orchestration behavior — which is what
makes the earliest possible point also a safe one.

## Options considered

- **Option A — state the obligation in Section 15.3 as a property of captured subprocess text,
  discharged where the text enters the process, and point at it from Sections 10.4, 13.1 and 13.8.2**
  (chosen). Trade-offs: it edits four sections instead of one, and it widens the case from the API to
  every captured-text producer, which is more than the issue asked for.
- **Option B — one sentence in Section 13.8.2 requiring the free-text fields to be redacted before they
  are served** (the issue's first ask; rejected). It is the smallest possible edit and it closes the
  network-reachable path. It is refused because it fixes one consumer of a value that is already in
  orchestrator state by the time the handler runs: the identical string stays in the log sink, the
  snapshot, the status surface, the humanized summary, and the linked session transcript, so the
  specification would carry a rule that reads as a guarantee and is not one. It also puts the only
  statement of a security requirement inside an OPTIONAL extension, leaving a non-HTTP deployment with
  nothing, and it sets the precedent that each new surface restates the sentence — which is how one
  gets missed.
- **Option C — state that Section 15.3 already governs the fields and the surface inherits it** (the
  issue's second ask; rejected *as written*, adopted as a consequence of Option A). Read literally
  against today's Section 15.3, it is false: those bullets bind values Symphony resolved and printed,
  not a string that arrived from a subprocess, so declaring inheritance would have the document claim a
  guarantee no clause provides. That is worse than silence, because a reader who is told the case is
  covered stops looking. Once Option A puts the rule in Section 15.3, Option C's sentence becomes true
  and is exactly what Section 13.8.2 now says.
- **Option D — require pattern, regex, or entropy matching over agent output** (rejected). It is the
  mechanism that catches a secret Symphony never resolved, which known-value replacement cannot. It is
  refused as the requirement because it has false positives that corrupt legitimate output (a diff, a
  test fixture, an encoded blob) and false negatives without bound, so an implementation cannot state
  what it guarantees; and prescribing a matcher is the kind of implementation detail this document
  keeps out of normative text. It is retained as permitted and forbidden as a substitute for the floor.
- **Option E — leave the mechanism entirely `Implementation-defined` with no floor** (rejected). The
  term means the spec does not pick a policy while the behavior stays part of the contract, so it needs
  a behavior to bind. With no floor, an implementation that logs a warning and serves the token
  conforms, and Section 17 has nothing to test. Exact replacement of the values this run resolved is
  the largest set the implementation provably knows, which makes it the honest floor.
- **Option F — drop `last_message` and `recent_events[].message` from the response shape** (rejected).
  It removes the exposure the issue names without any mechanism at all. It is refused because those
  fields are what makes a per-issue debug endpoint worth having, and the value stays in the log either
  way: it trades an observability capability for no reduction in exposure.
- **Option G — bind the requirement to the orchestrator↔executor seam (Sections 3.1, 9.11) rather than
  to the adapter** (rejected). The seam is a natural chokepoint and every event crosses it. It is
  refused because it is one hop too late where it matters most: with a remote executor the seam is a
  network boundary, so a raw value would already have crossed the network and been written to whatever
  the executor logs on its node. The adapter is where the text is first captured from the subprocess,
  and there is no earlier point at which redaction is possible.

## Decision and reasoning

Section 15.3 gains the rule, stated over *text Symphony captures from a subprocess it runs* — the
agent's messages and notifications (Section 10.4) and a host-side hook's output (Section 15.4). Such
text is untrusted content, not a secret-typed value, and MUST be redacted of the run's resolved secret
values where it enters the process, before it reaches orchestrator state, a log sink, or a durable
transcript. Section 10.4 carries the obligation at the emit boundary, and Sections 13.1 and 13.8.2 state
that their surfaces inherit it. The mechanism above a known-value floor is `Implementation-defined`.

The reasoning worth keeping is the placement rule, not the mechanism. **A redaction obligation belongs
at the boundary where the untrusted text is first captured, not at each boundary where it is published,
because the set of publishers is open and the set of capture points is closed.** Symphony captures agent
text in exactly one place and hook output in one other; it publishes that text through logs, a snapshot,
a status surface, humanized summaries, a transcript, and an OPTIONAL HTTP API, and the next release adds
a seventh. A rule at the capture point is discharged once and inherited by every consumer including ones
not yet written; a rule at a publisher is an enumeration that is wrong as soon as it is finished. That
is the test to apply the next time a value of uncertain provenance enters the system: ask how many
places can produce it, not how many can leak it.

The floor is what makes the requirement a MUST rather than a SHOULD. The obligation is bounded and
mechanical — the values are the ones this run resolved through the secret-provider interface, a finite
set the implementation is holding — the failure mode is publishing a credential to whoever can reach the
port, and the fields are observability-only so nothing can break by complying. None of the usual reasons
to soften a requirement apply. Above the floor the mechanism is `Implementation-defined` with the
attendant MUST-document obligation (Section 19), which is what keeps a language-agnostic document from
prescribing a matcher while still letting an auditor see which one was chosen.

The residual is stated in the specification rather than glossed, because a mitigation that is described
as complete is worse than one described accurately. Known-value replacement does not reach a derived
form — an encoding of a credential, or one the agent paraphrases — and it cannot reach a secret Symphony
never resolved, such as one the agent reads out of repository or tracker content, because there is no
value to match against. Those belong to the trust boundary and harness hardening (Sections 15.1, 15.5),
and their existence is the reason the secret-isolation invariant stays the primary control: the
credential is not in the sandbox to begin with (Sections 9.6, 10.8). Redaction is the backstop for the
paths that invariant does not cover — a credential the agent found rather than was given, a broker
result or hook output that quotes one — and the document says so.

Two boundaries are drawn deliberately. Host-side hook output is inside the rule: it is captured the same
way, a host-side hook MAY hold a repo-internal integrity value in its environment (Section 15.4), and
Section 15.4's existing "hook output SHOULD be truncated in logs" is a size rule with the same gap
Section 13.1 had. Commit messages and pull-request bodies are outside it: they are also agent prose
leaving the sandbox, but they are artifacts the repository publishes deliberately and they are already
gated by the repository's own `before:commit` gate / `scan-content` (Sections 9.8, 9.12, decision 0032),
which refuses rather than rewrites. Silently rewriting a commit message would be a worse failure than
refusing the commit, and the control that exists there has the right shape.

What would make us reconsider: agent free text becoming an orchestration input — a milestone signal
parsed out of prose — which would make redaction order-sensitive and argue for a structured channel for
the signal rather than a looser rule for the text; or a secret provider that rotates a credential
mid-run, which makes "the values this run resolved" time-varying and would need the floor to name the
union of values resolved during the run.

Relates to 0003 (the credential broker and the secret-isolation invariant this backstops), 0004 (the
sandbox that keeps Symphony's own credentials out of the agent's reach in the first place), 0032 (agent
prose crossing into commit and pull-request messages, the surface deliberately left to the repository's
gate), 0035 and 0036 (the executor and the orchestrator↔executor seam Option G would have used), and
0011 (the usage ledger, which carries no free text and needs no rule).
