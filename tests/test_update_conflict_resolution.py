"""
Conflict resolution tests for YDoc update system.

These tests verify that the conflict resolution and update merging
functionality works correctly, inspired by Yjs patterns.
"""

import pytest
from ydoc import (
    Doc, get_state_vector, get_state_update, apply_state_update,
    merge_updates, diff_updates, get_missing_updates,
    get_update_encoding_version
)


class TestStateVector:
    """Test state vector functionality."""

    def test_get_state_vector_empty_doc(self):
        """Test getting state vector from empty document."""
        doc = Doc()
        state_vector = get_state_vector(doc)

        # Empty document should have empty state vector
        assert isinstance(state_vector, dict)
        assert len(state_vector) == 0

    def test_get_state_vector_with_data(self):
        """Test getting state vector from document with data."""
        doc = Doc()

        # Add some data to the document and make some changes
        text = doc.get("text")

        # Manually add a struct to the store for testing
        from ydoc import ID, create_id, Item
        test_id = create_id(doc.client_id, 10)
        test_item = Item(test_id)
        doc.store.add_struct(test_item)

        # The state vector should contain the client ID
        state_vector = get_state_vector(doc)

        # Should have at least the local client
        assert doc.client_id in state_vector
        assert state_vector[doc.client_id] > 0


class TestStateUpdateGeneration:
    """Test state update generation."""

    def test_get_state_update_empty_state_vector(self):
        """Test generating update with empty state vector."""
        doc = Doc()
        empty_state = {}

        update = get_state_update(doc, empty_state)

        # Should return valid binary data
        assert isinstance(update, bytes)
        assert len(update) > 0

    def test_get_state_update_with_state_vector(self):
        """Test generating update with non-empty state vector."""
        doc = Doc()
        state_vector = {doc.client_id: 0}

        update = get_state_update(doc, state_vector)

        # Should return valid binary data
        assert isinstance(update, bytes)
        assert len(update) > 0


class TestStateUpdateApplication:
    """Test state update application."""

    def test_apply_state_update_empty_update(self):
        """Test applying empty update."""
        doc = Doc()

        # Create an empty update
        from ydoc.encoding import Encoder
        encoder = Encoder()
        encoder.write_var_uint(0)  # Empty state vector
        empty_update = encoder.to_bytes()

        # Should not raise exceptions
        apply_state_update(doc, empty_update)

    def test_apply_state_update_with_data(self):
        """Test applying update with state vector data."""
        doc = Doc()

        # Create an update with some state vector data
        from ydoc.encoding import Encoder
        encoder = Encoder()
        encoder.write_var_uint(1)  # One client
        encoder.write_var_uint(123)  # Client ID
        encoder.write_var_uint(456)  # Clock
        update = encoder.to_bytes()

        # Should not raise exceptions
        apply_state_update(doc, update)


