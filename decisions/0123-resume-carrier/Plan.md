# Plan — 0123 A termination guarantee that holds in one encoding is not a guarantee

## Scope

`VCSX-SPEC.md`: Section 8.1 "Entry Points and Arguments" (the `resume` argument), Section 8.2 "Result
Envelope" (the `resume_token` output), Section 5.5 "Escalation Binding" (what a resume carries and
what it must not), Section 5.6 "Flow Bound and Termination" (the bound spans a resumed flow),
Section 8.4 "Escalation Payload" (holds carry no token), Section 8.6 "Invocation Preconditions" (a
token the engine cannot establish), Section 8 preamble (encoding neutrality), Sections 13.1, 13.2,
13.3.

`VCSX-CONTRACT.md`: Section 5.6 "Abstract `escalate`", where resume behavior is described at the
surface.

## Steps

1. **`resume_token` in `outputs`.** Ensure Section 8.2 defines an `outputs` key carrying an opaque
   token an invocation that ended at `needs_caller` with a **resolvable** need returns, naming the
   point that raised the need and the flow bound already spent. Ensure the key is absent where the
   need is a hold (`intervention`, `flow_exhausted`, Section 8.4) and where `status` is not
   `needs_caller`. Done-condition: the token's presence and the need's resolvability agree, so a
   front-end can read Section 8.4's prohibition off the envelope.

2. **The `resume` argument.** Ensure Section 8.1 defines an OPTIONAL `resume` argument taking the
   token a previous invocation returned, with `Default: unset — the invocation begins at its entry
   point`. Ensure the round-trip paragraph states it in the terms `pr_state_validator`'s already
   uses: the engine holds nothing between invocations, so the value leaves in the envelope and comes
   back as this argument. Done-condition: the round trip is readable from Sections 8.1 and 8.2 alone.

3. **Opacity, and why it is a choice here.** Ensure Section 8.1 states that the engine holds the token
   opaque as it holds the base ref and the coordinate opaque, and that the reason differs: this value
   is the engine's own, and publishing the executor's traversal position would owe a stable spelling
   for every graph shape a policy can express. Done-condition: the opacity is argued rather than
   asserted by analogy.

4. **What the token carries, and what it MUST NOT.** Ensure Section 5.5's "Nothing a position
   established carries across a resume" is stated over the token explicitly: it carries the point and
   the count, and MUST NOT carry `expected_worktree`, `expected_head`, or any other state a position
   established, which are read again at the re-entered position. Done-condition: the existing
   guarantee is restated where the new value could break it.

5. **The bound spans a resumed flow.** Ensure Section 5.6's bound is stated over the flow rather than
   over one invocation, with a resumed invocation continuing from the count its token carries, and
   ensure the paragraph arguing that "a resolver that always resolves would otherwise loop there"
   holds for both front-ends. Done-condition: `flow_exhausted` is reachable through a chain of
   resumed invocations, not only within one.

6. **A token the engine cannot establish.** Ensure Section 8.6 gains a precondition row for a
   `resume` the engine cannot establish as its own and current — issued under a different policy,
   against a different repository, or by a different major version — reported with a reason of its
   own under `usage_or_config`, the policy not run. State the direction: a refused resume costs a
   re-invocation from the entry point, where an accepted stale one runs an operation the policy no
   longer routes. Done-condition: the row exists and names what it is judged from.

7. **Encoding neutrality.** Ensure Section 8's opening claim that "the contract is the same either
   way; only the encoding differs" is true of a resume, and ensure Section 5.5's closing sentence
   still names `escalate` as the single point of front-end divergence — which it now is, the bound
   having stopped being the second. Done-condition: neither sentence requires a qualification.

8. **`VCSX-CONTRACT.md` Section 5.6.** Ensure the surface names that a resume round-trips through the
   consumer, at the surface's altitude and without the field-level schema Section 11 defers.
   Done-condition: the surface does not imply engine-held state between invocations.

9. **Sections 13.1, 13.2, 13.3.** Ensure the test matrix checks that a resolvable `needs_caller`
   carries a `resume_token` and a hold carries none; that supplying it re-enters the point that raised
   the need rather than the entry point, re-running a gate rather than committing past it; that the
   re-entered position reads the working tree and the pull-request head again rather than reusing what
   the token was issued beside; that a resolver resolving every time reaches `flow_exhausted` **across
   invocations** and not only in-process; and that a token from a different policy is refused. Ensure
   the checklist's machine bullet names a flow bounded across resumed invocations, and Section 13.3
   records the token's form as `Implementation-defined`. Done-condition: steps 1, 4, 5 and 6 each have
   a check.

## Cross-cutting sync

Section 8.5: the `resume` argument and the `resume_token` key are additive, so a `MINOR` introduces
them; the precondition reason joins the registry Section 8.5 already permits a `MINOR` to extend.

`SPEC.md`: Symphony's daemon binds `escalate` to an agent-assigned task (Section 8.10) and parks
between invocations, so it is the consumer this argument exists for. No normative change is required —
the token is carried like any other engine result — but Section 14.3's recovery classification is
where a stored token would belong if a later decision has Symphony persist one, and that is not this
decision's to make.

## Anchor changes

New anchors: the `resume` argument, the `resume_token` output key, and one precondition reason. No
anchor is renamed or removed.

## Status

Applied to `VCSX-SPEC.md` (Sections 5.5, 5.6, 8.1, 8.2, 8.4, 8.6, 13.1, 13.2, 13.3),
`VCSX-CONTRACT.md` (Section 5.6) and `conformance/vcsx/vocabulary.json`.
