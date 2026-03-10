"""
YEvent implementation for YDoc - represents changes on YTypes.
"""

from typing import Set, Any, Dict


class YEvent:
    """
    YEvent describes the changes on a YType.
    """

    def __init__(
        self, target: "YType", transaction: "Transaction", subs: Set[Any] | None = None
    ):
        """
        Initialize a YEvent.

        Args:
            target: The changed type
            transaction: The transaction that triggered this event
            subs: Set of keys that changed (None for child list changes)
        """
        self.target = target
        self.current_target = target
        self.transaction = transaction

        # Track what changed
        self.child_list_changed = False
        self.keys_changed: Set[str] = set()

        if subs:
            for sub in subs:
                if sub is None:
                    self.child_list_changed = True
                else:
                    self.keys_changed.add(sub)

        # Cache for delta computations
        self._delta = None
        self._delta_deep = None

    def deletes(self, struct: "AbstractStruct") -> bool:
        """
        Check if a struct is deleted by this event.

        Args:
            struct: The struct to check

        Returns:
            True if the struct was deleted by this event
        """
        return struct.id in self.transaction.delete_set

    def adds(self, struct: "AbstractStruct") -> bool:
        """
        Check if a struct is added by this event.

        Args:
            struct: The struct to check

        Returns:
            True if the struct was added by this event
        """
        # Check if the struct was inserted in this transaction
        client_structs = self.transaction.doc.store.clients.get(struct.id.client, [])
        for item in client_structs:
            if item.id == struct.id and not item.deleted:
                return True
        return False

    def get_delta(self) -> Dict[str, Any]:
        """
        Compute the changes in delta format.

        Returns:
            Delta representation of the changes
        """
        if self._delta is None:
            self._delta = self._compute_delta()
        return self._delta

    def _compute_delta(self) -> Dict[str, Any]:
        """
        Compute delta representation of changes.
        Simplified version - full implementation would use proper delta format.
        """
        delta = {
            "target": str(self.target),
            "child_list_changed": self.child_list_changed,
            "keys_changed": list(self.keys_changed),
            "transaction": str(self.transaction),
        }

        # For YText, include content changes
        if hasattr(self.target, "_content"):
            delta["content"] = self.target.to_string()

        return delta

    @property
    def delta(self) -> Dict[str, Any]:
        """Get the delta representation of changes."""
        return self.get_delta()

    def __str__(self) -> str:
        return f"YEvent(target={self.target}, child_list_changed={self.child_list_changed}, keys_changed={list(self.keys_changed)})"

    def __repr__(self) -> str:
        return self.__str__()
