"""
Funding engine for Helios.
Builds the monetization catalog that best fits the current Flask/XRPL infrastructure.
"""

from __future__ import annotations

import importlib
import uuid
from datetime import datetime, timezone

from config import HeliosConfig
from core.integrations import IntegrationReadiness


class FundingEngine:
    """Catalog and checkout helpers for the funding model."""

    TOKEN_PRICE_USD = 0.05

    def __init__(self, db_session=None):
        self.db = db_session

    OFFERS = {
        "entry": {
            "name": "Atomic Entry",
            "amount_usd": HeliosConfig.ENTRY_FEE_USD,
            "mode": "payment",
            "category": "activation",
            "description": "Primary conversion event that funds onboarding and protocol activation.",
            "token_amount": int(HeliosConfig.ENTRY_FEE_USD / TOKEN_PRICE_USD),
            "featured": False,
        },
        "builder": {
            "name": "Builder Activation",
            "amount_usd": 250,
            "mode": "payment",
            "category": "activation",
            "description": "Mid-tier founding activation with expanded allocation power.",
            "token_amount": int(250 / TOKEN_PRICE_USD),
            "featured": False,
        },
        "protocol": {
            "name": "Protocol Contract",
            "amount_usd": 500,
            "mode": "payment",
            "category": "activation",
            "description": "Founding sweet spot with the strongest value-to-entry ratio.",
            "token_amount": int(500 / TOKEN_PRICE_USD),
            "featured": True,
        },
        "accelerator": {
            "name": "Accelerator Activation",
            "amount_usd": 1000,
            "mode": "payment",
            "category": "activation",
            "description": "High-conviction activation for larger allocation and treasury participation.",
            "token_amount": int(1000 / TOKEN_PRICE_USD),
            "featured": False,
        },
        "architect": {
            "name": "Protocol Architect Activation",
            "amount_usd": 5000,
            "mode": "payment",
            "category": "activation",
            "description": "Highest activation tier for operators building directly on the protocol.",
            "token_amount": int(5000 / TOKEN_PRICE_USD),
            "featured": False,
        },
        "plus": {
            "name": "Plus Membership",
            "amount_usd": HeliosConfig.TIER_PLUS_MONTHLY_USD,
            "mode": "subscription",
            "interval": "month",
            "category": "subscription",
            "description": "Vault access recurring revenue.",
        },
        "pro": {
            "name": "Pro Membership",
            "amount_usd": HeliosConfig.TIER_PRO_MONTHLY_USD,
            "mode": "subscription",
            "interval": "month",
            "category": "subscription",
            "description": "Vault + spaces + advanced protocol access.",
        },
        "operator": {
            "name": "Operator Membership",
            "amount_usd": HeliosConfig.TIER_OPERATOR_MONTHLY_USD,
            "mode": "subscription",
            "interval": "month",
            "category": "subscription",
            "description": "Highest-value recurring plan for hosts and operators.",
        },
        "credential_operator": {
            "name": "Operator Credential",
            "amount_usd": HeliosConfig.CREDENTIAL_OPERATOR_FEE_USD,
            "mode": "payment",
            "category": "credential",
            "description": "Annual operator credential revenue.",
        },
        "credential_vendor": {
            "name": "Vendor Credential",
            "amount_usd": HeliosConfig.CREDENTIAL_VENDOR_FEE_USD,
            "mode": "payment",
            "category": "credential",
            "description": "Annual vendor credential revenue.",
        },
        "credential_host": {
            "name": "Host Credential",
            "amount_usd": HeliosConfig.CREDENTIAL_HOST_FEE_USD,
            "mode": "payment",
            "category": "credential",
            "description": "Annual host credential revenue.",
        },
    }

    def get_catalog(self) -> dict:
        offers = []
        activation_tiers = []
        subscriptions = []
        credentials = []
        featured_offer = None
        for code, offer in self.OFFERS.items():
            payload = self._offer_payload(code, offer)
            offers.append(payload)
            if offer["category"] == "activation":
                activation_tiers.append(payload)
                if offer.get("featured"):
                    featured_offer = payload
            elif offer["category"] == "subscription":
                subscriptions.append(payload)
            elif offer["category"] == "credential":
                credentials.append(payload)

        return {
            "recommended_stack": {
                "chain": "XRPL",
                "wallet": "Xaman / XUMM",
                "payments": "Stripe",
                "evidence": "Pinata + IPFS",
            },
            "execution_flow": [
                "Create hosted checkout",
                "Receive Stripe webhook",
                "Inject entry energy or activate subscription",
                "Record payment event history",
            ],
            "offers": offers,
            "activation_tiers": activation_tiers,
            "subscriptions": subscriptions,
            "credentials": credentials,
            "featured_offer": featured_offer,
            "best_funding_mix": [
                "Atomic entry conversions",
                "Recurring Plus/Pro/Operator subscriptions",
                "Annual operator/vendor/host credentials",
                "Paid spaces and events after launch",
            ],
            "next_best_step": "Enable Stripe checkout for entry, then add recurring memberships.",
            "readiness": IntegrationReadiness.snapshot()["providers"],
        }

    def create_checkout(self, offer_code: str, quantity: int = 1,
                        customer_email: str | None = None,
                        member_id: str | None = None,
                        metadata: dict | None = None) -> dict:
        offer = self.OFFERS.get(offer_code)
        if not offer:
            raise ValueError(f"Unknown funding offer: {offer_code}")
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        metadata = {**(metadata or {})}
        if member_id:
            metadata.setdefault("member_id", member_id)
        metadata.setdefault("offer_code", offer_code)
        metadata.setdefault("quantity", str(quantity))

        if not self._stripe_ready():
            return {
                "status": "not_configured",
                "offer": self._offer_payload(offer_code, offer),
                "quantity": quantity,
                "amount_total_usd": round(offer["amount_usd"] * quantity, 2),
                "member_id": member_id,
                "message": "Stripe is not configured. Add HELIOS_STRIPE_SECRET_KEY to enable hosted checkout.",
            }

        stripe = importlib.import_module("stripe")

        stripe.api_key = HeliosConfig.STRIPE_SECRET_KEY
        price_data = {
            "currency": "usd",
            "unit_amount": int(round(offer["amount_usd"] * 100)),
            "product_data": {
                "name": offer["name"],
                "description": offer["description"],
            },
        }
        if offer["mode"] == "subscription":
            price_data["recurring"] = {"interval": offer.get("interval", "month")}

        session = stripe.checkout.Session.create(
            mode=offer["mode"],
            success_url=HeliosConfig.PAYMENTS_SUCCESS_URL,
            cancel_url=HeliosConfig.PAYMENTS_CANCEL_URL,
            customer_email=customer_email,
            metadata=metadata,
            line_items=[{
                "quantity": quantity,
                "price_data": price_data,
            }],
        )

        self._record_payment_event(
            external_id=session.id,
            reference_id=session.id,
            provider="stripe",
            event_type="checkout.session.created",
            member_id=member_id,
            offer_code=offer_code,
            mode=offer["mode"],
            status="created",
            amount_usd=round(offer["amount_usd"] * quantity, 2),
            raw_payload={"session_id": session.id, "url": session.url, "metadata": metadata},
        )

        return {
            "status": "created",
            "offer": self._offer_payload(offer_code, offer),
            "quantity": quantity,
            "amount_total_usd": round(offer["amount_usd"] * quantity, 2),
            "checkout_url": session.url,
            "session_id": session.id,
        }

    def process_stripe_webhook(self, payload: bytes | str, signature: str | None = None) -> dict:
        if not self._stripe_ready():
            raise ValueError("Stripe is not configured.")

        stripe = importlib.import_module("stripe")
        stripe.api_key = HeliosConfig.STRIPE_SECRET_KEY
        payload_bytes = payload if isinstance(payload, bytes) else payload.encode("utf-8")

        if HeliosConfig.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload=payload_bytes,
                sig_header=signature,
                secret=HeliosConfig.STRIPE_WEBHOOK_SECRET,
            )
        else:
            # Fail-closed: refuse unverified webhooks in production.
            raise ValueError(
                "STRIPE_WEBHOOK_SECRET is not configured. "
                "Cannot process unverified webhook payloads."
            )

        event_type = event.get("type")
        event_id = event.get("id") or f"evt_{uuid.uuid4().hex}"
        data_object = event.get("data", {}).get("object", {})
        metadata = data_object.get("metadata", {}) or {}

        self._record_payment_event(
            external_id=event_id,
            reference_id=data_object.get("id"),
            provider="stripe",
            event_type=event_type,
            member_id=metadata.get("member_id"),
            offer_code=metadata.get("offer_code"),
            mode=data_object.get("mode") or data_object.get("object"),
            status="received",
            amount_usd=(data_object.get("amount_total") or 0) / 100,
            raw_payload=event,
        )

        if event_type == "checkout.session.completed":
            fulfillment = self._fulfill_offer(
                offer_code=metadata.get("offer_code"),
                member_id=metadata.get("member_id"),
                session_id=data_object.get("id"),
                amount_total=(data_object.get("amount_total") or 0) / 100,
                metadata=metadata,
            )
            return {"received": True, "fulfilled": True, "fulfillment": fulfillment, "event_type": event_type}

        return {"received": True, "fulfilled": False, "event_type": event_type}

    def get_payment_event(self, external_id: str) -> dict:
        if not self.db:
            raise ValueError("Database session is required to read payment events.")
        from models.payment_event import PaymentEvent

        event = self.db.query(PaymentEvent).filter_by(external_id=external_id).first()
        if not event:
            raise ValueError(f"Payment event {external_id} not found")
        return event.to_dict()

    def _fulfill_offer(self, offer_code: str | None, member_id: str | None,
                       session_id: str | None, amount_total: float, metadata: dict) -> dict:
        if not self.db:
            return {
                "status": "deferred",
                "reason": "Database session unavailable",
                "offer_code": offer_code,
                "member_id": member_id,
            }

        if not offer_code:
            raise ValueError("Webhook metadata missing offer_code")

        offer = self.OFFERS.get(offer_code or "")
        if offer and offer.get("category") == "activation":
            if not member_id:
                raise ValueError("Entry fulfillment requires member_id metadata")
            from core.energy_exchange import EnergyExchange
            from models.transaction import Transaction

            resolved_amount = amount_total or offer["amount_usd"]
            result = EnergyExchange(self.db).inject_entry_energy(member_id=member_id, amount_usd=resolved_amount)
            self.db.add(Transaction(
                member_id=member_id,
                activity_type=f"activation_{offer_code}_confirmed",
                value=float(resolved_amount),
                extra_data={
                    "session_id": session_id,
                    "offer_code": offer_code,
                    "token_amount": offer.get("token_amount"),
                },
            ))
            self.db.commit()
            return {
                "status": "energy_injected",
                "offer": self._offer_payload(offer_code, offer),
                "result": result,
            }

        if offer_code in {"plus", "pro", "operator"}:
            if not member_id:
                raise ValueError("Subscription fulfillment requires member_id metadata")
            return self._activate_subscription(member_id, offer_code, amount_total, session_id)

        return self._record_non_subscription_purchase(member_id, offer_code, amount_total, session_id, metadata)

    def _activate_subscription(self, member_id: str, tier: str, amount_total: float, session_id: str | None) -> dict:
        from models.subscription import Subscription

        subscription = self.db.query(Subscription).filter_by(member_id=member_id).first()
        if not subscription:
            subscription = Subscription(
                subscription_id=f"SUB-{uuid.uuid4().hex[:16].upper()}",
                member_id=member_id,
            )
            self.db.add(subscription)

        subscription.tier = tier
        subscription.monthly_fee_usd = self.OFFERS[tier]["amount_usd"]
        subscription.is_active = True
        subscription.total_paid_usd = float(subscription.total_paid_usd or 0) + float(amount_total or self.OFFERS[tier]["amount_usd"])
        subscription.months_active = int(subscription.months_active or 0) + 1
        subscription.vault_access = tier in {"plus", "pro", "operator"}
        subscription.space_access = tier in {"pro", "operator"}
        subscription.credential_access = tier in {"pro", "operator"}
        subscription.operator_tools = tier == "operator"
        self.db.commit()
        return {
            "status": "subscription_activated",
            "member_id": member_id,
            "tier": tier,
            "session_id": session_id,
            "subscription_id": subscription.subscription_id,
        }

    def _record_non_subscription_purchase(self, member_id: str | None, offer_code: str, amount_total: float,
                                          session_id: str | None, metadata: dict) -> dict:
        from models.transaction import Transaction

        if member_id:
            self.db.add(Transaction(
                member_id=member_id,
                activity_type=f"purchase_{offer_code}",
                value=float(amount_total or self.OFFERS[offer_code]["amount_usd"]),
                extra_data={"session_id": session_id, "metadata": metadata},
            ))
            self.db.commit()
        return {
            "status": "purchase_recorded",
            "member_id": member_id,
            "offer_code": offer_code,
            "session_id": session_id,
        }

    def _offer_payload(self, code: str, offer: dict) -> dict:
        payload = {"code": code, **offer}
        if offer.get("category") == "activation":
            token_amount = int(offer.get("token_amount") or (offer["amount_usd"] / self.TOKEN_PRICE_USD))
            payload["token_amount"] = token_amount
            payload["token_price_usd"] = self.TOKEN_PRICE_USD
            payload["wallet_flow"] = [
                "Create Helios identity",
                "Complete hosted checkout",
                "Connect Xaman wallet",
                "Open XRPL trustline",
                "Receive HLS + XLS-20 certificates",
            ]
        return payload

    def _record_payment_event(self, external_id: str, reference_id: str | None, provider: str,
                              event_type: str, member_id: str | None, offer_code: str | None,
                              mode: str | None, status: str, amount_usd: float, raw_payload: dict):
        if not self.db:
            return None
        from models.payment_event import PaymentEvent

        event = self.db.query(PaymentEvent).filter_by(external_id=external_id).first()
        if not event:
            event = PaymentEvent(external_id=external_id, provider=provider, event_type=event_type)
            self.db.add(event)

        event.reference_id = reference_id
        event.member_id = member_id
        event.offer_code = offer_code
        event.mode = mode
        event.status = status
        event.amount_usd = amount_usd or 0.0
        event.raw_payload = raw_payload
        event.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return event

    @staticmethod
    def _stripe_ready() -> bool:
        providers = IntegrationReadiness.snapshot()["providers"]
        return bool(providers["stripe"]["ready"])
