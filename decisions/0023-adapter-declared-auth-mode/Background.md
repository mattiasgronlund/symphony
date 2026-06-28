# Background — 0023 Adapter-declared auth mode

## Context

The spec hardwires every tracker as a remote, credentialed API: `tracker.api_key` is resolved through the
secret provider (Section 5.3.1, Section 15.3), dispatch preflight **hard-requires it present** (Section 6.3:
"`tracker.api_key` is present after `$` resolution"), `tracker.endpoint` assumes a network API base, and the
broker performs writes "using Symphony's configured tracker auth" (Section 11.5). A missing key is
`missing_tracker_api_key` (Section 11.4).

The 22-fork sweep (`adapter-layer-fork-evidence` memory) found local backends that do not fit, in two
different ways:

- **Local `td` (SQLite)** — *no-auth*: no API key, no endpoint; access is filesystem permission. It fails
  Section 6.3 preflight outright, and `endpoint` is meaningless. The fork's own config still defaulted to the
  Linear endpoint and `LINEAR_API_KEY` despite needing neither.
- **Self-owned Postgres (PitchAI)** — *credentialed but not token+endpoint*: it needs a connection-string
  secret (a DSN with a password), not an `api_key` + `endpoint`. The secret model fits; the `api_key`/
  `endpoint` *shape* does not.

So the spec conflates two separable things — *does the adapter need a secret at all* and *what shape is the
connection* — and the "api_key always required" rule is really a Linear/Forgejo-ism. The standing memory
finding was to model auth as an adapter-declared property rather than a baked-in assumption.

Important boundary nuance: a no-auth adapter does **not** dissolve the broker. The broker (decision 0003)
enforces both confidentiality (credentials out of the sandbox) and scope (write only to the assigned issue).
For a local adapter, confidentiality is moot but scope and host-side isolation still require the broker to
perform the write — provided the local store is host-side. If the store lived *inside* the bind-mounted
workspace, the sandboxed agent could write it directly and bypass the broker, breaking decision 0008's
"Symphony owns tracker writes".

## Options considered

- **Adapter-declared auth mode (chosen).** The adapter declares whether it needs a secret; `api_key`/
  `endpoint` and the secret provider apply only then. Generalizes the self-describing fork pattern
  (jialinyi94's `validate_config`/`secret_env_var`) and the capability-descriptor precedent (decision 0018),
  and admits both local cases without a special backend.
- **A dedicated `local` tracker kind.** A special no-auth/local kind with file/DB transport. Narrower; it
  special-cases one backend instead of removing the hardcoded auth assumption, and would not cleanly cover
  the DSN-credentialed case.
- **Defer.** Capture only.

## Decision and reasoning

Each tracker adapter declares its **auth mode** as part of its capability descriptor (Section 11.7):

- `secret` — a credential resolved through the secret provider (Section 15.3). The credential is whatever the
  adapter needs (an API token, a connection string); `tracker.api_key` carries it and `tracker.endpoint` is
  adapter-specific.
- `none` — no credential; the adapter reaches a host-side store such as a local file or database. `api_key`
  and `endpoint` do not apply.

`tracker.api_key` and `tracker.endpoint` apply only to `secret`-mode adapters, and dispatch preflight
(Section 6.3) requires `tracker.api_key` only then. The broker still mediates tracker writes for scope and
isolation even when the adapter has no credential; a local adapter's store MUST be host-side (outside the
bind-mounted workspace) so the agent cannot bypass the broker. `linear` and `forgejo` are `secret`-mode; a
`none`-mode adapter is admissible as an OPTIONAL extension (core defines no `none`-mode backend).

Reasoning: this makes "needs a secret" an adapter-declared datum — the same "requirement is adapter-declared
DATA" philosophy already adopted for write capability (decision 0018) — removing the Linear/Forgejo-shaped
assumption from the core, and admits both the no-auth and DSN-credentialed local backends without inventing a
special kind. The broker boundary is preserved: only its credential aspect goes degenerate.

Problems to watch: `api_key` is a token-flavoured name for what is really "the adapter's credential" (a
`secret`-mode DSN reuses it) and `endpoint` is unused for some adapters — a neutral rename could clean this up
later but is out of scope here. The host-side-store requirement is the load-bearing condition for a local
adapter. The auth-mode concept could generalize to the VCS/forge adapters (a local/file git remote), but this
decision scopes it to the tracker.

## Re-evaluation — refined by 0029 (2026-06-28); stays Accepted

This decision **remains Accepted** and its auth-mode mechanism is unchanged. Decision 0029 refines the
secret model this decision builds on (Section 15.3): it splits the broker's secret handling into
**outward credentials** (broker-mediated — the isolation invariant; the `secret`-mode credential this
decision resolves through the secret provider is one) and **repo-internal integrity values**
(repo-owned, supplied to a host-side hook's environment, not broker-mediated — e.g. the gate-cache
HMAC). Nothing here becomes false: `secret`/`none` auth modes and the secret-provider consultation are
exactly as decided; 0029 only adds a sibling category for non-credential integrity values. See 0029
for the taxonomy.
