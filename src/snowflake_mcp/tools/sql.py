# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
SQL execution tools for Snowflake MCP Server.
"""

from typing import Annotated

import sqlglot
from fastmcp import FastMCP
from pydantic import Field

from snowflake_mcp.core.exceptions import SnowflakeException
from snowflake_mcp.core.connection import SnowflakeConnectionManager
from snowflake_mcp.prompts.sql_prompts import query_tool_prompt


def run_query(statement: str, connection_manager: SnowflakeConnectionManager):
    """
    Execute SQL statement and fetch all results using Snowflake connector.

    Parameters
    ----------
    statement : str
        SQL statement to execute
    connection_manager : SnowflakeConnectionManager
        The Snowflake connection manager instance to use for connection

    Returns
    -------
    list[dict]
        List of dictionaries containing query results with column names as keys

    Raises
    ------
    SnowflakeException
        If connection fails or SQL execution encounters an error
    """
    try:
        with connection_manager.get_connection(
            use_dict_cursor=True,
            session_parameters=connection_manager.get_query_tag_param(),
        ) as (con, cur):
            cur.execute(statement)
            return cur.fetchall()
    except Exception as e:
        raise SnowflakeException(
            tool="query_manager",
            message=f"Error executing query: {e}",
            status_code=500,
        )


def initialize_query_manager_tool(server: FastMCP, connection_manager: SnowflakeConnectionManager, config=None):
    """Initialize SQL query execution tools for the MCP server."""
    
    @server.tool(
        name="run_snowflake_query",
        description=query_tool_prompt,
    )
    def run_query_tool(
        statement: Annotated[
            str,
            Field(description="SQL query to execute"),
        ],
    ):
        # Validate SQL permissions if config is provided
        if config and config.sql_statement_permissions:
            statement_type, is_valid = validate_sql_type(
                statement, 
                config.sql_statement_permissions.allowed,
                config.sql_statement_permissions.disallowed
            )
            
            if not is_valid:
                raise SnowflakeException(
                    tool="run_snowflake_query",
                    message=f"SQL statement type '{statement_type}' is not permitted by configuration",
                    status_code=403,
                )
        
        return run_query(statement, connection_manager)


def get_statement_type(sql_string):
    """
    Parses a SQL statement and returns its primary command type.
    """
    try:
        # Parse the SQL statement. The root of the AST is the statement type.
        expression_tree = sqlglot.parse_one(sql_string)
        # The expression type is the class of the root node.
        statement_type = type(expression_tree).__name__
        return statement_type
    except sqlglot.errors.ParseError:
        # We will map this back to user's Unknown statement type setting
        return "Unknown"


def map_statement_type_to_config(sql_string: str, statement_type: str) -> str:
    """
    Map SQLGlot statement types to configuration-friendly names.
    
    This function handles the mapping between SQLGlot's AST node names 
    and the more intuitive permission names used in configuration files.
    """
    statement_lower = statement_type.lower()
    
    # Handle Snowflake-specific commands that SQLGlot parses as "Command" or "Unknown"
    sql_upper = sql_string.strip().upper()
    
    if statement_lower == "command" or statement_lower == "unknown":
        if sql_upper.startswith("SHOW"):
            return "show"
        elif sql_upper.startswith("DESCRIBE") or sql_upper.startswith("DESC"):
            return "describe"
        elif sql_upper.startswith("USE"):
            return "use"
        elif sql_upper.startswith("EXPLAIN"):
            return "explain"
        elif sql_upper.startswith("GRANT"):
            return "grant"
        elif sql_upper.startswith("REVOKE"):
            return "revoke"
        elif sql_upper.startswith("SET"):
            return "set"
        elif sql_upper.startswith("CALL"):
            return "call"
        else:
            return "unknown"
    
    # Direct mapping for standard SQL statement types
    return statement_lower


def validate_sql_type(
    sql_string: str, sql_allow_list: list[str], sql_disallow_list: list[str]
) -> tuple[str, bool]:
    """
    Validates a SQL statement type against a list of allowed and disallowed statement types.
    """
    raw_statement_type = get_statement_type(sql_string)
    statement_type = map_statement_type_to_config(sql_string, raw_statement_type)
    
    if "all" in sql_allow_list:
        # Escape hatch for allowing all statements if user elects to explicitly
        valid = True
    elif statement_type in sql_disallow_list:
        # Allow/Disallow lists should already be lowercase at load
        valid = False
    elif statement_type in sql_allow_list:
        valid = True
    # There may be a new unmapped type that is not in the allow/disallow lists. 
    # If the user has set Unknown to True, allow it.
    elif statement_type == "unknown" and "unknown" in sql_allow_list:
        valid = True
    # User has not added any permissions, so we default to disallowing all statements
    elif len(sql_allow_list) == 0 and len(sql_disallow_list) == 0:
        valid = False
    else:
        # If not in allowed or disallowed and unknown in disallow or omitted, return error. 
        # User can always add to list as they find statements not otherwise allowed.
        valid = False

    return (statement_type, valid)