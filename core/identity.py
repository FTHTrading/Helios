"""
Helios Identity System
─────────────────────
Permanent, human-readable IDs: name.helios
No crypto jargon. No wallet addresses shown. QR-based sharing.
"""

import re
import hashlib
import secrets
import qrcode
import io
import base64
from datetime import datetime, timezone
from config import HeliosConfig


class HeliosIdentity:
    """Manages the name.helios identity layer."""

    # Allowed characters: lowercase alphanumeric, hyphens, underscores
    NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_-]*$')

    def __init__(self, db_session):
        self.db = db_session

    # ─── Registration ─────────────────────────────────────────────

    def create_id(self, name: str, referrer_helios_id: str = None) -> dict:
        """
        Register a new Helios ID — instantiate a node in the field.

        Args:
            name: Desired name (without .helios suffix)
            referrer_helios_id: The peer who introduced them (optional)

        Returns:
            dict with helios_id, recovery_phrase, qr_code, created_at
        """
        name = name.lower().strip()
        self._validate_name(name)

        helios_id = f"{name}{HeliosConfig.IDENTITY_SUFFIX}"

        # Check availability
        from models.member import Member
        if self.db.query(Member).filter_by(helios_id=helios_id).first():
            raise ValueError(f"'{helios_id}' is already taken. Try another name.")

        # Generate internal crypto identity (hidden from user)
        internal_key = secrets.token_hex(32)
        key_hash = hashlib.sha256(internal_key.encode()).hexdigest()

        # Generate human-friendly recovery phrase (12 words)
        recovery_phrase = self._generate_recovery_phrase()

        # Create member record
        member = Member(
            helios_id=helios_id,
            display_name=name,
            key_hash=key_hash,
            recovery_hash=hashlib.sha256(
                " ".join(recovery_phrase).encode()
            ).hexdigest(),
            referrer_id=referrer_helios_id,
            created_at=datetime.now(timezone.utc),
            status="active"
        )
        self.db.add(member)
        self.db.commit()

        # Generate QR code for sharing
        qr_data = self._generate_qr(helios_id)

        return {
            "helios_id": helios_id,
            "recovery_phrase": recovery_phrase,
            "qr_code": qr_data,
            "created_at": member.created_at.isoformat(),
            "message": (
                f"Welcome to Helios, {name}! "
                "Save your recovery phrase somewhere safe — "
                "it's the only way to recover your account."
            ),
            "_internal_key": internal_key  # Stored client-side only, never on server
        }

    def verify_id(self, helios_id: str) -> dict:
        """Look up a Helios ID and return public info."""
        from models.member import Member
        member = self.db.query(Member).filter_by(
            helios_id=helios_id, status="active"
        ).first()

        if not member:
            return {"exists": False, "helios_id": helios_id}

        return {
            "exists": True,
            "helios_id": member.helios_id,
            "display_name": member.display_name,
            "member_since": member.created_at.isoformat(),
            "bond_count": self._get_bond_count(member.helios_id),
            "node_state": member.node_state,
            "activity_score": self._get_activity_score(member.helios_id),
            "verified": member.verified
        }

    def recover_account(self, helios_id: str, recovery_phrase: list) -> dict:
        """Recover account access using the 12-word phrase."""
        from models.member import Member
        member = self.db.query(Member).filter_by(helios_id=helios_id).first()

        if not member:
            raise ValueError("Helios ID not found.")

        phrase_hash = hashlib.sha256(" ".join(recovery_phrase).encode()).hexdigest()
        if phrase_hash != member.recovery_hash:
            raise ValueError("Recovery phrase does not match.")

        # Generate new internal key
        new_key = secrets.token_hex(32)
        member.key_hash = hashlib.sha256(new_key.encode()).hexdigest()
        self.db.commit()

        return {
            "helios_id": helios_id,
            "recovered": True,
            "_internal_key": new_key,
            "message": "Account recovered. Your old key is now invalid."
        }

    # ─── QR Code Generation ──────────────────────────────────────

    def _generate_qr(self, helios_id: str) -> str:
        """Generate a QR code for sharing a Helios ID. Returns base64 PNG."""
        join_url = f"https://{HeliosConfig.DOMAIN}/enter/{helios_id}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(join_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#1a1a2e", back_color="#ffffff")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def get_join_qr(self, helios_id: str) -> str:
        """Public method to get a shareable QR code."""
        return self._generate_qr(helios_id)

    # ─── Validation ───────────────────────────────────────────────

    def _validate_name(self, name: str):
        """Enforce naming rules."""
        if len(name) < HeliosConfig.IDENTITY_MIN_LENGTH:
            raise ValueError(
                f"Name must be at least {HeliosConfig.IDENTITY_MIN_LENGTH} characters."
            )
        if len(name) > HeliosConfig.IDENTITY_MAX_LENGTH:
            raise ValueError(
                f"Name must be {HeliosConfig.IDENTITY_MAX_LENGTH} characters or less."
            )
        if not self.NAME_PATTERN.match(name):
            raise ValueError(
                "Name can only contain lowercase letters, numbers, hyphens, "
                "and underscores. Must start with a letter."
            )
        if name in HeliosConfig.IDENTITY_RESERVED:
            raise ValueError(f"'{name}' is reserved and cannot be registered.")

    # ─── Helpers ──────────────────────────────────────────────────

    def _generate_recovery_phrase(self, word_count: int = 12) -> list:
        """Generate a BIP39-style recovery phrase."""
        words = [
            "sun", "moon", "star", "fire", "wave", "stone", "light", "seed",
            "path", "gold", "wind", "rain", "tree", "peak", "flow", "dawn",
            "rise", "glow", "forge", "pulse", "spark", "drift", "bloom",
            "crest", "vault", "echo", "flame", "orbit", "nexus", "prism",
            "shield", "bridge", "crown", "anchor", "beacon", "cipher",
            "delta", "ember", "frost", "grove", "haven", "ivory", "jewel",
            "karma", "lotus", "maple", "noble", "oasis", "pearl", "quest",
            "ridge", "solar", "terra", "unity", "vigor", "zenith", "atlas",
            "brave", "coral", "depth", "eagle", "faith", "grace", "honor"
        ]
        return [secrets.choice(words) for _ in range(word_count)]

    def _get_bond_count(self, helios_id: str) -> int:
        """Count active bonds for a node."""
        from models.bond import Bond
        count = self.db.query(Bond).filter(
            ((Bond.node_a == helios_id) | (Bond.node_b == helios_id)),
            Bond.state == "active"
        ).count()
        return count

    def _get_activity_score(self, helios_id: str) -> float:
        """Calculate activity score for the last 30 days."""
        from models.transaction import Transaction
        from datetime import timedelta
        window = HeliosConfig.FIELD_ACTIVITY_WINDOW_DAYS
        cutoff = datetime.now(timezone.utc) - timedelta(days=window)
        # SQLite stores naive datetimes — compare naive to avoid TypeError
        cutoff_naive = cutoff.replace(tzinfo=None)
        txns = self.db.query(Transaction).filter(
            Transaction.member_id == helios_id,
            Transaction.created_at >= cutoff_naive
        ).count()
        # Normalize: 1 txn/day = score of 100
        return min(round(txns / window * 100, 1), 100.0)
