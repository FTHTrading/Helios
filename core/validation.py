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


_SCHEMAS = {
    "identity_create": IdentityCreateSchema(),
    "wallet_send": WalletSendSchema(),
    "funding_checkout": FundingCheckoutSchema(),
    "energy_inject": EnergyInjectSchema(),
    "treasury_receipt": TreasuryReceiptSchema(),
    "treasury_anchor": TreasuryAnchorSchema(),
    "xaman_payload": XamanPayloadSchema(),
    "link_create": LinkCreateSchema(),
    "link_dissolve": LinkDissolveSchema(),
}


def validate_payload(schema_name: str, payload: dict | None) -> dict:
    schema = _SCHEMAS[schema_name]
    try:
        return schema.load(payload or {})
    except ValidationError as exc:
        raise ValueError(exc.messages)
