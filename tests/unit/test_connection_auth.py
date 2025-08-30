# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for connection authentication methods.
"""

import pytest
from unittest.mock import Mock, patch

from snowflake_mcp.core.connection import SnowflakeConnectionManager


class TestConnectionAuthentication:
    """Test different authentication methods in SnowflakeConnectionManager."""
    
    def test_prepare_connection_params_externalbrowser(self):
        """Test externalbrowser authentication parameter preparation."""
        connection_params = {
            "account": "test_account",
            "user": "test_user", 
            "password": "should_be_removed",
            "authenticator": "externalbrowser",
            "warehouse": "test_warehouse",
            "private_key": "should_be_removed"
        }
        
        manager = SnowflakeConnectionManager(connection_params)
        result = manager._prepare_connection_params()
        
        # Should remove password and private key for externalbrowser
        assert "password" not in result
        assert "private_key" not in result
        assert "private_key_file" not in result
        assert "private_key_pwd" not in result
        
        # Should keep other params
        assert result["account"] == "test_account"
        assert result["user"] == "test_user"
        assert result["authenticator"] == "externalbrowser"
        assert result["warehouse"] == "test_warehouse"
    
    def test_prepare_connection_params_oauth(self):
        """Test OAuth authentication parameter preparation."""
        connection_params = {
            "account": "test_account",
            "user": "test_user",
            "password": "oauth_token_here",
            "authenticator": "oauth",
            "private_key": "should_be_removed"
        }
        
        manager = SnowflakeConnectionManager(connection_params)
        result = manager._prepare_connection_params()
        
        # Should convert password to token for OAuth
        assert "password" not in result
        assert result["token"] == "oauth_token_here"
        assert result["authenticator"] == "oauth"
        
        # Should remove private key params
        assert "private_key" not in result
    
    def test_prepare_connection_params_keypair(self):
        """Test key pair authentication parameter preparation."""
        connection_params = {
            "account": "test_account", 
            "user": "test_user",
            "password": "should_be_removed",
            "private_key": "-----BEGIN PRIVATE KEY-----...",
            "private_key_pwd": "key_passphrase"
        }
        
        manager = SnowflakeConnectionManager(connection_params)
        result = manager._prepare_connection_params()
        
        # Should remove password for key pair auth
        assert "password" not in result
        
        # Should keep private key params
        assert result["private_key"] == "-----BEGIN PRIVATE KEY-----..."
        assert result["private_key_pwd"] == "key_passphrase"
        assert result["authenticator"] == "snowflake"  # Key pair uses default
    
    def test_prepare_connection_params_okta(self):
        """Test Okta authentication parameter preparation."""
        connection_params = {
            "account": "test_account",
            "user": "test_user",
            "password": "password123", 
            "authenticator": "https://company.okta.com",
            "private_key": "should_be_removed"
        }
        
        manager = SnowflakeConnectionManager(connection_params)
        result = manager._prepare_connection_params()
        
        # Should keep password for Okta
        assert result["password"] == "password123"
        assert result["authenticator"] == "https://company.okta.com"
        
        # Should remove private key params
        assert "private_key" not in result
    
    def test_prepare_connection_params_standard(self):
        """Test standard username/password authentication."""
        connection_params = {
            "account": "test_account",
            "user": "test_user", 
            "password": "password123",
            "authenticator": "snowflake"
        }
        
        manager = SnowflakeConnectionManager(connection_params)
        result = manager._prepare_connection_params()
        
        # Should keep all standard params
        assert result["account"] == "test_account"
        assert result["user"] == "test_user"
        assert result["password"] == "password123"
        assert result["authenticator"] == "snowflake"
    
    def test_prepare_connection_params_mfa(self):
        """Test MFA authentication parameter preparation."""
        connection_params = {
            "account": "test_account",
            "user": "test_user",
            "password": "password123", 
            "authenticator": "username_password_mfa",
            "passcode": "123456"
        }
        
        manager = SnowflakeConnectionManager(connection_params)
        result = manager._prepare_connection_params()
        
        # Should keep all MFA params
        assert result["password"] == "password123"
        assert result["authenticator"] == "username_password_mfa"
        assert result["passcode"] == "123456"
    
    def test_none_values_removed(self):
        """Test that None values are removed from connection params."""
        connection_params = {
            "account": "test_account",
            "user": "test_user",
            "password": None,
            "role": None,
            "warehouse": "test_warehouse",
            "authenticator": "externalbrowser"
        }
        
        manager = SnowflakeConnectionManager(connection_params)
        result = manager._prepare_connection_params()
        
        # Should not contain None values
        assert "password" not in result
        assert "role" not in result
        
        # Should contain non-None values
        assert result["account"] == "test_account"
        assert result["user"] == "test_user"
        assert result["warehouse"] == "test_warehouse"
    
    @patch('snowflake_mcp.core.connection.logger')
    def test_log_authentication_method_externalbrowser(self, mock_logger):
        """Test logging for externalbrowser authentication."""
        connection_params = {
            "account": "test_account",
            "user": "test_user",
            "authenticator": "externalbrowser"
        }
        
        manager = SnowflakeConnectionManager({})
        manager._log_authentication_method(connection_params)
        
        # Should log externalbrowser-specific messages
        mock_logger.info.assert_any_call(
            "Authenticating with external browser SSO for user 'test_user' on account 'test_account'"
        )
        mock_logger.info.assert_any_call(
            "Browser will open for authentication. Please complete SSO login in the browser."
        )