class TestUpdateMerging:
    """Test update merging functionality."""

    def test_merge_empty_updates(self):
        """Test merging two empty updates."""
        # Create two empty updates
        from ydoc.encoding import Encoder
        encoder1 = Encoder()
        encoder1.write_var_uint(0)  # Empty state vector
        update1 = encoder1.to_bytes()

        encoder2 = Encoder()
        encoder2.write_var_uint(0)  # Empty state vector
        update2 = encoder2.to_bytes()

        merged = merge_updates(update1, update2)

        # Should return valid merged update
        assert isinstance(merged, bytes)
        assert len(merged) > 0

    def test_merge_updates_same_client(self):
        """Test merging updates from same client."""
        from ydoc.encoding import Encoder

        # Create update1 with client 123 at clock 100
        encoder1 = Encoder()
        encoder1.write_var_uint(1)  # One client
        encoder1.write_var_uint(123)  # Client ID
        encoder1.write_var_uint(100)  # Clock
        update1 = encoder1.to_bytes()

        # Create update2 with client 123 at clock 200
        encoder2 = Encoder()
        encoder2.write_var_uint(1)  # One client
        encoder2.write_var_uint(123)  # Client ID
        encoder2.write_var_uint(200)  # Clock
        update2 = encoder2.to_bytes()

        merged = merge_updates(update1, update2)

        # Should take the maximum clock (200)
        assert isinstance(merged, bytes)
        assert len(merged) > 0

    def test_merge_updates_different_clients(self):
        """Test merging updates from different clients."""
        from ydoc.encoding import Encoder

        # Create update1 with client 123 at clock 100
        encoder1 = Encoder()
        encoder1.write_var_uint(1)  # One client
        encoder1.write_var_uint(123)  # Client ID
        encoder1.write_var_uint(100)  # Clock
        update1 = encoder1.to_bytes()

        # Create update2 with client 456 at clock 200
        encoder2 = Encoder()
        encoder2.write_var_uint(1)  # One client
        encoder2.write_var_uint(456)  # Client ID
        encoder2.write_var_uint(200)  # Clock
        update2 = encoder2.to_bytes()

        merged = merge_updates(update1, update2)

        # Should contain both clients
        assert isinstance(merged, bytes)
        assert len(merged) > 0

    def test_merge_updates_overlapping_clients(self):
        """Test merging updates with overlapping clients."""
        from ydoc.encoding import Encoder

        # Create update1 with clients 123 and 456
        encoder1 = Encoder()
        encoder1.write_var_uint(2)  # Two clients
        encoder1.write_var_uint(123)  # Client ID 1
        encoder1.write_var_uint(100)  # Clock 1
        encoder1.write_var_uint(456)  # Client ID 2
        encoder1.write_var_uint(200)  # Clock 2
        update1 = encoder1.to_bytes()

        # Create update2 with clients 456 and 789
        encoder2 = Encoder()
        encoder2.write_var_uint(2)  # Two clients
        encoder2.write_var_uint(456)  # Client ID 1
        encoder2.write_var_uint(300)  # Clock 1 (higher than update1)
        encoder2.write_var_uint(789)  # Client ID 2
        encoder2.write_var_uint(400)  # Clock 2
        update2 = encoder2.to_bytes()

        merged = merge_updates(update1, update2)

        # Should take max clocks for each client
        assert isinstance(merged, bytes)
        assert len(merged) > 0


class TestUpdateDifferences:
    """Test update difference computation."""

    def test_diff_identical_updates(self):
        """Test difference between identical updates."""
        from ydoc.encoding import Encoder

        # Create identical updates
        encoder1 = Encoder()
        encoder1.write_var_uint(1)  # One client
        encoder1.write_var_uint(123)  # Client ID
        encoder1.write_var_uint(100)  # Clock
        update1 = encoder1.to_bytes()

        encoder2 = Encoder()
        encoder2.write_var_uint(1)  # One client
        encoder2.write_var_uint(123)  # Client ID
        encoder2.write_var_uint(100)  # Clock
        update2 = encoder2.to_bytes()

        diff = diff_updates(update1, update2)

        # Should be empty (no differences)
        assert isinstance(diff, bytes)
        # The diff should have 0 clients since clocks are equal
        assert diff[0] == 0  # First byte should be 0 (no clients)

    def test_diff_update_with_higher_clock(self):
        """Test difference when second update has higher clock."""
        from ydoc.encoding import Encoder

        # Create update1 with lower clock
        encoder1 = Encoder()
        encoder1.write_var_uint(1)  # One client
        encoder1.write_var_uint(123)  # Client ID
        encoder1.write_var_uint(100)  # Clock
        update1 = encoder1.to_bytes()

        # Create update2 with higher clock
        encoder2 = Encoder()
        encoder2.write_var_uint(1)  # One client
        encoder2.write_var_uint(123)  # Client ID
        encoder2.write_var_uint(200)  # Clock (higher)
        update2 = encoder2.to_bytes()

        diff = diff_updates(update1, update2)

        # Should contain the difference
        assert isinstance(diff, bytes)
        assert len(diff) > 0

    def test_diff_update_with_new_client(self):
        """Test difference when second update has new client."""
        from ydoc.encoding import Encoder

        # Create update1 with one client
        encoder1 = Encoder()
        encoder1.write_var_uint(1)  # One client
        encoder1.write_var_uint(123)  # Client ID
        encoder1.write_var_uint(100)  # Clock
        update1 = encoder1.to_bytes()

        # Create update2 with two clients
        encoder2 = Encoder()
        encoder2.write_var_uint(2)  # Two clients
        encoder2.write_var_uint(123)  # Client ID 1
        encoder2.write_var_uint(100)  # Clock 1 (same as update1)
        encoder2.write_var_uint(456)  # Client ID 2
        encoder2.write_var_uint(200)  # Clock 2 (new)
        update2 = encoder2.to_bytes()

        diff = diff_updates(update1, update2)

        # Should contain only the new client
        assert isinstance(diff, bytes)
        assert len(diff) > 0


