# Plan — 0185 A hook cannot decline what runs before its first line

## Scope

`SPEC.md`:

- Section 9.4 (Workspace Hooks), the shell bullet and a note;
- Section 17.2 (Workspace Manager and Safety);
- Section 18.1.2 (Broker Core Conformance).

Section 10.1 (Launch Contract) is unchanged; `Background.md` says why. `VCSX-SPEC.md` and
`VCSX-CONTRACT.md` are unchanged.

## Steps

1. **Section 9.4 states the property.** Ensure the execution-contract bullet beginning "Execute in a
   local shell context appropriate to the host OS" says:
   - the script is the first thing the shell runs, and no startup file is sourced ahead of it,
     which rules out a login shell;
   - `sh -c <script>` is a conforming default on POSIX systems;
   - an implementation using `bash -c` MUST ensure `BASH_ENV` does not reach the shell.

   Done when `sh -lc` and `bash -lc` no longer occur in `SPEC.md`, and `BASH_ENV` occurs in Section
   9.4.
2. **Section 9.4 gives the reasons.** Ensure a `Note:` follows the execution-contract list. It
   gives the one-line opt-in, why `-l` does not reliably deliver a toolchain, the in-sandbox reason
   (Section 9.6), and the host-side reason (the policy branch's reviewed revision, Section 15.4).
3. **Section 17.2.** Ensure a check follows the `before_remove` check. It runs each half with a
   controlled profile in `HOME` and a controlled `BASH_ENV`, and asserts that neither ran.
4. **Section 18.1.2.** Ensure an item follows "Both halves of a lifecycle point execute", requiring
   a shell that sources no startup file ahead of the script.

## Cross-cutting sync

- **Section 6.4**: no configuration key changes.
- **Sections 17 and 18**: steps 3 and 4.
- **Conformance Statement template**: no row owed. The requirement is fixed, not
  `Implementation-defined`.

## Anchor changes

None renamed or removed. `BASH_ENV` is a new token in Section 9.4.
