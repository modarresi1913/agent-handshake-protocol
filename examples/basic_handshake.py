"""Basic Handshake Example.

Demonstrates the full flow without a server (local/offline).
Run:  python examples/basic_handshake.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sdk.python.agent_passport import AgentPassport
from sdk.python.handshake import HandshakeProtocol


def main():
    # ── 1. REGISTER: Two agents create identities ──────
    print("=" * 50)
    print("1. REGISTER")
    print("=" * 50)

    alice = AgentPassport(name="Alice", capabilities=["code-review", "testing"])
    bob = AgentPassport(name="Bob", capabilities=["data-analysis", "testing"])

    print(f"  Alice: {alice.agent_id}")
    print(f"  Bob:   {bob.agent_id}")

    # ── 2. CHALLENGE: Alice challenges Bob ──────────────
    print("\n" + "=" * 50)
    print("2. CHALLENGE")
    print("=" * 50)

    challenge = HandshakeProtocol.create_challenge(alice)
    print(f"  Nonce:   {challenge['handshake']['challenge']['nonce']}")
    print(f"  Signed: {challenge['handshake']['signature'][:40]}...")

    # ── 3. VERIFY: Bob verifies Alice ───────────────────
    print("\n" + "=" * 50)
    print("3. VERIFY")
    print("=" * 50)

    result = HandshakeProtocol.verify(challenge)
    print(f"  Valid:     {result['valid']}")
    print(f"  Agent ID:  {result['agent_id']}")
    print(f"  Capabilities: {result['capabilities']}")

    # ── 4. Full mutual handshake ────────────────────────
    print("\n" + "=" * 50)
    print("4. FULL MUTUAL HANDSHAKE")
    print("=" * 50)

    outcome = HandshakeProtocol.full_handshake(alice, bob)
    print(f"  Mutual Trust: {outcome['mutual_trust']}")
    print(f"  Alice verified: {outcome['alice_verified']['valid']}")
    print(f"  Bob verified:   {outcome['bob_verified']['valid']}")

    # ── 5. TRUST: Record the outcome ────────────────────
    print("\n" + "=" * 50)
    print("5. TRUST")
    print("=" * 50)

    trust_record = HandshakeProtocol.trust_record(
        agent_id=alice.agent_id,
        peer_id=bob.agent_id,
        success=outcome["mutual_trust"],
        details="Full handshake completed successfully",
    )
    print(f"  Record: {trust_record}")

    # ── 6. Tampered signature (should FAIL) ─────────────
    print("\n" + "=" * 50)
    print("6. TAMPERED SIGNATURE (expected: FAIL)")
    print("=" * 50)

    tampered = challenge.copy()
    tampered["handshake"]["signature"] = "AAAA" + tampered["handshake"]["signature"][4:]
    bad_result = HandshakeProtocol.verify(tampered)
    print(f"  Valid: {bad_result['valid']}")
    print(f"  Error:  {bad_result['error'][:60]}...")

    print("\n" + "=" * 50)
    print("All primitives demonstrated successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
