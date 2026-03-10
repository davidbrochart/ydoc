"""
Awareness system for YDoc - tracks client presence and collaboration state.

This provides the foundation for real-time collaboration features like:
- Client presence tracking
- Cursor position sharing
- User metadata (names, colors)
- Collaboration state synchronization
"""

from typing import Dict, Any, List
from .observable import Observable
from .encoding import Encoder, Decoder, write_any, read_any


class AwarenessClient:
    """
    Represents a single client's awareness information.
    """

    def __init__(self, client_id: int):
        self.client_id = client_id
        self.cursor: Dict[str, Any] | None = None
        self.user: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    def set_cursor(
        self, position: int, selection: Dict[str, int] | None = None
    ) -> None:
        """Set cursor position and selection."""
        self.cursor = {
            "position": position,
            "selection": selection or {"anchor": position, "head": position},
        }

    def set_user(self, name: str, color: str = "#000000") -> None:
        """Set user information."""
        self.user = {"name": name, "color": color}

    def set_metadata(self, key: str, value: Any) -> None:
        """Set custom metadata."""
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "client_id": self.client_id,
            "cursor": self.cursor,
            "user": self.user,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AwarenessClient":
        """Create from dictionary."""
        client = cls(data["client_id"])
        client.cursor = data.get("cursor")
        client.user = data.get("user", {})
        client.metadata = data.get("metadata", {})
        return client


class Awareness(Observable):
    """
    Awareness system for tracking collaborative clients and their states.
    """

    def __init__(self, doc: "Doc"):
        super().__init__()
        self.doc = doc
        self.clients: Dict[int, AwarenessClient] = {}
        self.local_client: AwarenessClient | None = None
        self.last_updated: float = 0.0

        # Register with document
        self.doc._awareness = self

        # Set up local client
        self.set_local_state()

    def set_local_state(self, client_id: int | None = None) -> None:
        """Set up local client awareness state."""
        if client_id is None:
            client_id = self.doc.client_id

        self.local_client = AwarenessClient(client_id)
        self.local_client.set_user(f"User {client_id % 1000}")
        self.clients[client_id] = self.local_client

        # Emit local state change
        self.emit("change", {"added": [client_id], "updated": [], "removed": []})

    def set_local_cursor(
        self, position: int, selection: Dict[str, int] | None = None
    ) -> None:
        """Update local client's cursor position."""
        if self.local_client:
            self.local_client.set_cursor(position, selection)
            self.emit_cursor_update()

    def set_local_user(self, name: str, color: str = "#000000") -> None:
        """Update local client's user information."""
        if self.local_client:
            self.local_client.set_user(name, color)
            self.emit("update", {"client_id": self.local_client.client_id})

    def get_states(self) -> Dict[int, Dict[str, Any]]:
        """Get all client states as dictionaries."""
        return {
            client_id: client.to_dict() for client_id, client in self.clients.items()
        }

    def update_client(self, client_id: int, updates: Dict[str, Any]) -> None:
        """Update a remote client's state."""
        if client_id == self.doc.client_id:
            return  # Don't update local client from remote

        if client_id not in self.clients:
            self.clients[client_id] = AwarenessClient(client_id)

        client = self.clients[client_id]

        if "cursor" in updates:
            client.cursor = updates["cursor"]
        if "user" in updates:
            client.user = updates["user"]
        if "metadata" in updates:
            client.metadata.update(updates["metadata"])

        self.emit("update", {"client_id": client_id})

    def remove_client(self, client_id: int) -> None:
        """Remove a client from awareness."""
        if client_id in self.clients and client_id != self.doc.client_id:
            del self.clients[client_id]
            self.emit("remove", {"client_id": client_id})

    def emit_cursor_update(self) -> None:
        """Emit cursor update event."""
        if self.local_client and self.local_client.cursor:
            self.emit(
                "cursor-update",
                {
                    "client_id": self.local_client.client_id,
                    "cursor": self.local_client.cursor,
                },
            )

    def encode_awareness_update(self) -> bytes:
        """Encode awareness state as binary for network transmission."""
        encoder = Encoder()

        # Encode all client states
        states = {}
        for client_id, client in self.clients.items():
            states[str(client_id)] = client.to_dict()

        write_any(encoder, states)
        return encoder.to_bytes()

    def apply_awareness_update(self, update_data: bytes) -> None:
        """Apply awareness update from binary data."""
        decoder = Decoder(update_data)
        states = read_any(decoder)

        if not isinstance(states, dict):
            return

        current_client_ids = set(self.clients.keys())
        updated_client_ids = set()

        for client_id_str, client_data in states.items():
            try:
                client_id = int(client_id_str)
                updated_client_ids.add(client_id)
                self.update_client(client_id, client_data)
            except (ValueError, TypeError):
                continue

        # Remove clients that are no longer present
        for client_id in current_client_ids - updated_client_ids:
            if client_id != self.doc.client_id:
                self.remove_client(client_id)

    def get_local_state(self) -> Dict[str, Any]:
        """Get local client state."""
        return self.local_client.to_dict() if self.local_client else {}

    def get_remote_states(self) -> List[Dict[str, Any]]:
        """Get all remote client states."""
        return [
            client.to_dict()
            for client_id, client in self.clients.items()
            if client_id != self.doc.client_id
        ]


def add_awareness_support_to_doc():
    """Add awareness support to Doc class."""
    from .doc import Doc

    def get_awareness(self) -> "Awareness":
        """Get or create the awareness instance for this document."""
        if not hasattr(self, "_awareness"):
            self._awareness = Awareness(self)
        return self._awareness

    def set_cursor(
        self, position: int, selection: Dict[str, int] | None = None
    ) -> None:
        """Set cursor position for local client."""
        awareness = self.get_awareness()
        awareness.set_local_cursor(position, selection)

    def set_user(self, name: str, color: str = "#000000") -> None:
        """Set user information for local client."""
        awareness = self.get_awareness()
        awareness.set_local_user(name, color)

    def get_awareness_states(self) -> Dict[int, Dict[str, Any]]:
        """Get all awareness states."""
        awareness = self.get_awareness()
        return awareness.get_states()

    # Add methods to Doc class
    Doc.get_awareness = get_awareness
    Doc.set_cursor = set_cursor
    Doc.set_user = set_user
    Doc.get_awareness_states = get_awareness_states


# Initialize awareness support when module is imported
add_awareness_support_to_doc()
