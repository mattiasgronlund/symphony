# Background — 0105 One lowercase, named once and cited everywhere

## Context

Section 4.2 fixes the rule in a single line — "Compare states after `lowercase`" — and issue #56
observes that the word is unqualified while the available readings disagree on real inputs. The
normalized value is not a display string. It is the key three comparisons test, so two readings of
that word do not render a state differently; they dispatch differently.

## What branches on the value

- **Dispatch eligibility.** Section 8.2 admits an issue only if its state is in `active_states` and
  not in `terminal_states`. Section 16.3 reconciles a *running* issue through the same two
  membership tests and terminates the worker when neither matches. A state that normalizes two ways
  is a worker one implementation keeps and another stops.
- **Per-state concurrency.** Section 8.3 resolves `max_concurrent_agents_by_state[state]` on the
  normalized key and falls back to the global limit on a miss. The miss is silent, because an
  unmatched key is indistinguishable from an absent override — the deployment runs at the global
  limit and nothing reports that the override it configured was never read. Section 17.1 makes this
  a `Core Conformance` check, which is where issue #56 starts.
- **Transition-graph validity.** Section 11.6 requires at most one transition per `(from, on)` pair
  and calls a duplicate a configuration error caught at dispatch preflight. `from` is a state name,
  so the reading decides whether two entries collide: under the full-Unicode reading `İn Review` and
  `i̇n review` are one `from` and the policy is refused, and under the ASCII-only reading they are
  two and it loads.

The third is the sharpest and is not in the report: the reading decides not how the daemon behaves
but whether a repository's `repo.policy.toml` loads at all. It also shows the rule reaching past the
two sites Section 4.2 could be read as covering, which is what made "define the operation once and
cite it" the shape of this decision rather than "qualify one word".

## The readings, measured

`İ` (U+0130) is the separator issue #56 names. Measured here, code points shown:

| Reading | `İnceleme` | `IN PROGRESS` | `ẞ` |
|---|---|---|---|
| ASCII-only (`A`–`Z` only) | `İnceleme` (U+0130 …) | `in progress` | `ẞ` (U+1E9E) |
| Unicode default, no tailoring | `i̇nceleme` (U+0069 U+0307 …) | `in progress` | `ß` (U+00DF) |
| Unicode, Turkish tailoring | `inceleme` (U+0069 …) | `ın progress` (U+0131) | `ß` |

Row 2 measured three ways and identical in all three: `rustc` 1.95.0 `str::to_lowercase`, CPython
3.13.5 `str.lower()` (`unicodedata.unidata_version` 15.1.0), Node v26.5.1 `String.toLowerCase()`.
All three also apply the language-independent Final_Sigma context rule (`ΟΔΟΣ` → `οδος`, ending
U+03C2), which is part of the full mapping and not a tailoring. Row 3 measured with Node
`toLocaleLowerCase("tr")`. Row 1 computed directly.

So the plain reading of the unqualified word is what a reference implementation in each of the three
languages produces by default, and it is the reading issue #56's reporter had already resolved to.
That is the reading this decision fixes.

## The corpus is green under the dangerous reading — but only on the host it ran on

Issue #56 reports the four `state-normalization.json` vectors as passing under every reading,
"including the locale-sensitive one on a host that happens not to be Turkish". The qualifier is the
whole finding, and it is worth stating in the sharper form: the `title-case-two-words` vector
(`In Progress` → `in progress`) **does** fail under the Turkish tailoring, because `I` lowercases
to U+0131 there. The corpus therefore does not fail to check the locale reading — it checks it
*conditionally on the environment of the machine that ran it*. A green corpus on a CI runner is not
evidence about the deployment host, and the failure it does not catch is the one that appears only
in production. That is a stronger reason to pin the rule in the prose than an unchecked vector would
have been.

## Options considered

**Option A — the Unicode Default Case Conversion `toLowercase`, full mappings, no language-specific
tailoring.** Chosen; reasoning below.

**Option B — ASCII-only lowercase: `A`–`Z` map to `a`–`z`, every other code point unchanged.** This
is the option with the repository's own precedent behind it. Decision 0047 settled the workspace-key
unit as the UTF-8 **byte** for exactly this family of reasons — "identical in every language with no
Unicode library" — and `vectors/workspace-key.json` carries precomposed and decomposed vectors that
deliberately differ. Option B extends that philosophy: no case tables, no Unicode version to track,
no library, and every implementation agrees by construction on every input that exists.

