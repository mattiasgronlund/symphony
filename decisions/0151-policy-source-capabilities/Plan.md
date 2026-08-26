# Plan — 0151 Reading and materializing the policy source

## Scope

- `VCSX-SPEC.md` — Section 9.1 (VCS Backend Plugin), Section 9.3 (Capability Descriptors), Section
  4.1 (Operation Set, `load_policy`), Section 6.1 (File Discovery and `vcsx.toml` Merge), Section
  6.6 (`[hooks.engine]`), Section 6.11 (Validation), Section 13.1 (Test Matrix), Section 13.2
  (Implementation Checklist), Section 13.3 (Conformance Statement).
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — Section 6.1's VCS-backend declaration table gains a
  column; Section 3 or 4 gains a row for `vcsx.toml`'s discovery precedence.
- `conformance/vcsx/vocabulary.json` — **no change**. Capabilities are not a group there.
- `conformance/vcsx/vectors/` — no new file for the capabilities; the `vcsx.toml` location is
  checked in Section 13.1.
- `SPEC.md` and Symphony's artifacts — no change.

## Steps

1. **`VCSX-SPEC.md` Section 9.1 — `read_at_source(remote, branch, path)` joins the list.** Ensure
   the required-capability list carries a capability answering the file's content at that revision,
   none where the revision carries no such file, or that it could not be read — three distinct
   answers, because Section 6.1 distinguishes `policy_source_unreadable` from `policy_not_found`.
   Ensure the bullet says it reads a copy the checkout already holds and acquires nothing. *Done
   when:* `load_policy` is realizable through the plugin layer, and the two conditions Section 6.1
   names separately are separable in the capability's answer.
2. **`VCSX-SPEC.md` Section 9.1 — `export_source(remote, branch, into)` joins the list as OPTIONAL
   with a descriptor field.** Ensure the capability materializes the revision at `into`, that it is
   the first OPTIONAL capability in Section 9.1, and that a backend declares whether it provides one
   — in the shape "whether it can derive more than one working tree from one store" already uses.
   Ensure the `into` argument's reason is stated: where a backend materializes is the consumer's
   decision, as `store_location` and `tree_location` already are, because backends materialize
   differently enough that the engine cannot own the mechanism. *Done when:* the descriptor carries
   the declaration, and the capability's optionality is readable in Section 9.1 rather than only in
   Section 9.3.
3. **`VCSX-SPEC.md` Section 9.1 — the ordering that makes both credential-free.** Ensure the section
   states why the two take no `git_access` and no `git_credential`, citing three passages by their
   own sections: `VCSX-SPEC.md` Section 4.1 places `provision` "before everything the engine reads
   out of the repository"; `VCSX-SPEC.md` Section 8.1 resolves the policy source to "the copy
   belonging to the resolved `remote`", which that `provision` already put in the store; and
   `VCSX-SPEC.md` Section 13.1 already records the consequence, that a change to the policy source
   after that does not take effect until the next unit of work. Ensure the network enumeration in
   `VCSX-SPEC.md` Section 9.1 still names exactly four, and that its sentence "Every other
   capability above is local to the checkout" absorbs both additions **explicitly**, since that
   section says a capability's context is read off the list and never inferred from its arguments.
   *Done when:* a reader can tell why a capability naming a `remote` and a `branch` acquires
   nothing, without re-deriving it.
4. **`VCSX-SPEC.md` Section 9.1 and Section 4.1 — the two false sentences.** Ensure Section 9.1's
   closing sentence quoted as "every operation Section 4.1 defines is realizable through it" is true
   once the capabilities exist, and that Section 4.1's `load_policy` clause quoted as "it is why no
   capability of Section 9.1 reads a file at a revision — one operation does it once, rather than a
   capability doing it per read" is replaced. Ensure the replacement is written from the
   post-decision 0141 text: under the policy pin every entry point reads and validates the document,
   so the read is per invocation rather than once per unit of work. *Done when:* neither sentence
   asserts what the list contradicts, and Section 4.1 says what `load_policy` is realized through.
5. **`VCSX-SPEC.md` Section 6.6 — the resolution's `Implementation-defined` clause narrows rather
   than disappears.** Ensure the sentence quoted as "How an engine resolves a `host_side` unit is
   `Implementation-defined` and MUST be documented (Section 13.3)" is reconciled with the
   capability: the mechanism for turning a revision into a directory is `export_source`'s, while
   which unit form the engine's `run` takes, and how a unit is addressed within the materialized
   source, remain the engine's and remain documented. Ensure the Section 13.3 obligation and its
   rows are **not** deleted as a side effect — a deletion nobody should make while narrowing a
   clause. *Done when:* the obligation still has a referent, and the part the capability answers is
   no longer inside it.
