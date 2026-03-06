"""
Undo/Redo Demo for YDoc

This example demonstrates the undo/redo functionality that allows users
to revert and reapply changes made to collaborative documents.
"""

from ydoc import Doc, YText


def demo_basic_undo_redo():
    """Demonstrate basic undo/redo functionality."""
    print("=== Basic Undo/Redo Demo ===")

    # Create a document with undo manager
    doc = Doc()
    undo_manager = doc.add_undo_manager()

    # Get a text type
    text = doc.get("content", "text")

    print(f"Initial content: '{text}'")

    # Make some changes
    text.insert(0, "Hello")
    print(f"After 'Hello': '{text}'")

    text.insert(5, " World")
    print(f"After ' World': '{text}'")

    # Check undo/redo state
    print(f"Can undo: {doc.can_undo()}")
    print(f"Can redo: {doc.can_redo()}")

    # Undo last operation
    doc.undo()
    print(f"After undo: '{text}'")

    # Undo again
    doc.undo()
    print(f"After second undo: '{text}'")

    # Redo
    doc.redo()
    print(f"After redo: '{text}'")

    print()


def demo_undo_manager_features():
    """Demonstrate undo manager features."""
    print("=== UndoManager Features Demo ===")

    doc = Doc()

    # Customize undo manager
    undo_manager = doc.add_undo_manager(
        capture_timeout=1.0,  # Merge changes within 1 second
        tracked_origins={"user", None}  # Only track user actions and default
    )

    text = doc.get("content", "text")

    # Make changes with different origins
    text.insert(0, "User edit: ", origin="user")
    text.insert(11, "Hello", origin="user")

    # This won't be tracked (different origin)
    text.insert(16, " (system)", origin="system")

    print(f"Content: '{text}'")
    print(f"Undo stack size: {len(undo_manager.undo_stack)}")

    # Undo should only undo user actions
    doc.undo()
    print(f"After undo: '{text}'")

    # Clear undo history
    undo_manager.clear()
    print(f"After clear - can undo: {doc.can_undo()}")

    print()


def demo_practical_usage():
    """Demonstrate practical usage scenarios."""
    print("=== Practical Usage Demo ===")

    # Create a collaborative document
    doc = Doc()
    doc.add_undo_manager()  # Enable undo/redo

    text = doc.get("content", "text")

    # Simulate user typing
    words = ["The", " quick", " brown", " fox", " jumps"]
    for word in words:
        text.insert(len(text), word)

    print(f"Full sentence: '{text}'")

    # User decides to undo the last word
    doc.undo()
    print(f"After undo last word: '{text}'")

    # User changes mind and redoes
    doc.redo()
    print(f"After redo: '{text}'")

    # User undoes multiple times
    while doc.undo():
        print(f"Undo step: '{text}'")

    print(f"Final state: '{text}'")
    print(f"Can undo: {doc.can_undo()}")
    print(f"Can redo: {doc.can_redo()}")

    print()


def demo_advanced_features():
    """Demonstrate advanced undo manager features."""
    print("=== Advanced Features Demo ===")

    doc = Doc()
    undo_manager = doc.add_undo_manager(capture_timeout=0.5)

    text = doc.get("content", "text")

    # Rapid changes (should be merged into one undo step)
    text.insert(0, "A")
    text.insert(1, "B")
    text.insert(2, "C")

    print(f"After ABC: '{text}'")
    print(f"Undo stack size: {len(undo_manager.undo_stack)}")

    # Force separate undo step
    undo_manager.stop_capturing()
    text.insert(3, "D")

    print(f"After D: '{text}'")
    print(f"Undo stack size: {len(undo_manager.undo_stack)}")

    # First undo should only remove D
    doc.undo()
    print(f"After undo D: '{text}'")

    # Second undo should remove ABC
    doc.undo()
    print(f"After undo ABC: '{text}'")

    print()


if __name__ == "__main__":
    demo_basic_undo_redo()
    demo_undo_manager_features()
    demo_practical_usage()
    demo_advanced_features()

    print("🎉 Undo/Redo demo completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Basic undo/redo operations")
    print("✅ Origin-based tracking")
    print("✅ Multiple undo/redo steps")
    print("✅ Capture timeout for merging changes")
    print("✅ Manual capture control")
    print("✅ Undo stack management")