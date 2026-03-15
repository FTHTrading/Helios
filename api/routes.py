"""
Helios API Routes
─────────────────
Protocol-enforced REST API. No hierarchy language.
Network, not MLM. Bonds, not downlines.
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps

from core.validation import validate_payload

# ─── Blueprints ───────────────────────────────────────────────────────

identity_bp = Blueprint("identity", __name__, url_prefix="/api/identity")
field_bp = Blueprint("field", __name__, url_prefix="/api/field")
network_bp = Blueprint("network", __name__, url_prefix="/api/network")
energy_bp = Blueprint("energy", __name__, url_prefix="/api/energy")
wallet_bp = Blueprint("wallet", __name__, url_prefix="/api/wallet")
token_bp = Blueprint("token", __name__, url_prefix="/api/token")
chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")
treasury_bp = Blueprint("treasury", __name__, url_prefix="/api/treasury")
certificates_bp = Blueprint("certificates", __name__, url_prefix="/api/certificates")
spaces_bp = Blueprint("spaces", __name__, url_prefix="/api/spaces")
metrics_bp = Blueprint("metrics", __name__, url_prefix="/api/metrics")
rewards_bp = Blueprint("rewards", __name__, url_prefix="/api/rewards")
funding_bp = Blueprint("funding", __name__, url_prefix="/api/funding")
handoff_bp = Blueprint("handoff", __name__, url_prefix="/api/handoff")


def get_db():
    """Get database session from Flask g."""
    return g.db_session


def api_response(data=None, error=None, status=200):
    """Standard API response format."""
    if error:
        return jsonify({"success": False, "error": str(error)}), status
    return jsonify({"success": True, "data": data}), status


def handle_errors(f):
    """Decorator to catch and format errors."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return api_response(error=str(e), status=400)
        except Exception as e:
            return api_response(error="Something went wrong. Please try again.", status=500)
    return wrapper


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IDENTITY ROUTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@identity_bp.route("/create", methods=["POST"])
@handle_errors
def create_helios_id():
    """Register a new Helios ID — instantiate a node in the field."""
    from core.identity import HeliosIdentity

    data = validate_payload("identity_create", request.get_json())
    name = data.get("name", "").strip()
    referrer = data.get("referrer")

    identity = HeliosIdentity(get_db())
    result = identity.create_id(name, referrer)

    # Don't send internal key in API response — only in initial registration
    safe_result = {k: v for k, v in result.items() if k != "_internal_key"}
    safe_result["_key"] = result.get("_internal_key")  # Send once, client stores

    return api_response(safe_result, status=201)


@identity_bp.route("/verify/<helios_id>", methods=["GET"])
@handle_errors
def verify_helios_id(helios_id):
    """Look up a Helios ID."""
    from core.identity import HeliosIdentity

    identity = HeliosIdentity(get_db())
    result = identity.verify_id(helios_id)
    return api_response(result)


@identity_bp.route("/recover", methods=["POST"])
@handle_errors
def recover_account():
    """Recover account with 12-word phrase."""
    from core.identity import HeliosIdentity

    data = request.get_json()
    helios_id = data.get("helios_id")
    phrase = data.get("recovery_phrase", [])

    identity = HeliosIdentity(get_db())
    result = identity.recover_account(helios_id, phrase)

    safe_result = {k: v for k, v in result.items() if k != "_internal_key"}
    safe_result["_key"] = result.get("_internal_key")

    return api_response(safe_result)


@identity_bp.route("/qr/<helios_id>", methods=["GET"])
@handle_errors
def get_qr(helios_id):
    """Get shareable QR code for a Helios ID."""
    from core.identity import HeliosIdentity

    identity = HeliosIdentity(get_db())
    qr = identity.get_join_qr(helios_id)
    return api_response({"helios_id": helios_id, "qr_code": qr})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIELD ROUTES (Neural Field — Bonds, not connections)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@field_bp.route("/bond", methods=["POST"])
@handle_errors
def form_bond():
    """Form a bond between two peers. Undirected. Max 5 bonds per node."""
    from core.network import FieldEngine

    data = request.get_json()
    engine = FieldEngine(get_db())
    result = engine.form_bond(data["initiator_id"], data["peer_id"])
    return api_response(result, status=201)


@field_bp.route("/bond/dissolve", methods=["POST"])
@handle_errors
def dissolve_bond():
    """Dissolve a bond — sets state to INACTIVE."""
    from core.network import FieldEngine

    data = request.get_json()
    engine = FieldEngine(get_db())
    result = engine.dissolve_bond(data["initiator_id"], data["peer_id"])
    return api_response(result)


