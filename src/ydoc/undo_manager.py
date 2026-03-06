"""
UndoManager implementation for YDoc - enables undo/redo functionality
"""

import time
from typing import Dict, List, Set, Any, Callable
from .id import ID
from .struct_store import Item
from .types import YText


class StackItem:
    """
    Represents a single undo/redo operation on the stack.
    Stores the changes made in a transaction.
    """

    def __init__(self) -> None:
        self.inserted_items: List[Item] = []
        self.deleted_items: List[Item] = []
        self.meta: Dict[str, Any] = {}
        self.timestamp: float = time.time()


class UndoManager:
    """
    Manages undo/redo functionality for YDoc documents.
    Tracks changes and allows reverting or reapplying them.
    """

    def __init__(self, doc: 'Doc', 
                 capture_timeout: float = 0.5,
                 capture_transaction: Callable[['Transaction'], bool] | None = None,
                 tracked_origins: Set[Any] | None = None) -> None:
        """
        Initialize UndoManager.

        Args:
            doc: The document to manage undo/redo for
            capture_timeout: Time in seconds to merge consecutive changes into one undo step
            capture_transaction: Function to determine if a transaction should be captured
            tracked_origins: Set of origins that should be tracked for undo/redo
        """
        self.doc = doc
        self.capture_timeout = capture_timeout
        self.capture_transaction = capture_transaction or (lambda txn: True)
        self.tracked_origins = tracked_origins or {None, self}

        # Undo/redo stacks
        self.undo_stack: List[StackItem] = []
        self.redo_stack: List[StackItem] = []

        # State tracking
        self.undoing = False
        self.redoing = False
        self.last_change_time = 0.0
        self.current_stack_item: StackItem | None = None

        # Register event handlers
        self.doc._add_after_transaction_handler(self._after_transaction_handler)

    def _after_transaction_handler(self, transaction: 'Transaction') -> None:
        """Handle transactions to capture undo/redo information."""
        # Check if we should capture this transaction
        if not self._should_capture_transaction(transaction):
            return

        # Determine which stack to use
        if self.undoing:
            stack = self.redo_stack
        elif self.redoing:
            stack = self.undo_stack
        else:
            stack = self.undo_stack
            # Clear redo stack when making new changes
            self.redo_stack.clear()

        # Create or merge stack items
        current_time = time.time()

        # Get the before state from transaction metadata (set by before_transaction_handler)
        before_state = getattr(transaction, '_undo_before_state', {})

        if (self.last_change_time > 0 and 
            current_time - self.last_change_time < self.capture_timeout and
            stack and not self.undoing and not self.redoing):
            # Merge with previous stack item
            stack_item = stack[-1]
            # Store after state
            self._capture_current_state(transaction, stack_item, is_after_state=True)
        else:
            # Create new stack item
            stack_item = StackItem()
            # Store before state (from transaction metadata)
            for ytype_id, content in before_state.items():
                stack_item.meta[f'before_text_content_{ytype_id}'] = content
            # Store after state
            self._capture_current_state(transaction, stack_item, is_after_state=True)
            stack.append(stack_item)

        # Update timestamp
        if not self.undoing and not self.redoing:
            self.last_change_time = current_time

    def _capture_current_state(self, transaction: 'Transaction', stack_item: StackItem, is_after_state: bool) -> None:
        """Capture the current state of YText types."""
        prefix = 'after_' if is_after_state else 'before_'

        for ytype in transaction.doc.share.values():
            if isinstance(ytype, YText):
                key = f'{prefix}text_content_{id(ytype)}'
                stack_item.meta[key] = ytype.to_string()

    def _should_capture_transaction(self, transaction: 'Transaction') -> bool:
        """Determine if a transaction should be captured for undo/redo."""
        # Check if transaction should be captured based on filter
        if not self.capture_transaction(transaction):
            return False

        # Check if origin is tracked
        origin = transaction.origin
        if origin is not None and origin not in self.tracked_origins:
            # Check if origin's constructor is tracked
            if not any(tracked_origin == origin.__class__ for tracked_origin in self.tracked_origins 
                       if hasattr(tracked_origin, '__class__') and hasattr(origin, '__class__')):
                return False

        return True

    def _capture_transaction_changes(self, transaction: 'Transaction', stack_item: StackItem) -> None:
        """Capture the changes made in a transaction."""
        # For now, we'll use a simplified approach that works with the current YDoc architecture
        # Instead of tracking Items directly, we'll track the text content changes

        # Store the current state of all YText types in the document
        for ytype in transaction.doc.share.values():
            if isinstance(ytype, YText):
                # Store a snapshot of the current content
                stack_item.meta[f'text_content_{id(ytype)}'] = ytype.to_string()

        # Also store deleted items for completeness
        for item_id in transaction.delete_set:
            item = transaction.doc.store.get_item(item_id)
            if item:
                stack_item.deleted_items.append(item)

    def undo(self) -> bool:
        """Undo the last operation.

        Returns:
            True if undo was performed, False if nothing to undo
        """
        if not self.undo_stack:
            return False

        self.undoing = True
        try:
            stack_item = self.undo_stack.pop()
            self._apply_stack_item(stack_item, is_undo=True)
            self.redo_stack.append(stack_item)
            return True
        finally:
            self.undoing = False

    def redo(self) -> bool:
        """Redo the last undone operation.

        Returns:
            True if redo was performed, False if nothing to redo
        """
        if not self.redo_stack:
            return False

        self.redoing = True
        try:
            stack_item = self.redo_stack.pop()
            self._apply_stack_item(stack_item, is_undo=False)
            self.undo_stack.append(stack_item)
            return True
        finally:
            self.redoing = False

    def _apply_stack_item(self, stack_item: StackItem, is_undo: bool) -> None:
        """Apply a stack item (undo or redo)."""
        def apply_changes(transaction: 'Transaction') -> None:
            # For now, we'll use a simplified approach that works with YText
            # In a full implementation, this would work with Items directly

            # Find all text states in metadata
            before_states = {}
            after_states = {}
            for key, value in stack_item.meta.items():
                if key.startswith('before_text_content_'):
                    ytype_id = int(key[len('before_text_content_'):])
                    before_states[ytype_id] = value
                elif key.startswith('after_text_content_'):
                    ytype_id = int(key[len('after_text_content_'):])
                    after_states[ytype_id] = value

            # Apply changes to YText types
            for ytype in transaction.doc.share.values():
                if isinstance(ytype, YText):
                    ytype_id = id(ytype)

                    if is_undo:
                        # Undo: restore to before state
                        if ytype_id in before_states:
                            ytype._content = list(before_states[ytype_id])
                    else:
                        # Redo: restore to after state
                        if ytype_id in after_states:
                            ytype._content = list(after_states[ytype_id])

        # Perform changes in a transaction
        self.doc.transact(apply_changes)

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self.redo_stack) > 0

    def clear(self, clear_undo: bool = True, clear_redo: bool = True) -> None:
        """Clear undo/redo stacks."""
        if clear_undo:
            self.undo_stack.clear()
        if clear_redo:
            self.redo_stack.clear()

    def stop_capturing(self) -> None:
        """Stop merging subsequent changes into the current undo step."""
        self.last_change_time = 0.0

    def destroy(self) -> None:
        """Clean up the undo manager."""
        # Remove event handlers
        if hasattr(self.doc, '_remove_after_transaction_handler'):
            self.doc._remove_after_transaction_handler(self._after_transaction_handler)


