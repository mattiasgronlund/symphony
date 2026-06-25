# Background — 0022 Forge adapter surface

## Context

Decision 0007 folded pull-request operations into the VCS adapter: one adapter backs "the broker's git and
pull-request verbs" (Section 9.7/9.9), and `link_pull_request` is a tracker write (Section 11.1, decision
0008). The tracker-vs-forge scoping pass (this session) found that PR/review writes are a distinct surface
from the git remote, and that `link_pull_request` is under-specified.

Evidence from the 22-fork sweep (`adapter-layer-fork-evidence` memory): the forks that abstracted PR/review
writes consistently separated the git-remote plumbing from the code-host *collaboration* layer — Harmony
split a dedicated `Forge` behaviour (PR/MR plus `create_review`/`reply_to_review_thread`/
`resolve_review_thread`), miyataka exposed a separate `PullRequestMerger`, mattconzen an optional
`PullRequestSetter`, issuepilot kept `createMergeRequest` on the GitLab (forge) adapter. The current spec
has no home for review-thread writes at all (its broker verbs are only `pr` and `request-merge`).

The scoping also resolved `link_pull_request` by topology: when the tracker is the same platform as the
forge (GitHub issues + GitHub PRs), the link is forge-native (a reference in the PR body); when the tracker
is a separate system (Linear issues + GitHub PRs), the PR reference must be written onto the tracker item.

## Options considered

- **Clarify only; keep PR folded into the VCS adapter.** Minimal, but leaves review-thread writes
  homeless and keeps the git-remote and collaboration surfaces conflated. Not chosen.
- **Move PR-linking entirely to the forge, drop `link_pull_request` from the tracker.** Clean for
  same-platform, but lossy cross-system: a GitHub forge adapter cannot write a reference onto a Linear
  issue. Rejected.
- **Split a first-class Forge adapter (chosen).** Separate the single VCS adapter into a VCS (git-remote)
  contract and a Forge (code-host collaboration) contract, matching the attested fork architecture and
  giving review-thread writes a home.

## Decision and reasoning

Split Section 9's adapter into two contracts on the same code host:

- **VCS adapter** (Section 9.7) — the git remote: clone/fetch/branch/back-merge/push. Broker **git verbs**
  are `push` and `back-merge` (Section 9.9).
- **Forge adapter** (new Section 9.10) — the code-host collaboration layer: pull-request/merge-request
  create/update/merge, plus OPTIONAL review-thread writes (post a review comment, reply to a thread,
  resolve a thread). Broker **forge verbs** are `pr` (create/update), `request-merge`, and, where
  supported, the review writes.

The Forge adapter is the same code host as the VCS adapter and reuses `vcs.kind` and `vcs.api_key`; the
split is at the contract level, not a separate credential. Like the agent (Section 10.9) and tracker
(Section 11.7) adapters, the Forge adapter advertises a static capability descriptor (data, not a runtime
call): pull-request create/update is REQUIRED of every forge adapter; review-thread writes are OPTIONAL.

`link_pull_request` is reconciled: when the tracker shares the forge's platform the link is forge-native
(PR body reference) and the tracker adapter MAY declare `link_pull_request` unsupported (Section 11.7); when
the tracker is a separate system the PR reference is written onto the tracker item through
`link_pull_request` (Section 11.1). PR creation and the orchestrator's `pull_request_opened` run-outcome
trigger (Section 11.6) are unchanged in intent.

Reasoning: matches the attested fork architecture (Harmony's Tracker/Forge split), gives review-thread
writes a home, makes the PR-to-issue link boundary explicit, and adds no config by reusing the code-host
credential. Refines decision 0007 (PR moves out of the VCS adapter) and decision 0008 (`link_pull_request`
semantics).

Problems to watch: VCS and Forge are co-located by assumption (same code host); a git remote on one host
with a forge elsewhere is deliberately not modeled (a non-real case). Review-write *enablement* is
capability-gated, not a policy toggle, so an operator who wants a capable adapter but a disabled review
surface has no switch yet — a possible later refinement. Reusing the `vcs` config for the forge (rather than
a separate `forge` block) is a deliberate, reversible choice recorded here.
