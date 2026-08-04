# -*- coding: utf-8 -*-
"""
DevClean API — text cleaning operations over HTTP.

Note that the website does NOT call this service: every tool on the site runs
client-side in the browser, which is what keeps the user's text private and the
UI instant. This API exists for the other use case — automating the same
operations from scripts, build steps and scheduled jobs.

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload
"""

from __future__ import annotations

import base64
import json
import random
import re
import unicodedata
from html import escape as html_escape
from html.parser import HTMLParser
from typing import Any, Callable
from urllib.parse import quote, unquote_plus

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

MAX_CHARS = 200_000

app = FastAPI(
    title="DevClean API",
    version="2.0.0",
    description=(
        "Text cleaning and conversion operations. The DevClean website processes "
        "text in the browser; this API is for automation."
    ),
)

ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "https://albertomariapareti.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# ==========================================================================
# Helpers
# ==========================================================================


def split_lines(text: str) -> list[str]:
    """Normalise CRLF/CR to LF so every operation sees the same thing."""
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def to_words(value: str) -> list[str]:
    """Split an identifier into lowercase words (camelCase, snake_case, ...)."""
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    return [w.lower() for w in re.split(r"[^A-Za-z0-9]+", spaced) if w]


def trim_blank_edges(lines: list[str]) -> list[str]:
    start, end = 0, len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


# ==========================================================================
# Operations
# ==========================================================================


def op_clean_spaces(text: str, o: dict) -> str:
    keep_indent = o.get("keepIndent", True)
    out = []
    for line in split_lines(text):
        indent = re.match(r"^[ \t]*", line).group(0) if keep_indent else ""
        body = re.sub(r"[ \t]+", " ", line[len(indent):]).rstrip()
        if (indent + body).strip():
            out.append(indent + body)
    return "\n".join(out)


def op_trim_lines(text: str, o: dict) -> str:
    return "\n".join(line.strip() for line in split_lines(text))


def op_collapse_blank_lines(text: str, o: dict) -> str:
    out: list[str] = []
    for line in split_lines(text):
        blank = not line.strip()
        if blank and out and not out[-1].strip():
            continue
        out.append("" if blank else line.rstrip())
    return "\n".join(trim_blank_edges(out))


def op_remove_blank_lines(text: str, o: dict) -> str:
    return "\n".join(line for line in split_lines(text) if line.strip())


def _dedup_key(line: str, o: dict) -> str:
    key = line
    if o.get("ignoreCase"):
        key = key.lower()
    if o.get("ignoreWhitespace"):
        key = key.strip()
    return key


def op_remove_duplicates(text: str, o: dict) -> str:
    seen: set[str] = set()
    out = []
    for line in split_lines(text):
        key = _dedup_key(line, o)
        if key in seen:
            continue
        seen.add(key)
        out.append(line)
    return "\n".join(out)


def op_keep_duplicates(text: str, o: dict) -> str:
    lines = split_lines(text)
    counts: dict[str, int] = {}
    for line in lines:
        key = _dedup_key(line, o)
        counts[key] = counts.get(key, 0) + 1
    emitted: set[str] = set()
    out = []
    for line in lines:
        key = _dedup_key(line, o)
        if counts[key] > 1 and key not in emitted:
            emitted.add(key)
            out.append(line)
    return "\n".join(out)


def op_to_json_array(text: str, o: dict) -> str:
    items: list[Any] = [line.strip() for line in split_lines(text) if line.strip()]
    if o.get("numeric"):
        converted: list[Any] = []
        for value in items:
            try:
                num = float(value)
                converted.append(int(num) if num.is_integer() and "." not in value else num)
            except ValueError:
                converted.append(value)
        items = converted
    indent = None if o.get("compact") else 2
    separators = (",", ":") if o.get("compact") else None
    return json.dumps(items, indent=indent, separators=separators, ensure_ascii=False)


def op_to_json_object(text: str, o: dict) -> str:
    obj: dict[str, str] = {}
    for line in split_lines(text):
        if not line.strip():
            continue
        match = re.match(r"^\s*([^,:]+)\s*[,:]\s*(.*)$", line)
        if match:
            obj[match.group(1).strip()] = match.group(2).strip()
        else:
            obj[line.strip()] = ""
    return json.dumps(obj, indent=2, ensure_ascii=False)


