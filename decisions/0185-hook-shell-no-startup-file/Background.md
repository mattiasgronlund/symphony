# Background — 0185 A hook cannot decline what runs before its first line

## Context

Reported as issue #172 from `symphony-rs`, against `86a2188`, and settled in that thread at
`b04797e`. `SPEC.md` Section 9.4 (Workspace Hooks) said:

> Execute in a local shell context appropriate to the host OS. On POSIX systems, `sh -lc <script>`
> (or a stricter equivalent such as `bash -lc <script>`) is a conforming default.

Decision 0172 moved Section 10.1's agent launch from `bash -lc` to `bash -c`. It recorded the hook
shell as "the same defect one execution context over", left for its own decision because "the
host-side half being a trust question this one has no evidence about". `symphony-rs` runs `sh -lc`
(`crates/symphony-workspace/src/hooks.rs:147`) because Section 9.4 names it.

## Three arguments in the report that do not hold

- **"No such freedom."** `sh -lc` was "**a** conforming default" of "a local shell context
  appropriate to the host OS", not a mandate. `sh -c` conformed already. That is the real difference
  from Section 10.1, which did mandate the flag.
- **"The same channel."** 0172's decisive argument was framing: a profile writes to the stdout the
  protocol is parsed from. Nothing parses a workspace hook's output. Section 9.4 reads the wait
  status, and Section 15.4 says only that output SHOULD be truncated in logs. `symphony-rs` confirmed
  this is stronger than stated: `classify` (`hooks.rs:162`) matches only `Exited { status, .. }`. A
  banner here is log noise. Their `duplex.rs` test proves a profile runs and prints, on a stream
  parsed in that path and not in this one.
- **The Section 15.4 ladder.** It opens "Repository-owned configuration is trusted by where it is
  sourced from". A host's profile is not repository-owned, so the ladder says nothing about it.

`symphony-rs` agreed with all three.

## What decides it

**1. A script can opt in to a startup file but cannot opt out.** The file runs before the script's
first line, so nothing the author writes can decline it. Under `sh -c`, one line takes it.
Measured with `env -i PATH=/composed:/usr/bin:/bin HOME=<dir>`, where `<dir>/.profile` echoes a
banner, prefixes `PATH` and exports `CARGO_TARGET_DIR`. Debian 13, dash 0.5.12, bash 5.2.37:

| Invocation | Banner | `PATH` | `CARGO_TARGET_DIR` |
|---|---|---|---|
| `sh -lc` | yes | `/profile/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games` | `/from/profile` |
| `bash -lc` | yes | same as `sh -lc` | `/from/profile` |
| `sh -c` | no | `/composed:/usr/bin:/bin` | unset |
| `sh -c '. "$HOME/.profile"; …'` | yes | `/profile/bin:/composed:/usr/bin:/bin` | `/from/profile` |

`symphony-rs` reproduced all four rows on the same versions.

**2. `-l` does not reliably deliver the toolchain it is wanted for.** The one argument for `-l` the
report took seriously was a version manager's toolchain on `PATH`. In rows one and two `/composed` is
gone altogether, because `/etc/profile` assigns `PATH` on this host (lines 5 and 7) rather than
extending it. That happens with no user profile too: `HOME=/nonexistent sh -lc` gives
`/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games`. The last row is what `-l` was hoped to
provide, the version manager's directory on top of the deployment's path, and only the explicit
source produces it.

**3. In-sandbox, the old default sat against a MUST.** An in-sandbox half runs in the run's
sandbox, and Section 9.6 says a variable naming a location outside the workspace "MUST NOT reach the
run" unless the deployment named it. Row one shows `-l` delivering exactly that. To be precise
about the evidence: this is the mechanism on a profile written for the test, not a hook observed in
a deployment, which is what 0172's trigger asked for. `symphony-rs` has not exercised it through
their in-sandbox path, and the decision does not need them to.

**4. Host-side, the reason is different and narrower.** Section 9.6 does not govern the host-side
half, so reasons 2 and 3 do not carry there as stated. What applies:

- The body comes from the policy branch so that a reviewed revision decides what runs. Under `-l`,
  an unreviewed per-host file runs first, so one revision behaves differently from host to host.
- Section 15.4 says trust in a declaration "establishes nothing if the program it names is one the
  agent writes". The sandbox profile is `Implementation-defined`. Under one that leaves the host
  user's profile writable, `-l` would run agent-written code at host authority. A strict profile
  closes that, so this argument is conditional and does not carry the decision alone.

That answers 0172's trust question. `-l` grants no authority the service user lacks; removing it
takes away only an implicit step, and an author who wants the step writes it, in reviewed text.

