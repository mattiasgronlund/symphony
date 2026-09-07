# Plan — 0174 Four Core checks against a document the specification declines to pin

## Scope

`SPEC.md` Section 10 (Agent Runner Protocol (Coding Agent Integration)) intro, Section 17.5
(Coding-Agent Adapters), Section 18.1.2 (Broker Core Conformance) and Section 19 (Conformance
Statement); plus `CONFORMANCE-STATEMENT-TEMPLATE.md`.

Section 17.8 (Real Integration Profile (RECOMMENDED)) is unchanged — the four checks stay Core, so
its header does not need widening. Section 10's Protocol source of truth bullets keep their existing
deferral verbatim.

**Sections 10.1, 10.2 and 10.3 are deliberately unchanged.** They state the obligation — startup
MUST follow the targeted contract, the session is initialized using the targeted protocol, updates
are processed according to it — and that obligation is real and stays. What this decision changes is
only what a Section 17 *check* can assert, since a self-contained conformance run cannot discharge a
claim about a document the specification does not pin. The requirement and the check are separated
rather than the requirement weakened.

## Steps

1. **Section 10 states the documented target.** Ensure the Protocol source of truth bullets gain one
   saying that, because this specification pins no protocol version and no schema, the version an
   adapter targets is the implementation's choice and MUST be documented (Section 19): the protocol
   version, the transport framing, and whether a published schema exists for that version and which
   one composed payloads are validated against. Ensure it says Section 17.5's checks are stated
   against that documented target rather than against a version this specification names.
   Done when Section 10's intro carries the MUST-document obligation and cites Sections 17.5 and 19.

2. **The startup check is about this implementation.** Ensure Section 17.5's session-startup bullet
   asserts that the adapter documents the protocol version it targets and composes and sends the
   startup exchange that version requires before the first turn.
   Done when the `SPEC.md` Section 17.5 bullet no longer asserts that startup follows the targeted
   protocol.

3. **The identity/capability payload check is about this implementation.** Ensure the bullet asserts
   that those payloads are composed where the targeted version requires them and are validated
   against that version's published schema where one is published, with the implementation
   documenting which.
   Done when the `SPEC.md` Section 17.5 bullet no longer asserts the payloads are valid against the
   protocol.

4. **The framing check is about this implementation.** Ensure the bullet asserts that the transport
   framing the adapter targets is documented and that framed messages of that shape round-trip,
   including one split across reads and one arriving coalesced with the next.
   Done when the `SPEC.md` Section 17.5 bullet no longer asserts that the framing the protocol
   requires is handled correctly.

5. **The signal-interpretation check is about this implementation.** Ensure the bullet asserts that
   the approval, user-input-required, usage and rate-limit signals the adapter recognizes are
   documented and each is dispatched to its documented handling.
   Done when the `SPEC.md` Section 17.5 bullet no longer asserts the signals are interpreted
   according to the targeted protocol.

6. **The two extraction bullets are untouched.** Ensure the bullets asserting that thread and turn
   identities and that usage and rate-limit telemetry exposed by the targeted protocol are
   *extracted* keep their wording; they are claims about this implementation already.
   Done when both still read as they did.

7. **Section 19 records the obligation.** Ensure the Statement's enumeration of `Implementation-defined`
   and MUST-document resolutions includes the protocol version and transport framing each adapter
   targets and the published schema, if any, composed payloads are validated against (Section 10),
   distinct from the executor protocol floor already listed.
   Done when Section 19 names the targeted agent protocol version.

8. **The template carries the rows.** Ensure `CONFORMANCE-STATEMENT-TEMPLATE.md`'s Section 4.1 Core
   table has a row for the targeted protocol version and transport framing per adapter, and a row
   for the schema composed payloads are validated against or its absence.
   Done when both rows exist and cite Section 10.

9. **Section 18.1.2's agent-runner item names the target.** Ensure the neutral agent runner contract
   item states that each adapter's targeted protocol version, framing, and schema (or its absence)
   are documented.
   Done when the item names the documented target.

## Cross-cutting sync

- **Section 6.4** — unaffected. No configuration key changes.
- **Section 17** — steps 2–6. **Section 18** — step 9. **Section 19** — step 7.
- **Conformance Statement template** — step 8, which is the obligation decision 0128 exists to keep
  from being missed.
- **`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md`** — unaffected. The agent protocol is not the engine's.
- **Conformance corpus** — unaffected. No vector asserts protocol conformance, and none could.

## Anchor changes

None. No code-token identifier is renamed or removed and no section is retitled.

## Status

Not started.
