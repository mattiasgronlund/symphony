# Plan — 0111 The corpus states the assertion; the harness holds the fixture

## Scope

`conformance/vcsx/README.md`: a section fixing the fault-injection vector schema, its assertion set,
the harness obligation, and why no vector data is authored here.

`VCSX-SPEC.md`: Section 13.1's preamble, which describes what the published corpus covers.

No `vectors/*.json` file is added. That is the decision.

## Steps

1. **`conformance/vcsx/README.md` — the kind.** Ensure the schema section states that a
   fault-injection file is a second kind of vector file, distinguished from the pure-function kind
   every existing file uses, and that a runner unable to execute one MUST report it as not run
   rather than as passed. Done-condition: "the corpus is green" cannot mean two things depending on
   which files a runner supports.

2. **`conformance/vcsx/README.md` — the injected conditions.** Ensure the enumerated set is fixed —
   a rate-limited refusal, a server error, an expired network bound, a transport failure, a
   satisfied conditional read, and a response missing a depended-on field — each naming the
   `VCSX-SPEC.md` section it is read from. Done-condition: an implementation can enumerate the cases
   it owes without reading this decision.

3. **`conformance/vcsx/README.md` — the assertion set.** Ensure a vector is required to assert the
   reason, its proto class, the need and its `retryable` value, the `outputs` keys that must be
   present, and — for a drift case — that the answer is undetermined and distinguishable from the
   legitimate absent case. Done-condition: each of the five is named as REQUIRED rather than
   suggested.

4. **`conformance/vcsx/README.md` — the effect assertion.** Ensure a vector is required to assert
   that the operation **did not act** where the condition prevented it: no second pull request, no
   push over a closed one, no merge on an unread head. Ensure the text says why it is called out
   separately — the other assertions are readable off an envelope, and an engine reporting the right
   reason while having acted anyway would satisfy them. Done-condition: the assertion set covers the
   forge's state and not only the result.

5. **`conformance/vcsx/README.md` — the harness boundary.** Ensure the text states that the fixture
   — the bytes a forge returns, which header carries a reset, what a drifted payload looks like — is
   the implementation's and differs per plugin, so the cases are authored where the harness lives.
   Done-condition: a reader can tell why the data is absent here without reading the decision folder.

6. **`conformance/vcsx/README.md` — "Surfaced findings".** Ensure the finding is recorded: the
   corpus was green across every existing vector while the transient family had no coverage at all,
   which is what makes a green corpus weak evidence about the conditions these vectors name.
   Done-condition: the finding reads without reference to this decision folder.

7. **`VCSX-SPEC.md` Section 13.1 preamble.** Ensure the sentence describing the published corpus
   accounts for a second kind of file whose execution needs a harness, so the "deterministic,
   host-independent subset" claim stays true of the first kind and is not silently widened.
   Done-condition: the preamble does not claim host-independence for a vector that needs a forge
   twin.

## Cross-cutting sync

No vocabulary token, configuration key or reason changes.

## Anchor changes

None.

## Status

Applied to `conformance/vcsx/README.md` and `VCSX-SPEC.md` (Section 13.1).