# Add methods to Doc class for undo manager support
def _add_undo_support_to_doc() -> None:
    """Monkey-patch Doc class to add undo manager support."""
    from .doc import Doc

    def add_undo_manager(self, capture_timeout: float = 0.5, 
                         capture_transaction: Callable[['Transaction'], bool] | None = None,
                         tracked_origins: Set[Any] | None = None) -> 'UndoManager':
        """Add an undo manager to this document."""
        undo_manager = UndoManager(self, capture_timeout, capture_transaction, tracked_origins)
        self._undo_manager = undo_manager
        return undo_manager

    def get_undo_manager(self) -> 'UndoManager | None':
        """Get the undo manager for this document."""
        return getattr(self, '_undo_manager', None)

    def undo(self) -> bool:
        """Undo the last operation."""
        undo_manager = self.get_undo_manager()
        return undo_manager.undo() if undo_manager else False

    def redo(self) -> bool:
        """Redo the last undone operation."""
        undo_manager = self.get_undo_manager()
        return undo_manager.redo() if undo_manager else False

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        undo_manager = self.get_undo_manager()
        return undo_manager.can_undo() if undo_manager else False

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        undo_manager = self.get_undo_manager()
        return undo_manager.can_redo() if undo_manager else False

    # Add methods to Doc class
    Doc.add_undo_manager = add_undo_manager
    Doc.get_undo_manager = get_undo_manager
    Doc.undo = undo
    Doc.redo = redo
    Doc.can_undo = can_undo
    Doc.can_redo = can_redo


# Initialize undo support when module is imported
_add_undo_support_to_doc()