"""Agent Handshake Registry — Simple REST API (v0.1).

In-memory registry for MVP. Replace with a database for production.
Run: python server/app.py
"""

import json
from flask import Flask, request, jsonify

from sdk.python.handshake import HandshakeProtocol

app = Flask(__name__)

# ── In-memory store (MVP) ─────────────────────────────
agents: dict = {}          # agent_id -> agent_data
trust_records: list = []   # list of trust records


# ── Register ───────────────────────────────────────────
@app.route("/api/v0/agents/register", methods=["POST"])
def register():
    """Primitive 1: REGISTER — Register a new agent."""
    data = request.get_json()
    agent_id = data.get("agent_id")

    if not agent_id:
        return jsonify({"error": "agent_id is required"}), 400

    if agent_id in agents:
        return jsonify({"error": "Agent already registered"}), 409

    agents[agent_id] = {
        **data,
        "trust_score": 0.0,
        "tx_count": 0,
        "registered_at": data.get("created_at"),
    }

    return jsonify({"status": "registered", "agent_id": agent_id}), 201


# ── Discover ───────────────────────────────────────────
@app.route("/api/v0/agents/discover", methods=["GET"])
def discover():
    """Primitive 2: DISCOVER — Find agents by capability."""
    capability = request.args.get("capability")
    limit = int(request.args.get("limit", 10))

    results = []
    for aid, adata in agents.items():
        if capability and capability not in adata.get("capabilities", []):
            continue
        results.append({"agent_id": aid, **adata})
        if len(results) >= limit:
            break

    return jsonify({"agents": results, "count": len(results)})


# ── Get Agent ──────────────────────────────────────────
@app.route("/api/v0/agents/<agent_id>", methods=["GET"])
def get_agent(agent_id):
    """Look up an agent by DID."""
    if agent_id not in agents:
        return jsonify({"error": "Agent not found"}), 404
    return jsonify({"agent_id": agent_id, **agents[agent_id]})


# ── Challenge ──────────────────────────────────────────
@app.route("/api/v0/handshake/challenge", methods=["POST"])
def challenge():
    """Primitive 3: CHALLENGE — Accept a handshake challenge."""
    data = request.get_json()
    handshake = data.get("handshake")

    if not handshake:
        return jsonify({"error": "handshake payload required"}), 400

    # Verify immediately
    result = HandshakeProtocol.verify({"handshake": handshake})

    return jsonify(result)


# ── Verify ─────────────────────────────────────────────
@app.route("/api/v0/handshake/verify", methods=["POST"])
def verify():
    """Primitive 4: VERIFY — Verify a handshake payload."""
    data = request.get_json()
    result = HandshakeProtocol.verify(data)

    if result["valid"] and result["agent_id"] in agents:
        return jsonify(result)
    elif result["valid"]:
        return jsonify({**result, "error": "Agent not registered"}), 404
    else:
        return jsonify(result), 403


# ── Trust ──────────────────────────────────────────────
@app.route("/api/v0/trust/record", methods=["POST"])
def trust():
    """Primitive 5: TRUST — Record a trust outcome."""
    data = request.get_json()
    agent_id = data.get("agent_id")
    peer_id = data.get("peer_id")
    success = data.get("success")

    if not all([agent_id, peer_id, success is not None]):
        return jsonify({"error": "agent_id, peer_id, success required"}), 400

    if agent_id not in agents or peer_id not in agents:
        return jsonify({"error": "Both agents must be registered"}), 404

    record = {**data, "id": len(trust_records)}
    trust_records.append(record)

    # Update trust score (simple: +1 for success, -1 for failure)
    if success:
        agents[peer_id]["trust_score"] += 1
        agents[peer_id]["tx_count"] += 1
    else:
        agents[peer_id]["trust_score"] -= 1
        agents[peer_id]["tx_count"] += 1

    return jsonify({"status": "recorded", "trust_score": agents[peer_id]["trust_score"]}), 201


# ── Health ─────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "version": "0.1",
        "registered_agents": len(agents),
        "trust_records": len(trust_records),
    })


if __name__ == "__main__":
    print("Agent Handshake Registry v0.1")
    print("Endpoints:")
    print("  POST /api/v0/agents/register")
    print("  GET  /api/v0/agents/discover?capability=xxx")
    print("  GET  /api/v0/agents/<agent_id>")
    print("  POST /api/v0/handshake/challenge")
    print("  POST /api/v0/handshake/verify")
    print("  POST /api/v0/trust/record")
    print()
    app.run(host="0.0.0.0", port=5000, debug=True)
