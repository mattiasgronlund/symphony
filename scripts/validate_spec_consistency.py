#!/usr/bin/env python3
"""Check the artifacts derived from SPEC.md, VCSX-SPEC.md and VCSX-CONTRACT.md against the
enumerations that govern them.

Checks 1 to 4 each correspond to a defect found by hand in decision 0132, where the same shape had
been found by a person reading for the fourth time: a specification sentence enumerates something,
a second artifact restates that enumeration, the two disagree, and nothing notices because each
artifact is complete against itself. Check 5 was added by decision 0133, whose two issues were the
same shape again with no registry involved — one prose sentence enumerating what other prose
establishes. Check 6 was added by decision 0134, whose defect ran the direction check 4 cannot see:
`VCSX-SPEC.md` Section 4.1 defines `load_policy` as an operation and the engine registry published
ten operations without it.

Checks:

  1. Section references resolve, within a document and across the three.
  2. Every section carrying an `Implementation-defined` or "MUST document" obligation has at least
     one row in the matching Conformance Statement template.
  3. A config key is spelled in the namespace its defining section fixes.
  4. Every token a registry publishes occurs in the document that governs it.
  5. The await enumeration: every await parameter is named where VCSX-SPEC.md fixes the set and in
     the engine registry, and VCSX-SPEC.md and VCSX-CONTRACT.md state the same number of terminal
     conditions for `await_checks`.
  6. Both directions over the groups whose membership the prose closes: every token the governing
     section enumerates occurs in the registry, and every token the group publishes is enumerated
     there. The second direction is what check 4 cannot see — that check reads the whole corpus, so
     a token the prose spells anywhere passes whether or not the section the group cites is where.

Five limits are deliberate and stated here rather than left to be discovered:

  * Check 2 matches per *section*, not per obligation. A section with three obligations and two
    rows is reported as a shortfall; a section with one obligation and one row that answers a
    different question passes. Only a zero-row section is an error, because the counts legitimately
    differ in at least one place — Section 14.2's node-provisioning obligation is rowed under the
    extension's own section 9.11 — so a strict count would fail a correct tree.
  * Check 4 is a substring test, which is what a registry-versus-prose comparison can honestly do.
    It under-reports: `parent` occurs in VCSX-SPEC.md as an English word ("re-parents a commit"), so
    a field named `parent` passes whether or not the document fixes it as a token.
  * Check 5 carries one set and one count, spelled here rather than derived. It catches a parameter
    or a condition dropped from one artifact and not the other, which is the drift decision 0133
    repaired; it cannot catch a set that grows in both artifacts and leaves this constant behind,
    and it says nothing about what any parameter or condition *means*. A parameter added to
    VCSX-SPEC.md without being added here passes.
  * Check 6 runs over a table of four groups rather than over every group, because closedness is a
    property of the prose that no general rule reads off it: a group this table does not name is
    unchecked in both directions, as every group was before decision 0134.
  * The `arguments` group is read from Section 8.1's argument bullets, which is that section's
    enumeration of the arguments it names. It is not the whole of the section's argument surface:
    the forge repository coordinate, the two identities and the execution context are named there
    in prose and carry no token, so nothing here can check them.

Run from the repository root. Exit 0 if no error, 1 otherwise; warnings are printed either way.
"""

import json
import os
import re
import sys

DOCS = ["SPEC.md", "VCSX-SPEC.md", "VCSX-CONTRACT.md"]

TEMPLATES = {
    "SPEC.md": "CONFORMANCE-STATEMENT-TEMPLATE.md",
    "VCSX-SPEC.md": "VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md",
}

REGISTRIES = {
    "conformance/vocabulary.json": ["SPEC.md"],
    "conformance/vcsx/vocabulary.json": ["VCSX-SPEC.md", "VCSX-CONTRACT.md"],
}

