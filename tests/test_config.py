"""Tests for configuration module"""

import pytest
from src.config import Settings, get_settings


def test_settings_creation():
    """Test that settings can be created"""
    settings = Settings()
    assert settings.APP_NAME is not None
    assert settings.ENVIRONMENT in ["development", "production"]


def test_get_settings():
    """Test get_settings singleton"""
    settings = get_settings()
    assert settings is not None
    assert settings.API_PORT > 0


def test_settings_debug_flag():
    """Test debug flag based on environment"""
    settings = Settings(ENVIRONMENT="development")
    assert settings.DEBUG is True

    settings = Settings(ENVIRONMENT="production")
    assert settings.DEBUG is False
