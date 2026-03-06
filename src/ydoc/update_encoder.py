"""
UpdateEncoder implementation for YDoc - binary encoding of updates
"""

from typing import Dict, List, Any
from .encoding import Encoder, write_var_uint, write_uint8
from .id import ID


class UpdateEncoderV1:
    """Version 1 update encoder - basic implementation."""

    def __init__(self):
        self.rest_encoder = Encoder()

    def to_bytes(self) -> bytes:
        """Get the encoded update as bytes."""
        return self.rest_encoder.to_bytes()

    def write_left_id(self, id: ID) -> None:
        """Write a left ID (client + clock)."""
        write_var_uint(self.rest_encoder.buffer, id.client)
        write_var_uint(self.rest_encoder.buffer, id.clock)

    def write_right_id(self, id: ID) -> None:
        """Write a right ID (client + clock)."""
        write_var_uint(self.rest_encoder.buffer, id.client)
        write_var_uint(self.rest_encoder.buffer, id.clock)

    def write_client(self, client: int) -> None:
        """Write a client ID."""
        write_var_uint(self.rest_encoder.buffer, client)

    def write_info(self, info: int) -> None:
        """Write info byte (8-bit unsigned)."""
        write_uint8(self.rest_encoder.buffer, info)

    def write_string(self, string: str) -> None:
        """Write a string."""
        self.rest_encoder.write_var_string(string)

    def write_parent_info(self, is_y_key: bool) -> None:
        """Write parent info (0 or 1)."""
        write_var_uint(self.rest_encoder.buffer, 1 if is_y_key else 0)

    def write_type_ref(self, info: int) -> None:
        """Write type reference."""
        write_var_uint(self.rest_encoder.buffer, info)

    def write_len(self, length: int) -> None:
        """Write length."""
        write_var_uint(self.rest_encoder.buffer, length)

    def write_any(self, value: Any) -> None:
        """Write any value."""
        from .encoding import write_any
        write_any(self.rest_encoder, value)

    def write_buf(self, buf: bytes) -> None:
        """Write binary data."""
        self.rest_encoder.write_var_uint8_array(buf)

    def write_json(self, value: Any) -> None:
        """Write JSON (legacy - uses any encoding)."""
        self.write_any(value)

    def write_key(self, key: str) -> None:
        """Write a key."""
        self.rest_encoder.write_var_string(key)


class UpdateEncoderV2:
    """Version 2 update encoder - optimized with RLE encoding."""

    def __init__(self):
        self.rest_encoder = Encoder()
        self.key_map: Dict[str, int] = {}
        self.key_clock = 0
        # For V2, we'll use simpler encoding without full RLE optimization
        # This can be enhanced later

    def to_bytes(self) -> bytes:
        """Get the encoded update as bytes."""
        # For V2, we need to encode the key map and other optimizations
        # This is a simplified version
        main_encoder = Encoder()
        main_encoder.write_var_uint(0)  # Feature flag

        # Encode key map (simplified - just write the rest encoder for now)
        main_encoder.write_var_uint8_array(self.rest_encoder.to_bytes())
        return main_encoder.to_bytes()

    def write_left_id(self, id: ID) -> None:
        """Write a left ID (client + clock)."""
        write_var_uint(self.rest_encoder.buffer, id.client)
        write_var_uint(self.rest_encoder.buffer, id.clock)

    def write_right_id(self, id: ID) -> None:
        """Write a right ID (client + clock)."""
        write_var_uint(self.rest_encoder.buffer, id.client)
        write_var_uint(self.rest_encoder.buffer, id.clock)

    def write_client(self, client: int) -> None:
        """Write a client ID."""
        write_var_uint(self.rest_encoder.buffer, client)

    def write_info(self, info: int) -> None:
        """Write info byte (8-bit unsigned)."""
        write_uint8(self.rest_encoder.buffer, info)

    def write_string(self, string: str) -> None:
        """Write a string."""
        self.rest_encoder.write_var_string(string)

    def write_parent_info(self, is_y_key: bool) -> None:
        """Write parent info (0 or 1)."""
        write_var_uint(self.rest_encoder.buffer, 1 if is_y_key else 0)

    def write_type_ref(self, info: int) -> None:
        """Write type reference."""
        write_var_uint(self.rest_encoder.buffer, info)

    def write_len(self, length: int) -> None:
        """Write length."""
        write_var_uint(self.rest_encoder.buffer, length)

    def write_any(self, value: Any) -> None:
        """Write any value."""
        from .encoding import write_any
        write_any(self.rest_encoder, value)

    def write_buf(self, buf: bytes) -> None:
        """Write binary data."""
        self.rest_encoder.write_var_uint8_array(buf)

    def write_json(self, value: Any) -> None:
        """Write JSON (uses any encoding)."""
        self.write_any(value)

    def write_key(self, key: str) -> None:
        """Write a key with potential optimization."""
        if key in self.key_map:
            # Use existing key reference
            write_var_uint(self.rest_encoder.buffer, self.key_map[key])
        else:
            # Add new key to map
            self.key_map[key] = self.key_clock
            write_var_uint(self.rest_encoder.buffer, self.key_clock)
            self.rest_encoder.write_var_string(key)
            self.key_clock += 1