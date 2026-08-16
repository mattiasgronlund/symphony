# Plan — 0099 The edge is the binding, and a unit at a position that says nothing

## Scope

`VCSX-SPEC.md`: Sections 4.3 "Reason-Token Registry", 6.6 "`[hooks.engine]`", 6.8 "`[messages]`",
6.11 "Validation", 8.2 "Result Envelope", 10.2 "Pull-Request Composition", 10.3 "Squash
(`pr_to_squash`)", 10.4 "Content Scanning", 13.1 "Test Matrix", 13.2 "Implementation Checklist".

`VCSX-CONTRACT.md`: Section 9 "Message Formulation".

`conformance/vcsx/vocabulary.json` (`message_formulation`, `config_reasons`, `output_keys`),
`conformance/vcsx/vectors/policy-validation.json`.

`SPEC.md`: no change. Its references to `scan-content` and `pr_to_squash` describe behavior rather
than the schema keys this decision moves, and remain true.

## Tokens introduced

- `transform_unbound` — configuration reason (Section 6.11), for a `[messages.squash]` `transform`
  naming a unit the consumer bound nothing to.

## Tokens removed

- `title_scan`, `body_scan` — keys of `[messages.pr]`. The capability they declared survives in the
  repository's own scan unit; no key replaces them, and none is added for the commit diff.

## Steps

1. **`[messages]` carries no scan key (`VCSX-SPEC.md` Section 6.8 "`[messages]`")** — ensure the
   example block declares `body_source` under `[messages.pr]` and `strategy`/`transform` under
   `[messages.squash]`, and no scan key under any of the three tables. Ensure the section states that
   a scan is bound by a `[policy]` edge rather than here, and why: the binding a repository writes for
   a scan is the one it writes for every other unit the engine runs at a position. *Done when* a
   search for `title_scan` or `body_scan` in the document returns nothing, and `[messages.commit]`
   still declares no key.

2. **`transform` is a documented key (`VCSX-SPEC.md` Section 6.8)** — ensure `transform` has a field
   bullet naming the unit it binds, its position, and that a named transform with no unit bound is a
   configuration error, with `Default: none` and the disposition where none is named (the code host
   composes the squash message). *Done when* `transform` is documented to the same shape as
   `strategy` and `transform_unbound`'s scope is readable from Section 6.8 alone.

3. **Section 10.4 "Content Scanning" states the binding and the supplied content** — ensure it states
   that a scan is declared as a hook and run by a `[policy]` edge at a lifecycle position; that
   `[messages]` carries no scan key and a position no edge binds runs no scan, which is what Section
   5.4 already says a position does; and what the engine supplies at each position — the commit
   message and the diff the commit would record at `before:commit`, the composed title and body at
   `before:create_pr` — mirroring Section 10.3's "the engine supplies only the position and the
   pull-request content". Ensure the phrase "during `create_pr`" no longer appears, execution context
   being stated as following the declaring artifact (Sections 3.2, 6.6). Ensure the existing paragraph
   on the title and body being the values the operation writes is preserved. *Done when* no sentence
   in the section places a scan anywhere but at a lifecycle position.

4. **Section 10.2 "Pull-Request Composition" names no profile key** — ensure the sentence that
   assigned `title_scan` to the title and `body_scan` to the body instead states that the composed
   title and body are what a `before:create_pr` scan inspects. *Done when* Section 10.2 cites Section
   10.4 without naming a key.

5. **Section 10.3 "Squash (`pr_to_squash`)" states the transform's binding and disposition** — ensure
   it states that the transform is named by `[messages.squash]` `transform` and bound by the consumer
   as the `template` unit is; that a named transform with no unit bound is `transform_unbound` at
   validation; that Section 6.6's bound applies to it; and that a transform giving no usable answer
   yields `merge:hook_unanswered` and the operation does not act, stated as the effect — the pull
   request is not merged — rather than as a claim about whether the forge was called. *Done when* the
   section answers all three conditions of Section 6.6 for the transform and states no separate
   prohibition on falling back to the pull request's own content.

