# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Pytest configuration and fixtures for Snowflake MCP Server tests.
"""

import os
from pathlib import Path
from unittest.mock import Mock

import pytest
from snowflake.core import Root

from snowflake_mcp.config.settings import ServerConfig, SQLStatementPermissions
from snowflake_mcp.core.connection import SnowflakeConnectionManager


@pytest.fixture
def mock_connection_params():
    """Mock connection parameters for testing."""
    return {
        "account": "test_account",
        "user": "test_user",
        "password": "test_password",
        "warehouse": "test_warehouse",
        "role": "test_role"
    }


@pytest.fixture
def mock_connection_manager(mock_connection_params):
    """Mock Snowflake connection manager."""
    manager = Mock(spec=SnowflakeConnectionManager)
    manager.connection_params = mock_connection_params
    manager.connection = Mock()
    manager.root = Mock(spec=Root)
    return manager


@pytest.fixture
def test_config():
    """Test server configuration."""
    return ServerConfig(
        sql_statement_permissions=SQLStatementPermissions(
            allowed=["select", "show", "describe", "create", "drop"],
            disallowed=["delete", "truncate"]
        )
    )


@pytest.fixture
def test_config_file(tmp_path):
    """Create a temporary test configuration file."""
    config_content = """
sql_statement_permissions:
  - select: true
  - show: true
  - describe: true
  - create: true
  - drop: false
  - unknown: false
"""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    return str(config_file)


@pytest.fixture
def mock_execute_query():
    """Mock execute_query function."""
    def _mock_execute(statement, connection_manager):
        # Return mock data based on statement type
        if "SHOW DATABASES" in statement.upper():
            return [
                {"name": "TEST_DB", "comment": "Test database"},
                {"name": "SAMPLE_DB", "comment": "Sample database"}
            ]
        elif "SHOW TABLES" in statement.upper():
            return [
                {"name": "TEST_TABLE", "database_name": "TEST_DB", "schema_name": "PUBLIC"},
                {"name": "SAMPLE_TABLE", "database_name": "TEST_DB", "schema_name": "PUBLIC"}
            ]
        elif "SELECT" in statement.upper():
            return [
                {"id": 1, "name": "test_row_1"},
                {"id": 2, "name": "test_row_2"}
            ]
        else:
            return []
    return _mock_execute