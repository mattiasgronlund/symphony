# Plan — 0125 A gate that stopped existing should not read as a gate that passed

## Scope

`VCSX-SPEC.md`: Section 4.1 "Operation Set" (the `await_checks` entry), Section 4.3 "Reason-Token
Registry" (the row and its boundary paragraph), Sections 13.1, 13.2.

`SPEC.md`: Section 9.10 "Forge Operations, Pull Requests, and Review Writes" (the disposition list),
Sections 17.4, 18.1.

`VCSX-CONTRACT.md`: Section 6, where `await_checks`'s terminal conditions are named at the surface.

## Steps

1. **`await_checks` — the fifth terminal condition.** Ensure the entry in `Operation Set` reads until
   one of **five** conditions holds, the fifth being that the forge reports no required checks for the
   pull request. Done-condition: the operation's conditions and `checks_state`'s determinate answers
   correspond, with `unchanged` and an undetermined state covered as they already are.

2. **The registry row.** Ensure Section 4.3 carries `await_checks` / `no_checks` / `done` / `—` with a
   gloss naming the condition: the forge reports no required checks for the pull request, so there is
   nothing to wait for. Done-condition: the row exists with class `done` and no default need, `done`
   reasons carrying none.

3. **The boundary paragraph.** Ensure a paragraph states why `no_checks` is not `ok`, in the idiom the
   registry uses for its other near-neighbour pairs: `ok` names checks that completed successfully and
   this names checks that do not exist, and a consumer that could not tell them apart could not see a
   merge gate stop existing. Done-condition: the paragraph argues the split rather than asserting it,
   and names what a shared token would cost.

4. **Why `done` rather than `needs_caller`.** Ensure the same paragraph states that the class follows
   Section 4.2's definition — a benign no-op is `done` — and that requiring checks is a Way of Working
   the engine does not hold (Section 1.1), so a repository that wants the anomaly surfaced binds the
   reason. Done-condition: the class is argued from the operation's outcome rather than from a policy
   preference.

5. **`VCSX-CONTRACT.md` Section 6.** Ensure the `await_checks` description at the surface names the
   fifth condition alongside the four it already lists. Done-condition: the surface and the full spec
   describe the same operation.

6. **`SPEC.md` `Forge Operations` — the fifth disposition.** Ensure the outcome list disposes of five:
   `await_checks:no_checks` continues the flow as `await_checks:ok` does, the pull request being
   mergeable with no required checks. Ensure the accompanying reasoning states that Symphony holds no
   opinion about whether a repository ought to have checks, which is the repository's Way of Working.
   Done-condition: no engine outcome reaches `SPEC.md` without a stated disposition.

7. **Sections 13.1, 13.2; `SPEC.md` Sections 17.4, 18.1.** Ensure the engine test matrix checks that
   an `await_checks` against a pull request the forge reports no required checks for yields
   `no_checks` on the first read — not `ok`, not `still_pending` after burning a supplied bound, and
   not `failed` — and that a `land --await` against such a repository merges rather than ending on the
   await's result. Ensure `SPEC.md`'s matrix checks the disposition. Done-condition: steps 1, 2 and 6
   each have a check, and the bound-burning misreading is asserted against.

## Cross-cutting sync

Section 8.5: a new reason token is a `MINOR`, absorbed by existing `#done` edges through the `#class`
fallback.

`SPEC.md` Section 6.4 gains nothing: the outcome needs no configuration. Section 14.1 gains nothing:
the disposition is to continue, so no failure class is involved.

## Anchor changes

New anchor: the `await_checks:no_checks` reason token. No anchor is renamed or removed.

## Status

Applied to `VCSX-SPEC.md` (Sections 4.1, 4.3, 9.2, 13.1), `VCSX-CONTRACT.md` (Section 6), `SPEC.md`
(Sections 6.4, 9.10, 17.4, 18.1) and `conformance/vcsx/vocabulary.json`.
