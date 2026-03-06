# YDoc - Python CRDT Implementation

[![CI Status](https://github.com/davidbrochart/ydoc/actions/workflows/test.yml/badge.svg)](https://github.com/davidbrochart/ydoc/actions/workflows/test.yml)

A Python implementation of Yjs core CRDT (Conflict-free Replicated Data Type) functionality, inspired by the JavaScript Yjs library.

## Quick Start

YDoc brings the power of Yjs CRDTs to Python with a familiar API.

### Installation

```bash
pip install ydoc
```

### Your first YDoc

```python
from ydoc import Doc

# Create a document
doc = Doc()

# Get or create shared data types (Yjs-like API)
text = doc.get_text("content")
map_ = doc.get_map("data")
array = doc.get_array("items")

# Make changes
text.insert(0, "Hello World!")
map_["key"] = "value"
array.insert(0, ["item"])
```

### Synchronize documents

```python
from ydoc import Doc, encode_state_as_update, apply_update

# Create two documents
doc1 = Doc()
doc2 = Doc()

# Encode and apply updates
update = encode_state_as_update(doc1)
apply_update(doc2, update)

# Now both documents have the same state!
```

## Features

YDoc implements core Yjs functionality with a Pythonic API:

### Shared Data Types

- **YText**: Collaborative text editing
- **YMap**: Key-value storage
- **YArray**: Ordered lists
- **YXml**: XML/HTML elements

### Synchronization

- **State Updates**: Encode and apply document state
- **Conflict Resolution**: Automatic merge of concurrent changes
- **Update Propagation**: Multi-client synchronization

### Advanced Features

- **Transactions**: Atomic changes with `doc.transact()`
- **Undo/Redo**: Track and revert changes
- **Event System**: Observe document changes
- **Awareness**: Track collaborative users

## API Reference

### Yjs-like Methods (Recommended)

```python
doc.get_text(name="text")    # YText
doc.get_map(name="map")      # YMap
doc.get_array(name="array")  # YArray
doc.get_xml(name="xml")      # YXml
```

### Document Synchronization

```python
update = encode_state_as_update(doc)
apply_update(other_doc, update)
```

### Transactions

```python
doc.transact(lambda txn: 
    doc.get_text("content").insert(0, "Hello!")
)
```

## Examples

Explore the [examples](examples/) directory for practical usage:

- [`basic_usage.py`](examples/basic_usage.py) - Core functionality
- [`yjs_api_demo.py`](examples/yjs_api_demo.py) - Yjs-like API
- [`api_reference.py`](examples/api_reference.py) - Complete reference
- [`encode_apply_demo.py`](examples/encode_apply_demo.py) - Update system
- [`conflict_resolution_demo.py`](examples/conflict_resolution_demo.py) - Conflict resolution

## Development

This project is a work in progress, translating Yjs to Python while maintaining:

- **API Compatibility**: Match Yjs patterns where possible
- **Python Idioms**: Use Python conventions and type hints
- **Performance**: Efficient CRDT operations
- **Test Coverage**: Comprehensive test suite (116 tests)

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

### Roadmap

- [x] Core CRDT data structures
- [x] Shared data types (Text, Map, Array, Xml)
- [x] Document synchronization
- [x] Yjs-like convenience methods
- [x] Comprehensive test suite
- [ ] Network layer integration
- [ ] Persistence and loading
- [ ] Advanced conflict resolution

## Resources

- [Yjs Documentation](https://docs.yjs.dev) - Learn CRDT concepts
- [API Documentation](API_DOCUMENTATION.md) - Complete YDoc reference
- [Examples](examples/) - Practical usage patterns

## License

MIT License - See [LICENSE](LICENSE) for details.