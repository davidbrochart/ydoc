"""
Tests for StructStore and CRDT components
"""

import pytest
from ydoc import StructStore, Item, GC, create_id


def test_struct_store_initialization():
    """Test StructStore initialization."""
    store = StructStore()
    assert store.clients == {}
    assert store.deleted_set == set()
    assert store.pending_structs is None
    assert store.pending_ds is None


def test_item_creation():
    """Test Item creation."""
    id1 = create_id(1, 10)
    item = Item(id=id1, content=["hello"])
    
    assert item.id == id1
    assert item.content == ["hello"]
    assert item.deleted == False
    assert item.left is None
    assert item.right is None


def test_add_struct():
    """Test adding structs to the store."""
    store = StructStore()
    
    # Add some items
    id1 = create_id(1, 10)
    id2 = create_id(1, 20)
    id3 = create_id(2, 5)
    
    item1 = Item(id=id1)
    item2 = Item(id=id2)
    item3 = Item(id=id3)
    
    store.add_struct(item1)
    store.add_struct(item2)
    store.add_struct(item3)
    
    # Check they were added correctly
    assert len(store.clients) == 2
    assert len(store.clients[1]) == 2
    assert len(store.clients[2]) == 1
    
    # Check ordering
    assert store.clients[1][0].id == id1
    assert store.clients[1][1].id == id2


def test_get_item():
    """Test getting items from the store."""
    store = StructStore()
    
    id1 = create_id(1, 10)
    item1 = Item(id=id1, content=["test"])
    store.add_struct(item1)
    
    # Get existing item
    retrieved = store.get_item(id1)
    assert retrieved is item1
    assert retrieved.content == ["test"]
    
    # Get non-existent item
    id2 = create_id(2, 5)
    assert store.get_item(id2) is None


def test_mark_deleted():
    """Test marking items as deleted."""
    store = StructStore()
    
    id1 = create_id(1, 10)
    item1 = Item(id=id1)
    store.add_struct(item1)
    
    # Mark as deleted
    store.mark_deleted(id1)
    
    assert id1 in store.deleted_set
    assert item1.deleted == True


def test_state_vector():
    """Test state vector generation."""
    store = StructStore()
    
    # Empty store
    assert store.get_state_vector() == {}
    
    # Add some items
    id1 = create_id(1, 10)
    id2 = create_id(1, 20)
    id3 = create_id(2, 5)
    
    item1 = Item(id=id1, length=5)
    item2 = Item(id=id2, length=3)
    item3 = Item(id=id3, length=10)
    
    store.add_struct(item1)
    store.add_struct(item2)
    store.add_struct(item3)
    
    state = store.get_state_vector()
    assert state[1] == 20 + 3  # id2.clock + item2.length
    assert state[2] == 5 + 10  # id3.clock + item3.length


def test_get_state():
    """Test getting state for specific client."""
    store = StructStore()
    
    # Non-existent client
    assert store.get_state(1) == 0
    
    # Add items
    id1 = create_id(1, 10)
    id2 = create_id(1, 20)
    
    item1 = Item(id=id1, length=5)
    item2 = Item(id=id2, length=3)
    
    store.add_struct(item1)
    store.add_struct(item2)
    
    assert store.get_state(1) == 20 + 3
    assert store.get_state(2) == 0


def test_integrity_check():
    """Test integrity checking."""
    store = StructStore()
    
    # Empty store should be valid
    assert store.integrity_check() == True
    
    # Add properly ordered items
    id1 = create_id(1, 10)
    id2 = create_id(1, 20)  # Should come after id1 with length 10
    
    item1 = Item(id=id1, length=10)
    item2 = Item(id=id2, length=5)
    
    store.add_struct(item1)
    store.add_struct(item2)
    
    assert store.integrity_check() == True
    
    # Add malformed item (gap)
    id3 = create_id(1, 25)  # Gap between 20+5=25 and 25
    item3 = Item(id=id3, length=1)
    store.add_struct(item3)
    
    # Should still be valid because we insert in order
    assert store.integrity_check() == True


def test_gc_creation():
    """Test GC marker creation."""
    id1 = create_id(1, 10)
    gc = GC(id=id1)
    
    assert gc.id == id1
    assert gc.length == 1


if __name__ == "__main__":
    pytest.main([__file__])