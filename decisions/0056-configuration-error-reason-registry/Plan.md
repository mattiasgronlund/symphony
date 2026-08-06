# Plan — 0056 A configuration-error reason registry and the `usage_or_config` status

## Scope

`VCSX-SPEC.md` Sections 6.10 "Validation", 8.2 "Result Envelope", 8.3 "Exit Codes", 8.5 "Versioning and
the Version Grammar", and 13.3 "Conformance Statement". The vocabulary registry, the corpus, and
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` follow.

No `VCSX-CONTRACT.md` edit: its Section 11 defers "the engine invocation contract (result envelope,
exit codes, escalation payload) and the version grammar" to `VCSX-SPEC.md` Section 8, and Section 6.10
is part of the `repo.policy.toml` schema it also defers. No `SPEC.md` edit: decision 0044 already
classifies an engine result "in which the policy did not run" as an `Engine Invocation Failure`, and
that classification is unchanged by the refusal becoming legible.

## Steps

1. **Section 6.10 carries a reason per condition.** Ensure each configuration error has a stable token
   — `unknown_trigger`, `unknown_action`, `unknown_operation`, `unknown_hook`, `duplicate_edge`,
   `duplicate_transition`, `base_unresolvable`, `set_state_unbound`, `version_floor_unmet` — with the
   condition it names and the section that owns that condition. Done when every condition previously
   listed in prose has a token and none is unnamed.
2. **The `unknown_trigger` / `unknown_operation` boundary is explicit.** Ensure the table distinguishes
   an unrecognized trigger (Section 6.5 recognizes an `op:reason` form only over a known operation)
   from a `run_op` naming an operation the engine does not define. Done when a reader can classify a
   policy with `on = "teleport:ok"` without inference.
3. **Configuration reasons are stated to carry no proto class.** Ensure Section 6.10 records that a
   refused policy has no operation result to classify, that these reasons are reported under the
   `usage_or_config` status rather than through the `#class` fallback, and that an engine MUST document
   any it adds. Done when a consumer knows it never needs a class edge for a configuration reason.
4. **Section 8.2 gains the fourth status and covers the no-operation case.** Ensure `status` is defined
   as the invocation's outcome — the overall proto class for a run that executed the policy,
   `usage_or_config` for one that did not — and that the `op` / `reason` / `class` bullet states that
   under `usage_or_config` the `op` and `class` are null and `reason` carries the configuration reason.
   Done when Sections 8.2 and 8.3 can both be satisfied by one engine.
5. **Section 8.3 mirrors the status, not the proto class.** Ensure the exit-code list is introduced as
   mirroring the invocation status and that `2` names `usage_or_config`. Done when the mapping is total
   over the four status values.
6. **Section 8.5 records the new major-stable surface.** Ensure the invocation status values and the
   configuration reasons are named in the major-stable list, and that the compatible-release bullet
   says a new configuration reason is absorbed by the unchanging `usage_or_config` status rather than
   by a class edge. Done when both additions appear.
7. **Section 13.3 records the new obligations.** Ensure the Conformance Statement's required content
   includes which reason is reported when several configuration conditions hold (the new
   `Implementation-defined` site) and any configuration reason the engine adds. Done when both appear
   in Section 13.3's list.
8. **The registry agrees.** Ensure `conformance/vcsx/vocabulary.json` carries a `config_reasons` group
   and an `invocation_statuses` group with the exit-code mapping. Done when both exist with
   `spec_refs`.
9. **The corpus names the reason.** Ensure every failing `validate_policy` vector expects its specific
   Section 6.10 token rather than a generic class, that a vector distinguishes `unknown_operation` from
   `unknown_trigger`, and that the file notes why the multiple-condition case is not exercised. Done
   when no vector expects a generic configuration error.
10. **The template records the new choices.** Ensure
    `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` has a resolution row for the multiple-condition choice and
    a table for configuration reasons added beyond the registry. Done when both exist.
11. **The README finding is marked resolved.** Ensure `conformance/vcsx/README.md`'s "Surfaced
    findings" records the resolution and names this decision. Done when the entry reads as resolved.

## Out of scope

- **Reporting every condition found.** Option C in `Background.md`; the envelope keeps one error shape,
  and an engine MAY report several under the documented `Implementation-defined` choice.
- **A proto class for configuration reasons.** A refused policy has no operation result; inventing a
  fourth proto class would put a non-result into a taxonomy Section 4.2 defines over results.
- **The other two findings 0053 surfaced**, taken up as decisions 0054 and 0055.

## Cross-cutting sync

`conformance/vcsx/vocabulary.json` (Step 8), `conformance/vcsx/vectors/policy-validation.json` and
`exit-codes.json` (Step 9), `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` (Step 10), and
`conformance/vcsx/README.md` (Step 11).

`SPEC.md` needs no change, but the interaction is worth recording: decision 0044's `Engine Invocation
Failures` class covers "a usage/configuration result in which the policy did not run", and that result
now carries a reason a Symphony deployment can log rather than only an exit code.

## Anchor changes

None. No existing token is renamed or removed. `usage_or_config` is a new value of an existing field,
and the nine configuration reasons are new tokens in a new registry.

## Status

Applied to `VCSX-SPEC.md` (Sections 6.10, 8.2, 8.3, 8.5, 13.3), `conformance/vcsx/` (vocabulary,
vectors, README), and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`.
