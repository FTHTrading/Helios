"""
Helios Distribution Engine
───────────────────────────
5-channel distribution system for member cards and invitations.

Channels:
  1. Link    — copy shareable URL
  2. QR      — generate/download QR code
  3. vCard   — downloadable .vcf contact
  4. Text    — SMS/iMessage share
  5. Invite  — native share API or clipboard fallback

The Forward Doctrine: "Even when the backend is complex,
the product must feel simple, clear, premium, and easy to trust."
"""

from dataclasses import dataclass
from typing import Optional
from config import HeliosConfig


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
            "og:site_name": "Helios Protocol",
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
            "description": "Copy your personal join link",
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
    def build_join_url(cls, display_name: str) -> str:
        """Build the canonical join URL for a member."""
        return f"https://{cls.DOMAIN}/join/{display_name}"

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
        join_url = cls.build_join_url(display_name)
        tier_word = "founder" if is_founder else "member"
        message = (
            f"I'm inviting you to Helios — a gold-backed smart contract protocol. "
            f"Join through my personal link as a {tier_word} connection: {join_url}"
        )
        # sms: URI scheme works on iOS and Android
        return f"sms:?&body={_url_encode(message)}"

    @classmethod
    def build_share_object(cls, member_data: dict) -> ShareObject:
        """Create a rich share object for a member."""
        display_name = member_data.get("display_name", "member")
        helios_id = member_data.get("helios_id", "member.helios")
        is_founder = member_data.get("is_founder", False)
        node_state = member_data.get("node_state", "instantiated")

        tier = "Founding Member" if is_founder else {
            "stable": "Verified Node",
            "propagating": "Network Propagator",
            "connected": "Connected Member",
        }.get(node_state, "Helios Member")

        return ShareObject(
            title=f"{display_name.title()} — {tier} | Helios Protocol",
            description=(
                f"Join Helios through {display_name.title()}. "
                "Gold-backed smart contract protocol. One payment. "
                "Fully autonomous. XRPL & Stellar settlement."
            ),
            url=cls.build_join_url(display_name),
            member_name=display_name,
            tier=tier,
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
                "url": cls.build_join_url(display_name),
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
                "url": cls.build_join_url(display_name),
                "action": "share",
                "description": "Share via device share sheet",
            },
        ]

    @classmethod
    def get_drop_context(cls, member_data: dict) -> dict:
        """
        Build full template context for the drop landing page.
        This is what someone sees when they scan a QR code.
        """
        display_name = member_data.get("display_name", "member")
        helios_id = member_data.get("helios_id", "member.helios")
        is_founder = member_data.get("is_founder", False)
        node_state = member_data.get("node_state", "instantiated")
        bond_count = member_data.get("bond_count", 0)
        created_at = member_data.get("member_since", "")

        tier = "founder" if is_founder else node_state
        tier_label = "Founding Member" if is_founder else {
            "stable": "Verified Node",
            "propagating": "Network Propagator",
            "connected": "Connected Member",
            "acknowledged": "Registered Member",
            "instantiated": "New Member",
        }.get(node_state, "Helios Member")

        share_obj = cls.build_share_object(member_data)

        return {
            "display_name": display_name,
            "helios_id": helios_id,
            "tier": tier,
            "tier_label": tier_label,
            "is_founder": is_founder,
            "bond_count": bond_count,
            "created_at": created_at,
            "join_url": cls.build_join_url(display_name),
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
