# Background — 0117 The sandbox is stated over secrets, and the damage came from something else

## Context

Issue #62's environment item: the sandbox MUST neutralise ambient environment that leaks across
worktree and session boundaries — "an inherited build-target-dir, a cross-checkout virtualenv
shebang" — "rather than letting a session act on a sibling's config". The study records two
concrete instances: an inherited `CARGO_TARGET_DIR` causing a build against the wrong tree, and a
`.venv` shebang running a sibling checkout's interpreter.

## What Section 9.6 actually guarantees

It guarantees a great deal about secrets and almost nothing about anything else.

> No credentials are present inside the sandbox. Every secret-bearing environment variable MUST be
> scrubbed before the sandbox starts (Section 15.3).

That is precise, checkable, and about exactly one class of variable. Every other variable in the
orchestrator's environment is inherited by default, because nothing says otherwise — the section
describes containment from the *host* and from Symphony's *credentials*, and treats the rest of the
environment as unremarkable.

The result is that environment isolation is **assumed via the sandbox** rather than stated as a
guarantee, which is how the study describes it. And the assumption is doing real work: a reader who
believes the sandbox isolates the agent would reasonably believe it isolates the agent's
environment, when what the specification requires is that it isolates the agent's access to
credentials and the host filesystem.

## Why the failure is not a sandbox escape

This is the part worth being careful about, because it decides where the fix goes.

`CARGO_TARGET_DIR` pointing at a sibling worktree's build directory is not a containment failure. The
sandbox did what it was configured to do; the variable was legitimately inherited, the path it names
is legitimately reachable, and the agent legitimately used it. Every component behaved correctly and
the outcome was a session compiling into another session's tree.

The same is true of the interpreter case: a `.venv` shebang is an absolute path recorded at
virtualenv-creation time, so a script copied or shared between checkouts runs an interpreter
belonging to a checkout the session has nothing to do with. No boundary was crossed that anybody
declared.

So the requirement is not "strengthen the sandbox". It is that the environment a run is given must
be **constructed** rather than **inherited** — the difference between a set of variables someone
chose and a set of variables that happened to be present in whatever shell started the orchestrator.

That framing also explains why concurrency makes it visible rather than causing it. A single-session
deployment with an inherited `CARGO_TARGET_DIR` builds into a directory it did not intend too; there
is simply no sibling for the mistake to collide with, so nothing surfaces.

## What the rule is

The run's environment is constructed:

- The agent's environment is composed from what the run needs, not inherited wholesale from the
  orchestrator's process. Variables the deployment intends are passed explicitly.
- Variables that name a **location outside the run's own workspace** — a build output directory, a
  cache root, a toolchain or interpreter path, a temporary directory — MUST NOT reach the run
  unless the deployment named them deliberately. That is the class the observed failures come from,
  and it is stated as a class rather than as a list, because the list is per-ecosystem and would be
  obsolete before it was complete.
- Where the run needs such a location, it resolves inside the run's workspace (Section 9.1) so two
  concurrent runs cannot name the same one.
- The composed set is `Implementation-defined` and MUST be documented, which is the disposition
  Section 9.6 already gives the sandbox profile and the egress policy. This specification cannot
  enumerate every ecosystem's variables and does not try; what it fixes is that a deployment can say
  what its agents get.

The prohibition is stated over what a variable *names* rather than over a list of variable names,
which is the only form that survives contact with a new toolchain. An implementation checking this
has a test it can write: start a run with a poisoned `CARGO_TARGET_DIR` and assert the agent does not
see it.

## Why Core, and what it costs

Nothing, on this slice's test. Composing an environment rather than inheriting one is the same
amount of work at startup — a deployment already scrubs secret-bearing variables before the sandbox
starts (Section 15.3), so it is already filtering the environment; this changes the filter from a
denylist of secrets to an explicit set.

And the protection is not concurrency-specific, per the argument above: a single-session deployment
building into an unintended directory is the same defect with nothing to collide with. A requirement
that is free and prevents a session acting on another's configuration belongs in Core, on the same
reasoning that put 0113 and 0114 there.

## Steelmanning the alternative

The argument for leaving it is that this is the sandbox's job and the specification already delegates
the sandbox profile as `Implementation-defined` with a documentation obligation — so a deployment
that wants environment isolation configures it, and adding a clause duplicates a knob that exists.

It loses on what the delegation actually says. Section 9.6 delegates the *profile* and names one
baseline; nothing in that delegation implies environment construction, and a conforming
implementation using the named baseline inherits the environment. A knob nobody is told to turn, for
a property the specification never claims, is not a delegation — it is a gap with an
`Implementation-defined` label nearby.

## Reconsideration trigger

Reconsider if the class-based prohibition proves unenforceable — if implementations diverge on what
"names a location outside the run's workspace" covers, and two conforming deployments pass different
variables through. The repair would be a named baseline set per ecosystem, published beside the
specification rather than inside it, which is the shape the token registry already takes.

## Relationship to other decisions

It is the third of this slice's three free-and-Core rules, beside 0113's liveness evidence and
0114's identity re-verification. All three share the property that concurrency reveals them rather
than causes them.
