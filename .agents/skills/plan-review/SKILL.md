---
name: plan-review
description: Check a plan's claims about SPEC.md, VCSX-SPEC.md, VCSX-CONTRACT.md, the Conformance Statement templates and conformance/ before implementing it — quote fidelity, anchor reach, convention compliance, and whether each asserted consequence survives the premise the plan removes. Use once a plan is written and before its first edit.
---

# Plan Review

A plan is read once and then trusted. Every claim it makes about a document — what a section says,
which sections carry a premise, what a convention requires — is a claim the implementation acts on
without re-checking. Check them before the first edit. A claim caught at review has already been
written into the corpus.

## The test

> Does every claim this plan makes about the corpus survive being checked against the corpus?

- "Section 13.2's operation-set bullet loses its 'required set' framing" — **fails**. The phrase
  occurs in Section 4.1 and nowhere in Section 13.2.
- "Sections 9.1 and 13.3 carry the engine-extension premise" — **fails**. Section 9.3 carries it
  too, and a plan that names two of three leaves the third standing.
- "Keep the OPTIONAL-capability path, which the template's first-use table needs" — **fails**. The
  same plan removes two of that path's three producers, so the path it keeps is unreachable.
- "`SPEC.md` needs no change — verified: `engine-defined` and `MAY define additional` occur only
  in `VCSX-SPEC.md` and its template" — **passes**. The claim arrives with the check that
  settles it.

## The four lenses

**Q — quote fidelity** and **R — anchor reach** are mechanical:

```sh
python3 scripts/check_plan_anchors.py <plan.md> --rev <the revision the plan was written against>
```

Q asserts every quoted span occurs in the file and section the plan attributes it to. R reports
every other site carrying the same distinctive wording that the plan does not name. Pass `--rev`: a
plan quotes the tree it was written against, and against a later tree every quotation of wording the
plan removes reads as absent. The script's docstring states its six limits; the sharpest is that
matching is literal, so a difference the plan's own wording carries is bridged only where a
four-word window falls clear of it.

**C — convention compliance** is read, against the obligations no script here checks:

- Implementation lands in a **sibling** worktree, `../<repo>-<slug>`, not under the repository root.
- A substantive content change syncs the cross-cutting sections: `SPEC.md` Sections 6.4, 17 and 18;
  `VCSX-SPEC.md` Sections 13.1, 13.2 and 13.3.
- A change adding an `Implementation-defined` or "MUST document" obligation adds its row to the
  matching Conformance Statement template. Three decisions in a row missed this (decision 0128).

**P — premise and consequence** is read, and is the lens the other three cannot stand in for. For
each thing the plan says to *keep*, name the premise being removed, then count what still produces
the kept thing once it is gone. A consequence with no surviving producer is not preserved by being
left in the document.

## Worked failure (decision 0134)

One plan, four claims about the corpus, none of them true:

1. A worktree under `.claude/worktrees/`, against the sibling rule — corrected mid-turn, by which
   point 17 misplaced worktrees had accumulated (**C**).
2. A "required set" framing attributed to `VCSX-SPEC.md` Section 13.2, which does not carry it
   (**Q**).
3. Sections 4.1 and 9.1 named as carrying the engine-extension premise; Section 9.3 carries it too,
   and was found by hand mid-implementation (**R**).
4. "Keep the OPTIONAL-capability path" — but a *declared* capability is supported and cannot yield
   `unsupported`, so closing the operation set had removed the path's producers. This one
   **shipped** into `VCSX-SPEC.md`, and was caught only by re-reading it on a second pass
   (**P**).

Measured against `1dfec5d`, the tree that plan was written against: 8 findings from 28 quoted spans.
Q reported defect 2 and one unmarked elision; R reported all three unnamed sites the plan itself
enumerated — `VCSX-SPEC.md:2781`, `conformance/vcsx/vocabulary.json:275` and
`conformance/vcsx/README.md:108` — and three more the plan did not, among them
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md:155`, whose "required operation set" the plan narrowed in
Section 2 and left standing in Section 5.

## Checklist

- The script was run with `--rev` set to the tree the plan was written against, and every Q finding
  is either repaired in the plan or recorded as a deliberate paraphrase.
- Every R site is either named by the plan or recorded as needing no change, with the reason.
- Each enumeration the plan restates was counted against its source, not against the plan's prose.
- Each consequence the plan keeps has a named surviving producer.
- The worktree is a sibling, the cross-cutting sections are named, and any new obligation names its
  template row.
- Findings are appended to `~/.claude/plans/log/plan-review.jsonl` — one `kind: review` object
  with `"repo": "symphony"`, `lenses_applied` drawn from `Q`/`R`/`C`/`P`, and a `findings`
  array. The letters are symphony's own, so `python3 ~/.claude/bin/plan_review_audit.py` keeps
  this repository's hit rates separable from the other repository sharing the file. A defect
  found after the fact goes back as a `kind: retro` object, classified by the lens that should
  have caught it.

## Boundary

`decision-record` owns the reasoning behind a change, `spec-guarantee` the wording of the clause it
introduces, and `scripts/validate_spec_consistency.py` the drift between the documents and the
artifacts derived from them. This skill owns the plan's claims about the corpus and nothing else. It
reports; it does not gate, and it does not decide whether a finding is worth acting on.
