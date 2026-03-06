"""
Event System Demo for YDoc

This example demonstrates the event system that allows applications
to react to changes in collaborative documents.
"""

from ydoc import Doc, YText, YMap, YEvent


def demo_basic_events():
    """Demonstrate basic event listening."""
    print("=== Basic Event Demo ===")
    
    # Create a document
    doc = Doc()
    
    # Get a text type
    text = doc.get("content", "text")
    
    # Set up event listeners
    def handle_text_change(event: YEvent) -> None:
        print(f"Text changed! New content: '{event.target}'")
        print(f"  Child list changed: {event.child_list_changed}")
        print(f"  Keys changed: {event.keys_changed}")
    
    def handle_doc_change(event: YEvent) -> None:
        print(f"Document change detected on: {event.target}")
    
    # Register listeners
    text.on('change', handle_text_change)
    doc.on('change', handle_doc_change)
    
    # Make some changes
    print("Making changes...")
    text.insert(0, "Hello")
    text.insert(5, " World")
    
    # Clean up
    text.off('change', handle_text_change)
    doc.off('change', handle_doc_change)
    print()


def demo_ymap_events():
    """Demonstrate YMap event listening."""
    print("=== YMap Event Demo ===")
    
    doc = Doc()
    map_type = doc.get("data", "map")
    
    def handle_map_change(event: YEvent) -> None:
        print(f"Map changed! Keys: {event.keys_changed}")
        if 'name' in event.keys_changed:
            print(f"  Name is now: {map_type.get('name')}")
    
    map_type.on('change', handle_map_change)
    
    # Make changes
    map_type.set("name", "Alice")
    map_type.set("age", 30)
    map_type.delete("name")
    
    map_type.off('change', handle_map_change)
    print()


def demo_transaction_events():
    """Demonstrate transaction-level events."""
    print("=== Transaction Event Demo ===")
    
    doc = Doc()
    text = doc.get("content", "text")
    
    def handle_after_transaction(transaction, doc) -> None:
        print(f"Transaction completed. Origin: {transaction.origin}")
        print(f"  Delete set size: {len(transaction.delete_set)}")
        print(f"  Changed types: {len(transaction.changed)}")
    
    doc.on('afterTransaction', handle_after_transaction)
    
    # Make changes with different origins
    text.insert(0, "User edit", origin="user")
    text.insert(10, " System edit", origin="system")
    text.insert(21, " Default origin")
    
    doc.off('afterTransaction', handle_after_transaction)
    print()


def demo_event_patterns():
    """Demonstrate advanced event patterns."""
    print("=== Advanced Event Patterns Demo ===")
    
    doc = Doc()
    text = doc.get("content", "text")
    
    # One-time event listener
    def handle_once(event: YEvent) -> None:
        print("One-time event triggered!")
    
    text.once('change', handle_once)
    
    # This will trigger the one-time listener
    text.insert(0, "First change")
    
    # This won't trigger it again
    text.insert(12, " Second change")
    
    # Check listener management
    print(f"Text has change listeners: {text.has_listeners('change')}")
    
    # Add multiple listeners
    def listener1(event: YEvent): print("Listener 1")
    def listener2(event: YEvent): print("Listener 2")
    
    text.on('change', listener1)
    text.on('change', listener2)
    
    text.insert(20, " Third")  # Should trigger both
    
    # Remove specific listener
    text.off('change', listener1)
    text.insert(27, " Fourth")  # Should only trigger listener2
    
    # Remove all listeners
    text.remove_all_listeners('change')
    text.insert(35, " Fifth")   # Should not trigger any
    
    print()


def demo_practical_usage():
    """Demonstrate practical event system usage."""
    print("=== Practical Usage Demo ===")
    
    # Create a collaborative document
    doc = Doc()
    text = doc.get("content", "text")
    
    # Simulate a real-time collaboration scenario
    print("Simulating collaborative editing...")
    
    # Track all changes for audit trail
    change_history = []
    
    def log_change(event: YEvent) -> None:
        change_history.append({
            'timestamp': 'now',
            'content': event.target.to_string(),
            'type': type(event.target).__name__,
            'child_list_changed': event.child_list_changed
        })
        print(f"Logged change: '{event.target.to_string()}'")
    
    text.on('change', log_change)
    
    # Simulate user typing
    sentences = ["The quick brown fox", " jumps over the", " lazy dog."]
    for sentence in sentences:
        text.insert(len(text), sentence)
    
    print(f"\nTotal changes logged: {len(change_history)}")
    print(f"Final content: '{text}'")
    
    # Clean up
    text.off('change', log_change)
    print()


def demo_delta_computation():
    """Demonstrate delta computation from events."""
    print("=== Delta Computation Demo ===")
    
    doc = Doc()
    text = doc.get("content", "text")
    
    def handle_change_with_delta(event: YEvent) -> None:
        delta = event.delta
        print(f"Change detected:")
        print(f"  Content: '{delta.get('content', '')}'")
        print(f"  Child list changed: {delta.get('child_list_changed', False)}")
        print(f"  Keys changed: {delta.get('keys_changed', [])}")
    
    text.on('change', handle_change_with_delta)
    
    # Make a change
    text.insert(0, "Delta test")
    
    text.off('change', handle_change_with_delta)
    print()


if __name__ == "__main__":
    demo_basic_events()
    demo_ymap_events()
    demo_transaction_events()
    demo_event_patterns()
    demo_practical_usage()
    demo_delta_computation()
    
    print("🎉 Event System Demo Completed!")
    print("\nEvent System Features Demonstrated:")
    print("✅ Observable pattern with on/off/emit methods")
    print("✅ YEvent class with detailed change information")
    print("✅ Event emission on YText and YMap changes")
    print("✅ Transaction-level events (afterTransaction)")
    print("✅ Advanced patterns (once, has_listeners, remove_all_listeners)")
    print("✅ Delta computation for change tracking")
    print("✅ Practical collaboration scenarios")
    print("\nThis event system enables:")
    print("- Real-time collaboration features")
    print("- Change tracking and auditing")
    print("- Reactive UI updates")
    print("- Conflict resolution")
    print("- Undo/redo functionality")
    print("- Presence detection")