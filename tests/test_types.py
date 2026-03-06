"""
Tests for Yjs data types
"""

import pytest
from ydoc import Doc, YText, YMap, YArray, YXml, YType, create_y_type


def test_ytext_creation():
    """Test YText creation and basic functionality."""
    doc = Doc()
    text = YText("test_text", "Hello World")
    text._integrate(doc, None)
    
    assert str(text) == "Hello World"
    assert len(text) == 11
    assert text.to_json() == "Hello World"


def test_ytext_insert():
    """Test YText insert operations."""
    doc = Doc()
    text = YText("test_text", "Hello")
    text._integrate(doc, None)
    
    # Insert at beginning
    text.insert(0, "Start:")
    assert str(text) == "Start:Hello"
    
    # Insert in middle
    text.insert(6, " MIDDLE")
    assert str(text) == "Start: MIDDLEHello"
    
    # Insert at end
    text.insert(len(text), " END")
    assert str(text) == "Start: MIDDLEHello END"


def test_ytext_delete():
    """Test YText delete operations."""
    doc = Doc()
    text = YText("test_text", "Hello World")
    text._integrate(doc, None)
    
    # Delete from middle
    text.delete(5, 1)  # Delete space
    assert str(text) == "HelloWorld"
    
    # Delete from beginning
    text.delete(0, 5)  # Delete "Hello"
    assert str(text) == "World"
    
    # Delete from end
    text.delete(2, 3)  # Delete "rld"
    assert str(text) == "Wo"


def test_ymap_creation():
    """Test YMap creation and basic functionality."""
    doc = Doc()
    map_type = YMap("test_map")
    map_type._integrate(doc, None)
    
    assert map_type.to_json() == {}
    assert map_type.get("nonexistent") is None


def test_ymap_set_get():
    """Test YMap set and get operations."""
    doc = Doc()
    map_type = YMap("test_map")
    map_type._integrate(doc, None)
    
    # Set values
    map_type.set("name", "Alice")
    map_type.set("age", 30)
    map_type.set("active", True)
    
    # Get values
    assert map_type.get("name") == "Alice"
    assert map_type.get("age") == 30
    assert map_type.get("active") is True
    assert map_type.get("nonexistent") is None
    
    # Test JSON conversion
    json_data = map_type.to_json()
    assert json_data["name"] == "Alice"
    assert json_data["age"] == 30


def test_ymap_delete():
    """Test YMap delete operations."""
    doc = Doc()
    map_type = YMap("test_map")
    map_type._integrate(doc, None)
    
    # Add some data
    map_type.set("key1", "value1")
    map_type.set("key2", "value2")
    map_type.set("key3", "value3")
    
    # Delete a key
    map_type.delete("key2")
    
    assert map_type.get("key2") is None
    assert map_type.get("key1") == "value1"
    assert map_type.get("key3") == "value3"


def test_ymap_methods():
    """Test YMap convenience methods."""
    doc = Doc()
    map_type = YMap("test_map")
    map_type._integrate(doc, None)
    
    # Add some data
    map_type.set("a", 1)
    map_type.set("b", 2)
    map_type.set("c", 3)
    
    # Test keys, values, items
    keys = map_type.keys()
    values = map_type.values()
    items = map_type.items()
    
    assert len(keys) == 3
    assert len(values) == 3
    assert len(items) == 3
    assert "a" in keys
    assert 1 in values
    assert ("b", 2) in items


def test_yarray_creation():
    """Test YArray creation and basic functionality."""
    doc = Doc()
    array = YArray("test_array", [1, 2, 3])
    array._integrate(doc, None)
    
    assert len(array) == 3
    assert array[0] == 1
    assert array[1] == 2
    assert array[2] == 3
    assert array.to_json() == [1, 2, 3]


def test_yarray_insert():
    """Test YArray insert operations."""
    doc = Doc()
    array = YArray("test_array", [1, 3])
    array._integrate(doc, None)
    
    # Insert in middle
    array.insert(1, [2])
    assert array.to_json() == [1, 2, 3]
    
    # Insert at beginning
    array.insert(0, [0])
    assert array.to_json() == [0, 1, 2, 3]
    
    # Insert at end
    array.insert(len(array), [4])
    assert array.to_json() == [0, 1, 2, 3, 4]


