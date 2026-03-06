"""
Yjs data types implementation for YDoc.
"""

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING, Set
from .id import ID, create_id
from .struct_store import Item, AbstractStruct
from .observable import Observable
from .yevent import YEvent

if TYPE_CHECKING:
    from .doc import Doc
    from .transaction import Transaction

class YType(Observable):
    """
    Base class for all Yjs data types.
    """
    
    def __init__(self, name: str | None = None):
        super().__init__()
        self._item: Item | None = None
        self._start: Item | None = None
        self._length = 0
        self._doc: 'Doc | None' = None
        self._name = name
        self._map: Dict[str, Item] = {}
    
    def _integrate(self, doc: 'Doc', item: Item | None) -> None:
        """Integrate this type into a document."""
        self._doc = doc
        self._item = item
        
        if item is not None:
            # TODO: Proper integration logic
            pass
    
    def to_json(self) -> Any:
        """Convert this type to JSON."""
        return {"type": self._name or "unknown"}

class YText(YType):
    """
    YText represents a collaborative text type.
    This is one of the most commonly used Yjs types.
    """
    
    def __init__(self, name: str | None = None, initial_text: str = ""):
        super().__init__(name)
        self._content: List[str] = list(initial_text)
    
    def insert(self, index: int, text: str, transaction_origin: Any | None = None, origin: Any | None = None) -> None:
        """Insert text at the given index."""
        if self._doc is None:
            raise ValueError("YText must be integrated into a document first")
        
        def insert_in_transaction(txn: 'Transaction') -> None:
            # Set origin if provided
            if origin is not None:
                txn.origin = origin
            elif transaction_origin is not None:
                txn.origin = transaction_origin
            # Create new items for the inserted text
            for i, char in enumerate(text):
                # Generate a unique ID for this character
                char_id = create_id(self._doc.client_id, txn.doc.store.get_state(self._doc.client_id) + i)
                
                # Create item with the character content
                item = Item(
                    id=char_id,
                    content=[char],
                    parent=self._item,
                    parent_sub=self._name
                )
                
                # Add to store
                self._doc.store.add_struct(item)
                
                # Update our content - insert at the correct position
                self._content.insert(index + i, char)
        
        def insert_and_emit(txn: 'Transaction') -> None:
            insert_in_transaction(txn)
            # Emit change event
            event = YEvent(self, txn, {None})
            self.emit('change', event)
            self._doc.emit('change', event)
        
        self._doc.transact(insert_and_emit, transaction_origin)
    
    def delete(self, index: int, length: int, transaction_origin: Any | None = None) -> None:
        """Delete text starting at index with given length."""
        if self._doc is None:
            raise ValueError("YText must be integrated into a document first")
        
        def delete_in_transaction(txn: 'Transaction') -> None:
            # Update content - delete the specified range
            del self._content[index:index + length]
        
        self._doc.transact(delete_in_transaction, transaction_origin)
        
        # Emit change event
        if self._doc and self._doc._transaction:
            event = YEvent(self, self._doc._transaction, {None})
            self.emit('change', event)
            self._doc.emit('change', event)
    
    def to_string(self) -> str:
        """Get the current text content."""
        return ''.join(self._content)
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return self.to_string()
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __len__(self) -> int:
        return len(self._content)

