import pytest
from datetime import datetime
from app.utils.logger.pii_masker import PIIMaskingConfig, mask_pii

def test_default_config():
    """Test default PII masking configuration"""
    config = PIIMaskingConfig()
    
    # Test default settings
    assert config.is_enabled == True
    assert config.mask_emails == True
    assert config.mask_passwords == True
    assert config.mask_jwt == True
    
    # Test default masking characters
    assert config.email_mask_char == '*'
    assert config.password_mask_char == '#'
    assert config.jwt_mask_char == '*'

def test_email_masking():
    """Test email masking patterns"""
    config = PIIMaskingConfig()
    test_cases = [
        # Basic email
        ("user@example.com", "us***@example.com"),
        # Email with dots
        ("john.doe@example.com", "jo***@example.com"),
        # Email with plus
        ("user+test@example.com", "us***@example.com"),
        # Short local part
        ("a@example.com", "a***@example.com"),
        # Long local part
        ("verylongusername@example.com", "ve***@example.com"),
        # Mixed case
        ("UserName@Example.com", "Us***@Example.com"),
    ]
    
    for input_email, expected_output in test_cases:
        assert mask_pii({"email": input_email}, config)["email"] == expected_output

def test_password_masking():
    """Test password field masking"""
    config = PIIMaskingConfig()
    test_cases = [
        # Standard password field
        ({"password": "secret123"}, {"password": "[MASKED]"}),
        # Different field names
        ({"pwd": "secret123"}, {"pwd": "[MASKED]"}),
        ({"user_password": "secret123"}, {"user_password": "[MASKED]"}),
        # Nested password
        ({"user": {"password": "secret123"}}, {"user": {"password": "[MASKED]"}}),
        # Password in array
        ({"passwords": ["secret1", "secret2"]}, {"passwords": ["[MASKED]", "[MASKED]"]}),
    ]
    
    for input_data, expected_output in test_cases:
        assert mask_pii(input_data, config) == expected_output

def test_jwt_masking():
    """Test JWT token masking"""
    config = PIIMaskingConfig()
    test_cases = [
        # Standard JWT
        ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8",
         "***w5N_XgL0"),
        # Bearer token
        ("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8",
         "Bearer ***w5N_XgL0"),
        # Short token
        ("abcd1234", "***1234"),
    ]
    
    for input_token, expected_output in test_cases:
        assert mask_pii({"token": input_token}, config)["token"] == expected_output

def test_custom_masking_chars():
    """Test custom masking characters"""
    config = PIIMaskingConfig(
        email_mask_char='#',
        password_mask_char='*',
        jwt_mask_char='$'
    )
    
    test_data = {
        "email": "user@example.com",
        "password": "secret123",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8"
    }
    
    masked = mask_pii(test_data, config)
    assert masked["email"] == "us###@example.com"
    assert masked["password"] == "[MASKED]"
    assert masked["token"].endswith("w5N_XgL0")
    assert "$$$" in masked["token"]

def test_disable_masking():
    """Test disabling masking features"""
    config = PIIMaskingConfig(
        mask_emails=False,
        mask_passwords=True,
        mask_jwt=False
    )
    
    test_data = {
        "email": "user@example.com",
        "password": "secret123",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8"
    }
    
    masked = mask_pii(test_data, config)
    assert masked["email"] == "user@example.com"  # Not masked
    assert masked["password"] == "[MASKED]"  # Still masked
    assert masked["token"] == test_data["token"]  # Not masked

def test_nested_objects():
    """Test masking PII in nested objects"""
    config = PIIMaskingConfig()
    test_data = {
        "user": {
            "email": "user@example.com",
            "settings": {
                "password": "secret123",
                "tokens": ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123"]
            }
        },
        "logs": [
            {"user_email": "user1@example.com"},
            {"user_email": "user2@example.com"}
        ]
    }
    
    masked = mask_pii(test_data, config)
    assert masked["user"]["email"] == "us***@example.com"
    assert masked["user"]["settings"]["password"] == "[MASKED]"
    assert masked["user"]["settings"]["tokens"][0].endswith("c123")
    assert masked["logs"][0]["user_email"] == "us***@example.com"
    assert masked["logs"][1]["user_email"] == "us***@example.com"

def test_audit_log():
    """Test audit logging of masked fields"""
    config = PIIMaskingConfig()
    test_data = {
        "email": "user@example.com",
        "password": "secret123",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123"
    }
    
    masked, audit = mask_pii(test_data, config, return_audit=True)
    
    # Check masked data
    assert masked["email"] == "us***@example.com"
    assert masked["password"] == "[MASKED]"
    assert masked["token"].endswith("c123")
    
    # Check audit log
    assert len(audit) == 3  # Three fields were masked
    assert any(entry["field"] == "email" for entry in audit)
    assert any(entry["field"] == "password" for entry in audit)
    assert any(entry["field"] == "token" for entry in audit)
    assert all("timestamp" in entry for entry in audit)
    assert all(isinstance(entry["timestamp"], datetime) for entry in audit)

def test_edge_cases():
    """Test edge cases and invalid inputs"""
    config = PIIMaskingConfig()
    test_cases = [
        # Empty values
        ({"email": ""}, {"email": ""}),
        ({"password": ""}, {"password": ""}),
        ({"token": ""}, {"token": ""}),
        
        # None values
        ({"email": None}, {"email": None}),
        
        # Invalid email formats
        ({"email": "invalid-email"}, {"email": "invalid-email"}),
        
        # Very short values
        ({"email": "a@b.c"}, {"email": "a***@b.c"}),
        
        # Unicode characters
        ({"email": "üser@example.com"}, {"email": "üs***@example.com"}),
        
        # Mixed PII types
        ({"password_reset_token": "secret123"}, {"password_reset_token": "[MASKED]"}),
    ]
    
    for input_data, expected_output in test_cases:
        assert mask_pii(input_data, config) == expected_output 