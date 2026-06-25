# Plan — 0022 Forge adapter surface

## Scope

Splits the single VCS adapter (Section 9.7) into a VCS (git-remote) contract and a new Forge (code-host
collaboration) contract. Moves pull-request content and verbs out of Section 9.9 into a new Section 9.10,
adds OPTIONAL review-thread writes and a forge capability descriptor, and reconciles `link_pull_request`
(Sections 11.1/11.5/11.7). Syncs Section 17.2 and Section 18. Refines decisions 0007 and 0008. No new config
field: the forge reuses `vcs.kind`/`vcs.api_key`.

## Steps

1. In Section 9.7, ensure the VCS adapter is described as backing the broker's **git** verbs (Section 9.9)
   and that pull-request and review operations go through the Forge adapter (Section 9.10). Done when
   Section 9.7 no longer claims the VCS adapter backs pull-request verbs.

2. In Section 9.8, ensure the remote-operation list is git-only (fetch, branch, back-merge, push) and that
   pull-request/review operations are attributed to the Forge adapter (Section 9.10). Done when "pull-request
   management" is no longer listed among the VCS adapter's remote operations.

3. Retitle Section 9.9 "Pull Requests and Broker Git/PR Verbs" to "Broker Git Verbs" and reduce its verbs to
   the git core (`push`, `back-merge`) with reason codes `non_fast_forward`/`scope_denied`; move the
   pull-request model and the `pr`/`request-merge` verbs to Section 9.10. Done when Section 9.9 lists only
   git verbs.

4. Ensure a Section 9.10 "Forge Adapter, Pull Requests, and Review Writes" exists defining: the Forge
   adapter (`github`, `forgejo`) on the same code host as the VCS adapter, reusing `vcs.kind`/`vcs.api_key`;
   the one-pull-request-per-issue model; the issue-link reconciliation (forge-native same-platform vs
   `link_pull_request` cross-system); OPTIONAL review-thread writes (post/reply/resolve); the forge verbs
   (`pr`, `request-merge`, review writes) with reason codes; and a static forge capability descriptor (PR
   create/update REQUIRED, review-thread writes OPTIONAL). Done when Section 9.10 defines the Forge adapter
   with those parts.

5. In Section 11.5, ensure `link_pull_request` is described as recording a pull-request reference on the
   tracker item — the cross-system mechanism (Section 9.10) — and that a same-platform tracker MAY declare it
   unsupported (Section 11.7). In Section 11.7, ensure the `link_pull_request` capability example notes the
   forge-native case. Done when both reflect the reconciliation.

6. Cross-cutting sync of Section 17.2 and Section 18 (see below).

## Cross-cutting sync

- Section 17.2: change the "Symphony performs fetch/branch/back-merge/push/PR" row to attribute git to the
  VCS adapter and PR/review writes to the Forge adapter, and add a row that the Forge adapter advertises a
  capability descriptor with OPTIONAL review-thread writes.
- Section 18 checklist: split the VCS-adapter bullet into a VCS (git-remote) bullet and a new Forge-adapter
  bullet (one-PR-per-issue + OPTIONAL review-thread writes + forge capability descriptor).
- Section 6.4 cheat sheet: no change (the forge reuses the `vcs` config block).

## Anchor changes

- Section 9.9 "Pull Requests and Broker Git/PR Verbs" — retitled to "Broker Git Verbs"; the `pr` and
  `request-merge` broker verbs move to Section 9.10.
- New anchors: Section 9.10 "Forge Adapter, Pull Requests, and Review Writes"; the Forge adapter
  (`github`, `forgejo`); the review-thread write operations (post review comment, reply to thread, resolve
  thread); the forge capability descriptor.
- `link_pull_request` is unchanged as a name; its semantics are clarified as the cross-system link mechanism.

## Status

Applied to `SPEC.md`.
