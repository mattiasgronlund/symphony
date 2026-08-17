# Plan — 0107 The budget the call already saw

## Scope

`VCSX-SPEC.md`: Section 8.2 "Result Envelope" (the `forge_budget` output), Section 9.2 "Forge
Backend Plugin" (the obligation stated over the capability list, and the snapshot's shape), Section
13.1 "Test Matrix", Section 13.2, Section 13.3.

`VCSX-CONTRACT.md`: no change. The result envelope is deferred to the full engine spec by its
Section 11, and no shared name is added.

`conformance/vcsx/`: no vector data here; the snapshot's presence-on-success is a fault-injection
and live-forge concern, authored against decision 0111's vector shape.

## Steps

1. **Section 9.2 — the obligation over the list.** Ensure a paragraph after the capability list
   states that every capability of the section answers, alongside its own result or value, the
   budget snapshot the forge reported on the call it made, or that the forge reported none — stated
   over the list rather than per capability, in the shape Section 9.1 states its bookkeeping-write
   allowance. Done-condition: no capability entry carries the obligation individually, and adding a
   capability to Section 9.2 inherits it without further text.

2. **Section 9.2 — the snapshot's shape.** Ensure the snapshot is defined as one or more named
   **buckets**, each carrying `limit`, `remaining` and an OPTIONAL `resets_at`, plus the time the
   observation was made. Ensure the text states that bucket identity is opaque — the engine carries
   the name the forge used, normalizes nothing, and compares nothing — and that `limit` and
   `remaining` are counts in the bucket's own unit, which is the forge's, so no unit is named here
   and a consumer compares a bucket only against itself. Done-condition: a reader can tell why a
   single `remaining` field would be wrong, without consulting the decision record.

3. **Section 9.2 — reported whether or not a limit was hit.** Ensure the text states the snapshot
   is answered on a call that succeeded exactly as on one that did not, since a budget visible only
   at exhaustion is visible only after the decision it should have informed. Done-condition: the
   requirement is legible from the success path alone.

4. **Section 8.2 — the `forge_budget` output.** Ensure `outputs` carries `forge_budget`, the most
   recently observed snapshot of the invocation, absent where the invocation reached no forge
   capability **and** where it reached one and the forge reported none. Ensure the text states why
   the two share one spelling — the consumer learned nothing new in either and keeps the figure it
   last held — and states the departure from Section 9's answer discipline explicitly: that
   discipline governs a value the engine composes an operation from, and no operation, reason or
   precondition branches on this one. Done-condition: a reader can tell the departure is reasoned
   rather than overlooked.

5. **Section 8.2 — the engine acts on nothing.** Ensure the text states that the engine reports the
   snapshot and does not pace, defer or refuse on it, consistent with Section 2.2's placement of
   retry, back-off and budget outside the engine. Done-condition: no clause in Section 8.2 or 9.2
   makes an engine behavior conditional on a bucket's value.

6. **Scope — forge only.** Ensure the text states that the version-control network capabilities
   (Section 9.1's four) report no budget and are outside this, a git transport publishing no quota.
   Done-condition: a reader does not expect a `git_budget` counterpart.

7. **Section 13.1 — the test matrix.** Ensure checks exist for: a successful forge-touching
   operation carries `forge_budget`; a forge reporting several buckets yields several, with the
   forge's own names preserved; and the key is absent for an invocation reaching no forge
   capability. Done-condition: each of steps 1–4 has a check that would fail if the step were
   reverted.

8. **Sections 13.2 and 13.3.** Ensure the implementation checklist names the snapshot on every
   forge-touching operation, and the Conformance Statement records which buckets each forge backend
   observes and where it reads them from — `Implementation-defined` per backend, as the
   `forge_parameters` keys already are. Done-condition: a statement author can fill the row without
   reading Section 9.2.

## Cross-cutting sync

No `repo.policy.toml` key changes, so Section 6's schema and the contract surface are untouched. No
reason or `need` token is added, so `conformance/vcsx/vocabulary.json` gains nothing.

## Anchor changes

New anchors: the `forge_budget` output token and its bucket field names (`limit`, `remaining`,
`resets_at`). No anchor is renamed or removed.

## Status

Applied to `VCSX-SPEC.md` (Sections 8.2, 9.2, 13.1, 13.2, 13.3).