# Sections that restate obligations rather than impose them: the definition of the term, and the
# Conformance Statement section itself, which exists to gather the others.
OBLIGATION_EXEMPT_TITLES = ("Normative Language", "Conformance Statement")
OBLIGATION_EXEMPT_SECTIONS = {
    "SPEC.md": {"6.4", "17", "17.4", "18", "18.1", "18.1.1", "19"},
    "VCSX-SPEC.md": {"13.1", "13.2", "13.3"},
}

# Section 5.3.4 fixes these two namespaces and says why: prefixing is what keeps a lifecycle point
# and a named unit of the same name from colliding.
NAMESPACE_RULES = {"hooks": ("hooks.workspace.", "hooks.engine.")}

# The groups whose membership the governing prose closes, and where check 6 reads that membership
# from: the registry group, the document, the sections that fix it, the pattern that spells a token
# there, and an OPTIONAL region pattern narrowing the section body before the token pattern runs.
# Section 4.1 lists the operations as column-0 bullets and both sections write the lifecycle
# positions as `before:<op>` literals, so neither needs a region. Section 8.1 spells hundreds of
# other tokens, so `entry_points` is read from its opening enumeration alone (decision 0141: that
# group carried thirteen entries citing a section that named ten, and nothing compared them), and
# `arguments` from that section's own argument bullets (decision 0142).
CLOSED_GROUPS = {
    "conformance/vcsx/vocabulary.json": {
        "operations": ("VCSX-SPEC.md", ("4.1",), r"^- `([a-z_]+)` —", None),
        "lifecycle_positions": ("VCSX-SPEC.md", ("4.1", "5.1"), r"`(before:[a-z_]+)`", None),
        "entry_points": ("VCSX-SPEC.md", ("8.1",), r"`([a-z_]+)`",
                         r"The entry points are[^\n]*:\n\n((?:(?:- |  )[^\n]*\n)+)"),
        "arguments": ("VCSX-SPEC.md", ("8.1",), r"^- `([a-z_]+)`(?: \(OPTIONAL\))? — ", None),
    },
}

# VCSX-SPEC.md Section 8.1 fixes the await parameters and Section 4.1 the terminal conditions the
# operation exits at; VCSX-CONTRACT.md Section 6 restates the count. Decision 0133 repaired the
# drift between them.
AWAIT_PARAMETERS = ("await_bound_ms", "await_max_reads", "await_interval_ms", "await_budget_floor")
AWAIT_TERMINAL_CONDITIONS = 5
AWAIT_COUNT_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}

errors = []
warnings = []


