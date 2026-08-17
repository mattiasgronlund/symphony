# Plan — 0109 The other program the engine waits on

## Scope

`VCSX-SPEC.md`: Section 8.1 "Entry Points and Arguments" (the bound as a consumer-supplied
argument), Section 9 preamble or Sections 9.1/9.2 (the bound stated over the network-touching
capabilities and what expiry reports), Sections 13.1, 13.2, 13.3.

`VCSX-CONTRACT.md`: no change; the invocation contract and the consumer configuration's field-level
schema are deferred by its Section 11.

`conformance/vcsx/vocabulary.json`: no new token — `bound_elapsed` already exists as a
`hook_conditions` entry and is reused as a `forge_unavailable_condition` value (decision 0108).

## Steps

1. **Section 8.1 — the argument.** Ensure a consumer-supplied network bound exists, `OPTIONAL`, with
   its value `Implementation-defined` and MUST be documented (Section 13.3), stated as a bound on
   **one network call** rather than on an operation's total. Ensure it is listed among the values
   readable from the consumer configuration. Done-condition: a reader can tell the bound is the
   consumer's and where it is supplied, without consulting Section 9.

2. **Section 8.1 — the floor.** Ensure the text requires an engine to admit a configured value of at
   least 600 seconds, and that an engine letting a deployment configure it holds the configured
   value to the same floor — the shape Section 6.6 uses. Ensure the reason is stated from
   `ensure_store` rather than by reference to Section 6.6: the bound covers a capability that
   fetches an entire repository, so the floor accommodates the slowest network unit, and a capped
   engine would make provisioning unusable at scale while remaining conformant. Done-condition: the
   floor is justified without the word "likewise".

3. **Section 8.1 — why not the policy.** Ensure the text states that `repo.policy.toml` carries no
   key for it, on the ground that the endpoint and the credential are already the consumer's and how
   long to wait for an endpoint is a fact about the consumer's environment — a repository cannot know
   whether its policy runs against a forge on a LAN or across a saturated link. Done-condition: the
   argument stands on Section 8.1's own placement of the access parameters rather than only on
   Section 6.6's sourcing argument.

4. **Section 9 — the bound over the network capabilities.** Ensure the specification states that an
   engine MUST bound the time it waits for each network call, naming the capability set it covers —
   Section 9.1's four network-touching capabilities and every capability of Section 9.2 — and stating
   that a network call is the second place the engine hands control to a program this specification
   does not describe, so the engine's own boundedness (Sections 1, 2.2, 5.6) is otherwise
   conditional on every server answering. Done-condition: the requirement is argued from the
   contract's boundedness rather than from operational hygiene.

5. **Section 9 — what expiry reports.** Ensure the text states that a forge call reaching the bound
   yields `forge_unavailable` with `bound_elapsed` in `outputs.forge_unavailable_condition`
   (Sections 4.3, 8.2), and that a version-control call reaching it reports the operation's existing
   reason — `provision:unreachable`, and the universal `failed` for `integrate`, `pull` and `push` —
   naming this as decision 0108's recorded scope limit rather than a new asymmetry.
   Done-condition: for each of the network capabilities a reader can state what an expiry reports.

6. **Section 9 — the engine does not retry.** Ensure the text states that the bound stops a call and
   reports it, and that whether to call again is the consumer's (Section 2.2); an engine retrying
   inside the bound would silently multiply the wait by an attempt count it chose.
   Done-condition: no clause permits an engine-internal retry within the bound.

7. **Sections 13.1, 13.2, 13.3.** Ensure the test matrix checks that a forge call exceeding the
   bound yields `forge_unavailable` with `bound_elapsed` and not the universal `failed`; that a
   configured value at the floor is accepted; and that the bound applies per call rather than across
   an operation's capabilities. Ensure the checklist names the bound and the Conformance Statement
   records its default and any per-capability values. Done-condition: each of steps 1, 2, 4 and 5
   has a check that would fail if the step were reverted.

## Cross-cutting sync

No `repo.policy.toml` key changes. No new token: `bound_elapsed` is reused from Section 6.6's
condition set, which is the point — one spelling for one event on two kinds of unit.

## Anchor changes

New anchor: the consumer-supplied network-bound argument. No anchor is renamed or removed;
`bound_elapsed` gains a second site rather than a second spelling.

## Status

Applied to `VCSX-SPEC.md` (Sections 8.1, 9, 13.1, 13.2, 13.3).

One application finding: the Section 9 text was first placed between the answer-domain rule and the
paragraph explaining it, which left "The rule is stated over the capability list" reading as if it
described the network bound. Moved after that paragraph. A reference to this decision by number was
also written into the specification and removed — neither `SPEC.md` nor `VCSX-SPEC.md` cites a
decision number anywhere, the decision log pointing at the spec and not the reverse.

A third finding, shared with decision 0107 and corrected by 0112: step 6's text cites Section 2.2
for whether to call again being the consumer's, and **Section 2.2 did not state that** when this
decision was applied. The boundary was real in the design and unstated in the document. 0112 adds
the non-goal, which makes the citation true.
