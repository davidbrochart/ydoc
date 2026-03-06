"""
Basic usage example for YDoc
"""

from ydoc import Doc, create_id

def main():
    print("=== YDoc Basic Usage Example ===")

    # Create a new document
    doc = Doc()
    print(f"Created document with GUID: {doc.guid}")
    print(f"Client ID: {doc.client_id}")

    # Create some IDs
    id1 = create_id(1, 10)
    id2 = create_id(2, 5)
    print(f"Created IDs: {id1}, {id2}")
    print(f"ID comparison: {id1 < id2}")

    # Get shared data types
    text_type = doc.get("text", "text")
    map_type = doc.get("map", "map")
    print(f"Available shared types: {list(doc.share.keys())}")

    # Execute a transaction
    result = doc.transact(lambda d: "Transaction executed successfully!")
    print(f"Transaction result: {result}")

    # Convert to JSON
    json_data = doc.to_json()
    print(f"Document as JSON: {json_data}")

    # Clean up
    doc.destroy()
    print("Document destroyed")

if __name__ == "__main__":
    main()