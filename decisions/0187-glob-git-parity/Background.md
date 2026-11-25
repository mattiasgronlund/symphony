# Background — 0187 A glob with git as its reference, and five places it is not git's

## Context

Reported as issue #186 from `symphony-rs`, against `c12ed93`, while planning the matcher (its
decision 0159, roadmap I1). Decision 0183 made every `base_branch_allowed` entry "a glob in the
syntax of a gitignore pattern" (`VCSX-SPEC.md` Section 8.1 (Entry Points and Arguments)), and
`SPEC.md` Section 9.7 (Repository Provisioning and the VCS Engine) applies the same match to
`vcs.base_branch_allowed`. The fixture `conformance/vcsx/vectors/base-branch-allowed.json` says its
vectors were checked against git's own wildmatch. So git is the reference, and the reference an
operator reaches for: write an entry, try it with git, trust the answer.

Section 8.1 states the glob in its own words, and those words leave open, or contradict, what git
does in five places. Each one is a place where two implementations of the same sentence can admit
different bases, or where an operator's git check and the bound give different answers. A sixth gap
does not concern git: neither document says what a configured but empty bound means, and the two
judges in `symphony-rs` already disagree about it.

The direction of each difference matters more than the difference itself. A bound narrower than the
operator's git check refuses something they expected admitted. The refusal is visible: the engine
reports `base_branch_not_permitted`, and Symphony refuses the issue, logs it and comments on it, or
refuses at startup with `invalid_base_branch_pattern` (`SPEC.md` Section 6.3). A bound wider than the
check admits a base the operator tested and saw refused. Nothing reports that. The admitted run
back-merges from, and opens its pull request against, a branch the operator believes is outside the
bound. That is the failure 0183 was written to rule out, and it is the test applied to every option
below.

## Measurements

Every claim below was measured twice, on git 2.47.3 (the Debian package) and on git 2.56.1 (the
latest release, built from the `v2.56.1` tag with `NO_RUST=1`; the Rust sources in that release are
hashing and varint code, and `wildmatch.c` is C). The two versions gave byte-identical output on
every probe.

Two tools were used:

- **`git for-each-ref --format='%(refname:strip=2)' refs/heads/<entry>`**, over a repository holding
  the branches listed below. This is the tool the issue and the fixture used.
- **`t/helper/test-tool wildmatch wildmatch <name> <entry>`**, git's own test helper, built from the
  same tree. It calls `wildmatch(entry, name, WM_PATHNAME)` and nothing else, so it is the glob with
  no ref-matching rules around it. (The mode word is repeated: the first `wildmatch` selects the
  helper, the second its `WM_PATHNAME` mode. Omitting it fails every match silently.)

Branches: `]`, `a]`, `a/-`, `a/]`, `a/a`, `a/b`, `a/c`, `a/d`, `a/m`, `a/x`, `a/z`, `a/é`, `x/y`,
`policy`, `master`. For a plain entry, `for-each-ref` also lists names below the entry, as the last
section explains. The glob column below is the same under both tools.

