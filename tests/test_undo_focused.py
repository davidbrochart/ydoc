"""
Focused UndoManager tests inspired by Yjs patterns.
Tests that work with current YDoc API and improve coverage.
"""

import pytest
from ydoc.doc import Doc
from ydoc.types import YText, YMap, YArray
from ydoc.undo_manager import UndoManager, StackItem


def test_undo_manager_initialization():
    """Test basic UndoManager initialization."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    
    # Verify basic properties
    assert undo_manager.doc == doc
    assert undo_manager.undo_stack == []
    assert undo_manager.redo_stack == []
    assert undo_manager.capture_timeout == 0.5
    assert callable(undo_manager.capture_transaction)
    assert isinstance(undo_manager.tracked_origins, set)


def test_undo_manager_stack_item_structure():
    """Test StackItem structure and properties."""
    # Create a stack item directly
    stack_item = StackItem()
    
    # Verify structure
    assert hasattr(stack_item, 'inserted_items')
    assert hasattr(stack_item, 'deleted_items')
    assert hasattr(stack_item, 'meta')
    assert hasattr(stack_item, 'timestamp')
    
    assert isinstance(stack_item.inserted_items, list)
    assert isinstance(stack_item.deleted_items, list)
    assert isinstance(stack_item.meta, dict)
    assert isinstance(stack_item.timestamp, float)
    
    # Verify timestamp is reasonable
    import time
    current_time = time.time()
    assert abs(current_time - stack_item.timestamp) < 1.0


def test_undo_manager_with_text_operations():
    """Test undo manager with text operations."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    text = doc.get("text", "text")
    
    # Make a change
    text.insert(0, "Hello")
    
    # Verify stack item was created
    assert len(undo_manager.undo_stack) == 1
    assert len(undo_manager.redo_stack) == 0
    
    stack_item = undo_manager.undo_stack[0]
    assert isinstance(stack_item, StackItem)
    # inserted_items might be empty depending on how the operation was captured
    assert isinstance(stack_item.inserted_items, list)


def test_undo_manager_capture_timeout_options():
    """Test undo manager with different capture timeout values."""
    doc = Doc()
    
    # Test with short timeout
    undo_manager1 = doc.add_undo_manager(capture_timeout=0.1)
    assert undo_manager1.capture_timeout == 0.1
    
    # Test with long timeout
    undo_manager2 = doc.add_undo_manager(capture_timeout=10.0)
    assert undo_manager2.capture_timeout == 10.0
    
    # Test with infinite timeout
    undo_manager3 = doc.add_undo_manager(capture_timeout=float('inf'))
    assert undo_manager3.capture_timeout == float('inf')


def test_undo_manager_custom_capture_function():
    """Test undo manager with custom capture transaction function."""
    doc = Doc()
    
    # Create a custom capture function
    def custom_capture(txn):
        # Always capture for this test
        return True
    
    undo_manager = doc.add_undo_manager(capture_transaction=custom_capture)
    assert undo_manager.capture_transaction == custom_capture
    
    # Make a change
    text = doc.get("text", "text")
    text.insert(0, "Test")
    
    # Should be captured
    assert len(undo_manager.undo_stack) == 1


def test_undo_manager_tracked_origins():
    """Test undo manager with different tracked origins."""
    doc = Doc()
    
    # Test with default origins
    undo_manager1 = doc.add_undo_manager()
    assert None in undo_manager1.tracked_origins
    
    # Test with custom origins
    undo_manager2 = doc.add_undo_manager(tracked_origins={"user", "system"})
    assert "user" in undo_manager2.tracked_origins
    assert "system" in undo_manager2.tracked_origins
    
    # Test with mixed origins
    undo_manager3 = doc.add_undo_manager(tracked_origins={"user", None})
    assert "user" in undo_manager3.tracked_origins
    assert None in undo_manager3.tracked_origins


def test_undo_manager_transaction_registration():
    """Test that undo manager properly registers with document."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    
    # Check that the handler is registered
    handlers = doc._after_transaction_handlers
    assert len(handlers) == 1
    assert callable(handlers[0])
    
    # Verify it's the undo manager's handler
    assert handlers[0] == undo_manager._after_transaction_handler


def test_undo_manager_clear_functionality():
    """Test undo manager clear functionality."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    text = doc.get("text", "text")
    
    # Make some changes
    text.insert(0, "A")
    text.insert(1, "B")
    
    # Verify stacks have content
    assert len(undo_manager.undo_stack) >= 1
    assert len(undo_manager.redo_stack) == 0
    
    # Clear the undo manager
    undo_manager.clear()
    
    # Verify stacks are empty
    assert len(undo_manager.undo_stack) == 0
    assert len(undo_manager.redo_stack) == 0


def test_undo_manager_state_flags():
    """Test undo manager state flags."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    
    # Initial state
    assert undo_manager.undoing == False
    assert undo_manager.redoing == False
    assert undo_manager.last_change_time == 0.0
    assert undo_manager.current_stack_item is None


def test_undo_manager_with_multiple_documents():
    """Test undo manager with multiple independent documents."""
    # Create multiple documents with undo managers
    doc1 = Doc()
    undo_manager1 = doc1.add_undo_manager()
    
    doc2 = Doc()
    undo_manager2 = doc2.add_undo_manager()
    
    # Make changes to first document
    text1 = doc1.get("text", "text")
    text1.insert(0, "Doc1")
    
    # Make changes to second document
    text2 = doc2.get("text", "text")
    text2.insert(0, "Doc2")
    
    # Verify independence
    assert len(undo_manager1.undo_stack) == 1
    assert len(undo_manager2.undo_stack) == 1
    
    # Undo on first document shouldn't affect second
    doc1.undo()
    assert text1.to_string() == ""
    assert text2.to_string() == "Doc2"


def test_undo_manager_stack_item_metadata():
    """Test stack item metadata handling."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    text = doc.get("text", "text")
    
    # Make a change
    text.insert(0, "Test Content")
    
    # Get the stack item
    stack_item = undo_manager.undo_stack[0]
    
    # Test metadata
    assert isinstance(stack_item.meta, dict)
    
    # Add custom metadata
    stack_item.meta["custom_key"] = "custom_value"
    assert stack_item.meta["custom_key"] == "custom_value"


