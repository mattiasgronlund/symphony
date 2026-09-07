# Plan — 0167 Did the engine run, and separately, what did it answer

## Scope

`SPEC.md` only. Section 16 (Reference Algorithms (Language-Agnostic)) gains an introductory
paragraph and three of its algorithms change; Section 17.4 (Orchestrator Dispatch, Reconciliation,
and Retry) gains one check; Section 18.1.4 (VCS Engine) has one bullet corrected; Sections 7.1
(Issue Orchestration States), 7.3 (Transition Triggers) and 8.5 (Active Run Reconciliation) record
the new worker-exit site on the side of the claim partition it takes.

No change to Section 14.1 or Section 14.2 — both are correct as written and are the authority the
rest is being brought into line with. No change to `VCSX-SPEC.md` or `VCSX-CONTRACT.md`: nothing new
is required of an engine, only of a caller reading what an engine already reports.

## Steps

1. **Section 16 states the two-layer rule once, before its first algorithm.** Ensure the section
   opens with a short paragraph, ahead of Section 16.1 (Service Startup), stating that every
   `engine.*` dispatch in the section distinguishes an invocation that produced no usable result
   from a conforming result the operation produced: an invocation with no readable result envelope,
   or one whose status reports that the policy did not run, is `engine_invocation_failures`
   (Section 14.1), while a result the policy produced is classified by the operation's own domain.
   The paragraph restates no requirement — it names where Section 14.1 class 7's boundary applies —
   and cites `VCSX-SPEC.md` Section 8.2 (Result Envelope) and Section 8.3 (Exit Codes) for the
   status and exit-code mapping that makes the distinction total.
   Done when a paragraph between the Section 16 heading and the Section 16.1 heading names both
   layers and cites class 7.

2. **`ensure_object_store`'s comment is two-armed.** Ensure the `if result failed:` comment in
   Section 16.5 (Ensure Repository Object Store) distinguishes a conforming provisioning result
   reporting failure — `repository_provisioning_failures` — from an invocation that produced no
   usable result, which is `engine_invocation_failures`, and ensure the returned error carries which
   of the two it is so its caller can dispose of it.
   Done when the pseudocode block names both classes and the comment no longer labels every failure
   with one.

3. **`dispatch_issue` disposes of both classes.** Ensure the `if store failed:` branch in Section
   16.4 (Dispatch One Issue) no longer asserts a repo-scoped disposition for every failure
   `ensure_object_store` can return: it names both classes, defers each to Section 14.2, and keeps
   its existing behaviour of writing no entry, arming no retry, and leaving the issue unclaimed —
   which is the disposition both classes share at this site.
   Done when the branch's comment names `engine_invocation_failures` alongside
   `repository_provisioning_failures` and cites Section 14.2 for the disposition of each.

4. **`engine.integrate` has a failure arm for an invocation that produced no usable result.** Ensure
   Section 16.6 (Worker Attempt (Workspace + Prompt + Agent)) binds the result of
   `engine.integrate` and branches on it: an invocation with no readable result envelope, or one
   reporting that the policy did not run, ends the attempt; a conforming result reporting a merge
   conflict is postponed exactly as today, with no `fail_worker` and no change to the
   resolved-later-only-if-a-push-is-rejected behaviour. Ensure the comment says which arm is which,
   so the remaining asymmetry reads as a decision rather than an oversight.
   Done when the block contains a branch on the invocation and the conflict path is unchanged.

5. **The new arm ends the run on the releasing side of the claim partition.** Ensure the exit that
   step 4 takes is distinct from `fail_worker`, and that `on_worker_exit` in Section 16.7 (Worker
   Exit and Retry Handling) routes it by removing the running entry, adding the run's runtime to the
   totals, releasing the claim, and arming no retry — rather than through `schedule_retry`, whose
   exponential per-worker backoff Section 14.2 forbids for this class. Ensure the comment cites
   Section 14.2 for why the retry belongs to the repository or the instance rather than to this
   worker.
   Done when `on_worker_exit` has three arms, the new one calls no `schedule_retry`, and the
   comment names the class.

