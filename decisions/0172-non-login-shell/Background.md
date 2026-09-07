# Background — 0172 The launch contract mandates what the environment clause forbids

## Context

Reported from `symphony-rs` as issue #149, against `5a4fdf7`, found while building that repository's
roadmap D5c — by spawning a real child through the real launch path rather than by reading.

Section 9.6 (Agent Sandbox and Execution Isolation) requires the agent's environment to be composed:

> A variable naming a **location outside the run's own workspace** — a build output directory, a
> cache root, a toolchain or interpreter path, a temporary directory — MUST NOT reach the run unless
> the deployment named it deliberately.

Section 10.1 (Launch Contract) mandates the mechanism:

> - Invocation: `bash -lc <codex.command>`

`bash -l` is a login shell. It sources `/etc/profile`, `/etc/profile.d/*.sh` and the user's profile
files, and on many systems `/etc/profile` *assigns* `PATH` rather than appending to it. So a
conforming implementation composes the environment correctly, hands it to `bash`, and `bash`
re-populates part of it before `codex.command` runs.

## The mechanism

**The clause Section 10.1 undoes is stated over construction, and a login shell is a construction
step that runs after Symphony's.** Section 9.6's own nuance says so:

> What this clause fixes is how the environment is **constructed**, not how strongly the sandbox
> contains.

An implementation can therefore satisfy Section 9.6 exactly as written and still hand the agent
variables the deployment did not name. The report's observation that `/etc/profile.d/*.sh` commonly
exports build-tool and language-runtime variables is what takes this past `PATH`: that is precisely
the category Section 9.6 enumerates, and decision 0117 was written from an incident of exactly that
shape — a `CARGO_TARGET_DIR` reaching an agent.

**`-l` is not incidental, and facing why it is there is the cost of removing it.** The report is
careful to say only that the reason is unstated. There is a plausible one: `codex.command` defaults
to `codex app-server`, a bare name resolved through `PATH`, and agent CLIs of this kind are commonly
installed behind a version manager or a per-user prefix that only a profile script puts on `PATH`.
So `-l` may well be what makes the default command resolve at all.

That does not save it, and `symphony-rs` supplied the measurement that turns the argument around.
They have a passing test —
`a_login_shells_own_profile_can_prefix_path_while_the_rest_of_the_composed_set_survives` — that
writes its own `~/.bash_profile` and shows a profile *prefixing* `PATH` ahead of the composed value.
So on a host whose profile assigns `PATH`, `-l` lets that host shadow the composed `PATH`'s `codex`
with a different one. `-l` does not reliably add the version manager's directory; it
non-deterministically overrides a directory the deployment already named. The convenience it was
plausibly there for is not one it delivers.

**The decisive argument is not about the environment at all, and it came from the implementation.**
A login shell's profile is free to write to stdout, and for the Codex adapter that is the same
stdout the app-server protocol stream is parsed from. `symphony-rs` had already closed this hole for
the *glue* shell it composes ahead of a configured wrapper, deliberately making it `sh -c` and never
`sh -l`:

> A login shell here would be a corruption channel, not a convenience. Its `/etc/profile` writes to
> the same stdout `DuplexChild::read_line` parses as the protocol stream, and a frame reader that
> silently ingests a system banner is exactly the corrupt half … refuses.

They could not reach the same conclusion for the agent's own shell, because Section 10.1 mandates
`-lc` there. So a banner-printing profile is a **protocol-framing** defect and not a `PATH`
inconvenience, and that is what makes this a correctness fix rather than a tidy-up. It is also
independent of Section 9.6 entirely: an implementation that never had an environment-composition
requirement would still be wrong to parse a protocol stream a profile can write to.

**The invocation is stated in four places and three of them are the same rule.** Measured at
`0da61d3`:

```
$ grep -n 'bash -lc' SPEC.md
860:  - The runtime launches this command via `bash -lc` in the workspace directory.
2181:  (or a stricter equivalent such as `bash -lc <script>`) is a conforming default.
2881:- Invocation: `bash -lc <codex.command>`
5719:- Launch command uses workspace cwd and invokes `bash -lc <codex.command>`
```

Lines 860, 2881 and 5719 are the agent launch stated in the `codex.command` field documentation, in
Section 10.1, and as a Core Conformance check. All three move together; leaving the Section 17.5
check behind would pin the defect as a conformance requirement.

