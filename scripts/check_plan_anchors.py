#!/usr/bin/env python3
"""Check a plan's claims about this corpus against the corpus, before the plan is implemented.

A plan states what a document says, and the implementation takes the statement on trust: it reads
the plan, not the section. Decision 0134's plan carried four claims that did not hold. Three were
caught by hand during implementation; the fourth was written into `VCSX-SPEC.md` and caught only by
re-reading it afterwards. Two of the four are mechanical, and this script is those two.

  Q  Quote fidelity. Every span the plan quotes occurs in the file, and in the section, the plan
     attributes it to. 0134's plan attributed a "required set" framing to `VCSX-SPEC.md` Section
     13.2, where the phrase occurs only in Section 4.1.
  R  Anchor reach. Every other site carrying the same distinctive wording that the plan does not
     name. An edit addressed to one section leaves its twins behind: 0134's plan named Section 13.3
     for a sentence Section 9.3 carries too, and `conformance/vcsx/vocabulary.json`'s `operations`
     note for a sentence its `output_keys` group carries too.

Both are word-sequence comparisons, not byte comparisons. Markdown emphasis, backticks, edge
punctuation and line wrapping are normalized away on both sides and case is ignored, so a quotation
that spans a line break in the document still matches, and `` `before:<op>` `` in a plan matches
`before:<op>` in a registry note. An ellipsis in a quotation splits it: each fragment is checked
separately, which is what a plan means by eliding the middle of a sentence.

Six limits are deliberate and stated here rather than left to be discovered:

  * A quotation is a double-quoted span or a block quote. A backticked span is not read as one: in
    this repository's register backticks carry code tokens, commands and expected output, and on
    0134's plan every finding they produced was false — three of seven, including a shell command
    checked for occurrence in `SPEC.md`. A plan that quotes prose in backticks is unchecked.
  * Matching is literal after normalization, so an inflection defeats any window that spans it. At
    `1dfec5d`, `conformance/vcsx/README.md:108` wrote "Section 4.1 gates at no fixed position"
    against 0134's plan quoting "gated at no fixed position" — and the site is reached anyway, by
    the window `at no fixed position`, which falls clear of the differing word. A quotation with
    fewer than SHINGLE words to one side of the difference has no such window and is missed.
    Stemming would bridge that case and is not here.
  * A shingle occurring at more than MAX_SITES sites is treated as stock phrasing rather than as
    reach, and reports nothing; so is one built only from closed-class words. A quotation made
    entirely of either is invisible to R.
  * A span's section is the last section reference before it in the same step; its file is the last
    file named before it in the same *sentence*, falling back to the enclosing heading's file and
    then to the step's first. A step naming its section after the quotation, or in a neighbouring
    one, is attributed wrongly or not at all — and a span with no file in view is skipped by Q,
    since with nothing attributed there is no claim to check.
  * R asks whether the plan names a site's *anchor* — a section number for a numbered document, a
    top-level group for a registry, a `path:line` for anything else. A section number is matched
    exactly and per file, so naming Section 6 of one document does not excuse Section 6.11 of that
    document, nor Section 6 of another; but a registry group is matched as a bare identifier
    anywhere in the plan, so a group whose name is an ordinary English word is easily "named".
  * Quotations of text the plan proposes to *write* are checked as though they were quotations of
    text that exists. This repository's register — quoted for the old wording, italic or
    unquoted for the new — keeps that rare rather than making it safe.

Usage: check_plan_anchors.py <plan.md> [--rev REV]. `--rev` reads the corpus from a git revision
instead of the working tree, which is how a plan is checked against the tree it was written
against. Run from the repository root. Exit 0 if no finding, 1 otherwise.
"""

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Section slicing is `validate_spec_consistency.py`'s, imported rather than copied so the two
# checks cannot disagree about where a section begins. The repository carries no `.gitignore`, so
# the import is kept from leaving a `__pycache__` behind in `scripts/`.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_spec_consistency import headings, section_at, section_body  # noqa: E402

CORPUS_FILES = (
    "SPEC.md",
    "VCSX-SPEC.md",
    "VCSX-CONTRACT.md",
    "CONFORMANCE-STATEMENT-TEMPLATE.md",
    "VCSX-CONFORMANCE-STATEMENT-TEMPLATE.md",
)
CORPUS_TREE = "conformance"
CORPUS_SUFFIXES = (".md", ".json")

# A four-word window is the shortest that is a phrase rather than a collocation: it is what carries
# "additional operations and their" and "defines beyond Section 4.1", the two shingles that reach
# the sites 0134's plan left unnamed.
SHINGLE = 4
MAX_SITES = 8
MIN_QUOTE_WORDS = 2

