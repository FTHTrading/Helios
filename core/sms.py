"""
Helios SMS — Telnyx Phone Verification & Notifications
───────────────────────────────────────────────────────
Phone verification for onboarding. SMS notifications for rewards.
No spam. Only things you asked for.
"""

import hashlib
import secrets
import time
from datetime import datetime, timezone, timedelta
from config import HeliosConfig
class HeliosSMS:
    """
    SMS engine powered by Telnyx.
    - Phone verification during join flow
    - Reward notifications (opt-in only)
    - Security alerts

    Verification codes are persisted to the database so they
    survive restarts and work across multiple worker processes.
    """

    def __init__(self, db_session=None):
        self.db = db_session
        self.api_key = HeliosConfig.TELNYX_API_KEY
        self.from_number = HeliosConfig.TELNYX_FROM_NUMBER
        self.available = bool(self.api_key)
        self.expiry_minutes = HeliosConfig.TELNYX_VERIFY_EXPIRY_MINUTES
        self.max_attempts = HeliosConfig.TELNYX_MAX_VERIFY_ATTEMPTS

    # ─── Phone Verification ────────────────────────────────────────────

    def send_verification(self, phone_number: str, helios_id: str = None) -> dict:
        """
        Send a 6-digit verification code via SMS.
        Returns verification_id for later confirmation.
        """
        if not self.available:
            return {
                "sent": False,
                "error": "SMS service not configured",
                "available": False
            }

        # Normalize phone number
        phone = self._normalize_phone(phone_number)
        if not phone:
            return {
                "sent": False,
                "error": "Invalid phone number. Use format: +1XXXXXXXXXX"
            }

        # Rate limiting: max 3 codes per phone per hour
        if self._is_rate_limited(phone):
            return {
                "sent": False,
                "error": "Too many verification attempts. Please wait and try again."
            }

        # Generate 6-digit code
        code = f"{secrets.randbelow(900000) + 100000}"
        verification_id = secrets.token_hex(16)

        # Store verification in database
        from models.phone_verification import PhoneVerification
        pv = PhoneVerification(
            verification_id=verification_id,
            phone_hash=hashlib.sha256(phone.encode()).hexdigest(),
            code_hash=hashlib.sha256(code.encode()).hexdigest(),
            helios_id=helios_id,
            attempts=0,
            verified=False,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=self.expiry_minutes),
        )
        if self.db:
            self.db.add(pv)
            self.db.commit()

        # Send SMS
        message = (
            f"☀️ Helios Verification\n\n"
            f"Your code: {code}\n\n"
            f"Expires in {self.expiry_minutes} minutes.\n"
            f"Never share this code with anyone."
        )

        try:
            result = self._send_sms(phone, message)

            return {
                "sent": True,
                "verification_id": verification_id,
                "phone_masked": self._mask_phone(phone),
                "expires_in": self.expiry_minutes * 60,
                "message_id": result.get("message_id")
            }

        except Exception as e:
            # Clean up on failure
            if self.db:
                pv_cleanup = self.db.query(PhoneVerification).filter_by(
                    verification_id=verification_id
                ).first()
                if pv_cleanup:
                    self.db.delete(pv_cleanup)
                    self.db.commit()
            return {
                "sent": False,
                "error": f"Failed to send SMS: {str(e)}"
            }

    def verify_code(self, verification_id: str, code: str) -> dict:
        """
        Verify a phone number with the code received via SMS.
        Uses DB-backed storage so codes survive restarts.
        """
        from models.phone_verification import PhoneVerification

        if not self.db:
            return {"verified": False, "error": "Database session unavailable"}

        pending = self.db.query(PhoneVerification).filter_by(
            verification_id=verification_id
        ).first()

        if not pending:
            return {
                "verified": False,
                "error": "Verification not found or expired"
            }

        # Check expiry
        now = datetime.now(timezone.utc)
        expires = pending.expires_at.replace(tzinfo=timezone.utc) if pending.expires_at.tzinfo is None else pending.expires_at
        if now > expires:
            self.db.delete(pending)
            self.db.commit()
            return {
                "verified": False,
                "error": "Verification code expired. Please request a new one."
            }

        # Check attempts
        pending.attempts += 1
        if pending.attempts > self.max_attempts:
            self.db.delete(pending)
            self.db.commit()
            return {
                "verified": False,
                "error": "Too many failed attempts. Please request a new code."
            }

        # Verify code
        code_hash = hashlib.sha256(code.strip().encode()).hexdigest()
        if code_hash != pending.code_hash:
            self.db.commit()  # persist attempt count
            remaining = self.max_attempts - pending.attempts
            return {
                "verified": False,
                "error": f"Wrong code. {remaining} attempts remaining."
            }

        # Success — mark as verified
        pending.verified = True
        helios_id = pending.helios_id
        # We don't store the raw phone — only the hash. Mask from hash is "***".
        phone_masked = "***"

        # Update member's verified status if helios_id available
        if helios_id:
            self._mark_member_verified(helios_id, None)

        # Cleanup
        self.db.delete(pending)
        self.db.commit()

        return {
            "verified": True,
            "phone_masked": phone_masked,
            "helios_id": helios_id,
            "message": "Phone verified successfully! ✓"
        }

    # ─── Notifications ─────────────────────────────────────────────────

    def send_reward_notification(self, phone: str, amount: float,
                                  reward_type: str, helios_id: str) -> dict:
        """Send a reward notification SMS (opt-in only)."""
        if not self.available:
            return {"sent": False, "error": "SMS not configured"}

        message = (
            f"☀️ Helios Reward\n\n"
            f"You earned {amount:.2f} HLS!\n"
            f"Type: {reward_type}\n"
            f"Account: {helios_id}\n\n"
            f"View details in your dashboard."
        )

        try:
            result = self._send_sms(phone, message)
            return {"sent": True, "message_id": result.get("message_id")}
        except Exception as e:
            return {"sent": False, "error": str(e)}

    def send_security_alert(self, phone: str, alert_type: str,
                             helios_id: str) -> dict:
        """Send a security alert SMS."""
        if not self.available:
            return {"sent": False, "error": "SMS not configured"}

        alerts = {
            "login": f"☀️ Security Alert\n\nNew login detected for {helios_id}.\nIf this wasn't you, recover your account immediately.",
            "recovery": f"☀️ Security Alert\n\nAccount recovery initiated for {helios_id}.\nIf this wasn't you, contact support immediately.",
            "large_transfer": f"☀️ Security Alert\n\nA large transfer was made from {helios_id}.\nIf this wasn't you, recover your account immediately."
        }

        message = alerts.get(alert_type, f"☀️ Security Alert for {helios_id}")

        try:
            result = self._send_sms(phone, message)
            return {"sent": True, "message_id": result.get("message_id")}
        except Exception as e:
            return {"sent": False, "error": str(e)}

    # ─── Service Status ────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Check SMS service status and configuration."""
        if not self.available:
            return {
                "status": "not_configured",
                "message": "Add HELIOS_TELNYX_API_KEY to .env"
            }

        result = {
            "status": "active",
            "from_number": self._mask_phone(self.from_number) if self.from_number else "not_set",
            "verify_expiry_minutes": self.expiry_minutes,
            "max_attempts": self.max_attempts,
            "pending_verifications": self._count_pending()
        }

        # Try to ping Telnyx API
        try:
            import requests
            response = requests.get(
                "https://api.telnyx.com/v2/balance",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json().get("data", {})
                result["balance"] = data.get("balance")
                result["currency"] = data.get("currency")
            else:
                result["api_status"] = "auth_error"
        except Exception as e:
            result["api_status"] = f"unreachable: {str(e)}"

        return result

    # ─── Telnyx API Call ───────────────────────────────────────────────

    def _send_sms(self, to: str, text: str) -> dict:
        """Send an SMS message via Telnyx API."""
        import requests

        url = "https://api.telnyx.com/v2/messages"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": self.from_number,
            "to": to,
            "text": text
        }

        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()

        data = response.json().get("data", {})
        return {
            "message_id": data.get("id"),
            "status": data.get("to", [{}])[0].get("status", "queued") if isinstance(data.get("to"), list) else "sent"
        }

    # ─── Helpers ───────────────────────────────────────────────────────

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to E.164 format."""
        import re
        # Strip all non-digit characters except leading +
        cleaned = re.sub(r'[^\d+]', '', phone)

        if cleaned.startswith('+'):
            return cleaned if len(cleaned) >= 11 else None
        elif cleaned.startswith('1') and len(cleaned) == 11:
            return f"+{cleaned}"
        elif len(cleaned) == 10:
            return f"+1{cleaned}"
        else:
            return f"+{cleaned}" if len(cleaned) >= 10 else None

    def _mask_phone(self, phone: str) -> str:
        """Mask phone number for display: +1***555****1234"""
        if not phone or len(phone) < 6:
            return "***"
        return phone[:3] + "*" * (len(phone) - 7) + phone[-4:]

    def _is_rate_limited(self, phone: str) -> bool:
        """Check if a phone number has too many recent verification attempts."""
        from models.phone_verification import PhoneVerification

        if not self.db:
            return False

        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        phone_hash = hashlib.sha256(phone.encode()).hexdigest()
        recent_count = self.db.query(PhoneVerification).filter(
            PhoneVerification.phone_hash == phone_hash,
            PhoneVerification.created_at >= one_hour_ago
        ).count()
        return recent_count >= 3

    def _count_pending(self) -> int:
        """Count pending (unverified, unexpired) verifications in the DB."""
        from models.phone_verification import PhoneVerification
        if not self.db:
            return 0
        now = datetime.now(timezone.utc)
        return self.db.query(PhoneVerification).filter(
            PhoneVerification.verified == False,
            PhoneVerification.expires_at > now
        ).count()

    def _mark_member_verified(self, helios_id: str, phone: str):
        """Mark a member as phone-verified in the database."""
        try:
            from models.member import Member
            member = self.db.query(Member).filter_by(helios_id=helios_id).first()
            if member:
                member.verified = True
                self.db.commit()
        except Exception:
            self.db.rollback()