@field_bp.route("/graph/<helios_id>", methods=["GET"])
@handle_errors
def get_field_graph(helios_id):
    """Get the neural field graph for visualization — undirected, no hierarchy."""
    from core.network import FieldEngine

    max_hops = request.args.get("hops", type=int)
    engine = FieldEngine(get_db())
    result = engine.get_field(helios_id, max_hops=max_hops)
    return api_response(result)


@field_bp.route("/stats/<helios_id>", methods=["GET"])
@handle_errors
def get_node_stats(helios_id):
    """Get node statistics — bonds, state, field reach."""
    from core.network import FieldEngine

    engine = FieldEngine(get_db())
    result = engine.get_node_stats(helios_id)
    return api_response(result)


@field_bp.route("/bonds/<helios_id>", methods=["GET"])
@handle_errors
def get_bonds(helios_id):
    """Get direct bonds (peers)."""
    from core.network import FieldEngine

    engine = FieldEngine(get_db())
    result = engine.get_bonds(helios_id)
    return api_response(result)


@field_bp.route("/path/<from_id>/<to_id>", methods=["GET"])
@handle_errors
def get_propagation_path(from_id, to_id):
    """Get shortest path between two nodes — for settlement routing."""
    from core.network import FieldEngine

    engine = FieldEngine(get_db())
    result = engine.get_propagation_path(from_id, to_id)
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENERGY ROUTES (Propagation — acknowledgement, not commission)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@energy_bp.route("/propagate", methods=["POST"])
@handle_errors
def propagate_energy():
    """Preview energy propagation through the field (doesn't execute)."""
    from core.rewards import PropagationEngine
    from decimal import Decimal

    data = request.get_json()
    engine = PropagationEngine(get_db())
    result = engine.calculate_propagation(
        origin_id=data["origin_id"],
        energy_amount=Decimal(str(data["amount"])),
        event_type=data.get("event_type", "join")
    )
    return api_response(result)


@energy_bp.route("/execute", methods=["POST"])
@handle_errors
def execute_propagation():
    """Execute energy propagation — settle all acknowledgements."""
    from core.rewards import PropagationEngine
    from decimal import Decimal

    data = request.get_json()
    engine = PropagationEngine(get_db())
    result = engine.execute_propagation(
        origin_id=data["origin_id"],
        energy_amount=Decimal(str(data["amount"])),
        event_type=data.get("event_type", "join")
    )
    return api_response(result)


@energy_bp.route("/history/<helios_id>", methods=["GET"])
@handle_errors
def get_settlement_history(helios_id):
    """Get energy settlement history."""
    from core.rewards import PropagationEngine

    limit = request.args.get("limit", 50, type=int)
    engine = PropagationEngine(get_db())
    result = engine.get_settlement_history(helios_id, limit=limit)
    return api_response(result)


@energy_bp.route("/total/<helios_id>", methods=["GET"])
@handle_errors
def get_total_energy(helios_id):
    """Get total energy received."""
    from core.rewards import PropagationEngine

    engine = PropagationEngine(get_db())
    result = engine.get_total_energy_received(helios_id)
    return api_response(result)


@energy_bp.route("/protocol", methods=["GET"])
@handle_errors
def get_protocol_stats():
    """Public protocol statistics — anyone can verify. Settlement follows rules, not relationships."""
    from core.rewards import PropagationEngine

    engine = PropagationEngine(get_db())
    result = engine.get_protocol_stats()
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WALLET ROUTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@wallet_bp.route("/balance/<helios_id>", methods=["GET"])
@handle_errors
def get_balance(helios_id):
    """Get wallet balance."""
    from core.wallet import HeliosWallet

    wallet = HeliosWallet(get_db())
    result = wallet.get_balance(helios_id)
    return api_response(result)


@wallet_bp.route("/send", methods=["POST"])
@handle_errors
def send_tokens():
    """Send HLS to another member."""
    from core.wallet import HeliosWallet

    data = validate_payload("wallet_send", request.get_json())
    wallet = HeliosWallet(get_db())
    result = wallet.send(
        from_id=data["from_id"],
        to_id=data["to_id"],
        amount=float(data["amount"]),
        note=data.get("note", "")
    )
    return api_response(result)


@wallet_bp.route("/history/<helios_id>", methods=["GET"])
@handle_errors
def get_wallet_history(helios_id):
    """Get wallet transaction history."""
    from core.wallet import HeliosWallet

    limit = request.args.get("limit", 50, type=int)
    wallet = HeliosWallet(get_db())
    result = wallet.get_history(helios_id, limit=limit)
    return api_response(result)


