"""
Encode/Apply Update Demo for YDoc

This example demonstrates the complete encode_state_as_update() and apply_update()
cycle, showing how documents can synchronize their state.
"""

from ydoc import Doc, encode_state_as_update, apply_update, Encoder, Decoder


def demo_basic_encode_apply():
    """Demonstrate basic encode/apply cycle."""
    print("=== Basic Encode/Apply Demo ===")

    # Create two documents
    alice_doc = Doc()
    bob_doc = Doc()

    alice_doc.client_id = 1
    bob_doc.client_id = 2

    print(f"Alice's document (client {alice_doc.client_id})")
    print(f"Bob's document (client {bob_doc.client_id})")

    # Alice encodes her current state
    alice_update = encode_state_as_update(alice_doc)
    print(f"Alice encoded her state: {len(alice_update)} bytes")

    # Parse the update to see what's in it
    decoder = Decoder(alice_update)
    state_vector_length = decoder.read_var_uint()
    print(f"Update contains state vector with {state_vector_length} clients")

    for i in range(state_vector_length):
        client_id = decoder.read_var_uint()
        clock = decoder.read_var_uint()
        print(f"  Client {client_id}: clock {clock}")

    # Bob applies Alice's update
    apply_update(bob_doc, alice_update, origin="alice")
    print("Bob applied Alice's update")

    # Check that Bob has the transaction
    if bob_doc._transaction_cleanups:
        last_tx = bob_doc._transaction_cleanups[-1]
        print(f"Bob's transaction metadata: {last_tx.meta}")

    print()


def demo_bidirectional_sync():
    """Demonstrate bidirectional synchronization."""
    print("=== Bidirectional Synchronization Demo ===")

    # Create two documents
    doc_a = Doc()
    doc_b = Doc()

    doc_a.client_id = 101
    doc_b.client_id = 102

    print("Initial state:")
    print(f"Doc A (client {doc_a.client_id})")
    print(f"Doc B (client {doc_b.client_id})")

    # Both documents encode their current state
    update_a = encode_state_as_update(doc_a)
    update_b = encode_state_as_update(doc_b)

    print(f"Doc A encoded state: {len(update_a)} bytes")
    print(f"Doc B encoded state: {len(update_b)} bytes")

    # Exchange updates
    apply_update(doc_a, update_b, origin="doc_b")
    apply_update(doc_b, update_a, origin="doc_a")

    print("✓ Documents exchanged updates")

    # Both should now have transactions from each other
    if doc_a._transaction_cleanups:
        print(f"Doc A received {len(doc_a._transaction_cleanups)} update(s) from Doc B")

    if doc_b._transaction_cleanups:
        print(f"Doc B received {len(doc_b._transaction_cleanups)} update(s) from Doc A")

    print()


def demo_state_vector_targeting():
    """Demonstrate encoding against a target state vector."""
    print("=== State Vector Targeting Demo ===")

    # Create a document
    doc = Doc()
    doc.client_id = 42

    # Create a target state vector (simulating what a remote client knows)
    target_encoder = Encoder()
    target_encoder.write_var_uint(1)  # One client
    target_encoder.write_var_uint(42)  # Our client ID
    target_encoder.write_var_uint(10)  # They know up to clock 10
    target_state = target_encoder.to_bytes()

    print("Doc has client ID 42")
    print("Target state: client 42 knows up to clock 10")

    # Encode against the target
    update = encode_state_as_update(doc, target_state)
    print(f"Encoded update: {len(update)} bytes")

    # Parse the update
    decoder = Decoder(update)
    sv_length = decoder.read_var_uint()
    print(f"Update contains {sv_length} client(s) in state vector")

    if sv_length > 0:
        client_id = decoder.read_var_uint()
        clock = decoder.read_var_uint()
        print(f"Client {client_id} is at clock {clock}")

        if clock > 10:
            print("✓ Update contains new changes beyond the target")
        else:
            print("✓ No new changes since target")

    print()


def demo_multi_client_sync():
    """Demonstrate synchronization among multiple clients."""
    print("=== Multi-Client Synchronization Demo ===")

    # Create a network of clients
    clients = [Doc() for _ in range(4)]

    # Assign client IDs
    for i, client in enumerate(clients):
        client.client_id = i + 1

    print(f"Created {len(clients)} clients with IDs: {[c.client_id for c in clients]}")

    # Each client encodes their state
    updates = []
    for i, client in enumerate(clients):
        update = encode_state_as_update(client)
        updates.append(update)
        print(f"Client {i + 1} encoded {len(update)} bytes")

    # Client 1 (the "server") collects all updates
    server = clients[0]

    for i, update in enumerate(updates[1:], start=2):  # Skip client 1's own update
        apply_update(server, update, origin=f"client_{i}")

    print(f"✓ Server processed {len(server._transaction_cleanups)} updates")

    # Server can now distribute the merged state back to clients
    server_update = encode_state_as_update(server)
    print(f"Server encoded merged state: {len(server_update)} bytes")

    # Distribute to other clients
    for i, client in enumerate(clients[1:], start=2):
        apply_update(client, server_update, origin="server")
        print(f"✓ Client {i} received server update")

    print()


def demo_error_handling():
    """Demonstrate robust error handling."""
    print("=== Error Handling Demo ===")

    doc = Doc()

    # Test with malformed target state
    try:
        malformed_target = b"\x01\x00"  # Incomplete state vector
        update = encode_state_as_update(doc, malformed_target)
        print("✓ Malformed target handled gracefully")
    except Exception as e:
        print(f"❌ Malformed target caused error: {e}")

    # Test with empty target
    try:
        empty_target = b"\x00"  # Empty state vector
        update = encode_state_as_update(doc, empty_target)
        print("✓ Empty target handled correctly")
    except Exception as e:
        print(f"❌ Empty target caused error: {e}")

    print()


def main():
    """Run all encode/apply demos."""
    print("YDoc Encode/Apply Update Demo")
    print("=" * 45)
    print()

    demo_basic_encode_apply()
    demo_bidirectional_sync()
    demo_state_vector_targeting()
    demo_multi_client_sync()
    demo_error_handling()

    print("🎉 All encode/apply demos completed successfully!")
    print()
    print("Key Features Demonstrated:")
    print("- Basic encode_state_as_update() functionality")
    print("- apply_update() for receiving updates")
    print("- Bidirectional document synchronization")
    print("- State vector targeting")
    print("- Multi-client update propagation")
    print("- Robust error handling")
    print("- Complete encode/apply roundtrip")


if __name__ == "__main__":
    main()
