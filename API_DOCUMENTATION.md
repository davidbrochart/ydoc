# YDoc API Documentation

This document provides comprehensive documentation for YDoc's API, including both the original API and the new Yjs-like convenience methods.

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [Yjs-like Methods (Recommended)](#-yjs-like-methods-recommended)
- [Original Methods (Backward Compatible)](#-original-methods-backward-compatible)
- [API Comparison](#-api-comparison)
- [Usage Patterns](#-usage-patterns)
- [Best Practices](#-best-practices)
- [Migration Guide](#-migration-guide)

## 🚀 Quick Start

```python
from ydoc import Doc

# Create a document
doc = Doc()

# Recommended: Yjs-like methods
content = doc.get_text("main_content")
data = doc.get_map("user_data")
items = doc.get_array("item_list")

# Backward compatible: Original method
text = doc.get("some_text", "text")
```

## 🎯 Yjs-like Methods (Recommended)

These methods provide a more intuitive, Yjs-compatible API:

### `get_text(name="text")`

Get or create a YText shared data type.

**Parameters:**
- `name` (str): The key/name for the text type (default: "text")

**Returns:** `YText` instance

**Example:**
```python
doc = Doc()
# With default name
content = doc.get_text()  # name = "text"

# With custom name
article = doc.get_text("article_content")
```

### `get_map(name="map")`

Get or create a YMap shared data type.

**Parameters:**
- `name` (str): The key/name for the map type (default: "map")

**Returns:** `YMap` instance

**Example:**
```python
doc = Doc()
# With default name
data = doc.get_map()  # name = "map"

# With custom name
settings = doc.get_map("user_settings")
```

### `get_array(name="array")`

Get or create a YArray shared data type.

**Parameters:**
- `name` (str): The key/name for the array type (default: "array")

**Returns:** `YArray` instance

**Example:**
```python
doc = Doc()
# With default name
items = doc.get_array()  # name = "array"

# With custom name
history = doc.get_array("edit_history")
```

### `get_xml(name="xml")`

Get or create a YXml shared data type.

**Parameters:**
- `name` (str): The key/name for the xml type (default: "xml")

**Returns:** `YXml` instance

**Example:**
```python
doc = Doc()
# With default name
element = doc.get_xml()  # name = "xml"

# With custom name
node = doc.get_xml("dom_element")
```

## 📚 Original Methods (Backward Compatible)

The original `get()` method is still available for backward compatibility:

### `get(key, name=None)`

Define a shared data type.

**Parameters:**
- `key` (str): The key/name for the shared data type
- `name` (str, optional): The type name ("text", "map", "array", or "xml")

**Returns:** `YType` instance

**Example:**
```python
doc = Doc()
# Get text type
text = doc.get("content", "text")

# Get map type
map_ = doc.get("data", "map")

# Get array type
array = doc.get("items", "array")

# Get xml type
xml = doc.get("element", "xml")
```

## 🔄 API Comparison

| Yjs Method | YDoc Yjs-like | YDoc Original |
|------------|---------------|---------------|
| `doc.getText()` | `doc.get_text()` | `doc.get("name", "text")` |
| `doc.getMap()` | `doc.get_map()` | `doc.get("name", "map")` |
| `doc.getArray()` | `doc.get_array()` | `doc.get("name", "array")` |
| `doc.getXml()` | `doc.get_xml()` | `doc.get("name", "xml")` |

**Key Differences:**
- Yjs uses camelCase (`getText`)
- YDoc uses snake_case (`get_text`)
- Both APIs are fully equivalent and interchangeable

## 📝 Usage Patterns

### Pattern 1: Default Names

```python
doc = Doc()
# Use default names when they're appropriate
content = doc.get_text()      # name = "text"
data = doc.get_map()         # name = "map"
items = doc.get_array()      # name = "array"
```

### Pattern 2: Custom Names

```python
doc = Doc()
# Use descriptive names for clarity
article_content = doc.get_text("article_content")
user_settings = doc.get_map("user_settings")
edit_history = doc.get_array("edit_history")
```

### Pattern 3: Mixed Usage

```python
doc = Doc()
# Both styles can be mixed (though consistency is recommended)
title = doc.get_text("page_title")
metadata = doc.get("post_metadata", "map")  # Original style
tags = doc.get_array("content_tags")
```

## ✅ Best Practices

### ✅ DO

1. **Use Yjs-like methods for new code**
   ```python
   content = doc.get_text("main_content")
   ```

2. **Use descriptive names**
   ```python
   user_data = doc.get_map("current_user_data")
   ```

3. **Be consistent within a project**
   ```python
   # Stick to one style (Yjs-like recommended)
   text = doc.get_text("a")
   map_ = doc.get_map("b")
   ```

4. **Use default names when appropriate**
   ```python
   text = doc.get_text()  # When "text" is a good name
   ```

### ⚠️ AVOID

1. **Mixing styles unnecessarily**
   ```python
   # ❌ Inconsistent
   doc.get_text("a")
   doc.get("b", "map")

   # ✅ Consistent
   doc.get_text("a")
   doc.get_map("b")
   ```

2. **Overly generic names**
   ```python
   # ❌ Not descriptive
   doc.get_text("data")

   # ✅ Descriptive
   doc.get_text("article_content")
   ```

## 🚀 Migration Guide

### From Original API to Yjs-like API

**Before:**
```python
doc = Doc()
text = doc.get("content", "text")
map_ = doc.get("data", "map")
array = doc.get("items", "array")
```

**After:**
```python
doc = Doc()
text = doc.get_text("content")
map_ = doc.get_map("data")
array = doc.get_array("items")
```

### Migration Steps

1. **Identify usage**: Find all `doc.get()` calls
   ```bash
   grep -r 'doc\.get(' your_project/
   ```

2. **Replace method calls**:
   - `doc.get("name", "text")` → `doc.get_text("name")`
   - `doc.get("name", "map")` → `doc.get_map("name")`
   - `doc.get("name", "array")` → `doc.get_array("name")`
   - `doc.get("name", "xml")` → `doc.get_xml("name")`

3. **Test thoroughly**: All existing tests should pass

4. **Update documentation**: Use Yjs-like methods in new examples

### Benefits of Migration

- ✅ More readable and maintainable code
- ✅ Familiar to Yjs developers
- ✅ Better IDE autocomplete support
- ✅ Follows modern Python conventions
- ✅ Easier to understand for new team members

## 🎉 Summary

YDoc provides two equivalent APIs:

1. **Yjs-like methods** (recommended) - More intuitive and modern
2. **Original `get()` method** - Maintained for backward compatibility

**Recommendation:** Use Yjs-like methods for new code, but both APIs will continue to work indefinitely.

## 📚 Additional Resources

- [Yjs Documentation](https://docs.yjs.dev/) - For Yjs concepts and patterns
- [YDoc Examples](examples/) - Practical usage examples
- [API Reference](examples/api_reference.py) - Complete API demonstration
- [Yjs-like Demo](examples/yjs_api_demo.py) - Yjs compatibility showcase

## 🐍 Python-Specific Notes

- YDoc uses `snake_case` instead of Yjs's `camelCase`
- All methods are fully type-hinted
- Works with Python 3.10+
- Follows PEP 8 style guidelines

## 🔧 Troubleshooting

**Issue:** `AttributeError: 'Doc' object has no attribute 'get_text'`

**Solution:** Make sure you're using the latest version of YDoc and have imported correctly:
```python
from ydoc import Doc
doc = Doc()
text = doc.get_text("content")  # Should work
```

**Issue:** Getting unexpected type

**Solution:** Check that you're using the correct method:
```python
# For text content
doc.get_text("name")  # Returns YText

# For key-value data
doc.get_map("name")   # Returns YMap

# For lists/arrays
doc.get_array("name") # Returns YArray
```

## 📈 Performance

Both APIs have identical performance characteristics:
- Same underlying implementation
- Same memory usage
- Same execution speed
- Choose based on readability, not performance

## 🤝 Community

- Found a bug? [Open an issue](https://github.com/your-repo/ydoc/issues)
- Have a question? Check our [discussions](https://github.com/your-repo/ydoc/discussions)
- Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

This documentation is provided under the same license as YDoc itself.

---

*Last updated: 2024*
*YDoc version: 0.1.0*