**5. The clause cited a flag POSIX does not define.** It said "On POSIX systems, `sh -lc`", but the
`sh` page of POSIX.1-2024 (Issue 8) has no `-l` in its synopsis or options; dash accepts it as an
extension. Nor was `bash -lc` "stricter" in any identifiable sense. `symphony-rs` added that, given a
`.bash_profile`, bash reads it and skips `.profile`, where dash reads `.profile`. So the two do not
even read the same files.

## The finding that changed the wording: `BASH_ENV`

The first proposal read "not in a login shell … `sh -c <script>` (or an equivalent such as
`bash -c <script>`)". `symphony-rs` found that `bash -c` is not equivalent: it sources the file
`BASH_ENV` names before the script, which reintroduces exactly what reason 1 argues against. "Not a
login shell" does not catch it, because `bash -c` is not one. Re-measured with
`env -i PATH=/usr/bin:/bin BASH_ENV=<file> ENV=<file2>`, bash 5.2.37 and dash 0.5.12:

| Invocation | Startup file runs ahead of the script |
|---|---|
| `bash -c` | yes (`strace` shows the `openat` of the file) |
| `bash --norc --noprofile -c` | **yes** |
| `dash -c` | no |
| `sh -c`, `sh` being dash | no |
| `/bin/bash` with `argv[0]` of `sh`, `-c` | no |
| `bash --posix -c` | no |
| `bash -c` with `BASH_ENV` unset | no |

The second row matters most: the flags a reader would reach for to rule out startup files do not
rule this one out. Nor is it hypothetical. The measuring host sets `BASH_ENV` in `/etc/environment`,
pointing at a file that exports cache and toolchain locations, the variables Section 9.6 is about.
That host is not a Symphony deployment, so this is not a hook seen misbehaving, but the configuration
is real.

So the clause states the **property** the reasoning depends on: the script is the first thing the
shell runs, with no startup file sourced ahead of it. A login shell is ruled out as a consequence,
and `BASH_ENV` is named so that an implementation using `bash -c` does not have to discover it.
`symphony-rs` preferred this to the smaller alternative, which drops the `bash -c` example and
leaves the gap unstated.

## Why Section 10.1's `bash -c` does not change

The agent's environment is composed (Section 9.6). `BASH_ENV` names a location outside the
workspace, so it cannot reach the run unless the deployment named it deliberately; a sourced
`BASH_ENV` there is the deployment's own choice, which is not the case a profile presents. The same
reasoning covers an in-sandbox hook half. It does not cover the host-side half, because nothing in
the specification composes that half's environment, which is why the property is stated in Section
9.4 itself. The host-side environment stays unstated, as before. Nothing here depends on it,
because the property holds whatever the shell inherits.

## Options considered

- **Keep it a default, change the example to `sh -c`, and leave `-l` conforming.** Steelman: the
  smallest edit, adds no obligation, and breaks no deployment. It loses because a repository's hook
  body has to mean one thing whichever implementation runs it. An author cannot know whether to
  write the source line if the shell may or may not already have sourced the file, and the
  in-sandbox conflict with Section 9.6 would remain.
- **Split the halves, as 0172 predicted: in-sandbox MUST NOT, host-side free.** Steelman: it
  respects that the host-side half has no Section 9.6 argument, and it is the strongest
  alternative. It loses because all the split keeps is a convenience that the measurement above shows
  is unreliable, and it keeps the host-to-host variance. The halves differ in their reasons, but
  not in the answer.
- **The property, for both halves (chosen).**

## The cost

A deployment whose hooks rely on a profile breaks. At `after_create` and `before_run` that is loud,
because the failure is fatal. At `after_run` and `before_remove` it is quiet: a teardown that loses
its tool fails, and Section 9.4 logs and ignores that. `symphony-rs` knows of no hook that depends on
a profile. They can speak only to their own repository, so that is absence of evidence and not a
survey of deployments. Their operator guide carries the loud/quiet warning.

## Decision and reasoning

Section 9.4's shell bullet requires the script to be the first thing the shell runs, with no
startup file sourced ahead of it. That rules out a login shell. `sh -c <script>` is the conforming
default on POSIX systems, and an implementation using `bash -c` MUST keep `BASH_ENV` from reaching
the shell. A note gives the per-half reasons and the one-line opt-in. Section 17.2 checks both halves
against a controlled profile and a controlled `BASH_ENV`, and Section 18.1 carries the item. No
Conformance Statement row is owed, because nothing is `Implementation-defined`. `VCSX-SPEC.md` and
`VCSX-CONTRACT.md` mention no shell, so the engine's units are unaffected.

## Reconsideration trigger

A hook that needs state from a profile that one explicit source line cannot provide, such as
something that holds only when the shell itself is a login shell.
