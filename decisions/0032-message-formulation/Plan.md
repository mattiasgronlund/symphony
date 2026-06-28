# Plan — 0032 Message formulation: commit, pull request, squash

## Scope

Affected anchors in `SPEC.md`:

- Section 9.8/9.9 (commit + git verbs) — commit message authoring + validation; identity vs content.
- Section 9.10 (forge, pull requests) — PR title/body composition + scanning; one-PR-per-issue.
- The `before:merge` transform (decision 0030) — `pr_to_squash`.
- The broker CLI (decisions 0003/0004) — a content seam for agent-supplied PR text.

This plan defines the end-state only; no `SPEC.md` edit is made while the decision is `Proposed`.

## Steps

1. **Three message surfaces.** Ensure `SPEC.md` states the three surfaces and their origins: commit =
   **authored** (agent content), PR = **composed**, squash = **transformed**. Done when all three are
   described with their origin.

2. **Commit message.** Ensure the commit message is agent-authored in-sandbox, conventions conveyed
   by the prompt, validated by `scan-content`/`before:commit`; author/committer **identity** is repo
   config (decision 0007), distinct from content; mechanical merge commits use the engine default.
   Done when authoring, validation, and the identity/content split are stated.

3. **PR composition.** Ensure PR title/body are content composed from agent-supplied prose and/or
   durable inputs (ticket + closed task list + commit subjects), scanned with **title strict** /
   **body Linear-key-relaxed**, maintaining one PR per issue (created then updated, decision 0007).
   Done when the composition inputs and the strict/relaxed scan are specified.

4. **Content seam.** Ensure the broker CLI provides a credential-free channel for the agent to supply
   PR text (decisions 0003/0004). Done when the content verb is on the broker CLI surface.

5. **Squash transform.** Ensure the squash subject/body are mechanically derived from the PR via a
   repo-owned `pr_to_squash` transform at `before:merge` (title verbatim, body `strip-linear` for the
   surrounding repo), and that `land` never authors a message. Done when the transform and the
   thin-`land` property are stated.

6. **PR-body default = auto-compose.** Ensure the default PR body is auto-composed from durable inputs
   (ticket title/link + closed task list, decision 0031, + commit subjects), with agent-supplied prose
   **overriding** (replacing) it when present. Done when the auto-compose default and the agent-prose
   override path are stated.

## Cross-cutting sync

- **Section 6.4 (cheat sheet):** note the `pr_to_squash` transform and the message-surface origins.
- **Section 17 (test matrix):** squash message = `transform(PR)`; PR title is strict-scanned; PR body
  retains Linear keys but the squash body is laundered; commit message passes `scan-content`; the
  default PR body is auto-composed from ticket + closed task list + commit subjects, and agent-supplied
  prose replaces it.
- **Section 18 (checklist):** note message formulation is repo-owned WoW.

## Anchor changes

New tokens: `pr_to_squash`, the three message-surface terms (authored/composed/transformed), a broker
CLI content verb. Shares the `before:merge` position with decision 0030. Relates to decisions 0003,
0007, 0022, 0030, 0031. Depends on decisions 0027, 0030.

## Status

Accepted; `SPEC.md` application not started. Dependencies 0027 and 0030 are Accepted. The open fork
(default PR-body source) is **resolved**: auto-compose from ticket + closed task list (0031) + commit
subjects, agent prose overriding — see this decision's `Background.md` *Fork resolution*. `SPEC.md`
application is deferred and batched with the companion `vcsx` spec (0028) and decisions 0029–0031
(`pr_to_squash` is a `before:merge` edge of 0030's machine, housed in `repo.policy.toml`).
