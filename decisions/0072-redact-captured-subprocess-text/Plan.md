# Plan — 0072 Captured subprocess text is redacted where it enters the process

## Scope

`SPEC.md`: the rule is stated once in Section 15.3 "Secret Handling", carried at the emit boundary in
Section 10.4 "Emitted Runtime Events (Upstream to Orchestrator)", and inherited by Section 13.1
"Logging Conventions" and Section 13.8.2 "JSON REST API (`/api/v1/*`)". Cross-cutting sync touches
Section 17.5 "Coding-Agent Adapters", Section 17.6 "Observability", Section 18.1.2 "Broker Core
Conformance", and Section 19 "Conformance Statement". `CONFORMANCE-STATEMENT-TEMPLATE.md` gains one
core row.

No new section and no renumbering: every edit is a bullet added to an existing list.

The obligation is `Core Conformance`, owned by `Broker Core Conformance` — the adapter and the executor
that runs it are Broker Core (Section 18.1.2), and Section 15.3 is core security. Section 13.8 stays an
OPTIONAL extension: its edit is a statement that the surface inherits a core guarantee, not a new
requirement on the extension, so a deployment shipping no HTTP server is bound just the same.

No edit to the config cheat sheet (Section 6.4 "Core Config Fields Summary (Cheat Sheet)"): the decision
adds no configuration key. The mechanism is `Implementation-defined` and published in the Conformance
Statement, not configured — a redaction policy an operator can weaken is a security control an operator
can switch off, and the floor is not optional.

No edit to Section 13.2 "Logging Outputs and Sinks", Section 13.3 "Runtime Snapshot / Monitoring
Interface", Section 13.4 "OPTIONAL Human-Readable Status Surface", or Section 13.7 "Humanized Agent
Event Summaries": each consumes text that is already redacted, and restating the rule at each consumer
is the enumeration this decision rejects (Option B in `Background.md`). Sections 13.1 and 13.8.2 are
edited only because each already carries a nearby content rule a reader would otherwise read as
exhaustive — Section 13.1's large-payload bullet and Section 13.8.2's own free-text fields.

No edit to Section 13.6 "Per-Execution Usage Ledger": its entry schema is counters, identifiers and a
`source_event` name, and carries no free text.

No edit to Section 9.8 "Git Automation and Work Branch" or Section 9.10 "Forge Operations, Pull
Requests, and Review Writes": commit messages and pull-request bodies are agent prose the repository
publishes deliberately, gated by its own `before:commit` gate / `scan-content` (Section 9.12, decision
0032). That control refuses rather than rewrites, which is the right shape for an artifact whose title
is used verbatim.

No `VCSX-SPEC.md` or `VCSX-CONTRACT.md` edit: the engine neither runs the agent nor captures its
messages, and no engine result carries agent free text.

## Steps

1. **Captured subprocess text is untrusted content.** Ensure Section 15.3 "Secret Handling" states that
   text Symphony captures from a subprocess it runs — the agent's messages and notifications (Section
   10.4) and a host-side hook's output (Section 15.4) — is untrusted content rather than a
   secret-typed value, because an agent that echoes a credential into its own message produces ordinary
   text with nothing to distinguish it from any other message. Done when the reason the preceding
   bullets do not reach this case is stated where those bullets live.
2. **The obligation is discharged at ingest.** Ensure Section 15.3 states that such text MUST be
   redacted of the run's resolved secret values where it enters the process — before it reaches
   orchestrator state (`last_message`, Section 4.1.6), a log sink, or a durable agent-session
   transcript — and that redacting once at that boundary rather than at each publishing surface is what
   makes every consumer inherit the guarantee, naming the log sinks, the snapshot, the status surface,
   humanized summaries and the OPTIONAL HTTP API as those consumers. Ensure it notes that the fields
   are observability data and not orchestration inputs (Sections 13.4, 13.7, 13.8), so redacting them
   cannot change behavior. Done when an implementer can locate the single point at which the
   requirement is satisfied.
3. **The mechanism is `Implementation-defined` above a stated floor.** Ensure Section 15.3 states that
   an implementation MUST replace at least every exact occurrence of the secret values this run
   resolved through the secret-provider interface — outward credentials and any repo-internal integrity
   value supplied to a host-side hook (both classes named in this section) — that the mechanism above
   that floor and the marker substituted are `Implementation-defined` and MUST be documented (Section
   19), and that pattern or heuristic matching MAY be added but MUST NOT replace the known-value floor.
   Done when "we scan with a regex instead" is non-conformant and "we also scan with a regex" is not.
