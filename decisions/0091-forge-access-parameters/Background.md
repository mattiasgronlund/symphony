# Background — 0091 Forge access parameters, and the credential pair

## Context

Nothing in `VCSX-SPEC.md` can say **where** a forge is. Measured against the working tree at the
revision that carries decision 0090, with `grep -o <term> VCSX-SPEC.md | wc -l` (GNU grep 3.11):

| Term | Occurrences in `VCSX-SPEC.md` |
|------|-------------------------------|
| `endpoint` | 0 |
| `URL` | 0 |
| `URI` | 0 |
| `instance` | 0 |
| `service` | 5 |

Four of the five `service` hits mean "the Symphony service" or "an automation service". The fifth is
Section 11's "the service the credential is presented to travels with the credential on the same
reasoning: the engine runs where both are already held" — a description of ambient context, not a
parameter. It is not a defined term, it is not in Section 8.1's common-argument list, and no Section
9.2 capability signature carries it.

So `forge = "forgejo"` selects a *kind of software* and nothing else. Every Forgejo instance in the
world is the same value to the engine.

**The failure path is concrete and it is already reachable.** Symphony manages a repository on a
self-hosted Forgejo. Its tracker adapter reaches the instance, because `tracker.endpoint` exists and
`SPEC.md` Section 5.3.1 says the `forgejo` adapter "uses the configured Forgejo instance API base".
Its pull requests go through this engine, which receives the forge repository coordinate (decision
0085) and a credential and nothing that names a host. One instance: addressable for issues,
unaddressable for pull requests. A conforming engine must read it from somewhere the specification
does not name, so two conforming engines given the same policy, the same coordinate and the same
credential can reach different instances and both report `create_pr:ok`. That is the conformance
hole decision 0062 closed for the remote, one seam over and still open.

**Decision 0085 decided this deliberately, and the decision is what is being reversed.** Its
Background records that "the service root was settled first, and on a security argument", and its
reasoning section explains what settling it meant: "the credential and the service root stay out of
the argument list, for the reason the report gave for excluding the credential: Section 11 has the
engine run 'where they are already held'". The root was reasoned about and then left implicit. The
argument was sound for what 0085 was deciding — it kept the credential's target from being read out
of the checkout — but "not derived from the checkout" and "not expressible at all" are different
conclusions, and 0085 delivered the second while arguing the first.

**Two parameters, not one, because the plugin layer already has two halves.** Section 9.1 has exactly
three network-touching capabilities (decision 0062: those realizing `push`, `integrate` and `pull`;
every other capability is local to the checkout). Section 9.2 says every forge capability "reaches
the code host, needs a credential… the forge plugin has no local half for an enumeration like Section
9.1's to separate". Two plugins reach the network over two different transports, and their endpoints
are not the same origin: 0085's own Background records that GitHub serves `api.github.com` for the
public host and `<host>/api/v3` for an enterprise one, and that a self-hosted Forgejo can live under
a path prefix. Git access and forge-API access differ by host on one and by path on the other.

**One credential is an assumption that is already false.** `SPEC.md` Section 6.4 states it plainly:
`vcs.api_key` is "the credential for the repository's selected code host", and it is the single value
used for Symphony's clone, for the engine's `push`, and for every forge capability. That holds for a
GitHub personal access token. It does not hold where git access is a deploy key or an SSH credential
and forge access is a scoped API token — different objects, different lifetimes, different rotation.
That arrangement is ordinary rather than exotic, and the surface being designed here is the one a
third backend has to fit into.

## Options considered

- **A — one service root.** A single value naming the forge instance, which is the minimum that
  closes the self-hosted-Forgejo gap. Rejected on the mechanism above: one root cannot express an
  endpoint pair that differs by host on GitHub and by path on GitHub Enterprise, so the first
  deployment that is not github.com needs a second value anyway.
