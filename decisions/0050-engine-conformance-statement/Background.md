# Background — 0050 Publish an engine Conformance Statement

## Context

Decision 0045 introduced the Conformance Statement — a per-implementation published artifact
consolidating exactly the contract-visible choices — and built `CONFORMANCE-STATEMENT-TEMPLATE.md` for
it. That work was Symphony-scoped by construction, because decision 0043 had already *deferred* engine
conformance rather than restating it: `SPEC.md` Section 17 says "The VCS engine has no profile here",
and the Symphony template's own conformance-claim section says "Engine conformance is deferred to
`VCSX-SPEC.md` Section 13."

`VCSX-SPEC.md` Section 13 receives that deferral with a test matrix (Section 13.1) and an
implementation checklist (Section 13.2) — but with no place to *publish* what an engine chose. The
engine specification carries obligations of its own that nothing currently gathers:

- checkout-mode detection: `Implementation-defined`, and "the backend MUST document how it detects the
  mode" (Section 3.3);
- `repo.policy.toml` discovery precedence: `Implementation-defined` and MUST be documented
  (Section 6.1);
- the form of a hook's engine-invoked `run` unit (Section 6.6);
- the argument encodings for entry points, where only the argument *names* are fixed (Section 8.1);
- the escalation `detail` field (Section 8.4).

Three further obligations are documentation duties in the same sense even though they are not phrased
with the `Implementation-defined` keyword: an engine "MUST document any reason it adds beyond this
registry" (Section 4.3), the `need` vocabulary "MUST be documented and stable within a major version"
(Section 8.4), and each plugin advertises a static capability descriptor that the executor reads before
invoking a capability and MUST NOT invoke an undeclared one (Section 9.3) — so which capabilities a
given engine build declares is a fact a consumer must know *before* writing policy against it.

The gap is sharpest for exactly the thing decision 0049 schedules first. `SPEC.md` Section 3.4 says the
`engine-direct` topology "claims a conforming engine only, and therefore no profile defined here", so a
pure engine implementation that is never embedded in Symphony has no publication surface at all under
the current artifacts.

## Options considered

- **Option A — a minimal engine Conformance Statement template (chosen).**
  `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` beside `VCSX-SPEC.md`, mirroring 0045's structure at the
  engine's much smaller scale, plus a short `VCSX-SPEC.md` Section 13 clause requiring the Statement.
  Trade-offs: applies 0045's reasoning where it still holds — a silently-skipped obligation stays
  invisible, and implementations cannot be compared — at a cost proportional to the surface, which
  here is five resolutions plus the version, reason, `need`, and capability declarations. Adds one
  artifact to keep aligned with the specification.
- **Option B — the Section 13.2 checklist plus a per-implementation README.** Trade-offs: no new
  artifact, and Section 13.2 already reads as a definition of done. But a checklist item is not a
  filled-in value: it can be ticked without recording *which* discovery precedence or *which* detection
  mechanism was chosen, which is precisely the information a consumer needs. This is the option 0045
  weighed and rejected for Symphony as "a definition-of-done bullet is not a published declaration and
  cannot carry a filled-in value"; nothing about the engine changes that reasoning.
- **Option C — extend the Symphony template with an engine section.** Trade-offs: one artifact instead
  of two, and a `daemon` deployment does declare an engine pin. But it puts the obligations under the
  wrong owner: an engine is conformant independently of Symphony, and `engine-direct` claims no
  Symphony profile, so this would make a Symphony artifact a precondition for publishing an engine
  that may never be embedded. It also re-couples the two documents that 0043 deliberately decoupled.
- **Option D — defer until a second engine implementation exists.** Trade-offs: mirrors how 0045
  deferred its machine-readable manifest. But that deferral was justified by a specific hazard —
  "over-commits to a wire format before an implementation exists to shape it" — and a human-readable
  statement has no wire format to over-commit. The trigger 0045 named has also already fired: an
  implementation now exists (0049), and it is the topology with no other surface.

## Decision and reasoning

Choose **Option A**. Publish a per-engine Conformance Statement, add
`VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` to the specification repository as its RECOMMENDED shape, and
add a short `VCSX-SPEC.md` Section 13.3 clause that requires the Statement and enumerates what it must
record — mirroring `SPEC.md` Section 19 in structure and register, at the engine's scale.

The template is deliberately small, because the engine's contract-visible surface is small. It is a
*view* over obligations that already exist — the five `Implementation-defined` sites, the version and
major-stable surface (Section 8.5), reasons added beyond the Section 4.3 registry, the `need`
vocabulary, and the plugin capability descriptors (Section 9.3) — and it adds no obligation of its own.
That is the same single-source derivation 0045 used, and it is what keeps a checklist from drifting
into three.

Including the capability descriptors is the one addition that is not a restatement of an
`Implementation-defined` clause, and it earns its place: Section 9.3 makes an undeclared capability an
`error`-class result and Section 6.10 makes a policy requiring an unsupported capability a
configuration error, so which capabilities a build declares is load-bearing for anyone authoring
`repo.policy.toml` against it. It is contract-visible by the strictest reading of 0045's test.

The Statement remains a *published declaration*, not a gate: Section 13.1's matrix and Section 13.2's
checklist keep their existing roles, and nothing here makes the Statement a precondition for running
the engine.

We would reconsider the separate-artifact split if the engine ever ceased to be an independent
deliverable — the case decision 0042 anticipated for its Option B, where the engine becomes an
in-process module — since a single embedded artifact would then have a single owner again.

The decision is **Accepted** and applied: `VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md` is created and
`VCSX-SPEC.md` gains Section 13.3. Depends on 0043 (which deferred engine conformance to
`VCSX-SPEC.md` Section 13), 0045 (the Statement model and its reasoning), and 0049 (which made the
gap live); relates to 0002 (the stable-addressing discipline the template follows).
