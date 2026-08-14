"""Agent Passport — Portable cryptographic identity for any Agent.

Every Agent owns its passport. No platform controls it.
Uses Ed25519 asymmetric cryptography (no blockchain required).
"""

import json
import time
import uuid
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


class AgentPassport:
    """Portable, self-sovereign Agent identity."""

    def __init__(
        self,
        name: str,
        capabilities: Optional[list[str]] = None,
        private_key: Optional[Ed25519PrivateKey] = None,
        agent_id: Optional[str] = None,
    ):
        self.name = name
        self.capabilities = capabilities or []
        self._private_key = private_key or Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        self.agent_id = agent_id or self._generate_did()
        self.created_at = int(time.time())
        self.trust_score: float = 0.0
        self.tx_count: int = 0

    # ── DID ──────────────────────────────────────────────
    @staticmethod
    def _generate_did() -> str:
        """Generate a did:agent:xxx identifier."""
        raw = uuid.uuid4().hex[:12]
        return f"did:agent:{raw}"

    # ── Key serialization ───────────────────────────────
    @property
    def public_key_pem(self) -> str:
        """Public key in PEM format."""
        return (
            self._public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode()
        )

    @property
    def private_key_pem(self) -> str:
        """Private key in PEM format (handle with care!)."""
        return (
            self._private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            .decode()
        )

    @classmethod
    def from_private_key_pem(cls, pem: str, name: str, **kwargs) -> "AgentPassport":
        """Reconstruct a passport from a saved private key PEM."""
        private_key = serialization.load_pem_private_key(pem.encode(), password=None)
        return cls(name=name, private_key=private_key, **kwargs)

    # ── Signing ──────────────────────────────────────────
    def sign(self, data: bytes) -> str:
        """Sign arbitrary bytes, return base64 signature."""
        import base64

        sig = self._private_key.sign(data)
        return base64.b64encode(sig).decode()

    # ── Export ───────────────────────────────────────────
    def to_dict(self) -> dict:
        """Serializable passport payload (no private key!)."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "public_key": self.public_key_pem,
            "capabilities": self.capabilities,
            "trust_score": self.trust_score,
            "tx_count": self.tx_count,
            "created_at": self.created_at,
            "protocol_version": "0.1",
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def save_private_key(self, path: str) -> None:
        """Persist private key to file."""
        with open(path, "w") as f:
            f.write(self.private_key_pem)

    def __repr__(self) -> str:
        return f"AgentPassport(id={self.agent_id}, name={self.name!r})"
