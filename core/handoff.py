"""Handoff portal manifest and document retrieval helpers."""

from __future__ import annotations

from html import escape
from pathlib import Path

from config import HeliosConfig

try:
    import markdown as markdown_lib
except ImportError:  # pragma: no cover - optional dependency
    markdown_lib = None


REPO_ROOT = Path(__file__).resolve().parent.parent

HANDOFF_DOCS = [
    {
        "slug": "start",
        "title": "START",
        "summary": "Shortest path for the incoming team: use Route B, keep the watermark hidden, and validate the launch path first.",
        "path": "START.md",
        "order": 1,
    },
    {
        "slug": "final-recommendation",
        "title": "Final Recommendation",
        "summary": "Single authoritative decision on route, stack, messaging posture, and first launch actions.",
        "path": "docs/FINAL_RECOMMENDATION.md",
        "order": 2,
    },
    {
        "slug": "white-paper",
        "title": "Helios White Paper",
        "summary": "Senior-level explanation of the current Helios system, launch posture, architecture, treasury path, and truth-based production framing.",
        "path": "docs/HELIOS_WHITE_PAPER.md",
        "order": 3,
    },
    {
        "slug": "operator-system-guide",
        "title": "Operator System Guide",
        "summary": "Operator-grade system guide covering responsibilities, environment requirements, validation, release discipline, and stakeholder answer posture.",
        "path": "docs/HELIOS_OPERATOR_SYSTEM_GUIDE.md",
        "order": 4,
    },
    {
        "slug": "sr-engineered-tokenomics",
        "title": "Senior-Engineered Tokenomics",
        "summary": "High-level tokenomics framing focused on fixed supply clarity, disciplined rollout, utility, and conservative public positioning.",
        "path": "docs/HELIOS_SR_ENGINEERED_TOKENOMICS.md",
        "order": 5,
    },
    {
        "slug": "full-rebuttal",
        "title": "Full Rebuttal",
        "summary": "Full rebuttal package for future diligence questions, built from the review, current codebase, and launch documentation set.",
        "path": "docs/HELIOS_FULL_REBUTTAL.md",
        "order": 6,
    },
    {
        "slug": "ai-system",
        "title": "AI Knowledge System",
        "summary": "How Ask Helios should answer from the actual build by prioritizing docs, rebuttal materials, and source-aware context.",
        "path": "docs/HELIOS_AI_SYSTEM.md",
        "order": 7,
    },
    {
        "slug": "move-forward-runbook",
        "title": "Move Forward Runbook",
        "summary": "Full execution path from handoff to launch readiness, including setup, validation, and go/no-go gates.",
        "path": "docs/MOVE_FORWARD_RUNBOOK.md",
        "order": 8,
    },
    {
        "slug": "takeover-start-here",
        "title": "Takeover Start Here",
        "summary": "First-read orientation for the build-and-launch team taking operational control of the Helios stack.",
        "path": "docs/TAKEOVER_START_HERE.md",
        "order": 9,
    },
    {
        "slug": "operator-checklist",
        "title": "Operator Handoff Checklist",
        "summary": "Operator checklist covering environment setup, validation steps, and launch readiness responsibilities.",
        "path": "docs/OPERATOR_HANDOFF_CHECKLIST.md",
        "order": 10,
    },
    {
        "slug": "final-launch-readiness",
        "title": "Final Launch Readiness",
        "summary": "Single checklist for what is complete in-repo, what still blocks public launch, and the exact final production actions.",
        "path": "docs/FINAL_LAUNCH_READINESS.md",
        "order": 11,
    },
    {
        "slug": "github-checklist",
        "title": "GitHub Handoff Checklist",
        "summary": "Exact About settings, protections, and public repository posture for the takeover team.",
        "path": "docs/GITHUB_HANDOFF_CHECKLIST.md",
        "order": 12,
    },
    {
        "slug": "route-options",
        "title": "Build Route Options",
        "summary": "Decision sheet for choosing the correct implementation route, with Route B as the default launch choice.",
        "path": "docs/BUILD_ROUTE_OPTIONS.md",
        "order": 13,
    },
    {
        "slug": "page-alignment",
        "title": "Page Alignment Memo",
        "summary": "What public marketing copy can stay, what should be softened, and what must wait until verified deployment exists.",
        "path": "docs/PAGE_ALIGNMENT_MEMO.md",
        "order": 14,
    },
    {
        "slug": "prompt-pack",
        "title": "Takeover Prompt Pack",
        "summary": "Reusable prompts for the incoming team to continue implementation, setup, QA, and launch alignment work.",
        "path": "docs/TAKEOVER_PROMPT_PACK.md",
        "order": 15,
    },
    {
        "slug": "simplified-option",
        "title": "Helios Simplified Option",
        "summary": "Lower-complexity launch option intended to reduce delivery risk while keeping core activation and funding paths intact.",
        "path": "docs/HELIOS_SIMPLIFIED_OPTION.md",
        "order": 16,
    },
    {
        "slug": "launch-blueprint",
        "title": "Launch Blueprint",
        "summary": "Production architecture, environment groups, launch sequencing, and maturity posture for the current repository.",
        "path": "docs/HELIOS_LAUNCH_BLUEPRINT.md",
        "order": 17,
    },
    {
        "slug": "review-response",
        "title": "Review Response",
        "summary": "Condensed color-coded response to the review with current-state corrections and optional enhancement roadmap.",
        "path": "docs/HELIOS_REVIEW_RESPONSE.md",
        "order": 18,
    },
    {
        "slug": "claims-coverage-matrix",
        "title": "Claims Coverage Matrix",
        "summary": "Claim-by-claim map of what the repository now covers, what is provider-gated, and what still remains for production.",
        "path": "docs/HELIOS_CLAIMS_COVERAGE_MATRIX.md",
        "order": 19,
    },
]