6. **`VCSX-SPEC.md` Section 6.6 and Section 6.11 — the refusal is determinable.** Ensure a merged
   surface declaring a `[hooks.engine]` unit, under an engine whose declared unit form requires
   materialization and a backend whose descriptor declares no `export_source`, is refused at
   validation with `capability_unsupported`. Ensure the condition is stated over the **engine's
   declared unit form** rather than per unit — a command-line unit form carries no statement of
   whether it names a path in the source, so a per-unit condition is not evaluable from the
   specified configuration. *Done when:* both halves of the test are static and held before the
   policy runs, and the refusal creates no new first-use producer.
7. **`VCSX-SPEC.md` Section 9.3 — the first-use sentence widens.** Ensure the sentence quoted as
   "What remains on the first-use side is an OPTIONAL capability (Section 9.2)" accounts for an
   OPTIONAL capability in Section 9.1 whose refusal is on the determinable side. *Done when:* the
   split Section 9.3 describes is true with an OPTIONAL Section 9.1 capability in it.
8. **`VCSX-SPEC.md` Section 6.1 — `vcsx.toml` gets a location.** Ensure the section fixes
   `vcsx.toml`'s path relative to the repository root and states its discovery precedence as
   `Implementation-defined` and MUST document, on `repo.policy.toml`'s own precedent in the same
   section. Ensure the reason is recorded where it belongs: two conforming engines merging different
   documents from one revision execute different policies. *Done when:* both files `load_policy`
   reads have a stated address, and neither is left to a constant an engine picks.
9. **`VCSX-SPEC.md` Sections 13.1 and 13.2 — rows and lines.** Ensure Section 13.1 covers (a) a
   `load_policy` against a revision carrying no `repo.policy.toml` yielding `policy_not_found` where
   a source it could not read yields `policy_source_unreadable`, now realized through a capability
   with three answers; (b) a `[hooks.engine]` declaration against a backend declaring no
   `export_source` being refused with `capability_unsupported` before the policy runs; (c) a
   `vcsx.toml` at the fixed location being merged and one elsewhere not being. Ensure Section 13.2
   gains the matching lines without restating Section 13.1's wording. *Done when:* each addition has
   a check and none duplicates another.
10. **`VCSX-SPEC.md` Section 13.3 and `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` — the rows.** Ensure
    Section 13.3's obligations list carries `vcsx.toml`'s discovery precedence and the (narrowed)
    host-side unit resolution, and that the template carries a row for the first modelled on its
    existing `repo.policy.toml discovery precedence | 6.1`. Ensure the VCS-backend declaration table
    in `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` Section 6.1 gains a column for `export_source`,
    beside its existing column headed "Derives >1 working tree from one store". *Done when:*
    `python3 scripts/validate_spec_consistency.py` reports 0 errors and 0 warnings, and every
    `Implementation-defined` or MUST-document sentence this decision adds or narrows has a row in
    the **same commit** — `check_obligations` errors rather than warns (`CLAUDE.md`, decision 0128).

## Cross-cutting sync

