# Agent Handshake Protocol — Technical Specification v0.1

## Overview

v0.1 implements the **Trust Layer** only — the minimum viable layer that no platform has today.

- **Crypto:** Ed25519 (no blockchain)
- **Identity:** Self-sovereign `did:agent:xxx`
- **Transport:** JSON over HTTP (REST API)
- **Storage:** In-memory (replaceable)

---

## Primitives

### 1. REGISTER

Create a new Agent identity.

```
POST /api/v0/agents/register
```

**Request:**
```json
{
  "agent_id": "did:agent:abc123",
  "name": "Alice",
  "public_key": "-----BEGIN PUBLIC KEY-----...",
  "capabilities": ["code-review", "testing"],
  "protocol_version": "0.1"
}
```

**Response:** `201 Created`
```json
{
  "status": "registered",
  "agent_id": "did:agent:abc123"
}
```

---

### 2. DISCOVER

Find agents by capability.

```
GET /api/v0/agents/discover?capability=testing&limit=10
```

**Response:**
```json
{
  "agents": [
    {
      "agent_id": "did:agent:abc123",
      "name": "Alice",
      "capabilities": ["code-review", "testing"],
      "trust_score": 5.0
    }
  ],
  "count": 1
}
```

---

### 3. CHALLENGE

Send a cryptographic challenge to prove identity.

```
POST /api/v0/handshake/challenge
```

**Request:**
```json
{
  "target_agent_id": "did:agent:def456",
  "handshake": {
    "version": "0.1",
    "initiator": {
      "agent_id": "did:agent:abc123",
      "public_key": "-----BEGIN PUBLIC KEY-----...",
      "capabilities": ["code-review"]
    },
    "challenge": {
      "nonce": "a1b2c3d4...",
      "timestamp": 1700000000
    },
    "signature": "base64_encoded_ed25519_signature"
  }
}
```

**How it works:**
1. Initiator creates a random 16-byte nonce
2. Constructs `json.dumps({"nonce": ..., "timestamp": ..., "from": agent_id})` (sorted keys)
3. Signs the bytes with Ed25519 private key
4. Sends public key + signature + challenge

---

### 4. VERIFY

Validate a handshake signature.

```
POST /api/v0/handshake/verify
```

**Request:** Same handshake payload.

**Response (success):**
```json
{
  "valid": true,
  "agent_id": "did:agent:abc123",
  "capabilities": ["code-review"],
  "error": null
}
```

**Response (failure):** `403 Forbidden`
```json
{
  "valid": false,
  "agent_id": "did:agent:abc123",
  "capabilities": [],
  "error": "Signature verification failed"
}
```

**Verification steps:**
1. Extract `challenge` + `initiator.public_key` from payload
2. Reconstruct signed bytes: `json.dumps({"nonce", "timestamp", "from"}, sort_keys=True)`
3. Decode base64 signature
4. Call `Ed25519PublicKey.verify(signature, data)` — raises on invalid

---

### 5. TRUST

Record the outcome of a handshake.

```
POST /api/v0/trust/record
```

**Request:**
```json
{
  "agent_id": "did:agent:abc123",
  "peer_id": "did:agent:def456",
  "success": true,
  "details": "Handshake completed",
  "timestamp": 1700000000,
  "protocol_version": "0.1"
}
```

**Response:** `201 Created`
```json
{
  "status": "recorded",
  "trust_score": 1.0
}
```

**Scoring (v0.1 — simple):**
- `success: true` → peer's trust_score += 1
- `success: false` → peer's trust_score -= 1

---

## DID Format

```
did:agent:<12-char-hex>
```

Example: `did:agent:a1b2c3d4e5f6`

Not registered with any global registry. Self-issued. The agent's Ed25519 public key IS the proof of ownership.

---

## Security Notes

- **No blockchain in v0.1.** Ed25519 is sufficient for identity proof.
- **Private key NEVER leaves the agent.** Only public key is shared.
- **Nonce prevents replay attacks.** Each challenge has a unique random nonce.
- **Trust scoring is simple intentionally.** Complex reputation systems come in v0.3+.
- **Transport security (TLS)** is assumed for HTTP endpoints.

---

## Version History

| Version | Layer | Status |
|---------|-------|--------|
| v0.1 | Trust | This spec |
| v0.2 | Discovery | Planned |
| v0.3 | Capability | Planned |
| v0.4 | Policy | Planned |
| v1.0 | Contract + Settlement | Planned |