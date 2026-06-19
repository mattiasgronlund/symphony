# Background — 0001 Adopt a decision log

## Context

`SPEC.md` is the primary work product and will be refined incrementally over a long period. Spec
prose records *what* was decided but not *why*. Without a record of the reasoning, a future reader
(human or Claude) cannot tell a deliberate, considered choice from an accident, and any later
re-evaluation has to re-derive the original context from scratch — which is lossy and error-prone.

## Options considered

- **No log; rely on git history and commit messages.** Low overhead, but reasoning is scattered,
  hard to query by topic, and commit messages rarely capture alternatives considered or the state of
  a decision (proposed vs. accepted vs. rejected).
- **A single flat decisions file.** Simple, but mixes the short "what" with the long "why" and has
  nowhere natural to keep an implementation plan or the trail of sessions that worked on it.
- **A log index plus one folder per decision (chosen).** A short chapter per decision in
  `DECISIONS.md` for at-a-glance scanning, backed by a folder with `Background.md`, `Plan.md`, and
  `Sessions.md` for depth. Slightly more structure to maintain, but it separates concerns cleanly and
  supports later re-evaluation.

## Decision and reasoning

Adopt the log-index-plus-folder structure. It keeps the high-level list readable while preserving the
full reasoning, the implementation plan, and the session trail for each decision. The explicit
`State` field makes the lifecycle (proposed → accepted/rejected) visible, which is what enables
revisiting a decision later with its motivation intact.

We would reconsider this if the overhead of maintaining the folders outweighs the value — for
example if decisions become so small and frequent that a flat file would serve better.