- **B — an opaque per-backend bag only.** The consumer supplies key/values the engine carries to the
  backend without interpreting them; any forge's needs are expressible on day one. Steelmanned: this
  is the most honest expression of "the engine holds it opaque", it needs no core-set growth ever,
  and it puts URI grammar exactly where Sections 9.1/9.2 already keep service-specific knowledge.
  It loses because nothing is then portable: a consumer moving between backends learns each backend's
  key names from that backend's documentation, and a missing endpoint is a first-use `failed` after
  a push rather than something the engine can refuse in advance — the disposition decision 0084
  argues against for `template_unbound`.
- **C — three core parameters**, adding a web base for human-facing links. Rejected as speculation:
  no capability in Section 9.2 returns a URL to a human, and a backend that derives the web base from
  the API base would carry a redundant key. The extension bag in D covers a backend that needs one.
- **D — two core parameters plus an OPTIONAL per-backend extension bag (chosen).**
- **E — one credential, as today.** Steelmanned: it is correct for both currently-implemented forges,
  it is what Symphony ships, and splitting adds a key that nobody configuring GitHub needs. It loses
  on the same ground as A — the surface is the one a third backend fits into — and on the observation
  that the split is not hypothetical but the default wherever git access is a deploy key.
- **F — two credentials with no defaulting.** Rejected: it makes the common case configure the same
  token twice, which is the cost that keeps a correct model from being adopted.

## Decision and reasoning

**D and a defaulted pair.** The consumer supplies a **git-access parameter** and a
**forge-API-access parameter**, and MAY supply an OPTIONAL per-backend extension bag. The consumer
supplies a **git credential** and a **forge credential**, where the forge credential defaults to the
git credential when unset.

**The engine holds all of them opaque**, as it holds the forge repository coordinate (Section 8.1),
the commit identity (Section 10.1) and the base ref (Section 6.4) opaque: it takes them, supplies
them to the backend that uses them, and interprets none. This is not a stylistic echo. Parsing an
endpoint is service-specific — SSH against HTTPS, ports, nested namespaces, path-prefixed instances —
and 0085 already established that a VCS backend has no business knowing a forge's URL grammar, "which
is the mixing Sections 9.1 and 9.2 are separate to prevent". A parameter the engine parses would put
that grammar back in the engine.

**The two core parameters map one-to-one onto the two plugins**, which is what makes them checkable
rather than a guess at what forges need: the git-access parameter is used by exactly the three
capabilities Section 9.1 places on the network, and the forge-API parameter by every capability of
Section 9.2. A reviewer adding a capability has a rule to apply rather than a list to consult.

**The defaulting rule has a cost, recorded so it is not discovered later.** Where an operator sets a
git credential and forgets the forge one, a git credential is presented to an API endpoint. The
endpoint is still the operator's own — the parameters and the credentials come from the same party,
which is the property decision 0092 turns on — so the failure is an authentication refusal from the
forge rather than a credential reaching a host its holder did not choose. The cost is a confusing
401, not an exfiltration. That is why the default is admissible here and would not be if the
parameters could come from anywhere else.

**Ownership is deliberately not settled here.** This decision fixes *what* the values are and *that*
the consumer supplies them, which needs no new machinery: Section 8.1 already carries a
consumer-supplied, engine-opaque value with exactly this shape. *Who* owns them on the consumer's
side, and by what route they reach the engine, is decision 0092. Splitting it this way keeps this
decision re-evaluable on its own — the parameter shape stands whether or not the ownership argument
survives.

## Reconsideration trigger

Promote a bag key to the core set when **two independent backends both require it** — that is the
evidence that it is a property of forges rather than of one forge, and it is recognizable without
re-deriving this decision. Revisit the defaulting rule, not the split, if a backend appears whose git
credential cannot serve as a sensible default for its forge credential in any deployment. Revisit the
opacity rule if the engine is ever required to compare two endpoints for equality, since that is the
first thing that cannot be done without parsing.

Relates to 0085 (which reasoned about the service root and settled it by leaving it ambient; this
decision reverses that half while keeping its "not derived from the checkout" conclusion intact),
0062 (whose two-conforming-engines-disagree argument this reuses), 0073 (whose enumeration of the
network-touching capabilities is what makes the parameter pair map onto the plugin pair), and 0084
(whose refuse-before-publishing argument decides that a missing parameter is a precondition rather
than a first-use failure).
