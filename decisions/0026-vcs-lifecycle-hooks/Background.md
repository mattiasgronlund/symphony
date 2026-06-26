# Background — 0026 VCS-operation lifecycle hooks aligned with `vcsx`

## Context

An external tool, working name `vcsx`, is being extracted from the version-control wrapper layer of a
repository that runs Symphony. `vcsx` is the generic, policy-free engine over `git`/`jj`/forge that
automates and enforces a repository's VCS workflow through high-level commands (`safe-push`, `land`,
`update-branch`, …) and a set of repo-special **hooks** it calls out to. Symphony and `vcsx` overlap
exactly at Symphony's Sections 9.7–9.10 (VCS/forge adapters, broker git/forge verbs) and Section 10.8
(the privileged broker).

The integration must support three deployment topologies for the *same* repository policy:

1. **Symphony** — the broker runs the VCS engine host-side, with credentials, over the bind-mounted
   worktree; the agent has no credentials.
2. **Agent under Symphony (in-sandbox)** — the sandboxed agent runs the credential-free part of the
   engine (commit, content scan, gate) and leaves results in the worktree.
3. **Non-Symphony** — a user clones the repo and runs the engine directly in one trust domain with
   full credentials (the topology `vcsx` was extracted from).

Across these, the gate that gives confidence and speed (and any build-result cache it warms) is **not**
an enforcement boundary — the real gate stays at the forge's merge-time checks plus review, exactly as
today's GitHub workflow. Whether a cache exists at all, and whether it is trusted, is the integrating
repository's business; Symphony and `vcsx` must provide only the seams. The design rests on one
invariant: a "before" hook and a later "after" hook communicate **only through durable worktree
state**, so the warm→publish pair can be split across the sandbox boundary (cases 1+2) or folded into
one process (case 3) with identical behavior.

`vcsx`'s current hook layer is named by *role* in that one integration — `validate`, `scan-content`,
`resolve-base`, `pr-body-transform`, `post-push`, `post-gate` — and several of these fire in direct
sequence at the same point in the flow. A companion proposal to the `vcsx` spec **merges** each
adjacent cluster into one hook per lifecycle position and **renames** them to positional, abstract
`before_*` / `after_*` names: `before_commit`, `before_push`, `after_push`, `before_pull_request`
(with base resolution demoted to configuration, not a hook).

Symphony already has the right machinery but on the wrong axis:

- It models hooks at **two trust levels** (Section 15.4): operator-owned, trusted, **host-side**
  policy-config hooks, and repo-owned, untrusted, **in-sandbox** `WORKFLOW.md` hooks.
- But its lifecycle hooks (`after_create`, `before_run`, `after_run`, `before_remove`; Section 9.4)
  sit on the **workspace** lifecycle (create / run / remove), not the **VCS-operation** lifecycle
  (commit / push / pull request). The VCS work in Sections 9.8–9.10 is modeled as broker *behavior*
  with no hook seam, so a repo cannot inject policy around it.

This decision is to align Symphony's hook vocabulary with `vcsx`'s positional set by adding a
VCS-operation lifecycle hook axis on top of Symphony's existing two-trust-level model — so one repo
can express one policy and have it honored identically in all three topologies.

## Options considered

- **Option A — Do nothing; keep VCS work hook-less.** Symphony keeps modeling commit/push/PR as
  broker behavior with no repo seam. Trade-offs: zero change, but a repo's gate / content-scan /
  cache-publish policy cannot be wired around Symphony's broker verbs, so topologies 1 and 3 cannot
  run the *same* policy. Defeats the integration goal.

- **Option B — Adopt `vcsx`'s positional hooks as a new VCS-operation lifecycle axis (chosen).**
  Introduce OPTIONAL `before_commit`, `before_push`, `after_push`, `before_pull_request` hooks fired
  around the broker's commit/push (Sections 9.8–9.9) and forge `pr` (Section 9.10) verbs, classified
  onto the existing two-trust-level model (Section 15.4): `before_commit` at the in-sandbox/untrusted
  level (warming, no secrets); `before_push` / `after_push` / `before_pull_request` at the
  policy-config/host/trusted level, with `after_push` permitted a declared secret (Section 15.3) and
  outward writes under the operator's credentials. `before_*` may block (stable reason code, Section
  10.8); `after_*` is best-effort and never blocks (mirroring `after_run` / `before_remove`). The
  worktree (Section 9.6) is the only channel between an in-sandbox `before_commit` and a host-side
  `after_push`. Trade-offs: net-new OPTIONAL surface and a second hook axis to document and test, but
  it reuses the trust model and adapter/verb structure already present, and it is the minimum that
  makes one policy portable across the three topologies. Marked OPTIONAL so core conformance is
  unaffected.

- **Option C — Invent a Symphony-native hook vocabulary, not aligned with `vcsx`.** Trade-offs: free
  to fit Symphony's idiom, but it forces a translation layer at the boundary and a repo to maintain
  two policy expressions; it forfeits the "same command, same config" property that makes topology 3
  and topology 1 provably equivalent.

## Decision and reasoning

Choose **Option B**. The alignment value is the whole point: a positional, tool-neutral hook
vocabulary lets a repository write its VCS policy once and have `vcsx` (interactive) and Symphony (the
broker) execute it identically, with the sandbox boundary falling cleanly on the
`before_commit | after_push` worktree seam. Symphony contributes the host-side trusted execution and
secret provision the seam needs; it ships **no** cache, token, or signing policy — those live entirely
in the repo's wired hook implementations, so Symphony cannot tell whether a cache exists or is trusted.

Keeping the set **OPTIONAL** preserves core conformance: a deployment that wants only the forge's
merge-time gate wires nothing and behaves as today. We would reconsider if the four positions prove
insufficient (for example a genuine need for `after_commit` or a `before_merge` seam), or if the
`vcsx` proposal settles on different position names — in which case this decision tracks that
vocabulary, since the explicit goal is alignment, not independence.

The corresponding `SPEC.md` change is **not** made yet: this records the decision and its reasoning
(State: Proposed), pending acceptance and the parallel `vcsx` spec change.