# Stripped from both ends of every word, on both sides of every comparison: markdown emphasis, the
# quotation's own delimiters, and sentence punctuation the document happens to carry.
EDGE = "`*_\"'()[]{}<>,.;:!?" + "“”‘’—–…"

# Closed-class English. A window built only from these is a connective, not a phrase: `so none of
# the` occurs wherever a sentence draws a consequence, and reports two unrelated sites in
# `conformance/vcsx/README.md` for a quotation about `VCSX-SPEC.md` Section 4.3. The list is
# grammatical rather than corpus-tuned, so it does not silence any word this specification owns.
STOPWORDS = frozenset("""
a about all also although an and another any are as at be because been being both but by can could
do does each either even every few for from had has have he hence her him his how however i if in
into is it its just many may might more most much must neither never no none nor not of on once one
only or other our out over own per rather same several shall she should since so some still such
than that the their them then there therefore these they this those though through thus to too
under unless until up upon was we were what when where whereas whether which while who whom whose
why will with within without would yet you your
""".split())

FILE_REF = re.compile(r"(?:[\w.-]+/)*[A-Za-z0-9_.-]+\.(?:md|json)")
SECTION_REF = re.compile(r"§\s*([0-9]+(?:\.[0-9]+)*)|Sections?\s+"
                         r"([0-9]+(?:\.[0-9]+)*(?:\s*(?:,|and|/|or)\s*[0-9]+(?:\.[0-9]+)*)*)")
QUOTE_SPAN = re.compile(r"\"([^\"]{3,400})\"")
JSON_GROUP = re.compile(r"^  \"([A-Za-z_][A-Za-z0-9_]*)\"\s*:")
# A sentence boundary, allowing for the emphasis and the closing delimiter a plan writes over it.
SENTENCE_END = re.compile(r"(?<=[.;:!?])[*_`\"')\]]*\s+(?=[A-Z§`\"'*\[(])")


# --------------------------------------------------------------------------- words

def to_words(text):
    """`text` as the word sequence every comparison here is made over."""
    return [w for w in (raw.strip(EDGE).lower() for raw in text.split()) if w]


def numbered_words(text):
    """[(word, line number)] — the same sequence, each word carrying where it was read."""
    out = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        for raw in line.split():
            word = raw.strip(EDGE).lower()
            if word:
                out.append((word, lineno))
    return out


class Words:
    """A word sequence with an index from first word to position, so a span is found in one pass."""

    def __init__(self, text):
        self.stream = numbered_words(text)
        self.index = defaultdict(list)
        for i, (word, _) in enumerate(self.stream):
            self.index[word].append(i)

    def occurrences(self, seq):
        """Start positions where `seq` occurs."""
        if not seq:
            return []
        found, n = [], len(seq)
        for i in self.index.get(seq[0], ()):
            if i + n <= len(self.stream) and all(self.stream[i + j][0] == seq[j] for j in range(n)):
                found.append(i)
        return found

    def line_of(self, position):
        return self.stream[position][1]


def shingles(seq):
    """Every SHINGLE-word window of `seq` that carries a word of this corpus's own, in order."""
    seen, out = set(), []
    for i in range(len(seq) - SHINGLE + 1):
        window = tuple(seq[i:i + SHINGLE])
        if window in seen or all(word in STOPWORDS for word in window):
            continue
        seen.add(window)
        out.append(list(window))
    return out


def fragments(text):
    """A quotation split at its elisions — each fragment is a separate claim of verbatim text."""
    return [f for f in re.split(r"\s*(?:…|\.\.\.)\s*", text) if f.strip()]


# --------------------------------------------------------------------------- corpus

class Doc(Words):
    def __init__(self, path, text):
        super().__init__(text)
        self.path = path
        self.text = text
        self.markdown = path.endswith(".md")
        self.headings = headings(text) if self.markdown else {}
        self.line_start = [0]
        for line in text.split("\n"):
            self.line_start.append(self.line_start[-1] + len(line) + 1)
        self.groups = []
        if path.endswith(".json"):
            for lineno, line in enumerate(text.split("\n"), start=1):
                m = JSON_GROUP.match(line)
                if m:
                    self.groups.append((lineno, m.group(1)))
        self._bodies = {}

    def anchor(self, lineno):
        """What a plan would have to write to name this site, or None where the file offers no
        finer address than itself."""
        if self.headings:
            return section_at(self.text, self.line_start[lineno - 1])[0]
        if self.groups:
            current = None
            for start, name in self.groups:
                if start > lineno:
                    break
                current = name
            return current
        return None

    def body(self, number):
        """The section's text as a word sequence, or None where the document has no such section."""
        if number not in self._bodies:
            text = section_body(self.text, number)
            self._bodies[number] = None if text is None else Words(text)
        return self._bodies[number]


