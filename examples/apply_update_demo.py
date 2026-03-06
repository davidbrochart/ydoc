"""
Apply Update Demo for YDoc

This example demonstrates the new apply_update() functionality,
showing how to apply binary updates to documents.
"""

from ydoc import Doc, apply_update, get_state_update, Encoder


def demo_basic_apply_update():
    """Demonstrate basic apply_update functionality."""
    print("=== Basic Apply Update Demo ===")

    # Create a document
    doc = Doc()
    doc.client_id = 1
    print(f"Created document with client ID: {doc.client_id}")

    # Create a binary update from another client
    encoder = Encoder()
    encoder.write_var_uint(1)  # State vector length
    encoder.write_var_uint(2)  # Client ID 2
    encoder.write_var_uint(100)  # Clock 100
    update = encoder.to_bytes()

    print(f"Created update from client 2: {len(update)} bytes")

    # Apply the update
    apply_update(doc, update, origin="client_2")
    print("✓ Successfully applied update")

    # Check transaction metadata
    if doc._transaction_cleanups:
        last_tx = doc._transaction_cleanups[-1]
        print(f"Transaction metadata: {last_tx.meta}")

    print()


def demo_update_with_origin():
    """Demonstrate applying updates with origin tracking."""
    print("=== Update with Origin Tracking ===")

    # Create multiple documents representing different clients
    docs = [Doc() for _ in range(3)]

    # Assign client IDs
    for i, doc in enumerate(docs):
        doc.client_id = i + 1

    print(f"Created {len(docs)} documents with client IDs: {[doc.client_id for doc in docs]}")

    # Client 2 creates an update and sends to others
    encoder = Encoder()
    encoder.write_var_uint(1)  # State vector length
    encoder.write_var_uint(2)  # Client ID 2
    encoder.write_var_uint(50)  # Clock 50
    update_from_client_2 = encoder.to_bytes()

    # Clients 1 and 3 apply the update
    apply_update(docs[0], update_from_client_2, origin="client_2")
    apply_update(docs[2], update_from_client_2, origin="client_2")

    print("✓ Client 1 applied update from client 2")
    print("✓ Client 3 applied update from client 2")

    # Verify transactions were created
    for i, doc in enumerate([docs[0], docs[2]]):
        if doc._transaction_cleanups:
            last_tx = doc._transaction_cleanups[-1]
            print(f"✓ Client {i+1} transaction origin: {last_tx.meta.get('origin')}")

    print()


def demo_update_propagation():
    """Demonstrate update propagation between multiple clients."""
    print("=== Update Propagation Demo ===")

    # Create a network of documents
    alice = Doc()
    bob = Doc()
    charlie = Doc()

    alice.client_id = 1
    bob.client_id = 2
    charlie.client_id = 3

    print("Created network: Alice (1), Bob (2), Charlie (3)")

    # Alice makes changes and creates update
    alice_encoder = Encoder()
    alice_encoder.write_var_uint(1)  # State vector length
    alice_encoder.write_var_uint(1)  # Client ID 1
    alice_encoder.write_var_uint(75)  # Clock 75
    alice_update = alice_encoder.to_bytes()

    # Bob makes changes and creates update
    bob_encoder = Encoder()
    bob_encoder.write_var_uint(1)  # State vector length
    bob_encoder.write_var_uint(2)  # Client ID 2
    bob_encoder.write_var_uint(125)  # Clock 125
    bob_update = bob_encoder.to_bytes()

    print(f"Alice created update: {len(alice_update)} bytes")
    print(f"Bob created update: {len(bob_update)} bytes")

    # Apply updates to Charlie (the server/relay)
    apply_update(charlie, alice_update, origin="alice")
    apply_update(charlie, bob_update, origin="bob")

    print("✓ Charlie received updates from Alice and Bob")

    # Charlie now has both updates and can propagate them
    # In a real system, Charlie would merge these and send back to clients

    if charlie._transaction_cleanups:
        print(f"✓ Charlie processed {len(charlie._transaction_cleanups)} updates")
        for i, tx in enumerate(charlie._transaction_cleanups):
            print(f"  Update {i+1} origin: {tx.meta.get('origin')}")

    print()


def demo_error_handling():
    """Demonstrate robust error handling."""
    print("=== Error Handling Demo ===")

    doc = Doc()

    # Test with empty update
    empty_encoder = Encoder()
    empty_encoder.write_var_uint(0)  # Empty state vector
    empty_update = empty_encoder.to_bytes()

    try:
        apply_update(doc, empty_update, origin="empty_test")
        print("✓ Empty update handled gracefully")
    except Exception as e:
        print(f"❌ Empty update failed: {e}")

    # Test with malformed update (incomplete data)
    try:
        malformed_update = b'\x01'  # Just the length, missing client data
        apply_update(doc, malformed_update, origin="malformed_test")
        print("❌ Malformed update should have failed")
    except Exception as e:
        print(f"✓ Malformed update correctly rejected: {type(e).__name__}")

    print()


def main():
    """Run all apply_update demos."""
    print("YDoc Apply Update Demo")
    print("=" * 40)
    print()

    demo_basic_apply_update()
    demo_update_with_origin()
    demo_update_propagation()
    demo_error_handling()

    print("🎉 All apply_update demos completed successfully!")
    print()
    print("Key Features Demonstrated:")
    print("- Basic update application")
    print("- Origin tracking for updates")
    print("- Multi-client update propagation")
    print("- Robust error handling")
    print("- Transaction-based update processing")


if __name__ == "__main__":
    main()