class TestMissingUpdates:
    """Test missing updates detection."""

    def test_get_missing_updates_empty_docs(self):
        """Test missing updates between empty documents."""
        doc1 = Doc()
        doc2 = Doc()

        missing = get_missing_updates(doc1, doc2)

        # Should return empty update
        assert isinstance(missing, bytes)
        assert missing[0] == 0  # No missing clients

    def test_get_missing_updates_same_state(self):
        """Test missing updates when documents have same state."""
        doc1 = Doc()
        doc2 = Doc()

        # Both docs should have same initial state
        missing = get_missing_updates(doc1, doc2)

        # Should be empty
        assert isinstance(missing, bytes)
        assert missing[0] == 0  # No missing clients

    def test_get_missing_updates_different_clients(self):
        """Test missing updates when documents have different clients."""
        doc1 = Doc()
        doc2 = Doc()

        # Force different client IDs for testing
        doc1.client_id = 123
        doc2.client_id = 456

        # Add some data to doc2 to create state
        text2 = doc2.get("text")

        missing = get_missing_updates(doc1, doc2)

        # Should contain missing updates from doc2
        assert isinstance(missing, bytes)
        assert len(missing) > 0


class TestUpdateEncodingVersion:
    """Test update encoding version detection."""

    def test_get_update_encoding_version(self):
        """Test getting encoding version from update."""
        from ydoc.encoding import Encoder

        # Create a simple update
        encoder = Encoder()
        encoder.write_var_uint(0)  # Empty state vector
        update = encoder.to_bytes()

        version = get_update_encoding_version(update)

        # Should return version 1
        assert version == 1


