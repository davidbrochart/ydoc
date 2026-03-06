"""
Tests for the awareness system
"""

import pytest
from ydoc import Doc, Awareness, AwarenessClient


def test_awareness_initialization():
    """Test awareness system initialization."""
    doc = Doc()
    awareness = doc.get_awareness()
    
    assert isinstance(awareness, Awareness)
    assert awareness.doc == doc
    assert len(awareness.get_states()) == 1  # Local client
    
    # Check local client
    local_state = awareness.get_local_state()
    assert local_state['client_id'] == doc.client_id
    assert 'user' in local_state
    assert 'cursor' in local_state


def test_client_state_management():
    """Test client state management."""
    doc = Doc()
    awareness = doc.get_awareness()
    
    # Test setting user info
    awareness.set_local_user("Test User", "#FF5733")
    local_state = awareness.get_local_state()
    assert local_state['user']['name'] == "Test User"
    assert local_state['user']['color'] == "#FF5733"
    
    # Test setting cursor
    awareness.set_local_cursor(42)
    local_state = awareness.get_local_state()
    assert local_state['cursor']['position'] == 42
    assert local_state['cursor']['selection']['anchor'] == 42
    assert local_state['cursor']['selection']['head'] == 42
    
    # Test setting cursor with selection
    awareness.set_local_cursor(100, {'anchor': 90, 'head': 110})
    local_state = awareness.get_local_state()
    assert local_state['cursor']['position'] == 100
    assert local_state['cursor']['selection']['anchor'] == 90
    assert local_state['cursor']['selection']['head'] == 110


def test_remote_client_management():
    """Test adding and removing remote clients."""
    doc = Doc()
    awareness = doc.get_awareness()
    
    # Add a remote client
    remote_client = AwarenessClient(999)
    remote_client.set_user("Remote User", "#3357FF")
    remote_client.set_cursor(200)
    
    awareness.update_client(999, remote_client.to_dict())
    
    states = awareness.get_states()
    assert len(states) == 2  # Local + remote
    
    remote_state = states[999]
    assert remote_state['user']['name'] == "Remote User"
    assert remote_state['cursor']['position'] == 200
    
    # Remove remote client
    awareness.remove_client(999)
    states = awareness.get_states()
    assert len(states) == 1  # Only local remains


def test_awareness_events():
    """Test awareness event emission."""
    doc = Doc()
    awareness = doc.get_awareness()
    
    events_caught = []
    
    def handle_event(event_type, data):
        events_caught.append((event_type, data))
    
    # Test various events
    awareness.on('change', lambda data: handle_event('change', data))
    awareness.on('update', lambda data: handle_event('update', data))
    awareness.on('remove', lambda data: handle_event('remove', data))
    awareness.on('cursor-update', lambda data: handle_event('cursor-update', data))
    
    # These should trigger events
    awareness.set_local_user("Test", "#000000")
    awareness.set_local_cursor(50)
    
    # Add and remove remote client
    awareness.update_client(123, {'user': {'name': 'Remote'}, 'cursor': {'position': 100}})
    awareness.remove_client(123)
    
    assert len(events_caught) > 0
    
    # Clean up
    awareness.remove_all_listeners()


def test_encoding_decoding():
    """Test awareness state encoding and decoding."""
    doc = Doc()
    awareness = doc.get_awareness()
    
    # Set up some state
    awareness.set_local_user("Test User", "#123456")
    awareness.set_local_cursor(50)
    awareness.update_client(123, {
        'user': {'name': 'Remote', 'color': '#654321'},
        'cursor': {'position': 75}
    })
    
    # Encode
    encoded = awareness.encode_awareness_update()
    assert len(encoded) > 0
    
    # Decode into new awareness instance
    doc2 = Doc()
    awareness2 = doc2.get_awareness()
    awareness2.apply_awareness_update(encoded)
    
    states2 = awareness2.get_states()
    assert len(states2) >= 1  # At least local client
    
    # Check that remote client was added
    remote_state = states2.get(123)
    if remote_state:
        assert remote_state['user']['name'] == 'Remote'
        assert remote_state['cursor']['position'] == 75


def test_doc_convenience_methods():
    """Test Doc class convenience methods for awareness."""
    doc = Doc()
    
    # Test convenience methods
    doc.set_user("Convenience User", "#ABCDEF")
    doc.set_cursor(300)
    
    states = doc.get_awareness_states()
    assert len(states) == 1
    
    local_state = states[doc.client_id]
    assert local_state['user']['name'] == "Convenience User"
    assert local_state['cursor']['position'] == 300


def test_awareness_client_class():
    """Test AwarenessClient class functionality."""
    client = AwarenessClient(42)
    
    # Test initial state
    assert client.client_id == 42
    assert client.cursor is None
    assert client.user == {}
    assert client.metadata == {}
    
    # Test setting values
    client.set_user("Test User", "#FF0000")
    assert client.user['name'] == "Test User"
    assert client.user['color'] == "#FF0000"
    
    client.set_cursor(100)
    assert client.cursor['position'] == 100
    
    client.set_metadata("custom_key", "custom_value")
    assert client.metadata['custom_key'] == "custom_value"
    
    # Test serialization
    data = client.to_dict()
    assert data['client_id'] == 42
    assert data['user']['name'] == "Test User"
    assert data['cursor']['position'] == 100
    assert data['metadata']['custom_key'] == "custom_value"
    
    # Test deserialization
    client2 = AwarenessClient.from_dict(data)
    assert client2.client_id == 42
    assert client2.user == client.user
    assert client2.cursor == client.cursor
    assert client2.metadata == client.metadata


def test_observable_patterns():
    """Test awareness observable patterns."""
    doc = Doc()
    awareness = doc.get_awareness()
    
    # Test has_listeners
    assert not awareness.has_listeners('change')
    
    # Add listener
    def dummy_listener(data): pass
    awareness.on('change', dummy_listener)
    assert awareness.has_listeners('change')
    
    # Test once
    once_called = []
    def once_listener(data):
        once_called.append(data)
    
    awareness.once('update', once_listener)
    awareness.emit('update', {'test': 'data'})
    awareness.emit('update', {'test': 'data2'})
    
    assert len(once_called) == 1
    
    # Test remove_all_listeners
    awareness.remove_all_listeners()
    assert not awareness.has_listeners('change')


if __name__ == "__main__":
    pytest.main([__file__])