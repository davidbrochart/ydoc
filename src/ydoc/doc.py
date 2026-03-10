"""
Core Document class for YDoc - the main CRDT document container.
"""

import random
from typing import Any, Dict, Set, Callable
from .struct_store import StructStore
from .transaction import transact
from .types import create_y_type
from .observable import Observable


class Doc(Observable):
    """
    A YDoc instance handles the state of shared data.
    This is the main container for CRDT operations.
    """

    def __init__(
        self,
        guid: str | None = None,
        collection_id: str | None = None,
        gc: bool = True,
        gc_filter: Callable | None = None,
        meta: Any = None,
        auto_load: bool = False,
        should_load: bool = True,
        is_suggestion_doc: bool = False,
    ):

        # Initialize observable first
        Observable.__init__(self)

        self.gc = gc
        self.gc_filter = gc_filter or (lambda x: True)
        self.client_id = random.randint(0, 0xFFFFFFFF)  # 32-bit client ID
        self.guid = guid or self._generate_guid()
        self.collection_id = collection_id
        self.is_suggestion_doc = is_suggestion_doc
        self.cleanup_formatting = not is_suggestion_doc

        # Shared data types
        self.share: Dict[str, Any] = {}
        self.store = StructStore()
        self._transaction = None
        self._transaction_cleanups = []
        self.subdocs: Set["Doc"] = set()
        self._item = None  # For subdocuments
        self.should_load = should_load
        self.auto_load = auto_load
        self.meta = meta
        self.is_loaded = False
        self.is_synced = False
        self.is_destroyed = False

    def _generate_guid(self) -> str:
        """Generate a random GUID."""
        return f"{random.randint(0, 0xFFFFFFFF):08x}-{random.randint(0, 0xFFFF):04x}-{random.randint(0, 0xFFFF):04x}-{random.randint(0, 0xFFFFFFFF):08x}"

    def get(self, key: str = "", name: str | None = None) -> "YType":
        """
        Define a shared data type.

        Multiple calls with the same key yield the same result.
        """
        if key not in self.share:
            # Create the appropriate YType based on the name
            # Default to YText if no specific type is specified
            type_name = name or "text"
            ytype = create_y_type(type_name, key)
            ytype._integrate(self, None)  # Integrate into this document
            self.share[key] = ytype
        return self.share[key]

    def get_text(self, name: str = "text") -> "YText":
        """
        Get or create a YText shared data type.

        Yjs equivalent: doc.getText()

        Args:
            name: The key/name for the text type

        Returns:
            YText instance
        """
        return self.get(name, "text")

    def get_map(self, name: str = "map") -> "YMap":
        """
        Get or create a YMap shared data type.

        Yjs equivalent: doc.getMap()

        Args:
            name: The key/name for the map type

        Returns:
            YMap instance
        """
        return self.get(name, "map")

    def get_array(self, name: str = "array") -> "YArray":
        """
        Get or create a YArray shared data type.

        Yjs equivalent: doc.getArray()

        Args:
            name: The key/name for the array type

        Returns:
            YArray instance
        """
        return self.get(name, "array")

    def get_xml(self, name: str = "xml") -> "YXml":
        """
        Get or create a YXml shared data type.

        Yjs equivalent: doc.getXml()

        Args:
            name: The key/name for the xml type

        Returns:
            YXml instance
        """
        return self.get(name, "xml")

    def transact(self, f: Callable, origin: Any = None) -> Any:
        """
        Execute a function within a transaction.
        Changes are bundled and observers fire after the transaction completes.
        """
        return transact(self, f, origin)

    def to_json(self) -> Dict[str, Any]:
        """
        Convert the entire document to a JSON object.
        """
        return {key: value for key, value in self.share.items()}

    def destroy(self) -> None:
        """
        Clean up the document and unregister event handlers.
        """
        self.is_destroyed = True
        for subdoc in self.subdocs:
            subdoc.destroy()

        if self._item is not None:
            self._item = None

    def load(self) -> None:
        """
        Request to load data into this document if it's a subdocument.
        """
        self.should_load = True

    def _add_after_transaction_handler(
        self, handler: Callable[["Transaction"], None]
    ) -> None:
        """Add a handler to be called after transactions."""
        if not hasattr(self, "_after_transaction_handlers"):
            self._after_transaction_handlers = []
        self._after_transaction_handlers.append(handler)

    def _remove_after_transaction_handler(
        self, handler: Callable[["Transaction"], None]
    ) -> None:
        """Remove a handler from after transaction callbacks."""
        if hasattr(self, "_after_transaction_handlers"):
            if handler in self._after_transaction_handlers:
                self._after_transaction_handlers.remove(handler)

    def _notify_after_transaction_handlers(self, transaction: "Transaction") -> None:
        """Notify all after transaction handlers."""
        if hasattr(self, "_after_transaction_handlers"):
            for handler in self._after_transaction_handlers:
                handler(transaction)
