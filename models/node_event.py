"""
Node Event model — full telemetry spine for Helios member QR nodes.

Every QR code is a live member node. Every scan, join, wallet init,
activation, issuance, and chain propagation is captured as a NodeEvent.
This is the event-sourced foundation for member attribution, stats,
real-time dashboards, and recursive network propagation tracking.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Boolean, JSON
from models.member import Base


class NodeEvent(Base):
    __tablename__ = "node_events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ═══ Event Classification ═══
    event_type = Column(String(50), nullable=False, index=True)
    # Event types:
    #   qr_view, qr_scan, join_page_open,
    #   wallet_init_started, wallet_init_completed, trustline_created,
    #   activation_selected, payment_started, payment_completed,
    #   member_created, hls_issued, membership_nft_minted, ceremonial_nft_minted,
    #   reward_accrued, reward_distributed,
    #   child_node_created, share_link_copied, invite_sent,
    #   network_depth_increased

    # ═══ Attribution Chain ═══
    issuer_slug = Column(String(64), nullable=False, index=True)   # e.g. "kenny"
    issuer_wallet = Column(String(128), nullable=True)             # XRPL/Stellar wallet
    referral_code = Column(String(128), nullable=True)             # join URL or QR code ID
    parent_member_id = Column(String(64), nullable=True, index=True)  # who referred the issuer
    child_member_id = Column(String(64), nullable=True, index=True)   # newly created member (if applicable)

    # ═══ Session Tracking ═══
    session_id = Column(String(128), nullable=True, index=True)    # browser session
    device_id = Column(String(128), nullable=True)                 # device fingerprint
    ip_hash = Column(String(64), nullable=True)                    # hashed IP for dedup
    user_agent = Column(String(256), nullable=True)                # browser UA

    # ═══ Financial / Issuance Data ═══
    amount_paid = Column(Float, nullable=True)                     # fiat amount (USD)
    hls_amount = Column(Float, nullable=True)                      # HLS tokens issued
    offer_code = Column(String(32), nullable=True)                 # entry/builder/protocol/etc.
    tx_hash = Column(String(128), nullable=True)                   # on-chain tx hash
    nft_token_ids = Column(JSON, nullable=True)                    # list of minted NFT IDs

    # ═══ Chain / Propagation ═══
    chain_depth = Column(Integer, nullable=True)                   # depth from root
    chain_path = Column(JSON, nullable=True)                       # full ancestry path
    network_size_after = Column(Integer, nullable=True)            # total network size after event

    # ═══ State / Outcome ═══
    status = Column(String(20), default="completed")               # completed, pending, failed
    error_code = Column(String(50), nullable=True)                 # error classification
    error_detail = Column(Text, nullable=True)                     # error message

    # ═══ Metadata ═══
    extra = Column(JSON, nullable=True)                            # extensible payload
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<NodeEvent {self.event_type} issuer={self.issuer_slug} @{self.timestamp}>"

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "issuer_slug": self.issuer_slug,
            "issuer_wallet": self.issuer_wallet,
            "referral_code": self.referral_code,
            "parent_member_id": self.parent_member_id,
            "child_member_id": self.child_member_id,
            "session_id": self.session_id,
            "amount_paid": self.amount_paid,
            "hls_amount": self.hls_amount,
            "offer_code": self.offer_code,
            "tx_hash": self.tx_hash,
            "nft_token_ids": self.nft_token_ids,
            "chain_depth": self.chain_depth,
            "chain_path": self.chain_path,
            "status": self.status,
            "error_code": self.error_code,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