def read_at(path, rev):
    if rev:
        run = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True)
        return run.stdout if run.returncode == 0 else None
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def tree_paths(rev):
    if rev:
        run = subprocess.run(["git", "ls-tree", "-r", "--name-only", rev, "--", CORPUS_TREE],
                             capture_output=True, text=True)
        names = run.stdout.split("\n") if run.returncode == 0 else []
    else:
        names = []
        for root, _dirs, files in os.walk(CORPUS_TREE):
            names += [os.path.join(root, name) for name in files]
    return sorted(name for name in names if name.endswith(CORPUS_SUFFIXES))


def load_corpus(rev):
    docs = {}
    for path in list(CORPUS_FILES) + tree_paths(rev):
        text = read_at(path, rev)
        if text is not None:
            docs[path] = Doc(path, text)
    return docs


def sites_of(corpus, seq):
    """[(doc, line)] for every occurrence of `seq` anywhere in the corpus."""
    out = []
    for doc in corpus.values():
        for i in doc.occurrences(seq):
            out.append((doc, doc.line_of(i)))
    return out


# --------------------------------------------------------------------------- the plan

class Span:
    def __init__(self, text, file, section):
        self.text = text
        self.file = file
        self.section = section

    def where(self):
        if self.file and self.section:
            return f"{self.file} Section {self.section}"
        return self.file or "the corpus"


def section_refs(text):
    """[(position, number)] for every section reference, single or listed."""
    out = []
    for m in SECTION_REF.finditer(text):
        group = m.group(1) or m.group(2)
        for number in re.findall(r"[0-9]+(?:\.[0-9]+)*", group):
            out.append((m.start(), number.rstrip(".")))
    return out


def last_before(items, position, since=0):
    """The value of the last (position, value) pair before `position`, or None."""
    found = None
    for at, value in items:
        if at >= position:
            break
        if at >= since:
            found = value
    return found


def sentence_start(text, position):
    """Where the sentence containing `position` begins.

    A document named in a sentence is the subject of that sentence and of no other.
    "…a MINOR release of `VCSX-SPEC.md` Section 8.5. Section 1's claim to fix …" names the
    engine spec and then quotes the contract, and only the sentence boundary separates them.
    """
    start = 0
    for m in SENTENCE_END.finditer(text):
        if m.end() > position:
            break
        start = m.end()
    return start


class Plan:
    def __init__(self, path, text, corpus_paths):
        self.path = path
        self.text = text
        self.corpus_paths = corpus_paths
        self.spans = []
        self.sections = defaultdict(set)  # corpus path -> the section numbers named for it
        self.loose = set()                # section numbers named with no file in view
        self.identifiers = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text))
        self._named_file = {}
        self._carry = (None, None)  # the file and section the previous step ended in view of
        self._parse()

    # -- reading the plan

    def _resolve(self, reference):
        """A file reference as written in the plan, as a corpus path, or None."""
        if reference in self.corpus_paths:
            return reference
        matches = [p for p in self.corpus_paths if os.path.basename(p) == reference]
        return matches[0] if len(matches) == 1 else None

    def _parse(self):
        heading_files, fenced = [], False
        step, quoted = [], False

        def flush():
            nonlocal step, quoted
            if step:
                self._step(" ".join(step), heading_files, quoted)
            step, quoted = [], False

        for line in self.text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("```"):
                fenced = not fenced
                flush()
                continue
            if fenced:
                continue
            if not stripped:
                flush()
                continue
            if re.match(r"^#{1,6}\s", line):
                flush()
                heading_files = self._files_in(line)
                continue
            block = stripped.startswith(">")
            if block != quoted or re.match(r"^\s*(?:[-*+]\s|[0-9]+\.\s|\|)", line):
                flush()
                quoted = block
            step.append(stripped.lstrip("> ") if block else stripped)
        flush()

    def _files_in(self, text):
        """[(position, corpus path)] for every corpus file the text names."""
        out = []
        for m in FILE_REF.finditer(text):
            path = self._resolve(m.group(0))
            if path:
                out.append((m.start(), path))
        return out

    def _step(self, text, heading_files, quoted):
        files = self._files_in(text)
        refs = section_refs(text)
        # A heading naming a file scopes the steps under it. Falling back to a file the step names
        # only *after* the quotation would attribute it to a document it merely cites in passing.
        default = (heading_files[0][1] if heading_files else None) or (files[0][1] if files
                                                                       else None)

        for position, number in refs:
            owner = last_before(files, position) or default
            if owner:
                self.sections[owner].add(number)
            else:
                self.loose.add(number)

        if quoted:
            # A block quote is a step of its own, with nothing before it to attribute it to; the
            # step that introduced it holds the anchor.
            spans = [(len(text), text)]
        else:
            spans = [(m.start(), m.group(1)) for m in QUOTE_SPAN.finditer(text)]
        for position, quotation in spans:
            file = (last_before(files, position, sentence_start(text, position))
                    or default or self._carry[0])
            section = last_before(refs, position) or (self._carry[1] if quoted else None)
            self.spans.append(Span(quotation, file, section))

        self._carry = (last_before(files, len(text)) or default or self._carry[0],
                       last_before(refs, len(text)) or self._carry[1])

    # -- what the plan names

    def names_file(self, path):
        if path not in self._named_file:
            pattern = r"(?<![\w/.-])" + re.escape(path) + r"(?![\w-])"
            self._named_file[path] = re.search(pattern, self.text) is not None
        return self._named_file[path]

    def names_site(self, doc, lineno):
        if not self.names_file(doc.path):
            return False
        anchor = doc.anchor(lineno)
        if anchor is None:
            return f"{doc.path}:{lineno}" in self.text
        if doc.headings:
            return anchor in self.sections.get(doc.path, ()) or anchor in self.loose
        return anchor in self.identifiers