def _split_csv_row(row: str, delimiter: str) -> list[str]:
    out, cur, in_quotes, i = [], "", False, 0
    while i < len(row):
        ch = row[i]
        if in_quotes:
            if ch == '"' and i + 1 < len(row) and row[i + 1] == '"':
                cur += '"'
                i += 1
            elif ch == '"':
                in_quotes = False
            else:
                cur += ch
        elif ch == '"':
            in_quotes = True
        elif ch == delimiter:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
        i += 1
    out.append(cur.strip())
    return out


def op_csv_to_json(text: str, o: dict) -> str:
    delimiter = o.get("delimiter") or ","
    rows = [line for line in split_lines(text) if line.strip()]
    if not rows:
        return "[]"
    headers = _split_csv_row(rows[0], delimiter)
    records = []
    for row in rows[1:]:
        cells = _split_csv_row(row, delimiter)
        records.append({h: (cells[i] if i < len(cells) else "") for i, h in enumerate(headers)})
    return json.dumps(records, indent=2, ensure_ascii=False)


def _per_line(text: str, fn: Callable[[str], str]) -> str:
    return "\n".join(fn(line) for line in split_lines(text))


def op_upper_case(text: str, o: dict) -> str:
    return text.upper()


def op_lower_case(text: str, o: dict) -> str:
    return text.lower()


def op_title_case(text: str, o: dict) -> str:
    return re.sub(r"\w\S*", lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), text)


def op_sentence_case(text: str, o: dict) -> str:
    def fix(line: str) -> str:
        lowered = line.lower()
        return re.sub(r"(^\s*\w)|([.!?]\s+\w)", lambda m: m.group(0).upper(), lowered)
    return _per_line(text, fix)


def op_camel_case(text: str, o: dict) -> str:
    def fix(line: str) -> str:
        words = to_words(line)
        if not words:
            return line
        return words[0] + "".join(w.capitalize() for w in words[1:])
    return _per_line(text, fix)


def op_pascal_case(text: str, o: dict) -> str:
    def fix(line: str) -> str:
        words = to_words(line)
        return "".join(w.capitalize() for w in words) if words else line
    return _per_line(text, fix)


def op_snake_case(text: str, o: dict) -> str:
    return _per_line(text, lambda l: "_".join(to_words(l)) or l)


def op_kebab_case(text: str, o: dict) -> str:
    return _per_line(text, lambda l: "-".join(to_words(l)) or l)


def op_constant_case(text: str, o: dict) -> str:
    return _per_line(text, lambda l: "_".join(to_words(l)).upper() or l)


def _natural_key(line: str):
    """Sort key giving natural number ordering and case/accent insensitivity."""
    parts = re.split(r"(\d+)", line)
    key = []
    for part in parts:
        if part.isdigit():
            key.append((1, int(part), ""))
        elif part:
            folded = unicodedata.normalize("NFKD", part.lower())
            folded = "".join(c for c in folded if not unicodedata.combining(c))
            key.append((0, 0, folded))
    return key


def _sorted_preserving_trailing(text: str, **kwargs) -> str:
    lines = split_lines(text)
    trailing = len(lines) > 1 and lines[-1] == ""
    if trailing:
        lines.pop()
    lines.sort(**kwargs)
    if trailing:
        lines.append("")
    return "\n".join(lines)


def op_sort_asc(text: str, o: dict) -> str:
    return _sorted_preserving_trailing(text, key=_natural_key)


def op_sort_desc(text: str, o: dict) -> str:
    return _sorted_preserving_trailing(text, key=_natural_key, reverse=True)


def op_sort_length(text: str, o: dict) -> str:
    return _sorted_preserving_trailing(text, key=lambda l: (len(l), _natural_key(l)))


def op_sort_length_desc(text: str, o: dict) -> str:
    return _sorted_preserving_trailing(text, key=lambda l: (-len(l), _natural_key(l)))


def op_reverse_lines(text: str, o: dict) -> str:
    return "\n".join(reversed(split_lines(text)))


def op_shuffle_lines(text: str, o: dict) -> str:
    lines = split_lines(text)
    random.shuffle(lines)
    return "\n".join(lines)


