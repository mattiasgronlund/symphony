# Background — 0047 Workspace-key sanitization operates on UTF-8 bytes

## Context

Decision 0046 surfaced, while authoring the conformance corpus, that the workspace-key sanitization
rule is under-specified for non-ASCII input. Section 9.5 Invariant 3 and Section 4.2 Workspace Key
say to replace "any character not in `[A-Za-z0-9._-]`" with `_`, but do not fix what a "character"
is. The allowed set is entirely ASCII, so every allowed character is one byte, one code point, and
one grapheme alike; the ambiguity bites only on non-ASCII input, where the three readings diverge —
and a precomposed versus decomposed accented letter would sanitize differently under some of them.
Because languages iterate strings differently by default (UTF-16 code units in Java/JS/C#, code
points in Go/Rust/Python, bytes when treated as raw), a non-ASCII vector could not be authored
without first pinning the unit, and the corpus deliberately left one out.

## Options considered

- **Option A — UTF-8 byte (chosen).** Replace every byte of the identifier's UTF-8 encoding not in
  `[A-Za-z0-9._-]` with `_`. A non-ASCII code point yields one `_` per byte. Trade-offs: the only
  definition that is trivially identical in every language (UTF-8-encode, then scan bytes) with zero
  iteration ambiguity — no UTF-16 surrogate handling, no Unicode library — and it always yields
  pure-ASCII output, satisfying the invariant. A non-ASCII code point expands to several underscores,
  and the rule stays normalization-sensitive (NFC and NFD encode to different bytes).
- **Option B — Unicode code point (scalar value).** One `_` per disallowed code point. Trade-offs:
  matches the intuitive reading of "character", but true code-point iteration needs `codePointAt`
  care in UTF-16 languages to avoid splitting non-BMP code points into surrogate halves, and it
  remains normalization-sensitive. More ways to get it subtly wrong across languages.
- **Option C — grapheme cluster.** One `_` per user-perceived character. Trade-offs: the most
  visually intuitive and the only reading that is normalization-insensitive, but it requires a
  UAX-29 segmentation library in every language and the segmentation algorithm changes across Unicode
  versions — so two conforming implementations on different Unicode versions could disagree. That
  directly violates the cross-version determinism the corpus exists to provide.

## Decision and reasoning

Choose **Option A**. The invariant's purpose (Section 9.5, "the most important portability
constraint") is a *safe, containment-respecting directory name*, not a reversible or human-pretty
one, and the corpus's purpose is behavior identical in every implementation language. UTF-8 byte-wise
is the only reading that serves both without a Unicode dependency: encode to UTF-8, replace each byte
outside the ASCII allowed set, done — the same few lines in Go, Rust, Python, JS, and Java, with no
surrogate or segmentation subtlety and a guaranteed pure-ASCII result.

The two costs are accepted deliberately. Multi-underscore expansion of a non-ASCII code point is
harmless for a directory name. Normalization-sensitivity (the same abstract identifier in NFC vs NFD
sanitizing to different keys) is tolerable because sanitization is already lossy and non-reversible
(Section 4.2 makes no round-trip claim), tracker identifiers are ASCII in practice, and the only way
to remove the sensitivity — normalize before sanitizing — would reintroduce exactly the
Unicode-table dependency this choice avoids. The rule therefore does **not** normalize first.

We would reconsider if a real tracker began issuing non-ASCII identifiers at scale where
collision or readability of the key mattered (then normalization, or a code-point rule, might earn
its dependency), or if the workspace key ever had to round-trip back to an identifier (it does not
today).

The decision is **Accepted** and applied to `SPEC.md` (Sections 4.2, 9.5) and the corpus.
Depends on 0046; relates to 0002.
