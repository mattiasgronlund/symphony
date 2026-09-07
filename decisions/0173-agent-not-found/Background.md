# Background — 0173 One adapter's name in a normalized vocabulary

## Context

Reported from `symphony-rs` as issue #150, against `5a4fdf7`, found while building the second
adapter (their roadmap D5d).

Section 10.6 (Timeouts and Error Mapping) lists nine RECOMMENDED normalized categories an agent
adapter maps its protocol's failures onto. Eight are adapter-neutral — `invalid_workspace_cwd`,
`response_timeout`, `turn_timeout`, `port_exit`, `response_error`, `turn_failed`, `turn_cancelled`,
`turn_input_required`. The ninth is `codex_not_found`.

## The mechanism

**The condition the odd name covers is every adapter's, and the specification requires a second
adapter.** Section 10.9:

> an implementation MUST NOT require a non-native agent to impersonate another agent's protocol. At
> least two adapters are defined: `codex` … and `claude_code`.

and Section 17.5's first Core Conformance check is "At least the `codex` and `claude_code` adapters
implement the neutral runner contract". So the second adapter is required, and the most basic launch
failure it has — the agent's binary or entry point could not be found or executed — has no
normalized name. The report walks the three things that leaves it, and each is wrong differently:
report `codex_not_found` and a non-native agent wears another agent's name in the one field an
operator reads to find out what broke; report an unknown token and the commonest startup failure of
half the defined adapters sits outside the normalized vocabulary; report a neighbour like
`port_exit` and it is a misclassification.

**The strongest case for leaving it alone is textual and real.** Section 10.9 labels Sections
10.1–10.8 "the worked example", and Section 10.6 is inside that span. So the specification itself
says the section the list lives in is the Codex example, which is a genuine basis for reading the
list as scoped rather than general.

**It loses to Section 10.6's own heading, and then to the list itself.** The heading is "Error
mapping (RECOMMENDED **normalized** categories)". Normalization is not a property one adapter can
have: a list scoped to Codex would not need normalizing, because Codex's own protocol errors would
serve. Normalizing exists so two adapters reporting the same condition report it the same way, which
is what Section 14.1 states for its own tokens — "two implementations reporting the same condition
MUST report the same token, so an operator … can compare them".

The decisive evidence is the list's own composition. Eight of nine names are already neutral. A list
written for one adapter does not come out adapter-neutral in eight places by accident; the single
Codex-shaped name is the residue, not the rule.

**The rename costs almost nothing, and the group was built to absorb exactly this.** The registry's
note says so:

> RECOMMENDED, so the names are a target vocabulary rather than a checked spelling; a generated type
> MUST admit an unknown token.

So no REQUIRED spelling changes under an implementer. That also settles the report's parenthetical
about adding the new name and deprecating the old: a deprecation shim is machinery a RECOMMENDED
group does not need.

**The token has two live sites and no others.** Measured at `750d84d`:

```
$ grep -rn 'codex_not_found' --include='*.md' --include='*.json' . | grep -v '^./.git/'
conformance/vocabulary.json:496:      "codex_not_found",
SPEC.md:3075:- `codex_not_found`
decisions/0102-enumerated-error-tokens/Background.md:107: …
```

The third is a prior decision's recorded measurement, which is history and stays. Section 17.5 and
both Conformance Statement templates name no agent error category at all, which was checked rather
than assumed because the call published on the issue promised to check it.

## Options considered

- **Option A — rename `codex_not_found` to `agent_not_found`** in Section 10.6 and in the registry.

  Trade-offs: it removes a token an implementation may already emit. On a RECOMMENDED group whose
  consumers MUST admit unknown tokens, the cost of that is an implementation reading a name it does
  not recognize, which is the case the group is specified to handle.

- **Option B — confirm the list is scoped to the Codex worked example**, and narrow the registry
  note's general phrasing ("an agent adapter maps its protocol's failures onto") to match.

  Trade-offs: it is coherent, it costs one sentence rather than a token, and Section 10.9's own
  "worked example" label supports it. It loses on the heading and on the list's composition, above;
  and it would make the specification require a second adapter (Section 17.5) while declining to
  name that adapter's commonest failure, which pushes the normalization the section is titled for
  onto every implementation separately.

- **Option C — add `agent_not_found` and keep `codex_not_found`** as a deprecated alias.

  Trade-offs: no implementation reads an unrecognized name, which is the one thing Option A costs.
  It loses because two names for one condition is the opposite of normalizing it: an operator
  comparing two implementations would find the same launch failure under two spellings, which is the
  defect Section 14.1's own token rule exists to prevent — and it would be carried indefinitely,
  since a RECOMMENDED group has no mechanism for retiring an alias.

## Decision and reasoning

**Option A.**

**One half of the call published on the issue is not taken.** That call said the condition would be
"stated neutrally: the agent's binary or entry point could not be found or executed." It is not,
and the reason is a fact about Section 10.6 the registry already publishes:

> Section 10.6 states no condition for any of them.

That sentence is in the `agent_error_categories` note, recorded by decision 0162. Stating a
condition for the renamed token alone would make Section 10.6 inconsistent with itself — one of nine
entries carrying a gloss — and would falsify a sentence the registry publishes about it. Stating
conditions for all nine is a different decision with its own argument. The neutrality this issue is
about is carried entirely by the name, so nothing is lost by leaving the list in the shape decision
0162 measured it in.

## Reconsideration trigger

Reopen if Section 10.6's nine categories are ever given stated conditions. `agent_not_found`'s would
then need one, and the drafted wording — the agent's binary or entry point could not be found or
executed — is recorded here so that decision does not have to re-derive it.

A second trigger, and the one more likely to arrive: an adapter for an agent that is not a local
process — a hosted agent reached over a network, where there is no binary to fail to find. The
launch failure there is a connection or an authorization failure, and `agent_not_found` would be
naming a launch *mode* rather than a launch failure. The evidence is a third adapter whose startup
failure fits none of the nine, and the answer is likely a second neutral category rather than a
rename of this one.
