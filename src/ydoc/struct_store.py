"""
StructStore implementation - core data structure for Yjs CRDT operations.
"""

from typing import Dict, List, Set
from .id import ID

class AbstractStruct:
    """Base class for all structs in the CRDT."""
    def __init__(self, id: ID, length: int = 1):
        self.id = id
        self.length = length

class Item(AbstractStruct):
    """
    Item represents a piece of content in the document.
    This is the basic building block of Yjs CRDT.
    """
    def __init__(self, 
                 id: ID, 
                 left: 'Item | None' = None,
                 origin: ID | None = None,
                 right: 'Item | None' = None,
                 right_origin: ID | None = None,
                 parent: AbstractStruct | None = None,
                 parent_sub: str | None = None,
                 content: any = None,
                 length: int = 1):
        
        super().__init__(id, length)
        self.left = left
        self.origin = origin
        self.right = right
        self.right_origin = right_origin
        self.parent = parent
        self.parent_sub = parent_sub
        self.content = content or []
        self.deleted = False
        self.redone = None
        self.keep = False
        
        # For garbage collection
        self.info = 0
    
    def delete(self, transaction: 'Transaction') -> None:
        """Mark this item as deleted."""
        self.deleted = True
        if hasattr(transaction, 'delete_set'):
            transaction.delete_set.add(self.id)

class GC(AbstractStruct):
    """Garbage collection marker."""
    def __init__(self, id: ID):
        super().__init__(id)

class StructStore:
    """
    The main data structure that stores all the structs (Items and GCs).
    This is where the CRDT magic happens.
    """
    def __init__(self):
        # Map of client ID to list of structs
        self.clients: Dict[int, List[AbstractStruct]] = {}
        # Track deleted structs
        self.deleted_set: Set[ID] = set()
        # Pending structs for synchronization
        self.pending_structs = None
        self.pending_ds = None
    
    def get_state_vector(self) -> Dict[int, int]:
        """
        Return the state as a map of client -> clock.
        The clock refers to the next expected clock ID.
        """
        state = {}
        for client_id, structs in self.clients.items():
            if structs:
                last_struct = structs[-1]
                state[client_id] = last_struct.id.clock + last_struct.length
        return state
    
    def get_state(self, client_id: int) -> int:
        """Get the current clock for a specific client."""
        structs = self.clients.get(client_id)
        if structs is None:
            return 0
        last_struct = structs[-1]
        return last_struct.id.clock + last_struct.length
    
    def add_struct(self, struct: AbstractStruct) -> None:
        """Add a struct to the store."""
        client_id = struct.id.client
        if client_id not in self.clients:
            self.clients[client_id] = []
        
        client_structs = self.clients[client_id]
        
        # Find insertion point to maintain order
        insert_pos = 0
        for i, existing in enumerate(client_structs):
            if struct.id.clock < existing.id.clock:
                break
            insert_pos = i + 1
        
        client_structs.insert(insert_pos, struct)
    
    def get_item(self, id: ID) -> Item | None:
        """Get an item by its ID."""
        structs = self.clients.get(id.client)
        if structs is None:
            return None
        
        for struct in structs:
            if struct.id == id and isinstance(struct, Item):
                return struct
        return None
    
    def mark_deleted(self, id: ID) -> None:
        """Mark a struct as deleted."""
        self.deleted_set.add(id)
        
        # Also mark the item as deleted if it exists
        item = self.get_item(id)
        if item:
            item.deleted = True
    
    def integrity_check(self) -> bool:
        """Check the integrity of the struct store."""
        for client_id, structs in self.clients.items():
            for i in range(1, len(structs)):
                left = structs[i-1]
                right = structs[i]
                if left.id.clock + left.length != right.id.clock:
                    return False
        return True