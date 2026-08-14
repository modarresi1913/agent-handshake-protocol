"""Handshake Protocol — The 5 primitives.

REGISTER  → Create identity, get DID
DISCOVER  → Find agents by capability
CHALLENGE → Send cryptographic challenge
VERIFY    → Validate signature & identity
TRUST     → Record trust outcome
"""

import json
import time
import secrets
import base64
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

from .agent_passport import AgentPassport


class HandshakeProtocol:
    """Implements the 5 core primitives of the Agent Handshake Protocol."""

    PROTOCOL_VERSION = "0.1"

    # ── REGISTER ─────────────────────────────────────────
    @staticmethod
    def register(name: str, capabilities: Optional[list[str]] = None) -> AgentPassport:
        """Primitive 1: Create a new Agent identity.

        Generates Ed25519 keypair and returns an AgentPassport.
        """
        passport = AgentPassport(name=name, capabilities=capabilities)
        return passport

    # ── CHALLENGE ────────────────────────────────────────
    @staticmethod
    def create_challenge(initiator: AgentPassport) -> dict:
        """Primitive 3: Create a cryptographic challenge.

        The initiator signs a nonce to prove identity.
        Returns a handshake payload to send to the responder.
        """
        nonce = secrets.token_hex(16)
        challenge_payload = json.dumps(
            {"nonce": nonce, "timestamp": int(time.time()), "from": initiator.agent_id},
            sort_keys=True,
        ).encode()

        signature = initiator.sign(challenge_payload)

        return {
            "handshake": {
                "version": HandshakeProtocol.PROTOCOL_VERSION,
                "initiator": {
                    "agent_id": initiator.agent_id,
                    "public_key": initiator.public_key_pem,
                    "capabilities": initiator.capabilities,
                },
                "challenge": {
                    "nonce": nonce,
                    "timestamp": int(time.time()),
                },
                "signature": signature,
            }
        }

    # ── VERIFY ──────────────────────────────────────────
    @staticmethod
    def verify(handshake_payload: dict) -> dict:
        """Primitive 4: Verify a handshake payload.

        Checks the signature against the claimed public key.
        Returns {"valid": bool, "agent_id": str, "error": str|None}
        """
        try:
            hs = handshake_payload["handshake"]
            initiator = hs["initiator"]
            challenge = hs["challenge"]
            signature_b64 = hs["signature"]

            # Reconstruct the signed payload
            challenge_data = json.dumps(
                {"nonce": challenge["nonce"], "timestamp": challenge["timestamp"], "from": initiator["agent_id"]},
                sort_keys=True,
            ).encode()

            # Load public key
            pub_key_pem = initiator["public_key"].encode()
            pub_key = serialization.load_pem_public_key(pub_key_pem)

            # Verify signature
            signature_bytes = base64.b64decode(signature_b64)
            pub_key.verify(signature_bytes, challenge_data)

            return {
                "valid": True,
                "agent_id": initiator["agent_id"],
                "capabilities": initiator["capabilities"],
                "error": None,
            }
        except Exception as e:
            return {
                "valid": False,
                "agent_id": initiator.get("agent_id", "unknown"),
                "capabilities": [],
                "error": str(e),
            }

    # ── TRUST ────────────────────────────────────────────
    @staticmethod
    def trust_record(
        agent_id: str,
        peer_id: str,
        success: bool,
        details: Optional[str] = None,
    ) -> dict:
        """Primitive 5: Record a trust outcome.

        Returns a trust record to be submitted to the registry.
        """
        return {
            "agent_id": agent_id,
            "peer_id": peer_id,
            "success": success,
            "details": details,
            "timestamp": int(time.time()),
            "protocol_version": HandshakeProtocol.PROTOCOL_VERSION,
        }

    # ── Full handshake flow (convenience) ────────────────
    @staticmethod
    def full_handshake(alice: AgentPassport, bob: AgentPassport) -> dict:
        """Execute a complete handshake between two agents.

        Returns the full result including verification.
        """
        # Alice creates challenge
        payload = HandshakeProtocol.create_challenge(alice)

        # Bob verifies Alice
        result_alice = HandshakeProtocol.verify(payload)

        # Bob creates challenge (response)
        response = HandshakeProtocol.create_challenge(bob)

        # Alice verifies Bob
        result_bob = HandshakeProtocol.verify(response)

        # Both valid → trust
        mutual_trust = result_alice["valid"] and result_bob["valid"]

        return {
            "mutual_trust": mutual_trust,
            "alice_verified": result_alice,
            "bob_verified": result_bob,
            "trust_record_alice": (
                HandshakeProtocol.trust_record(alice.agent_id, bob.agent_id, mutual_trust)
                if mutual_trust
                else None
            ),
            "trust_record_bob": (
                HandshakeProtocol.trust_record(bob.agent_id, alice.agent_id, mutual_trust)
                if mutual_trust
                else None
            ),
        }
