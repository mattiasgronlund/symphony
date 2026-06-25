# Background — 0020 Normalized issue metadata and optional fields

## Context

Section 4.1.1 defines the normalized `Issue` as a flat record. The 22-fork tracker sweep (0008
`Background.md`; `adapter-layer-fork-evidence` memory) showed two problems the spec inherited from its
Linear origin:

- **Silent field loss.** Every fork normalizes into a flat struct and drops whatever the fields do not
  capture — Jira custom fields, Monday board columns, Feishu Bitable cells, Todoist due/deadline. The
  schema-rich targets (boards, spreadsheets) are exactly where the loss hurts, and there is nowhere on the
  model to round-trip a provider handle a later write needs (GitHub Projects v2 requires a project-item-id
  distinct from the issue node-id, which forks either modelled as a field, re-resolved per write, or keyed
  off `repo#number`).
- **Linear-ism fields that no-op elsewhere.** `branch_name` (Linear supplies it natively) and `blocked_by`
  (derived from Linear `blocks` relations) silently become null/empty on trackers without those concepts.
  Monday and Bitable hard-code `blocked_by` empty; odyssey's blocker gating silently stops working for
  Jira/GitHub. The fields read as universal but are not.

No fork keeps a raw provider blob on `Issue`; the escape hatch, where present, is a structured carrier —
kimjj81 puts a `metadata` map on `Issue`, jialinyi94 wraps `Issue` in a `WorkItem{tracker_kind,metadata,
attached_pr}`. The standing finding across sweeps: keep the model flat and neutral, add a carrier rather
than a raw blob, and mark the Linear-specific fields optional.

## Options considered

- **Keep flat, document the loss, no carrier.** Rejected: loses data where it is richest and forces
  per-write re-resolution of provider handles.
- **Raw provider payload on `Issue`.** Rejected: no fork does this; it leaks provider shape into the
  neutral model and bloats prompt rendering (Section 12 iterates the issue object).
- **A wrapper entity (WorkItem) around `Issue`.** Rejected for now: a larger architectural change that
  introduces a new entity threaded through orchestration/prompt/observability. The metadata-on-`Issue`
  approach captures the value with far less churn.
- **Opaque `metadata` map on `Issue` plus optional Linear-isms (chosen).** Matches kimjj81; minimal and at
  the same altitude as the surrounding fields.

## Decision and reasoning

- **Add `metadata` to Section 4.1.1**: an opaque, adapter-owned key/value map carrying tracker-specific
  data the flat fields do not capture; empty when the adapter has none. The orchestrator core does not
  interpret it. An adapter MAY use it to round-trip a provider handle it needs for writes (for example a
  GitHub Projects v2 item id) instead of re-resolving it per write. This is the documented escape hatch
  replacing silent field droppage.
- **Mark `branch_name` and `blocked_by` OPTIONAL and tracker-dependent.** An adapter whose tracker has no
  native branch metadata leaves `branch_name` null or MAY synthesize one; an adapter whose tracker has no
  dependency model leaves `blocked_by` empty, and blocker-gated dispatch (Section 8.2) then observes no
  blockers and does not gate. This makes the existing degradation explicit rather than accidental.
- **Section 11.3**: the `blocked_by`/`branch_name` derivations shown are Linear-specific; other adapters
  populate them per their own model or leave them empty. `metadata` contents are `Implementation-defined`
  (the implementation MUST document what its adapter places there).

Reasoning: keeps the normalized model neutral and honest (no silent loss, no provider-shape leak), gives
the GitHub Projects v2 dual-handle problem a home without per-write re-resolution, and degrades
dependency-gating cleanly. It stops short of a WorkItem wrapper to stay surgical.

Problems to watch: `metadata` MUST stay opaque to the orchestrator core — no core logic may branch on its
contents, or provider specifics leak back into neutral code (the failure mode the sweep documented). It is
exposed to the repository-owned prompt template (Section 12), which is acceptable: it carries no secret
channel (secrets resolve only through the secret provider, Section 15.3). And the carrier must not grow
into a typed per-provider schema — keep it opaque key/value, or it re-creates the coupling it removes.
