# Background — 0090 `entry` is a described field, null exactly where no entry point was read

## Context

Resolves issue #46. Decision 0084 closed the last condition that had no home: an invocation whose
arguments the engine cannot decode is refused with `arguments_unreadable`, `usage_or_config` and exit
`2` — and an envelope on stdout, because Section 8.3 now requires that "on every path that produces a
result, stdout carries exactly one JSON object and nothing else", so a caller parses one shape rather
than branching on whether anything was written.

Composing that envelope needs a field the case may not have. Section 8.2 opens "Every invocation
returns one structured result", its example carries an `entry`, and there is no entry to name for:

```
$ vcsx
$ vcsx --repo /srv/work
$ vcsx frobnicate
```

No first word, or a first word that is not one of Section 8.1's ten.

## What the defect does, and the sharper half underneath it

`entry` is Section 8.2 surface a caller branches on before deciding anything else, and Section 8.5
makes the envelope's fields major-stable. Three engines will answer three ways — a JSON `null`, a
sentinel token like `"unknown"`, the literal first word the caller typed — and each is a different
shape. A consumer reading `entry` as a Section 8.1 token gets a type error, a token no registry
contains, or a string that is whatever a user mistyped.

The sharper half is why the gap exists at all. **`entry` is not merely un-nulled — it is undescribed.**
Section 8.2's normative bullets cover `status`, `op`/`reason`/`class`, `escalation` and `outputs`, and
close with "A consumer MAY add fields but SHOULD NOT break the fields above within a major version."
`vcsx_version`, `entry` and `message` appear in the example JSON and in nothing normative at all. So
their type, their nullability and their meaning are inferred from one sample. Nobody wrote that `entry`
is non-null because nobody wrote `entry`; describing the three fields is worth doing on its own, and
once they are described, `entry` being null exactly where no entry point was read is a sentence in a
place that exists to hold it.

The two command lines also differ in a way worth keeping: `vcsx ship --frobnicate` is decodable enough
to name an entry point and fails after it, while `vcsx frobnicate` is not. Only the second has no
answer.

## Options

**A — Describe the three fields, and make `entry` nullable with one named case (chosen).** `entry`
names the Section 8.1 entry point the invocation ran, and is null **exactly where no Section 8.1 entry
point was read** — `usage_or_config` carrying `arguments_unreadable`, and nowhere else. The
"exactly where" is load-bearing rather than stylistic: without it an engine may null the field wherever
it finds it inconvenient, including where the command line parsed and the entry is known. It is the
same shape as the escalation rule Section 8.2 already states — "present exactly when `status ==
needs_caller`" — and it is enforceable for the same reason, because both halves are fixed. A consumer's
mapping over `entry` becomes total: a Section 8.1 token, or null.

`message` is described as free-form prose that nothing parses. That is stated now rather than later
because it is the only field in the envelope with no schema, so it is where structure gets put when
something has nowhere else to go — the filing implementation reports being tempted to put a `fail`
reason there, and decision 0089 gives that token an `outputs` key precisely to keep it out. A field
nothing parses only stays that way if the document says so.

**B — Only a decodable invocation owes an envelope (rejected).** An engine owes an envelope exactly
when a Section 8.1 entry point was read, and stderr plus exit `2` otherwise. This is what the filing
implementation does, and it was the right call *as a meanwhile*: its discipline is not to mint Section
8.2 surface locally, which is what this repository's own decision log refused to do for a Section 4.3
token on the reasoning that a value every engine would have to invent independently belongs upstream.

As a normative answer it hands back exactly what 0084 bought. 0084 extended the envelope to
`usage_or_config` so a caller parses one shape instead of branching on whether anything was written,
and B reintroduces that branch at the one exit code where a caller has least idea what happened: a
caller on exit `2` would have to test stdout for emptiness before it could parse, for the condition
whose whole content is "your invocation was unreadable". Section 8.3's "every path that produces a
result" would then hold only by making this path produce none, which is true by construction rather
than by design.

**C — A reserved `entry` token (rejected).** Add `unknown` to the entry-point vocabulary, keeping the
field non-null and typed — attractive for a typed in-process encoding where `entry` is an enumeration
rather than a nullable string.

It loses for a reason that only shows up in an implementation. An engine generating its entry-point
type from `conformance/vcsx/vocabulary.json` gets `unknown` as a variant, and Section 8.6's identity
precondition is a total function of the entry point — whether an entry requires a commit identity. Every
exhaustive match over the ten must then answer for a variant where the question does not apply, forever
and in every such function. "The question does not apply" is what an option type says and what a
sentinel cannot. C also makes "the entry points" ambiguous in every section that quantifies over
Section 8.1's ten. A nullable field costs one option at one call site; a sentinel costs a nonsense arm
in every total function over the type.

The reading that a null is itself a forbidden absent-case spelling — Section 9's rule that a
value-answering capability's non-answer "MUST NOT be spelled as the value's absent or negative case" —
does not reach this. That rule requires a non-answer to "map to a reason a caller can read", and here it
does: the null travels with `reason: "arguments_unreadable"`, so the condition is carried by the reason
token and the null is the field agreeing with it, not the report itself.

## Verification

- The claim that `vcsx_version`, `entry` and `message` are undescribed was checked against
  `VCSX-SPEC.md` Section 8.2 at `e00ebb1`: the section's five bullets cover `status`,
  `op`/`reason`/`class`, `escalation`, `outputs`, and consumer-added fields. The three names appear in
  the example block and nowhere else in the section.
- `conformance/vcsx/vocabulary.json` at `e00ebb1` carries `envelope_fields` as a flat list of nine
  names with no type or nullability, and `entry_points` as ten tokens with a `kind` each — so the
  generated-type argument against option C is checkable against the artifact an engine generates from.
- The claim that Section 8.6 makes the identity precondition a function of the entry point was checked
  against Section 8.6 at `e00ebb1`: "For an entry that can write a commit — `commit`, `integrate`,
  `pull`, and a front-end sequence that dispatches one — an identity is REQUIRED", and "The entry point
  alone fixes that scope".
- Section 8.3 needs no change: the code for this condition is `2`, as it already is, and the reserved
  `1` continues to mean an invocation that produced no result at all.

## Reconsideration trigger

Reopen if a second condition is found where an envelope is owed and no entry point was read. The
"exactly where" clause names one case by name, so a second one makes the clause a list, and a list of
two is the point at which the property should be stated over what the cases have in common instead.

Reopen if the invocation contract gains an encoding in which a null is not expressible — a positional
or fixed-width encoding, say. The nullable-versus-sentinel argument is settled here on the shape of a
generated type, and an encoding that cannot carry a null would move it.

## Relates to

0084 (whose envelope this completes, and whose property option B would give back), 0065 (the
precondition registry `arguments_unreadable` belongs to), 0089 (which keeps `message` unparsed by
giving the `fail` token an `outputs` key of its own), 0071 and 0051 (the vocabulary the nullability is
recorded in).
