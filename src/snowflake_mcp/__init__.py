# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Snowflake Minimal MCP Server Package.

This package provides a minimal Model Context Protocol (MCP) server implementation for
interacting with Snowflake's core database functionality. The server enables seamless
integration with Snowflake's data management capabilities through a standardized protocol.

The package supports:
- Object Management: Create, alter, drop, describe, and list Snowflake objects
- SQL Execution: Execute SQL statements with configurable permissions  
- Semantic View Querying: Discover and query Snowflake Semantic Views

Environment Variables
---------------------
SNOWFLAKE_ACCOUNT : str
    Snowflake account identifier (alternative to --account)
SNOWFLAKE_USER : str
    Snowflake username (alternative to --username)
SNOWFLAKE_PASSWORD : str
    Password or Programmatic Access Token (alternative to --password)
SERVICE_CONFIG_FILE : str
    Path to service configuration file (alternative to --service-config-file)
"""

from snowflake_mcp.server import main

__version__ = "1.0.0"
__all__ = ["main"]