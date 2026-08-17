# Plan — 0110 A field that moved is not a field that is empty

## Scope

`VCSX-SPEC.md`: Section 9 preamble (the answer-domain rule extended to the derivation), Section 9.2
"Forge Backend Plugin" (the parse obligation stated over the capability list), Sections 13.1, 13.2.

`VCSX-CONTRACT.md`: no change; the plugin API is deferred by its Section 11.

`conformance/vcsx/`: the check's shape is decision 0111's; no vocabulary token is added.

## Steps

1. **Section 9 preamble — the rule reaches the derivation.** Ensure the preamble states that the
   obligation holds over how a capability *derives* its answer and not only over what it answers,
   and names the mechanism: a response field read as its type's default yields a well-formed value
   nobody established, satisfying the letter of the rule while producing exactly the failure it
   exists to prevent. Done-condition: a reader can tell that a deserializer default is a violation,
   without inferring it.

2. **Section 9.2 — the parse obligation.** Ensure the section states that where a forge response
   does not carry the shape a capability depends on, the capability MUST answer that it could not
   determine the value, and MUST NOT answer a default, an empty value, or the value's absent case.
   Ensure it covers a value whose content the backend cannot interpret — an unrecognized
   pull-request state — as the same condition one level in. Done-condition: `pr_state` under a
   renamed number field answers undetermined, and a reader can trace that to a stated requirement
   rather than to Section 9's general rule.

3. **Section 9.2 — the boundary.** Ensure the text states that a field the capability does not read
   is not drift: a forge adding a key, reordering an object, or returning a member the backend
   ignores MUST NOT be treated as an undeterminable response. Done-condition: a reader can tell the
   clause does not require refusing every unrecognized payload.

4. **Section 9.2 — the consequence is already stated.** Ensure the new text points at the
   consequences `pr_state`'s entry already documents — `create_or_update_pr` creating a second pull
   request, `push` no longer refusing over a CLOSED/MERGED one, `status` reporting no pull request
   rather than `pr_state_unavailable` — rather than restating them. Done-condition: no consequence
   is written twice in Section 9.2.

5. **Section 13.1 — the conformance point.** Ensure a check exists that a response missing a
   depended-on field yields an undetermined answer and the refusing result, distinguishable from
   the response that legitimately carries no pull request. Done-condition: the check is phrased over
   an injected response rather than over a backend's source.

6. **Section 13.2.** Ensure the checklist names forge-response parsing among the things bound to the
   answer domain. Done-condition: the checklist's plugin bullet accounts for the derivation as well
   as the answer.

## Cross-cutting sync

No configuration key, reason token or `need` changes.

## Anchor changes

None. This decision adds requirements to existing anchors and introduces no token.

## Status

Applied to `VCSX-SPEC.md` (Sections 9, 9.2, 13.1, 13.2).
