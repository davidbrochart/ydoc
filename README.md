# YDoc - Python CRDT Implementation

A Python implementation of Yjs core CRDT (Conflict-free Replicated Data Type) functionality, inspired by the JavaScript Yjs library.

## Status

[![CI Status](https://github.com/yjs/ydoc/actions/workflows/test.yml/badge.svg)](https://github.com/yjs/ydoc/actions/workflows/test.yml)

This is an early-stage translation of Yjs to Python, focusing on the core CRDT algorithms and data structures.

## Key Features

- **CRDT Core**: Conflict-free replicated data types
- **Collaborative Editing**: Real-time document synchronization
- **Offline Support**: Work offline and sync when connection is restored
- **Event System**: Observe document changes

## Installation

```bash
# TODO: Add installation instructions
```

## Usage

```python
from ydoc import Doc

# Create a document
doc = Doc()

# Get or create a shared data type
text = doc.get("text", "text")

# Make changes within a transaction
doc.transact(lambda txn: text.insert(0, "Hello World!"))
```

## Development

This project is a work in progress. The goal is to provide Python developers with the same powerful CRDT capabilities available in Yjs.