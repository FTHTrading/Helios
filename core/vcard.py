"""
Helios vCard System
───────────────────
Generates premium .vcf contact cards for Helios members.
When a founder hands you their card, it should feel like receiving
an invitation to something exclusive — not a business card from a filing cabinet.

vCard 3.0 spec — maximum device compatibility (iOS, Android, Outlook, macOS).
"""

from datetime import datetime, timezone
from config import HeliosConfig


class HeliosVCard:
    """Generates downloadable vCard (.vcf) files for Helios members."""

    DOMAIN = HeliosConfig.DOMAIN

    # ─── Tier Titles ──────────────────────────────────────────────
    TIER_TITLES = {
        "founder":      "Founding Member",
        "genesis":      "Genesis Member",
        "propagating":  "Network Propagator",
        "stable":       "Verified Node",
        "connected":    "Connected Member",
        "acknowledged": "Registered Member",
        "instantiated": "New Member",
    }

    TIER_ORG = {
        "founder":      "Helios Protocol — Founding Council",
        "genesis":      "Helios Protocol — Genesis Circle",
        "propagating":  "Helios Protocol — Network",
        "stable":       "Helios Protocol — Network",
        "connected":    "Helios Protocol",
        "acknowledged": "Helios Protocol",
        "instantiated": "Helios Protocol",
    }

    @classmethod
    def generate(cls, member_data: dict) -> str:
        """
        Generate a vCard 3.0 string from member data.

        Args:
            member_data: dict with keys:
                - helios_id: str (e.g. "kenny.helios")
                - display_name: str (e.g. "kenny")
                - node_state: str (e.g. "propagating")
                - is_founder: bool
                - created_at: str (ISO datetime)
                - bond_count: int (optional)
                - email: str (optional)
                - phone: str (optional)

        Returns:
            vCard 3.0 formatted string
        """
        helios_id = member_data.get("helios_id", "member.helios")
        display_name = member_data.get("display_name", "Member")
        node_state = member_data.get("node_state", "instantiated")
        is_founder = member_data.get("is_founder", False)
        created_at = member_data.get("created_at", "")
        bond_count = member_data.get("bond_count", 0)

        # Determine tier
        tier = "founder" if is_founder else node_state
        title = cls.TIER_TITLES.get(tier, "Helios Member")
        org = cls.TIER_ORG.get(tier, "Helios Protocol")

        # Build vCard lines
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{display_name.title()}",
            f"N:{display_name.title()};;;;",
            f"ORG:{org}",
            f"TITLE:{title}",
            f"URL:https://{cls.DOMAIN}/join/{display_name}",
            f"NOTE:Helios Network — {helios_id}\\n"
            f"Tier: {title}\\n"
            f"Bonds: {bond_count}\\n"
            f"Join: https://{cls.DOMAIN}/join/{display_name}\\n"
            f"Card: https://{cls.DOMAIN}/card/{display_name}\\n"
            f"Protocol: Smart-contract governed. Gold-backed certificates. XRPL settlement.",
        ]

        # Optional fields
        email = member_data.get("email")
        if email:
            lines.append(f"EMAIL;TYPE=INTERNET:{email}")

        phone = member_data.get("phone")
        if phone:
            lines.append(f"TEL;TYPE=CELL:{phone}")

        # Categories based on tier
        if is_founder:
            lines.append("CATEGORIES:Helios,Founder,Protocol Council")
        else:
            lines.append(f"CATEGORIES:Helios,{title}")

        # Revision timestamp
        rev = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        lines.append(f"REV:{rev}")

        # Custom fields (X-properties for rich clients)
        lines.append(f"X-HELIOS-ID:{helios_id}")
        lines.append(f"X-HELIOS-TIER:{tier}")
        lines.append(f"X-HELIOS-BONDS:{bond_count}")
        lines.append(f"X-HELIOS-JOIN:https://{cls.DOMAIN}/join/{display_name}")

        lines.append("END:VCARD")

        return "\r\n".join(lines)

    @classmethod
    def generate_filename(cls, display_name: str, is_founder: bool = False) -> str:
        """Generate a premium filename for the vCard download."""
        prefix = "Helios-Founder" if is_founder else "Helios-Member"
        safe_name = display_name.replace(" ", "-").lower()
        return f"{prefix}-{safe_name}.vcf"

    @classmethod
    def content_type(cls) -> str:
        """MIME type for vCard files."""
        return "text/vcard; charset=utf-8"

    @classmethod
    def content_disposition(cls, filename: str) -> str:
        """Content-Disposition header value for download."""
        return f'attachment; filename="{filename}"'