def op_number_lines(text: str, o: dict) -> str:
    start = int(o.get("start", 1))
    separator = o.get("separator", ". ")
    lines = split_lines(text)
    width = len(str(start + len(lines) - 1))
    out = []
    for i, line in enumerate(lines):
        number = str(start + i)
        if o.get("pad"):
            number = number.zfill(width)
        out.append(f"{number}{separator}{line}")
    return "\n".join(out)


def op_add_prefix_suffix(text: str, o: dict) -> str:
    prefix, suffix = o.get("prefix", ""), o.get("suffix", "")
    skip_empty = o.get("skipEmpty", True)
    return _per_line(
        text, lambda l: l if (skip_empty and not l.strip()) else f"{prefix}{l}{suffix}"
    )


def op_tabs_to_spaces(text: str, o: dict) -> str:
    size = int(o.get("tabSize", 4) or 4)

    def expand(line: str) -> str:
        out = ""
        for ch in line:
            if ch == "\t":
                out += " " * (size - (len(out) % size))
            else:
                out += ch
        return out
    return _per_line(text, expand)


def op_spaces_to_tabs(text: str, o: dict) -> str:
    size = int(o.get("tabSize", 4) or 4)

    def convert(line: str) -> str:
        indent = re.match(r"^[ \t]*", line).group(0)
        return indent.replace(" " * size, "\t") + line[len(indent):]
    return _per_line(text, convert)


def op_base64_encode(text: str, o: dict) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def op_base64_decode(text: str, o: dict) -> str:
    cleaned = re.sub(r"\s+", "", text)
    try:
        return base64.b64decode(cleaned, validate=True).decode("utf-8")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Input is not valid Base64 (check for missing characters or padding).",
        ) from exc


def op_url_encode(text: str, o: dict) -> str:
    safe = "" if o.get("component", True) else "/:?#[]@!$&'()*+,;="
    return quote(text, safe=safe)


def op_url_decode(text: str, o: dict) -> str:
    try:
        return unquote_plus(text)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail="Input contains an invalid percent-encoding sequence."
        ) from exc


def op_html_escape(text: str, o: dict) -> str:
    return html_escape(text, quote=True)


def op_html_unescape(text: str, o: dict) -> str:
    import html as html_module
    # &nbsp; is technically U+00A0, but this is a text-cleaning tool and a
    # non-breaking space is exactly the invisible character users are trying to
    # get rid of. Normalise it to a plain space, matching the browser engine.
    return html_module.unescape(text).replace(" ", " ")


class _TextExtractor(HTMLParser):
    """Collects visible text, turning block elements into line breaks."""

    BLOCK = {"p", "div", "li", "tr", "br", "h1", "h2", "h3", "h4", "h5", "h6"}
    SKIP = {"script", "style", "noscript"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skipping += 1
        elif tag == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skipping:
            self._skipping -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skipping:
            self.parts.append(data)


def op_strip_html(text: str, o: dict) -> str:
    parser = _TextExtractor()
    parser.feed(text)
    parser.close()
    return op_collapse_blank_lines("".join(parser.parts), {})


def op_text_stats(text: str, o: dict) -> str:
    lines = split_lines(text)
    words = text.split()
    sentences = [s for s in re.split(r"[.!?]+(?=\s|$)", text) if s.strip()]
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    unique = {re.sub(r"[^\w'-]", "", w.lower()) for w in words}
    unique.discard("")
    rows = [
        ("Characters", len(text)),
        ("Characters (no spaces)", len(re.sub(r"\s", "", text))),
        ("Words", len(words)),
        ("Unique words", len(unique)),
        ("Lines", len(lines)),
        ("Non-empty lines", sum(1 for l in lines if l.strip())),
        ("Sentences", len(sentences)),
        ("Paragraphs", len(paragraphs)),
        ("Average word length",
         round(sum(len(w) for w in words) / len(words), 1) if words else 0),
        ("Longest word", max(words, key=len) if words else "\u2014"),
        ("Reading time", f"~{max(1, round(len(words) / 225))} min"),
        ("Speaking time", f"~{max(1, round(len(words) / 130))} min"),
    ]
    width = max(len(label) for label, _ in rows)
    return "\n".join(f"{label.ljust(width)}  {value}" for label, value in rows)


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)
NUMBER_RE = re.compile(r"-?\d+(?:[.,]\d+)?")


def _extract(text: str, pattern: re.Pattern, unique: bool) -> str:
    found = pattern.findall(text)
    if unique:
        seen, out = set(), []
        for value in found:
            key = value.lower()
            if key not in seen:
                seen.add(key)
                out.append(value)
        found = out
    return "\n".join(found)


