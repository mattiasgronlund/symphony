# Plan — 0176 A constraint with no operand, and a verb with no stated arguments

## Scope

`SPEC.md` only: Section 10.8 (Privileged Operation Broker (`symphony` CLI)), Section 9.10 (Forge
Operations, Pull Requests, and Review Writes), Section 5.6 (`repo.policy.toml` (Repository Way of
Working)), Section 17.2 (Workspace Manager and Safety) and Section 18.1.2 (Broker Core Conformance).

Section 9.7 (Repository Provisioning and the VCS Engine) is unchanged: its three-source resolution
is what this decision relies on and is already correct. `VCSX-SPEC.md` and `VCSX-CONTRACT.md` are
unchanged — nothing is asked of an engine, and no `outputs.base` is added.

## Steps

1. **Section 10.8 states what the `pr` verb carries.** Ensure the brokered-operations bullet says
   that the `pr` verb carries the agent's pull-request text and no base: the base is the resolved
   pull-request target (Section 9.7), supplied by Symphony rather than named by the agent, so the
   agent has no way to select a pull-request target from inside the sandbox.
   Done when Section 10.8 states the `pr` verb's payload and says it carries no base.

2. **Section 10.8's authorization-scope bullet distinguishes its three mechanisms.** Ensure the
   bullet no longer lists three constraints as one kind of check: the work branch is derived from
   the binding and a request naming another ref is refused; the issue is derived from the binding
   and an agent-supplied identifier is not trusted; and the pull-request base is constrained by the
   verb carrying none, so there is nothing to check rather than a check to perform.
   Done when the bullet names the mechanism for each of the three.

3. **Section 9.10's content seam says what the agent does not supply.** Ensure the bullet stating
   that the agent supplies pull-request text across the sandbox boundary adds that it supplies no
   base, cross-referencing Section 10.8 for the verb's payload and Section 9.7 for where the base
   comes from.
   Done when the content-seam bullet names the base as something the agent does not supply.

4. **Section 5.6 names the base branch among `repo.policy.toml`'s sections.** Ensure the Sections
   list includes the base branch — the repository's own contribution to the pull-request target and
   the lowest of Section 9.7's three sources, whose field-level schema is deferred to the engine
   contract like the rest of the file.
   Done when Section 5.6's section list names the base branch.

5. **Section 17.2 checks it.** Ensure a `Broker Core Conformance` check asserts that the broker's
   `pr` verb carries no base, so the agent cannot name a pull-request target — in the shape the
   neighbouring provisioning-verb check already uses, which asserts a verb set's absence rather than
   a refusal.
   Done when Section 17.2 contains that check beside the provisioning-verb one.

6. **Section 18.1.2's broker item names it.** Ensure the Privileged Operation Broker item states
   that the verb set carries no pull-request base, alongside its existing authorization-scope and
   structured-result clauses.
   Done when the item names it.

## Cross-cutting sync

- **Section 6.4 (Core Config Fields Summary (Cheat Sheet))** — unaffected. No configuration key is
  added, removed or renamed; `vcs.base_branch` keeps its entry and its meaning.
- **Section 17** — step 5. **Section 18** — step 6.
- **Conformance Statement templates** — no row owed. This decision adds no `Implementation-defined`
  value and no MUST-document obligation; it fixes an argument list the specification left unstated,
  and the resolved base's three sources are already Section 9.7's.
- **`VCSX-SPEC.md` Sections 13.1–13.3** — unaffected. No engine obligation changes and no
  `outputs.base` is added; the engine already resolves the base from its own three sources
  (`VCSX-SPEC.md` Sections 6.4, 8.1).
- **Conformance corpus** — unaffected. A broker verb's payload is not a deterministic,
  host-independent function, so it stays a Section 17.2 check.

## Migration note (not a specification change)

An implementation that today carries an agent-supplied base removes it in this order: the in-sandbox
client's argument, the wire field, the engine-verb field, the run binding, and the comparison
**last**. For as long as the argument exists the comparison is the only thing between a mandatory
agent-supplied operand and the operation, so removing the guard first converts a fail-closed design
into an unconstrained one. Recorded here because a later implementer reading this decision is the one
who needs it; see `Background.md`.

## Anchor changes

None. No code-token identifier is renamed or removed and no section is retitled. The `pr` verb keeps
its spelling; what changes is that its payload is stated.

## Status

Applied to `SPEC.md`: Section 10.8's authorization-scope bullet and its VCS/forge verb entry,
Section 9.10's content-seam bullet, Section 5.6's sections list, Section 17.2's check, and Section
18.1.2's broker item. All six steps.

Section 10.8's authorization-scope list keeps its `for example` — the three named constraints are
illustrative of a rule over every brokered operation, not a closed set, and the mechanism sentence
is scoped to those three examples rather than to the list.
