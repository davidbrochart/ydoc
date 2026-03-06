"""
CRDT Demo - Demonstrating the core conflict resolution functionality
"""

from ydoc import Doc, StructStore, Item, create_id

def main():
    print("=== YDoc CRDT Demo ===")
    
    # Create a struct store to demonstrate CRDT operations
    store = StructStore()
    
    print("1. Creating items from different clients...")
    
    # Simulate two clients creating content
    client1_id = 1
    client2_id = 2
    
    # Client 1 creates some items
    id1_1 = create_id(client1_id, 10)
    item1_1 = Item(id=id1_1, content=["Hello "])
    store.add_struct(item1_1)
    
    id1_2 = create_id(client1_id, 20)
    item1_2 = Item(id=id1_2, content=["World"])
    store.add_struct(item1_2)
    
    # Client 2 creates some items (interleaved clocks)
    id2_1 = create_id(client2_id, 5)
    item2_1 = Item(id=id2_1, content=[" from "])
    store.add_struct(item2_1)
    
    id2_2 = create_id(client2_id, 15)
    item2_2 = Item(id=id2_2, content=["CRDT"])
    store.add_struct(item2_2)
    
    print(f"   Client 1 items: {[(item.id.client, item.id.clock) for item in store.clients[client1_id]]}")
    print(f"   Client 2 items: {[(item.id.client, item.id.clock) for item in store.clients[client2_id]]}")
    
    print("\n2. Current state vector:")
    state_vector = store.get_state_vector()
    for client, clock in state_vector.items():
        print(f"   Client {client}: clock {clock}")
    
    print("\n3. Testing item retrieval...")
    retrieved = store.get_item(id1_2)
    print(f"   Retrieved item {id1_2}: {retrieved.content}")
    
    print("\n4. Testing deletion...")
    store.mark_deleted(id2_1)
    print(f"   Marked item {id2_1} as deleted")
    print(f"   Deleted set: {store.deleted_set}")
    print(f"   Item deleted flag: {item2_1.deleted}")
    
    print("\n5. Testing integrity...")
    integrity_ok = store.integrity_check()
    print(f"   Store integrity: {'OK' if integrity_ok else 'FAILED'}")
    
    print("\n6. Demonstrating document integration...")
    doc = Doc()
    print(f"   Created document with client ID: {doc.client_id}")
    print(f"   Document has StructStore: {doc.store is not None}")
    
    # Add an item to the document's store
    doc_id = create_id(doc.client_id, 100)
    doc_item = Item(id=doc_id, content=["Document content"])
    doc.store.add_struct(doc_item)
    
    print(f"   Added item to document store: {doc_item.content}")
    print(f"   Document state: {doc.store.get_state_vector()}")
    
    print("\n7. Simulating concurrent edits...")
    
    # Create two documents simulating different clients
    doc_a = Doc(guid="client_a")
    doc_b = Doc(guid="client_b")
    
    # Both clients create items at the same "position"
    item_a = Item(id=create_id(doc_a.client_id, 1), content=["Client A text"])
    item_b = Item(id=create_id(doc_b.client_id, 1), content=["Client B text"])
    
    doc_a.store.add_struct(item_a)
    doc_b.store.add_struct(item_b)
    
    print(f"   Client A created: {item_a.content}")
    print(f"   Client B created: {item_b.content}")
    print(f"   Client A state: {doc_a.store.get_state_vector()}")
    print(f"   Client B state: {doc_b.store.get_state_vector()}")
    
    print("\n✅ CRDT Demo completed successfully!")
    print("This demonstrates the foundation for conflict-free replicated data types.")

if __name__ == "__main__":
    main()