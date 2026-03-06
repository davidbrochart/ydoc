"""
Basic tests for YDoc core functionality
"""

import pytest
from ydoc import Doc, ID, create_id, compare_ids, YText


def test_id_creation():
    """Test ID creation and comparison."""
    id1 = create_id(1, 10)
    id2 = create_id(1, 10)
    id3 = create_id(2, 10)
    
    assert id1 == id2
    assert id1 != id3
    assert compare_ids(id1, id2) == True
    assert compare_ids(id1, id3) == False


def test_id_ordering():
    """Test ID ordering."""
    id1 = create_id(1, 5)
    id2 = create_id(1, 10)
    id3 = create_id(2, 1)
    
    assert id1 < id2
    assert id2 < id3  # Different clients, so client ID determines order


def test_doc_creation():
    """Test basic document creation."""
    doc = Doc()
    assert doc.client_id is not None
    assert doc.guid is not None
    assert doc.gc == True
    assert doc.is_destroyed == False


def test_doc_with_options():
    """Test document creation with options."""
    doc = Doc(
        guid="test-guid",
        collection_id="test-collection",
        gc=False,
        meta={"test": "value"}
    )
    
    assert doc.guid == "test-guid"
    assert doc.collection_id == "test-collection"
    assert doc.gc == False
    assert doc.meta == {"test": "value"}


def test_doc_get():
    """Test getting shared data types."""
    doc = Doc()
    
    # Get a new type
    text_type = doc.get("text", "text")
    assert "text" in doc.share
    assert isinstance(doc.share["text"], YText)
    
    # Get the same type again
    same_type = doc.get("text", "text")
    assert text_type == same_type


def test_doc_transact():
    """Test transaction execution."""
    doc = Doc()
    
    result = doc.transact(lambda d: "test_result")
    assert result == "test_result"


def test_doc_to_json():
    """Test document JSON serialization."""
    doc = Doc()
    doc.get("text", "text")
    doc.get("map", "map")
    
    json_data = doc.to_json()
    assert "text" in json_data
    assert "map" in json_data


def test_doc_destroy():
    """Test document destruction."""
    doc = Doc()
    doc.destroy()
    
    assert doc.is_destroyed == True


if __name__ == "__main__":
    pytest.main([__file__])