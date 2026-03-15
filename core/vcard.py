"""
Helios vCard System
───────────────────
Generates premium .vcf contact cards for Helios members.
When a founder hands you their card, it should feel like receiving
an invitation to something exclusive — not a business card from a filing cabinet.

vCard 3.0 spec — maximum device compatibility (iOS, Android, Outlook, macOS).

Aligned to heliosdigital.xyz — the live gold platform.
"""

from datetime import datetime, timezone
from config import HeliosConfig


class HeliosVCard:
    """Generates downloadable vCard (.vcf) files for Helios members."""

    DOMAIN = HeliosConfig.DOMAIN

    # ─── Member Tier Titles (matches live site tier system) ───────
    TIER_TITLES = {
        "founder":        "Founding Member",
        "silver":         "Silver Member",
        "gold":           "Gold Member",
        "platinum":       "Platinum Member",
        "diamond":        "Diamond Member",
        "gold_desk":      "Gold Desk Member",
        "strategic":      "Strategic Member",
        "premier":        "Premier Member",
        "institutional":  "Institutional Member",
    }

    TIER_ORG = {
        "founder":        "Helios — Founding Member",
        "silver":         "Helios — Silver",
        "gold":           "Helios — Gold",
        "platinum":       "Helios — Platinum",
        "diamond":        "Helios — Diamond",
        "gold_desk":      "Helios — Gold Desk",
        "strategic":      "Helios — Strategic Access",
        "premier":        "Helios — Premier Reserve",
        "institutional":  "Helios — Institutional",
    }

    @classmethod
    def _resolve_tier(cls, member_data: dict) -> str:
        """Resolve the display tier from member data."""
        if member_data.get("is_founder", False):
            return "founder"
        return member_data.get("tier", "founder")

    @classmethod
    def generate(cls, member_data: dict) -> str:
        """
        Generate a vCard 3.0 string from member data.

        Args:
            member_data: dict with keys:
                - helios_id: str (e.g. "kevan.helios")
                - display_name: str (e.g. "kevan")
                - tier: str (e.g. "founder", "gold", "platinum")
                - is_founder: bool
                - created_at: str (ISO datetime)
                - email: str (optional)
                - phone: str (optional)

        Returns:
            vCard 3.0 formatted string
        """
        helios_id = member_data.get("helios_id", "member.helios")
        display_name = member_data.get("display_name", "Member")
        is_founder = member_data.get("is_founder", False)
        created_at = member_data.get("created_at", "")

        tier = cls._resolve_tier(member_data)
        title = cls.TIER_TITLES.get(tier, "Helios Member")
        org = cls.TIER_ORG.get(tier, "Helios")

        # Club join URL — the canonical CTA
        club_url = f"https://{cls.DOMAIN}/club"
        card_url = f"https://{cls.DOMAIN}/card/{display_name}"

        # Build vCard lines
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{display_name.title()}",
            f"N:{display_name.title()};;;;",
            f"ORG:{org}",
            f"TITLE:{title}",
            f"URL:{card_url}",
            f"NOTE:{helios_id}\\n"
            f"{title}\\n"
            f"Helios — Modern digital gold platform\\n"
            f"Founding membership · .helios namespace · Gold Desk access\\n"
            f"Join: {club_url}\\n"
            f"Card: {card_url}",
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
            lines.append("CATEGORIES:Helios,Founding Member,Gold Platform")
        else:
            lines.append(f"CATEGORIES:Helios,{title}")

        # Revision timestamp
        rev = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        lines.append(f"REV:{rev}")

        # Custom X-properties for rich clients
        lines.append(f"X-HELIOS-ID:{helios_id}")
        lines.append(f"X-HELIOS-TIER:{tier}")
        lines.append(f"X-HELIOS-NAMESPACE:{helios_id}")
        lines.append(f"X-HELIOS-CLUB:{club_url}")

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
