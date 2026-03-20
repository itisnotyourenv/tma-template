#!/usr/bin/env python3
"""Generate valid Telegram WebApp init data for testing.

This script creates properly signed init data that can be used with
safe_parse_webapp_init_data from aiogram.utils.web_app.

Usage:
    uv run python scripts/generate_tg_init_data.py [--bot-token TOKEN] [options]
    uv run python scripts/generate_tg_init_data.py  # Uses bot_token from config.yaml

The generated init data is printed to stdout and can be used for:
- Testing API endpoints that validate init data
- Setting the tg_init_data field in config.yaml if --set-config is passed
- CI/CD pipeline testing

Based on: aiogram.utils.web_app.safe_parse_webapp_init_data
"""

import argparse
from contextlib import suppress
from datetime import UTC, datetime
import hashlib
import hmac
import json
from pathlib import Path
import sys
from urllib.parse import parse_qsl, unquote, urlencode

from aiogram.utils.web_app import safe_parse_webapp_init_data
import yaml


def load_config() -> dict:
    """Load config.yaml to get bot token."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if not config_path.exists():
        return {}

    return yaml.safe_load(config_path.read_text())


def extract_bot_token(config: dict) -> str | None:
    """Extract bot token from config dict."""
    telegram = config.get("telegram", {})
    return telegram.get("bot_token")


def parse_init_data(init_data: str) -> dict:
    """Parse init data query string into dict."""
    parsed = {}
    for key, value in parse_qsl(unquote(init_data)):
        parsed[key] = value
    return parsed


def generate_hash(data: dict, token: str) -> str:
    """Generate HMAC-SHA256 hash for init data

    This follows Telegram's WebApp validation algorithm:
    1. Sort data pairs by key (excluding hash)
    2. Join as key=value with newlines
    3. Compute HMAC-SHA256 with derived secret key
    """
    # Sort all fields except hash
    pairs = []
    for key in sorted(data.keys()):
        if key != "hash":
            value = data[key]
            # Handle user field specially to ensure stable JSON
            if key == "user" and isinstance(value, dict):
                # Sort keys for consistent JSON
                value = json.dumps(value, separators=(",", ":"), sort_keys=True)
            pairs.append(f"{key}={value}")

    data_check_string = "\n".join(pairs)

    # Compute secret key: HMAC-SHA256 with key='WebAppData' and msg=token
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=token.encode(),
        digestmod=hashlib.sha256,
    ).digest()

    # Calculate HMAC-SHA256
    return hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()


def create_user_json(
    user_id: int = 123456789,
    username: str = "test_user",
    first_name: str = "Test",
    last_name: str = "User",
    language_code: str = "en",
    photo_url: str | None = None,
    added_to_attachment_menu: bool = False,
    allows_write_to_pm: bool = True,
    is_premium: bool = False,
    is_bot: bool = False,
) -> dict:
    """Create user dict compatible with WebAppUser."""
    user = {
        "id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "language_code": language_code,
        "added_to_attachment_menu": added_to_attachment_menu,
        "allows_write_to_pm": allows_write_to_pm,
        "is_premium": is_premium,
        "is_bot": is_bot,
    }
    if photo_url:
        user["photo_url"] = photo_url
    return user


def generate_init_data(
    bot_token: str,
    user: dict | None = None,
    start_param: str = "",
    chat_instance: str = "",
    chat_type: str = "",
    auth_date: datetime | None = None,
    receiver: dict | None = None,
) -> str:
    """Generate valid signed WebApp init data.

    Args:
        bot_token: The bot token to use for signing
        user: User data dict (or None for default test user)
        start_param: Optional start_param value
        chat_instance: Optional chat_instance value
        chat_type: Optional chat_type value
        auth_date: Optional auth_date (defaults to now)
        receiver: Optional receiver data for launch mode

    Returns:
        URL-encoded init data string with hash
    """
    if user is None:
        user = create_user_json()

    if auth_date is None:
        auth_date = datetime.now(UTC)

    data: dict = {"user": user}

    # Add timestamp
    data["auth_date"] = int(auth_date.timestamp())

    # Add optional fields
    if start_param:
        data["start_param"] = start_param
    if chat_instance:
        data["chat_instance"] = chat_instance
    if chat_type:
        data["chat_type"] = chat_type
    if receiver:
        data["receiver"] = receiver

    # Serialize user/receiver to JSON
    for key in ["user", "receiver"]:
        if isinstance(data.get(key), dict):
            data[key] = json.dumps(data[key], separators=(",", ":"), sort_keys=True)

    # Generate hash
    data["hash"] = generate_hash(data, bot_token)

    # Build query string
    # Must match Telegram's ordering for consistency
    return urlencode(data, safe="/:=&")


def validate_init_data(init_data: str, token: str) -> dict[str, str | None]:
    """Validate init data by parsing with aiogram if available."""
    try:
        parsed = safe_parse_webapp_init_data(token, init_data)
        return {
            "user_id": str(parsed.user.id) if parsed.user else None,
            "username": parsed.user.username if parsed.user else None,
            "first_name": parsed.user.first_name if parsed.user else None,
            "last_name": parsed.user.last_name if parsed.user else None,
            "language_code": parsed.user.language_code if parsed.user else None,
            "start_param": parsed.start_param,
            "auth_date": str(parsed.auth_date) if parsed.auth_date else None,
        }
    except Exception as ex:
        return {"error": str(ex)}


def set_config_init_data(init_data: str) -> bool:
    """Update config.yaml with the generated init data."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        return False

    try:
        config = yaml.safe_load(config_path.read_text()) or {}
        if "telegram" not in config:
            config["telegram"] = {}
        config["telegram"]["tg_init_data"] = init_data

        with open(config_path, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"Updated {config_path} with new tg_init_data")
        return True

    except Exception as ex:
        print(f"Error updating config file: {ex}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate valid Telegram WebApp init data for testing"
    )
    parser.add_argument(
        "--bot-token",
        "-t",
        help="Bot token (defaults to telegram.bot_token from config.yaml)",
    )
    parser.add_argument(
        "--user-id", type=int, default=123456789, help="User ID (default: 123456789)"
    )
    parser.add_argument(
        "--username", "-u", default="test_user", help="Username (default: test_user)"
    )
    parser.add_argument(
        "--first-name", "-f", default="Test", help="First name (default: Test)"
    )
    parser.add_argument(
        "--last-name", "-l", default="User", help="Last name (default: User)"
    )
    parser.add_argument(
        "--language-code", "-L", default="en", help="Language code (default: en)"
    )
    parser.add_argument("--start-param", "-s", default="", help="Start parameter")
    parser.add_argument("--photo-url", default="", help="User photo URL")
    parser.add_argument("--premium", action="store_true", help="Mark user as premium")
    parser.add_argument(
        "--set-config",
        action="store_true",
        help="Update config.yaml with the generated init data",
    )
    parser.add_argument(
        "--validate",
        "-v",
        action="store_true",
        help="Validate the generated init data with aiogram",
    )
    parser.add_argument(
        "--format",
        choices=["oneline", "pretty"],
        default="oneline",
        help="Output format (default: oneline)",
    )

    args = parser.parse_args()

    # Load bot token
    config = load_config()
    bot_token = args.bot_token or extract_bot_token(config)

    if not bot_token:
        print(
            "Error: Bot token required. Set --bot-token or ensure telegram.bot_token in config.yaml",
            file=sys.stderr,
        )
        return 1

    # Create user dict
    user = create_user_json(
        user_id=args.user_id,
        username=args.username,
        first_name=args.first_name,
        last_name=args.last_name,
        language_code=args.language_code,
        photo_url=args.photo_url or None,
        is_premium=args.premium,
    )

    # Generate init data
    init_data = generate_init_data(
        bot_token=bot_token,
        user=user,
        start_param=args.start_param,
    )

    # Output
    if args.format == "pretty":
        # Convert to parseable form
        parsed = parse_init_data(init_data)
        if "user" in parsed:
            with suppress(json.JSONDecodeError):
                parsed["user"] = json.loads(parsed["user"])

        print(json.dumps(parsed, indent=2))

    else:
        print(init_data)

    # Validate if requested
    if args.validate:
        result = validate_init_data(init_data, bot_token)
        print("\nValidation:", file=sys.stderr)
        if "error" in result:
            print(f"  FAILED: {result['error']}", file=sys.stderr)
        else:
            for key, value in result.items():
                print(f"  {key}: {value}", file=sys.stderr)

    # Update config if requested
    if args.set_config:
        set_config_init_data(init_data)

    return 0


if __name__ == "__main__":
    sys.exit(main())
