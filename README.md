<p align="center">
  <h1 align="center">Agent Handshake Protocol</h1>
  <p align="center"><strong>The Trust Layer for the Agent-to-Agent Economy</strong></p>
  <p align="center">
    <code>v0.1 — Trust Layer Only</code> ·
    <code>Ed25519</code> ·
    <code>No Blockchain Required</code>
  </p>
</p>

---

## The Problem

Every AI Agent is trapped inside its platform. An Agent built on OpenAI has no identity on Anthropic. There is **no universal trust layer** that lets any Agent verify another Agent's identity before transacting.

Everyone is building payment protocols (Layer 5). **Nobody is building the trust layer (Layer 1).**

---

## The Solution

A lightweight cryptographic handshake that happens **before** any transaction:

```
Agent A ─── CHALLENGE ────→ Agent B
Agent A ←── SIGNATURE ──── Agent B
Agent A ─── TRUST RECORD ─→ Registry
```

Each Agent owns a **passport** — a portable Ed25519 identity that no platform controls.

---

## 5 Primitives

| # | Primitive | What it does |
|---|-----------|-------------|
| 1 | **REGISTER** | Generate Ed25519 keypair + `did:agent:xxx` |
| 2 | **DISCOVER** | Find agents by capability |
| 3 | **CHALLENGE** | Send nonce + signature to prove identity |
| 4 | **VERIFY** | Validate Ed25519 signature against public key |
| 5 | **TRUST** | Record trust outcome (updates score) |

---

## 5-Layer Stack

```
┌─────────────────────────────────┐
│  5. Settlement (Payment)       │  ← v1.0
├─────────────────────────────────┤
│  4. Policy (Rules + SLA)       │  ← v0.4
├─────────────────────────────────┤
│  3. Capability (Proof of Skill)│  ← v0.3
├─────────────────────────────────┤
│  2. Discovery (Find Agents)    │  ← v0.2
├─────────────────────────────────┤
│  1. Trust (Identity + Verify)  │  ← v0.1 ← WE ARE HERE
└─────────────────────────────────┘
```

We start at Layer 1. Each layer builds on the one below.

---

## Quick Start

### 1. Install

```bash
pip install cryptography flask requests
```

### 2. Create an Agent (5 seconds)

```python
from sdk.python import AgentPassport, HandshakeProtocol

# REGISTER
alice = AgentPassport(name="Alice", capabilities=["code-review"])
print(alice.agent_id)  # did:agent:a1b2c3d4e5f6

bob = AgentPassport(name="Bob", capabilities=["data-analysis"])

# Full handshake in one line
result = HandshakeProtocol.full_handshake(alice, bob)
print(result["mutual_trust"])  # True
```

### 3. Run the Registry Server

```bash
cd server
python app.py
# → Listening on http://localhost:5000
```

### 4. Use the Client

```python
from sdk.python import AgentPassport, HandshakeClient

passport = AgentPassport(name="Charlie", capabilities=["testing"])
client = HandshakeClient("http://localhost:5000")

client.register(passport)
agents = client.discover(capability="testing")
```

### 5. Run the Example

```bash
python examples/basic_handshake.py
```

---

## Project Structure

```
agent-handshake-protocol/
├── README.md                    # This file
├── spec/
│   └── handshake-v0.1.md       # Technical specification
├── sdk/
│   └── python/
│       ├── __init__.py
│       ├── agent_passport.py   # Ed25519 identity + DID
│       ├── handshake.py        # 5 primitives implementation
│       └── client.py           # HTTP client for registry
├── server/
│   └── app.py                  # REST API (Flask, in-memory)
└── examples/
    └── basic_handshake.py     # Offline demo (no server needed)
```

---

## Handshake Payload Format

```json
{
  "handshake": {
    "version": "0.1",
    "initiator": {
      "agent_id": "did:agent:abc123",
      "public_key": "-----BEGIN PUBLIC KEY-----...",
      "capabilities": ["code-review", "testing"]
    },
    "challenge": {
      "nonce": "a1b2c3d4e5f6...",
      "timestamp": 1700000000
    },
    "signature": "base64_ed25519_signature"
  }
}
```

---

## Roadmap

| Version | Layer | Status |
|---------|-------|--------|
| **v0.1** | **Trust** | **This release** |
| v0.2 | Discovery | Next |
| v0.3 | Capability | Planned |
| v0.4 | Policy | Planned |
| v1.0 | Contract + Money | Planned |
| v2.0 | Dispute Resolution | Future |

---

## Why No Blockchain?

Ed25519 signatures provide cryptographic proof of identity without any blockchain. Blockchain becomes relevant at v1.0 (Settlement layer) — not before. Simple is the moat.

---

## License

MIT
