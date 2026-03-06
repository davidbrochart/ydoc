"""
Yjs-like API Demo for YDoc

This example demonstrates the new Yjs-like convenience methods that make
YDoc's API more familiar to Yjs developers.
"""

from ydoc import Doc


def demo_yjs_like_api():
    """Demonstrate Yjs-like API methods."""
    print("=== Yjs-like API Demo ===")

    # Create a document
    doc = Doc()
    print("Created YDoc document")

    # Use Yjs-like methods (instead of doc.get("name", "type"))
    content = doc.get_text("content")
    data = doc.get_map("data")
    items = doc.get_array("items")
    element = doc.get_xml("element")

    print("✅ Created all YType instances using Yjs-like API:")
    print(f"  - content: {type(content).__name__}")
    print(f"  - data: {type(data).__name__}")
    print(f"  - items: {type(items).__name__}")
    print(f"  - element: {type(element).__name__}")

    # Verify they're the same as using the original API
    assert content == doc.get("content", "text")
    assert data == doc.get("data", "map")
    assert items == doc.get("items", "array")
    assert element == doc.get("element", "xml")

    print("✅ All methods return the same instances as doc.get()")
    print()


def demo_api_comparison():
    """Compare old and new API styles."""
    print("=== API Comparison Demo ===")

    doc = Doc()

    # Old way (still works)
    text_old = doc.get("message", "text")
    map_old = doc.get("settings", "map")

    # New Yjs-like way
    text_new = doc.get_text("message")
    map_new = doc.get_map("settings")

    print("Old API style:")
    print("  text = doc.get('message', 'text')")
    print("  map  = doc.get('settings', 'map')")

    print("\nNew Yjs-like style:")
    print("  text = doc.get_text('message')")
    print("  map  = doc.get_map('settings')")

    # They should be identical
    assert text_old is text_new
    assert map_old is map_new

    print("\n✅ Both APIs return the exact same instances")
    print("✅ New API is more concise and Yjs-like")
    print()


def demo_real_world_usage():
    """Demonstrate real-world usage patterns."""
    print("=== Real-World Usage Demo ===")

    # Create a document for a collaborative editor
    doc = Doc()

    # Set up the document structure (like Yjs)
    content = doc.get_text("content")  # Main text content
    users = doc.get_map("users")     # User presence/metadata
    comments = doc.get_array("comments")  # Comments array

    print("Collaborative editor document structure:")
    print(f"  - content: {type(content).__name__} (main text)")
    print(f"  - users: {type(users).__name__} (user data)")
    print(f"  - comments: {type(comments).__name__} (comment list)")

    # This matches Yjs usage patterns exactly:
    # const content = doc.getText('content')
    # const users = doc.getMap('users')
    # const comments = doc.getArray('comments')

    print("\n✅ API matches Yjs exactly - easy migration!")
    print()


def demo_all_types():
    """Demonstrate all Yjs-like methods."""
    print("=== All Yjs-like Methods Demo ===")

    doc = Doc()

    # Test all convenience methods
    methods = [
        ("get_text", doc.get_text("text")),
        ("get_map", doc.get_map("map")),
        ("get_array", doc.get_array("array")),
        ("get_xml", doc.get_xml("xml"))
    ]

    print("Available Yjs-like methods:")
    for method_name, instance in methods:
        print(f"  - doc.{method_name}() → {type(instance).__name__}")

    # Test with custom names
    custom_text = doc.get_text("custom_text")
    custom_map = doc.get_map("custom_map")

    assert custom_text == doc.get("custom_text", "text")
    assert custom_map == doc.get("custom_map", "map")

    print("\n✅ All methods support custom names")
    print("✅ Default names: text, map, array, xml")
    print()


def demo_migration_from_yjs():
    """Show how Yjs code would migrate to YDoc."""
    print("=== Yjs Migration Demo ===")

    print("Yjs code:")
    print("```javascript")
    print("const doc = new Y.Doc()")
    print("const text = doc.getText('content')")
    print("const map = doc.getMap('data')")
    print("const array = doc.getArray('items')")
    print("```")

    print("\nYDoc equivalent:")
    print("```python")
    print("from ydoc import Doc")
    print("doc = Doc()")
    print("text = doc.get_text('content')")
    print("map = doc.get_map('data')")
    print("array = doc.get_array('items')")
    print("```")

    # Verify it actually works
    doc = Doc()
    text = doc.get_text('content')
    map_ = doc.get_map('data')
    array = doc.get_array('items')

    print("\n✅ Migration is straightforward!")
    print("✅ Only difference: snake_case vs camelCase")
    print()


def main():
    """Run all Yjs API demos."""
    print("YDoc Yjs-like API Demo")
    print("=" * 35)
    print()

    demo_yjs_like_api()
    demo_api_comparison()
    demo_real_world_usage()
    demo_all_types()
    demo_migration_from_yjs()

    print("🎉 All Yjs-like API demos completed successfully!")
    print()
    print("Key Benefits:")
    print("- ✅ Familiar API for Yjs developers")
    print("- ✅ Easy migration from Yjs to YDoc")
    print("- ✅ Backward compatible with existing code")
    print("- ✅ More intuitive method names")
    print("- ✅ Matches Yjs documentation patterns")


if __name__ == "__main__":
    main()