def test_yarray_push():
    """Test YArray push operations."""
    doc = Doc()
    array = YArray("test_array", [1, 2])
    array._integrate(doc, None)
    
    array.push([3, 4])
    assert array.to_json() == [1, 2, 3, 4]


def test_yarray_delete():
    """Test YArray delete operations."""
    doc = Doc()
    array = YArray("test_array", [1, 2, 3, 4, 5])
    array._integrate(doc, None)
    
    # Delete from middle
    array.delete(2, 1)
    assert array.to_json() == [1, 2, 4, 5]
    
    # Delete multiple
    array.delete(0, 2)
    assert array.to_json() == [4, 5]


def test_yarray_setitem():
    """Test YArray setitem operations."""
    doc = Doc()
    array = YArray("test_array", [1, 2, 3])
    array._integrate(doc, None)
    
    array[1] = 99
    assert array.to_json() == [1, 99, 3]


def test_yxml_creation():
    """Test YXml creation and basic functionality."""
    doc = Doc()
    xml = YXml("test_xml", "div")
    xml._integrate(doc, None)
    
    assert xml.tag_name == "div"
    assert xml.attributes == {}
    assert xml.children == []


def test_yxml_attributes():
    """Test YXml attribute operations."""
    doc = Doc()
    xml = YXml("test_xml", "span")
    xml._integrate(doc, None)
    
    xml.set_attribute("class", "highlight")
    xml.set_attribute("id", "main")
    
    assert xml.attributes["class"] == "highlight"
    assert xml.attributes["id"] == "main"


def test_yxml_children():
    """Test YXml child operations."""
    doc = Doc()
    xml = YXml("test_xml", "div")
    xml._integrate(doc, None)
    
    xml.insert_child(0, "Text content")
    child_xml = YXml("child", "span")
    child_xml._integrate(doc, None)
    xml.insert_child(1, child_xml)
    
    assert len(xml.children) == 2
    assert xml.children[0] == "Text content"
    assert isinstance(xml.children[1], YXml)


def test_yxml_to_json():
    """Test YXml JSON conversion."""
    doc = Doc()
    xml = YXml("test_xml", "div")
    xml._integrate(doc, None)
    
    xml.set_attribute("class", "container")
    xml.insert_child(0, "Hello")
    
    json_data = xml.to_json()
    assert json_data["tag"] == "div"
    assert json_data["attributes"]["class"] == "container"
    assert json_data["children"] == ["Hello"]


def test_create_y_type():
    """Test the create_y_type utility function."""
    # Test creating different types
    text = create_y_type("text", "test_text")
    assert isinstance(text, YText)
    
    map_type = create_y_type("map", "test_map")
    assert isinstance(map_type, YMap)
    
    array = create_y_type("array", "test_array")
    assert isinstance(array, YArray)
    
    xml = create_y_type("xml", "test_xml")
    assert isinstance(xml, YXml)
    
    # Test default (unknown type falls back to YType)
    unknown = create_y_type("unknown", "test_unknown")
    assert isinstance(unknown, YType)


def test_doc_get_creates_correct_types():
    """Test that Doc.get() creates the correct YType instances."""
    doc = Doc()
    
    # Get different types
    text = doc.get("text_type", "text")
    assert isinstance(text, YText)
    
    map_type = doc.get("map_type", "map")
    assert isinstance(map_type, YMap)
    
    array = doc.get("array_type", "array")
    assert isinstance(array, YArray)
    
    xml = doc.get("xml_type", "xml")
    assert isinstance(xml, YXml)
    
    # Default should be YText
    default = doc.get("default_type")
    assert isinstance(default, YText)


def test_ytext_with_doc_integration():
    """Test YText fully integrated with document transactions."""
    doc = Doc()
    text = doc.get("content", "text")
    
    # Should be a YText instance
    assert isinstance(text, YText)
    assert str(text) == ""
    
    # Insert some text
    text.insert(0, "Hello")
    text.insert(5, " World")
    
    assert str(text) == "Hello World"
    assert len(text) == 11


def test_ymap_with_doc_integration():
    """Test YMap fully integrated with document transactions."""
    doc = Doc()
    map_type = doc.get("data", "map")
    
    # Should be a YMap instance
    assert isinstance(map_type, YMap)
    
    # Set some values
    map_type.set("name", "Test")
    map_type.set("value", 123)
    
    assert map_type.get("name") == "Test"
    assert map_type.get("value") == 123


if __name__ == "__main__":
    pytest.main([__file__])