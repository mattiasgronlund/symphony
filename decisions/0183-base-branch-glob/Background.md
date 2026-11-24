# Background — 0183 An allow-list of patterns with no pattern syntax

## Context

Reported as issue #182 from `symphony-rs`, against `b04797e`. `SPEC.md` Section 9.7 (Repository
Provisioning and the VCS Engine) gives `vcs.base_branch_allowed` as an OPTIONAL bound on the targets
a per-issue source may name, "as branch names or patterns", and `VCSX-SPEC.md` Section 8.1 (Entry
Points and Arguments) gives the engine's `base_branch_allowed` "as names or patterns". Neither
document, nor `VCSX-CONTRACT.md`, says what a pattern is. The only other pattern in the corpus,
`scope.branch_pattern`, is a name template, not a matcher.

The failure path is the dangerous direction for an allow-list. Take an operator who writes
`release/*` and an issue whose tracker field names `release/1.2/hotfix` as its target. An
implementation reading the entry as a shell glob without `FNM_PATHNAME` admits the target. One
reading it as a path glob refuses it. One reading it as an unanchored regular expression admits
`release-notes` too. The admitted run then back-merges from, and opens its pull request against, a
branch the operator did not think they had allowed. Nothing downstream catches it, because the
bound *is* the check: Section 9.7 refuses before the run starts, and the engine refuses with
`base_branch_not_permitted` before the policy runs (`VCSX-SPEC.md` Section 8.6).

Two parties judge the same bound. Symphony judges it when it dispatches an issue, and the engine
judges it on every invocation that supplies a base. So the gap is not only between two
implementations: one deployment can disagree with itself. Symphony admits a target, the engine
refuses it, and the issue fails after dispatch instead of being refused before it.

`symphony-rs` matches exact names only in the meantime. That fails closed: a pattern entry admits
only its literal spelling, which for git is never a legal branch name (below).

## The choice: gitignore-style globs

Mattias chose the syntax: gitignore-style globs. The issue had proposed glob with "git's and the
forges' semantics" and listed the rules it meant. Both answers say glob. They part on `**`, and on
what "gitignore" brings along beyond the glob itself.

### What gitignore's pattern syntax is, checked

From `gitignore(5)`, git 2.47.3, PATTERN FORMAT:

- "An asterisk "*" matches anything except a slash. The character "?" matches any one character
  except "/". The range notation, e.g. [a-zA-Z], can be used to match one of the characters in a
  range. See fnmatch(3) and the FNM_PATHNAME flag".
- `**` is special in three places only: "A leading "**" followed by a slash means match in all
  directories", "A trailing "/**" matches everything inside", and "A slash followed by two
  consecutive asterisks then a slash matches zero or more directories". Then: "Other consecutive
  asterisks are considered regular asterisks".

The issue's proposal said "`**` matches across segments" without restriction. Gitignore's rule is
narrower: `release**` is `release*` and does not cross `/`. The narrower rule is the one adopted. It
is also the safer one, because a `**` written inside a segment by mistake cannot quietly widen the
bound to every depth.

### What gitignore's *line* semantics are, and why they are not adopted

A gitignore file is not just globs. Each line also carries path semantics that make sense for a
directory tree. Read into an allow-list, each of them either widens it or means nothing:

- **Slash-free lines match at any level.** `gitignore(5)`: "If there is a separator at the
  beginning or middle (or both) of the pattern, then the pattern is relative to the directory level
  of the particular .gitignore file itself. Otherwise the pattern may also match at any level below
  the .gitignore level." Read as a gitignore line, `main` would admit `release/main` and
  `team/x/main`. Every exact-name bound written today would widen silently. This is the deciding
  reason the entry is a gitignore *pattern's glob*, matched against the whole name, and not a
  gitignore *line*.
- **Directory containment.** A gitignore line that matches a directory also excludes everything
  inside it. Measured below: `git check-ignore` reports `release/*` matching `release/1.2/hotfix`
  for that reason, not because of the glob. Branch names have no directories.
- **Negation.** "An optional prefix "!" which negates the pattern; any matching file excluded by a
  previous pattern will become included again." In an allow-list a negation would have to mean
  exclusion, with last-match-wins ordering. Read as a literal entry instead, it does nothing, and
  the operator's `release/**` plus `!release/secret` admits `release/secret`. That is the specific
  widening a gitignore-literate operator would write and not notice, so an entry beginning with an
  unescaped `!` is refused rather than read either way (below).
- **Trailing `/` (directory only), leading `/` (anchor), `#` (comment).** None needs a rule. Every
  entry is already anchored to the whole name, so a leading `/` adds nothing. A git branch name
  cannot begin or end with `/` (`git-check-ref-format(1)` rule 6), so an entry with either matches
  nothing, which fails closed. A `#` is a literal character, and a `#`-prefixed entry admits only a
  branch spelled with one, which is narrower than whatever its author meant.

### The issue's second question answers itself for git

The issue asks whether an entry with no metacharacter should be defined as an exact name, so that
existing configurations keep their meaning. Under whole-name matching it *is* one: a glob with no
metacharacter matches exactly its own spelling. No extra rule is needed, and Section 8.1 states it
only as a consequence.

