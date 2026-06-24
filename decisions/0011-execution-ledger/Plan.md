# Plan — 0011 Per-execution durable ledger

## Scope

Adds a new OPTIONAL extension subsection under Logging, Status, and Observability (Section 13),
referencing the token accounting rules (Section 13.5) and class D from decision 0010. Touches the
config cheat sheet (6.4), test matrix (17), and checklist (18). Depends on 0010 (class D); consumed by
0012 (budget counter re-seed).

## Steps

1. Ensure a per-execution usage ledger is specified as an OPTIONAL extension: append-only, durable,
   keyed by `(issue_identifier, session_id)`. Done when the extension subsection exists under Section
   13 and is marked OPTIONAL.
2. Ensure the ledger entry schema is defined at the Section 13.5 altitude with fields `schema_version`,
   `observed_at`, `final`, `issue_id`, `issue_identifier`, `session_id`, `turn_count`, `input_tokens`,
   `output_tokens`, `total_tokens`, `source_event`; with `issue_identifier` and `session_id` REQUIRED
   for a valid entry and token counts as absolute snapshots (not deltas), consistent with the Section
   13.5 "Token accounting rules". Done when the field list with constraints is present.
3. Ensure the read/summarize rule is specified: take the maximum `total_tokens` per
   `(issue_identifier, session_id)` (high-water mark), then sum across sessions; never sum every
   observed entry. Done when the rule is stated and explicitly identified as what makes appends
   idempotent under retries, reconnects, and the final snapshot.
4. Ensure the ledger is named the RECOMMENDED realization of class-D durability (decision 0010):
   replaying it yields the cumulative total and re-seeds enforcement counters idempotently, while class
   D's abstract contract still admits non-ledger stores. Done when the cross-reference to class D is
   present.
5. Ensure ledger I/O is non-fatal: write failures MUST log and continue (never crash orchestration);
   readers MUST tolerate and skip truncated/garbage/unknown-`schema_version` lines. Done when both
   rules are stated.
6. Ensure the ledger is observability-first: the core schema carries no pricing/cost/`model` field,
   with a note that post-hoc cost attribution would require a `model` field. Done when the boundary and
   the note are present.
7. Ensure the ledger owns its config keys (storage location, retention) under the extension's
   namespace, defaulted and documented. Done when the keys and defaults are specified.

## Cross-cutting sync

- Config cheat sheet (6.4): note that the ledger extension owns its config (no core keys); document
  the keys in the extension subsection per the existing convention.
- Test matrix (17): add `Extension Conformance` rows under 17.6 — append-only + high-water-mark
  summarization is idempotent under retries/reconnects/final snapshot; non-fatal writes; tolerant
  reads skip malformed/unknown-version lines.
- Checklist (18): add the ledger to 18.2 and mark it as realizing the existing TODO "Persist ...
  session metadata across process restarts".

## Anchor changes

- New Section 13.6 "Per-Execution Usage Ledger (OPTIONAL)" inserted after 13.5. The former 13.6
  "Humanized Agent Event Summaries" renumbered to 13.7; the former 13.7 "OPTIONAL HTTP Server
  Extension" to 13.8 (and 13.7.1 / 13.7.2 to 13.8.1 / 13.8.2); the Section 13.7 cross-reference in the
  Section 18.2 HTTP-server item updated to 13.8.
- New anchors: entry fields `schema_version`, `observed_at`, `final`, `source_event` (alongside the
  existing `input_tokens` / `output_tokens` / `total_tokens` / `issue_id` / `issue_identifier` /
  `session_id`).
- Complements the Section 18.2 recovery-class item introduced by decision 0010 (which replaced the old
  "persist session metadata" TODO): the ledger is the extension that realizes the `Durable` class.

## Status

Applied to `SPEC.md` (working tree; not yet committed).
