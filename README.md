<div align="center">

<img src="https://img.shields.io/badge/version-0.1-blue?style=for-the-badge" alt="v0.1"/>
<img src="https://img.shields.io/badge/crypto-Ed25519-9B59B6?style=for-the-badge" alt="Ed25519"/>
<img src="https://img.shields.io/badge/blockchain-NOT%20REQUIRED-27AE60?style=for-the-badge" alt="No Blockchain"/>
<img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="MIT"/>

<br/><br/>

<img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 60'><text x='200' y='40' text-anchor='middle' font-family='monospace' font-size='24' fill='%231284BA' font-weight='bold'>Agent Handshake Protocol</text></svg>" width="400" alt="AHP"/>

<sup><strong>The Trust Layer for the Agent-to-Agent Economy</strong></sup>

<br/><br/>

<a href="#quick-start"><img src="https://img.shields.io/badge/Get_Started-5_seconds-1284BA?style=flat-square"/></a>
<a href="spec/handshake-v0.1.md"><img src="https://img.shields.io/badge/Spec-v0.1-9B59B6?style=flat-square"/></a>
<a href="#roadmap"><img src="https://img.shields.io/badge/Roadmap-5_Layers-orange?style=flat-square"/></a>

</div>

<div align="center">

`ai-agents` · `agent-protocol` · `agent-identity` · `trust-layer` · `agent-to-agent` · `ed25519` · `self-sovereign-identity` · `did` · `multi-agent-systems` · `agent-economy` · `zero-trust` · `decentralized-identity` · `cryptographic-handshake` · `ai-infrastructure` · `agent-communication`

</div>

---

## ⚠️ The Problem

Every AI Agent is **trapped inside its platform**.

An Agent built on OpenAI has zero identity on Anthropic. An Agent from Company X cannot verify an Agent from Company Y. There is no universal mechanism for one Agent to answer the most basic question before any interaction:

> **"Who are you, and can I trust you?"**

Meanwhile, the industry is obsessed with building **payment protocols** — the top of the stack. But without trust, identity, and verification at the bottom, payments between Agents are meaningless.

```
  What everyone builds        What nobody builds
  ─────────────────        ────────────────────

  ┌──────────────┐
  │  💰 Payment  │         ┌──────────────────┐
  └──────────────┘         │ 🔐 Trust Layer  │
                            └──────────────────┘
```

---

## 💡 The Solution

A lightweight **cryptographic handshake** that happens *before* any Agent interaction. Think of it as **TLS for Agents** — but for identity, not encryption.

Each Agent owns a **Passport**: a portable, self-sovereign Ed25519 identity that **no platform controls**.

```
  Agent A                        Agent B
  ───────                        ───────
  ┌──────────┐                  ┌──────────┐
  │ Passport │                  │ Passport │
  │ (Ed25519)│                  │ (Ed25519)│
  └────┬─────┘                  └────┬─────┘
       │                             │
       │──── CHALLENGE (nonce) ────→│
       │←─── SIGNATURE ────────────│
       │                             │
       │──── TRUST RECORD ────────→│ Registry
       │                             │
       ╰──── ✅ Mutual Trust ──────╯
```

---

## 🔧 5 Primitives

The entire protocol is built on **5 operations** that form a complete trust cycle:

| # | Primitive | Purpose | Analogy |
|:-:|:----------:|---------|---------|
| 1 | `REGISTER` | Generate Ed25519 keypair + receive `did:agent:xxx` | Get a passport |
| 2 | `DISCOVER` | Find agents by capability | Search a directory |
| 3 | `CHALLENGE` | Send cryptographic nonce + sign it | "Prove you're you" |
| 4 | `VERIFY` | Validate signature against claimed public key | Check the passport |
| 5 | `TRUST` | Record outcome → update trust score | Leave a review |

---

## 🏗️ 5-Layer Stack

We build **bottom-up**. Each layer depends on the one below it. We start at Layer 1 — the layer nobody else is building.

