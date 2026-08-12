"""Deterministic mechanical checker for one WELL-governed Markdown artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.front_matter import front_matter_plugin


CHECKER_ID = "capabilities/well_check/well_check.py"
CHECKER_VERSION = "3"
RULES = ("WELL-S001", "WELL-N001", "WELL-N002", "WELL-N003", "WELL-U001")
NAME = re.compile(r"[a-z]+(?:-[a-z]+)*")
DEFINITION = re.compile(r"^\s*`([^`]+)`\s+—\s+(.+)$")
ABBREVIATIONS = {"e.g.", "i.e.", "etc.", "vs.", "Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "Fig.", "No."}
CROSS_DOCUMENT = re.compile(r"(?:\.md(?:#|$)|::)[^\s`]*$")


@dataclass(frozen=True)
class Finding:
    line: int
    rule: str
    explanation: str


@dataclass(frozen=True)
class Exemption:
    line: int
    rule: str
    kind: str
    explanation: str
    requires_manual_review: bool = False


@dataclass(frozen=True)
class InlineCandidate:
    line: int
    source: str
    prose: str
    codes: list[str]


def _line(token: Token) -> int:
    return (token.map[0] + 1) if token.map else 1


def _sentence_end(text: str, index: int) -> bool:
    """Recognize a simple sentence boundary without treating common abbreviations as one."""
    char = text[index]
    if char not in ".!?":
        return False
    if char == ".":
        word = text[: index + 1].rsplit(None, 1)[-1] if text[: index + 1].split() else ""
        if word in ABBREVIATIONS or re.fullmatch(r"(?:[A-Za-z]\.){2,}", word):
            return False
        if index and index + 1 < len(text) and text[index - 1].isdigit() and text[index + 1].isdigit():
            return False
    return index + 1 == len(text) or text[index + 1].isspace() or text[index + 1] in "\"')] }"


def _sentences(text: str) -> list[str]:
    start, result = 0, []
    for index in range(len(text)):
        if _sentence_end(text, index):
            sentence = text[start : index + 1].strip()
            if sentence:
                result.append(sentence)
            start = index + 1
    tail = text[start:].strip()
    if tail:
        result.append(tail)
    return result


def _inline_text(token: Token) -> str:
    """Extract prose text from an inline AST token while omitting inline code."""
    # Keep Markdown emphasis delimiters in the token source: they prevent a
    # bold/italic label such as ``**Warranted.**`` from becoming a prose
    # sentence merely because markdown-it represents its text child alone.
    result = token.content
    for code in _inline_code(token):
        result = result.replace(f"`{code}`", "")
    return result


def _inline_code(token: Token) -> list[str]:
    return [child.content for child in token.children or () if child.type == "code_inline"]


def _is_undefined_formula_candidate(content: str) -> bool:
    """Recognize an unparsed delimiter-shaped block without assigning it formula semantics."""
    lines = content.splitlines()
    return len(lines) >= 2 and lines[0].strip() == "$$" and lines[-1].strip() == "$$"


def _add_exemption(exemptions: list[Exemption], line: int, kind: str, explanation: str, *, manual: bool = False) -> None:
    exemptions.append(Exemption(line, "WELL-U001" if manual else "WELL-S001", kind, explanation, manual))


def _parse(text: str) -> list[Token]:
    """The sole Markdown parsing path; table support is part of repository Markdown."""
    return MarkdownIt("commonmark", {"html": True}).enable("table").use(front_matter_plugin).parse(text)


def _classify(tokens: list[Token]) -> tuple[list[InlineCandidate], list[InlineCandidate], list[Exemption]]:
    """Classify Markdown AST tokens into prose, definition-bearing headings, and exemptions."""
    prose: list[InlineCandidate] = []
    headings: list[InlineCandidate] = []
    exemptions: list[Exemption] = []
    stack: list[str] = []

    for token in tokens:
        if token.type in {"fence", "code_block"}:
            _add_exemption(exemptions, _line(token), "fenced-code" if token.type == "fence" else "indented-code", "code block is structural syntax")
        elif token.type == "front_matter":
            _add_exemption(exemptions, _line(token), "front-matter", "YAML front matter is structural syntax")
        elif token.type == "html_block":
            _add_exemption(exemptions, _line(token), "unknown-block", "HTML block requires manual review", manual=True)
        elif token.type == "hr":
            _add_exemption(exemptions, _line(token), "thematic-break", "thematic break is structural syntax")

        if token.nesting == 1:
            stack.append(token.type)
            if token.type == "heading_open":
                _add_exemption(exemptions, _line(token), "heading", "heading is structural syntax")
            elif token.type == "tr_open":
                _add_exemption(exemptions, _line(token), "table-row", "table row is structural syntax")
            elif token.type == "blockquote_open":
                _add_exemption(exemptions, _line(token), "blockquote", "blockquote requires explicit example marker or manual review", manual=True)
        elif token.type == "inline":
            line, content, codes = _line(token), _inline_text(token), _inline_code(token)
            contexts = set(stack)
            if "heading_open" in contexts:
                headings.append(InlineCandidate(line, token.content, content, codes))
            elif _is_undefined_formula_candidate(token.content):
                _add_exemption(
                    exemptions,
                    line,
                    "possible-block-formula",
                    "delimiter-shaped block formula has no WELL-defined machine grammar and requires manual review",
                    manual=True,
                )
            elif "table_open" in contexts:
                # The containing table has one receipt entry; its cells are not prose.
                pass
            elif "blockquote_open" in contexts:
                if re.match(r"^\s*(?:example|e\.g\.)\b", content, re.IGNORECASE):
                    # Replace the provisional unmarked-blockquote failure deterministically.
                    exemptions[:] = [item for item in exemptions if not (item.line == line and item.kind == "blockquote")]
                    _add_exemption(exemptions, line, "quoted-example", "explicitly marked quoted example is exempt")
            elif "list_item_open" in contexts:
                if not any(_sentence_end(content, index) for index in range(len(content))):
                    _add_exemption(exemptions, line, "list-fragment", "list item has no sentence punctuation")
                else:
                    prose.append(InlineCandidate(line, token.content, content, codes))
            elif token.content.strip() and not (len(codes) == 1 and token.content.strip() == f"`{codes[0]}`") and not NAME.fullmatch(content.strip()):
                prose.append(InlineCandidate(line, token.content, content, codes))
            elif token.content.strip():
                _add_exemption(exemptions, line, "inline-code" if codes else "bare-identifier", "structural syntax is exempt from the sentence rule")
        if token.nesting == -1 and stack:
            stack.pop()
    return prose, headings, exemptions


def _record_names(
    entries: list[InlineCandidate], definitions: dict[str, int], codes: list[tuple[str, int]], violations: list[Finding], exemptions: list[Exemption]
) -> None:
    for entry in entries:
        definition = DEFINITION.match(entry.source)
        if definition:
            name = definition.group(1)
            if not NAME.fullmatch(name):
                violations.append(Finding(entry.line, "WELL-N001", f"canonical definition `{name}` is not lowercase kebab-case"))
            elif name in definitions:
                violations.append(Finding(entry.line, "WELL-N002", f"canonical definition `{name}` duplicates line {definitions[name]}"))
            else:
                definitions[name] = entry.line
        codes.extend((name, entry.line) for name in entry.codes)


def check_bytes(raw: bytes, artifact: str) -> dict[str, object]:
    digest = hashlib.sha256(raw).hexdigest()
    violations: list[Finding] = []
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = ""
        violations.append(Finding(1, "WELL-U001", "artifact is not valid UTF-8 Markdown"))
    prose, headings, exemptions = _classify(_parse(text))
    definitions: dict[str, int] = {}
    codes: list[tuple[str, int]] = []
    _record_names([*prose, *headings], definitions, codes, violations, exemptions)
    for entry in prose:
        for sentence in _sentences(entry.prose):
            if not re.search(r"(?<![A-Za-z])because(?![A-Za-z])", sentence):
                violations.append(Finding(entry.line, "WELL-S001", "prose sentence lacks literal `because`"))
    for spelling, line in codes:
        if CROSS_DOCUMENT.search(spelling):
            _add_exemption(exemptions, line, "cross-document-reference", f"cross-document reference `{spelling}` has no mechanically defined target grammar", manual=True)
            continue
        normalized = spelling.lower().replace("_", "-")
        if spelling != normalized and normalized in definitions:
            violations.append(Finding(line, "WELL-N003", f"canonical reference `{spelling}` is not the exact name `{normalized}`"))
    for exemption in exemptions:
        if exemption.requires_manual_review:
            violations.append(Finding(exemption.line, "WELL-U001", exemption.explanation))
    return {
        "artifact": artifact,
        "artifact_sha256": digest,
        "checker": {"identity": CHECKER_ID, "version": CHECKER_VERSION},
        "applied_rules": list(RULES),
        "violations": [asdict(item) for item in sorted(violations, key=lambda item: (item.line, item.rule, item.explanation))],
        "exemptions": [asdict(item) for item in sorted(exemptions, key=lambda item: (item.line, item.kind, item.explanation))],
        "status": (
            "FAIL"
            if any(item.rule != "WELL-U001" for item in violations)
            else "REVIEW"
            if violations
            else "PASS"
        ),
    }


def check_document(path: Path | str) -> dict[str, object]:
    candidate = Path(path)
    return check_bytes(candidate.read_bytes(), str(candidate))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="check one WELL-governed Markdown document")
    parser.add_argument("artifact", help="Markdown artifact to check")
    args = parser.parse_args(argv)
    try:
        receipt = check_document(args.artifact)
    except OSError as exc:
        receipt = {"artifact": args.artifact, "checker": {"identity": CHECKER_ID, "version": CHECKER_VERSION}, "applied_rules": list(RULES), "violations": [asdict(Finding(1, "WELL-U001", f"artifact unavailable: {exc.strerror or exc}"))], "exemptions": [], "status": "FAIL"}
    for item in receipt["violations"]:
        print(f"{receipt['artifact']}:{item['line']}: {item['rule']}: {item['explanation']}", file=sys.stderr)
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return {"PASS": 0, "FAIL": 1, "REVIEW": 2}[receipt["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
