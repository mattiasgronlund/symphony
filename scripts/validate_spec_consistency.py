#!/usr/bin/env python3
"""Check the artifacts derived from SPEC.md, VCSX-SPEC.md and VCSX-CONTRACT.md against the
enumerations that govern them.

Every check here corresponds to a defect found by hand in decision 0132, where the same shape had
been found by a person reading for the fourth time: a specification sentence enumerates something,
a second artifact restates that enumeration, the two disagree, and nothing notices because each
artifact is complete against itself.

Checks:

  1. Section references resolve, within a document and across the three.
  2. Every section carrying an `Implementation-defined` or "MUST document" obligation has at least
     one row in the matching Conformance Statement template.
  3. A config key is spelled in the namespace its defining section fixes.
  4. Every token a registry publishes occurs in the document that governs it.

Two limits are deliberate and stated here rather than left to be discovered:

  * Check 2 matches per *section*, not per obligation. A section with three obligations and two
    rows is reported as a shortfall; a section with one obligation and one row that answers a
    different question passes. Only a zero-row section is an error, because the counts legitimately
    differ in at least one place — Section 14.2's node-provisioning obligation is rowed under the
    extension's own section 9.11 — so a strict count would fail a correct tree.
  * Check 4 is a substring test, which is what a registry-versus-prose comparison can honestly do.
    It under-reports: `parent` occurs in VCSX-SPEC.md as an English word ("re-parents a commit"), so
    a field named `parent` passes whether or not the document fixes it as a token.

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

def obligation_sentences(doc, text):
    """Distinct obligation sentences, grouped by the section they sit in."""
    marker = re.compile(r"`Implementation-defined`|Implementation-defined|MUST document|"
                        r"MUST be documented")
    flat = text.replace("\n", " ")
    by_section = {}
    for m in marker.finditer(flat):
        start = flat.rfind(".", 0, max(0, m.start() - 1)) + 1
        end = flat.find(".", m.end())
        sentence = flat[start:end if end != -1 else len(flat)].strip()
        # `flat` swaps each newline for one space, so offsets map 1:1 onto `text`.
        num, title = section_at(text, m.start())
        if title and any(t in title for t in OBLIGATION_EXEMPT_TITLES):
            continue
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

    for line in warnings:
        print(f"warning: {line}")
    for line in errors:
        print(f"error: {line}")

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
