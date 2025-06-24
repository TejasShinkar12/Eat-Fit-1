from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
import re


class PIIMaskingConfig:
    """Configuration for PII masking in logs"""

    def __init__(
        self,
        is_enabled: bool = True,
        mask_emails: bool = True,
        mask_passwords: bool = True,
        mask_jwt: bool = True,
        email_mask_char: str = "*",
        password_mask_char: str = "#",
        jwt_mask_char: str = "*",
    ):
        self.is_enabled = is_enabled
        self.mask_emails = mask_emails
        self.mask_passwords = mask_passwords
        self.mask_jwt = mask_jwt
        self.email_mask_char = email_mask_char
        self.password_mask_char = password_mask_char
        self.jwt_mask_char = jwt_mask_char

        # Compile regex patterns
        self.email_pattern = re.compile(
            r"[^@\s]+@[^@\s]+\.[^@\s]+"
        )  # Simpler email pattern
        self.jwt_pattern = re.compile(
            r"[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*"
        )
        self.password_fields = {
            "password",
            "pwd",
            "user_password",
            "password_reset_token",
        }


def mask_email(email: str, config: PIIMaskingConfig) -> str:
    """Mask email address keeping first 2 characters"""
    if not email or not isinstance(email, str):
        return email

    if not config.email_pattern.match(email):
        return email

    local_part, domain = email.split("@", 1)
    visible_chars = min(2, len(local_part))
    masked_part = config.email_mask_char * 3  # Always use exactly 3 mask characters
    return f"{local_part[:visible_chars]}{masked_part}@{domain}"


def extract_jwt_parts(value: str) -> Tuple[str, str]:
    """Extract JWT token into prefix and token parts"""
    if value.startswith("Bearer "):
        return "Bearer ", value[7:]
    return "", value


def mask_jwt(token: str, config: PIIMaskingConfig) -> str:
    """Mask JWT token keeping the last 4 characters of the signature."""
    if not token or not isinstance(token, str):
        return token

    prefix, main_token = extract_jwt_parts(token)

    # Check if it's a valid JWT or short token
    if not (config.jwt_pattern.match(main_token) or len(main_token) <= 8):
        return token

    parts = main_token.split(".")
    if len(parts) >= 3:
        # It's a JWT, mask the signature part
        signature = parts[-1]
        suffix = signature[-4:] if len(signature) > 4 else signature
    else:
        # For short tokens, use the last 4 chars
        suffix = main_token[-4:] if len(main_token) > 4 else main_token

    masked_part = config.jwt_mask_char * 3  # Always use 3 mask characters
    return f"{prefix}{masked_part}{suffix}"


def is_password_field(field_name: str, config: PIIMaskingConfig) -> bool:
    """Check if a field name indicates a password"""
    return any(pwd_field in field_name.lower() for pwd_field in config.password_fields)


def mask_value(value: Any, config: PIIMaskingConfig) -> Any:
    """Mask a single value based on its type"""
    if isinstance(value, str):
        if config.mask_jwt and (
            config.jwt_pattern.match(value.replace("Bearer ", ""))
            or len(value.replace("Bearer ", "")) <= 8
        ):
            return mask_jwt(value, config)
        elif config.mask_emails and "@" in value and config.email_pattern.match(value):
            return mask_email(value, config)
    return value


def mask_pii(
    data: Dict[str, Any],
    config: PIIMaskingConfig,
    return_audit: bool = False,
    _audit_log: Optional[List[Dict[str, Any]]] = None,
) -> Union[Dict[str, Any], Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
    """
    Mask PII in a dictionary according to configuration.
    Returns masked data and optionally an audit log.
    """
    if not config.is_enabled:
        return (data, []) if return_audit else data

    if _audit_log is None:
        _audit_log = []

    masked_data = {}

    for key, value in data.items():
        if value is None or value == "":
            masked_data[key] = value
            continue

        # Handle nested dictionaries
        if isinstance(value, dict):
            if return_audit:
                nested_result, nested_audit = mask_pii(
                    value, config, return_audit=True, _audit_log=_audit_log
                )
                masked_data[key] = nested_result
            else:
                masked_data[key] = mask_pii(value, config)
            continue

        # Handle lists/arrays
        if isinstance(value, list):
            if config.mask_passwords and is_password_field(key, config):
                # If it's a password field, mask all values in the list
                masked_data[key] = ["[MASKED]" for _ in value]
                _audit_log.extend(
                    [
                        {
                            "field": f"{key}[{i}]",
                            "type": "password",
                            "timestamp": datetime.now(),
                        }
                        for i in range(len(value))
                    ]
                )
            else:
                # Otherwise process each item
                masked_data[key] = [
                    mask_pii(item, config)
                    if isinstance(item, dict)
                    else mask_value(item, config)
                    for item in value
                ]
            continue

        # Handle strings
        if not isinstance(value, str):
            masked_data[key] = value
            continue

        # Apply masking rules
        masked_value = value

        # Mask passwords
        if config.mask_passwords and is_password_field(key, config):
            masked_value = "[MASKED]"
            _audit_log.append(
                {"field": key, "type": "password", "timestamp": datetime.now()}
            )

        # Mask emails
        elif config.mask_emails and "@" in value:
            masked = mask_email(value, config)
            if masked != value:
                masked_value = masked
                _audit_log.append(
                    {"field": key, "type": "email", "timestamp": datetime.now()}
                )

        # Mask JWT tokens
        elif config.mask_jwt:
            token = value.replace("Bearer ", "")
            if config.jwt_pattern.match(token) or len(token) <= 8:
                masked_value = mask_jwt(value, config)
                if masked_value != value:
                    _audit_log.append(
                        {"field": key, "type": "jwt", "timestamp": datetime.now()}
                    )

        masked_data[key] = masked_value

    return (masked_data, _audit_log) if return_audit else masked_data