For git, the question has no edge either. `git-check-ref-format(1)` rule 5: refs "cannot have
question-mark ?, asterisk *, or open bracket [ anywhere", and rule 10: they "cannot contain a \".
So no legal git branch name contains a glob metacharacter. Every entry that names a real git
branch today means the same thing tomorrow. The `\` escape matters only for a backend whose names
admit those characters, and it is defined because the match is the engine's, not git's.

## Options considered

- **Regular expressions.** Steelman: the most expressive, the only option that can say "digits
  only" or "one of these three prefixes" in one entry, and supported by every implementation
  language without a hand-written matcher. Loses because the usual mistakes widen the bound.
  Unanchored `main` matches `not-main`, and an unescaped `.` matches any character. The cases it
  adds are covered by listing exact names, which the bound already allows. The issue argued this and
  the argument holds.
- **fnmatch with `FNM_PATHNAME`, no `**`.** Steelman: one well-known definition every platform
  ships. A deployment that wants every depth lists one entry per depth. Loses because "every
  release branch at any depth" is a real bound operators already write as `release/**`, in git
  refspecs and forge branch rules. Without `**` they would get a bound that refuses what they meant
  to allow, and they would widen it by hand, most likely to `*`-something broader.
- **The issue's proposal: `**` matching across segments anywhere.** Close to the choice, but
  without gitignore's restriction to whole segments, so `release**` would cross `/`. Loses to the
  restriction for the reason above: a mistake should not widen the bound.
- **Gitignore lines wholesale.** Steelman: operators could paste lines they already have. Loses on
  slash-free any-level matching, which silently widens every existing exact name, and on negation,
  whose last-match-wins ordering is one more way to admit a branch by accident.
- **A gitignore pattern's glob, matched against the whole name (chosen).**

## The refused entry: why the whole bound, and why at two points

Two kinds of entry cannot be read as the operator meant: one beginning with an unescaped `!`, and
one that is not well formed (an unclosed `[`, a trailing unescaped `\`). Git's own wildmatch treats
an unclosed bracket as matching nothing. Per entry, that already fails closed. The negation's harm
is different, though: it lives in the *other* entry, the `release/**` the negation was meant to
narrow. Only refusing the bound as a whole stops that. One rule covering both kinds keeps the two
readings from drifting apart: a bound holding such an entry admits no base.

- **The engine** reports it as `base_branch_not_permitted` on every invocation that supplies a base.
  No new precondition reason is added: what is refused is the supplied base, and the existing token
  already says so. The cost is that the token does not name the repair. Recorded as left open, with
  the trigger below.
- **Symphony** refuses the configuration at startup under the new dispatch-preflight reason
  `invalid_base_branch_pattern` (`SPEC.md` Section 6.3). Otherwise a deployment with a negated entry
  finds out only when the first issue names a target, and Section 9.7 then refuses that issue, logs
  it, and comments on it. That reports an operator's configuration mistake as though the issue were
  at fault.

The policy branch stays excluded whatever any pattern matches, `**` included. That rule is
unchanged and is now pinned by a vector.

## Measurements

Every well-formed, non-negated vector in `conformance/vcsx/vectors/base-branch-allowed.json` was
checked against git's own wildmatch, git 2.47.3. The method: a throwaway repository holding one
branch `refs/heads/<base>`, then `git for-each-ref refs/heads/<entry>`. `for-each-ref` matches the
full ref name with the gitignore glob rules (wildmatch with `WM_PATHNAME`). All 25 agreed with the
`expect` written from the text. One harness slip was found and fixed: shell `read` without `-r`
stripped the `\` from `a\?b`, so git first saw `a?b`. Re-run literally, `a\?b` does not match `axb`,
and `\!important` matches `!important`.

Two tools were tried first and rejected, and are recorded so that nobody re-runs them:

- `git check-ignore --no-index` reported `release/*` matching `release/1.2/hotfix`. That is
  gitignore's directory containment: `release/1.2` matches as a directory and its contents follow.
- `git ls-files ':(glob)<entry>'` reported `release**` matching `release/1`, and an unclosed
  `release/[ab` matching the literal path `release/[ab`. Pathspecs match leading directories and
  fall back to a literal comparison, and neither behaviour is the glob's.

## Decision and reasoning

Each `base_branch_allowed` entry, the engine's and `vcs.base_branch_allowed` alike, is a glob in the
syntax of a gitignore pattern, matched against the whole branch name:

- `*`, `?` and `[...]` do not match `/`;
- `**` is special only as a whole segment;
- `\` escapes the next character;
- braces are literal, and matching is case-sensitive.

An entry beginning with an unescaped `!`, or one that is not well formed, makes the bound admit no
base. Symphony refuses it at startup. The syntax is defined once, in `VCSX-SPEC.md` Section 8.1, and
`SPEC.md` Section 9.7 points to it, so the two parties that judge the bound cannot apply two
syntaxes.

What this means for `symphony-rs`: exact entries keep their meaning, since an exact-name matcher is
the metacharacter-free case of this one. Pattern entries move from admitting their literal spelling
(never a legal git name) to admitting what they say, so the re-pin widens only to what the operator
wrote. An entry beginning with `!`, which an exact matcher accepted as a literal, becomes a startup
refusal.

## Reconsideration triggers

- **A deployment needs an exclusion.** The answer is a separate deny key judged after the allow
  list, not negation with ordering. It would be a new decision, and this one's refusal of `!` is
  what keeps that key from colliding with an existing meaning.
- **A second consumer of the engine with no startup validation of its own.** That consumer would
  see a negated bound only as `base_branch_not_permitted` on every invocation, with no repair named.
  That is the signal to give the engine a precondition reason of its own for a bound it cannot read.
- **A VCS backend whose branch names routinely contain `*`, `?`, `[` or `\`.** Every literal entry
  would then need escaping, which is a burden the git-only measurement above does not see.
