# Background — 0066 A policy that is not well formed is `malformed_policy`

## Context

Resolves issue #12, raised while building `vcsx-config` and `vcsx-policy` against `06a3bc19`. It
reports three configuration states `VCSX-SPEC.md` Section 6.10's reason table has no row for: an
`[engine] version_floor` that is not a parsable `MAJOR.MINOR`; a required action argument (`run_op`'s
`op`, `run`'s `hook`) that is *absent* rather than wrong; and a `repo.policy.toml` that is not valid
TOML at all.

The issue supplies its own diagnosis and it is the right one: **the table is complete for a policy
that is inconsistent and silent about a policy that is unreadable.** Every one of the nine reasons
decision 0056 registered describes a document the engine read and then found at odds with something —
an edge naming a trigger the engine does not define, two edges on one key, a floor above the running
version, a `set_state` binding no consumer can apply. Each presupposes that a document exists and that
its keys hold values of the shape Section 6 declares. None describes a file that never became a
document, a key whose value the schema does not admit, or an edge that names an action and hands it
nothing to act on.

The silence is wider than the three states reported. `[base] resolve` outside `fixed` / `by_prefix`,
`[hooks] context` naming neither execution context, `[messages.pr] body_source` outside its three
values — none of these has a reason either, and for the same structural cause. The registry was
enumerated over the *checks* Section 6.10 performs rather than over the *states* a policy file can be
in, so everything upstream of those checks fell out.

The third state is the one that changes what an implementation builds, and the document already
settles everything about it except the token. Section 3.1 makes the `Policy Loader` — "reads and
validates `repo.policy.toml`" — a component of the engine, and Section 6.1 gives it an
`Implementation-defined` discovery precedence it MUST document (Section 13.3), so reading the file is
unambiguously the engine's act. Section 8.2 fixes the envelope for a run in which the policy did not
run: `usage_or_config`, `op` and `class` null, `reason` carrying a configuration reason (Section 6.10)
or a precondition reason (Section 8.6). So the engine that cannot read the file has an envelope to
fill, a status to report, an exit code to return — and nothing to put in `reason`. Left unanswered,
every engine invents a token, which is the divergence the registry exists to prevent.

## Options considered

- **Option A — one token, `malformed_policy`, for the whole well-formedness class (chosen).** A
  discovered file that does not parse, a key whose value does not satisfy the constraints its section
  states, and an edge whose action cannot be dispatched from the arguments it carries all report it.
  Trade-offs: one addition to a major-stable vocabulary, and one token where three states are
  distinguishable in principle. It closes the class rather than three points in it, and it is the only
  option under which the conditions the issue did not report — a bogus `resolve`, a bogus `context` —
  are answered too.
- **Option B — the filing implementation's meanwhile answers (rejected).** `version_floor_unmet` for
  an unreadable floor; the reason for the argument's kind (`unknown_operation`, `unknown_hook`) for an
  absent argument; the parse failure left as the loader's own typed fault. Its case is real and is
  taken seriously below: reusing a token costs the public vocabulary nothing, and for the floor there
  is a scenario in which the meanwhile is more truthful than this decision — a future `MAJOR` that
  extends the version grammar would produce floors an older engine cannot parse, whose honest meaning
  is "you need a newer engine". Rejected because each of its three answers fails on its own terms
  (below), and because the parse failure has to be answered somewhere, which pays the vocabulary cost
  the other two were being contorted to avoid.
- **Option C — a token per state: `malformed_version_floor`, `missing_argument`, `malformed_config`
  (rejected).** The most precise option and the one the issue argues against. Rejected on its own
  cost: three tokens on the major-stable surface (Section 8.5), three rows in every engine's
  Conformance Statement, for three states with one owner, one repair, and no caller that branches
  between them.
- **Option D — reading the file is the front-end's problem, out of scope for Section 6.10 (rejected).**
  The issue's own alternative for part 3. Refused on the document's own text: Section 3.1 places the
  `Policy Loader` inside the engine and Section 6.1 makes discovery an engine obligation, so a
  specification that assigns the read and then declines to define its failure is incomplete rather
  than deferring. It would also leave `ship` and `land` — the engine's own front-ends (Section 7) —
  with the problem, and they have no envelope of their own to report it in.
- **Option E — leave it to Section 6.10's existing extension clause (rejected).** An engine MAY add a
  documented configuration reason, so `malformed_config` is already available to anyone who wants it.
  This is the status quo, and its outcome is exactly the divergence the issue predicts: the one state
  every engine reaches becomes the one state no two engines report alike, and a consumer branching on
  `reason` has to learn each engine's spelling — from a Conformance Statement, at which point the
  token is not a contract.
- **Option F — file the three under Section 8.6's precondition registry (rejected).** Natural to ask,
  because decision 0065 created that registry for failures the engine hits before the policy runs, and
  these are earlier still. Rejected by 0065's own dividing line, applied unchanged: a precondition
  failure needs the invocation's arguments and the checkout, and all three of these are properties of
  `repo.policy.toml` alone, judged from the file's text with no argument and no checkout in hand. That
  is the definition of a configuration error, so they belong in Section 6.10.

## Decision and reasoning

Choose **Option A**. Section 6.10's registry gains a tenth reason, `malformed_policy`, and three rows —
a discovered `repo.policy.toml` (or a `vcsx.toml` merged into it) that does not parse; a key whose
value does not satisfy the constraints its section states, of which an unparsable `version_floor` is
the reported instance; and an edge whose action cannot be dispatched from the arguments it carries, of
which `run_op` without `op` and `run` without `hook` are the reported instances.

**The line the registry was missing is well-formedness versus consistency.** A well-formedness failure
is a policy the engine cannot read as the schema describes; a consistency failure is a policy it read
and found at odds with itself, with the engine, or with the consumer. The nine existing reasons are
all of the second kind, and each of them presupposes the first kind has passed — `unknown_hook` can
only be determined against a `[hooks]` table that parsed. Stating that ordering is what makes the new
rows coherent with Section 6.10's opening claim that "a policy is validated before use": validation
takes a document, and a file that does not parse yields none, so its refusal is reported as a
configuration error in its own right rather than as an outcome of the checks below it. That ordering
also means no new `Implementation-defined` site: where the policy does not parse, no other condition is
determinable, so the multiple-condition rule never engages.

**One token rather than three, on decision 0056's own criterion.** 0056 split its first condition into
four `unknown_*` tokens rather than one `unknown_name` "because the four are found at different points
in a policy and repaired differently". Applied here, the criterion argues the other way: all three
states are found by the same pass, are owned by the repository, and are repaired by one act — editing
`repo.policy.toml` until it matches the schema. No caller branches between "the file has a syntax
error" and "a value has the wrong shape"; both surface to a human with `message`, which is what
`message` is for. The distinction that does earn a token is the one against `version_floor_unmet`,
because that reason's repair is a *newer engine*, not a corrected file.

**Why the floor's meanwhile is overturned.** The meanwhile's fail-closed argument is correct and is
kept: an engine that cannot read the floor MUST refuse, because Section 8.5 lets it run only where the
floor is demonstrably satisfied. But fail-closedness decides the *behavior*, and the behavior is
identical under either answer — refuse, `usage_or_config`, exit `2`, policy not run. It does not decide
the *report*, and there the two tokens differ in truth: `version_floor_unmet` is defined as "a
`version_floor` above the running engine version", which asserts a comparison that did not happen, while
`malformed_policy` is true of `"latest"`, `"1"` and `"1.2.3"` alike under this document, whose grammar
is `MAJOR.MINOR`. The strongest counter-argument is the forward one — a future `MAJOR` that extends the
grammar would make an old engine's `malformed_policy` misleading where the truth is "this policy needs a
newer engine" — and it is the recorded reconsideration trigger. It does not win today because the
engine cannot distinguish the two cases anyway, because typos will outnumber cross-major grammar
extensions by a wide margin in a `MAJOR.MINOR` grammar that has never changed, and because the token
that is true under the document in force is the better default when the ambiguity is inherent.

**Why the absent-argument meanwhile is overturned.** `unknown_operation` and `unknown_hook` name an
argument the engine resolved and did not recognize; an absent argument was never resolved, and the
message an engine would have to write ("the operation `` is not defined") is the tell. The decisive
objection is that the meanwhile does not generalize: it works only where the argument's kind happens to
have a token, so `set_state` with no target, `notify` with no channel and `create_task` with no spec
have no answer at all, and `set_state_unbound` — the only `set_state` reason — means something
entirely different. Decision 0057 settled this shape once already, rejecting "add the missing tokens
one at a time" for a rule quantified over the operation set, because "any rule stated over all
operations was going to outrun an enumeration". The same holds over the action set, so the row is
written over the actions and keyed on dispatchability rather than on a table of required arguments —
which also leaves the bare `do = "escalate"` of Section 6.5's own example valid, since Section 5.4
defines what an escalate with no reason of its own escalates.

**The cost argument, settled by sequencing.** The issue's objection to new tokens is sound and is the
reason this decision adds one rather than three: Section 8.5 makes configuration reasons major-stable
and Section 13.3 requires an added reason to be published, so the vocabulary should not grow to
describe a typo. But part 3 cannot be answered by reuse — no existing reason can mean "this is not
TOML" — so the vocabulary grows by one whatever else is decided. Once it has grown, routing parts 1 and
2 through the same token costs nothing further and removes two false statements from the registry. The
cheap answer and the true answer coincide, which is why this is one decision and not three.

**The boundary, stated because it is how this could rot.** `malformed_policy` is the general condition
in a table of specific ones, so it needs a rule against absorbing them: a well-formedness failure that
another row names is reported under that row's reason — a missing or malformed `prefixes` map stays
`base_unresolvable` (Section 6.4) — and `malformed_policy` covers what no other row names. It is also
judged from the policy text alone, which keeps it inside Section 6.10's contract that its conditions
are statically determinable and out of Section 8.6's and Section 4.3's territory. Section 6.1's rule
that an unknown key SHOULD be ignored for forward compatibility is stated not to extend to a declared
key whose value the schema does not admit, since that is the reading under which the new rows would
quietly do nothing.

What is deliberately left unanswered: whether a repository with **no** `repo.policy.toml` at all is a
configuration error, and how an I/O failure reading a discovered file is reported. Both are adjacent
and neither is needed for this decision to be coherent — unlike decision 0065's `branch_pattern`
default, which its own registry entry depended on. Answering the absent-file case means deciding
whether a policy-less repository is a valid input, which touches the defaults of `[base]`, `[engine]`
and `[scope]` together; that is a decision of its own, and guessing at it here would put a rule about
the whole schema inside a rule about a parse failure.

Relates to 0056 (which created this registry and whose splitting criterion decides how many tokens
this adds), 0065 (whose "what is it judged from" line files all three conditions here rather than in
the precondition registry), 0057 (whose rejection of enumerate-the-gaps in favour of a rule over a set
is reused for the action arguments), 0051 (the vocabulary the token joins), and 0044 (Symphony's
`Engine Invocation Failures` class, which already names "an invalid `repo.policy.toml`" and now has a
token for it).
