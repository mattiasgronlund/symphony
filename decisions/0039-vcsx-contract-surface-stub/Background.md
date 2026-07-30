# Background — 0039 vcsx contract-surface stub to unblock the repo-owned-WoW batch

## Context

Decisions 0027–0032 (the repo-owned Way-of-Working re-framing) are all `Accepted`, but their `SPEC.md`
edits are deferred and **batched**, and decision 0028 requires that the batch "land in step with the
companion `vcsx` spec so the contract names stay identical across both documents." That companion
`vcsx` spec did not exist in this repository, and nothing here tracked its owner or schedule. The
result was a hard external gate: the single largest re-framing of `SPEC.md` (three-layer architecture,
the action-policy machine, `repo.policy.toml`, computed completion, message formulation) could not be
written without an out-of-repo artifact that had no visible timeline.

A design-review interview over the whole spec identified this as the most likely place the batch
stalls: the deferral discipline is sound, but it points at a document that no one had started. The
interview's chosen de-risking step was to **author the contract *surface* first** — the names, verbs,
and policy-graph vocabulary the batch must reference — as a tracked artifact, so the shared vocabulary
is frozen and the deferred edits can proceed against a stable local anchor.

This decision does not re-open 0028; it acts on 0028's own deferral, the way decision 0034 acted on a
host-side op named in decision 0025 and decision 0016 acted on the sweep deferred by 0006.

## Options considered

- **Option A — leave the batch gated on the external spec.** The coupling is real and piecemeal edits
  would forward-reference unwritten concepts. Trade-offs: honest, but the batch waits indefinitely on
  out-of-repo work with no owner; `SPEC.md` (the stated source of truth) keeps lagging the decided
  design.
- **Option B — a bare placeholder pointer in-repo.** A forward-reference target naming the future
  `vcsx` spec without fixing any vocabulary. Trade-offs: cheap, but it freezes nothing, so the batch
  still cannot be written without inventing tokens that may later diverge from the real engine spec.
- **Option C — draft the contract surface as a stub (chosen).** A companion document that fixes the
  shared names and surface semantics (executor + front-ends, `repo.policy.toml` sections, the
  action-policy machine, engine operations/results, lifecycle positions, the task model and verbs,
  message-formulation surfaces, trust sourcing) while explicitly deferring the wire schema, the
  field-level TOML schema, the plugin API, and the internal algorithms. Trade-offs: unblocks the batch
  and freezes vocabulary; risks getting a name wrong that the full engine spec later has to reconcile,
  which is mitigated by pinning the names to what decisions 0026–0032 already specify and by keeping
  the stub strictly at the surface (no schema/algorithm).

## Decision and reasoning

Chosen: **Option C** — author `VCSX-CONTRACT.md` as a contract-surface stub. It mirrors the deferral
pattern `SPEC.md` already uses for the coding-agent app-server protocol: the stub owns entry points and
policy vocabulary; the full engine spec/implementation owns schema and algorithm. Every token in the
stub is taken from what decisions 0026–0032 already fixed, so freezing them here creates no new design
— it records the vocabulary the batch was always going to reference.

The stub keeps `SPEC.md` as the single source of truth (the interview's stance) and shrinks the
deferral window: the 0027–0032 edits can now be written against a stable in-repo anchor, and the full
`vcsx` spec, when authored, reconciles to these names rather than inventing them independently.

We would reconsider if the full engine spec, once written, needs a surface name this stub got wrong (a
name change is then recorded in the owning decision's `Anchor changes` and applied to both documents),
or if the batch turns out to need engine *schema* the stub deliberately deferred — in which case the
stub grows a section rather than the batch stalling again.
