"""
Helios Wallet Abstraction
─────────────────────────
Hidden complexity. Balance-only view. No keys exposed.
Users see: balance, history, send/receive.
Users DON'T see: private keys, gas, chain IDs, hex addresses.
"""

from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
from config import HeliosConfig


class HeliosWallet:
    """
    Abstracted wallet that hides all crypto complexity.
    Users interact with Helios IDs, not addresses.
    """

    def __init__(self, db_session):
        self.db = db_session

    # ─── Balance ──────────────────────────────────────────────────────

    def get_balance(self, helios_id: str) -> dict:
        """Get simple balance view for a member."""
        from models.reward import Reward
        from models.wallet_tx import WalletTransaction
        from sqlalchemy import func

        # Total earned from rewards
        earned = self.db.query(
            func.sum(Reward.amount)
        ).filter(
            Reward.member_id == helios_id,
            Reward.status == "settled"
        ).scalar() or Decimal('0')

        # Total sent
        sent = self.db.query(
            func.sum(WalletTransaction.amount)
        ).filter(
            WalletTransaction.from_id == helios_id,
            WalletTransaction.status == "completed"
        ).scalar() or Decimal('0')

        # Total received (transfers from other members)
        received = self.db.query(
            func.sum(WalletTransaction.amount)
        ).filter(
            WalletTransaction.to_id == helios_id,
            WalletTransaction.status == "completed"
        ).scalar() or Decimal('0')

        balance = Decimal(str(earned)) + Decimal(str(received)) - Decimal(str(sent))

        return {
            "helios_id": helios_id,
            "balance": float(balance),
            "token": HeliosConfig.TOKEN_SYMBOL,
            "earned": float(earned),
            "sent": float(sent),
            "received": float(received),
            "display": f"{float(balance):,.2f} {HeliosConfig.TOKEN_SYMBOL}"
        }

    # ─── Transfers ────────────────────────────────────────────────────

    def send(self, from_id: str, to_id: str, amount: float, note: str = "") -> dict:
        """
        Send HLS to another Helios member.
        No gas. No addresses. Just name.helios → name.helios.

        Uses SELECT … FOR UPDATE on the sender row to serialise
        concurrent transfers and prevent double-spend.
        """
        from models.member import Member
        from models.wallet_tx import WalletTransaction
        from sqlalchemy import func as sa_func

        amount_d = Decimal(str(amount)).quantize(
            Decimal('0.00000001'), rounding=ROUND_DOWN
        )

        if amount_d <= 0:
            raise ValueError("Amount must be positive.")

        if from_id == to_id:
            raise ValueError("Cannot send to yourself.")

        try:
            # Lock sender row to serialise concurrent balance checks.
            # with_for_update() issues SELECT … FOR UPDATE on supported
            # backends; on SQLite it's a no-op but SQLite serialises
            # writes at the DB level anyway.
            sender = self.db.query(Member).filter_by(
                helios_id=from_id, status="active"
            ).with_for_update().first()
            if not sender:
                raise ValueError(f"Sender '{from_id}' not found.")

            # Verify recipient (no lock needed — read-only)
            receiver = self.db.query(Member).filter_by(
                helios_id=to_id, status="active"
            ).first()
            if not receiver:
                raise ValueError(f"Recipient '{to_id}' not found.")

            # Compute balance inside the locked transaction
            from models.reward import Reward
            earned = self.db.query(
                sa_func.sum(Reward.amount)
            ).filter(
                Reward.member_id == from_id,
                Reward.status == "settled"
            ).scalar() or Decimal('0')

            sent_total = self.db.query(
                sa_func.sum(WalletTransaction.amount)
            ).filter(
                WalletTransaction.from_id == from_id,
                WalletTransaction.status == "completed"
            ).scalar() or Decimal('0')

            received_total = self.db.query(
                sa_func.sum(WalletTransaction.amount)
            ).filter(
                WalletTransaction.to_id == from_id,
                WalletTransaction.status == "completed"
            ).scalar() or Decimal('0')

            current_balance = Decimal(str(earned)) + Decimal(str(received_total)) - Decimal(str(sent_total))
            if current_balance < amount_d:
                raise ValueError(
                    f"Insufficient balance. You have {float(current_balance):,.2f} {HeliosConfig.TOKEN_SYMBOL}."
                )

            # Execute transfer
            tx = WalletTransaction(
                from_id=from_id,
                to_id=to_id,
                amount=float(amount_d),
                note=note[:280] if note else "",
                status="completed",
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(tx)
            self.db.commit()

        except ValueError:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise

        return {
            "success": True,
            "transaction_id": tx.id,
            "from": from_id,
            "to": to_id,
            "amount": float(amount_d),
            "note": note,
            "new_balance": self.get_balance(from_id)["display"],
            "timestamp": tx.created_at.isoformat(),
            "message": f"Sent {float(amount_d):,.2f} {HeliosConfig.TOKEN_SYMBOL} to {to_id}"
        }

    # ─── Transaction History ──────────────────────────────────────────

    def get_history(self, helios_id: str, limit: int = 50) -> list:
        """Get wallet transaction history — simple, human-readable."""
        from models.wallet_tx import WalletTransaction
        from models.reward import Reward

        # Get transfers
        transfers = self.db.query(WalletTransaction).filter(
            (WalletTransaction.from_id == helios_id) |
            (WalletTransaction.to_id == helios_id)
        ).order_by(WalletTransaction.created_at.desc()).limit(limit).all()

        # Get rewards
        rewards = self.db.query(Reward).filter_by(
            member_id=helios_id, status="settled"
        ).order_by(Reward.created_at.desc()).limit(limit).all()

        # Combine and sort
        history = []

        for tx in transfers:
            is_sent = tx.from_id == helios_id
            history.append({
                "type": "sent" if is_sent else "received",
                "amount": tx.amount,
                "other_party": tx.to_id if is_sent else tx.from_id,
                "note": tx.note,
                "date": tx.created_at.isoformat(),
                "display": (
                    f"{'Sent' if is_sent else 'Received'} "
                    f"{tx.amount:,.2f} {HeliosConfig.TOKEN_SYMBOL} "
                    f"{'to' if is_sent else 'from'} "
                    f"{tx.to_id if is_sent else tx.from_id}"
                )
            })

        for r in rewards:
            history.append({
                "type": "reward",
                "amount": r.amount,
                "other_party": r.source_member_id,
                "note": r.reason,
                "date": r.created_at.isoformat(),
                "display": (
                    f"Earned {r.amount:,.2f} {HeliosConfig.TOKEN_SYMBOL} — {r.reason}"
                )
            })

        # Sort by date descending
        history.sort(key=lambda x: x["date"], reverse=True)
        return history[:limit]

    # ─── Export (Advanced Users) ──────────────────────────────────────

    def export_key(self, helios_id: str, internal_key: str) -> dict:
        """
        For advanced users who want to export their private key.
        This reveals the underlying crypto — most users should never need this.
        """
        from models.member import Member
        import hashlib

        member = self.db.query(Member).filter_by(helios_id=helios_id).first()
        if not member:
            raise ValueError("Member not found.")

        # Verify the internal key
        key_hash = hashlib.sha256(internal_key.encode()).hexdigest()
        if key_hash != member.key_hash:
            raise ValueError("Invalid key. Cannot export.")

        return {
            "helios_id": helios_id,
            "private_key": internal_key,
            "warning": (
                "This is your private key. Anyone with this key controls your account. "
                "Never share it. Helios support will NEVER ask for it."
            ),
            "chain_id": HeliosConfig.CHAIN_ID,
            "exported_at": datetime.now(timezone.utc).isoformat()
        }

    # ─── Receive QR ───────────────────────────────────────────────────

    def get_receive_qr(self, helios_id: str) -> dict:
        """Generate a QR code for receiving payments."""
        import qrcode
        import io
        import base64

        pay_url = f"helios://pay/{helios_id}"

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(pay_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#1a1a2e", back_color="#ffffff")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_b64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            "helios_id": helios_id,
            "qr_code": qr_b64,
            "pay_url": pay_url,
            "message": f"Scan to send {HeliosConfig.TOKEN_SYMBOL} to {helios_id}"
        }