6. **Section 6.6 "`[hooks.engine]`" bounds every unit at a position** — ensure the paragraph carrying
   the bound states that it holds for every unit the engine runs at a lifecycle position and waits on,
   naming the `pr_to_squash` transform as the one that is not a hook, on the reasoning that what makes
   the bound necessary is that the program is one this specification does not describe rather than
   which key named it. *Done when* no unit the engine waits on at a position is outside the bound.

7. **`hook_unanswered`'s gloss reaches the transform (`VCSX-SPEC.md` Section 4.3)** — ensure the
   `(any gated)` registry row and the paragraph beginning "`blocked`, `failed` and `hook_unanswered`
   divide" quantify over a unit the engine ran at a `before:<op>` position rather than over a hook
   alone, and name the transform as the second such unit. Ensure the class stays `error` and the
   `Default need` stays `—`. *Done when* the row's gloss admits the transform without admitting
   anything that is not at a position.

8. **`transform_unbound` is a validation row (`VCSX-SPEC.md` Section 6.11 "Validation")** — ensure the
   table carries a row for a `[messages.squash]` `transform` naming a unit the consumer bound nothing
   to; ensure the fifth validation input names both `template_unbound` and `transform_unbound`; and
   ensure the paragraph explaining why the fifth input is stated rather than inferred extends to the
   transform, whose first use is later than the template's. *Done when* the reason is judged from an
   input Section 6.11 already names and no new input is introduced.

9. **`unanswered_gates` admits a unit that is not a gate (`VCSX-SPEC.md` Section 8.2)** — ensure the
   key's description quantifies over the `before:*` units that gave the engine no usable answer. The
   key name is unchanged; ensure the tension is stated once rather than left for a reader to notice.
   *Done when* a transform's condition has a reported home under an unchanged key name.

10. **`VCSX-CONTRACT.md` Section 9 "Message Formulation"** — ensure the pull-request bullet attributes
    the strict-title / relaxed-body difference to the repository's own check at the
    `before:create_pr` position rather than to configuration, and ensure the squash bullet states that
    a transform giving no usable answer leaves the pull request unmerged. *Done when* the surface
    asserts no per-field schema this document no longer defines.

## Cross-cutting sync

- `VCSX-SPEC.md` Section 13.1 "Test Matrix": a scan bound by an edge blocks its operation and a
  position no edge binds runs no scan; a `pr_to_squash` that gives no usable answer yields
  `merge:hook_unanswered` with the pull request unmerged and the condition in
  `outputs.unanswered_gates`; a `[messages.squash]` `transform` with no unit bound is refused at
  validation with `transform_unbound`.
- `VCSX-SPEC.md` Section 13.2 "Implementation Checklist": the message-formulation seam bullet names
  the scan's binding rather than a scan key.
- `conformance/vcsx/vocabulary.json`: remove the `title_scan` and `body_scan` entries from
  `message_formulation`; record how `scan-content` and `pr_to_squash` are bound; add
  `transform_unbound` to `config_reasons`; widen the `unanswered_gates` meaning under `output_keys`.
- `conformance/vcsx/vectors/policy-validation.json`: vectors for a named transform with and without a
  bound unit, and for a squash strategy naming no transform; extend the `bound_units` note to the
  transform.
- `SPEC.md` Sections 6.4, 17, 18: no change — no key it documents is affected.

## Anchor changes

- `title_scan` — removed. No successor key; a scan's profile is the repository's own and is named in
  its unit.
- `body_scan` — removed. As above.
- `transform_unbound` — added (Section 6.11).

## Status

Applied to `VCSX-SPEC.md`, `VCSX-CONTRACT.md` and `conformance/vcsx/`.

## Left open

Section 9.2's `request_merge(pr, strategy, expected_head)` takes no message, and nothing in Section
9.2, its descriptor fields or Section 12.3 carries the transform's output to the forge. The seam
Section 10.3 describes therefore has no route to the operation that would use it. Verified against the
document on 2026-08-16; predates this issue and is out of its scope. See `Background.md`.