It loses on what the two rules are for. Sanitizing an identifier into a directory name is a
*projection*, and 0047 was free to pick any total function as long as every implementation picked
the same one; a byte-level rule is a fine projection. This rule is a *match*, between a state the
tracker owns and a string the operator typed into `symphony.toml`. Under Option B the promise
"compare states after lowercase" holds for `TODO` and silently does not hold for `İNCELEME`, so
case-insensitivity becomes a property of the alphabet the tracker happens to be configured in. The
deployments that lose are the non-English ones, which are also the ones least likely to read the
rule expecting the caveat. Option B is right where a rule projects and wrong where a rule matches,
and 0047 is not the precedent it looks like.

**Option C — full Unicode case folding (`toCasefold`), the operation Unicode actually specifies for
caseless matching.** The strongest technical case: Default Caseless Matching is defined in the same
section as Default Case Conversion, folding is what it is built from, and it matches strings
lowercasing does not — `Straße` and `STRASSE` fold together (measured: CPython 3.13.5
`"Straße".casefold()` → `strasse`, `"Straße".lower()` → `straße`). If the goal is "the operator's
spelling matches the tracker's", folding does the goal better.

It loses on availability, which is measurable and was measured. The appeal of `lowercase` is that
every implementation's standard library already has it and all of them agree; folding does not have
that property. Rust's standard library has no case fold at all — `rustc` 1.97.1 rejects
`"Straße".to_casefold()` with `E0599: no method named to_casefold found for reference &str`, and
suggests nothing, so the operation needs a crate. Go's `strings.EqualFold` documents itself as
"simple Unicode case-folding" and its own package example asserts `EqualFold("ß", "ss") == false`
"because comparison does not use full case-folding" (pkg.go.dev, verified). So an implementation
reaching for its language's obvious folding primitive gets *simple* folding, which disagrees with
full folding on the single character that motivates the option. Requiring folding would replace a
divergence the specification can close with a divergence in what "folding" means, and would put a
third-party dependency in the path of a `Core Conformance` check. Deferred, not dismissed: the
reconsideration trigger below names the evidence that would reopen it.

**Option D — require a Unicode normalization form (NFC) on both sides before lowercasing.** The
comparison crosses an artifact boundary: the tracker supplies one side and the operator's
`symphony.toml` the other, so `Ünder Review` composed (U+00DC) and decomposed (U+0055 U+0308) never
match even after Option A pins the case rule. Considered and not taken, on a distinction worth
recording: **this is not an interoperability defect.** Every implementation that lowercases the code
points as given produces the same answer, so no two conforming implementations disagree — the
surprise is the operator's, not the specification's. Option A closes a hole where the document is
silent between implementations; Option D would add a requirement (and a normalizer dependency: in
Rust and Go a third-party crate or module, stdlib only in Python and Java) to fix a different
problem, one issue #56 did not report. What the decision does instead is state that no normalization
form is applied, so the absence is a fixed, checkable property rather than another silence.

## The residual, stated plainly

The case mapping is versioned: two implementations built against different Unicode versions can
disagree on a code point whose mapping was assigned or changed between them. This decision does not
put a Unicode-version requirement in the prose, because for the input in question — tracker workflow
state names, which are words in living languages — the mappings have been stable for many versions,
and an `Implementation-defined` "MUST document its Unicode version" clause would impose a
Conformance Statement row for a divergence nobody can produce. Recorded here rather than in
`SPEC.md` so a later reader can see it was weighed rather than missed.

Two smaller notes. The spec text cites the Unicode section by **title and number together**, the
same shape decision 0002 requires of `Plan.md` steps addressing `SPEC.md` — the title is the stable
key and the number is the hint. (Verified: Section 3.13 "Default Case Algorithms" in The Unicode
Standard 16.0, whose conformance clause C20 binds Default Case Conversion to it.) And the rule is
stated over the *full* mappings explicitly, because the simple mappings are a real alternative
reading of "lowercase" that differs on `İ` in the same direction ASCII-only does.

## What the widening turned up

The user chose "define once, cite everywhere" over "states only, as filed", so the operation became
a named rule in Section 4.2 that the other sites cite. Applying that surfaced three things:

