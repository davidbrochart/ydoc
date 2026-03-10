"""
Tests for the transaction system
"""

import pytest
from ydoc import Doc, Transaction, TransactionContext, transact, create_id, Item


def test_transaction_creation():
    """Test transaction creation."""
    doc = Doc()
    transaction = Transaction(doc)

    assert transaction.doc is doc
    assert transaction.before_state == {}
    assert transaction.after_state == {}
    assert transaction.delete_set == set()
    assert transaction.origin is None


def test_transaction_context():
    """Test transaction context manager."""
    doc = Doc()

    with TransactionContext(doc) as transaction:
        assert doc._transaction is transaction
        assert isinstance(transaction, Transaction)

    # After context, transaction should be cleared
    assert doc._transaction is None


def test_transaction_commit():
    """Test transaction commit."""
    doc = Doc()

    # Add an item to delete
    item_id = create_id(1, 10)
    item = Item(id=item_id, content=["test"])
    doc.store.add_struct(item)

    def transaction_func(txn):
        txn.delete_set.add(item_id)
        return "success"

    result = transact(doc, transaction_func)

    assert result == "success"
    assert item_id in doc.store.deleted_set
    assert item.deleted == True


def test_transaction_with_origin():
    """Test transaction with origin."""
    doc = Doc()

    def transaction_func(txn):
        assert txn.origin == "test_origin"
        return "done"

    result = transact(doc, transaction_func, origin="test_origin")
    assert result == "done"


def test_nested_transactions():
    """Test that nested transactions work correctly."""
    doc = Doc()

    def outer_txn(txn):
        assert doc._transaction is txn

        def inner_txn(txn2):
            assert doc._transaction is txn2
            assert txn2 is not txn
            return "inner"

        result = transact(doc, inner_txn)
        assert result == "inner"
        return "outer"

    result = transact(doc, outer_txn)
    assert result == "outer"
    assert doc._transaction is None


def test_transaction_state_tracking():
    """Test that transaction tracks state correctly."""
    doc = Doc()

    # Add some items to have non-empty state
    item1 = Item(id=create_id(1, 10), content=["item1"])
    item2 = Item(id=create_id(2, 5), content=["item2"])
    doc.store.add_struct(item1)
    doc.store.add_struct(item2)

    initial_state = doc.store.get_state_vector()

    def transaction_func(txn):
        assert txn.before_state == initial_state
        # State should be copied, not referenced
        txn.before_state[999] = 999
        assert 999 not in initial_state
        return "ok"

    result = transact(doc, transaction_func)
    assert result == "ok"


def test_transaction_cleanup():
    """Test that transactions are properly cleaned up."""
    doc = Doc()

    assert len(doc._transaction_cleanups) == 0

    def transaction_func(txn):
        return "test"

    transact(doc, transaction_func)

    assert len(doc._transaction_cleanups) == 1
    assert isinstance(doc._transaction_cleanups[0], Transaction)


def test_transaction_error_handling():
    """Test that transactions handle errors correctly."""
    doc = Doc()

    def failing_transaction(txn):
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        transact(doc, failing_transaction)

    # Transaction should be cleaned up even after error
    assert doc._transaction is None


if __name__ == "__main__":
    pytest.main([__file__])