6. **Section 7.1's `Released` list names the new producer.** Ensure the `Released` entry's list of
   causes gains the engine-invocation worker exit, in the shape its neighbours use — the cause, then
   the site in Section 16 that produces it.
   Done when the `Released` bullet list names `on_worker_exit` for this cause.

7. **Section 7.3's `Worker Exit (abnormal)` trigger records the exception.** Ensure the trigger no
   longer reads as though every abnormal exit schedules an exponential-backoff retry: an exit
   carrying `engine_invocation_failures` removes the entry, updates totals, releases the claim, and
   schedules none.
   Done when the trigger's bullets name the exception.

8. **Section 8.5's claim partition names the new site's side.** Ensure the `on_worker_exit` bullet
   of the partition list no longer says that site always arms a retry: it releases the claim for an
   engine-invocation exit and arms a retry otherwise, and either way is on one side of the
   partition. This is the obligation Section 8.5 states for a site added later.
   Done when the `on_worker_exit` bullet names both arms.

9. **Section 17.4 gains a check for Section 14.2's instance-wide clause.** Ensure a `Daemon
   Conformance` check asserts that in an instance managing two repositories that both require an
   engine, an unavailable or non-conforming engine suppresses new dispatches for **both** rather
   than only the one whose dispatch discovered it, while a repository provisioning failure — the
   engine having run and reported — suppresses only the affected repository and leaves the second
   dispatching. The check cites Sections 14.1, 14.2 and 16.5.
   Done when Section 17.4 contains a check pairing the two classes and
   `awk '/^## 17\. /,/^## 18\. /' SPEC.md | grep -c -i 'every repository'` is no longer `0`.

10. **Section 18.1.4's engine bullet stops claiming the narrow scope for the wide condition.**
    Ensure the bullet that classifies a below-floor refusal, an unavailable or non-conforming
    engine, and a usage/configuration result as `engine_invocation_failures` states the two
    dispositions Section 14.2 gives them rather than one: repo-scoped for the repository-declared
    causes, and dispatch suppressed for every repository requiring an engine where the engine itself
    is unavailable or non-conforming.
    Done when the bullet no longer reads `recovered repo-scoped per Section 14.2` for the
    unavailable case.

## Cross-cutting sync

- **Section 6.4 (Configuration Cheat Sheet)** — unaffected. This decision adds, removes and renames
  no configuration key.
- **Section 17 (Test and Validation Matrix)** — step 9.
- **Section 18 (Implementation Checklist (Definition of Done))** — step 10.
- **`VCSX-SPEC.md` Sections 13.1–13.3** — unaffected. The engine's obligations are unchanged; this
  decision only makes a caller read what Section 8.2 and Section 8.3 there already require an engine
  to report.
- **Conformance Statement templates** — no row is owed. This decision introduces no
  `Implementation-defined` value and no MUST-document obligation. The two rows Section 14.2's engine
  dispositions already own in `CONFORMANCE-STATEMENT-TEMPLATE.md` — the persistent park-versus-retry
  choice and the unusable-policy per-repository backoff schedule — are unchanged in substance and
  need no edit.
- **Conformance corpus** — no vector added, deliberately. The reason and the trigger that would
  reverse it are in `Background.md` under the reconsideration trigger.

## Anchor changes

- `log_provisioning_error` → `log_object_store_failure` (Section 16.4, Dispatch One Issue). Renamed
  under step 3: the site now receives either of two classes, and one of them — an engine that could
  not be invoked, or a credential the secret provider could not resolve — is not a provisioning
  result. The function logs a failure of `ensure_object_store`, which is what the new name says.

No section is retitled and nothing is removed. Three tokens are new rather than renamed:
`engine_invocation_error` (Section 16.5), `fail_engine_invocation` (Sections 16.6, 16.7), and the
`engine_invocation_failures` worker-exit reason `on_worker_exit` branches on (Section 16.7).

## Status

Applied to `SPEC.md`: Sections 7.1, 7.3, 8.5, the Section 16 preamble, 16.4, 16.5, 16.6, 16.7, 17.4
and 18.1.4. All ten steps.
