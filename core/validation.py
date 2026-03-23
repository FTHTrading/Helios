"""Request validation helpers for Helios API routes."""

from __future__ import annotations

from marshmallow import Schema, ValidationError, fields, validate


class IdentityCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=24))
    referrer = fields.Str(load_default=None, allow_none=True)


class WalletSendSchema(Schema):
    from_id = fields.Str(required=True)
    to_id = fields.Str(required=True)
    amount = fields.Decimal(required=True, as_string=False)
    note = fields.Str(load_default="", validate=validate.Length(max=280))


class FundingCheckoutSchema(Schema):
    offer_code = fields.Str(required=True)
    quantity = fields.Int(load_default=1, validate=validate.Range(min=1, max=25))
    customer_email = fields.Email(load_default=None, allow_none=True)
    member_id = fields.Str(load_default=None, allow_none=True)
    metadata = fields.Dict(load_default=dict)


class EnergyInjectSchema(Schema):
    member_id = fields.Str(required=True)
    amount_usd = fields.Float(load_default=None, allow_none=True, validate=validate.Range(min=1))


class TreasuryReceiptSchema(Schema):
    dealer = fields.Str(required=True)
    invoice_id = fields.Str(required=True)
    purchase_date = fields.Str(required=True)
    metal = fields.Str(required=True)
    form = fields.Str(required=True)
    purity = fields.Str(load_default="0.9999")
    weight_oz = fields.Float(required=True, validate=validate.Range(min=0.0001))
    quantity = fields.Int(load_default=1, validate=validate.Range(min=1))
    unit_cost_usd = fields.Float(required=True, validate=validate.Range(min=0.01))
    serials = fields.List(fields.Str(), load_default=list)
    evidence_cid = fields.Str(load_default=None, allow_none=True)
    evidence_sha256 = fields.Str(load_default=None, allow_none=True)


class TreasuryAnchorSchema(Schema):
    mvr_id = fields.Str(required=True)
    tx_hash = fields.Str(load_default=None, allow_none=True)
    issuer_wallet = fields.Str(load_default=None, allow_none=True)
    attestation_wallet = fields.Str(load_default=None, allow_none=True)


class XamanPayloadSchema(Schema):
    action = fields.Str(required=True, validate=validate.OneOf(["signin", "trustline", "payment"]))
    member_id = fields.Str(load_default=None, allow_none=True)
    account = fields.Str(load_default=None, allow_none=True)
    destination = fields.Str(load_default=None, allow_none=True)
    amount = fields.Float(load_default=None, allow_none=True)


class LinkCreateSchema(Schema):
    initiator_id = fields.Str(required=True, validate=validate.Length(min=3, max=64))
    peer_id = fields.Str(required=True, validate=validate.Length(min=3, max=64))


class LinkDissolveSchema(Schema):
    initiator_id = fields.Str(required=True, validate=validate.Length(min=3, max=64))
    peer_id = fields.Str(required=True, validate=validate.Length(min=3, max=64))


# ─── Schemas for previously-unvalidated POST routes ───────────────────

class EnergyPropagateSchema(Schema):
    origin_id = fields.Str(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    event_type = fields.Str(load_default="join")


class EnergyExecuteSchema(Schema):
    origin_id = fields.Str(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    event_type = fields.Str(load_default="join")


class CertificateMintSchema(Schema):
    holder_id = fields.Str(required=True)
    energy_amount_he = fields.Float(required=True, validate=validate.Range(min=0.0001))
    energy_value_usd = fields.Float(required=True, validate=validate.Range(min=0.01))


class CertificateRedeemSchema(Schema):
    certificate_id = fields.Str(required=True)
    mvr_id = fields.Str(load_default=None, allow_none=True)


class CertificateCancelSchema(Schema):
    certificate_id = fields.Str(required=True)


class TreasuryCustodySchema(Schema):
    mvr_id = fields.Str(required=True)
    status = fields.Str(required=True)


class TreasuryAllocationSchema(Schema):
    net_surplus_usd = fields.Float(required=True, validate=validate.Range(min=0))
    coefficient = fields.Float(load_default=None, allow_none=True)


class SpaceCreateSchema(Schema):
    owner_id = fields.Str(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    description = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=500))
    is_public = fields.Bool(load_default=True)
    entry_fee_usd = fields.Float(load_default=0, validate=validate.Range(min=0))
    max_members = fields.Int(load_default=500, validate=validate.Range(min=1, max=10000))


class SpaceEventSchema(Schema):
    space_id = fields.Str(required=True)
    host_id = fields.Str(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=1000))
    event_type = fields.Str(load_default="general")
    ticket_price_usd = fields.Float(load_default=0, validate=validate.Range(min=0))
    max_attendees = fields.Int(load_default=100, validate=validate.Range(min=1, max=50000))
    starts_at = fields.Str(load_default=None, allow_none=True)
    ends_at = fields.Str(load_default=None, allow_none=True)


_SCHEMAS = {
    "identity_create": IdentityCreateSchema(),
    "wallet_send": WalletSendSchema(),
    "funding_checkout": FundingCheckoutSchema(),
    "energy_inject": EnergyInjectSchema(),
    "energy_propagate": EnergyPropagateSchema(),
    "energy_execute": EnergyExecuteSchema(),
    "treasury_receipt": TreasuryReceiptSchema(),
    "treasury_anchor": TreasuryAnchorSchema(),
    "treasury_custody": TreasuryCustodySchema(),
    "treasury_allocation": TreasuryAllocationSchema(),
    "certificate_mint": CertificateMintSchema(),
    "certificate_redeem": CertificateRedeemSchema(),
    "certificate_cancel": CertificateCancelSchema(),
    "xaman_payload": XamanPayloadSchema(),
    "link_create": LinkCreateSchema(),
    "link_dissolve": LinkDissolveSchema(),
    "space_create": SpaceCreateSchema(),
    "space_event": SpaceEventSchema(),
}


def validate_payload(schema_name: str, payload: dict | None) -> dict:
    schema = _SCHEMAS[schema_name]
    try:
        return schema.load(payload or {})
    except ValidationError as exc:
        raise ValueError(exc.messages)