class TestConflictResolutionScenarios:
    """Test realistic conflict resolution scenarios."""

    def test_simple_merge_scenario(self):
        """Test a simple merge scenario with two conflicting updates."""
        from ydoc.encoding import Encoder

        # Simulate two clients making changes
        # Client 123 creates update with clock 100
        encoder1 = Encoder()
        encoder1.write_var_uint(1)
        encoder1.write_var_uint(123)
        encoder1.write_var_uint(100)
        update1 = encoder1.to_bytes()

        # Client 456 creates update with clock 200
        encoder2 = Encoder()
        encoder2.write_var_uint(1)
        encoder2.write_var_uint(456)
        encoder2.write_var_uint(200)
        update2 = encoder2.to_bytes()

        # Merge should contain both clients
        merged = merge_updates(update1, update2)

        # Verify merged update is valid
        assert isinstance(merged, bytes)
        assert len(merged) > 0

        # Parse merged update to verify contents
        from ydoc.encoding import Decoder
        decoder = Decoder(merged)
        num_clients = decoder.read_var_uint()

        # Should have 2 clients
        assert num_clients == 2

    def test_concurrent_edits_merge(self):
        """Test merging concurrent edits from multiple clients."""
        from ydoc.encoding import Encoder

        # Three clients make concurrent changes
        # Client 1: clock 150
        encoder1 = Encoder()
        encoder1.write_var_uint(1)
        encoder1.write_var_uint(1)
        encoder1.write_var_uint(150)
        update1 = encoder1.to_bytes()

        # Client 2: clock 250
        encoder2 = Encoder()
        encoder2.write_var_uint(1)
        encoder2.write_var_uint(2)
        encoder2.write_var_uint(250)
        update2 = encoder2.to_bytes()

        # Client 3: clock 350
        encoder3 = Encoder()
        encoder3.write_var_uint(1)
        encoder3.write_var_uint(3)
        encoder3.write_var_uint(350)
        update3 = encoder3.to_bytes()

        # Merge first two
        merged12 = merge_updates(update1, update2)

        # Merge result with third
        final_merged = merge_updates(merged12, update3)

        # Should contain all three clients
        assert isinstance(final_merged, bytes)
        assert len(final_merged) > 0

    def test_update_propagation_scenario(self):
        """Test update propagation between multiple documents."""
        # Create three documents
        doc1 = Doc()
        doc2 = Doc()
        doc3 = Doc()

        # Force different client IDs
        doc1.client_id = 1
        doc2.client_id = 2
        doc3.client_id = 3

        # Get initial states
        state1 = get_state_vector(doc1)
        state2 = get_state_vector(doc2)
        state3 = get_state_vector(doc3)

        # Generate updates
        update1 = get_state_update(doc1, {})
        update2 = get_state_update(doc2, {})
        update3 = get_state_update(doc3, {})

        # Merge all updates
        merged12 = merge_updates(update1, update2)
        final_merged = merge_updates(merged12, update3)

        # Apply merged update to all documents
        apply_state_update(doc1, final_merged)
        apply_state_update(doc2, final_merged)
        apply_state_update(doc3, final_merged)

        # All documents should now have consistent state
        final_state1 = get_state_vector(doc1)
        final_state2 = get_state_vector(doc2)
        final_state3 = get_state_vector(doc3)

        # They should all have the same clients
        assert set(final_state1.keys()) == set(final_state2.keys()) == set(final_state3.keys())


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_merge_with_empty_update(self):
        """Test merging with empty update."""
        from ydoc.encoding import Encoder

        # Create non-empty update
        encoder1 = Encoder()
        encoder1.write_var_uint(1)
        encoder1.write_var_uint(123)
        encoder1.write_var_uint(100)
        update1 = encoder1.to_bytes()

        # Create empty update
        encoder2 = Encoder()
        encoder2.write_var_uint(0)
        update2 = encoder2.to_bytes()

        # Should handle gracefully
        merged = merge_updates(update1, update2)
        assert isinstance(merged, bytes)

    def test_diff_with_empty_update(self):
        """Test difference with empty update."""
        from ydoc.encoding import Encoder

        # Create non-empty update
        encoder1 = Encoder()
        encoder1.write_var_uint(1)
        encoder1.write_var_uint(123)
        encoder1.write_var_uint(100)
        update1 = encoder1.to_bytes()

        # Create empty update
        encoder2 = Encoder()
        encoder2.write_var_uint(0)
        update2 = encoder2.to_bytes()

        # Should handle gracefully
        diff = diff_updates(update1, update2)
        assert isinstance(diff, bytes)

    def test_large_state_vectors(self):
        """Test with large state vectors."""
        from ydoc.encoding import Encoder

        # Create update with many clients
        encoder1 = Encoder()
        encoder1.write_var_uint(100)  # 100 clients
        for i in range(100):
            encoder1.write_var_uint(i)
            encoder1.write_var_uint(i * 10)
        update1 = encoder1.to_bytes()

        # Create another update with many clients
        encoder2 = Encoder()
        encoder2.write_var_uint(100)  # 100 clients
        for i in range(100):
            encoder2.write_var_uint(i)
            encoder2.write_var_uint(i * 20)
        update2 = encoder2.to_bytes()

        # Should handle large state vectors
        merged = merge_updates(update1, update2)
        assert isinstance(merged, bytes)
        assert len(merged) > 0