@wallet_bp.route("/receive-qr/<helios_id>", methods=["GET"])
@handle_errors
def get_receive_qr(helios_id):
    """Get QR code for receiving payments."""
    from core.wallet import HeliosWallet

    wallet = HeliosWallet(get_db())
    result = wallet.get_receive_qr(helios_id)
    return api_response(result)


@wallet_bp.route("/xaman/payload", methods=["POST"])
@handle_errors
def create_xaman_payload():
    """Create a Xaman payload for XRPL sign-in or signing."""
    from core.xaman import XamanService

    data = validate_payload("xaman_payload", request.get_json())
    service = XamanService()
    result = service.create_payload(
        action=data["action"],
        member_id=data.get("member_id"),
        account=data.get("account"),
        destination=data.get("destination"),
        amount=data.get("amount"),
    )
    return api_response(result, status=201)


@wallet_bp.route("/xaman/payload/<payload_uuid>", methods=["GET"])
@handle_errors
def get_xaman_payload(payload_uuid):
    """Get Xaman payload resolution state."""
    from core.xaman import XamanService

    service = XamanService()
    return api_response(service.get_payload(payload_uuid))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOKEN ROUTES (Public — anyone can verify)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@token_bp.route("/info", methods=["GET"])
@handle_errors
def get_token_info():
    """Public token information."""
    from core.token import TokenEngine

    engine = TokenEngine(get_db())
    result = engine.get_token_info()
    return api_response(result)


@token_bp.route("/supply", methods=["GET"])
@handle_errors
def get_supply():
    """Real-time supply statistics."""
    from core.token import TokenEngine

    engine = TokenEngine(get_db())
    result = engine.get_supply_stats()
    return api_response(result)


@token_bp.route("/verify", methods=["GET"])
@handle_errors
def verify_integrity():
    """Verify token supply integrity. Anyone can call this."""
    from core.token import TokenEngine

    engine = TokenEngine(get_db())
    result = engine.verify_integrity()
    return api_response(result)


@token_bp.route("/pools", methods=["GET"])
@handle_errors
def get_pools():
    """Get pool balances."""
    from core.token import TokenEngine

    engine = TokenEngine(get_db())
    result = engine.get_pool_balances()
    return api_response(result)


@token_bp.route("/founder-lock", methods=["GET"])
@handle_errors
def check_founder_lock():
    """Check founder lock status."""
    from core.token import TokenEngine

    engine = TokenEngine(get_db())
    result = engine.check_founder_lock()
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ASK HELIOS (Voice of the Protocol)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@chat_bp.route("/ask", methods=["POST"])
@handle_errors
def ask_helios():
    """Ask Helios — male, calm, authoritative. I'll explain it. You decide."""
    from ai.ask_helios import AskHelios

    data = request.get_json()
    question = data.get("question", "").strip()
    member_id = data.get("member_id")

    if not question:
        return api_response(error="Please ask a question.", status=400)

    assistant = AskHelios(get_db())
    result = assistant.ask(question, member_id=member_id)
    return api_response(result)


@chat_bp.route("/quick-answers", methods=["GET"])
@handle_errors
def get_quick_answers():
    """Get pre-built question buttons."""
    from ai.ask_helios import AskHelios

    assistant = AskHelios()
    result = assistant.get_quick_answers()
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VOICE ROUTES (ElevenLabs TTS — Drew, male, authoritative)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

voice_bp = Blueprint("voice", __name__, url_prefix="/api/voice")


@voice_bp.route("/speak", methods=["POST"])
@handle_errors
def speak_text():
    """Convert text to speech using ElevenLabs."""
    from core.voice import HeliosVoice

    data = request.get_json()
    text = data.get("text", "").strip()
    voice_id = data.get("voice_id")  # Optional override

    if not text:
        return api_response(error="No text provided", status=400)

    voice = HeliosVoice()
    result = voice.speak(text, voice_id=voice_id)
    return api_response(result)


@voice_bp.route("/voices", methods=["GET"])
@handle_errors
def list_voices():
    """List available TTS voices."""
    from core.voice import HeliosVoice

    voice = HeliosVoice()
    result = voice.get_voices()
    return api_response(result)


@voice_bp.route("/status", methods=["GET"])
@handle_errors
def voice_status():
    """Voice service health check."""
    from core.voice import HeliosVoice

    voice = HeliosVoice()
    result = voice.get_status()
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SMS ROUTES (Telnyx)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

sms_bp = Blueprint("sms", __name__, url_prefix="/api/sms")


