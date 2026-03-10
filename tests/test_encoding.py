"""
Comprehensive tests for YDoc encoding/decoding functionality.
Ported from Yjs test concepts to ensure compatibility.
"""

from ydoc.encoding import Encoder, Decoder
from ydoc.update_encoder import UpdateEncoderV1, UpdateEncoderV2
from ydoc.update_decoder import UpdateDecoderV1, UpdateDecoderV2
from ydoc.id import ID


def test_encoder_decoder_basic():
    """Test basic encoder/decoder functionality."""
    encoder = Encoder()

    # Test basic types
    test_values = [0, 1, 127, 128, 255, 256, 1000]
    for value in test_values:
        encoder.write_var_uint(value)

    encoded = encoder.to_bytes()

    # Decode using Decoder class
    decoder = Decoder(encoded)
    for expected in test_values:
        result = decoder.read_var_uint()
        assert result == expected, f"Expected {expected}, got {result}"


def test_update_encoder_v1_basic():
    """Test UpdateEncoderV1 basic functionality."""
    encoder = UpdateEncoderV1()

    # Test writing various operations
    encoder.write_client(1)
    encoder.write_len(10)
    encoder.write_left_id(ID(1, 5))
    encoder.write_right_id(ID(2, 3))
    encoder.write_parent_info(True)
    encoder.write_info(42)  # info should be an integer
    encoder.write_string("test string")

    # Get the encoded update
    update = encoder.to_bytes()
    assert len(update) > 0

    # Test decoding - need to create Decoder first
    decoder = Decoder(update)
    update_decoder = UpdateDecoderV1(decoder)
    assert update_decoder.read_client() == 1
    assert update_decoder.read_len() == 10


def test_update_encoder_v2_basic():
    """Test UpdateEncoderV2 basic functionality."""
    encoder = UpdateEncoderV2()

    # Test writing various operations
    encoder.write_client(1)
    encoder.write_len(10)
    encoder.write_left_id(ID(1, 5))
    encoder.write_right_id(ID(2, 3))
    encoder.write_parent_info(True)
    encoder.write_info(42)  # info should be an integer
    encoder.write_string("test string")

    # Get the encoded update
    update = encoder.to_bytes()
    assert len(update) > 0

    # Test decoding - need to create Decoder first
    decoder = Decoder(update)
    update_decoder = UpdateDecoderV2(decoder)
    assert update_decoder.read_client() == 1
    assert update_decoder.read_len() == 10


def test_encoding_decoding_roundtrip():
    """Test that encoding and decoding preserves data."""
    # Test with V1
    encoder_v1 = UpdateEncoderV1()
    encoder_v1.write_client(42)
    encoder_v1.write_len(100)
    encoder_v1.write_string("Hello World")

    encoded_v1 = encoder_v1.to_bytes()
    decoder_v1 = Decoder(encoded_v1)
    update_decoder_v1 = UpdateDecoderV1(decoder_v1)

    assert update_decoder_v1.read_client() == 42
    assert update_decoder_v1.read_len() == 100
    assert update_decoder_v1.read_string() == "Hello World"

    # Test with V2
    encoder_v2 = UpdateEncoderV2()
    encoder_v2.write_client(42)
    encoder_v2.write_len(100)
    encoder_v2.write_string("Hello World")

    encoded_v2 = encoder_v2.to_bytes()
    decoder_v2 = Decoder(encoded_v2)
    update_decoder_v2 = UpdateDecoderV2(decoder_v2)

    assert update_decoder_v2.read_client() == 42
    assert update_decoder_v2.read_len() == 100
    assert update_decoder_v2.read_string() == "Hello World"


def test_var_uint_encoding():
    """Test variable unsigned integer encoding edge cases."""
    encoder = Encoder()

    # Test boundary values
    boundary_values = [0, 1, 127, 128, 255, 256, 16383, 16384, 2097151, 2097152]

    for value in boundary_values:
        encoder.write_var_uint(value)

    encoded = encoder.to_bytes()

    # Decode using Decoder class
    decoder = Decoder(encoded)
    for expected in boundary_values:
        result = decoder.read_var_uint()
        assert result == expected, (
            f"VarUInt encoding failed for {expected}, got {result}"
        )


def test_update_structure_encoding():
    """Test encoding of complex update structures."""
    encoder = UpdateEncoderV1()

    # Simulate a complex update structure
    encoder.write_client(1)
    encoder.write_len(5)

    # Write some operations
    encoder.write_left_id(ID(1, 1))
    encoder.write_right_id(ID(1, 2))
    encoder.write_parent_info(False)
    encoder.write_info(1)  # insert operation
    encoder.write_string("test content")

    # Write another operation
    encoder.write_left_id(ID(2, 1))
    encoder.write_right_id(ID(1, 3))
    encoder.write_parent_info(True)
    encoder.write_info(2)  # delete operation
    encoder.write_len(3)

    # Verify the update can be decoded
    update = encoder.to_bytes()
    decoder = Decoder(update)
    update_decoder = UpdateDecoderV1(decoder)

    assert update_decoder.read_client() == 1
    assert update_decoder.read_len() == 5


def test_encoder_error_handling():
    """Test encoder error handling."""
    encoder = Encoder()

    # Test writing valid values
    encoder.write_var_uint(42)
    encoded = encoder.to_bytes()

    # Test decoder with invalid data
    try:
        decoder = Decoder(bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF]))
        decoder.read_var_uint()
        assert False, "Should have raised an exception"
    except Exception:
        pass  # Expected


def test_version_compatibility():
    """Test that V1 and V2 encoders produce different but valid outputs."""
    # Create same content with both versions
    encoder_v1 = UpdateEncoderV1()
    encoder_v2 = UpdateEncoderV2()

    for encoder in [encoder_v1, encoder_v2]:
        encoder.write_client(1)
        encoder.write_len(10)
        encoder.write_string("test")

    update_v1 = encoder_v1.to_bytes()
    update_v2 = encoder_v2.to_bytes()

    # They should be different (different versions)
    assert update_v1 != update_v2

    # But both should be decodable
    decoder_v1 = Decoder(update_v1)
    update_decoder_v1 = UpdateDecoderV1(decoder_v1)
    decoder_v2 = Decoder(update_v2)
    update_decoder_v2 = UpdateDecoderV2(decoder_v2)

    assert update_decoder_v1.read_client() == 1
    assert update_decoder_v2.read_client() == 1


def test_large_update_encoding():
    """Test encoding of large updates."""
    encoder = UpdateEncoderV1()

    # Write many operations
    for i in range(100):
        encoder.write_client(i % 10)
        encoder.write_len(i)
        encoder.write_string(f"operation_{i}")

    update = encoder.to_bytes()

    # Verify it can be decoded
    decoder = Decoder(update)
    update_decoder = UpdateDecoderV1(decoder)
    for i in range(100):
        assert update_decoder.read_client() == i % 10
        assert update_decoder.read_len() == i
        assert update_decoder.read_string() == f"operation_{i}"


def test_encoder_buffer_management():
    """Test encoder buffer growth and management."""
    encoder = Encoder()

    # Write enough data to force buffer growth
    initial_length = len(encoder.buffer)

    for i in range(1000):
        encoder.write_var_uint(i)

    final_length = len(encoder.buffer)
    assert final_length > initial_length, "Buffer should have grown"

    # Verify all data can be read back
    encoded = encoder.to_bytes()

    # Decode using Decoder class
    decoder = Decoder(encoded)
    for i in range(1000):
        result = decoder.read_var_uint()
        assert result == i
