import hashlib


def generate_referral_code(user_id: int) -> str:
    """Generate 8-character referral code from user ID using SHA256."""
    hash_input = f"referral:{user_id}".encode()
    hash_digest = hashlib.sha256(hash_input).hexdigest()
    return hash_digest[:8]


def find_referrer_id(code: str, user_ids: list[int]) -> int | None:
    """Find user ID by referral code. Returns None if not found."""
    for user_id in user_ids:
        if generate_referral_code(user_id) == code:
            return user_id
    return None