@sms_bp.route("/verify/send", methods=["POST"])
@handle_errors
def send_verification():
    """Send phone verification code."""
    from core.sms import HeliosSMS

    data = request.get_json()
    phone = data.get("phone", "").strip()
    helios_id = data.get("helios_id")

    if not phone:
        return api_response(error="Phone number required", status=400)

    sms = HeliosSMS(get_db())
    result = sms.send_verification(phone, helios_id)
    return api_response(result, status=200 if result.get("sent") else 400)


@sms_bp.route("/verify/confirm", methods=["POST"])
@handle_errors
def confirm_verification():
    """Confirm phone verification code."""
    from core.sms import HeliosSMS

    data = request.get_json()
    verification_id = data.get("verification_id", "").strip()
    code = data.get("code", "").strip()

    if not verification_id or not code:
        return api_response(error="verification_id and code required", status=400)

    sms = HeliosSMS(get_db())
    result = sms.verify_code(verification_id, code)
    return api_response(result, status=200 if result.get("verified") else 400)


@sms_bp.route("/status", methods=["GET"])
@handle_errors
def sms_status():
    """SMS service health check."""
    from core.sms import HeliosSMS

    sms = HeliosSMS()
    result = sms.get_status()
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INFRASTRUCTURE ROUTES (Cloudflare — heliosdigital.xyz)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

infra_bp = Blueprint("infra", __name__, url_prefix="/api/infra")


@infra_bp.route("/status", methods=["GET"])
@handle_errors
def infra_status():
    """Complete infrastructure health check."""
    from core.infrastructure import HeliosInfra

    infra = HeliosInfra()
    result = infra.get_status()
    return api_response(result)


@infra_bp.route("/readiness", methods=["GET"])
@handle_errors
def readiness():
    """Production readiness snapshot for blockchain, payments, IPFS, and infrastructure."""
    from core.integrations import IntegrationReadiness

    return api_response(IntegrationReadiness.snapshot())


@infra_bp.route("/launch-readiness", methods=["GET"])
@handle_errors
def launch_readiness():
    """Actionable launch-readiness report with remaining blockers and next actions."""
    from core.integrations import IntegrationReadiness

    return api_response(IntegrationReadiness.launch_readiness_report())


@infra_bp.route("/build", methods=["GET"])
@handle_errors
def build_manifest():
    """Build ownership, route, and watermark manifest."""
    from core.build_manifest import get_build_manifest

    return api_response(get_build_manifest())


@infra_bp.route("/dns", methods=["GET"])
@handle_errors
def list_dns():
    """List DNS records."""
    from core.infrastructure import HeliosInfra

    record_type = request.args.get("type")
    infra = HeliosInfra()
    result = infra.list_dns_records(record_type)
    return api_response(result)


@infra_bp.route("/dns", methods=["POST"])
@handle_errors
def create_dns():
    """Create a DNS record."""
    from core.infrastructure import HeliosInfra

    data = request.get_json()
    infra = HeliosInfra()
    result = infra.create_dns_record(
        record_type=data.get("type", "A"),
        name=data.get("name"),
        content=data.get("content"),
        proxied=data.get("proxied", True)
    )
    return api_response(result, status=201 if result.get("created") else 400)


@infra_bp.route("/ssl", methods=["GET"])
@handle_errors
def ssl_details():
    """SSL/TLS configuration details."""
    from core.infrastructure import HeliosInfra

    infra = HeliosInfra()
    result = infra.get_ssl_details()
    return api_response(result)


@infra_bp.route("/analytics", methods=["GET"])
@handle_errors
def analytics():
    """CDN analytics overview."""
    from core.infrastructure import HeliosInfra

    hours = request.args.get("hours", 24, type=int)
    infra = HeliosInfra()
    result = infra.get_analytics(since_hours=hours)
    return api_response(result)


@infra_bp.route("/cache/purge", methods=["POST"])
@handle_errors
def purge_cache():
    """Purge CDN cache."""
    from core.infrastructure import HeliosInfra

    data = request.get_json() or {}
    infra = HeliosInfra()
    result = infra.purge_cache(
        purge_everything=data.get("purge_everything", False),
        urls=data.get("urls")
    )
    return api_response(result)


@handoff_bp.route("/manifest", methods=["GET"])
@handle_errors
def handoff_manifest():
    """Public handoff manifest for the build team."""
    from core.handoff import get_handoff_manifest

    return api_response(get_handoff_manifest())


