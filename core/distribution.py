"""
Helios Distribution Engine
───────────────────────────
5-channel distribution system for member cards and invitations.
Aligned to heliosdigital.xyz — the live gold platform.

Channels:
  1. Link    — copy shareable URL
  2. QR      — generate/download QR code
  3. vCard   — downloadable .vcf contact
  4. Text    — SMS/iMessage share
  5. Invite  — native share API or clipboard fallback

Language and CTAs match the live site:
  - "Join the Helios Club — $99.95"
  - "Modern digital gold platform"
  - .helios namespace, Gold Desk, reserve-aware infrastructure
"""

from dataclasses import dataclass
from typing import Optional
from config import HeliosConfig


# ─── Member Tier System (matches live site /founder and /premium) ──
TIER_LABELS = {
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


@dataclass
class ShareObject:
    """Structured share payload for Open Graph and distribution."""
    title: str
    description: str
    url: str
    image_url: Optional[str] = None
    member_name: Optional[str] = None
    tier: Optional[str] = None

    def to_og_dict(self) -> dict:
        """Generate Open Graph meta tags."""
        return {
            "og:title": self.title,
            "og:description": self.description,
            "og:url": self.url,
            "og:image": self.image_url or f"https://{HeliosConfig.DOMAIN}/static/img/og-helios.svg",
            "og:type": "website",
            "og:site_name": "Helios",
        }

    def to_twitter_dict(self) -> dict:
        """Generate Twitter Card meta."""
        return {
            "twitter:card": "summary_large_image",
            "twitter:title": self.title,
            "twitter:description": self.description,
            "twitter:image": self.image_url or f"https://{HeliosConfig.DOMAIN}/static/img/og-helios.svg",
        }


class DistributionEngine:
    """Orchestrates all 5 distribution channels for Helios members."""

    DOMAIN = HeliosConfig.DOMAIN

    # ─── Channel Definitions ─────────────────────────────────────

    CHANNELS = {
        "link": {
            "label": "Copy Link",
            "icon": "🔗",
            "description": "Copy your personal invite link",
            "requires_js": True,
        },
        "qr": {
            "label": "QR Code",
            "icon": "📱",
            "description": "Download or display your QR code",
            "requires_js": False,
        },
        "vcard": {
            "label": "Save Contact",
            "icon": "👤",
            "description": "Download as a contact card",
            "requires_js": False,
        },
        "text": {
            "label": "Text",
            "icon": "💬",
            "description": "Send via SMS or iMessage",
            "requires_js": True,
        },
        "invite": {
            "label": "Share",
            "icon": "📤",
            "description": "Share via native share sheet",
            "requires_js": True,
        },
    }

    @classmethod
    def build_club_url(cls) -> str:
        """Build the canonical Helios Club join URL."""
        return f"https://{cls.DOMAIN}/club"

    @classmethod
    def build_invite_url(cls, display_name: str) -> str:
        """Build the personalized invite URL for a member."""
        return f"https://{cls.DOMAIN}/club?ref={display_name}"

    @classmethod
    def build_card_url(cls, display_name: str) -> str:
        """Build the URL for the premium member card page."""
        return f"https://{cls.DOMAIN}/card/{display_name}"

    @classmethod
    def build_drop_url(cls, display_name: str) -> str:
        """Build the lightweight drop page URL (for QR scans)."""
        return f"https://{cls.DOMAIN}/drop/{display_name}"

    @classmethod
    def build_qr_url(cls, display_name: str) -> str:
        """Build the full QR code page URL."""
        return f"https://{cls.DOMAIN}/qr/{display_name}"

    @classmethod
    def build_vcard_url(cls, display_name: str) -> str:
        """Build the vCard download endpoint URL."""
        return f"https://{cls.DOMAIN}/api/identity/{display_name}/vcard"

    @classmethod
    def build_text_url(cls, display_name: str, is_founder: bool = False) -> str:
        """Build an SMS share URL with pre-filled message."""
        invite_url = cls.build_invite_url(display_name)
        if is_founder:
            message = (
                f"I'd like to invite you to Helios — a modern digital gold platform. "
                f"Founding membership, your own .helios namespace, Gold Desk access, "
                f"and guided onboarding. Join through my personal link: {invite_url}"
            )
        else:
            message = (
                f"I joined Helios — a modern digital gold platform with gold certificates, "
                f"sovereign .helios identity, and reserve-aware infrastructure. "
                f"Join with founding access: {invite_url}"
            )
        return f"sms:?&body={_url_encode(message)}"

    @classmethod
    def build_share_object(cls, member_data: dict) -> ShareObject:
        """Create a rich share object for a member."""
        display_name = member_data.get("display_name", "member")
        helios_id = member_data.get("helios_id", "member.helios")
        is_founder = member_data.get("is_founder", False)

        tier = "founder" if is_founder else member_data.get("tier", "founder")
        tier_label = TIER_LABELS.get(tier, "Helios Member")

        if is_founder:
            description = (
                f"Join Helios through {display_name.title()}'s founding invitation. "
                "Modern digital gold platform with founding membership, "
                ".helios namespace, Gold Desk access, and reserve-aware infrastructure."
            )
        else:
            description = (
                f"Join Helios through {display_name.title()}. "
                "Founding membership, .helios namespace, gold certificates, "
                "and guided onboarding — $99.95 one-time."
            )

        return ShareObject(
            title=f"{display_name.title()} — {tier_label} | Helios",
            description=description,
            url=cls.build_invite_url(display_name),
            member_name=display_name,
            tier=tier_label,
        )

    @classmethod
    def get_channels_for_template(cls, display_name: str, is_founder: bool = False) -> list:
        """
        Returns all 5 channel configs ready for template rendering.
        Each channel includes: key, label, icon, url, action, description.
        """
        return [
            {
                "key": "link",
                "label": "Copy Link",
                "icon": "🔗",
                "url": cls.build_invite_url(display_name),
                "action": "copy",
                "description": "Copy your personal invitation link",
            },
            {
                "key": "qr",
                "label": "QR Code",
                "icon": "📱",
                "url": cls.build_qr_url(display_name),
                "action": "navigate",
                "description": "View and download your QR code",
            },
            {
                "key": "vcard",
                "label": "Save Contact",
                "icon": "👤",
                "url": cls.build_vcard_url(display_name),
                "action": "download",
                "description": "Download as a contact card",
            },
            {
                "key": "text",
                "label": "Text",
                "icon": "💬",
                "url": cls.build_text_url(display_name, is_founder),
                "action": "navigate",
                "description": "Send invite via text message",
            },
            {
                "key": "invite",
                "label": "Share",
                "icon": "📤",
                "url": cls.build_invite_url(display_name),
                "action": "share",
                "description": "Share via device share sheet",
            },
        ]

    @classmethod
    def get_drop_context(cls, member_data: dict) -> dict:
        """
        Build full template context for card and drop pages.
        This is what someone sees when they scan a QR code or visit a member's card.
        """
        display_name = member_data.get("display_name", "member")
        helios_id = member_data.get("helios_id", "member.helios")
        is_founder = member_data.get("is_founder", False)
        created_at = member_data.get("member_since", "")

        tier = "founder" if is_founder else member_data.get("tier", "founder")
        tier_label = TIER_LABELS.get(tier, "Helios Member")

        share_obj = cls.build_share_object(member_data)

        return {
            "display_name": display_name,
            "helios_id": helios_id,
            "tier": tier,
            "tier_label": tier_label,
            "is_founder": is_founder,
            "created_at": created_at,
            "club_url": cls.build_club_url(),
            "invite_url": cls.build_invite_url(display_name),
            "card_url": cls.build_card_url(display_name),
            "qr_url": cls.build_qr_url(display_name),
            "vcard_url": cls.build_vcard_url(display_name),
            "channels": cls.get_channels_for_template(display_name, is_founder),
            "share": share_obj,
            "og": share_obj.to_og_dict(),
            "twitter": share_obj.to_twitter_dict(),
        }


def _url_encode(text: str) -> str:
    """URL-encode a string for SMS body params."""
    import urllib.parse
    return urllib.parse.quote(text, safe="")
