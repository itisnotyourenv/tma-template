import base64
import hashlib
import struct


def encode_referral(user_id: int, secret_key: str) -> str:
    """Encode user_id into a short referral code using XOR encryption."""
    key_hash = hashlib.sha256(secret_key.encode()).digest()
    key_int = int.from_bytes(key_hash[:8], "big")

    encrypted = user_id ^ key_int
    packed = struct.pack(">Q", encrypted)
    return base64.urlsafe_b64encode(packed).decode().rstrip("=")


def decode_referral(code: str, secret_key: str) -> int | None:
    """Decode referral code back to user_id. Returns None if invalid."""
    try:
        padding = 4 - len(code) % 4
        if padding != 4:
            code += "=" * padding

        packed = base64.urlsafe_b64decode(code)
        encrypted = struct.unpack(">Q", packed)[0]

        key_hash = hashlib.sha256(secret_key.encode()).digest()
        key_int = int.from_bytes(key_hash[:8], "big")

        return encrypted ^ key_int
    except Exception:
        return None