def op_extract_emails(text: str, o: dict) -> str:
    return _extract(text, EMAIL_RE, o.get("unique", True))


def op_extract_urls(text: str, o: dict) -> str:
    return _extract(text, URL_RE, o.get("unique", True))


def op_extract_numbers(text: str, o: dict) -> str:
    return _extract(text, NUMBER_RE, o.get("unique", True))


# --------------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------------

OPERATIONS: dict[str, Callable[[str, dict], str]] = {
    "clean_spaces": op_clean_spaces,
    "trim_lines": op_trim_lines,
    "collapse_blank_lines": op_collapse_blank_lines,
    "remove_blank_lines": op_remove_blank_lines,
    "remove_duplicates": op_remove_duplicates,
    "keep_duplicates": op_keep_duplicates,
    "remove_unique": op_keep_duplicates,
    "to_json_array": op_to_json_array,
    "to_json_object": op_to_json_object,
    "csv_to_json": op_csv_to_json,
    "upper_case": op_upper_case,
    "lower_case": op_lower_case,
    "title_case": op_title_case,
    "sentence_case": op_sentence_case,
    "camel_case": op_camel_case,
    "pascal_case": op_pascal_case,
    "snake_case": op_snake_case,
    "kebab_case": op_kebab_case,
    "constant_case": op_constant_case,
    "sort_asc": op_sort_asc,
    "sort_desc": op_sort_desc,
    "sort_length": op_sort_length,
    "sort_length_desc": op_sort_length_desc,
    "reverse_lines": op_reverse_lines,
    "shuffle_lines": op_shuffle_lines,
    "number_lines": op_number_lines,
    "add_prefix_suffix": op_add_prefix_suffix,
    "tabs_to_spaces": op_tabs_to_spaces,
    "spaces_to_tabs": op_spaces_to_tabs,
    "base64_encode": op_base64_encode,
    "base64_decode": op_base64_decode,
    "url_encode": op_url_encode,
    "url_decode": op_url_decode,
    "html_escape": op_html_escape,
    "html_unescape": op_html_unescape,
    "strip_html": op_strip_html,
    "text_stats": op_text_stats,
    "extract_emails": op_extract_emails,
    "extract_urls": op_extract_urls,
    "extract_numbers": op_extract_numbers,
}

# The original API used these names; keep them working so existing callers
# do not break.
LEGACY_ALIASES = {
    "to_json_keys": "to_json_array",
}


# ==========================================================================
# Schema and routes
# ==========================================================================


class TextRequest(BaseModel):
    text: str = Field(..., description="The text to process.")
    option: str = Field(..., description="Operation id, e.g. 'remove_duplicates'.")
    options: dict[str, Any] = Field(
        default_factory=dict,
        description="Operation-specific settings, e.g. {'ignoreCase': true}.",
    )


class TextResponse(BaseModel):
    processed_text: str
    operation: str


@app.get("/")
def root() -> dict:
    return {
        "name": "DevClean API",
        "version": app.version,
        "docs": "/docs",
        "operations": "/api/operations",
        "website": "https://albertomariapareti.github.io/devclean/",
    }


@app.get("/api/health")
def health() -> dict:
    """Cheap endpoint for uptime checks and for waking a sleeping free instance."""
    return {"status": "ok"}


@app.get("/api/operations")
def list_operations() -> dict:
    return {
        "operations": sorted(OPERATIONS.keys()),
        "aliases": LEGACY_ALIASES,
        "max_characters": MAX_CHARS,
    }


@app.post("/api/process", response_model=TextResponse)
def process_text(req: TextRequest) -> TextResponse:
    if not req.text.strip():
        return TextResponse(processed_text="", operation=req.option)

    if len(req.text) > MAX_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"Text is too long ({len(req.text)} characters, maximum {MAX_CHARS}).",
        )

    option = LEGACY_ALIASES.get(req.option, req.option)
    handler = OPERATIONS.get(option)
    if handler is None:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Unknown option '{req.option}'.",
                "valid_options": sorted(OPERATIONS.keys()),
            },
        )

    try:
        result = handler(req.text, req.options or {})
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Processing error: {exc}") from exc

    return TextResponse(processed_text=result, operation=option)