@handoff_bp.route("/docs", methods=["GET"])
@handle_errors
def handoff_docs():
    """List mirrored handoff documents available through the site."""
    from core.handoff import list_handoff_docs

    return api_response(list_handoff_docs())


@handoff_bp.route("/docs/<slug>", methods=["GET"])
@handle_errors
def handoff_doc(slug):
    """Return a mirrored handoff document by slug."""
    from core.handoff import get_handoff_doc

    document = get_handoff_doc(slug)
    if not document:
        return api_response(error="Handoff document not found", status=404)
    return api_response(document)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TREASURY ROUTES (Metal Spine — APMEX MVR)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@treasury_bp.route("/reserves", methods=["GET"])
@handle_errors
def get_reserves():
    """Public proof-of-reserves. Anyone can verify."""
    from core.treasury import TreasuryEngine

    engine = TreasuryEngine(get_db())
    result = engine.get_proof_of_reserves()
    return api_response(result)


@treasury_bp.route("/receipt", methods=["POST"])
@handle_errors
def create_receipt():
    """Create a new Metal Vault Receipt (admin/operator)."""
    from core.treasury import TreasuryEngine

    data = validate_payload("treasury_receipt", request.get_json())
    engine = TreasuryEngine(get_db())
    result = engine.create_vault_receipt(
        dealer=data["dealer"],
        invoice_id=data["invoice_id"],
        purchase_date=data["purchase_date"],
        metal=data["metal"],
        form=data["form"],
        purity=data.get("purity", "0.9999"),
        weight_oz=float(data["weight_oz"]),
        quantity=int(data.get("quantity", 1)),
        unit_cost_usd=float(data["unit_cost_usd"]),
        serials=data.get("serials", []),
        evidence_cid=data.get("evidence_cid"),
        evidence_sha256=data.get("evidence_sha256")
    )
    return api_response(result, status=201)


@treasury_bp.route("/receipt/<mvr_id>", methods=["GET"])
@handle_errors
def get_receipt(mvr_id):
    """Get a single vault receipt."""
    from core.treasury import TreasuryEngine

    engine = TreasuryEngine(get_db())
    result = engine.get_vault_receipt(mvr_id)
    return api_response(result)


@treasury_bp.route("/receipts", methods=["GET"])
@handle_errors
def list_receipts():
    """List vault receipts with optional filters."""
    from core.treasury import TreasuryEngine

    metal = request.args.get("metal")
    custody = request.args.get("custody")
    engine = TreasuryEngine(get_db())
    result = engine.list_vault_receipts(metal=metal, custody_status=custody)
    return api_response(result)


@treasury_bp.route("/custody", methods=["POST"])
@handle_errors
def update_custody():
    """Update custody status of a vault receipt."""
    from core.treasury import TreasuryEngine

    data = request.get_json()
    engine = TreasuryEngine(get_db())
    result = engine.update_custody(data["mvr_id"], data["status"])
    return api_response(result)


@treasury_bp.route("/anchor", methods=["POST"])
@handle_errors
def anchor_receipt():
    """Record XRPL anchoring for a vault receipt."""
    from core.treasury import TreasuryEngine

    data = validate_payload("treasury_anchor", request.get_json())
    engine = TreasuryEngine(get_db())
    result = engine.anchor_to_xrpl(
        mvr_id=data["mvr_id"],
        tx_hash=data.get("tx_hash"),
        issuer_wallet=data.get("issuer_wallet"),
        attestation_wallet=data.get("attestation_wallet")
    )
    return api_response(result)


@treasury_bp.route("/allocation", methods=["POST"])
@handle_errors
def calculate_allocation():
    """Calculate metal allocation from net surplus."""
    from core.treasury import TreasuryEngine

    data = request.get_json()
    engine = TreasuryEngine(get_db())
    result = engine.calculate_metal_allocation(
        net_surplus_usd=float(data["net_surplus_usd"]),
        coefficient=data.get("coefficient")
    )
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CERTIFICATE ROUTES (HC-NFT — Stored Energy Batteries)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@certificates_bp.route("/mint", methods=["POST"])
@handle_errors
def mint_certificate():
    """Mint a new Helios Certificate (HC-NFT)."""
    from core.certificates import CertificateEngine

    data = request.get_json()
    engine = CertificateEngine(get_db())
    result = engine.mint(
        holder_id=data["holder_id"],
        energy_amount_he=float(data["energy_amount_he"]),
        energy_value_usd=float(data["energy_value_usd"])
    )
    return api_response(result, status=201)


