# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for validation utilities.
"""

import pytest

from snowflake_mcp.core.exceptions import SnowflakeException
from snowflake_mcp.utils.validators import (
    sanitize_tool_name,
    validate_identifier,
    validate_sql_permissions,
    validate_connection_params
)


class TestSanitizeToolName:
    """Test tool name sanitization."""
    
    def test_valid_name(self):
        assert sanitize_tool_name("valid_name") == "valid_name"
    
    def test_name_with_spaces(self):
        assert sanitize_tool_name("my tool name") == "my_tool_name"
    
    def test_name_with_special_chars(self):
        assert sanitize_tool_name("my-tool@name!") == "my_tool_name_"
    
    def test_name_starting_with_digit(self):
        assert sanitize_tool_name("123tool") == "service_123tool"


class TestValidateIdentifier:
    """Test Snowflake identifier validation."""
    
    def test_valid_identifier(self):
        assert validate_identifier("valid_name") == "valid_name"
        assert validate_identifier("ValidName") == "ValidName"
        assert validate_identifier("_private") == "_private"
        assert validate_identifier("$system") == "$system"
    
    def test_invalid_empty(self):
        with pytest.raises(SnowflakeException, match="must be a non-empty string"):
            validate_identifier("")
    
    def test_invalid_none(self):
        with pytest.raises(SnowflakeException, match="must be a non-empty string"):
            validate_identifier(None)
    
    def test_invalid_too_long(self):
        long_name = "a" * 256
        with pytest.raises(SnowflakeException, match="exceeds 255 character limit"):
            validate_identifier(long_name)
    
    def test_invalid_characters(self):
        with pytest.raises(SnowflakeException, match="must start with letter"):
            validate_identifier("123invalid")
        
        with pytest.raises(SnowflakeException, match="contain only letters"):
            validate_identifier("invalid-name")


class TestValidateSQL Permissions:
    """Test SQL permissions validation."""
    
    def test_create_operation(self):
        stmt_type, is_valid = validate_sql_permissions(
            "create_table", 
            ["create", "select"], 
            ["drop"]
        )
        assert stmt_type == "create"
        assert is_valid is True
    
    def test_disallowed_operation(self):
        stmt_type, is_valid = validate_sql_permissions(
            "drop_table", 
            ["create", "select"], 
            ["drop"]
        )
        assert stmt_type == "drop"
        assert is_valid is False
    
    def test_allow_all(self):
        stmt_type, is_valid = validate_sql_permissions(
            "unknown_operation", 
            ["all"], 
            []
        )
        assert is_valid is True
    
    def test_no_permissions_configured(self):
        stmt_type, is_valid = validate_sql_permissions(
            "any_operation", 
            [], 
            []
        )
        assert is_valid is False


class TestValidateConnectionParams:
    """Test connection parameter validation."""
    
    def test_valid_params(self):
        params = {
            "account": "test_account",
            "user": "test_user",
            "password": "test_password"
        }
        result = validate_connection_params(params)
        assert result == params
    
    def test_missing_account(self):
        params = {"user": "test_user", "password": "test_password"}
        with pytest.raises(SnowflakeException, match="Missing required connection parameters"):
            validate_connection_params(params)
    
    def test_invalid_account_format(self):
        params = {
            "account": "invalid@account!",
            "user": "test_user",
            "password": "test_password"
        }
        with pytest.raises(SnowflakeException, match="Invalid account identifier format"):
            validate_connection_params(params)