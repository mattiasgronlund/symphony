# Plan — 0057 Universal operation reasons: `blocked`, `failed`, `unsupported`

## Scope

`VCSX-SPEC.md` Sections 4.3 "Reason-Token Registry", 6.6 "`[hooks]`", 6.10 "Validation", 9.2 "Forge
Backend Plugin", 9.3 "Capability Descriptors", 10.4 "Content Scanning", 12.2 "`ship` Sequence", and 13.1
"Test Matrix". The vocabulary registry and the corpus follow.

No `VCSX-CONTRACT.md` edit: its Section 5.5 fixes the three proto classes and explicitly defers "the
concrete registry of reason tokens" to Section 11, and it names no reason this decision adds or renames
(`push:ok`, `push:non_fast_forward`, `integrate:merge_conflicts` are its examples). No `SPEC.md` edit:
Symphony consumes the engine through the contract surface and enumerates no engine reason token.

## Steps

1. **Section 4.3 defines three reasons for every operation.** Ensure the registry table opens with rows
   for `failed` (`error`), `blocked` (`needs_caller`), and `unsupported` (`error`), whose `Operation`
   cell reads `(any)` for the first and third and `(any gated)` for the second, and that the prose
   before the table says these are defined for every operation and not repeated per operation below.
   Done when a reader can name the reason a gate block on any operation returns without searching for a
   per-operation row.
2. **The per-operation rows carry only operation-specific reasons.** Ensure `commit:blocked` and
   `commit:failed` no longer appear as their own rows, being covered by the universal rows. Done when no
   reason appears both universally and per operation.
3. **`merge:rejected` names the forge refusal.** Ensure `merge` has a `rejected` reason at class `error`
   meaning branch protection or forge policy refused the merge, and that no `merge` row spells the
   forge refusal `blocked`. Done when `blocked` has exactly one meaning and one class across the whole
   registry.
4. **Section 4.3 states the totality property.** Ensure the section records that every operation has at
   least one `done` and at least one `error` reason, that a gated operation additionally has `blocked`,
   and that an engine defining an additional operation and its `before:<op>` position (Section 4.1)
   defines the same reasons for it. Done when the requirement is stated over operations rather than
   implied by the table's rows.
5. **Section 6.6's surfacing rule is total and class-preserving.** Ensure the blocking-hook bullet says
   a `needs_caller` result surfaces as the operation's `blocked` reason and an `error` result as its
   `failed` reason, and that both exist for every gated operation (Section 4.3). Done when the rule can
   be applied at all four required positions and at an engine-defined one.
6. **Section 9.3 names both halves of the undeclared-capability case.** Ensure the section says the
   validation-time case carries `capability_unsupported` (Section 6.10) and the first-use case surfaces
   as the operation's `unsupported` reason (Section 4.3). Done when neither half requires an engine to
   invent a token.
7. **Section 6.10 carries the configuration reason.** Ensure the validation table has a row for a policy
   requiring a capability no configured backend declares, with reason `capability_unsupported`. Done
   when Section 9.3's "surfaced at validation (Section 6.10)" resolves to a token.
8. **Section 9.2 names the forge refusal by its new token.** Ensure `request_merge`'s entry cites
   `merge:rejected` where it speaks of honoring branch protection, as it already cites
   `create_pr:base_mismatch` and `push:pr_closed` for its other two capabilities. Done when the plugin
   entry and the registry agree on the token.
9. **Section 10.4 says where a scan block surfaces.** Ensure the content-scanning section states that a
   block surfaces as the scanned operation's `blocked` or `failed` reason (Section 6.6). Done when a
   reader of Section 10.4 alone can name what `create_pr` returns when `title_scan` blocks.
10. **Section 12.2's push loop is exhaustive over classes.** Ensure the loop returns any non-`done`
    result rather than only the `error` class, so a `needs_caller` reason it does not name — a
    gate-blocked push — is dispositioned by its class default (Section 5.4) instead of falling through
    to `create_pr`. Done when no reason class can reach the `break`.
11. **Section 13.1 covers the new behavior.** Ensure the test matrix asserts that a blocking hook
    surfaces as `<op>:blocked` for a `needs_caller` result and `<op>:failed` for an `error` result, and
    that the plugin bullet names `<op>:unsupported` at first use and `capability_unsupported` at
    validation. Done when both additions appear in the matrix.
12. **The registry agrees.** Ensure `conformance/vcsx/vocabulary.json` expands the universal reasons per
    operation — `failed` and `unsupported` for all eight, `blocked` for the four gated ones — carries
    `merge:rejected` in place of the old `merge:blocked` entry, records `merge:blocked` at
    `needs_caller`, and adds `capability_unsupported` to `config_reasons`. Done when every Section 4.3
    row has its normalized entries and the reasons group's note explains the expansion.
13. **The corpus asserts the new classes.** Ensure `match-edge.json` no longer uses `merge:blocked` as
    an `error`-class trigger, and that vectors assert a gate block routing as `needs_caller`, an
    undeclared capability on a read-only operation routing as `error`, and `merge:blocked` being caught
    by a `merge:#needs_caller` edge. Done when each redefined or added class is exercised through the
    ladder.
14. **The corpus records what it does not exercise.** Ensure `policy-validation.json` notes that
    `capability_unsupported` needs a plugin capability descriptor and is deferred with the rest of
    plugin behavior, and that `conformance/vcsx/README.md`'s vector count and deferral list match. Done
    when no reader mistakes the absence for coverage.

## Cross-cutting sync

`conformance/vcsx/vocabulary.json` (Step 12), `conformance/vcsx/vectors/match-edge.json` and
`policy-validation.json` (Steps 13–14), and `conformance/vcsx/README.md` (Step 14).

`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` needs no change for this decision: its Section 4.1 already
collects operation reasons an engine adds beyond the registry, and its Section 4.2 configuration
reasons, and neither is a per-token list.

## Anchor changes

- `merge:blocked` — **redefined**, not removed. Was "Branch protection or policy blocked the merge" at
  class `error`; is now the `before:merge` gate block at class `needs_caller`. A reference to the old
  meaning must move to `merge:rejected`.
- `merge:rejected` — **new**, carrying the former meaning of `merge:blocked` at class `error`.
- `commit:blocked`, `commit:failed` — unchanged as tokens; their Section 4.3 rows are removed in favor
  of the universal rows that define them for every operation.

## Out of scope

- **Where a blocking hook's own reason is carried.** Section 6.6 requires the hook to return a stable
  reason; the envelope's `reason` field carries the operation's token. Whether the hook's reason is
  exposed as structured output is a question about the envelope (Section 8.2), not the registry, and is
  left open — recorded in `Background.md` so it is not lost.
- **A proto class for `capability_unsupported`.** Decision 0056 settled that configuration reasons carry
  none; this one joins that registry unchanged.
- **Part 1c of issue #2**, the missing `diff` capability, taken up as decision 0058.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.3, 6.6, 6.10, 9.2, 9.3, 10.4, 12.2, 13.1) and
`conformance/vcsx/` (vocabulary, vectors, README).