@certificates_bp.route("/redeem/gold", methods=["POST"])
@handle_errors
def redeem_gold():
    """Redeem certificate for gold."""
    from core.certificates import CertificateEngine

    data = request.get_json()
    engine = CertificateEngine(get_db())
    result = engine.redeem_gold(
        certificate_id=data["certificate_id"],
        mvr_id=data.get("mvr_id")
    )
    return api_response(result)


@certificates_bp.route("/redeem/stablecoin", methods=["POST"])
@handle_errors
def redeem_stablecoin():
    """Redeem certificate for stablecoin."""
    from core.certificates import CertificateEngine

    data = request.get_json()
    engine = CertificateEngine(get_db())
    result = engine.redeem_stablecoin(data["certificate_id"])
    return api_response(result)


@certificates_bp.route("/cancel", methods=["POST"])
@handle_errors
def cancel_certificate():
    """Cancel certificate — 2% energy BURNED permanently. Irreversible."""
    from core.certificates import CertificateEngine

    data = request.get_json()
    engine = CertificateEngine(get_db())
    result = engine.cancel(data["certificate_id"])
    return api_response(result)


@certificates_bp.route("/covenant", methods=["GET"])
@handle_errors
def check_covenant():
    """Check RRR covenant status — whether redemptions are permitted."""
    from core.certificates import CertificateEngine

    engine = CertificateEngine(get_db())
    result = engine.check_rrr_covenant()
    return api_response(result)


@certificates_bp.route("/burned", methods=["GET"])
@handle_errors
def total_burned():
    """Total energy permanently destroyed through cancellations."""
    from core.certificates import CertificateEngine

    engine = CertificateEngine(get_db())
    result = engine.get_total_burned()
    return api_response(result)


@certificates_bp.route("/<certificate_id>", methods=["GET"])
@handle_errors
def get_certificate(certificate_id):
    """Get certificate details."""
    from core.certificates import CertificateEngine

    engine = CertificateEngine(get_db())
    result = engine.get_certificate(certificate_id)
    return api_response(result)


@certificates_bp.route("/list", methods=["GET"])
@handle_errors
def list_certificates():
    """List certificates with optional filters."""
    from core.certificates import CertificateEngine

    holder = request.args.get("holder")
    state = request.args.get("state")
    engine = CertificateEngine(get_db())
    result = engine.list_certificates(holder_id=holder, state=state)
    return api_response(result)


@certificates_bp.route("/portfolio/<helios_id>", methods=["GET"])
@handle_errors
def get_portfolio(helios_id):
    """Get full certificate portfolio for a member."""
    from core.certificates import CertificateEngine

    engine = CertificateEngine(get_db())
    result = engine.get_portfolio(helios_id)
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FUNDING ROUTES (Activation + recurring revenue)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@funding_bp.route("/catalog", methods=["GET"])
@handle_errors
def funding_catalog():
    """Return the recommended monetization catalog for Helios."""
    from core.funding import FundingEngine

    engine = FundingEngine(get_db())
    return api_response(engine.get_catalog())


@funding_bp.route("/checkout", methods=["POST"])
@handle_errors
def funding_checkout():
    """Create a hosted checkout session for entry, memberships, or credentials."""
    from core.funding import FundingEngine

    data = validate_payload("funding_checkout", request.get_json())
    engine = FundingEngine(get_db())
    result = engine.create_checkout(
        offer_code=data["offer_code"],
        quantity=int(data.get("quantity", 1)),
        customer_email=data.get("customer_email"),
        member_id=data.get("member_id"),
        metadata=data.get("metadata") or {},
    )
    return api_response(result, status=201 if result.get("status") == "created" else 200)


@funding_bp.route("/webhook/stripe", methods=["POST"])
@handle_errors
def stripe_webhook():
    """Receive Stripe webhook events and fulfill offers."""
    from core.funding import FundingEngine

    signature = request.headers.get("Stripe-Signature")
    payload = request.get_data()
    engine = FundingEngine(get_db())
    result = engine.process_stripe_webhook(payload, signature=signature)
    return api_response(result, status=200)


@funding_bp.route("/events/<external_id>", methods=["GET"])
@handle_errors
def funding_event(external_id):
    """Get a recorded checkout or webhook event."""
    from core.funding import FundingEngine

    engine = FundingEngine(get_db())
    return api_response(engine.get_payment_event(external_id))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENERGY EXCHANGE ROUTES (Conservation-Law Engine)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@energy_bp.route("/inject", methods=["POST"])
