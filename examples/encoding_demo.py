"""
Encoding/Decoding Demo for YDoc

This example demonstrates the binary encoding/decoding system that enables
efficient synchronization of CRDT updates between clients.
"""

from ydoc import (
    Doc, YText, create_id, 
    UpdateEncoderV1, UpdateDecoderV1,
    Encoder, Decoder, write_any, read_any
)


def demo_basic_encoding():
    """Demonstrate basic encoding/decoding."""
    print("=== Basic Encoding Demo ===")
    
    # Create an encoder
    encoder = Encoder()
    
    # Write some data
    encoder.write_var_uint(42)
    encoder.write_var_string("Hello YDoc!")
    encoder.write_uint8(100)
    
    # Get the binary data
    binary_data = encoder.to_bytes()
    print(f"Encoded {len(binary_data)} bytes: {list(binary_data)}")
    
    # Decode it back
    decoder = Decoder(binary_data)
    value1 = decoder.read_var_uint()
    value2 = decoder.read_var_string()
    value3 = decoder.read_uint8()
    
    print(f"Decoded: {value1}, '{value2}', {value3}")
    print()


def demo_any_encoding():
    """Demonstrate encoding of complex data structures."""
    print("=== Any Encoding Demo ===")
    
    # Complex data structure
    data = {
        "document": {
            "title": "YDoc Encoding Demo",
            "version": 1.0,
            "active": True,
            "tags": ["crdt", "python", "yjs"],
            "metadata": None
        },
        "content": "This is a test document for encoding.",
        "binary": b"\x01\x02\x03\x04"
    }
    
    # Encode the complex structure
    encoder = Encoder()
    write_any(encoder, data)
    binary_data = encoder.to_bytes()
    
    print(f"Complex data encoded to {len(binary_data)} bytes")
    
    # Decode it back
    decoder = Decoder(binary_data)
    decoded_data = read_any(decoder)
    
    print(f"Original title: {data['document']['title']}")
    print(f"Decoded title:  {decoded_data['document']['title']}")
    print(f"Data matches: {data == decoded_data}")
    print()


def demo_update_encoding():
    """Demonstrate update encoding for CRDT synchronization."""
    print("=== Update Encoding Demo ===")
    
    # Create an update encoder
    encoder = UpdateEncoderV1()
    
    # Simulate some CRDT operations
    doc_id = create_id(1, 0)
    text_id = create_id(1, 1)
    
    # Write update information
    encoder.write_client(1)
    encoder.write_left_id(doc_id)
    encoder.write_right_id(text_id)
    encoder.write_info(4)  # String content type
    encoder.write_string("Hello from YDoc!")
    encoder.write_len(13)
    
    # Get the update binary
    update_data = encoder.to_bytes()
    print(f"CRDT update encoded to {len(update_data)} bytes")
    
    # Decode the update
    decoder = Decoder(update_data)
    update_decoder = UpdateDecoderV1(decoder)
    
    client = update_decoder.read_client()
    left_id = update_decoder.read_left_id()
    right_id = update_decoder.read_right_id()
    info = update_decoder.read_info()
    content = update_decoder.read_string()
    length = update_decoder.read_len()
    
    print(f"Decoded update:")
    print(f"  Client: {client}")
    print(f"  Left ID: {left_id}")
    print(f"  Right ID: {right_id}")
    print(f"  Info: {info} (String content)")
    print(f"  Content: '{content}'")
    print(f"  Length: {length}")
    print()


def demo_practical_usage():
    """Demonstrate practical usage with YDoc."""
    print("=== Practical Usage Demo ===")
    
    # Create a document
    doc = Doc()
    text = doc.get("content", "text")
    
    # Make some changes
    text.insert(0, "Hello World!")
    
    print(f"Document content: '{text}'")
    print(f"Document GUID: {doc.guid}")
    print(f"Client ID: {doc.client_id}")
    
    # In a real application, you would:
    # 1. Encode the document state or changes
    # 2. Send over network
    # 3. Decode and apply on remote client
    
    print("\nThis encoding system enables:")
    print("✅ Efficient binary representation of CRDT operations")
    print("✅ Network synchronization between clients")
    print("✅ State vector exchange for partial updates")
    print("✅ Conflict-free merge of concurrent edits")
    print()


if __name__ == "__main__":
    demo_basic_encoding()
    demo_any_encoding()
    demo_update_encoding()
    demo_practical_usage()
    
    print("🎉 Encoding/Decoding demo completed!")
    print("\nThe encoding system provides the foundation for:")
    print("- Binary update exchange between clients")
    print("- Efficient state synchronization")
    print("- Network protocol implementation")
    print("- Persistence and storage")