# Plan — 0039 vcsx contract-surface stub to unblock the repo-owned-WoW batch

## Scope

New artifact `VCSX-CONTRACT.md` at the repository root (a companion to `SPEC.md`, not a `SPEC.md`
edit). It fixes the shared vocabulary the deferred 0027–0032 `SPEC.md` edits reference. No `SPEC.md`
edit is made by this decision; it removes the external gate that blocked those edits.

The stub fixes these surfaces (each a section of `VCSX-CONTRACT.md`), with tokens taken verbatim from
decisions 0026–0032:

- executor + two front-ends (`ship`, `land`, the daemon driver); one policy-graph executor over one
  `repo.policy.toml` (decisions 0027, 0028);
- `repo.policy.toml` sections — engine selection, `scope.branch_pattern`, the action-policy edges/hooks,
  `tracker.transitions`, `[tasks]`, `[driver]`; `vcsx.toml` merged in (decisions 0028, 0029, 0030,
  0031);
- the action-policy machine — triggers (`before:commit`, `before:push`, `before:create_pr`,
  `before:merge`; `<op>:<reason>` results; task-state events), actions (`run_op`, `run`, `escalate`,
  `create_task`, `set_state`, `notify`, `park`, `fail`), `#class` fallback over `done`/`needs_caller`/
  `error`, the two unmatched policies, the reason-token class contract, abstract `escalate` (decision
  0030);
- engine operations and typed results (`commit`, `integrate`, `push`, `create_pr`, `merge`; `push:ok`,
  `push:non_fast_forward`, `integrate:merge_conflicts`) (decisions 0007, 0022, 0028, 0030);
- lifecycle positions and the positional-name mapping (`after_push` ≡ `push:ok`, etc.) (decisions 0026,
  0030);
- the task model (`id`/`description`/`status`/`assignee`/parent/link), broker task verbs
  (`add`/`split`/`close`/`need-help`/`update`), `tasks:all_closed` → `ship`, `structured-task-write`,
  write-through materialization (decision 0031);
- the message-formulation surfaces (authored/composed/transformed), `pr_to_squash` at `before:merge`,
  the content seam (decision 0032);
- trust sourcing (base-sourced vs worktree-sourced) and the outward-credential vs integrity-value
  taxonomy (decision 0029).

## Steps

1. **Author the stub.** Ensure `VCSX-CONTRACT.md` exists at the root, declares itself a contract-surface
   stub, states the `SPEC.md`-defers-to-it deferral (mirroring the app-server-protocol deferral), and
   fixes the surfaces above. Done when the file exists and each surface above appears with the tokens
   spelled as in decisions 0026–0032.

2. **Fix the deferral boundary.** Ensure the stub explicitly defers the wire/RPC schema, the field-level
   `repo.policy.toml` schema, the plugin API, the concrete reason-token registry beyond its classes, and
   internal algorithms. Done when a "Deferred to the full engine spec" section states each exclusion.

3. **Fix the alignment rule.** Ensure the stub states that names here and in `SPEC.md` MUST stay
   identical and that a name change is recorded in the owning decision's `Anchor changes`. Done when the
   provenance/alignment section states the rule and names the shaping decisions (0026–0032) and the
   reusing decisions (0035–0038).

4. **Unblock note in 0028.** Record in decision 0028 that its "companion `vcsx` spec" gate is now met at
   the surface by `VCSX-CONTRACT.md` (append-only), so the 0027–0032 batch may proceed against the
   frozen vocabulary. Done when 0028's record points at the stub. (This step is bookkeeping across the
   batch, not a `SPEC.md` edit.)

## Cross-cutting sync

None in `SPEC.md` (no `SPEC.md` edit). When the 0027–0032 batch is applied, its own plans own the
Section 6.4 / 17 / 18 sync; this decision only removes the blocker. The stub itself notes the
topology-equivalence test (decision 0028) that Section 17 will carry.

## Anchor changes

New artifact: `VCSX-CONTRACT.md`. No `SPEC.md` anchors are added, renamed, or removed by this decision.
The tokens the stub fixes are introduced into `SPEC.md` by the 0027–0032 batch, not here.

## Status

Applied — `VCSX-CONTRACT.md` authored. Depends on decision 0028 (Accepted); acts on 0028's deferral to
the companion `vcsx` spec. The 0027–0032 `SPEC.md` batch remains deferred but is now unblocked at the
vocabulary level; the full `vcsx` engine spec (schema, plugin API, algorithms) remains a separate
forward artifact this stub defers to.
