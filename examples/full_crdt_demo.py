"""
Full CRDT Demo - Demonstrating complete YDoc functionality
"""

from ydoc import Doc, create_id, Item


def main():
    print("=== Full YDoc CRDT Demo ===")

    # Create two documents representing different clients
    alice_doc = Doc(guid="alice")
    bob_doc = Doc(guid="bob")

    print(f"Alice's document: client_id={alice_doc.client_id}, guid={alice_doc.guid}")
    print(f"Bob's document: client_id={bob_doc.client_id}, guid={bob_doc.guid}")

    print("\n1. Demonstrating transaction system...")

    # Alice creates some content in a transaction
    def alice_transaction(txn):
        print(f"   Alice's transaction started (origin: {txn.origin})")
        print(f"   Before state: {txn.before_state}")

        # Create an item
        alice_id = create_id(alice_doc.client_id, 1)
        alice_item = Item(id=alice_id, content=["Hello from Alice! "])
        alice_doc.store.add_struct(alice_item)

        print(f"   Alice created: {alice_item.content}")
        return "Alice's transaction completed"

    result = alice_doc.transact(alice_transaction, origin="alice_client")
    print(f"   Transaction result: {result}")
    print(f"   Alice's document state: {alice_doc.store.get_state_vector()}")

    print("\n2. Bob creates content concurrently...")

    def bob_transaction(txn):
        print("   Bob's transaction started")

        # Bob creates his own item
        bob_id = create_id(bob_doc.client_id, 1)
        bob_item = Item(id=bob_id, content=["Hello from Bob! "])
        bob_doc.store.add_struct(bob_item)

        print(f"   Bob created: {bob_item.content}")
        return "Bob's transaction completed"

    result = bob_doc.transact(bob_transaction)
    print(f"   Transaction result: {result}")
    print(f"   Bob's document state: {bob_doc.store.get_state_vector()}")

    print("\n3. Demonstrating conflict resolution...")

    # Both clients create items that would conflict in a non-CRDT system
    # But with YDoc's CRDT algorithm, they can be merged

    def alice_second_transaction(txn):
        alice_id2 = create_id(alice_doc.client_id, 2)
        alice_item2 = Item(id=alice_id2, content=["This is Alice's second message."])
        alice_doc.store.add_struct(alice_item2)
        return "Alice's second transaction"

    def bob_second_transaction(txn):
        bob_id2 = create_id(bob_doc.client_id, 2)
        bob_item2 = Item(id=bob_id2, content=["This is Bob's second message."])
        bob_doc.store.add_struct(bob_item2)
        return "Bob's second transaction"

    # Execute both transactions
    alice_doc.transact(alice_second_transaction)
    bob_doc.transact(bob_second_transaction)

    print(f"   Alice's items: {len(alice_doc.store.clients[alice_doc.client_id])}")
    print(f"   Bob's items: {len(bob_doc.store.clients[bob_doc.client_id])}")

    print("\n4. Demonstrating deletion...")

    def deletion_transaction(txn):
        # Alice deletes one of her items
        target_id = create_id(alice_doc.client_id, 1)
        txn.delete_set.add(target_id)
        print(f"   Alice marked item {target_id} for deletion")
        return "Deletion completed"

    alice_doc.transact(deletion_transaction)

    # Check if the item was deleted
    deleted_item = alice_doc.store.get_item(create_id(alice_doc.client_id, 1))
    print(
        f"   Item deleted status: {deleted_item.deleted if deleted_item else 'Not found'}"
    )
    print(f"   Deletion set: {alice_doc.store.deleted_set}")

    print("\n5. Demonstrating nested transactions...")

    def outer_transaction(txn):
        print(f"   Outer transaction: {txn.origin}")

        def inner_transaction(txn2):
            print(f"   Inner transaction: {txn2.origin}")
            alice_id3 = create_id(alice_doc.client_id, 3)
            alice_item3 = Item(id=alice_id3, content=["Nested content"])
            alice_doc.store.add_struct(alice_item3)
            return "Inner done"

        result = alice_doc.transact(inner_transaction, origin="nested")
        print(f"   Inner result: {result}")
        return "Outer done"

    alice_doc.transact(outer_transaction, origin="outer")

    print("\n6. Final state summary...")
    print("   Alice's document:")
    print(
        f"     - Total items: {sum(len(items) for items in alice_doc.store.clients.values())}"
    )
    print(f"     - State vector: {alice_doc.store.get_state_vector()}")
    print(f"     - Deleted items: {len(alice_doc.store.deleted_set)}")
    print(f"     - Completed transactions: {len(alice_doc._transaction_cleanups)}")

    print("   Bob's document:")
    print(
        f"     - Total items: {sum(len(items) for items in bob_doc.store.clients.values())}"
    )
    print(f"     - State vector: {bob_doc.store.get_state_vector()}")
    print(f"     - Deleted items: {len(bob_doc.store.deleted_set)}")
    print(f"     - Completed transactions: {len(bob_doc._transaction_cleanups)}")

    print("\n✅ Full CRDT Demo completed!")
    print("This demonstrates:")
    print("  • Multi-client concurrent editing")
    print("  • Transaction-based operations")
    print("  • Conflict resolution through unique IDs")
    print("  • Deletion tracking")
    print("  • Nested transactions")
    print("  • State vector management")


if __name__ == "__main__":
    main()