class YMap(YType):
    """
    YMap represents a collaborative key-value map.
    """
    
    def __init__(self, name: str | None = None):
        super().__init__(name)
        self._map_data: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any, transaction_origin: Any | None = None) -> None:
        """Set a key-value pair in the map."""
        if self._doc is None:
            raise ValueError("YMap must be integrated into a document first")
        
        def set_in_transaction(txn: 'Transaction') -> None:
            # Create or update the item for this key
            if key in self._map:
                # Update existing item
                item = self._map[key]
                # TODO: Update item content properly
            else:
                # Create new item
                item_id = create_id(self._doc.client_id, txn.doc.store.get_state(self._doc.client_id))
                item = Item(
                    id=item_id,
                    content=[key, value],
                    parent=self._item,
                    parent_sub=key
                )
                self._doc.store.add_struct(item)
                self._map[key] = item
            
            # Update our local data
            self._map_data[key] = value
        
        self._doc.transact(set_in_transaction, transaction_origin)
    
    def get(self, key: str) -> Any | None:
        """Get a value from the map."""
        return self._map_data.get(key)
    
    def delete(self, key: str, transaction_origin: Any | None = None) -> None:
        """Delete a key from the map."""
        if self._doc is None:
            raise ValueError("YMap must be integrated into a document first")
        
        def delete_in_transaction(txn: 'Transaction') -> None:
            if key in self._map:
                item = self._map[key]
                txn.delete_set.add(item.id)
                del self._map[key]
            
            if key in self._map_data:
                del self._map_data[key]
        
        def delete_and_emit(txn: 'Transaction') -> None:
            delete_in_transaction(txn)
            # Emit change event
            event = YEvent(self, txn, {key})
            self.emit('change', event)
            self._doc.emit('change', event)
        
        self._doc.transact(delete_and_emit, transaction_origin)
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON."""
        return self._map_data.copy()
    
    def keys(self) -> List[str]:
        """Get all keys."""
        return list(self._map_data.keys())
    
    def values(self) -> List[Any]:
        """Get all values."""
        return list(self._map_data.values())
    
    def items(self) -> List[tuple[str, Any]]:
        """Get all key-value pairs."""
        return list(self._map_data.items())

class YArray(YType):
    """
    YArray represents a collaborative array.
    """
    
    def __init__(self, name: str | None = None, initial_data: List[Any] | None = None):
        super().__init__(name)
        self._array_data: List[Any] = list(initial_data or [])
    
    def insert(self, index: int, content: List[Any], transaction_origin: Any | None = None) -> None:
        """Insert elements at the given index."""
        if self._doc is None:
            raise ValueError("YArray must be integrated into a document first")
        
        def insert_in_transaction(txn: 'Transaction') -> None:
            # Insert items for each element
            for i, element in enumerate(content):
                element_id = create_id(self._doc.client_id, txn.doc.store.get_state(self._doc.client_id) + i)
                item = Item(
                    id=element_id,
                    content=[element],
                    parent=self._item
                )
                self._doc.store.add_struct(item)
            
            # Update our local array
            for element in reversed(content):
                self._array_data.insert(index, element)
        
        self._doc.transact(insert_in_transaction, transaction_origin)
    
    def push(self, content: List[Any], transaction_origin: Any | None = None) -> None:
        """Push elements to the end of the array."""
        self.insert(len(self._array_data), content, transaction_origin)
    
    def delete(self, index: int, length: int = 1, transaction_origin: Any | None = None) -> None:
        """Delete elements starting at index."""
        if self._doc is None:
            raise ValueError("YArray must be integrated into a document first")
        
        def delete_in_transaction(txn: 'Transaction') -> None:
            # In a real implementation, we'd find the actual Item IDs to delete
            # For now, just update our local array
            del self._array_data[index:index + length]
        
        self._doc.transact(delete_in_transaction, transaction_origin)
    
    def to_json(self) -> List[Any]:
        """Convert to JSON."""
        return self._array_data.copy()
    
    def __getitem__(self, index: int) -> Any:
        return self._array_data[index]
    
    def __setitem__(self, index: int, value: Any, transaction_origin: Any | None = None) -> None:
        # For simplicity, we'll delete and insert
        self.delete(index, 1, transaction_origin)
        self.insert(index, [value], transaction_origin)
    
    def __len__(self) -> int:
        return len(self._array_data)
    
    def __iter__(self):
        return iter(self._array_data)

class YXml(YType):
    """
    YXml represents collaborative XML elements.
    This is a simplified version - full XML support would be more complex.
    """
    
    def __init__(self, name: str | None = None, tag_name: str = "div"):
        super().__init__(name)
        self.tag_name = tag_name
        self.attributes: Dict[str, str] = {}
        self.children: List[Union['YXml', str]] = []
    
    def set_attribute(self, name: str, value: str, transaction_origin: Any | None = None) -> None:
        """Set an attribute on the XML element."""
        if self._doc is None:
            raise ValueError("YXml must be integrated into a document first")
        
        def set_attr_in_transaction(txn: 'Transaction') -> None:
            self.attributes[name] = value
        
        self._doc.transact(set_attr_in_transaction, transaction_origin)
    
    def insert_child(self, index: int, child: Union['YXml', str], transaction_origin: Any | None = None) -> None:
        """Insert a child element or text."""
        if self._doc is None:
            raise ValueError("YXml must be integrated into a document first")
        
        def insert_child_in_transaction(txn: 'Transaction') -> None:
            self.children.insert(index, child)
        
        self._doc.transact(insert_child_in_transaction, transaction_origin)
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON representation."""
        return {
            "tag": self.tag_name,
            "attributes": self.attributes,
            "children": [child.to_json() if hasattr(child, 'to_json') else child for child in self.children]
        }

# Utility function to create the appropriate YType
def create_y_type(type_name: str, name: str | None = None, *args, **kwargs) -> YType:
    """Create a YType instance based on the type name."""
    type_map = {
        'text': YText,
        'map': YMap,
        'array': YArray,
        'xml': YXml
    }
    
    type_class = type_map.get(type_name.lower(), YType)
    return type_class(name, *args, **kwargs)