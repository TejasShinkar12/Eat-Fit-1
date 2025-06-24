import pytest
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from app.utils.logger import setup_logger, get_logger


@pytest.fixture
def log_dir(tmp_path):
    """Create a temporary directory for log files"""
    log_path = tmp_path / "logs"
    log_path.mkdir()
    return log_path


@pytest.fixture
def cleanup_logs():
    """Cleanup any existing loggers"""
    yield
    logging.getLogger().handlers.clear()


def test_logger_creation(log_dir, cleanup_logs):
    """Test basic logger creation and configuration"""
    logger = setup_logger(log_dir, "dev")
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 2  # Console and File handlers

    # Check handler types
    handlers = logger.handlers
    assert any(
        isinstance(h, logging.StreamHandler) for h in handlers
    )  # Console handler
    assert any(isinstance(h, logging.FileHandler) for h in handlers)  # File handler


def test_log_file_creation(log_dir, cleanup_logs):
    """Test that log files are created with correct naming"""
    logger = setup_logger(log_dir, "dev")
    today = datetime.now().strftime("%Y-%m-%d")
    expected_file = log_dir / f"app-dev-{today}.log"

    logger.info("Test message")
    assert expected_file.exists()


def test_json_log_format(log_dir, cleanup_logs):
    """Test that logs are written in correct JSON format"""
    logger = setup_logger(log_dir, "dev")
    test_message = "Test log message"
    logger.info(test_message)

    # Read the log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-dev-{today}.log"
    with open(log_file) as f:
        log_entry = json.loads(f.readline())

    # Check required fields
    assert log_entry["message"] == test_message
    assert log_entry["level"] == "INFO"
    assert "timestamp" in log_entry
    assert "module_name" in log_entry
    assert "function_name" in log_entry
    assert "line_number" in log_entry
    assert "process_id" in log_entry
    assert "thread_id" in log_entry


def test_get_logger(log_dir, cleanup_logs):
    """Test that get_logger returns the same logger instance"""
    logger1 = get_logger("test_module")
    logger2 = get_logger("test_module")
    assert logger1 is logger2


def test_different_log_levels(log_dir, cleanup_logs):
    """Test logging at different levels"""
    logger = setup_logger(log_dir, "dev")

    test_messages = {
        "debug": "Debug message",
        "info": "Info message",
        "warning": "Warning message",
        "error": "Error message",
    }

    # Log messages at different levels
    logger.debug(test_messages["debug"])
    logger.info(test_messages["info"])
    logger.warning(test_messages["warning"])
    logger.error(test_messages["error"])

    # Read and parse log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-dev-{today}.log"
    with open(log_file) as f:
        logs = [json.loads(line) for line in f]

    # Debug shouldn't be logged (default level is INFO)
    assert len(logs) == 3

    # Verify levels and messages
    assert logs[0]["level"] == "INFO"
    assert logs[0]["message"] == test_messages["info"]
    assert logs[1]["level"] == "WARNING"
    assert logs[1]["message"] == test_messages["warning"]
    assert logs[2]["level"] == "ERROR"
    assert logs[2]["message"] == test_messages["error"]


def test_exception_logging(log_dir, cleanup_logs):
    """Test logging exceptions with traceback"""
    logger = setup_logger(log_dir, "dev")

    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.exception("An error occurred")

    # Read and parse log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-dev-{today}.log"
    with open(log_file) as f:
        log_entry = json.loads(f.readline())

    assert log_entry["level"] == "ERROR"
    assert "An error occurred" in log_entry["message"]
    assert "ValueError: Test exception" in log_entry["traceback"]
    assert "test_logger.py" in log_entry["traceback"]


def test_nested_exception_logging(log_dir, cleanup_logs):
    """Test logging nested exceptions with full traceback"""
    logger = setup_logger(log_dir, "dev")

    try:
        try:
            raise ValueError("Inner exception")
        except ValueError as e:
            raise RuntimeError("Outer exception") from e
    except Exception as e:
        logger.exception("A nested error occurred")

    # Read and parse log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-dev-{today}.log"
    with open(log_file) as f:
        log_entry = json.loads(f.readline())

    assert log_entry["level"] == "ERROR"
    assert "A nested error occurred" in log_entry["message"]
    assert "RuntimeError: Outer exception" in log_entry["traceback"]
    assert "ValueError: Inner exception" in log_entry["traceback"]


def test_unicode_logging(log_dir, cleanup_logs):
    """Test logging unicode characters"""
    logger = setup_logger(log_dir, "dev")

    unicode_message = "Unicode test: 你好, привет, مرحبا, שָׁלוֹם"
    logger.info(unicode_message)

    # Read and parse log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-dev-{today}.log"
    with open(log_file, encoding="utf-8") as f:
        log_entry = json.loads(f.readline())

    assert log_entry["message"] == unicode_message


def test_large_message_logging(log_dir, cleanup_logs):
    """Test logging large messages"""
    logger = setup_logger(log_dir, "dev")

    # Create a large message (100KB)
    large_message = "Large message test: " + "x" * 102400
    logger.info(large_message)

    # Read and parse log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-dev-{today}.log"
    with open(log_file) as f:
        log_entry = json.loads(f.readline())

    assert log_entry["message"] == large_message


def test_multiple_loggers_same_file(log_dir, cleanup_logs):
    """Test multiple loggers writing to the same file"""
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")

    setup_logger(log_dir, "dev")

    logger1.info("Message from logger1")
    logger2.info("Message from logger2")

    # Read and parse log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-dev-{today}.log"
    with open(log_file) as f:
        logs = [json.loads(line) for line in f]

    assert len(logs) == 2
    assert logs[0]["module_name"] == "module1"
    assert logs[1]["module_name"] == "module2"


def test_rapid_logging(log_dir, cleanup_logs):
    """Test rapid consecutive logging"""
    logger = setup_logger(log_dir, "dev")

    # Log 1000 messages as fast as possible
    for i in range(1000):
        logger.info(f"Rapid message {i}")

    # Read and parse log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-dev-{today}.log"
    with open(log_file) as f:
        logs = [json.loads(line) for line in f]

    assert len(logs) == 1000
    assert all(log["level"] == "INFO" for log in logs)
    assert all(log["message"].startswith("Rapid message") for log in logs)


def test_extra_fields_logging(log_dir, cleanup_logs):
    """Test logging with extra fields"""
    logger = setup_logger(log_dir, "dev")

    extra_data = {"user_id": "123", "action": "login"}
    logger.info("User action", extra=extra_data)

    # Read and parse log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-dev-{today}.log"
    with open(log_file) as f:
        log_entry = json.loads(f.readline())

    assert log_entry["message"] == "User action"
    assert "extra" in log_entry
    assert log_entry["extra"]["user_id"] == "123"
    assert log_entry["extra"]["action"] == "login"


def test_invalid_json_characters(log_dir, cleanup_logs):
    """Test logging messages with invalid JSON characters"""
    logger = setup_logger(log_dir, "dev")

    # Message with control characters and invalid JSON chars
    message = "Invalid chars: \x00\x01\x02\x03\x04\x05\x06\x07\x08\x09"
    logger.info(message)

    # Read and parse log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"app-dev-{today}.log"
    with open(log_file) as f:
        # Should not raise JSONDecodeError
        log_entry = json.loads(f.readline())

    assert "Invalid chars" in log_entry["message"]
