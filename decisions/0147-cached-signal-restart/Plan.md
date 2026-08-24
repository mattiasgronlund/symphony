# Plan — 0147 What a restart restores, and which class the Core field is

## Scope

- `SPEC.md` — Section 4.1.8 (Orchestrator Runtime State), Section 14.3 (State Recovery Classes),
  Section 14.4 (Partial State Recovery), Section 8.9 (Provider Quota Backpressure), Section 17.4
  (test matrix), Section 19 (Conformance Statement).
- `CONFORMANCE-STATEMENT-TEMPLATE.md` — Section 4.1 (one row), Section 5 (one row changes shape, one
  column header gains a clause).
- `conformance/vocabulary.json` — the `runtime_state_fields` entry for `provider_rate_limits`.
- `conformance/vectors/` — no new file. The properties are over a restart and over a configured
  policy, not over a pure function of one input; Section 17.4 is where they are checkable.

## Steps

1. **`SPEC.md` Section 4.1.8 — `provider_rate_limits` is dual-class.** Ensure the field is
   `Ephemeral` for observability (Section 13.5) with its reset consequence stated — the status
   surface reports no rate-limit reading until the next agent update refreshes it — and becomes
   `Cached external signal` when the provider-quota extension (Section 8.9) enforces on it, which is
   where its staleness bound (`stale_after_ms`) and its `UNKNOWN` policy come from. Ensure the
   existing sentence that an absent value denotes `UNKNOWN`, distinct from any reading and in
   particular not `0`, is kept. Ensure the shape matches `agent_totals`'s two-valued entry rather
   than inventing a third form. *Done when:* no Core field carries the `Cached external signal`
   class, Section 14.3's closing paragraph is true as written, and a Core-only build has no value it
   is told to age against a bound no Core section defines.
2. **`SPEC.md` Section 14.3 — the `C` bullet's restart half is scoped to a store.** Ensure the
   bullet quoted as "The most recent successfully fetched value (the last-known-good) MUST be
   carried across both a failed refresh and a process restart" is split: carrying across a failed
   refresh stays unconditional; carrying across a process restart requires a store, and where one
   backs the field it MUST be restored before any decision that enforces on it, while where none is
   configured the field starts `UNKNOWN` and the implementation MUST document the degradation.
   Ensure the clause mirrors the `Durable` bullet's existing degradation clause in shape and
   wording. *Done when:* a store-free implementation can satisfy the `C` bullet, and Section 16.1's
   `restore_cached_and_durable_state` paragraph is a description of the rule rather than an
   exception to it.
3. **`SPEC.md` Section 14.3 — the fail-open rule for an `UNKNOWN` that cannot be replaced.** Ensure
   the section states, beside the existing permanently-versus-transiently `UNKNOWN` allowance, that
   where no out-of-band refresh path is configured an `UNKNOWN` MUST fail open, with the reason
   given: the only source of readings is then an agent update, which a paused dispatch prevents, so
   a fail-closed policy would never release. Ensure the rule is stated over whether a reading can
   arrive rather than over whether one has been held — a rule worded over the latter does not reach
   a restored value that is already older than its bound, nor an idle deployment whose snapshot aged
   out with nothing running. *Done when:* no configuration of Section 8.9 admits a deployment that
   pauses dispatch and thereby prevents the only reading that would release it.
4. **`SPEC.md` Section 14.3 — a restored value is a reading; a restore that produced none is not.**
   Ensure that sentence is stated beside the permanently-versus-transiently `UNKNOWN` distinction
   rather than beside the escape in step 3, since its job is to decide which arm a startup `UNKNOWN`
   falls in. *Done when:* the existing SHOULD/MAY pair has an input, and the two conditions — never
   held a reading in this process, versus a reading aged past its bound — are distinguishable.
5. **`SPEC.md` Section 14.4 — both restorable classes.** Ensure the first paragraph states that
   state whose class provides for restoration is restored across a restart — `Durable` state, and
   `Cached external signal` state where a store backs it, both introduced by OPTIONAL extensions —
   rather than "Only `Durable` state". Ensure the After-restart list gains a `Cached external
   signal` bullet beside the `Durable` one, with the same second clause: with no store the field
   starts `UNKNOWN` and the consuming extension applies its documented `UNKNOWN` policy. *Done
   when:* Section 14.4 is true for a quota extension with a store configured, which Section 16.1
   already reaches.
6. **`SPEC.md` Section 8.9 — the extension's own bullet is scoped the same way.** Ensure the
   Recovery-semantics bullet quoted as "the last-known-good value is carried across a failed refresh
   and a process restart" carries the store condition and the store-free default, so the extension's
   section does not promise what the class no longer does. Ensure the never-read/aged-out
   distinction from step 4 is stated here in the extension's own terms, since `stale_after_ms` is
   what makes the second condition possible and the extension owns it. *Done when:* Sections 8.9,
   14.3 and 14.4 state one contract, and Section 8.9's SHOULD/MAY pair is evaluable.
