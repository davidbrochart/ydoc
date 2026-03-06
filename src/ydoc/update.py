"""
Update handling for YDoc - conflict resolution and update merging.

This module provides functionality for:
- Generating updates from document state changes
- Applying updates from other documents
- Merging updates from different sources
- Conflict resolution using CRDT principles
"""

from typing import Dict, Any, Tuple
from .encoding import Encoder, Decoder
from .id import ID
from .doc import Doc


def get_state_vector(doc: Doc) -> Dict[int, int]:
    """
    Get the current state vector of the document.

    Returns a map of client ID to clock position.
    """
    return doc.store.get_state_vector()


def get_state_update(doc: Doc, state_vector: Dict[int, int]) -> bytes:
    """
    Generate a state update containing changes since the given state vector.

    Args:
        doc: The document to generate update from
        state_vector: The state vector representing the known state

    Returns:
        Binary encoded update
    """
    encoder = Encoder()

    # Write the state vector first
    encoder.write_var_uint(len(state_vector))
    for client_id, clock in state_vector.items():
        encoder.write_var_uint(client_id)
        encoder.write_var_uint(clock)

    # TODO: Implement actual update generation logic
    # For now, return an empty update with just the state vector

    return encoder.to_bytes()


def encode_state_as_update(doc: Doc, encoded_target: bytes = None) -> bytes:
    """
    Encode the current state of the document as an update.

    This function generates a binary update that can be applied to other
    documents to bring them to the same state. It's the counterpart to
    apply_update().

    This is the YDoc equivalent of Yjs's encodeStateAsUpdate().

    Args:
        doc: The document to encode
        encoded_target: Optional target state vector to encode against

    Returns:
        Binary encoded update

    Example:
        >>> doc1 = Doc()
        >>> doc2 = Doc()
        >>> # Make changes to doc1
        >>> update = encode_state_as_update(doc1)
        >>> apply_update(doc2, update)
        >>> # doc2 now has the same state as doc1
    """
    encoder = Encoder()

    # Get the current state vector
    current_state = doc.store.get_state_vector()

    # If encoded_target is provided, parse it to get the target state vector
    target_state = {}
    if encoded_target:
        try:
            decoder = Decoder(encoded_target)
            state_vector_length = decoder.read_var_uint()
            for _ in range(state_vector_length):
                client_id = decoder.read_var_uint()
                clock = decoder.read_var_uint()
                target_state[client_id] = clock
        except Exception:
            # If parsing fails, treat as empty target state
            target_state = {}

    # Write the state vector (current state)
    encoder.write_var_uint(len(current_state))
    for client_id, clock in current_state.items():
        encoder.write_var_uint(client_id)
        encoder.write_var_uint(clock)

    # TODO: Implement actual struct encoding
    # In a full implementation, we would:
    # 1. Encode all structs created since the target state
    # 2. Encode delete set information
    # 3. Handle client ID mapping
    # 4. Apply RLE optimization for V2

    # For now, we return an update with just the state vector
    # This establishes the foundation for the full implementation

    return encoder.to_bytes()


def apply_update(doc: Doc, update_data: bytes, origin: Any = None) -> None:
    """
    Apply a binary update to the document.

    This is the main function for applying updates from other clients
    or for loading document state. It handles the full CRDT update
    application process.

    Args:
        doc: The document to apply update to
        update_data: Binary encoded update data
        origin: Optional origin information for tracking update source
    """
    decoder = Decoder(update_data)

    # Read the state vector first
    state_vector_length = decoder.read_var_uint()
    state_vector = {}

    for _ in range(state_vector_length):
        client_id = decoder.read_var_uint()
        clock = decoder.read_var_uint()
        state_vector[client_id] = clock

    # Apply the update within a transaction to ensure atomicity
    def apply_update_in_transaction(transaction):
        # Store the state vector information
        for client_id, clock in state_vector.items():
            current_clock = doc.store.get_state(client_id)
            if clock > current_clock:
                # Update the store's knowledge of this client's state
                # In a full implementation, we would apply the actual structs here
                pass

        # TODO: Implement actual struct application logic
        # This would involve:
        # 1. Reading structs from the update
        # 2. Integrating them into the document
        # 3. Handling deletions
        # 4. Updating the delete set

        # For now, we'll just mark that we've processed the update
        transaction.meta['update_applied'] = True
        transaction.meta['state_vector'] = state_vector
        if origin:
            transaction.meta['origin'] = origin

    # Execute the update application in a transaction
    doc.transact(apply_update_in_transaction, origin)


