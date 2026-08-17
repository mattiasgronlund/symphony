# Background — 0110 A field that moved is not a field that is empty

## Context

Issue #59's first half: parsing a forge response whose depended-on shape is absent MUST yield
undetermined, "never proceed on a defaulted/empty field", and forge-response parsing should become a
named conformance point under the existing answer-domain decision. The observed failure is recorded
as GitHub JSON schema drift, where a renamed field read as empty and was "indistinguishable from a
real absence".

## The rule exists; the mechanism that breaks it is not an answer

Section 9 already carries the requirement, and it is emphatic: a value-answering capability MUST be
able to answer that it could not determine a value, and that answer MUST NOT be spelled as the
value's absent or negative case. `pr_state`'s own entry spells out the stakes — an absent pull
request lets `push` proceed and `create_or_update_pr` create, while an undetermined one refuses
both. Section 4.1 says it in one line: a read reports no determinate value it did not establish.

So this decision does not introduce an obligation. It states where the obligation is broken, and the
gap is worth naming precisely: **the rule is written over what a capability answers, and the defect
lives in how the answer is derived.**

A backend does not decide to report a missing field as an empty one. A deserializer does it, by
default, as a library behavior — a field absent from the payload takes the type's zero value, and
the code that would have raised the question is never written. The capability then answers a
perfectly well-formed value, and every clause above is satisfied to the letter by a value nobody
established.

That is why a clause naming the parse step is worth its space even though it adds no new
requirement. It is a redundancy placed where the failure actually occurs, and the record should say
so rather than present it as a discovery.

## The failure path, end to end

Take a forge that renames the field carrying a pull request's number, or moves it under a new
object.

1. The backend's deserializer reads the absent field and yields its default.
2. `pr_state` answers **none** — the determinate fact that the work branch has no pull request —
   because that is what an empty result looks like after a lookup.
3. `create_or_update_pr` is required to maintain one pull request per work branch, and maintaining
   one requires finding the one that exists (Section 9.2). Told there is none, it **creates a
   second**.
4. `push` no longer refuses over a CLOSED or MERGED pull request, because the state it would have
   refused on is not there.
5. `status` reports no pull request rather than `pr_state_unavailable`, so the one surface that
   exists to say "the read established nothing" says the opposite.

Each of those is a consequence Section 9.2 already documents for an undetermined answer misspelled
as an absent one. The drift is simply the most likely way to produce that misspelling, and the one
least visible in review: nothing in the backend's source says "assume there is no pull request".

## What the clause covers, and what it does not

It covers the shape the backend **depends on**. A response that does not carry it is a response the
backend cannot answer from, whatever the transport said about the request's success.

It does not cover a field the backend does not read. A forge adding a key, reordering an object, or
returning a member the backend ignores is not drift and MUST NOT be treated as it — a backend that
refused every unrecognized response would break on the next upstream release for no reason. This is
worth stating because the conservative reading of "the shape changed" is unusable in practice: forge
payloads gain fields continuously.

It also covers a value present in the right place whose **content** the backend cannot interpret —
a pull-request state carrying a token the backend does not know. That is the same condition one
level in: the field was found, and what it holds does not determine an answer. Reading an unknown
state as `closed` because the enum's fallback arm says so is the same defect with a different
default.

## Where it lands, and why it is a conformance point rather than only prose

Issue #59 asks for a named conformance point, and the reason is mechanical. A prose obligation on a
parse step is checkable only by reading a backend's source, which is what the Conformance Statement
exists to avoid. A check phrased over an injected response — remove the depended-on field, assert the
capability answers undetermined and the operation refuses — is checkable against a binary, and it is
the one form in which this obligation can be demonstrated rather than asserted.

That check is a fault-injection vector, which is the subject of the sibling decision: this one fixes
what MUST be true, and that one fixes the shape the corpus states it in.

## Reconsideration trigger

Reconsider if a backend is observed refusing on drift that did not matter — an ignored field
disappearing, or a payload restructured around parts the backend never read. That would mean the
"depended-on shape" boundary is being read as "the shape the forge documented", and the clause needs
to say which of the two it means in stronger terms than it does here.

## Relationship to the other decisions

It extends 0076's answer domain from the capability's answer to the derivation of that answer, and
it is the requirement 0111's vector shape exists to make checkable. 0108 is adjacent but separate: a
forge that did not answer is `forge_unavailable`, while a forge that answered something the backend
cannot read is an undetermined value — the transport succeeded and the content did not carry what
was needed.