4. **The residual is stated, not glossed.** Ensure Section 15.3 states that redaction is partial by
   construction and MUST NOT be presented as complete: it does not reach a derived form (an encoding of
   a credential, or one the agent paraphrases) and cannot reach a secret Symphony never resolved, such
   as one the agent reads out of repository or tracker content, because no value exists to match
   against; those residuals are governed by the trust boundary and harness hardening (Sections 15.1,
   15.5), and are why the secret-isolation invariant (Sections 9.6, 10.8) remains the primary control
   and redaction its backstop. Done when an implementation cannot cite this specification as a claim of
   complete protection.
5. **The emit boundary carries the obligation.** Ensure Section 10.4 "Emitted Runtime Events (Upstream
   to Orchestrator)" states, alongside its event field list, that free-text payload fields are
   agent-produced content and MUST be redacted before the event is emitted (Section 15.3). Done when an
   adapter author reading only Section 10.4 knows the field is not passed through verbatim.
6. **The log inherits it.** Ensure Section 13.1 "Logging Conventions" states, next to the existing
   `Avoid logging large raw payloads` bullet, that agent-produced free text reaches the log already
   redacted of the run's resolved secret values (Section 15.3), the rule binding where the text is
   captured rather than at each sink. Done when the section's only content rule is no longer a size
   rule.
7. **The API says which fields and where the rule lives.** Ensure Section 13.8.2 "JSON REST API
   (`/api/v1/*`)" states in its API design notes that `last_message` and `recent_events[].message` are
   agent-produced free text, that they are served already redacted because the requirement is
   discharged where the text enters the process (Section 15.3), and that the surface inherits both that
   guarantee and its residual rather than restating either. Done when the question the issue asks is
   answered at the place the issue asks it.
8. **The adapter is tested at the emit boundary.** Ensure Section 17.5 "Coding-Agent Adapters" carries a
   check that free-text event payloads are redacted of the run's resolved secret values before the event
   is emitted upstream. Done when the ingest obligation has a testable line in the profile that owns it.
9. **The surfaces are tested for the consequence.** Ensure Section 17.6 "Observability" carries a check
   that a secret value echoed back in agent free text appears in no observability surface — log sinks,
   snapshot or status surface, or the OPTIONAL HTTP API — and a check that the documented redaction
   mechanism is not weaker than the known-value floor. Done when the conflict the issue reports is a
   test rather than a reading.
10. **The checklist names it under Broker Core.** Ensure Section 18.1.2 "Broker Core Conformance" lists
    redaction of captured subprocess text at ingest, with the documented mechanism and the known-value
    floor that pattern matching does not replace (Section 15.3). Done when a conformance claim cannot
    omit it, whether or not the HTTP extension is shipped.
11. **The Conformance Statement collects the choice.** Ensure Section 19 "Conformance Statement" names
    the secret-redaction mechanism and marker for captured subprocess text (Section 15.3) among the
    enumerated `Implementation-defined` resolutions the Statement MUST record. Done when the
    MUST-document obligation Step 3 creates has a stated home.
12. **The template has a row for it.** Ensure `CONFORMANCE-STATEMENT-TEMPLATE.md` Section 4.1 "Core"
    carries a row for the secret-redaction mechanism and marker, citing Section 15.3, ordered by
    section number among its neighbours. Done when an implementation fills the choice in without
    improvising a row.

## Cross-cutting sync

Section 17.5 and Section 17.6 (Steps 8, 9), Section 18.1.2 (Step 10), Section 19 and
`CONFORMANCE-STATEMENT-TEMPLATE.md` (Steps 11, 12).

Section 6.4 needs no edit — no configuration key is added, deliberately (see `Scope`).

Section 18.2 "RECOMMENDED Extensions" needs no edit: the HTTP server bullet there describes what the
extension ships, and inheriting a core guarantee is not an extension obligation.

## Anchor changes

None removed or renamed. No new section title and no new code token: the decision adds normative bullets
to existing sections and one row to the Conformance Statement template.

## Out of scope

- **Commit messages and pull-request bodies.** Agent prose that becomes a published artifact is gated by
  the repository's `before:commit` gate / `scan-content` (Sections 9.8, 9.12, decision 0032), which
  refuses rather than rewrites — the right shape where a title is used verbatim. Recorded in
  `Background.md` with the residual named.
- **A configurable redaction policy.** No `redaction.*` namespace: an operator-weakenable security floor
  is a floor an operator can remove.
- **Detection of secrets Symphony never resolved** — a credential the agent reads out of repository or
  tracker content. There is no value to match against; it belongs to the trust boundary and harness
  hardening (Sections 15.1, 15.5) and is stated as a residual rather than mitigated.
- **Mid-run credential rotation.** Recorded in `Background.md` as a reconsideration trigger: it makes
  "the values this run resolved" time-varying and would need the floor to name the union.

## Status

Applied to `SPEC.md` (Sections 10.4, 13.1, 13.8.2, 15.3, 17.5, 17.6, 18.1.2, 19) and
`CONFORMANCE-STATEMENT-TEMPLATE.md`.
