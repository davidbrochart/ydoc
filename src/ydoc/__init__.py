"""
YDoc - Python CRDT implementation inspired by Yjs
"""

from .doc import Doc
from .id import ID, create_id, compare_ids
from .struct_store import StructStore, Item, AbstractStruct, GC
from .transaction import Transaction, TransactionContext, transact
from .types import YType, YText, YMap, YArray, YXml, create_y_type
from .encoding import Encoder, Decoder, write_any, read_any
from .update_encoder import UpdateEncoderV1, UpdateEncoderV2
from .update_decoder import UpdateDecoderV1, UpdateDecoderV2
from .undo_manager import UndoManager
from .observable import Observable
from .yevent import YEvent
from .awareness import Awareness, AwarenessClient
from .update import (
    get_state_vector, get_state_update, encode_state_as_update, apply_update, apply_state_update,
    merge_updates, get_update_encoding_version, diff_updates,
    get_missing_updates
)

__all__ = [
    'Doc',
    'ID', 'create_id', 'compare_ids',
    'StructStore', 'Item', 'AbstractStruct', 'GC',
    'Transaction', 'TransactionContext', 'transact',
    'YType', 'YText', 'YMap', 'YArray', 'YXml', 'create_y_type',
    'Encoder', 'Decoder', 'write_any', 'read_any',
    'UpdateEncoderV1', 'UpdateEncoderV2',
    'UpdateDecoderV1', 'UpdateDecoderV2',
    'UndoManager',
    'Observable', 'YEvent',
    'Awareness', 'AwarenessClient',
    'get_state_vector', 'get_state_update', 'encode_state_as_update', 'apply_update', 'apply_state_update',
    'merge_updates', 'get_update_encoding_version', 'diff_updates',
    'get_missing_updates'
]

# Add Yjs-like convenience methods to Doc class for better API compatibility
def add_yjs_convenience_methods():
    """Add Yjs-like get_* methods to Doc class for API compatibility."""
    # These methods are already defined in the Doc class
    pass

__version__ = "0.1.0"