- `VCSX-SPEC.md` Sections 13.1, 13.2 and 13.3: steps 9 and 10.
- `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`: step 10 — **a row and a column are owed**.
- `conformance/vcsx/vocabulary.json`: no change, checked rather than assumed.
- `SPEC.md` Sections 6.4, 17, 18 and `CONFORMANCE-STATEMENT-TEMPLATE.md`: **no change**, and this is
  a step rather than an omission. Symphony carries its own host-side-unit resolution obligation, for
  its workspace lifecycle hooks (`SPEC.md` Section 5.3.4), in four places — `SPEC.md` Section 15.4's
  bullet, `SPEC.md` Section 18.1.2's checklist line, `SPEC.md` Section 19's list, and
  `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1's row. That obligation is **parallel to** the one
  step 5 narrows, not derived from it: it is about a Symphony hook's unit, where step 5 is about a
  `[hooks.engine]` unit under the engine's policy surface. None of the four is to be edited or
  deleted as a side effect of the narrowing. Confirm by re-reading them rather than by assuming the
  documents are independent.

## Ordering

- **After decision 0141**, whose fingerprint pin is the text step 4's replacement is written from.
  The record exists, so nothing waits.
- **After decision 0150.** Both edit Section 9.1's capability list, its closing paragraph and its
  network enumeration. Two decisions editing one anchor set in series with a gap between them is
  where a plan's quoted spans go stale; run `python3 scripts/check_plan_anchors.py` against this
  plan at the revision 0150 landed on rather than at the one it was written against.

## Anchor check

`python3 scripts/check_plan_anchors.py decisions/0151-policy-source-capabilities/Plan.md --rev
22b5194` reports reach findings at eight sites. Three are load-bearing and are now named in
Cross-cutting sync — `SPEC.md` Sections 15.4, 18.1.2 and 19, which carry Symphony's parallel
host-side-unit obligation that step 5 must not touch. The rest are benign and are recorded so a
later reader does not re-investigate. Line numbers below are refreshed to `b7912f6`; the site
assessments are the original ones and are unchanged.

- `conformance/vcsx/README.md:112` matches on the fragment "every operation Section 4.1", but its
  sentence is about operations Section 4.1 gives **no lifecycle position**, not about realizability
  through the capability list. Step 4's sentence has no twin there.
- `VCSX-SPEC.md:538` (Section 4.3) and `VCSX-SPEC.md:190` (Section 3.3) carry the
  more-than-one-working-tree phrasing step 2 quotes from Section 9.1's descriptor list. They are the
  same property stated for a reason and for a checkout mode; neither is edited.
- `VCSX-CONTRACT.md:248` (Section 6) carries the `provision`-precedes-everything phrasing step 3
  quotes from Section 4.1. That is the contract restating the ordering, which step 3 relies on
  rather than changes; if step 3's wording moves, check that the contract still agrees.
- `VCSX-SPEC.md:1033` (Section 6.4) carries the copy-belonging-to-the-resolved-remote phrasing,
  which is Section 6.4 stating the same resolution for a base ref. Not edited.

Re-run at `d78d7af`, after decisions 0140–0146, 0148 and 0152 landed, reported **one** finding, and
it was the `conformance/vcsx/README.md` site above: the `operations` bullet moved from `:108` to
`:112` when decision 0141 inserted Section 4.3's `load_policy` invariant above it. The assessment
stands; only the address moved. That file has no numbered sections, so the check has no finer
address for it than a line, and this record goes stale again whenever anything is inserted above
that bullet — the durable way to re-find the site is the `operations` bullet carrying
`lifecycle_position: null`, not the number.

Re-run again at `b7912f6`, after decisions 0147 and 0149 landed, reports **no** finding from 11
quoted spans, and every address above resolves unchanged. That pair edited `SPEC.md`,
`CONFORMANCE-STATEMENT-TEMPLATE.md`, `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` and
`conformance/vocabulary.json`, none of which this plan addresses — each site was re-read at that
revision rather than inferred from the file list.

One site is named only incidentally, recorded so a later reader does not read silence as judgement.
`conformance/vcsx/vocabulary.json:336` (`arguments`) carries the
copy-belonging-to-the-resolved-remote phrasing in its `policy_branch` note, and the check counts it
named because the word `arguments` happens to occur in step 3's prose about capability contexts —
a registry group is matched as a bare identifier anywhere in the plan. The judgement it did not get
mechanically it gets here: the note fixes which revision the argument names, not how that revision
is read, so step 1's `read_at_source` does not reach it and it is not edited.

The re-run Ordering asks for — at the revision decision 0150 lands on — has **not** been made,
because 0150 has not landed. Neither `d78d7af` nor `b7912f6` substitutes for it: both predate
0150's edits to Section 9.1's capability list, its closing paragraph and its network enumeration,
which is the anchor set this plan shares with that one.

## Anchor changes

- **Added:** `read_at_source(remote, branch, path)` and `export_source(remote, branch, into)` as
  `VCSX-SPEC.md` Section 9.1 capabilities, the second OPTIONAL with a descriptor field; a fixed
  location and an `Implementation-defined` discovery precedence for `vcsx.toml` in `VCSX-SPEC.md`
  Section 6.1; a template column and a template row.
- **Changed:** `VCSX-SPEC.md` Section 4.1's `load_policy` clause about there being no such
  capability; `VCSX-SPEC.md` Section 9.1's claim that every operation is realizable through the
  list; `VCSX-SPEC.md` Section 6.6's `Implementation-defined` resolution clause narrows;
  `VCSX-SPEC.md` Section 9.3's first-use sentence widens.
- **Removed:** from `VCSX-SPEC.md` Section 4.1, the sentence quoted as "it is why no capability of
  Section 9.1 reads a file at a revision — one operation does it once, rather than a capability
  doing it per read". Plans quoting it are not edited; they record what was true when written.

## Status

Not started.
