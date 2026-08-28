# Background — 0164 A preflight refusal that cannot say which check refused

## Context

Not a finding `conformance/README.md` recorded. It surfaced while resolving decision 0162, from a
measurement taken to establish which of Section 11.4's categories the specification actually uses.

Three of them — `unsupported_tracker_kind`, `missing_tracker_api_key`,
`missing_tracker_project_slug` — occur at exactly **one** site each in the whole of `SPEC.md`: the
bullet in Section 11.4 that defines them. Measured at `a4048bc` by `grep -n <token> SPEC.md`.
Nothing raises them, nothing disposes of them, and the conformance registry already records the
symptom without naming the cause: "The first three entries carry no `condition` because Section 11.4
states none."

They carry no condition because their conditions are not in Section 11.4. They are in Section 6.3.

## The mechanism

**Section 6.3 refuses and cannot say why.** Its validation checks are ten bullets, each ending in
"otherwise configuration error", and the section's disposition for one is:

- at startup — "If startup validation fails, fail startup and emit an operator-visible error";
- per tick — "If validation fails, skip dispatch for that tick, keep reconciliation active, and emit
  an operator-visible error."

The per-tick branch is the one that matters. The daemon stays up, keeps reconciling running work,
and dispatches nothing — every tick, indefinitely, until an operator notices. What it emits carries
no stable token, so the only machine-readable fact is that *something* was refused. An operator
watching the monitoring interface (Section 13.3) or the JSON API (Section 13.8.2) sees a daemon that
is healthy and idle, and must read a message string to learn whether the cause is a missing API key
or a routing rule keyed on a field the adapter does not populate. Those have nothing in common as
repairs.

This is exactly the state decision 0056 found in the engine, and its words fit Symphony's Section
6.3 unchanged: a caller "could tell *that* a policy was refused but not *why* without parsing
`message`". `VCSX-SPEC.md` Section 6.11 now carries a condition-to-reason table of twenty-three rows
against nine reason tokens, and states its own ordering rationale. Symphony's equivalent section has
ten checks and no tokens.

**The three orphans are the evidence, not the whole defect.** Someone writing Symphony's error
vocabulary noticed that three of Section 6.3's checks needed names, and put the names in the nearest
registry that had any — the tracker error contract. The result is three tokens filed under an
adapter's transport-failure mapping for conditions no adapter ever raises, and seven checks with no
token at all.

**Measured downstream, and the implementation already disagrees with the registry.** `symphony-rs`
at `ee74fe7`:

- `crates/symphony-orchestrator/src/step.rs` raises them as configuration faults:
  `FaultReport::of::<ConfigInvalid>("missing_tracker_api_key")` and
  `FaultReport::of::<ConfigInvalid>("unsupported_tracker_kind")`, with the fault's reason compared
  as a string.
- `crates/symphony-vocab/src/generated.rs` carries the same three as variants of
  `TrackerErrorCategory`, generated from `conformance/vocabulary.json`.

So the one implementation raises them under a config-fault type while its generated vocabulary files
them under the tracker type, and both are faithful to the specification, because the specification
puts the token in one place and the condition in another. The implementation reached into the
tracker registry for a configuration reason because that is where the only suitable tokens were.

## What a reason token has to be worth

The bar is not "every refusal deserves a name". `VCSX-SPEC.md` Section 6.11 gives the test: a reason
exists where its repair differs. That is why `base_unresolvable` is reported rather than
`malformed_policy` where a `prefixes` map is missing — "Each of those has a repair a reader can act
on where `malformed_policy` would name only that something is wrong: supply the map, or move the key
to the top level".

Applied to Section 6.3's ten checks, the repairs differ at every one, and at two of them they differ
*within* the check:

- "`tracker.kind` is present and supported" is two conditions with two repairs — supply a kind, or
  choose a supported one. One token for both would name neither.
- "At least one `repository` entry is configured, and every entry's key is a valid `Repository Key`"
  is likewise two: add a repository, or rename one. Section 4.2 is explicit that this key "is
  constrained where it is written rather than sanitized where it is used", so a bad key is an
  operator's edit rather than a value to be repaired automatically, which is what makes the distinct
  name useful.

## Options considered

- **Option A — a condition-to-reason table in Section 6.3, one token per condition, absorbing the
  three orphans.** Trade-offs: closes the whole hole, gives every refusal a repair a reader can act
  on, and puts the three tokens where their conditions are. It costs twelve new tokens to maintain,
  a stated evaluation order (below), and a registry group that has to stay in step with the section.

- **Option B — one token per check, ten tokens, no table.** Trade-offs: smaller, and it maps
  one-to-one onto a structure the section already has, so nothing has to be kept in step. Against
  it: `unsupported_tracker_kind` would have to mean "absent or unsupported", which the name denies
  and which a reader would act on wrongly half the time. Collapsing the two repository conditions
  costs the same. The saving is two tokens and the cost is the property the tokens exist for.

- **Option C — leave the three in Section 11.4 and add a note that they are preflight configuration
  errors rather than adapter mappings.** Trade-offs: it is the one-line edit, it makes the registry
  honest, and it touches nothing else. It is a real option because the mis-filing genuinely is
  cosmetic on its own — nothing branches on which registry a token is declared in. It loses because
  the mis-filing is not the defect; it is the visible corner of it. Seven checks would still refuse
  with no token, and the note would document that three of ten refusals can be named.

- **Option D — do nothing.** Trade-offs: no cost today, and no finding was open against it. Against
  it: the condition is reachable in ordinary operation. A `tracker.assignee` set against an adapter
  that does not populate `assignees` (Section 11.7) stops dispatch on every tick while
  reconciliation keeps running, and the specification's own answer to "which check refused" is to
  read prose.