# --------------------------------------------------------------------------- the lenses

def describe(doc, lineno):
    anchor = doc.anchor(lineno)
    if anchor is None:
        return f"{doc.path}:{lineno}"
    if doc.headings:
        return f"{doc.path}:{lineno} (Section {anchor})"
    return f"{doc.path}:{lineno} (`{anchor}`)"


def check_quotes(plan, corpus, findings):
    """Q — every quoted span occurs where the plan says it does."""
    reported = set()
    for span in plan.spans:
        doc = corpus.get(span.file)
        if doc is None:
            continue
        for fragment in fragments(span.text):
            seq = to_words(fragment)
            if len(seq) < MIN_QUOTE_WORDS:
                continue
            key = (span.file, span.section, tuple(seq))
            if key in reported:
                continue
            scope = doc
            if span.section and doc.headings:
                if span.section not in doc.headings:
                    reported.add(key)
                    findings.append(f"Q {span.where()}: the plan cites a section this document "
                                    f"does not have")
                    continue
                scope = doc.body(span.section)
            if scope.occurrences(seq):
                continue
            reported.add(key)
            elsewhere = sites_of(corpus, seq)
            quotation = " ".join(fragment.split())
            if elsewhere:
                where = ", ".join(describe(d, n) for d, n in elsewhere[:3])
                findings.append(f"Q {span.where()}: \"{quotation}\" does not occur there; it "
                                f"occurs at {where}")
            else:
                findings.append(f"Q {span.where()}: \"{quotation}\" occurs nowhere in the corpus")


def check_reach(plan, corpus, findings):
    """R — every site carrying the same distinctive wording that the plan does not name."""
    reported = set()
    for span in plan.spans:
        for fragment in fragments(span.text):
            for shingle in shingles(to_words(fragment)):
                sites = sites_of(corpus, shingle)
                if not sites or len(sites) > MAX_SITES:
                    continue
                for doc, lineno in sites:
                    if plan.names_site(doc, lineno):
                        continue
                    key = (doc.path, doc.anchor(lineno) or lineno)
                    if key in reported:
                        continue
                    reported.add(key)
                    findings.append(f"R {describe(doc, lineno)}: carries \"{' '.join(shingle)}\", "
                                    f"quoted in the plan against {span.where()}, and the plan does "
                                    f"not name this site")


# --------------------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("plan", help="the plan file to check")
    parser.add_argument("--rev", help="read the corpus from this git revision instead of the "
                                      "working tree")
    args = parser.parse_args()

    for path in CORPUS_FILES:
        if read_at(path, args.rev) is None:
            print(f"error: {path} not found — run from the repository root", file=sys.stderr)
            return 2
    plan_text = read_at(args.plan, None)
    if plan_text is None:
        print(f"error: {args.plan} not readable", file=sys.stderr)
        return 2

    corpus = load_corpus(args.rev)
    plan = Plan(args.plan, plan_text, set(corpus))

    findings = []
    check_quotes(plan, corpus, findings)
    check_reach(plan, corpus, findings)

    for line in findings:
        print(line)
    where = args.rev or "the working tree"
    print(f"\n{len(findings)} finding(s) from {len(plan.spans)} quoted span(s) against {where}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