```
  ┌─────────────────────────────────────────┐
  │  L5  Settlement    Payment & Micropay  │  v1.0+
  ├─────────────────────────────────────────┤
  │  L4  Policy        Rules, SLA, Limits  │  v0.4
  ├─────────────────────────────────────────┤
  │  L3  Capability    Proof of Skill      │  v0.3
  ├─────────────────────────────────────────┤
  │  L2  Discovery     Find Agents         │  v0.2
  ├─────────────────────────────────────────┤
  │  L1  Trust         Identity + Verify   │  v0.1  ← We are here
  └─────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### Install

```bash
pip install cryptography flask requests
```

### Create Two Agents & Handshake in 5 Lines

```python
from sdk.python import AgentPassport, HandshakeProtocol

# REGISTER — Each agent creates its own identity
alice = AgentPassport(name="Alice", capabilities=["code-review"])
bob   = AgentPassport(name="Bob",   capabilities=["data-analysis"])

# FULL HANDSHAKE — Verify each other cryptographically
result = HandshakeProtocol.full_handshake(alice, bob)
print(result["mutual_trust"])  # True
```

### Run the Registry Server

```bash
cd server && python app.py
# → Agent Handshake Registry v0.1 listening on port 5000
```

### Or Just Try the Offline Demo

```bash
python examples/basic_handshake.py
```

<details>
<summary>📖 <strong>Full example with HTTP client</strong></summary>

```python
from sdk.python import AgentPassport, HandshakeClient

passport = AgentPassport(name="Charlie", capabilities=["testing"])
client = HandshakeClient("http://localhost:5000")

# Register
client.register(passport)

# Discover
agents = client.discover(capability="testing")

# Challenge + Verify
result = client.send_challenge(passport, target_id="did:agent:abc123")
```

</details>

---

## 📦 Project Structure

```
agent-handshake-protocol/
├── README.md                      # You are here
├── spec/
│   └── handshake-v0.1.md         # Full API specification
├── sdk/
│   └── python/
│       ├── __init__.py
│       ├── agent_passport.py     # Ed25519 identity + DID generation
│       ├── handshake.py          # 5 primitives: register → discover → challenge → verify → trust
│       └── client.py             # Async-ready HTTP client
├── server/
│   └── app.py                    # REST API (6 endpoints, Flask, in-memory)
└── examples/
    └── basic_handshake.py        # Offline demo — no server needed
```

---

## 📄 Handshake Payload

Every handshake is a single JSON message. The initiator signs a nonce with their private key. The verifier checks it with the public key.

```json
{
  "handshake": {
    "version": "0.1",
    "initiator": {
      "agent_id": "did:agent:a1b2c3d4e5f6",
      "public_key": "-----BEGIN PUBLIC KEY-----...",
      "capabilities": ["code-review", "testing"]
    },
    "challenge": {
      "nonce": "f47ac10b58cc...",
      "timestamp": 1700000000
    },
    "signature": "Ed25519_base64_signature"
  }
}
```

---

## 🗺️ Roadmap

| Version | Layer | Focus | Status |
|:-------:|:-----:|-------|:------:|
| **v0.1** | **L1** | **Trust — Identity + Verify** | ✅ **This release** |
| v0.2 | L2 | Discovery — Find agents by capability | 🔜 Next |
| v0.3 | L3 | Capability — Prove what you can do | 📋 Planned |
| v0.4 | L4 | Policy — Rules, SLAs, spending limits | 📋 Planned |
| v1.0 | L5 | Settlement — Smart contracts + micropayments | 📋 Planned |
| v2.0 | L5+ | Dispute — Resolution + arbitration | 🔮 Future |

---

## ❓ Why No Blockchain?

Ed25519 signatures give us **cryptographic proof of identity** without any blockchain. No gas fees, no consensus delays, no token needed.

Blockchain becomes relevant at **v1.0** when we reach the Settlement layer. Until then, simplicity is the moat.

> _"The best protocol is the one that's so simple, everyone adopts it before anyone notices."_

---

## 🏷️ Topics

```
ai-agents, agent-protocol, agent-identity, trust-layer, agent-to-agent,
ed25519, self-sovereign-identity, did, decentralized-identity,
multi-agent-systems, agent-economy, zero-trust, cryptographic-handshake,
ai-infrastructure, agent-communication, agent-security, passport,
handshake-protocol, agent-interop, identity-verification
```

---

## 📜 License

MIT — Use it, fork it, build on top of it.
