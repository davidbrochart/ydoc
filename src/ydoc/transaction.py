"""
Transaction system for YDoc CRDT operations.
"""

from typing import Callable, Set, Any
from .id import ID
from .types import YText


class Transaction:
    """
    Represents a transaction in the YDoc system.
    Transactions bundle multiple operations and ensure atomicity.
    """

    def __init__(self, doc: "Doc"):
        self.doc = doc
        self.before_state = doc.store.get_state_vector().copy()
        self.after_state = {}
        self.delete_set: Set[ID] = set()
        self.meta: dict = {}
        self.origin: Any = None

        # Track changes made during this transaction
        self.changed: Set["AbstractStruct"] = set()
        self.changed_parent_types: Set["YType"] = set()

        # For subdocument handling
        self.subdocs_added: Set["Doc"] = set()
        self.subdocs_removed: Set["Doc"] = set()
        self.subdocs_loaded: Set["Doc"] = set()


class TransactionContext:
    """
    Context manager for handling transactions.
    """

    def __init__(self, doc: "Doc", origin: Any = None):
        self.doc = doc
        self.origin = origin
        self.transaction: Transaction | None = None

    def __enter__(self):
        # Start transaction
        self.transaction = Transaction(self.doc)
        self.transaction.origin = self.origin
        self.doc._transaction = self.transaction

        # Capture before state for undo manager
        self._capture_before_state_for_undo()

        return self.transaction

    def _capture_before_state_for_undo(self) -> None:
        """Capture the state before transaction for undo manager."""
        if hasattr(self.doc, "_undo_manager"):
            undo_manager = self.doc._undo_manager
            before_state = {}
            for ytype in self.doc.share.values():
                if isinstance(ytype, YText):
                    before_state[id(ytype)] = ytype.to_string()
            self.transaction._undo_before_state = before_state

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Commit or rollback transaction
        if exc_type is None:
            # Commit
            self._commit()
        else:
            # Rollback
            self._rollback()

        self.doc._transaction = None
        return False

    def _commit(self):
        if self.transaction:
            # Update the after state
            self.transaction.after_state = self.doc.store.get_state_vector().copy()

            # Apply deletions
            for item_id in self.transaction.delete_set:
                self.doc.store.mark_deleted(item_id)

            # Clean up
            self.doc._transaction_cleanups.append(self.transaction)

            # Emit transaction events
            self.doc.emit("beforeObserverCalls", self.transaction, self.doc)
            self.doc.emit("afterTransaction", self.transaction, self.doc)

            # Notify after transaction handlers
            self.doc._notify_after_transaction_handlers(self.transaction)

    def _rollback(self):
        # TODO: Implement proper rollback logic
        pass


def transact(doc: "Doc", f: Callable, origin: Any = None) -> Any:
    """
    Execute a function within a transaction context.
    """
    with TransactionContext(doc, origin) as transaction:
        return f(transaction)


# Import these after defining the classes to avoid circular imports
from .struct_store import AbstractStruct

# Forward reference for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .doc import Doc