7. **`SPEC.md` Section 17.4 — the conditioned rows still hold, plus one.** Ensure the two existing
   rows naming `Durable` / `Cached external signal` extensions read correctly against the scoped
   class. Ensure a row covers the store-free case: with no store, a `Cached external signal` field
   starts `UNKNOWN` after a restart, `UNKNOWN` is never represented as `0`, and with no out-of-band
   refresh path configured the gate fails open rather than pausing a deployment that has no way to
   obtain a reading. *Done when:* the new row fails an implementation that pauses dispatch on a
   startup `UNKNOWN` with only the in-band path configured.
8. **`SPEC.md` Section 19 and `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1 — the new obligation
   gets its row.** Ensure the MUST-document degradation added in step 2 has a row beside the
   existing `Durable-store degradation when no store is configured | 14.3` — either as a second row
   or by that row being restated over both restorable classes, whichever leaves the obligation
   sentence and the row in one-to-one correspondence. *Done when:* `python3
   scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings, and no obligation sentence
   this decision adds lacks a row (`CLAUDE.md`, decision 0128).
9. **`CONFORMANCE-STATEMENT-TEMPLATE.md` Section 5 — the row and the column header.** Ensure
   `provider_rate_limits`'s "Spec default" cell carries both classes in the shape `agent_totals`'s
   already uses, and that its "Reset consequence" cell is no longer `n/a`. Ensure the column header
   or the paragraph above the table states that a dual-valued "Spec default" cell is answered with
   **which of the two the implementation ships**, not "both" — one rule for the column, covering
   `agent_totals` as well. *Done when:* two implementations cannot publish the same string for
   different behaviour, and a generator reading the table has a stated rule for the dual cells.

10. **`conformance/vocabulary.json` — the registry carries the class per field.** Ensure the
    `runtime_state_fields` entry for `provider_rate_limits` takes the dual-class shape
    `agent_totals` already uses — `"recovery_class": "Ephemeral"` with a note naming the class it
    becomes under the provider-quota extension — rather than continuing to state `Cached external
    signal`. Ensure the existing note about an absent value denoting `UNKNOWN` survives. Ensure the
    `recovery_classes` group needs no change: its entries carry a token and a short code only, and
    its group note is about assignment rather than about what any one class promises, so nothing
    there restates the `C` bullet this decision edits — checked rather than assumed, because a
    registry note asserting what the specification no longer says is decision 0132's drift class.
    *Done when:* the registry's per-field class agrees with Section 4.1.8, and `python3
    scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings.

## Cross-cutting sync

- `conformance/vocabulary.json`: step 10. **This is the derived artifact most easily missed**: it
  states the class per field in its own structure rather than by citation, so the reclass in step 1
  is invisible to it. It was found by `python3 scripts/check_plan_anchors.py` against an earlier
  draft of this plan, which did not name the file.
- `SPEC.md` Sections 17.4 and 19: steps 7 and 8. Unaffected, because the reclass changes which class
  a field carries and not whether one is stated: `SPEC.md` Section 18.1.3's checklist line, quoted
  as "Every Orchestrator Runtime State field is assigned and documented as a recovery class";
  `SPEC.md` Section 18.1.1's summary of the same obligation; and `SPEC.md` Section 17.4's row quoted
  as "Every Orchestrator Runtime State field has a documented recovery class".
- `SPEC.md` Section 6.4 (config cheat sheet): no change. `quota.*` keys are unchanged and remain
  extension-owned.
- `CONFORMANCE-STATEMENT-TEMPLATE.md` Sections 4.1 and 5: steps 8 and 9. **A row is owed** for step
  2's degradation obligation — this is decision 0128's case.

## Ordering

- Independent of every other decision in this batch. It touches Sections 14.3, 14.4, 8.9 and 4.1.8,
  which decisions 0144–0146 do not.
- Step 1 must land with steps 2 and 5, not before them: reclassing the field while `SPEC.md` Section
  14.4 still restricts restoration to `Durable` state leaves the with-a-store case false, which is
  the half the reclass does not reach.

## Anchor changes

- **Changed:** `provider_rate_limits`'s recovery class in Section 4.1.8 becomes two-valued; Section
  14.3's `C` bullet splits its two carries; Section 14.4's first paragraph and After-restart list
  name both restorable classes; Section 8.9's Recovery-semantics bullet gains the store condition.
- **Added:** the fail-open rule (step 3), the reading/no-reading sentence (step 4), a template row
  (step 8), a column-header clause (step 9).
- **Removed:** in `SPEC.md` Section 14.3 and `SPEC.md` Section 8.9, the unconditional promise that a
  last-known-good value is "carried across" both a failed refresh and "a process restart". Plans
  quoting it are not edited; they record what was true when written.

## Status

Not started.
