"""
UpdateDecoder implementation for YDoc - binary decoding of updates
"""

from typing import Dict, List, Any
from .encoding import Decoder, read_var_uint, read_uint8
from .id import ID, create_id


class UpdateDecoderV1:
    """Version 1 update decoder - basic implementation."""

    def __init__(self, decoder: Decoder):
        self.rest_decoder = decoder

    def read_left_id(self) -> ID:
        """Read a left ID (client + clock)."""
        client = read_var_uint(self.rest_decoder.data, self.rest_decoder.offset)
        self.rest_decoder.offset = client[1]
        clock = read_var_uint(self.rest_decoder.data, self.rest_decoder.offset)
        self.rest_decoder.offset = clock[1]
        return create_id(client[0], clock[0])

    def read_right_id(self) -> ID:
        """Read a right ID (client + clock)."""
        client = read_var_uint(self.rest_decoder.data, self.rest_decoder.offset)
        self.rest_decoder.offset = client[1]
        clock = read_var_uint(self.rest_decoder.data, self.rest_decoder.offset)
        self.rest_decoder.offset = clock[1]
        return create_id(client[0], clock[0])

    def read_client(self) -> int:
        """Read a client ID."""
        client = read_var_uint(self.rest_decoder.data, self.rest_decoder.offset)
        self.rest_decoder.offset = client[1]
        return client[0]

    def read_info(self) -> int:
        """Read info byte (8-bit unsigned)."""
        info = read_uint8(self.rest_decoder.data, self.rest_decoder.offset)
        self.rest_decoder.offset = info[1]
        return info[0]

    def read_string(self) -> str:
        """Read a string."""
        return self.rest_decoder.read_var_string()

    def read_parent_info(self) -> bool:
        """Read parent info (0 or 1)."""
        val = read_var_uint(self.rest_decoder.data, self.rest_decoder.offset)
        self.rest_decoder.offset = val[1]
        return val[0] == 1

    def read_type_ref(self) -> int:
        """Read type reference."""
        ref = read_var_uint(self.rest_decoder.data, self.rest_decoder.offset)
        self.rest_decoder.offset = ref[1]
        return ref[0]

    def read_len(self) -> int:
        """Read length."""
        length = read_var_uint(self.rest_decoder.data, self.rest_decoder.offset)
        self.rest_decoder.offset = length[1]
        return length[0]

    def read_any(self) -> Any:
        """Read any value."""
        from .encoding import read_any
        return read_any(self.rest_decoder)

    def read_buf(self) -> bytes:
        """Read binary data."""
        return self.rest_decoder.read_var_uint8_array()

    def read_json(self) -> Any:
        """Read JSON (legacy - uses any decoding)."""
        return self.read_any()

    def read_key(self) -> str:
        """Read a key."""
        return self.rest_decoder.read_var_string()


class UpdateDecoderV2:
    """Version 2 update decoder - optimized with RLE decoding."""

    def __init__(self, decoder: Decoder):
        self.rest_decoder = decoder
        self.keys: List[str] = []

        # Read feature flag
        feature_flag = read_var_uint(decoder.data, decoder.offset)
        decoder.offset = feature_flag[1]

        # Read the main data (simplified - V2 has complex RLE encoders)
        # For now, we'll just read the rest as a single block
        self.main_data = decoder.read_var_uint8_array()
        self.main_decoder = Decoder(self.main_data)

    def read_left_id(self) -> ID:
        """Read a left ID (client + clock)."""
        client = read_var_uint(self.main_decoder.data, self.main_decoder.offset)
        self.main_decoder.offset = client[1]
        clock = read_var_uint(self.main_decoder.data, self.main_decoder.offset)
        self.main_decoder.offset = clock[1]
        return create_id(client[0], clock[0])

    def read_right_id(self) -> ID:
        """Read a right ID (client + clock)."""
        client = read_var_uint(self.main_decoder.data, self.main_decoder.offset)
        self.main_decoder.offset = client[1]
        clock = read_var_uint(self.main_decoder.data, self.main_decoder.offset)
        self.main_decoder.offset = clock[1]
        return create_id(client[0], clock[0])

    def read_client(self) -> int:
        """Read a client ID."""
        client = read_var_uint(self.main_decoder.data, self.main_decoder.offset)
        self.main_decoder.offset = client[1]
        return client[0]

    def read_info(self) -> int:
        """Read info byte (8-bit unsigned)."""
        info = read_uint8(self.main_decoder.data, self.main_decoder.offset)
        self.main_decoder.offset = info[1]
        return info[0]

    def read_string(self) -> str:
        """Read a string."""
        return self.main_decoder.read_var_string()

    def read_parent_info(self) -> bool:
        """Read parent info (0 or 1)."""
        val = read_var_uint(self.main_decoder.data, self.main_decoder.offset)
        self.main_decoder.offset = val[1]
        return val[0] == 1

    def read_type_ref(self) -> int:
        """Read type reference."""
        ref = read_var_uint(self.main_decoder.data, self.main_decoder.offset)
        self.main_decoder.offset = ref[1]
        return ref[0]

    def read_len(self) -> int:
        """Read length."""
        length = read_var_uint(self.main_decoder.data, self.main_decoder.offset)
        self.main_decoder.offset = length[1]
        return length[0]

    def read_any(self) -> Any:
        """Read any value."""
        from .encoding import read_any
        return read_any(self.main_decoder)

    def read_buf(self) -> bytes:
        """Read binary data."""
        return self.main_decoder.read_var_uint8_array()

    def read_json(self) -> Any:
        """Read JSON (uses any decoding)."""
        return self.read_any()

    def read_key(self) -> str:
        """Read a key with potential optimization."""
        key_clock = read_var_uint(self.main_decoder.data, self.main_decoder.offset)
        self.main_decoder.offset = key_clock[1]

        if key_clock[0] < len(self.keys):
            return self.keys[key_clock[0]]
        else:
            key = self.main_decoder.read_var_string()
            self.keys.append(key)
            return key