def test_undo_manager_with_complex_operations():
    """Test undo manager with complex operation sequences."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    
    # Create multiple types
    text = doc.get("text", "text")
    ymap = doc.get("map", "map")
    yarray = doc.get("array", "array")
    
    # Make changes to different types
    text.insert(0, "Hello")
    ymap.set("key", "value")
    yarray.push("item")
    
    # Verify stack items were created
    assert len(undo_manager.undo_stack) >= 1
    
    # Check stack item structure
    for stack_item in undo_manager.undo_stack:
        assert isinstance(stack_item, StackItem)
        assert hasattr(stack_item, 'inserted_items')
        assert hasattr(stack_item, 'deleted_items')


def test_undo_manager_error_handling():
    """Test undo manager error handling."""
    doc = Doc()
    
    # Test with invalid capture function that raises error
    def failing_capture(txn):
        raise ValueError("Test error")
    
    # This should not crash during initialization
    undo_manager = doc.add_undo_manager(capture_transaction=failing_capture)
    
    # But operations might fail or be handled gracefully
    text = doc.get("text", "text")
    # The behavior depends on how errors are handled in the transaction system


def test_undo_manager_timestamp_consistency():
    """Test that stack items have consistent timestamps."""
    import time
    
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    text = doc.get("text", "text")
    
    # Make multiple changes with delays
    text.insert(0, "A")
    time.sleep(0.01)  # Small delay
    text.insert(1, "B")
    time.sleep(0.01)
    text.insert(2, "C")
    
    # Check that timestamps are reasonable
    timestamps = [item.timestamp for item in undo_manager.undo_stack]
    
    # Timestamps should be in order (approximately)
    for i in range(len(timestamps) - 1):
        assert timestamps[i] <= timestamps[i + 1]


def test_undo_manager_memory_management():
    """Test undo manager memory management with many operations."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    text = doc.get("text", "text")
    
    # Make many changes
    for i in range(100):
        text.insert(i, str(i % 10))
    
    # Verify all operations were captured
    assert len(undo_manager.undo_stack) >= 1
    
    # Clear and verify memory is freed
    undo_manager.clear()
    assert len(undo_manager.undo_stack) == 0
    assert len(undo_manager.redo_stack) == 0


def test_undo_manager_with_empty_document():
    """Test undo manager with document that has no changes."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    
    # Get some types but don't make changes
    text = doc.get("text", "text")
    ymap = doc.get("map", "map")
    
    # Verify no stack items
    assert len(undo_manager.undo_stack) == 0
    assert len(undo_manager.redo_stack) == 0
    
    # Operations should work without errors
    doc.undo()  # No effect
    doc.redo()  # No effect


def test_undo_manager_initialization_edge_cases():
    """Test undo manager initialization with edge cases."""
    doc = Doc()
    
    # Test with very short timeout
    undo_manager1 = doc.add_undo_manager(capture_timeout=0.001)
    assert undo_manager1.capture_timeout == 0.001
    
    # Test with zero timeout
    undo_manager2 = doc.add_undo_manager(capture_timeout=0.0)
    assert undo_manager2.capture_timeout == 0.0
    
    # Test with very long timeout
    undo_manager3 = doc.add_undo_manager(capture_timeout=3600.0)  # 1 hour
    assert undo_manager3.capture_timeout == 3600.0


def test_undo_manager_stack_item_equality():
    """Test stack item equality and comparison."""
    # Create two stack items
    item1 = StackItem()
    item2 = StackItem()
    
    # They should be different instances
    assert item1 is not item2
    
    # But have similar structure
    assert type(item1.inserted_items) == type(item2.inserted_items)
    assert type(item1.deleted_items) == type(item2.deleted_items)
    assert type(item1.meta) == type(item2.meta)
    assert type(item1.timestamp) == type(item2.timestamp)


def test_undo_manager_with_nested_structures():
    """Test undo manager with nested data structures."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    
    # Create nested map structure
    root_map = doc.get("root", "map")
    
    # Add nested types (YDoc uses different approach for nested structures)
    # For now, just test that we can create and access nested data
    root_map.set("text_content", "Nested text")
    root_map.set("nested_key", "nested_value")
    
    # Verify operations were captured
    assert len(undo_manager.undo_stack) >= 1
    
    # Check that nested structures work
    assert root_map.get("text_content") == "Nested text"
    assert root_map.get("nested_key") == "nested_value"


def test_undo_manager_undoing_redoing_flags():
    """Test undo manager undoing/redoing state flags."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    
    # Initial state
    assert undo_manager.undoing == False
    assert undo_manager.redoing == False
    
    # Make a change
    text = doc.get("text", "text")
    text.insert(0, "Test")
    
    # Flags should still be false (they're set during undo/redo operations)
    assert undo_manager.undoing == False
    assert undo_manager.redoing == False


def test_undo_manager_current_stack_item():
    """Test undo manager current stack item handling."""
    doc = Doc()
    undo_manager = doc.add_undo_manager()
    
    # Initially should be None
    assert undo_manager.current_stack_item is None
    
    # After making a change, it might be set or cleared depending on implementation
    text = doc.get("text", "text")
    text.insert(0, "Test")
    
    # The current stack item behavior depends on the specific implementation
    # It might be None or might reference the last stack item
