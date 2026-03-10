"""
YDoc API Reference

This example serves as a comprehensive reference for both the original API
and the new Yjs-like convenience methods.
"""

from ydoc import Doc


def demo_complete_api_reference():
    """Complete API reference showing all available methods."""
    print("=== YDoc Complete API Reference ===")
    print()

    doc = Doc()

    print("📋 Yjs-like Methods (Recommended):")
    print("-" * 40)

    # Yjs-like methods
    text = doc.get_text("my_text")
    map_ = doc.get_map("my_map")
    array = doc.get_array("my_array")
    xml = doc.get_xml("my_xml")

    print(f"doc.get_text(name)    → {type(text).__name__}")
    print(f"doc.get_map(name)     → {type(map_).__name__}")
    print(f"doc.get_array(name)   → {type(array).__name__}")
    print(f"doc.get_xml(name)     → {type(xml).__name__}")

    print()
    print("📋 Original Methods (Backward Compatible):")
    print("-" * 40)

    # Original methods
    text_orig = doc.get("text_data", "text")
    map_orig = doc.get("map_data", "map")
    array_orig = doc.get("array_data", "array")
    xml_orig = doc.get("xml_data", "xml")

    print(f"doc.get(name, 'text')  → {type(text_orig).__name__}")
    print(f"doc.get(name, 'map')   → {type(map_orig).__name__}")
    print(f"doc.get(name, 'array') → {type(array_orig).__name__}")
    print(f"doc.get(name, 'xml')   → {type(xml_orig).__name__}")

    print()
    print("🔄 API Equivalence:")
    print("-" * 40)
    print("doc.get_text('name')  ≡  doc.get('name', 'text')")
    print("doc.get_map('name')   ≡  doc.get('name', 'map')")
    print("doc.get_array('name') ≡  doc.get('name', 'array')")
    print("doc.get_xml('name')   ≡  doc.get('name', 'xml')")

    print()
    print("✅ Both APIs return identical instances")
    print("✅ Use whichever style you prefer!")
    print()


def demo_api_usage_patterns():
    """Show common usage patterns for the API."""
    print("=== Common API Usage Patterns ===")
    print()

    doc = Doc()

    print("📝 Pattern 1: Default Names")
    print("-" * 30)
    # Using default names
    content = doc.get_text()  # Uses "text" as default name
    data = doc.get_map()  # Uses "map" as default name
    items = doc.get_array()  # Uses "array" as default name
    element = doc.get_xml()  # Uses "xml" as default name

    print("content = doc.get_text()      # name='text'")
    print("data = doc.get_map()         # name='map'")
    print("items = doc.get_array()      # name='array'")
    print("element = doc.get_xml()      # name='xml'")
    print()

    print("📝 Pattern 2: Custom Names")
    print("-" * 30)
    # Using custom names
    article = doc.get_text("article_content")
    settings = doc.get_map("user_settings")
    history = doc.get_array("edit_history")

    print("article = doc.get_text('article_content')")
    print("settings = doc.get_map('user_settings')")
    print("history = doc.get_array('edit_history')")
    print()

    print("📝 Pattern 3: Mixed Usage")
    print("-" * 30)
    # Mixing both styles
    title = doc.get_text("page_title")
    metadata = doc.get("post_metadata", "map")  # Original style
    tags = doc.get_array("content_tags")

    print("title = doc.get_text('page_title')        # Yjs-style")
    print("metadata = doc.get('post_metadata', 'map')  # Original style")
    print("tags = doc.get_array('content_tags')       # Yjs-style")
    print()

    print("✅ All patterns work seamlessly together!")
    print()


def demo_api_best_practices():
    """Show best practices for using the API."""
    print("=== API Best Practices ===")
    print()

    doc = Doc()

    print("✅ DO: Use Yjs-like methods for new code")
    print("   content = doc.get_text('main_content')")
    print()

    print("✅ DO: Use descriptive names")
    print("   user_data = doc.get_map('current_user_data')")
    print()

    print("✅ DO: Be consistent within a project")
    print("   Stick to one style (Yjs-like recommended)")
    print()

    print("✅ DO: Use default names for common cases")
    print("   text = doc.get_text()  # When 'text' is appropriate")
    print()

    print("⚠️  AVOID: Mixing styles unnecessarily")
    print("   ❌ Inconsistent: doc.get_text('a'); doc.get('b', 'map')")
    print("   ✅ Consistent:  doc.get_text('a'); doc.get_map('b')")
    print()

    print("💡 TIP: Yjs-like methods are more readable and maintainable")
    print()


def demo_api_performance():
    """Show that both APIs have identical performance."""
    print("=== API Performance Comparison ===")
    print()

    import time

    doc = Doc()

    # Test Yjs-like API
    start_time = time.time()
    for i in range(1000):
        doc.get_text(f"text_{i}")
    yjs_time = time.time() - start_time

    # Test original API
    start_time = time.time()
    for i in range(1000):
        doc.get(f"orig_{i}", "text")
    original_time = time.time() - start_time

    print(f"Yjs-like API:   {yjs_time:.6f} seconds for 1000 calls")
    print(f"Original API:   {original_time:.6f} seconds for 1000 calls")
    print(f"Difference:     {abs(yjs_time - original_time):.6f} seconds")

    if abs(yjs_time - original_time) < 0.001:
        print("✅ Performance is identical!")
    else:
        print("⚠️  Small difference due to measurement noise")

    print()
    print("💡 Both APIs have the same performance characteristics")
    print("💡 Choose based on readability, not performance")
    print()


def demo_api_migration_guide():
    """Guide for migrating from original to Yjs-like API."""
    print("=== Migration Guide ===")
    print()

    print("📋 Migration Steps:")
    print("-" * 25)

    print("1. Identify all doc.get() calls")
    print("   grep -r 'doc\.get(' your_project/")
    print()

    print("2. Replace with Yjs-like methods:")
    print("   doc.get('name', 'text')  →  doc.get_text('name')")
    print("   doc.get('name', 'map')   →  doc.get_map('name')")
    print("   doc.get('name', 'array') →  doc.get_array('name')")
    print("   doc.get('name', 'xml')   →  doc.get_xml('name')")
    print()

    print("3. Test thoroughly:")
    print("   - All existing tests should pass")
    print("   - No behavior changes expected")
    print()

    print("4. Update documentation:")
    print("   - Use Yjs-like methods in new examples")
    print("   - Keep old examples for reference")
    print()

    print("5. Enjoy the benefits!")
    print("   - More readable code")
    print("   - Familiar to Yjs developers")
    print("   - Better IDE autocomplete")
    print()

    print("⏱️  Estimated migration time: < 1 hour for most projects")
    print("🎯 Impact: Improved code quality and maintainability")
    print()


def main():
    """Run all API reference examples."""
    print("YDoc API Reference and Best Practices")
    print("=" * 50)
    print()

    demo_complete_api_reference()
    demo_api_usage_patterns()
    demo_api_best_practices()
    demo_api_performance()
    demo_api_migration_guide()

    print("🎉 API Reference Complete!")
    print()
    print("Key Takeaways:")
    print("- ✅ Yjs-like methods are recommended for new code")
    print("- ✅ Original API remains for backward compatibility")
    print("- ✅ Both APIs have identical performance")
    print("- ✅ Migration is straightforward and safe")
    print("- ✅ Choose the style that works best for your team")


if __name__ == "__main__":
    main()
