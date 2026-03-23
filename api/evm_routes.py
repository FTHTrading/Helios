"""
Helios EVM/ERC-20 API Routes
─────────────────────────────
Secondary issuance rail API endpoints.
These are layered *beside* the XRPL routes, not replacing them.

Prefix: /api/evm
"""

from flask import Blueprint, request, jsonify

evm_bp = Blueprint("evm", __name__, url_prefix="/api/evm")


def _api_response(data=None, error=None, status=200):
    if error:
        return jsonify({"success": False, "error": str(error)}), status
    return jsonify({"success": True, "data": data}), status


def _require_auth(f):
    """API-key gate — mirrors the one in api/routes.py."""
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        from config import HeliosConfig
        expected = getattr(HeliosConfig, "API_KEY", None)
        require = getattr(HeliosConfig, "REQUIRE_API_AUTH", False)

        if require and not expected:
            return _api_response(error="Server misconfigured: API auth required", status=503)
        if expected:
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer ") or auth[7:] != expected:
                return _api_response(error="Unauthorized", status=401)
        return f(*args, **kwargs)
    return wrapper


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STATUS / INFO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@evm_bp.route("/status")
def evm_status():
    """EVM bridge status — connectivity, chain, contract address."""
    from core.evm_bridge import get_evm_bridge
    bridge = get_evm_bridge()
    return _api_response(bridge.status())


@evm_bp.route("/token")
def evm_token_info():
    """On-chain token metadata (name, symbol, supply, cap, paused)."""
    from core.evm_bridge import get_evm_bridge
    bridge = get_evm_bridge()
    return _api_response(bridge.token_info())


@evm_bp.route("/balance/<address>")
def evm_balance(address):
    """Query HLS balance for an EVM address."""
    from core.evm_bridge import get_evm_bridge
    bridge = get_evm_bridge()
    return _api_response(bridge.balance_of(address))


@evm_bp.route("/tx/<tx_hash>")
def evm_tx_status(tx_hash):
    """Check transaction status by hash."""
    from core.evm_bridge import get_evm_bridge
    bridge = get_evm_bridge()
    return _api_response(bridge.get_tx_status(tx_hash))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MINTING (auth required)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@evm_bp.route("/mint", methods=["POST"])
@_require_auth
def evm_mint():
    """
    Mint HLS tokens to an EVM address.

    Request body:
        {
            "to": "0x...",
            "amount": 1000.0
        }

    The amount is in human-readable HLS tokens (not raw decimals).
    Only callable with a valid API key. MINTER_ROLE must be assigned
    to the backend wallet on the contract.
    """
    from core.evm_bridge import get_evm_bridge

    data = request.get_json(silent=True)
    if not data:
        return _api_response(error="Request body required", status=400)

    to_address = data.get("to")
    amount = data.get("amount")

    if not to_address:
        return _api_response(error="Missing 'to' address", status=400)
    if not amount or float(amount) <= 0:
        return _api_response(error="Invalid 'amount'", status=400)

    # Validate EVM address format
    if not to_address.startswith("0x") or len(to_address) != 42:
        return _api_response(error="Invalid EVM address format", status=400)

    bridge = get_evm_bridge()
    if not bridge.enabled:
        return _api_response(error="EVM rail not enabled", status=503)

    result = bridge.mint(to_address, float(amount))
    status_code = 200 if not result.get("simulation") else 202
    return _api_response(result, status=status_code)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WALLET VALIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@evm_bp.route("/validate/<address>")
def evm_validate_address(address):
    """Validate an EVM address (checksum check)."""
    try:
        from web3 import Web3
        is_valid = Web3.is_address(address)
        checksum = Web3.to_checksum_address(address) if is_valid else None
        return _api_response({
            "address": address,
            "valid": is_valid,
            "checksum": checksum,
        })
    except ImportError:
        # web3 not installed — basic regex check
        import re
        is_valid = bool(re.match(r"^0x[0-9a-fA-F]{40}$", address))
        return _api_response({
            "address": address,
            "valid": is_valid,
            "checksum": None,
            "note": "web3 not installed — basic format check only",
        })
    except Exception as exc:
        return _api_response(error=str(exc), status=400)
