"""
Basic encoding utilities for YDoc - inspired by lib0 encoding
"""

import struct
from typing import Any, List, Tuple


def write_var_uint(encoder: bytearray, value: int) -> None:
    """Write a variable-length unsigned integer (LEB128)."""
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            byte |= 0x80
        encoder.append(byte)
        if value == 0:
            break


def read_var_uint(decoder_data: bytes, offset: int) -> Tuple[int, int]:
    """Read a variable-length unsigned integer (LEB128)."""
    value = 0
    shift = 0
    while True:
        if offset >= len(decoder_data):
            raise ValueError("Unexpected end of data")
        byte = decoder_data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        shift += 7
        if (byte & 0x80) == 0:
            break
    return value, offset


def write_var_string(encoder: bytearray, string: str) -> None:
    """Write a string with variable-length prefix."""
    data = string.encode('utf-8')
    write_var_uint(encoder, len(data))
    encoder.extend(data)


def read_var_string(decoder_data: bytes, offset: int) -> Tuple[str, int]:
    """Read a string with variable-length prefix."""
    length, offset = read_var_uint(decoder_data, offset)
    if offset + length > len(decoder_data):
        raise ValueError("String data exceeds available bytes")
    string_data = decoder_data[offset:offset + length]
    return string_data.decode('utf-8'), offset + length


def write_uint8(encoder: bytearray, value: int) -> None:
    """Write an 8-bit unsigned integer."""
    if value < 0 or value > 255:
        raise ValueError("Value out of range for uint8")
    encoder.append(value)


def read_uint8(decoder_data: bytes, offset: int) -> Tuple[int, int]:
    """Read an 8-bit unsigned integer."""
    if offset >= len(decoder_data):
        raise ValueError("Unexpected end of data")
    return decoder_data[offset], offset + 1


def write_var_uint8_array(encoder: bytearray, data: bytes) -> None:
    """Write a byte array with variable-length prefix."""
    write_var_uint(encoder, len(data))
    encoder.extend(data)


def read_var_uint8_array(decoder_data: bytes, offset: int) -> Tuple[bytes, int]:
    """Read a byte array with variable-length prefix."""
    length, offset = read_var_uint(decoder_data, offset)
    if offset + length > len(decoder_data):
        raise ValueError("Array data exceeds available bytes")
    return decoder_data[offset:offset + length], offset + length


class Encoder:
    """Basic encoder for binary data."""

    def __init__(self):
        self.buffer = bytearray()

    def write_var_uint(self, value: int) -> None:
        """Write variable-length unsigned integer."""
        write_var_uint(self.buffer, value)

    def write_var_string(self, string: str) -> None:
        """Write variable-length string."""
        write_var_string(self.buffer, string)

    def write_uint8(self, value: int) -> None:
        """Write 8-bit unsigned integer."""
        write_uint8(self.buffer, value)

    def write_var_uint8_array(self, data: bytes) -> None:
        """Write variable-length byte array."""
        write_var_uint8_array(self.buffer, data)

    def to_bytes(self) -> bytes:
        """Get the encoded bytes."""
        return bytes(self.buffer)

    def reset(self) -> None:
        """Reset the encoder."""
        self.buffer = bytearray()


class Decoder:
    """Basic decoder for binary data."""

    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def read_var_uint(self) -> int:
        """Read variable-length unsigned integer."""
        value, self.offset = read_var_uint(self.data, self.offset)
        return value

    def read_var_string(self) -> str:
        """Read variable-length string."""
        string, self.offset = read_var_string(self.data, self.offset)
        return string

    def read_uint8(self) -> int:
        """Read 8-bit unsigned integer."""
        value, self.offset = read_uint8(self.data, self.offset)
        return value

    def read_var_uint8_array(self) -> bytes:
        """Read variable-length byte array."""
        data, self.offset = read_var_uint8_array(self.data, self.offset)
        return data

    def has_more(self) -> bool:
        """Check if there's more data to read."""
        return self.offset < len(self.data)


# Basic any encoding/decoding (simplified version)
def write_any(encoder: Encoder, value: Any) -> None:
    """Write any value using a simple type system."""
    if value is None:
        encoder.write_uint8(0)  # null
    elif isinstance(value, bool):
        encoder.write_uint8(1)  # boolean
        encoder.write_uint8(1 if value else 0)
    elif isinstance(value, int):
        encoder.write_uint8(2)  # integer
        encoder.write_var_uint(value)
    elif isinstance(value, float):
        encoder.write_uint8(3)  # float
        # Convert float to bytes
        encoder.write_var_uint(struct.unpack('>Q', struct.pack('>d', value))[0])
    elif isinstance(value, str):
        encoder.write_uint8(4)  # string
        encoder.write_var_string(value)
    elif isinstance(value, list):
        encoder.write_uint8(5)  # array
        encoder.write_var_uint(len(value))
        for item in value:
            write_any(encoder, item)
    elif isinstance(value, dict):
        encoder.write_uint8(6)  # object
        encoder.write_var_uint(len(value))
        for key, val in value.items():
            encoder.write_var_string(key)
            write_any(encoder, val)
    elif isinstance(value, bytes):
        encoder.write_uint8(7)  # binary
        encoder.write_var_uint8_array(value)
    else:
        raise ValueError(f"Unsupported type for encoding: {type(value)}")


def read_any(decoder: Decoder) -> Any:
    """Read any value using a simple type system."""
    type_byte = decoder.read_uint8()

    if type_byte == 0:  # null
        return None
    elif type_byte == 1:  # boolean
        return decoder.read_uint8() == 1
    elif type_byte == 2:  # integer
        return decoder.read_var_uint()
    elif type_byte == 3:  # float
        # Convert bytes back to float
        float_bits = decoder.read_var_uint()
        return struct.unpack('>d', struct.pack('>Q', float_bits))[0]
    elif type_byte == 4:  # string
        return decoder.read_var_string()
    elif type_byte == 5:  # array
        length = decoder.read_var_uint()
        return [read_any(decoder) for _ in range(length)]
    elif type_byte == 6:  # object
        length = decoder.read_var_uint()
        result = {}
        for _ in range(length):
            key = decoder.read_var_string()
            result[key] = read_any(decoder)
        return result
    elif type_byte == 7:  # binary
        return decoder.read_var_uint8_array()
    else:
        raise ValueError(f"Unknown type byte: {type_byte}")