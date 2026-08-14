"""HTTP Client for the Agent Handshake Registry.

Provides a thin wrapper over the REST API.
"""

import json
from typing import Optional

try:
    import requests
except ImportError:
    raise ImportError("pip install requests")

from .agent_passport import AgentPassport
from .handshake import HandshakeProtocol


class HandshakeClient:
    """Client for the Agent Handshake Registry REST API."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")

    # ── REGISTER ─────────────────────────────────────────
    def register(self, passport: AgentPassport) -> dict:
        """Register an agent with the registry."""
        resp = requests.post(
            f"{self.base_url}/api/v0/agents/register",
            json=passport.to_dict(),
        )
        resp.raise_for_status()
        return resp.json()

    # ── DISCOVER ─────────────────────────────────────────
    def discover(self, capability: Optional[str] = None, limit: int = 10) -> list:
        """Discover agents by capability."""
        params = {"limit": limit}
        if capability:
            params["capability"] = capability
        resp = requests.get(f"{self.base_url}/api/v0/agents/discover", params=params)
        resp.raise_for_status()
        return resp.json()["agents"]

    # ── CHALLENGE ────────────────────────────────────────
    def send_challenge(self, passport: AgentPassport, target_id: str) -> dict:
        """Send a handshake challenge to another agent."""
        payload = HandshakeProtocol.create_challenge(passport)
        resp = requests.post(
            f"{self.base_url}/api/v0/handshake/challenge",
            json={"target_agent_id": target_id, "handshake": payload["handshake"]},
        )
        resp.raise_for_status()
        return resp.json()

    # ── VERIFY ───────────────────────────────────────────
    def verify(self, handshake_payload: dict) -> dict:
        """Verify a handshake payload via the registry."""
        resp = requests.post(
            f"{self.base_url}/api/v0/handshake/verify",
            json=handshake_payload,
        )
        resp.raise_for_status()
        return resp.json()

    # ── TRUST ────────────────────────────────────────────
    def record_trust(self, record: dict) -> dict:
        """Submit a trust record to the registry."""
        resp = requests.post(
            f"{self.base_url}/api/v0/trust/record",
            json=record,
        )
        resp.raise_for_status()
        return resp.json()

    # ── GET AGENT ────────────────────────────────────────
    def get_agent(self, agent_id: str) -> dict:
        """Look up an agent by DID."""
        resp = requests.get(f"{self.base_url}/api/v0/agents/{agent_id}")
        resp.raise_for_status()
        return resp.json()