@handle_errors
def inject_energy():
    """Inject energy from entry fee. Atomic $100 split."""
    from core.energy_exchange import EnergyExchange

    data = validate_payload("energy_inject", request.get_json())
    engine = EnergyExchange(get_db())
    result = engine.inject_entry_energy(
        member_id=data["member_id"],
        amount_usd=data.get("amount_usd")
    )
    return api_response(result, status=201)


@energy_bp.route("/conservation", methods=["GET"])
@handle_errors
def verify_conservation():
    """Verify energy conservation law. Public — anyone can check."""
    from core.energy_exchange import EnergyExchange

    engine = EnergyExchange(get_db())
    result = engine.verify_conservation()
    return api_response(result)


@energy_bp.route("/map", methods=["GET"])
@handle_errors
def get_energy_map():
    """Get energy flow map."""
    from core.energy_exchange import EnergyExchange

    member_id = request.args.get("member_id")
    engine = EnergyExchange(get_db())
    result = engine.get_energy_map(member_id=member_id)
    return api_response(result)


@energy_bp.route("/balance/<helios_id>", methods=["GET"])
@handle_errors
def get_energy_balance(helios_id):
    """Get energy balance for a member."""
    from core.energy_exchange import EnergyExchange

    engine = EnergyExchange(get_db())
    result = engine.get_energy_balance(helios_id)
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SPACES ROUTES (Rooms, Events, Access Keys)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@spaces_bp.route("/create", methods=["POST"])
@handle_errors
def create_space():
    """Create a new space. Requires operator/host credential."""
    from core.spaces import SpaceEngine

    data = request.get_json()
    engine = SpaceEngine(get_db())
    result = engine.create_space(
        owner_id=data["owner_id"],
        name=data["name"],
        description=data.get("description"),
        is_public=data.get("is_public", True),
        entry_fee_usd=float(data.get("entry_fee_usd", 0)),
        max_members=int(data.get("max_members", 500))
    )
    return api_response(result, status=201)


@spaces_bp.route("/list", methods=["GET"])
@handle_errors
def list_spaces():
    """List active spaces."""
    from core.spaces import SpaceEngine

    engine = SpaceEngine(get_db())
    result = engine.list_spaces()
    return api_response(result)


@spaces_bp.route("/<space_id>", methods=["GET"])
@handle_errors
def get_space(space_id):
    """Get space details."""
    from core.spaces import SpaceEngine

    engine = SpaceEngine(get_db())
    result = engine.get_space(space_id)
    return api_response(result)


@spaces_bp.route("/event", methods=["POST"])
@handle_errors
def create_event():
    """Create an event within a space."""
    from core.spaces import SpaceEngine

    data = request.get_json()
    engine = SpaceEngine(get_db())
    result = engine.create_event(
        space_id=data["space_id"],
        host_id=data["host_id"],
        title=data["title"],
        description=data.get("description"),
        event_type=data.get("event_type", "general"),
        ticket_price_usd=float(data.get("ticket_price_usd", 0)),
        max_attendees=int(data.get("max_attendees", 100)),
        starts_at=data.get("starts_at"),
        ends_at=data.get("ends_at")
    )
    return api_response(result, status=201)


@spaces_bp.route("/events", methods=["GET"])
@handle_errors
def list_events():
    """List events with optional space filter."""
    from core.spaces import SpaceEngine

    space_id = request.args.get("space_id")
    engine = SpaceEngine(get_db())
    result = engine.list_events(space_id=space_id)
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# METRICS ROUTES (SR-Level — Public Health Dashboard)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@metrics_bp.route("/all", methods=["GET"])
@handle_errors
def get_all_metrics():
    """All SR-level metrics in one call. Public."""
    from core.metrics import MetricsEngine

    engine = MetricsEngine(get_db())
    result = engine.get_all_metrics()
    return api_response(result)


@metrics_bp.route("/rrr", methods=["GET"])
@handle_errors
def get_rrr():
    """Reserve Ratio — LiquidTreasury / 30d_Redeem_Demand."""
    from core.metrics import MetricsEngine

    engine = MetricsEngine(get_db())
    result = engine.get_reserve_ratio()
    return api_response(result)


@metrics_bp.route("/flow-efficiency", methods=["GET"])
@handle_errors
def get_flow_efficiency():
    """Flow Efficiency — (Routed + Stored + Pooled) / In."""
    from core.metrics import MetricsEngine

    engine = MetricsEngine(get_db())
    result = engine.get_flow_efficiency()
    return api_response(result)


@metrics_bp.route("/churn", methods=["GET"])
@handle_errors
def get_churn():
    """Churn Pressure — CancelRequests / ActiveNodes."""
    from core.metrics import MetricsEngine

    engine = MetricsEngine(get_db())
    result = engine.get_churn_pressure()
    return api_response(result)


