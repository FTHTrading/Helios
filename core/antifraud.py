"""
Anti-Fraud Engine — rate limiting, dedup, bot detection, reward guardrails.

Every node event passes through this engine before persisting.
Designed for soft-launch: conservative thresholds, clear audit trail.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from models.node_event import NodeEvent


# ═══ Known Bot User-Agent Patterns ════════════════════════════════════

BOT_UA_PATTERNS = re.compile(
    r"(bot|crawl|spider|scrape|headless|phantom|selenium|puppeteer|"
    r"wget|curl/|python-requests|httpx|aiohttp|node-fetch|"
    r"googlebot|bingbot|yandex|baidu|slurp|duckduck|facebookexternalhit|"
    r"twitterbot|linkedinbot|whatsapp|telegrambot)",
    re.IGNORECASE,
)

# ═══ Thresholds ═══════════════════════════════════════════════════════

# Events from same IP+session within this window are considered duplicates
DEDUP_WINDOW_SECONDS = 30

# Max events per IP per hour (across all event types)
IP_RATE_LIMIT_PER_HOUR = 120

# Max events per session per hour
SESSION_RATE_LIMIT_PER_HOUR = 200

# Max join events from a single referrer per day
MAX_JOINS_PER_REFERRER_PER_DAY = 50

# Max reward distributions per member per day
MAX_REWARDS_PER_MEMBER_PER_DAY = 100

# Suspiciously fast: events from same IP faster than this are flagged
RAPID_FIRE_SECONDS = 2


class AntifraudResult:
    """Result of anti-fraud check."""

    def __init__(self, allowed: bool, reason: str = "", code: str = ""):
        self.allowed = allowed
        self.reason = reason
        self.code = code

    def __bool__(self):
        return self.allowed

    def to_dict(self):
        return {"allowed": self.allowed, "reason": self.reason, "code": self.code}


class AntifraudEngine:
    """
    Pre-persist validation layer for node events.
    
    Checks (in order):
    1. Bot detection (user-agent analysis)
    2. Duplicate suppression (same event_type + ip_hash + session within window)
    3. IP rate limiting (max events per IP per hour)
    4. Session rate limiting (max events per session per hour)
    5. Referrer join caps (max joins per referrer per day)
    6. Reward guardrails (max reward events per member per day)
    7. Rapid-fire detection (events faster than threshold)
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def check(
        self,
        event_type: str,
        issuer_slug: str,
        *,
        ip_hash: str = None,
        session_id: str = None,
        user_agent: str = None,
        device_id: str = None,
    ) -> AntifraudResult:
        """
        Run all anti-fraud checks. Returns AntifraudResult.
        If .allowed is False, the event should be rejected.
        """

        # 1. Bot detection
        if user_agent and BOT_UA_PATTERNS.search(user_agent):
            return AntifraudResult(
                False,
                "Automated user-agent detected",
                "BOT_DETECTED",
            )

        # 2. Empty UA on non-view events is suspicious
        if not user_agent and event_type not in ("qr_view", "qr_scan"):
            return AntifraudResult(
                False,
                "Missing user-agent on non-scan event",
                "MISSING_UA",
            )

        now = datetime.now(timezone.utc)

        # 3. Duplicate suppression
        if ip_hash and session_id:
            dedup_cutoff = now - timedelta(seconds=DEDUP_WINDOW_SECONDS)
            dup = self.db.query(NodeEvent.id).filter(
                NodeEvent.event_type == event_type,
                NodeEvent.ip_hash == ip_hash,
                NodeEvent.session_id == session_id,
                NodeEvent.issuer_slug == issuer_slug.replace(".helios", ""),
                NodeEvent.timestamp >= dedup_cutoff,
            ).first()
            if dup:
                return AntifraudResult(
                    False,
                    f"Duplicate {event_type} within {DEDUP_WINDOW_SECONDS}s window",
                    "DUPLICATE",
                )

        # 4. IP rate limiting
        if ip_hash:
            hour_cutoff = now - timedelta(hours=1)
            ip_count = self.db.query(func.count(NodeEvent.id)).filter(
                NodeEvent.ip_hash == ip_hash,
                NodeEvent.timestamp >= hour_cutoff,
            ).scalar() or 0
            if ip_count >= IP_RATE_LIMIT_PER_HOUR:
                return AntifraudResult(
                    False,
                    f"IP rate limit exceeded ({ip_count}/{IP_RATE_LIMIT_PER_HOUR} per hour)",
                    "IP_RATE_LIMIT",
                )

        # 5. Session rate limiting
        if session_id:
            hour_cutoff = now - timedelta(hours=1)
            sess_count = self.db.query(func.count(NodeEvent.id)).filter(
                NodeEvent.session_id == session_id,
                NodeEvent.timestamp >= hour_cutoff,
            ).scalar() or 0
            if sess_count >= SESSION_RATE_LIMIT_PER_HOUR:
                return AntifraudResult(
                    False,
                    f"Session rate limit exceeded ({sess_count}/{SESSION_RATE_LIMIT_PER_HOUR} per hour)",
                    "SESSION_RATE_LIMIT",
                )

        # 6. Referrer join caps
        if event_type in ("member_created", "child_node_created"):
            day_cutoff = now - timedelta(days=1)
            join_count = self.db.query(func.count(NodeEvent.id)).filter(
                NodeEvent.issuer_slug == issuer_slug.replace(".helios", ""),
                NodeEvent.event_type.in_(["member_created", "child_node_created"]),
                NodeEvent.timestamp >= day_cutoff,
            ).scalar() or 0
            if join_count >= MAX_JOINS_PER_REFERRER_PER_DAY:
                return AntifraudResult(
                    False,
                    f"Referrer join cap exceeded ({join_count}/{MAX_JOINS_PER_REFERRER_PER_DAY} per day)",
                    "REFERRER_JOIN_CAP",
                )

        # 7. Reward guardrails
        if event_type in ("reward_accrued", "reward_distributed"):
            day_cutoff = now - timedelta(days=1)
            reward_count = self.db.query(func.count(NodeEvent.id)).filter(
                NodeEvent.issuer_slug == issuer_slug.replace(".helios", ""),
                NodeEvent.event_type.in_(["reward_accrued", "reward_distributed"]),
                NodeEvent.timestamp >= day_cutoff,
            ).scalar() or 0
            if reward_count >= MAX_REWARDS_PER_MEMBER_PER_DAY:
                return AntifraudResult(
                    False,
                    f"Reward cap exceeded ({reward_count}/{MAX_REWARDS_PER_MEMBER_PER_DAY} per day)",
                    "REWARD_CAP",
                )

        # 8. Rapid-fire detection (flag but allow — just mark for review)
        if ip_hash:
            rapid_cutoff = now - timedelta(seconds=RAPID_FIRE_SECONDS)
            rapid = self.db.query(NodeEvent.id).filter(
                NodeEvent.ip_hash == ip_hash,
                NodeEvent.timestamp >= rapid_cutoff,
            ).first()
            if rapid:
                # Allow but log as suspicious
                # The event will be persisted with a flag
                return AntifraudResult(
                    True,
                    "Rapid-fire detected — event allowed but flagged",
                    "RAPID_FIRE_FLAG",
                )

        return AntifraudResult(True)

    def get_suspicious_nodes(self, hours: int = 24) -> list:
        """
        Scan for suspicious activity patterns across all nodes.
        Returns list of alerts for the ops dashboard.
        """
        alerts = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        # 1. Nodes with abnormally high event counts in the period
        high_volume = self.db.query(
            NodeEvent.issuer_slug,
            func.count(NodeEvent.id).label("count"),
        ).filter(
            NodeEvent.timestamp >= cutoff,
        ).group_by(
            NodeEvent.issuer_slug,
        ).having(
            func.count(NodeEvent.id) > 100
        ).all()

        for slug, count in high_volume:
            alerts.append({
                "node": f"{slug}.helios",
                "reason": "High event volume",
                "detail": f"{count} events in {hours}h",
                "severity": "warning",
            })

        # 2. IPs with events across many different nodes (possible scraping)
        ip_spread = self.db.query(
            NodeEvent.ip_hash,
            func.count(func.distinct(NodeEvent.issuer_slug)).label("node_count"),
        ).filter(
            NodeEvent.timestamp >= cutoff,
            NodeEvent.ip_hash.isnot(None),
        ).group_by(
            NodeEvent.ip_hash,
        ).having(
            func.count(func.distinct(NodeEvent.issuer_slug)) > 10
        ).all()

        for ip, node_count in ip_spread:
            alerts.append({
                "node": f"IP:{ip[:8]}…",
                "reason": "Single IP hitting many nodes",
                "detail": f"{node_count} different nodes from one IP",
                "severity": "warning",
            })

        # 3. Nodes with joins but zero scans (possible direct-POST abuse)
        no_scan_joins = self.db.query(
            NodeEvent.issuer_slug,
            func.count(NodeEvent.id).label("join_count"),
        ).filter(
            NodeEvent.event_type.in_(["member_created", "child_node_created"]),
            NodeEvent.timestamp >= cutoff,
        ).group_by(
            NodeEvent.issuer_slug,
        ).all()

        for slug, join_count in no_scan_joins:
            scan_count = self.db.query(func.count(NodeEvent.id)).filter(
                NodeEvent.issuer_slug == slug,
                NodeEvent.event_type.in_(["qr_scan", "qr_view"]),
                NodeEvent.timestamp >= cutoff,
            ).scalar() or 0
            if join_count > 3 and scan_count == 0:
                alerts.append({
                    "node": f"{slug}.helios",
                    "reason": "Joins without scans",
                    "detail": f"{join_count} joins, 0 scans — possible API abuse",
                    "severity": "critical",
                })

        # 4. Failed events spike
        failed_nodes = self.db.query(
            NodeEvent.issuer_slug,
            func.count(NodeEvent.id).label("fail_count"),
        ).filter(
            NodeEvent.status == "failed",
            NodeEvent.timestamp >= cutoff,
        ).group_by(
            NodeEvent.issuer_slug,
        ).having(
            func.count(NodeEvent.id) > 5
        ).all()

        for slug, fail_count in failed_nodes:
            alerts.append({
                "node": f"{slug}.helios",
                "reason": "High failure rate",
                "detail": f"{fail_count} failed events in {hours}h",
                "severity": "warning",
            })

        return sorted(alerts, key=lambda a: 0 if a["severity"] == "critical" else 1)