def error(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def headings(text):
    """Section number -> title, for every numbered heading."""
    out = {}
    for line in text.split("\n"):
        m = re.match(r"^#{2,5}\s+([0-9]+(?:\.[0-9]+)*)\.?\s+(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def section_at(text, offset):
    """The (number, title) of the numbered heading a given offset falls under."""
    cur = (None, None)
    for m in re.finditer(r"^#{2,5}\s+([0-9]+(?:\.[0-9]+)*)\.?\s+(.*)$", text, re.M):
        if m.start() > offset:
            break
        cur = (m.group(1), m.group(2).strip())
    return cur


def numbers_in(group):
    return re.findall(r"[0-9]+(?:\.[0-9]+)*", group)


# --------------------------------------------------------------------------- check 1

def check_references(texts, heads):
    ref_group = r"[0-9]+(?:\.[0-9]+)*(?:\s*(?:,|and|/)\s*[0-9]+(?:\.[0-9]+)*)*"
    cross = re.compile(r"`(SPEC|VCSX-SPEC|VCSX-CONTRACT)\.md`[,]?\s+Sections?\s+(" + ref_group + ")")
    plain = re.compile(r"Sections?\s+(" + ref_group + ")")

    for doc in DOCS:
        text = texts[doc]
        flat = text.replace("\n", " ")
        claimed = set()

        for m in cross.finditer(flat):
            target = m.group(1) + ".md"
            for n in numbers_in(m.group(2)):
                claimed.add(m.start())
                if n not in heads[target]:
                    error(f"{doc}:{line_of(text, m.start())}: reference to {target} Section {n}, "
                          f"which that document does not have")

        for m in plain.finditer(flat):
            # Skip the number groups already consumed by a cross-document reference, and citations
            # of an external standard.
            if any(abs(m.start() - c) < 60 for c in claimed):
                continue
            if "Unicode" in flat[max(0, m.start() - 90):m.start()]:
                continue
            for n in numbers_in(m.group(1)):
                if n not in heads[doc]:
                    error(f"{doc}:{line_of(text, m.start())}: reference to Section {n}, "
                          f"which this document does not have")


# --------------------------------------------------------------------------- check 2

def blank_fenced(text):
    """`text` with every fenced block's content replaced by spaces, preserving every offset.

    An obligation inside a fence is a restatement by construction: a worked example repeats what the
    prose beside it already requires, and counting both makes one obligation two. Newlines are kept
    so line and section arithmetic over the result still holds.
    """
    out = list(text)
    for m in re.finditer(r"^```.*?^```", text, re.M | re.S):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def extension_home(text, offset):
    """The section an enclosing extension bullet attributes its obligation to, or None.

    An obligation nested under `- … (…; OPTIONAL extension, Section N.M):` is the extension's, and
    the template rows it under the extension's own section rather than under the section whose prose
    happens to carry it. Re-homing keeps `covers()` matching downward only; aliasing would loosen it
    for every section.
    """
    start = text.rfind("\n- ", 0, offset)
    if start == -1 or "\n\n" in text[start + 1:offset]:
        return None
    line = text[start + 1: text.find("\n", start + 1)]
    m = re.match(r"- .*?OPTIONAL extension, Sections? ([0-9]+(?:\.[0-9]+)*)", line)
    return m.group(1) if m else None


def obligation_sentences(doc, text):
    """Distinct obligation sentences, grouped by the section that answers for them."""
    marker = re.compile(r"`Implementation-defined`|Implementation-defined|MUST document|"
                        r"MUST be documented")
    scanned = blank_fenced(text)
    flat = scanned.replace("\n", " ")
    by_section = {}
    for m in marker.finditer(flat):
        start = flat.rfind(".", 0, max(0, m.start() - 1)) + 1
        end = flat.find(".", m.end())
        sentence = flat[start:end if end != -1 else len(flat)].strip()
        # `flat` swaps each newline for one space, so offsets map 1:1 onto `text`.
        num, title = section_at(text, m.start())
        if title and any(t in title for t in OBLIGATION_EXEMPT_TITLES):
            continue
        num = extension_home(text, m.start()) or num
        if num in OBLIGATION_EXEMPT_SECTIONS.get(doc, set()):
            continue
        if num is None:
            continue
        by_section.setdefault(num, set()).add(sentence)
    return by_section


def template_rows(path):
    """Section number -> how many places in the template answer for it.

    Two shapes count. An obligation row cites its section in the second column. A whole subsection
    answers an obligation that admits many values — the reason-token tables, whose headings read
    `### 4.1 Operation Reasons (Section 4.3)` — and counts as one answer for the section it names.
    """
    counts = {}
    text = read(path)
    for line in text.split("\n"):
        if not line.startswith("|") or line.startswith("|--"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("Obligation", "State field", "Extension", "Backend"):
            continue
        for n in re.findall(r"[0-9]+(?:\.[0-9x]+)*", cells[1]):
            counts[n.replace(".x", "")] = counts.get(n.replace(".x", ""), 0) + 1
    for m in re.finditer(r"^#{2,4}\s+.*?\(Sections?\s+([0-9., and]+)\)", text, re.M):
        for n in numbers_in(m.group(1)):
            counts[n] = counts.get(n, 0) + 1
    return counts


def covers(row_section, obligation_section):
    """A row citing Section 11 answers for an obligation in Section 11.2."""
    return (obligation_section == row_section
            or obligation_section.startswith(row_section + "."))


def check_obligations(texts):
    for doc, template in TEMPLATES.items():
        rows = template_rows(template)
        for num, sentences in sorted(obligation_sentences(doc, texts[doc]).items()):
            have = sum(c for sec, c in rows.items() if covers(sec, num))
            if have == 0:
                error(f"{doc} Section {num}: {len(sentences)} obligation(s) and no row in "
                      f"{template}")
            elif have < len(sentences):
                warn(f"{doc} Section {num}: {len(sentences)} obligation(s), {have} row(s) in "
                     f"{template} — check each is answered")


# --------------------------------------------------------------------------- check 3

def check_config_keys(texts):
    vocab = json.loads(read("conformance/vocabulary.json"))
    namespaces, extension_namespaces = set(), set()
    for entry in vocab["config_namespaces"]["entries"]:
        token = entry["token"].strip("[]")
        namespaces.add(token)
        if not entry.get("core", False):
            extension_namespaces.add(token)

    text = texts["SPEC.md"]
    sheet_start = text.find("### 6.4 ")
    sheet = text[sheet_start:text.find("## 7. ", sheet_start)]

    for m in re.finditer(r"`([a-z_]+(?:\.[a-z_<>]+)+)`", text):
        key = m.group(1)
        namespace = key.split(".")[0]
        if key.endswith((".md", ".toml", ".json")) or namespace not in namespaces:
            continue  # a file name, or a field path in a namespace no config artifact owns
        if namespace in NAMESPACE_RULES:
            allowed = NAMESPACE_RULES[namespace]
            if not (key.startswith(allowed) or key in [a.rstrip(".") for a in allowed]):
                error(f"SPEC.md:{line_of(text, m.start())}: `{key}` is outside the namespaces "
                      f"Section 5.3.4 fixes ({', '.join(allowed)})")
        elif key not in sheet and namespace not in extension_namespaces:
            warn(f"SPEC.md:{line_of(text, m.start())}: `{key}` is in no Section 6.4 cheat-sheet "
                 f"entry and its namespace owns no extension")


# --------------------------------------------------------------------------- check 4

def registry_tokens(node):
    """Every token a group publishes, under whatever field name."""
    out = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("spec_refs", "note", "description", "governed_by", "artifact"):
                continue
            if key in ("entries", "fields", "status_values", "assignee_values", "broker_verbs",
                       "values", "key"):
                for entry in value if isinstance(value, list) else []:
                    if isinstance(entry, str):
                        out.add(entry)
                    elif isinstance(entry, dict) and "token" in entry:
                        out.add(entry["token"])
            elif isinstance(value, dict):
                out |= registry_tokens(value)
    return out


def check_registries(texts):
    for path, govern in REGISTRIES.items():
        corpus = "".join(texts[d] for d in govern)
        registry = json.loads(read(path))
        for group, body in registry.items():
            if not isinstance(body, dict):
                continue
            for token in sorted(registry_tokens({group: body})):
                if token in corpus:
                    continue
                # A composed token — `<op>:<reason>`, `before:<op>` — is spelled by its parts where
                # the document tabulates the operation and the reason in separate columns.
                if ":" in token and all(part in corpus for part in token.split(":") if part):
                    continue
                error(f"{path}: `{group}` publishes `{token}`, which does not occur in "
                      f"{' or '.join(govern)}")


# --------------------------------------------------------------------------- check 5

def section_body(text, number):
    """The text under a numbered heading, up to the next numbered heading of any level."""
    start = re.search(r"^#{2,5}\s+" + re.escape(number) + r"\.?\s+\S", text, re.M)
    if not start:
        return None
    nxt = re.search(r"^#{2,5}\s+[0-9]+(?:\.[0-9]+)*\.?\s+\S", text[start.end():], re.M)
    return text[start.end(): start.end() + nxt.start()] if nxt else text[start.end():]


def stated_condition_count(body):
    """The count an `await_checks` entry states for its terminal conditions, or None.

    Whitespace is collapsed first: both documents wrap the sentence, so the phrase spans a line
    break and an indent wherever the wrap happens to fall.
    """
    m = re.search(r"until one of (\w+) conditions holds", " ".join(body.split()))
    return AWAIT_COUNT_WORDS.get(m.group(1)) if m else None


def check_await_enumeration(texts):
    parameters = section_body(texts["VCSX-SPEC.md"], "8.1")
    registry = read("conformance/vcsx/vocabulary.json")
    if parameters is None:
        error("VCSX-SPEC.md has no Section 8.1 for the await parameters to be fixed in")
    else:
        for name in AWAIT_PARAMETERS:
            if f"`{name}`" not in parameters:
                error(f"VCSX-SPEC.md Section 8.1 does not name `{name}`, which the await "
                      f"enumeration fixes")
            if name not in registry:
                error(f"conformance/vcsx/vocabulary.json does not name `{name}`, so a consumer "
                      f"reading the registry cannot tell what bounds a wait")

    counts = {}
    for doc, number in (("VCSX-SPEC.md", "4.1"), ("VCSX-CONTRACT.md", "6")):
        body = section_body(texts[doc], number)
        counts[doc] = stated_condition_count(body) if body else None
        if counts[doc] is None:
            error(f"{doc} Section {number} states no terminal-condition count for `await_checks` "
                  f"in the form this check reads (\"until one of N conditions holds\")")

    stated = {doc: n for doc, n in counts.items() if n is not None}
    if len(set(stated.values())) > 1:
        error("`await_checks` terminal conditions: "
              + ", ".join(f"{doc} states {n}" for doc, n in sorted(stated.items())))
    for doc, n in stated.items():
        if n != AWAIT_TERMINAL_CONDITIONS:
            error(f"{doc} states {n} `await_checks` terminal conditions where this check carries "
                  f"{AWAIT_TERMINAL_CONDITIONS} — update the constant if the set grew")


# --------------------------------------------------------------------------- check 6

def check_registry_completeness(texts):
    for path, groups in sorted(CLOSED_GROUPS.items()):
        registry = json.loads(read(path))
        for group, (doc, sections, pattern, region) in sorted(groups.items()):
            if group not in registry:
                error(f"{path} publishes no `{group}` group, which {doc} closes")
                continue
            published = registry_tokens({group: registry[group]})
            fixed = set()
            for number in sections:
                body = section_body(texts[doc], number)
                if body is None:
                    error(f"{doc} has no Section {number}, which fixes `{group}`")
                    continue
                if region is not None:
                    found = re.search(region, body, re.M)
                    if found is None:
                        error(f"{doc} Section {number} carries no enumeration for `{group}` in "
                              f"the form this check reads")
                        continue
                    body = found.group(1)
                fixed |= set(re.findall(pattern, body, re.M))
            where = " and ".join(f"Section {n}" for n in sections)
            for token in sorted(fixed - published):
                error(f"{path}: `{group}` omits `{token}`, which {doc} defines in {where} — a "
                      f"generator reading the group gets a set that is short and says so nowhere")
            for token in sorted(published - fixed):
                error(f"{path}: `{group}` publishes `{token}`, which {doc} does not enumerate in "
                      f"{where} — the group cites the prose it disagrees with as its source")


# --------------------------------------------------------------------------- main

def main():
    for path in DOCS + list(TEMPLATES.values()) + list(REGISTRIES):
        if not os.path.exists(path):
            print(f"error: {path} not found — run from the repository root", file=sys.stderr)
            return 2

    texts = {doc: read(doc) for doc in DOCS}
    heads = {doc: headings(texts[doc]) for doc in DOCS}

    check_references(texts, heads)
    check_obligations(texts)
    check_config_keys(texts)
    check_registries(texts)
    check_await_enumeration(texts)
    check_registry_completeness(texts)

    for line in warnings:
        print(f"warning: {line}")
    for line in errors:
        print(f"error: {line}")

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
