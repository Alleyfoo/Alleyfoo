from __future__ import annotations

"""Utilities for comparing product lines using a local GPT4All model."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List

try:  # pragma: no cover - optional dependency
    from gpt4all import GPT4All  # type: ignore
except Exception:  # pragma: no cover
    GPT4All = None  # type: ignore


@dataclass
class ProductLine:
    """Structured representation of a product line."""

    sku: str
    description: str


@dataclass
class DiffReport:
    """Result of comparing two product descriptions."""

    is_changed: bool
    differences: List[str]
    confidence: float
    notes: str | None = None


SYSTEM_PROMPT = (
    'Compare two product lines. Output ONLY valid JSON: {"is_changed":bool,'
    '"differences":list of short strings,"confidence":0-1,"notes":optional}.'
)
USER_TMPL = (
    "Original: {orig}\nCurrent: {curr}\n"
    "Rules: JSON only. If unsure, set is_changed=false with low confidence."
)


def extract_text_from_pdf(path: str | Path, page_index: int = 0) -> str:
    """Return text from a single PDF page with an OCR fallback."""

    try:  # pragma: no cover - optional dependency
        import pdfplumber  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ImportError("pdfplumber is required for PDF text extraction") from exc

    with pdfplumber.open(path) as pdf:
        if page_index >= len(pdf.pages):
            raise ValueError(f"PDF has only {len(pdf.pages)} pages")
        page = pdf.pages[page_index]
        text = page.extract_text() or ""
    text = text.strip()
    if text:
        return text

    try:  # pragma: no cover - optional dependency
        from pdf2image import convert_from_path  # type: ignore
        import pytesseract  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise ImportError("OCR dependencies not installed") from exc

    images = convert_from_path(path, first_page=page_index + 1, last_page=page_index + 1, fmt="png")
    if not images:
        return ""
    gray = images[0].convert("L")
    return pytesseract.image_to_string(gray)


PRODUCT_PAT = re.compile(r"\b\d{3}\.\d{3}\.\d{2}\b")
SIZE_PAT = re.compile(r"\b\d+[×x]\d+\b")


def looks_like_product(line: str) -> bool:
    """Heuristic filter for product lines."""

    low = line.lower()
    keywords = [
        "frame",
        "door",
        "drawer",
        "shelf",
        "tv unit",
        "combination",
        "overall size",
        "hinges",
        "glass",
        "screw",
        "nut",
        "washer",
    ]
    flags = [
        any(tok in low for tok in keywords),
        bool(PRODUCT_PAT.search(line)),
        bool(SIZE_PAT.search(line)),
    ]
    return sum(bool(f) for f in flags) >= 1


def synthesize_sku(line: str, idx: int) -> str:
    """Generate a SKU from a line if one is not present."""

    m = PRODUCT_PAT.search(line)
    return (m.group(0) + f"-{idx:02d}") if m else f"PROD-{idx:02d}"


def parse_product_lines(text: str) -> List[ProductLine]:
    """Extract candidate product lines from raw text."""

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    candidates = list(dict.fromkeys(ln for ln in lines if looks_like_product(ln)))
    return [ProductLine(synthesize_sku(ln, i + 1), ln) for i, ln in enumerate(candidates)]


def prompt_from_messages(messages: Iterable[dict[str, str]]) -> str:
    """Convert chat-style messages to a single prompt."""

    parts = [f"{m.get('role', 'user').upper()}: {m.get('content', '')}" for m in messages]
    parts.append("ASSISTANT:")
    return "\n".join(parts)


def _call_model(messages: List[dict[str, str]], model: Any | None) -> str:
    """Call a GPT4All model or stub and return its raw output."""

    if model is None:
        if GPT4All is None:  # pragma: no cover - optional dependency
            raise ImportError("gpt4all is required for diffing")
        model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
        out = model.chat_completion(messages)
        return out["choices"][0]["message"]["content"]
    if hasattr(model, "chat_completion"):
        out = model.chat_completion(messages)
        return out["choices"][0]["message"]["content"]
    if hasattr(model, "generate"):
        prompt = prompt_from_messages(messages)
        return model.generate(prompt, max_tokens=512, temp=0.1)
    raise TypeError("model must expose chat_completion or generate")


def diff_product_lines(
    orig: ProductLine, curr: ProductLine, model: Any | None = None
) -> DiffReport:
    """Compare two product lines using a local LLM."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_TMPL.format(orig=orig.description, curr=curr.description)},
    ]
    raw = _call_model(messages, model=model)
    start, end = raw.find("{"), raw.rfind("}")
    if start >= 0 and end > start:
        raw = raw[start : end + 1]
    data = json.loads(raw)
    return DiffReport(
        is_changed=bool(data.get("is_changed")),
        differences=list(data.get("differences") or []),
        confidence=float(data.get("confidence", 0.0)),
        notes=data.get("notes"),
    )


__all__ = [
    "ProductLine",
    "DiffReport",
    "extract_text_from_pdf",
    "parse_product_lines",
    "diff_product_lines",
]
