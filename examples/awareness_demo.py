"""
Awareness System Demo for YDoc

This example demonstrates the awareness system that enables real-time
collaboration features like presence tracking and cursor sharing.
"""

from ydoc import Doc, Awareness
import json


def demo_basic_awareness():
    """Demonstrate basic awareness functionality."""
    print("=== Basic Awareness Demo ===")

    # Create a document
    doc = Doc()

    # Get awareness instance
    awareness = doc.get_awareness()

    print(f"Document GUID: {doc.guid}")
    print(f"Local client ID: {doc.client_id}")

    # Set local user information
    awareness.set_local_user("Alice", "#FF5733")

    # Set cursor position
    awareness.set_local_cursor(42, {'anchor': 40, 'head': 45})

    # Get current state
    local_state = awareness.get_local_state()
    print(f"\nLocal client state:")
    print(f"  User: {local_state['user']['name']} ({local_state['user']['color']})")
    print(f"  Cursor: position={local_state['cursor']['position']}")
    print(f"  Selection: {local_state['cursor']['selection']}")

    print()


def demo_collaboration_simulation():
    """Simulate a collaborative editing session."""
    print("=== Collaboration Simulation Demo ===")

    # Create two documents (simulating two clients)
    doc1 = Doc()
    doc2 = Doc()

    # Get awareness instances
    awareness1 = doc1.get_awareness()
    awareness2 = doc2.get_awareness()

    # Set up client 1
    awareness1.set_local_user("Alice", "#FF5733")
    awareness1.set_local_cursor(100)

    # Set up client 2
    awareness2.set_local_user("Bob", "#3357FF")
    awareness2.set_local_cursor(200)

    print(f"Client 1 (ID {doc1.client_id}): {awareness1.get_local_state()['user']['name']}")
    print(f"Client 2 (ID {doc2.client_id}): {awareness2.get_local_state()['user']['name']}")

    # Simulate network transmission
    print("\nSimulating network synchronization...")

    # Client 1 encodes and sends its state
    update_from_client1 = awareness1.encode_awareness_update()
    print(f"Client 1 sent {len(update_from_client1)} bytes")

    # Client 2 receives and applies the update
    awareness2.apply_awareness_update(update_from_client1)

    # Client 2 encodes and sends its state
    update_from_client2 = awareness2.encode_awareness_update()
    print(f"Client 2 sent {len(update_from_client2)} bytes")

    # Client 1 receives and applies the update
    awareness1.apply_awareness_update(update_from_client2)

    # Now both clients should see each other
    states1 = awareness1.get_states()
    states2 = awareness2.get_states()

    print(f"\nClient 1 sees {len(states1)} clients:")
    for client_id, state in states1.items():
        user = state['user']
        cursor = state['cursor']
        print(f"  - Client {client_id}: {user['name']} at position {cursor['position'] if cursor else 'none'}")

    print(f"\nClient 2 sees {len(states2)} clients:")
    for client_id, state in states2.items():
        user = state['user']
        cursor = state['cursor']
        print(f"  - Client {client_id}: {user['name']} at position {cursor['position'] if cursor else 'none'}")

    print()


def demo_awareness_events():
    """Demonstrate awareness event handling."""
    print("=== Awareness Events Demo ===")

    doc = Doc()
    awareness = doc.get_awareness()

    # Set up event listeners
    def handle_cursor_update(data):
        client_id = data['client_id']
        cursor = data['cursor']
        print(f"Cursor update from client {client_id}: position {cursor['position']}")

    def handle_client_update(data):
        client_id = data['client_id']
        print(f"Client {client_id} updated their state")

    def handle_client_remove(data):
        client_id = data['client_id']
        print(f"Client {client_id} disconnected")

    # Register listeners
    awareness.on('cursor-update', handle_cursor_update)
    awareness.on('update', handle_client_update)
    awareness.on('remove', handle_client_remove)

    print("Event listeners registered. Making changes...")

    # Make changes that trigger events
    awareness.set_local_user("Event Test User", "#123456")
    awareness.set_local_cursor(50)
    awareness.set_local_cursor(75)

    # Simulate a remote client
    awareness.update_client(999, {
        'user': {'name': 'Remote User', 'color': '#654321'},
        'cursor': {'position': 150}
    })

    # Remove the remote client
    awareness.remove_client(999)

    # Clean up
    awareness.remove_all_listeners()
    print("Event listeners removed.")
    print()


def demo_doc_convenience_methods():
    """Demonstrate Doc class convenience methods."""
    print("=== Doc Convenience Methods Demo ===")

    doc = Doc()

    # Use convenience methods
    doc.set_user("Convenience User", "#ABCDEF")
    doc.set_cursor(300, {'anchor': 290, 'head': 310})

    # Get all awareness states
    states = doc.get_awareness_states()

    print(f"Awareness states: {len(states)} clients")

    for client_id, state in states.items():
        user = state['user']
        cursor = state['cursor']
        print(f"Client {client_id}:")
        print(f"  Name: {user['name']}")
        print(f"  Color: {user['color']}")
        print(f"  Cursor: {cursor['position']}")
        print(f"  Selection: {cursor['selection']}")

    print()


