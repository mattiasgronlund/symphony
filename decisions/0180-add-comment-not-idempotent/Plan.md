# Plan — 0180 `add_comment` is not idempotent, and the key a caller keeps has a recovery class

## Scope

`SPEC.md` Section 11.8 (State Transition Write Semantics), Section 9.7 (Repository Provisioning and
the VCS Engine) (the comment bullet), Section 14.3 (State Recovery Classes), Section 17.3 (Issue
Tracker Client) and Section 18.1.2 (Broker Core Conformance). `CONFORMANCE-STATEMENT-TEMPLATE.md`'s state
table.

## Steps

1. **Section 11.8 states `add_comment`'s repeat semantics.** Ensure a paragraph after the `set_state`
   bullets (and before "A `set_state` failure is logged") says that:
   - `add_comment` is not idempotent, and each successful call is a new comment;
   - an adapter MUST NOT re-send a comment write whose outcome it could not determine and report the
     result as one write, where "could not determine" means any failure after the request may have
     reached the tracker (a transport timeout, or a connection lost after sending) and excludes a
     definite refusal from the tracker;
   - a caller needing at-most-once keeps its own key and MUST NOT release that key on an outcome
     that could not be determined.
   Done when Section 11.8 contains that paragraph.

2. **Section 9.7's comment bullet names its key's class.** Ensure the bullet beginning "SHOULD
   comment on the issue" says that the (issue, target) record is runtime state whose recovery class
   is documented (Section 14.3), and that an outcome that could not be determined counts as written
   (Section 11.8). Done when the bullet cites Sections 11.8 and 14.3.

3. **Section 14.3's note lists the record.** Ensure the note beginning "the enumeration in Section
   4.1.8 is not closed" names the Section 9.7 (issue, target) comment record among the cases this
   document creates today, that it says the record cannot be `Reconstructable` because no read
   returns comments, and that as `Ephemeral` its reset consequence is one repeated comment per
   restart. Done when the note names it.

4. **Section 17.3 and Section 18.1.2 check it.** Ensure Section 17.3 has a check that an
   `add_comment` whose outcome could not be determined is not re-sent by the adapter. Ensure the
   Section 18.1.2 item naming `set_state` idempotency also states `add_comment`'s rule. Done when
   both contain it.

5. **The template carries the class.** Ensure `CONFORMANCE-STATEMENT-TEMPLATE.md`'s state table has
   a row for the Section 9.7 refusal-comment record, with `Ephemeral` or `Durable` as the spec
   default and the reset consequence column filled for `Ephemeral`. Done when the row exists.

## Cross-cutting sync

- Section 6.4: unaffected.
- Section 17: step 4. Section 18: step 4.
- Conformance Statement templates: step 5.
- `conformance/`: unaffected; adapter resend behavior is not a host-independent function.

## Anchor changes

None.

## Status

Applied, all steps, in the same pull request as decisions 0177–0182 (issues #173–#178).