@metrics_bp.route("/velocity", methods=["GET"])
@handle_errors
def get_velocity():
    """Energy Velocity — Transfers_7d / StoredEnergy."""
    from core.metrics import MetricsEngine

    engine = MetricsEngine(get_db())
    result = engine.get_energy_velocity()
    return api_response(result)


@metrics_bp.route("/health", methods=["GET"])
@handle_errors
def get_network_health():
    """Network health summary."""
    from core.metrics import MetricsEngine

    engine = MetricsEngine(get_db())
    result = engine.get_network_health()
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NETWORK ALIASES (templates use /api/network/*, backend uses /api/field/*)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@network_bp.route("/graph/<helios_id>", methods=["GET"])
@handle_errors
def network_graph(helios_id):
    """Alias: /api/network/graph → /api/field/graph."""
    from core.network import FieldEngine

    depth = request.args.get("depth", request.args.get("hops"), type=int)
    engine = FieldEngine(get_db())
    result = engine.get_field(helios_id, max_hops=depth)
    return api_response(result)


@network_bp.route("/stats/<helios_id>", methods=["GET"])
@handle_errors
def network_stats(helios_id):
    """Alias: /api/network/stats → /api/field/stats."""
    from core.network import FieldEngine

    engine = FieldEngine(get_db())
    result = engine.get_node_stats(helios_id)
    return api_response(result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIELD STATUS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@field_bp.route("/status", methods=["GET"])
@handle_errors
def field_status():
    """Overall field status — node count, bond count, average degree."""
    from models.member import Member
    from models.bond import Bond

    db = get_db()
    total_nodes = db.query(Member).count()
    total_bonds = db.query(Bond).count()
    avg_degree = round((total_bonds * 2) / max(total_nodes, 1), 2)
    return api_response({
        "total_nodes": total_nodes,
        "total_bonds": total_bonds,
        "avg_degree": avg_degree,
        "max_bonds_per_node": 5,
        "status": "active"
    })


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REWARDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@rewards_bp.route("/protocol", methods=["GET"])
@handle_errors
def rewards_protocol():
    """Protocol reward rules and settlement configuration."""
    from config import HeliosConfig

    return api_response({
        "acknowledgement_amount": HeliosConfig.ACKNOWLEDGEMENT_AMOUNT,
        "propagation_max_hops": HeliosConfig.PROPAGATION_MAX_HOPS,
        "propagation_decay_base": HeliosConfig.PROPAGATION_DECAY_BASE,
        "field_max_bonds": HeliosConfig.FIELD_MAX_BONDS,
        "settlement_min_activity": HeliosConfig.SETTLEMENT_MIN_ACTIVITY_SCORE,
        "absorption_pools": {
            "stability": HeliosConfig.ABSORPTION_STABILITY_PERCENT,
            "liquidity": HeliosConfig.ABSORPTION_LIQUIDITY_PERCENT,
            "intelligence": HeliosConfig.ABSORPTION_INTELLIGENCE_PERCENT,
            "compliance": HeliosConfig.ABSORPTION_COMPLIANCE_PERCENT,
        },
        "policy": "energy_exchange"
    })


@rewards_bp.route("/pool", methods=["GET"])
@handle_errors
def rewards_pool():
    """Reward pool status."""
    from models.token_pool import TokenPool
    from config import HeliosConfig

    db = get_db()
    pools = db.query(TokenPool).all()
    pool_data = {p.pool_name: float(p.balance) for p in pools} if pools else {}
    return api_response({
        "pools": pool_data,
        "total_supply": HeliosConfig.TOKEN_TOTAL_SUPPLY,
        "policy": "fixed_supply"
    })


@rewards_bp.route("/total/<helios_id>", methods=["GET"])
@handle_errors
def rewards_total(helios_id):
    """Total rewards earned by a node."""
    from models.energy_event import EnergyEvent

    db = get_db()
    events = db.query(EnergyEvent).filter_by(target_id=helios_id).all()
    total = sum(float(e.amount) for e in events) if events else 0.0
    return api_response({
        "helios_id": helios_id,
        "total_earned": round(total, 8),
        "event_count": len(events)
    })


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CERTIFICATES — /active alias
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@certificates_bp.route("/active", methods=["GET"])
@handle_errors
def active_certificates():
    """List active certificates (alias for /list?state=active)."""
    from core.certificates import CertificateEngine

    db = get_db()
    engine = CertificateEngine(db)
    result = engine.list_certificates(state="active")
    return api_response(result)
