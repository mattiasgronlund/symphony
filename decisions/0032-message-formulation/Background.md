# Background — 0032 Message formulation: commit, pull request, squash

## Context

How commit, pull-request, and squash-merge messages are formulated was unspecified. Two facts shape
it: the agent is credential-less and supplies only **content** (decision 0003); and message
formatting/laundering (forbidden-token hygiene, Linear-key stripping, a `Co-Authored-By` trailer,
Conventional-Commit conventions) is **Way-of-Working** — repo-owned, not something Symphony should
bake in. A clean observation drove the squash side: the squash-merge message is a **mechanical
transformation** of the pull-request message, not separately authored.

## Options considered

- **Commit message.** A commit is a *local* operation, so the agent authors it in-sandbox,
  credential-free. Conventions are conveyed by the prompt; validation is the `scan-content` /
  `before:commit` edge (for the surrounding repo, the forbidden-token scan). Author/committer
  **identity** is repo config (decision 0007), distinct from message content. Mechanical commits
  (the merge/back-merge from `integrate`) get the engine's default message, not agent content.

- **Pull-request message.** Title/body are content. Sourced from agent-supplied prose and/or
  **derived** from durable inputs the system already holds — the ticket (title, link), the closed
  task list (decision 0031 — a structured work summary), and commit subjects — then composed by a
  repo-owned step and scanned (title strict; body Linear-key-relaxed). This needs a small new
  **content seam**: the agent hands PR text across the credential boundary over the broker CLI
  (decisions 0003/0004). The default PR-body source was an open fork (agent-prose vs auto-compose vs
  both); it is now **resolved** — see *Fork resolution* below.

- **Squash message.** Mechanically derived from the PR via a repo-owned `pr_to_squash` transform at
  the `before:merge` position (decision 0030): title verbatim, body `strip-linear` for the
  surrounding repo. The transform **re-imposes on durable history the strictness deliberately relaxed
  for the live PR surface** (the PR body may carry Linear keys for the forge integration; history must
  not). `land` stays thin — it transforms, it never authors.

## Decision and reasoning

Message **content** is the agent's; message **formulation policy** (conventions, composition,
validation, laundering, transformation) is repo-owned WoW expressed in `repo.policy.toml` hooks
(decision 0029); Symphony bakes in no format. The three message surfaces have distinct origins:
commit is **authored** (agent), PR is **composed** (agent content + ticket + task list), squash is
**mechanically transformed** from the PR. This keeps `land` thin and reuses the action-policy machine
(decision 0030) for the `before:merge` transform and the `before:commit`/`before:create_pr` scans.

## Fork resolution — PR-body default is auto-compose (2026-06-28)

The default PR body is **auto-composed** by the repo-owned step from the durable inputs the system
already holds — the ticket (title, link), the closed task list (decision 0031, a structured work
summary), and commit subjects. Agent-supplied prose, when handed across the content seam,
**overrides** (replaces) the composed body; absent it, the auto-composed body stands. Chosen because
autonomous/daemon operation already holds these inputs, so the default is deterministic and consistent
without depending on the agent authoring a good body unattended — and decision 0031's materialized task
list makes the composed body a genuine work summary, not a mechanical stub. A "both" hybrid (prose plus
a derived section) was considered and not chosen as the default; since formulation is repo-owned WoW, a
repo is free to template that shape in `repo.policy.toml`.

We would revisit the content seam if a richer agent→broker content channel proves necessary.

The decision is **Accepted** (dependencies 0027 and 0030 are Accepted; the PR-body fork is resolved
above); the corresponding `SPEC.md` change is **not** made yet — application is deferred (see
`Plan.md` Status). Relates to decisions 0003 (agent supplies content), 0007/0022 (broker creates
PR/merge), 0030 (`before:merge` position), and 0031 (task list as a PR-body source).