- **The document spelled the same operation three ways.** Section 4.1.1 said `labels` are
  "Normalized to lowercase", Section 11.3 said label names are "trimmed and lowercased", and Section
  5.3.1 said `required_labels` matching "ignores case and surrounding whitespace" — a phrasing that
  does not obviously name a normalization at all. Three phrasings, one operation, and only one of
  them even hinted where the rule lives.
- **The label path has the same failure with a worse blast radius.** `required_labels` gates
  dispatch entirely (Section 8.2), so a label that normalizes two ways is an issue one
  implementation dispatches and another never picks up; `agent_by_label` and
  `compute.variant_by_label` select the agent and the compute variant off the same key.
- **The Section 16 pseudocode compares raw states.** `reconcile_running_issues` tests
  `issue.state in terminal_states` with no normalization step, so the reference algorithm reads as
  if the rule did not apply to it. The membership tests now name the normalized value, which is a
  consistency repair the widening exposed rather than a new requirement.

## The vector that tested nothing, once

The decomposed vector — `Ünder Review` spelled U+0055 U+0308, pinning the no-normalization-form rule
— was authored with a literal character, following `workspace-key.json`, which carries a
precomposed/decomposed pair written the same way. It arrived on disk **composed**: the authoring
tool silently normalized U+0055 U+0308 to U+00DC. The vector still passed, because the expected
output was composed too, and a composed input lowercasing to a composed output is a case every
reading agrees on. It had become a tautology, and nothing about the file said so: the two spellings
are identical on screen, which is the whole reason the vector exists.

Caught by re-parsing the file and comparing code points rather than by reading it, which is the
transferable part. The corpus's non-ASCII values are now `\uXXXX` escapes, stated as a convention in
`conformance/README.md`, and `workspace-key.json`'s two non-ASCII vectors are converted to match —
that file was verified intact on disk first (its decomposed vector really is U+0065 U+0301), so the
change is a rewrite of the encoding and not of a value. A JSON escape cannot be normalized by an
editor, and a reviewer can see which form is intended without trusting the rendering.

The cost of the failure is worth naming precisely, because it is not "a test broke". A vector that
degrades into a tautology **passes**, on every implementation, forever, and the corpus reports
coverage of a rule nothing checks. That is the same shape as the finding above about the four
existing vectors being green under the locale-sensitive reading — an artifact whose green is not
evidence — met twice in one decision, once in the specification and once in the tooling.

## Decision and reasoning

**Section 4.2 gains a named rule, `Lowercase Normalization`, and every case-insensitive comparison
in the document cites it.** The rule fixes three things a reader could previously not determine: it
is the Unicode Default Case Conversion, it uses the full mappings rather than the simple ones, and
it applies no language-specific tailoring — with the last stated as a MUST NOT, because that reading
is the one that makes the host's environment an input to a conformance-checked comparison and is the
only one no amount of care in the deployment can defend against. It also states that no Unicode
normalization form is applied, so the second axis of the same comparison is fixed rather than
silent.

**`Normalized Issue State` names the sites that test it.** A reader who knows only that states are
compared after lowercasing cannot tell that the value is a comparison key and never a display
string, which is what makes the `set_state` write path (Section 11.1, where `to` is the provider's
own spelling) obviously different from the match path.

**The corpus gains three vectors and no new function.** `İnceleme` separates all three readings in
one input and does so regardless of the runner's locale; `ẞ` separates Unicode from ASCII-only and
additionally pins lowercase against folding, which is the option deferred above; and a decomposed
`Ünder Review` pins the no-normalization-form rule. No `normalize_label` function is added: it would
put a second entry point in every implementation's harness to re-check the same mapping, and
trimming — the only part that would be new — is not the defect under repair. Recorded so a later
slice adding label vectors knows the omission was deliberate.

**Reconsideration trigger.** Two, and they pull opposite ways. If a deployment reports a state or
label that renders identically in the tracker and in `symphony.toml` and never matches, that is
Option D arriving with evidence, and the normalization-form axis should be reopened as its own
decision rather than folded into this one. If instead the reports are of `ß`/`ss`-shaped near-misses
— spellings that differ by a case-folding equivalence rather than a normalization form — that is
Option C arriving, and the answer is folding with the dependency cost accepted, not a patch to the
lowercase rule.

Relates to 0047 (whose byte-level unit this decision deliberately does not extend), 0002 (citation
by stable identity), and 0046 (the corpus slice this extends).
