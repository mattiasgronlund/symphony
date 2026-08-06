# Background — 0053 Engine conformance corpus, first slice

## Context

Decision 0051 published the engine's shared token vocabulary as data and named the corpus as its
natural successor, deliberately not taking it: "This decision publishes the vocabulary; vectors that
exercise the machine *over* that vocabulary are a separate slice with its own derivation work." This is
that slice.

`VCSX-SPEC.md` Section 13.1's test matrix is prose — eight bullets naming behaviors a conforming engine
"SHOULD include tests covering". Prose is not pass/fail, and it does not transfer: two engines can each
believe they satisfy the matching bullet while disagreeing about what an `op:#class` edge catches.
Decision 0046 solved exactly this for `SPEC.md` by publishing data-driven vectors, and the reasoning
carries over unchanged to an engine that decision 0042 made an independent, separately released
deliverable consumed over a version-pinned contract.

Decision 0049 makes it timely rather than merely desirable. A Rust engine is about to be built against
this specification, and the corpus is the thing that lets its correctness be checked against the
*specification* rather than against its own reading of it.

## Options considered

- **Option A — a pure, host-independent first slice authored from the specification (chosen).** Cover
  only behaviors deterministic from their inputs, so the slice runs on day one with a few-line harness
  and no repository, forge, network, subprocess, or filesystem; defer everything else. Trade-offs:
  mirrors 0046's proven shape and sequencing, and is available before the engine exists. It covers
  perhaps half of Section 13.1's bullets, leaving the front-end and plugin behaviors to a later slice.
- **Option B — wait for the engine, then derive vectors from its behavior.** Trade-offs: richer
  coverage sooner, including the integration-shaped behaviors. But it inverts the direction of
  derivation: a corpus read off an implementation encodes that implementation's reading of the
  specification, including its bugs, and then blesses them as the cross-implementation contract. The
  corpus exists precisely to be the independent check.
- **Option C — fold the vectors into `vocabulary.json`.** Trade-offs: one artifact instead of two. But
  a registry and a vector set have different schemas and different jobs — one says what the names are,
  the other says what the engine does — and merging them would make the registry's derivation rule
  ("names and the properties the specification fixes about them, not the prose of the rules those
  properties feed") impossible to state.
- **Option D — no corpus; rely on Section 13.1 plus each implementation's own tests.** Trade-offs: no
  new artifact. But this is the status quo whose weakness prompted the decision, and it leaves the
  major-stable surface — the reason classes, the ladder, the exit codes — checked only by each
  implementation against its own reading.

## Decision and reasoning

Choose **Option A**. Author `conformance/vcsx/vectors/` as a first slice of four pure functions and 49
vectors, derived from `VCSX-SPEC.md` and from nothing else.

Function selection follows where Section 13.1's weight actually sits. Three of its eight bullets —
matching, unmatched policy, determinism — are about the action-policy machine, so `match_edge` (18
vectors) and `validate_policy` (18 vectors) carry most of the slice between them. `resolve_base`
(9 vectors) earns its place because longest-prefix-wins with a required empty-prefix default is a rule
that reads simple and is easy to implement as first-match, and the failure is a silently wrong base
branch. `exit_code_for_status` is four trivial vectors that would not be worth a file in isolation, but
decision 0049 recorded a live hazard for exactly this mapping: the wrapper layer offered as a design
seed uses `0`/`2`/`10`/`64` against Section 8.3's `0`/`10`/`20`/`2`, colliding on `2` and `10` with
different meanings, so a carried-over numbering would satisfy an implementation's own tests while
violating the invocation contract. Four vectors are cheap insurance against a known, specific mistake.

**`proto_class` is deliberately omitted.** It is a lookup over the Section 4.3 registry, and
`vocabulary.json` already *is* that registry, so a vector file would restate it with no assertion
added. `match_edge`'s vectors exercise the lookup in composition instead, by supplying a trigger token
rather than its class — which is also what Section 12.1's algorithm does when it calls
`proto_class(op, reason)`. Recording the omission matters because the obvious move is to author it.

Existing conventions are reused rather than re-invented: 0048's success-or-error union in `expect`,
and the "keys absent from `expect` are unconstrained" rule the Symphony corpus already uses for
`resolve_config_defaults`. The second earns its keep immediately — it lets a vector pin the part of a
behavior the specification fixes without pinning a part it leaves open, which is what makes the first
finding below recordable as a finding rather than a guess. Vector files carry no `profile` field,
because decision 0043 deferred engine conformance rather than defining profiles for it; a file is
scoped by its `spec_refs` alone.

Authoring surfaced three gaps, all recorded rather than guessed at, per the corpus's second job:

1. **Unmatched lifecycle position.** Section 5.4 fixes the default for an unmatched operation outcome
   and for an unmatched signal, but not for a lifecycle position with no edge. The intended reading is
   presumably that nothing runs and the operation proceeds; it is not stated.
2. **Class form of a concrete task-state event.** Section 5.3's signal ladder falls back to "its class
   form" for a `#class`-shaped event token such as `task:#needs_help`, but `needs_help` is not a proto
   class and no mapping from a concrete task event to its class form is defined.
3. **Configuration errors carry no reason token.** Section 6.10 enumerates five refusal conditions and
   Section 8.3 maps them to exit `2`, but none is named, and Section 8.2's `reason` describes a
   decisive *operation* result, of which a refused policy has none. A caller can tell that a policy was
   refused but not why without parsing `message`. For an engine whose contract is otherwise built on
   stable reason tokens, this is the most substantive of the three.

None is resolved here. Each is a spec-clarification candidate in the shape decision 0046 used when it
surfaced the non-ASCII sanitization gap that decision 0047 then resolved.

We would reconsider the pure-only boundary once the engine exists and a fixture harness is cheap, at
which point the deferred behaviors — the `ship` and `land` sequences, plugin and checkout-mode
behavior, message formulation, hook execution — become a second slice. We would reconsider the
derivation direction only if the specification were found to under-determine a behavior so broadly that
no vector could be authored, which is a signal to fix the specification rather than to read vectors off
an implementation.

The decision is **Accepted** and applied: `conformance/vcsx/vectors/` is created with four files and
49 vectors, and `conformance/vcsx/README.md` is extended with the vector schema, the harness contract,
the coverage and deferral tables, and the three findings. Depends on 0051 (the vocabulary the vectors
cross-check against) and 0049 (which made the slice timely); relates to 0046 (the corpus discipline and
shape it reuses), 0048 (the error-vector convention), 0043 (whose deferral is why there is no
`profile` field), and 0052 (whose `notify` disposition one validation vector pins).