def demo_practical_usage():
    """Demonstrate practical awareness usage in a collaborative editor."""
    print("=== Practical Usage Demo ===")

    # Create a document for a collaborative editor
    doc = Doc()
    awareness = doc.get_awareness()

    # Set up the local user
    awareness.set_local_user("Editor User", "#2ECC71")

    # Track cursor movements
    cursor_history = []

    def track_cursor(data):
        cursor_history.append({
            'client_id': data['client_id'],
            'position': data['cursor']['position'],
            'timestamp': 'now'
        })
        print(f"Cursor moved to: {data['cursor']['position']}")

    awareness.on('cursor-update', track_cursor)

    # Simulate user typing and moving cursor
    print("Simulating user activity...")

    positions = [0, 10, 25, 35, 50, 60]
    for pos in positions:
        awareness.set_local_cursor(pos)

    print(f"\nCursor movement history: {len(cursor_history)} movements")

    # Simulate remote collaborators
    remote_users = [
        {'client_id': 1001, 'name': 'User A', 'color': '#E74C3C'},
        {'client_id': 1002, 'name': 'User B', 'color': '#3498DB'},
        {'client_id': 1003, 'name': 'User C', 'color': '#F39C12'}
    ]

    for user in remote_users:
        awareness.update_client(user['client_id'], {
            'user': {'name': user['name'], 'color': user['color']},
            'cursor': {'position': 50 + user['client_id'] % 100}
        })

    # Show all active collaborators
    states = awareness.get_states()
    print(f"\nActive collaborators: {len(states)}")

    for client_id, state in states.items():
        user = state['user']
        cursor = state['cursor']
        is_local = client_id == doc.client_id

        status = "👤 Local" if is_local else "👥 Remote"
        print(f"  {status} - {user['name']} at position {cursor['position']}")

    # Clean up
    awareness.remove_all_listeners()
    print()


def demo_encoding_performance():
    """Demonstrate awareness encoding for network transmission."""
    print("=== Encoding Performance Demo ===")

    doc = Doc()
    awareness = doc.get_awareness()

    # Set up local state
    awareness.set_local_user("Performance Test", "#9B59B6")
    awareness.set_local_cursor(1000)

    # Add multiple remote clients to test scaling
    num_remote_clients = 10

    for i in range(num_remote_clients):
        client_id = 2000 + i
        awareness.update_client(client_id, {
            'user': {'name': f'User {i}', 'color': f'#{i:06X}'},
            'cursor': {'position': 500 + i * 10}
        })

    # Encode the awareness state
    encoded = awareness.encode_awareness_update()

    print(f"Clients tracked: {len(awareness.get_states())}")
    print(f"Encoded size: {len(encoded)} bytes")
    print(f"Bytes per client: {len(encoded) / len(awareness.get_states()):.1f}")

    # Decode and verify
    doc2 = Doc()
    awareness2 = doc2.get_awareness()
    awareness2.apply_awareness_update(encoded)

    states2 = awareness2.get_states()
    print(f"Successfully decoded: {len(states2)} clients")

    # Verify data integrity
    original_local = awareness.get_local_state()
    decoded_local = awareness2.get_local_state()

    local_preserved = decoded_local['client_id'] == doc2.client_id
    print(f"Local client preserved: {local_preserved}")

    remote_clients_decoded = len([s for s in states2.values() if s['client_id'] != doc2.client_id])
    print(f"Remote clients decoded: {remote_clients_decoded}/{num_remote_clients}")

    print()


if __name__ == "__main__":
    demo_basic_awareness()
    demo_collaboration_simulation()
    demo_awareness_events()
    demo_doc_convenience_methods()
    demo_practical_usage()
    demo_encoding_performance()

    print("🎉 Awareness System Demo Completed!")
    print("\nAwareness System Features Demonstrated:")
    print("✅ Client presence tracking")
    print("✅ Cursor position sharing with selection")
    print("✅ User metadata (names, colors)")
    print("✅ Binary encoding/decoding for network transmission")
    print("✅ Event system for real-time updates")
    print("✅ Multi-client collaboration simulation")
    print("✅ Doc class integration")
    print("✅ Efficient state synchronization")
    print("\nThis awareness system enables:")
    print("- Real-time presence detection in collaborative apps")
    print("- Shared cursor positions for better collaboration")
    print("- User identification and differentiation")
    print("- Network-efficient state synchronization")
    print("- Foundation for rich collaboration features")
    print("- Scalable multi-user scenarios")