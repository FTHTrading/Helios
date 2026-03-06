"""
Helios Infrastructure — Cloudflare Integration
───────────────────────────────────────────────
DNS management, SSL status, CDN configuration, security.
Production-grade infrastructure from day one.
"""

import os
from datetime import datetime, timezone
from config import HeliosConfig
from core.integrations import IntegrationReadiness


class HeliosInfra:
    """
    Infrastructure management powered by Cloudflare.
    - DNS record management for helios domains
    - SSL/TLS status monitoring
    - CDN cache management
    - Security & WAF overview
    - Analytics overview
    """

    BASE_URL = "https://api.cloudflare.com/client/v4"

    def __init__(self):
        self.api_token = HeliosConfig.CF_API_TOKEN
        self.zone_id = HeliosConfig.CF_ZONE_ID
        self.available = bool(self.api_token)

    # ─── Infrastructure Status Dashboard ───────────────────────────────

    def get_status(self) -> dict:
        """
        Complete infrastructure health check.
        Returns DNS, SSL, CDN, and security status in one call.
        """
        if not self.available:
            return {
                "status": "not_configured",
                "message": "Add HELIOS_CF_TOKEN to .env",
                "readiness": IntegrationReadiness.snapshot(),
                "services": {
                    "dns": "not_configured",
                    "ssl": "not_configured",
                    "cdn": "not_configured",
                    "security": "not_configured"
                }
            }

        status = {
            "status": "checking",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "readiness": IntegrationReadiness.snapshot(),
            "services": {}
        }

        # Check API token validity
        token_check = self._verify_token()
        if not token_check.get("valid"):
            return {
                "status": "auth_error",
                "message": "Cloudflare API token is invalid or expired",
                "services": {}
            }

        status["account"] = token_check

        # Get zone info if zone_id is set
        if self.zone_id:
            zone_info = self._get_zone_info()
            status["zone"] = zone_info
            status["services"]["dns"] = "active" if zone_info.get("status") == "active" else "pending"
            status["services"]["ssl"] = self._get_ssl_status()
            status["services"]["cdn"] = "active"
            status["services"]["security"] = self._get_security_level()
        else:
            # List available zones so user can pick one
            zones = self._list_zones()
            status["zones_available"] = zones
            status["message"] = "Set HELIOS_CF_ZONE_ID in .env to enable DNS management"
            status["services"]["dns"] = "needs_zone_id"

        status["status"] = "operational"
        return status

    # ─── DNS Management ────────────────────────────────────────────────

    def list_dns_records(self, record_type: str = None) -> dict:
        """List all DNS records for the zone."""
        if not self._check_ready():
            return self._not_ready()

        try:
            params = {"per_page": 100}
            if record_type:
                params["type"] = record_type.upper()

            data = self._api_get(f"/zones/{self.zone_id}/dns_records", params=params)
            records = data.get("result", [])

            return {
                "records": [
                    {
                        "id": r["id"],
                        "type": r["type"],
                        "name": r["name"],
                        "content": r["content"],
                        "ttl": r["ttl"],
                        "proxied": r.get("proxied", False),
                        "created_on": r.get("created_on")
                    }
                    for r in records
                ],
                "total": len(records)
            }

        except Exception as e:
            return {"records": [], "error": str(e)}

    def create_dns_record(self, record_type: str, name: str,
                           content: str, proxied: bool = True,
                           ttl: int = 1) -> dict:
        """Create a new DNS record."""
        if not self._check_ready():
            return self._not_ready()

        try:
            payload = {
                "type": record_type.upper(),
                "name": name,
                "content": content,
                "ttl": ttl,
                "proxied": proxied
            }

            data = self._api_post(f"/zones/{self.zone_id}/dns_records", payload)
            record = data.get("result", {})

            return {
                "created": True,
                "record": {
                    "id": record.get("id"),
                    "type": record.get("type"),
                    "name": record.get("name"),
                    "content": record.get("content"),
                    "proxied": record.get("proxied")
                }
            }

        except Exception as e:
            return {"created": False, "error": str(e)}

    def delete_dns_record(self, record_id: str) -> dict:
        """Delete a DNS record by ID."""
        if not self._check_ready():
            return self._not_ready()

        try:
            self._api_delete(f"/zones/{self.zone_id}/dns_records/{record_id}")
            return {"deleted": True, "record_id": record_id}
        except Exception as e:
            return {"deleted": False, "error": str(e)}

    # ─── SSL / TLS ─────────────────────────────────────────────────────

    def get_ssl_details(self) -> dict:
        """Get SSL/TLS configuration details."""
        if not self._check_ready():
            return self._not_ready()

        try:
            data = self._api_get(f"/zones/{self.zone_id}/settings/ssl")
            ssl_mode = data.get("result", {}).get("value", "unknown")

            cert_data = self._api_get(f"/zones/{self.zone_id}/ssl/certificate_packs")
            certs = cert_data.get("result", [])

            return {
                "ssl_mode": ssl_mode,
                "certificates": [
                    {
                        "id": c.get("id"),
                        "type": c.get("type"),
                        "status": c.get("status"),
                        "hosts": c.get("hosts", [])
                    }
                    for c in certs
                ],
                "total_certs": len(certs)
            }

        except Exception as e:
            return {"ssl_mode": "unknown", "error": str(e)}

    # ─── CDN / Cache ───────────────────────────────────────────────────

    def purge_cache(self, purge_everything: bool = False,
                     urls: list = None) -> dict:
        """Purge CDN cache — full or selective."""
        if not self._check_ready():
            return self._not_ready()

        try:
            if purge_everything:
                payload = {"purge_everything": True}
            elif urls:
                payload = {"files": urls}
            else:
                return {"purged": False, "error": "Specify purge_everything=True or provide URLs"}

            data = self._api_post(f"/zones/{self.zone_id}/purge_cache", payload)

            return {
                "purged": True,
                "id": data.get("result", {}).get("id")
            }

        except Exception as e:
            return {"purged": False, "error": str(e)}

    # ─── Analytics ─────────────────────────────────────────────────────

    def get_analytics(self, since_hours: int = 24) -> dict:
        """Get basic zone analytics."""
        if not self._check_ready():
            return self._not_ready()

        try:
            from datetime import timedelta
            since = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
            until = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            params = {"since": since, "until": until}
            data = self._api_get(f"/zones/{self.zone_id}/analytics/dashboard", params=params)

            totals = data.get("result", {}).get("totals", {})
            requests_data = totals.get("requests", {})
            bandwidth = totals.get("bandwidth", {})
            threats = totals.get("threats", {})
            pageviews = totals.get("pageviews", {})

            return {
                "period_hours": since_hours,
                "requests": {
                    "total": requests_data.get("all", 0),
                    "cached": requests_data.get("cached", 0),
                    "uncached": requests_data.get("uncached", 0),
                    "cache_hit_rate": self._calc_rate(
                        requests_data.get("cached", 0),
                        requests_data.get("all", 1)
                    )
                },
                "bandwidth": {
                    "total_bytes": bandwidth.get("all", 0),
                    "cached_bytes": bandwidth.get("cached", 0),
                    "total_mb": round(bandwidth.get("all", 0) / (1024 * 1024), 2)
                },
                "threats": {
                    "total": threats.get("all", 0),
                    "types": threats.get("type", {})
                },
                "pageviews": {
                    "total": pageviews.get("all", 0)
                }
            }

        except Exception as e:
            return {"error": str(e)}

    # ─── Cloudflare API Helpers ────────────────────────────────────────

    def _verify_token(self) -> dict:
        """Verify the API token is valid."""
        try:
            data = self._api_get("/user/tokens/verify")
            result = data.get("result", {})
            return {
                "valid": result.get("status") == "active",
                "status": result.get("status"),
                "expires_on": result.get("expires_on")
            }
        except Exception:
            return {"valid": False}

    def _list_zones(self) -> list:
        """List all zones available to this token."""
        try:
            data = self._api_get("/zones", params={"per_page": 50})
            return [
                {
                    "id": z["id"],
                    "name": z["name"],
                    "status": z["status"],
                    "plan": z.get("plan", {}).get("name", "unknown")
                }
                for z in data.get("result", [])
            ]
        except Exception:
            return []

    def _get_zone_info(self) -> dict:
        """Get zone details."""
        try:
            data = self._api_get(f"/zones/{self.zone_id}")
            z = data.get("result", {})
            return {
                "name": z.get("name"),
                "status": z.get("status"),
                "name_servers": z.get("name_servers", []),
                "plan": z.get("plan", {}).get("name"),
                "created_on": z.get("created_on")
            }
        except Exception:
            return {"status": "unknown"}

    def _get_ssl_status(self) -> str:
        """Quick SSL status check."""
        try:
            data = self._api_get(f"/zones/{self.zone_id}/settings/ssl")
            return data.get("result", {}).get("value", "unknown")
        except Exception:
            return "unknown"

    def _get_security_level(self) -> str:
        """Quick security level check."""
        try:
            data = self._api_get(f"/zones/{self.zone_id}/settings/security_level")
            return data.get("result", {}).get("value", "unknown")
        except Exception:
            return "unknown"

    def _api_get(self, endpoint: str, params: dict = None) -> dict:
        """GET request to Cloudflare API."""
        import requests
        response = requests.get(
            f"{self.BASE_URL}{endpoint}",
            headers=self._headers(),
            params=params,
            timeout=15
        )
        response.raise_for_status()
        return response.json()

    def _api_post(self, endpoint: str, payload: dict) -> dict:
        """POST request to Cloudflare API."""
        import requests
        response = requests.post(
            f"{self.BASE_URL}{endpoint}",
            headers=self._headers(),
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        return response.json()

    def _api_delete(self, endpoint: str) -> dict:
        """DELETE request to Cloudflare API."""
        import requests
        response = requests.delete(
            f"{self.BASE_URL}{endpoint}",
            headers=self._headers(),
            timeout=15
        )
        response.raise_for_status()
        return response.json()

    def _headers(self) -> dict:
        """Standard Cloudflare API headers."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def _check_ready(self) -> bool:
        """Check if Cloudflare is configured with token and zone."""
        return self.available and bool(self.zone_id)

    def _not_ready(self) -> dict:
        """Standard response when not configured."""
        missing = []
        if not self.api_token:
            missing.append("HELIOS_CF_TOKEN")
        if not self.zone_id:
            missing.append("HELIOS_CF_ZONE_ID")
        return {
            "error": f"Cloudflare not fully configured. Missing: {', '.join(missing)}",
            "status": "not_configured"
        }

    @staticmethod
    def _calc_rate(part: int, total: int) -> str:
        """Calculate percentage rate."""
        if total == 0:
            return "0%"
        return f"{(part / total * 100):.1f}%"