Line 2181 is not the agent. It is Section 9.4's workspace-hook execution contract, and it is
recorded here as observed and deliberately not changed — see the decision below.

## Options considered

- **Option A — `bash -c`** (the report's first option), with the consequence absorbed: where the
  agent command is resolved by name, the composed set MUST include the search path that resolves it.

  Trade-offs: a deployment whose agent lives behind a version manager must now name that path. That
  is a real obligation where today a profile might supply it by accident, and a deployment that had
  been relying on the accident will find its agent unresolvable until it names the path.

- **Option B — keep `bash -lc` and scope Section 9.6's promise to the shell**, stating that
  profile-sourced variables are outside the guarantee.

  Trade-offs: it costs nothing to adopt and it stops the specification promising something no
  conforming implementation can deliver, which is a genuine improvement over the present pair. It
  loses because it converts a checkable guarantee into one that stops at a boundary a reader cannot
  see, and because Section 9.6's whole design is the opposite move — the prohibition is stated over
  what a variable *names* precisely because a list "would be incomplete before it was written".
  Scoping the guarantee to the shell reintroduces exactly the kind of edge a reader has to know the
  implementation to find. It also does nothing about the stdout channel, which is not an environment
  question.

- **Option C — keep `bash -lc` and require `--noprofile`.**

  Trade-offs: it reaches the same end as Option A and is the smaller textual change if one reads
  `-l` as load-bearing for something. It loses on plainness: `-lc --noprofile` is a flag pair that
  asks a reader to know that the second cancels most of the first, where `-c` simply does not have
  the behaviour. It also leaves `~/.bash_login` and `~/.profile` handling to be reasoned about
  rather than absent.

## Decision and reasoning

**Option A**, and the ordering of its reasons is the implementation's rather than the issue's:
protocol-stream integrity first, environment composition second. The issue is filed as a Section
9.6 conflict, and it is one; but the stronger fact is that Section 10.1 mandates parsing a protocol
stream that a system profile is free to write to, and that is wrong on its own without reference to
Section 9.6.

**On the obligation Option A creates.** Requiring the composed set to name the search path that
resolves the command is not a new kind of burden — it is Section 9.6's existing rule applied to the
one variable the launch contract itself depends on. `symphony-rs` reports this is already their
build's requirement of a deployment, with `PATH` injected by nothing and inherited from nothing, so
the addendum documents existing practice rather than imposing a new one. Their answer to the
blocking question — `codex` resolves under the composed `PATH`, not under the login shell's
assignment — is why this lands as a no-op for the only implementation rather than as a breaking
change.

**On Section 9.4's hook shell, which is not changed.** Line 2181 offers `sh -lc <script>` as a
conforming default for workspace hooks. The environment half of the argument does carry to an
in-sandbox hook half, which runs inside the run's sandbox where Section 9.6's composed set governs;
a login shell there re-populates it exactly as it does for the agent. The stdout half does not carry
at all — a hook's stdout is not a protocol stream.

It is left alone because the host-side half is a different question this decision has no evidence
about. A host-side hook is the operator's own script running with operator authority outside the
sandbox (Section 15.4), and whether the operator's profile *should* reach it is a trust question,
not a composition one. Deciding both halves here would mean guessing at the host-side one to fix the
in-sandbox one. The finding is recorded and given a trigger below instead.

## Reconsideration trigger

Reopen for Section 9.4's hook shell if an in-sandbox hook half is observed receiving a
profile-sourced variable the deployment did not compose — the same defect this decision fixes for
the agent, one execution context over. The evidence would be a hook reading a location outside the
run's workspace that no composed set named. The answer is likely to split the two halves rather than
change the default for both, which is why it wants its own decision.

A second trigger: a deployment that cannot resolve its agent under a composed `PATH` — an agent whose
launcher genuinely requires profile-sourced state beyond a search path, a locale or a shim that only
a profile establishes. Option A assumes the search path is the whole of what `-l` was supplying, and
`symphony-rs` confirms that for one implementation on the hosts it has run on. A counterexample
would mean the launch contract needs a way to name that state deliberately, which is the same move
Section 9.6 already makes and not a reason to restore `-l`.