| Entry | Matches | Section 8.1 today |
|---|---|---|
| `a/?` | `a/-` `a/]` `a/a` … `a/z`, not `a/é` | `?` matches "one character" |
| `a/??` | `a/é` | as above |
| `a/[é]` | nothing | "one character from a set" |
| `a/[!b]` | every one-byte name but `a/b`; not `a/é` | as above |
| `a/[]b]`, `[]]` | `a/]` `a/b`; `]` | silent |
| `a/[]`, `a/[!]` | nothing | silent |
| `a/[z-a]`, `a/[b-a]` | `a/z`; `a/b` | "a set or range" |
| `a/[[:alpha:]]` | `a/a` … `a/z` | silent |
| `a/[[:bogus:]]` | nothing | silent |
| `a/[a-]`, `a/[-a]` | `a/-` `a/a` | silent |
| `a/[a\-c]` | `a/-` `a/a` `a/c`, not `a/b` | `\` "makes the next character literal" |
| `a/[\]]` | `a/]` | as above |
| `a/[a-c-m]` | `a/-` `a/a` `a/b` `a/c` `a/m`, not `a/d` | silent |
| `**` | every name, `policy` included | "special only where it is a whole segment" |
| `x\/y` | `x/y` | agrees |
| `x[/]y`, `a/[b`, `a/b\` | nothing | agrees |

The mechanism, from `wildmatch.c` at `v2.56.1`:

- The pattern and the name are `const uchar *`, walked one byte at a time. There is no decoding.
- In a bracket, the first member is read before the loop tests for `]`, so a `]` there, after an
  optional `!` or `^`, is a member. `[]` and `[!]` therefore run off the end of the pattern, which
  returns `WM_ABORT_ALL`: the entry matches nothing.
- `-` is a range only where a previous member exists and the next byte is neither `]` nor the end.
  After a range or a class the previous member is reset, so the `-` in `[a-c-m]` is literal.
- A range tests `t_ch <= hi && t_ch >= lo` and nothing else. The low endpoint was already compared
  as a literal on the previous pass, so `[z-a]` matches `z` and nothing else. This follows from how
  the loop is written, and git's documentation does not state it as a rule.
- `\` escapes inside a bracket, an endpoint included.
- `[:name:]` accepts exactly twelve names (`alnum alpha blank cntrl digit graph lower print punct
  space upper xdigit`), tested through git's own `sane-ctype.h` table, which is ASCII-only and does
  not depend on the locale. An unknown name returns `WM_ABORT_ALL`.
- `**` is special where it has the pattern's start or a `/` before it, and the pattern's end or a
  `/` after it. A whole-pattern `**` meets both, sets `match_slash`, and matches every name.

`gitignore(5)` at the same tag lists the three `**` forms 0183 copied, adds "Other consecutive
asterisks are considered regular asterisks", and refers the rest to "fnmatch(3) and the
FNM_PATHNAME flag". So the manual does not settle any of the five gaps. The code does.

## The six gaps and their answers

### 1. Bytes, not characters

Section 8.1 says `?` matches "one character". Git matches one byte. On `a/é` the two readings
disagree in both directions: `a/?` admits it under characters and refuses it under bytes, while
`a/??` does the reverse.

- **Characters** (steelman). This is what the operator means when they write `release/?`: one
  symbol. It is also what the sentence already says.
- **It loses on direction.** An operator who tries `release/?` against `release/é` with git sees a
  refusal. A character-matching bound admits it, so the bound is wider than the check, which is the
  silent case. Characters also require the engine to choose an encoding, and the engine "holds a
  base branch opaque … and interprets nothing about the name" (Section 8.1). Git ref names are byte
  strings with no declared encoding.
- **Bytes (chosen).** `?`, `*` and `[...]` count bytes, and a character class tests one byte. The
  cost: a non-ASCII member inside `[...]` is a set of its bytes, so `[é]` never matches `é`. That
  cost refuses, and so is visible. Making a non-ASCII byte in a bracket not well formed was
  considered. It would be one more divergence from git, and it would buy nothing in the safe
  direction, since today's reading already refuses.

### 2. POSIX character classes

Git accepts the twelve `[:name:]` classes. Section 8.1 names "a set or range" and nothing else, so
read literally `[[:alpha:]]` is the set `[ : a l p h` followed by a literal `]`. On `a/b` that reading
refuses, and on `a/a]` it admits. It differs from git in both directions.

- **Leave classes out, or make them not well formed** (steelman). This keeps the syntax smaller, and
  "not well formed" fails closed.
- **It loses.** The literal reading is already in force wherever the text is silent, and it widens:
  `a/[[:alpha:]]` admits `a/a]`, which git refuses. "Not well formed" is safe but refuses something
  git defines exactly. Git's table is ASCII-only and ignores the locale, so there is no
  implementation latitude to fear.
- **Admit the twelve classes with git's ASCII meanings (chosen).** An unknown class name is not well
  formed. In git it matches nothing, which is the same effect as malformed, so this is git's answer
  stated in the bound's terms.

### 3. A reversed range

Git's `[z-a]` matches `z`. That is a property of the loop's order, not a documented rule.

- **Copy git** (steelman). An operator testing `[z-a]` in git sees `z` admitted, and the bound would
  agree with them.
- **It loses** for two reasons. Writing the loop's order into the specification makes an accident
  normative, and an implementation using any other range test would be wrong for a reason no reader
  could guess. And nobody writes `[z-a]` meaning `z`. They mean `[a-z]`, so what their git check
  confirms is a typo.
- **Not well formed (chosen).** A range whose first endpoint is above its second is not well formed,
  so a bound holding it admits no base, and Symphony refuses it at startup (Section 6.3's existing
  check already covers "not well formed"). This differs from git only in the direction that refuses,
  and it refuses loudly. It matches what the issue leaned towards.

### 4. The bracket's grammar: `]` first, `-` at an edge, `\` inside

Section 8.1 says `[...]` is "a set or range" and that `\` makes the next character literal. It does
not say where a set ends, when `-` is a range, or whether `\` works inside a set. Without those rules,
whether `[]` is an unclosed bracket or an empty set is an implementation's guess. The first guess
gives "not well formed, admits no base". The second gives "matches nothing", or, negated as `[!]`,
"matches any byte". An implementation that reads `[!]` as "any byte" admits what git refuses.

- **Adopt git's grammar (chosen).** A `]` straight after `[`, or after `[!` or `[^`, is a member, so
  `[]` and `[!]` are unclosed and not well formed. A `-` is literal when it is first or last, or when
  it directly follows a range or a class. `\` escapes inside a set, an endpoint included. No
  steelman for a different grammar survives: each alternative is a guess at what git does, and git
  has answered.

### 5. A bare `**`

Section 8.1 makes `**` special as "a leading `**/`", "a trailing `/**`" or "`/**/`", and "anywhere
else it is `*`". An entry that is just `**` has none of those three shapes, so the text makes it `*`:
it admits `main` but not `release/1.2`. Git admits every name. The fixture's own
`pattern_never_admits_policy_branch` describes `**` as "a `**` that matches every name", which
contradicts the text it tests. The vector's answer is right regardless, because the policy branch is
excluded whatever the bound lists.

This gap is not in the issue. It was found while checking the issue's claims. The fix states git's
rule rather than its examples: `**` is special where it is a whole segment, meaning the name's start
or a `/` on its left and the name's end or a `/` on its right. The three forms 0183 listed are
instances of that rule. A bare `**` is the fourth.

Here the current text is narrower than git, so the failure was the visible kind. It is still fixed:
the fixture states git's answer, and two readings of one sentence are two implementations.

### 6. An empty bound

Section 9.7 defaults `vcs.base_branch_allowed` to "unset — a per-issue target is otherwise
unbounded", and Section 8.1 calls the engine's key OPTIONAL. Neither says what `[]` means. In
`symphony-rs` the two judges disagree. `crates/symphony-orchestrator/src/target.rs` reads `[]` as
admitting nothing (`an_unconfigured_bound_does_not_refuse_and_an_empty_one_does`).
`crates/vcsx-cli/src/consumer.rs` reads the key into a plain list that defaults to empty, so unset
and `[]` arrive the same, and `crates/vcsx-engine/src/supplied.rs` then reads an empty list as no
bound. For one configured `[]`, Symphony refuses every per-issue target and the engine admits every
base.

- **`[]` means unset** (steelman). A templated configuration that always emits the key, empty by
  default, keeps working unbounded. It is also what the engine does today.
- **It loses on the cliff it builds.** Under that reading, removing entries from an allow-list
  narrows it until the last one goes, and then the bound becomes everything. An operator narrowing
  `["release/1.2"]` by deleting the one entry they no longer trust gets every branch. An allow-list
  must narrow monotonically as entries are removed.
- **`[]` is a configuration error** (steelman). Symphony would refuse at startup, as 0183 made it
  refuse a negated entry, and the operator finds out before the first issue.
- **It loses** because `[]` is not a mistake. 0183's startup refusal exists because a negation means
  something the bound cannot apply. `[]` means something the bound applies exactly: no per-issue
  target is permitted. Section 9.7 already reports each refused issue as refused, which is accurate
  here. The engine also has no startup to fail at, so it has to give `[]` a meaning anyway.
- **`[]` admits no base, under both keys; unset stays unbounded (chosen).** Section 9.7's prose
  already says "Where `vcs.base_branch_allowed` is configured", and `[]` is configured. For
  `symphony-rs` the consequence is that `consumer.rs` must keep unset and empty apart.

## The fixture's measurement method

The fixture note says `git for-each-ref refs/heads/<entry>` "matches the full ref name with the
gitignore glob rules". It does not. `match_name_as_path` in `ref-filter.c` tries a literal
leading-component prefix match before wildmatch, for every pattern. So `refs/heads/release` lists
`release/1.2`, and an empty entry lists every ref. For an entry holding `*`, `?`, `[` or `\` the prefix
half cannot fire, because `git-check-ref-format(1)` forbids those characters in a ref name. So it
only distorts plain entries.

The issue says re-running the method "gets a different result" for the plain-entry vectors. No
current vector does. Every plain-entry vector pairs its entry with a base that is not below it, as
`slash_free_entry_does_not_match_at_any_level` pairs `main` with `release/main`. Replayed on 2.56.1
through `for-each-ref` over a single branch, all 26 checkable vectors agree. The method is exact for
today's corpus only by luck, though, and the first vector pairing `release` with `release/1.2` would
break it. The note moves to `test-tool wildmatch wildmatch`, which agreed with all 26 as well, and
the plain-entry case gets a vector of its own.

## Decision and reasoning

The glob is git's wildmatch with `WM_PATHNAME`, stated in Section 8.1's own words, with one
deliberate difference:

- matching is over bytes;
- `[...]` admits git's twelve POSIX classes with ASCII meanings;
- a `]` first in a set is a member;
- a `-` first, last, or after a range or a class is literal;
- `\` escapes inside a set;
- `**` is special wherever it is a whole segment, so a bare `**` matches every name.

The one difference: a reversed range is not well formed, where git degrades it to its first
endpoint. So are an unknown class name, `[]` and `[!]`, which git also treats as matching nothing.
A configured empty `base_branch_allowed` admits no base, for the engine's key and Symphony's alike,
and unset stays unbounded.

The rule behind every answer is the one in Context. Where the bound and an operator's git check
differ, the bound is the narrower, so the difference shows up as a refusal and never as an admission.

## Reconsideration triggers

- **Git changes wildmatch.** In particular, it starts decoding UTF-8 or makes a reversed range an
  error. Re-run the measurement table above with both tools. Bytes and the reversed-range rule are
  the two answers that depend on git staying as it is.
- **An operator reports that a non-ASCII bracket member never matched.** That is the cost recorded
  under gap 1 arriving. It is the signal to reconsider making a non-ASCII byte in `[...]` not well
  formed, which turns a silent never-match into a startup refusal.
- **A consumer emits `base_branch_allowed = []` meaning "no bound".** For example, a configuration
  template. The answer is to omit the key, but a second such report is evidence that the empty
  reading is a trap and should become a Symphony startup error after all.
- **A VCS backend whose branch names are not byte strings, or not git's.** "Matches what git
  matches" stops being a check an operator can run, and gap 1's direction argument has to be redone
  against that backend's own tool.
