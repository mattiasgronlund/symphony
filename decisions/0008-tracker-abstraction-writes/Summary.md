# Tracker-Writes Investigation — Summary

**Session:** Tracker writes: 22-fork deep dive (`60feb229-ad43-45d3-811c-217a4f77d4ef`), 2026-06-25
**Trigger:** Deepen decision 0008 ("Tracker abstraction and writes") by studying forks that retargeted the
tracker.

## Method

Fanned out 7 parallel agents over ~22 live forks of `openai/symphony` (GitLab, GitHub Issues, GitHub
Projects v2, Jira, Monday, Feishu Bitable, Todoist, local SQLite `td`, bespoke Postgres, 2 real Rust ports).
Every claim verified against the actual repo — the inherited fork-label table was again partly wrong
(`miyataka`/`hawkymisc` are genuine ports; the four "Projects v2" forks are independent designs). Findings
recorded in this decision's `Background.md` (re-evaluation section) and the `adapter-layer-fork-evidence`
memory.

## What the forks confirmed about 0008

- The two core writes (`add_comment` + `set_state`) are the right floor; every richer write lived *outside*
  the core behaviour.
- `set_state(target_state)` is the right altitude (Jira proves it — the adapter resolves target→transition
  internally).

## Decisions produced (0017–0024, all Accepted, on `origin/main`)

| # | Outcome |
|---|---|
| 0017 | Flat milestone map -> explicit `{from, on, to}` transition graph (`tracker.transitions`), keyed on agent milestone signals + orchestrator run outcomes. |
| 0018 | Capability descriptor (static, adapter-declared): reads REQUIRED, writes declared; `tracker_unsupported_operation`; no silent no-ops. |
| 0019 | Neutralized `linear_*` error vocabulary -> `tracker_*` (mirror of 0016). |
| 0020 | Opaque `metadata` escape hatch on the normalized Issue; `branch_name`/`blocked_by` marked OPTIONAL/tracker-dependent. |
| 0021 | `set_state` write semantics: idempotent no-op, `tracker_state_unreachable`/`tracker_state_conflict`, SHOULD-verify, failure doesn't fail the run. |
| 0022 | Split a first-class Forge adapter (PR/MR + review-thread writes) out of the VCS adapter; reconciled `link_pull_request`. |
| 0023 | Adapter-declared auth mode (`secret`/`none`) — admits no-auth/local trackers; `api_key`/`endpoint`/preflight conditional. |
| 0024 | Candidate enumeration completeness — `fetch_candidate_issues` MUST return the full set; silent capping non-conformant. |

## Net effect on the spec

Decision 0008's broad "tracker abstraction and writes" became a precise, neutral, capability-gated tracker +
forge contract: graph-driven lifecycle, declared write/auth capabilities, neutralized vocabulary, an
escape-hatch issue model, honest `set_state` semantics, a separated forge surface, and complete candidate
enumeration. Recurring principle throughout: *requirements and capabilities are adapter-declared DATA, not
core assumptions.*

## Consciously deferred (recorded in the decisions' "problems to watch")

- Bounded/server-side-ordered candidate mode — a scale optimization (0024).
- Neutral `api_key` -> `credential` rename — `api_key`/`endpoint` are token-flavoured for a DSN adapter
  (0023).
- A policy toggle to disable a capable forge's review writes (0022).

## Git

`origin/main` `5547079 -> d080429`, fast-forward only, one commit per decision plus a lead commit for the
0008 investigation record.
