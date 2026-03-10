"""
ID system for YDoc - unique identifiers for CRDT operations.
"""


class ID:
    """
    Represents a unique identifier in Yjs CRDT system.
    Each ID consists of a client ID and a clock value.
    """

    def __init__(self, client: int, clock: int):
        self.client = client
        self.clock = clock

    def __eq__(self, other) -> bool:
        if not isinstance(other, ID):
            return False
        return self.client == other.client and self.clock == other.clock

    def __hash__(self) -> int:
        return hash((self.client, self.clock))

    def __repr__(self) -> str:
        return f"ID(client={self.client}, clock={self.clock})"

    def __lt__(self, other) -> bool:
        if not isinstance(other, ID):
            return NotImplemented
        if self.client == other.client:
            return self.clock < other.clock
        return self.client < other.client


def compare_ids(a: ID, b: ID) -> bool:
    """Compare two IDs for equality."""
    return a == b


def create_id(client: int, clock: int) -> ID:
    """Create a new ID."""
    return ID(client, clock)