def _site_base_url() -> str:
    return f"https://{HeliosConfig.DOMAIN}"


def _doc_absolute_path(path: str) -> Path:
    return REPO_ROOT / path


def _doc_record(record: dict) -> dict:
    site_base_url = _site_base_url()
    return {
        **record,
        "source_path": record["path"],
        "web_url": f"{site_base_url}/handoff/docs/{record['slug']}",
        "raw_url": f"{site_base_url}/handoff/docs/{record['slug']}/raw",
        "download_url": f"{site_base_url}/handoff/docs/{record['slug']}/download",
        "api_url": f"{site_base_url}/api/handoff/docs/{record['slug']}",
    }


def list_handoff_docs() -> list[dict]:
    return [_doc_record(record) for record in sorted(HANDOFF_DOCS, key=lambda item: item["order"])]


def get_handoff_doc(slug: str) -> dict | None:
    for record in HANDOFF_DOCS:
        if record["slug"] != slug:
            continue

        absolute_path = _doc_absolute_path(record["path"])
        content = absolute_path.read_text(encoding="utf-8")
        enriched = _doc_record(record)
        enriched["content"] = content
        enriched["html"] = render_markdown(content)
        return enriched
    return None


def render_markdown(content: str) -> str:
    if markdown_lib:
        return markdown_lib.markdown(
            content,
            extensions=["extra", "sane_lists", "tables", "toc"],
        )

    return f'<pre class="handoff-markdown-fallback">{escape(content)}</pre>'


def get_handoff_manifest() -> dict:
    site_base_url = _site_base_url()
    return {
        "domain": HeliosConfig.DOMAIN,
        "site_base_url": site_base_url,
        "default_route": "Route B — Simplified launch route",
        "default_route_key": "simplified",
        "default_watermark_mode": "hidden",
        "source_of_truth": "Repository docs mirrored through the handoff portal",
        "recommended_stack": ["Flask", "Postgres", "Stripe", "Xaman", "XRPL", "Cloudflare"],
        "defer_until_phase_two": [
            "Redis/Celery",
            "Coinbase Commerce",
            "WalletConnect",
            "Prometheus/Grafana",
            "advanced operator tooling",
        ],
        "retrieval": {
            "portal": f"{site_base_url}/handoff",
            "docs_index": f"{site_base_url}/api/handoff/docs",
            "manifest": f"{site_base_url}/api/handoff/manifest",
        },
        "github": {
            "source_repo": "https://github.com/FTHTrading/Helios",
            "launch_repo": "https://github.com/FTHTrading/Helios-launch",
            "source_tree": "https://github.com/FTHTrading/Helios/tree/main",
            "launch_tree": "https://github.com/FTHTrading/Helios-launch/tree/main",
        },
        "built_system": [
            "Onboarding and activation pages",
            "Funding catalog and Stripe checkout orchestration",
            "Payment event persistence and webhook path",
            "Xaman wallet sign-in and trustline staging",
            "XRPL issuance and anchoring bridge",
            "Treasury evidence and optional IPFS pinning path",
            "Build fingerprint and readiness endpoints",
            "Site-based handoff portal and mirrored launch docs",
            "Build-aware AI advisory path for future questions",
        ],
        "env_requirements": [
            "HELIOS_DATABASE_URL",
            "HELIOS_STRIPE_SECRET_KEY",
            "HELIOS_STRIPE_PUBLISHABLE_KEY",
            "HELIOS_STRIPE_WEBHOOK_SECRET",
            "HELIOS_XAMAN_API_KEY",
            "HELIOS_XAMAN_API_SECRET",
            "HELIOS_XRPL_ISSUER_WALLET",
            "HELIOS_XRPL_ISSUER_SECRET",
            "HELIOS_XRPL_TREASURY_WALLET",
            "HELIOS_XRPL_TREASURY_SECRET",
            "HELIOS_XRPL_ENABLE_SUBMIT",
            "HELIOS_WATERMARK_MODE",
            "HELIOS_BUILD_ID",
            "HELIOS_BUILD_WATERMARK",
            "HELIOS_LAUNCH_KEY",
            "HELIOS_DEPLOYMENT_ROUTE",
            "HELIOS_BUILD_OWNER",
            "HELIOS_CF_TOKEN",
            "HELIOS_CF_ZONE_ID",
        ],
        "validation_endpoints": [
            "/health",
            "/api/infra/build",
            "/api/infra/readiness",
            "/api/infra/launch-readiness",
            "/api/funding/catalog",
            "/activate",
            "/web3",
        ],
        "security_note": "Do not embed long-lived provider secrets in the site. Rotate deployment credentials after build and burn temporary tokens.",
        "docs": list_handoff_docs(),
    }