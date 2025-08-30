# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Input validation utilities for Snowflake MCP Server.
"""

import re
from typing import Any, Dict, List

from snowflake_mcp.core.exceptions import SnowflakeException


def sanitize_tool_name(service_name: str) -> str:
    """Sanitize service name to create a valid Python identifier for MCP tool name."""
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", service_name)
    if sanitized and sanitized[0].isdigit():
        sanitized = f"service_{sanitized}"
    return sanitized


def validate_identifier(name: str, context: str = "object") -> str:
    """
    Validate that a string is a valid Snowflake identifier.
    
    Parameters
    ----------
    name : str
        The identifier to validate
    context : str
        Context for error messages (e.g., "table", "database")
        
    Returns
    -------
    str
        The validated identifier
        
    Raises
    ------
    SnowflakeException
        If the identifier is invalid
    """
    if not name or not isinstance(name, str):
        raise SnowflakeException(
            tool="validate_identifier",
            message=f"Invalid {context} name: must be a non-empty string"
        )
    
    # Check length (Snowflake identifiers can be up to 255 characters)
    if len(name) > 255:
        raise SnowflakeException(
            tool="validate_identifier",
            message=f"Invalid {context} name: exceeds 255 character limit"
        )
    
    # Check for valid characters (letters, digits, underscores, and dollars)
    if not re.match(r'^[A-Za-z_$][A-Za-z0-9_$]*$', name):
        raise SnowflakeException(
            tool="validate_identifier",
            message=f"Invalid {context} name: must start with letter, underscore, or dollar sign and contain only letters, digits, underscores, and dollar signs"
        )
    
    return name


def validate_sql_permissions(
    function_name: str,
    sql_allow_list: List[str],
    sql_disallow_list: List[str]
) -> tuple[str, bool]:
    """
    Validate SQL permissions for a function call.
    
    Parameters
    ----------
    function_name : str
        Name of the function being called
    sql_allow_list : List[str]
        List of allowed SQL statement types
    sql_disallow_list : List[str]
        List of disallowed SQL statement types
        
    Returns
    -------
    tuple[str, bool]
        Tuple of (statement_type, is_valid)
    """
    # Extract statement type from function name
    func_lower = function_name.lower()
    
    if func_lower.startswith("create"):
        stmt_type = "create"
    elif func_lower.startswith("drop"):
        stmt_type = "drop"
    elif func_lower.startswith("alter"):
        stmt_type = "alter"
    elif func_lower.startswith("list") or func_lower.startswith("show"):
        stmt_type = "select"
    elif func_lower.startswith("describe"):
        stmt_type = "select"
    elif func_lower.startswith("query") or func_lower.startswith("run"):
        stmt_type = "select"
    else:
        stmt_type = "unknown"
    
    # Check permissions
    if not sql_allow_list and not sql_disallow_list:
        # No permissions configured - default to deny all
        return stmt_type, False
    
    if "all" in sql_allow_list:
        return stmt_type, True
    
    if stmt_type in sql_disallow_list:
        return stmt_type, False
    
    if stmt_type in sql_allow_list:
        return stmt_type, True
    
    if stmt_type == "unknown" and "unknown" in sql_allow_list:
        return stmt_type, True
    
    # Default to deny
    return stmt_type, False


def validate_connection_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate Snowflake connection parameters.
    
    Parameters
    ----------
    params : Dict[str, Any]
        Connection parameters to validate
        
    Returns
    -------
    Dict[str, Any]
        Validated connection parameters
        
    Raises
    ------
    SnowflakeException
        If required parameters are missing or invalid
    """
    required_params = ["account"]
    missing_params = [param for param in required_params if not params.get(param)]
    
    if missing_params:
        raise SnowflakeException(
            tool="validate_connection_params",
            message=f"Missing required connection parameters: {', '.join(missing_params)}"
        )
    
    # Validate account format (basic check)
    account = params.get("account", "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', account):
        raise SnowflakeException(
            tool="validate_connection_params",
            message="Invalid account identifier format"
        )
    
    return params