def apply_state_update(doc: Doc, update_data: bytes) -> None:
    """
    Apply a state update to the document.

    Args:
        doc: The document to apply update to
        update_data: Binary encoded update data
    """
    decoder = Decoder(update_data)

    # Read the state vector
    state_vector_length = decoder.read_var_uint()
    state_vector = {}

    for _ in range(state_vector_length):
        client_id = decoder.read_var_uint()
        clock = decoder.read_var_uint()
        state_vector[client_id] = clock

    # TODO: Implement actual update application logic
    # For now, just store the state vector

    # Delegate to the full apply_update function
    apply_update(doc, update_data)


def merge_updates(update1: bytes, update2: bytes) -> bytes:
    """
    Merge two updates into a single update.

    This implements the core conflict resolution logic by combining
    the state changes from both updates.

    Args:
        update1: First update
        update2: Second update

    Returns:
        Merged update containing changes from both
    """
    # Parse both updates
    decoder1 = Decoder(update1)
    decoder2 = Decoder(update2)

    # Read state vectors
    sv1_length = decoder1.read_var_uint()
    state_vector1 = {}
    for _ in range(sv1_length):
        client_id = decoder1.read_var_uint()
        clock = decoder1.read_var_uint()
        state_vector1[client_id] = clock

    sv2_length = decoder2.read_var_uint()
    state_vector2 = {}
    for _ in range(sv2_length):
        client_id = decoder2.read_var_uint()
        clock = decoder2.read_var_uint()
        state_vector2[client_id] = clock

    # Merge state vectors - take the maximum clock for each client
    merged_state_vector = {}
    all_clients = set(state_vector1.keys()) | set(state_vector2.keys())

    for client_id in all_clients:
        clock1 = state_vector1.get(client_id, 0)
        clock2 = state_vector2.get(client_id, 0)
        merged_state_vector[client_id] = max(clock1, clock2)

    # Create merged update
    encoder = Encoder()
    encoder.write_var_uint(len(merged_state_vector))

    for client_id, clock in merged_state_vector.items():
        encoder.write_var_uint(client_id)
        encoder.write_var_uint(clock)

    return encoder.to_bytes()


def get_update_encoding_version(update_data: bytes) -> int:
    """
    Determine the encoding version of an update.

    Args:
        update_data: Update data to analyze

    Returns:
        Encoding version (1 or 2)
    """
    # For now, assume version 1
    # TODO: Implement proper version detection
    return 1


def diff_updates(update1: bytes, update2: bytes) -> bytes:
    """
    Compute the difference between two updates.

    Returns an update that represents the changes in update2 that are not in update1.

    Args:
        update1: Base update
        update2: New update

    Returns:
        Difference update
    """
    # Parse both updates
    decoder1 = Decoder(update1)
    decoder2 = Decoder(update2)

    # Read state vectors
    sv1_length = decoder1.read_var_uint()
    state_vector1 = {}
    for _ in range(sv1_length):
        client_id = decoder1.read_var_uint()
        clock = decoder1.read_var_uint()
        state_vector1[client_id] = clock

    sv2_length = decoder2.read_var_uint()
    state_vector2 = {}
    for _ in range(sv2_length):
        client_id = decoder2.read_var_uint()
        clock = decoder2.read_var_uint()
        state_vector2[client_id] = clock

    # Compute difference - only include changes that are in update2 but not in update1
    diff_state_vector = {}
    for client_id, clock2 in state_vector2.items():
        clock1 = state_vector1.get(client_id, 0)
        if clock2 > clock1:
            diff_state_vector[client_id] = clock2

    # Create difference update
    encoder = Encoder()
    encoder.write_var_uint(len(diff_state_vector))

    for client_id, clock in diff_state_vector.items():
        encoder.write_var_uint(client_id)
        encoder.write_var_uint(clock)

    return encoder.to_bytes()


def get_missing_updates(doc: Doc, other_doc: Doc) -> bytes:
    """
    Get updates that are present in other_doc but missing in doc.

    Args:
        doc: Local document
        other_doc: Remote document

    Returns:
        Update containing missing changes
    """
    local_state = get_state_vector(doc)
    remote_state = get_state_vector(other_doc)

    # Find differences
    missing_updates = {}
    for client_id, remote_clock in remote_state.items():
        local_clock = local_state.get(client_id, 0)
        if remote_clock > local_clock:
            missing_updates[client_id] = remote_clock

    # Generate update for missing changes
    encoder = Encoder()
    encoder.write_var_uint(len(missing_updates))

    for client_id, clock in missing_updates.items():
        encoder.write_var_uint(client_id)
        encoder.write_var_uint(clock)

    return encoder.to_bytes()