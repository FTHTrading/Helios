"""
Treasury Engine — Precious Metals Spine
═══════════════════════════════════════════════════════════════════════
MetalAllocation = NetSurplus × m   (m = 0.05–0.12)

Manages:
- Metal Vault Receipt (MVR) creation and lifecycle
- Custody state tracking
- Proof-of-reserves aggregation
- XRPL anchoring (memo-based, 0-drop payment to self)
- Evidence bundle management (IPFS CIDs)
"""

import uuid
import hashlib
from datetime import datetime, timezone
from decimal import Decimal
from config import HeliosConfig
from core.ipfs import IpfsBundleService
from core.xrpl_bridge import XRPLBridge
from models.vault_receipt import VaultReceipt
from models.energy_event import EnergyEvent


class TreasuryEngine:
    """The metal spine. Every ounce is accounted for."""

    def __init__(self, db_session):
        self.db = db_session

    # ═══ MVR Lifecycle ════════════════════════════════════════════

    def create_vault_receipt(self, dealer: str, invoice_id: str,
                             purchase_date: str, metal: str, form: str,
                             purity: str, weight_oz: float, quantity: int,
                             unit_cost_usd: float, serials: list = None,
                             evidence_cid: str = None, evidence_sha256: str = None) -> dict:
        """
        Mint a new Metal Vault Receipt. Atomic — either fully created or not.
        """
        if dealer not in HeliosConfig.TREASURY_DEALERS:
            raise ValueError(f"Dealer '{dealer}' not in approved list: {HeliosConfig.TREASURY_DEALERS}")

        if metal not in HeliosConfig.METAL_TYPES:
            raise ValueError(f"Metal '{metal}' not recognized. Valid: {HeliosConfig.METAL_TYPES}")

        total_cost = unit_cost_usd * quantity
        mvr_id = f"MVR-{uuid.uuid4().hex[:12].upper()}"
        ipfs = IpfsBundleService()
        manifest = ipfs.build_receipt_manifest(
            mvr_id=mvr_id,
            dealer=dealer,
            invoice_id=invoice_id,
            purchase_date=purchase_date,
            metal=metal,
            form=form,
            purity=purity,
            weight_oz=weight_oz,
            quantity=quantity,
            unit_cost_usd=unit_cost_usd,
            serials=serials or [],
        )
        derived_sha256 = evidence_sha256 or ipfs.hash_bundle(manifest)

        if not evidence_cid and ipfs.is_ready():
            pin_result = ipfs.pin_json(manifest, name=f"{mvr_id}.json")
            evidence_cid = pin_result.get("cid") or evidence_cid
            derived_sha256 = pin_result.get("sha256") or derived_sha256

        mvr = VaultReceipt(
            mvr_id=mvr_id,
            policy_version=HeliosConfig.TREASURY_POLICY_VERSION,
            dealer=dealer,
            invoice_id=invoice_id,
            purchase_date=datetime.fromisoformat(purchase_date) if isinstance(purchase_date, str) else purchase_date,
            metal=metal,
            form=form,
            purity=purity,
            weight_oz=weight_oz,
            quantity=quantity,
            unit_cost_usd=unit_cost_usd,
            total_cost_usd=total_cost,
            serials=serials or [],
            custody_status=HeliosConfig.CUSTODY_IN_TREASURY,
            evidence_bundle_cid=evidence_cid,
            sha256_evidence_bundle=derived_sha256,
        )

        self.db.add(mvr)
        self.db.commit()

        return mvr.to_dict()

    def update_custody(self, mvr_id: str, new_status: str, notes: str = None) -> dict:
        """Update custody status of a vault receipt."""
        if new_status not in HeliosConfig.CUSTODY_STATES:
            raise ValueError(f"Invalid custody status: {new_status}")

        mvr = self.db.query(VaultReceipt).filter_by(mvr_id=mvr_id).first()
        if not mvr:
            raise ValueError(f"MVR {mvr_id} not found")

        mvr.custody_status = new_status
        if new_status == HeliosConfig.CUSTODY_DELIVERED:
            mvr.delivered_at = datetime.now(timezone.utc)

        self.db.commit()

        return {
            "mvr_id": mvr_id,
            "custody_status": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

    def anchor_to_xrpl(self, mvr_id: str, tx_hash: str = None,
                        issuer_wallet: str = None,
                        attestation_wallet: str = None) -> dict:
        """Record XRPL anchoring transaction for an MVR."""
        mvr = self.db.query(VaultReceipt).filter_by(mvr_id=mvr_id).first()
        if not mvr:
            raise ValueError(f"MVR {mvr_id} not found")

        anchor_result = None
        if not tx_hash:
            anchor_result = XRPLBridge().anchor_receipt(
                mvr_id=mvr.mvr_id,
                evidence_hash=mvr.sha256_evidence_bundle or hashlib.sha256(mvr.mvr_id.encode()).hexdigest(),
                cid=mvr.evidence_bundle_cid,
            )
            tx_hash = anchor_result.get("tx_hash")

        mvr.xrpl_tx_hash = tx_hash
        mvr.issuer_wallet = issuer_wallet or HeliosConfig.XRPL_WALLET_ADDRESS
        mvr.attestation_wallet = attestation_wallet
        self.db.commit()

        return {
            "mvr_id": mvr_id,
            "xrpl_tx_hash": tx_hash,
            "anchored": True,
            "simulation": anchor_result.get("simulation", False) if anchor_result else False,
            "memo": anchor_result.get("memo") if anchor_result else None,
        }

    # ═══ Metal Allocation ═════════════════════════════════════════

    def calculate_metal_allocation(self, net_surplus_usd: float,
                                    coefficient: float = None) -> dict:
        """
        MetalAllocation = NetSurplus × m
        m adjusts based on treasury health: 0.05 ≤ m ≤ 0.12
        """
        m = coefficient or HeliosConfig.TREASURY_METAL_COEFFICIENT
        m = max(HeliosConfig.TREASURY_METAL_COEFFICIENT_MIN,
                min(m, HeliosConfig.TREASURY_METAL_COEFFICIENT_MAX))

        allocation = net_surplus_usd * m

        return {
            "net_surplus_usd": net_surplus_usd,
            "metal_coefficient": m,
            "metal_allocation_usd": round(allocation, 2),
            "formula": f"${net_surplus_usd:,.2f} × {m} = ${allocation:,.2f}"
        }

    # ═══ Proof of Reserves ════════════════════════════════════════

    def get_proof_of_reserves(self) -> dict:
        """
        Public proof-of-reserves. Anyone can verify.
        Returns total metal holdings by type, total cost, anchored count.
        """
        receipts = self.db.query(VaultReceipt).all()

        by_metal = {}
        total_cost = 0.0
        total_oz = 0.0
        anchored = 0

        for r in receipts:
            metal = r.metal
            if metal not in by_metal:
                by_metal[metal] = {"total_oz": 0.0, "total_cost_usd": 0.0, "count": 0}
            by_metal[metal]["total_oz"] += r.total_oz
            by_metal[metal]["total_cost_usd"] += r.total_cost_usd
            by_metal[metal]["count"] += 1
            total_cost += r.total_cost_usd
            total_oz += r.total_oz
            if r.is_anchored:
                anchored += 1

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "policy_version": HeliosConfig.TREASURY_POLICY_VERSION,
            "total_receipts": len(receipts),
            "total_cost_usd": round(total_cost, 2),
            "total_oz": round(total_oz, 4),
            "anchored_on_xrpl": anchored,
            "by_metal": by_metal,
            "dealers": HeliosConfig.TREASURY_DEALERS,
            "metal_coefficient": HeliosConfig.TREASURY_METAL_COEFFICIENT,
            "verification": "All MVRs are independently verifiable via XRPL tx hashes"
        }

    def get_vault_receipt(self, mvr_id: str) -> dict:
        """Get a single vault receipt by ID."""
        mvr = self.db.query(VaultReceipt).filter_by(mvr_id=mvr_id).first()
        if not mvr:
            raise ValueError(f"MVR {mvr_id} not found")
        return mvr.to_dict()

    def list_vault_receipts(self, metal: str = None,
                             custody_status: str = None,
                             limit: int = 50) -> list:
        """List vault receipts with optional filters."""
        query = self.db.query(VaultReceipt)
        if metal:
            query = query.filter_by(metal=metal)
        if custody_status:
            query = query.filter_by(custody_status=custody_status)
        query = query.order_by(VaultReceipt.created_at.desc()).limit(limit)
        return [r.to_dict() for r in query.all()]