## Decision and reasoning

**Option A.** Section 6.3 gains a condition-to-reason table on `VCSX-SPEC.md` Section 6.11's shape.
Each configuration error carries a stable reason token surfaced with the operator-visible error, so
an operator or a monitoring surface can branch on the cause without parsing a message. The three
tokens move out of Section 11.4 with their conditions.

The token set, one per condition:

| Condition | Reason |
|---|---|
| No `repository` entry is configured | `no_repository_configured` |
| A `repository` entry's key is not a valid `Repository Key` (Section 4.2) | `invalid_repository_key` |
| A `vcs` field Section 9.7 requires is unresolved for an entry after resolution against the orchestrator level (Section 5.3.7) | `missing_vcs_field` |
| `tracker.kind` is absent | `missing_tracker_kind` |
| `tracker.kind` names a kind the implementation does not support | `unsupported_tracker_kind` |
| `tracker.api_key` is absent after `$` resolution for a `secret`-mode adapter (Section 11.7) | `missing_tracker_api_key` |
| `tracker.project_slug` is absent where the selected kind REQUIRES it | `missing_tracker_project_slug` |
| `tracker.transitions` is non-empty and the adapter declares no `set_state` capability (Section 11.7) | `set_state_capability_unmet` |
| `tracker.assignee` is non-null and the adapter declares it populates no `assignees` (Section 11.7) | `assignee_capability_unmet` |
| A `routing` rule keys on a record field the adapter declares it does not populate (Sections 5.3.7, 8.7, 11.7) | `routing_field_unpopulated` |
| A `tracker.transitions` entry's `on` is outside the Section 11.6 trigger vocabulary | `unknown_transition_trigger` |
| The selected agent adapter's launch command is absent or empty (`codex.command`, Section 5.3.6) | `missing_agent_command` |

Two naming judgments are recorded rather than left silent, because both are the kind a later reader
would otherwise reopen:

- **`unknown_transition_trigger`, not `unknown_trigger`.** The engine's `config_reasons` registry
  already publishes `unknown_trigger` for a structurally similar condition — an edge's `on` the
  engine does not recognize (`VCSX-SPEC.md` Section 6.11). The two are checked by different parties
  against different vocabularies, and Section 6.3 says so outright: "The VCS engine cannot make this
  check on Symphony's behalf: a bare token is a well-formed signal to the engine." Their repairs
  differ — one edits `tracker.transitions`, the other a `[policy]` edge — so an operator reading
  `unknown_trigger` in a log and not knowing which validator produced it is back to parsing prose,
  which is the defect this decision exists to close. The distinct spelling is the point.
- **`missing_agent_command`, not `missing_codex_command`.** The check as written names
  `codex.command`, but the condition is a property of the selected agent adapter (Section 10.9), and
  a token that has to be renamed when a second adapter's launch command is validated is a token that
  will not be. The meaning is stated over the selected adapter's launch command with `codex.command`
  named as the instance this specification defines; the check itself is not widened here.

**The evaluation order is stated, because the table makes it observable.** Section 6.3 does not say
which reason is reported where several conditions hold, and a caller branching on the token needs a
determinate answer — as does any vector asserting one. The order follows 6.11's rationale, which is
that a check is ordered after whatever produces the thing it reads: the repository set, then each
entry's resolved `vcs`, then the tracker kind (which fixes whose capability descriptor the later
checks read), then the key and slug that kind requires, then the capability-dependent checks, then
the trigger vocabulary, then the agent command. `VCSX-SPEC.md` states this as "The order is not
incidental"; Symphony's reason is narrower and concrete — three checks read a capability descriptor
that only a resolved `tracker.kind` selects.

**Filed rather than fixed.** Section 6.3 validates an operator configuration that has already been
parsed, and this specification names no class for an operator policy config that does not parse —
Section 5.5's five classes are `WORKFLOW.md`'s. The table added here covers Section 6.3's checks and
not the file's well-formedness, where `VCSX-SPEC.md` Section 6.11's first four rows do cover the
engine's. That is a real gap and a separate one: it belongs to Section 5.3's file contract rather
than to dispatch preflight, and closing it here would mean deciding what an operator config's parse
failure does to a running daemon, which is a recovery question.

**Reconsideration triggers.**

- A deployment reporting that the stated order hides a cause it needed — several conditions holding
  at once with the reported one being the least useful repair. The alternative is reporting all
  holding conditions rather than the first, which is a different envelope shape and would want the
  engine's answer re-examined too.
- A second agent adapter whose launch command is validated at preflight, which is when
  `missing_agent_command`'s generality is tested and the check itself would widen.
- An extension adding a preflight check, which is the first test of whether the table is stated as a
  closed set an extension may extend or a Core set it may not.

## What the plan review changed (2026-08-28)

Running `python3 scripts/check_plan_anchors.py` on the plan before its first edit found one defect,
and it was in the section whose whole purpose is to be read later.

- **The `Anchor changes` entries did not name their document, and the last document named before
  them was the engine's.** The three relocated tokens are recorded as moving "from Section 11.4 to
  Section 6.3", and the preceding `Sites checked` bullet names `VCSX-SPEC.md` Section 6.11 as the
  model. The checker read both sections as `VCSX-SPEC.md`'s and reported that the plan "cites a
  section this document does not have" — which is exactly the failure a later reader chasing a stale
  anchor would hit, since `Anchor changes` is append-only history consulted long after the
  surrounding prose is forgotten. Both entries now name `SPEC.md` explicitly.
- Five `Sites checked` bullets had the same defect for the same reason and were corrected with it.
- The quoted-title convention finding is recorded in decision 0162's `Background.md`; it applied to
  this plan identically.
