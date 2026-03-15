"""Build-aware knowledge retrieval for Ask Helios."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_REPO = "https://github.com/FTHTrading/Helios/blob/main"
LAUNCH_REPO = "https://github.com/FTHTrading/Helios-launch/blob/main"

KNOWLEDGE_SOURCES = [
    ("start", "Launch start guide", "START.md"),
    ("white-paper", "Helios white paper", "docs/HELIOS_WHITE_PAPER.md"),
    ("operator-guide", "Operator system guide", "docs/HELIOS_OPERATOR_SYSTEM_GUIDE.md"),
    ("tokenomics", "Senior-engineered tokenomics", "docs/HELIOS_SR_ENGINEERED_TOKENOMICS.md"),
    ("full-rebuttal", "Full rebuttal", "docs/HELIOS_FULL_REBUTTAL.md"),
    ("review-response", "Review response", "docs/HELIOS_REVIEW_RESPONSE.md"),
    ("direct-response", "Direct response to review", "docs/HELIOS_DIRECT_RESPONSE_TO_REVIEW.md"),
    ("claims-matrix", "Claims coverage matrix", "docs/HELIOS_CLAIMS_COVERAGE_MATRIX.md"),
    ("launch-blueprint", "Launch blueprint", "docs/HELIOS_LAUNCH_BLUEPRINT.md"),
    ("move-forward-runbook", "Move forward runbook", "docs/MOVE_FORWARD_RUNBOOK.md"),
    ("takeover-start", "Takeover start here", "docs/TAKEOVER_START_HERE.md"),
    ("operator-checklist", "Operator handoff checklist", "docs/OPERATOR_HANDOFF_CHECKLIST.md"),
    ("ai-system", "AI knowledge system", "docs/HELIOS_AI_SYSTEM.md"),
    ("review-text", "Extracted review text", "Helios-codebase-review.txt"),
    ("app", "Flask app bootstrap", "app.py"),
    ("routes", "API routes", "api/routes.py"),
    ("config", "Configuration", "config.py"),
    ("handoff", "Handoff manifest", "core/handoff.py"),
]


def _normalize_words(text: str) -> list[str]:
    return [word for word in re.findall(r"[a-z0-9_./-]+", text.lower()) if len(word) > 1]


def _github_url(relative_path: str) -> str:
    base = LAUNCH_REPO if relative_path.startswith("docs/") or relative_path in {"START.md", "README.md"} else SOURCE_REPO
    normalized = relative_path.replace("\\", "/")
    return f"{base}/{normalized}"


def _snippet_for_query(content: str, query_words: list[str], max_len: int = 560) -> str:
    lower = content.lower()
    best_index = -1
    for word in query_words:
        idx = lower.find(word)
        if idx != -1:
            best_index = idx
            break

    if best_index == -1:
        best_index = 0

    start = max(0, best_index - 160)
    end = min(len(content), best_index + max_len)
    snippet = content[start:end].strip()
    snippet = re.sub(r"\n{3,}", "\n\n", snippet)
    return snippet


@lru_cache(maxsize=1)
def load_corpus() -> list[dict]:
    corpus = []
    for slug, title, relative_path in KNOWLEDGE_SOURCES:
        absolute_path = ROOT / relative_path
        try:
            content = absolute_path.read_text(encoding="utf-8")
        except Exception:
            continue

        corpus.append({
            "slug": slug,
            "title": title,
            "path": relative_path,
            "content": content,
            "content_lower": content.lower(),
            "github_url": _github_url(relative_path),
        })
    return corpus


def find_relevant_sources(question: str, limit: int = 4) -> list[dict]:
    words = _normalize_words(question)
    if not words:
        return []

    ranked = []
    for item in load_corpus():
        score = 0
        title_lower = item["title"].lower()
        path_lower = item["path"].lower()
        for word in words:
            if word in title_lower:
                score += 6
            if word in path_lower:
                score += 5
            occurrences = item["content_lower"].count(word)
            score += min(occurrences, 8)

        if score:
            ranked.append((score, item))

    ranked.sort(key=lambda pair: pair[0], reverse=True)

    results = []
    for score, item in ranked[:limit]:
        results.append({
            "title": item["title"],
            "path": item["path"],
            "github_url": item["github_url"],
            "score": score,
            "snippet": _snippet_for_query(item["content"], words),
        })
    return results


def build_context_block(question: str, limit: int = 4) -> tuple[str, list[dict]]:
    sources = find_relevant_sources(question, limit=limit)
    if not sources:
        return "", []

    blocks = []
    for source in sources:
        blocks.append(
            f"SOURCE: {source['title']} ({source['path']})\n"
            f"GITHUB: {source['github_url']}\n"
            f"EXCERPT:\n{source['snippet']}"
        )
    return "\n\n---\n\n".join(blocks), sources


def build_grounded_fallback(question: str, limit: int = 3) -> dict | None:
    sources = find_relevant_sources(question, limit=limit)
    if not sources:
        return None

    summary_parts = [
        "Based on the current Helios build and handoff material:",
    ]
    for source in sources:
        summary_parts.append(f"- {source['title']}: {source['snippet'][:260].strip()}")

    return {
        "answer": "\n\n".join(summary_parts),
        "references": [
            {
                "title": source["title"],
                "path": source["path"],
                "github_url": source["github_url"],
            }
            for source in sources
        ],
        "confidence": "grounded",
    }