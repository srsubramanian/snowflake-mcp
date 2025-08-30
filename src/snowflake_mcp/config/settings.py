# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Configuration management for Snowflake MCP Server.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from pydantic import BaseModel, Field

from snowflake_mcp.core.exceptions import ConfigurationError


class SQLStatementPermissions(BaseModel):
    """SQL statement permissions configuration."""
    allowed: List[str] = Field(default_factory=list)
    disallowed: List[str] = Field(default_factory=list)


class ServerConfig(BaseModel):
    """Main server configuration."""
    sql_statement_permissions: SQLStatementPermissions = Field(
        default_factory=SQLStatementPermissions
    )


def unpack_sql_statement_permissions(
    sql_statement_permissions: List[Dict[str, bool]],
) -> Tuple[List[str], List[str]]:
    """Unpack SQL statement permissions into allowed and disallowed lists."""
    allowed = []
    disallowed = []
    
    for statement_dict in sql_statement_permissions:
        for sql_type, is_allowed in statement_dict.items():
            if is_allowed:
                allowed.append(sql_type.lower())
            else:
                disallowed.append(sql_type.lower())
                
    return allowed, disallowed


def load_config_from_file(config_file: str) -> ServerConfig:
    """
    Load configuration from YAML file.
    
    Parameters
    ----------
    config_file : str
        Path to the configuration YAML file
        
    Returns
    -------
    ServerConfig
        Parsed server configuration
        
    Raises
    ------
    ConfigurationError
        If the configuration file cannot be loaded or parsed
    """
    try:
        config_path = Path(config_file).expanduser().resolve()
        
        with open(config_path, "r") as file:
            config_data = yaml.safe_load(file)
            
        # Process SQL statement permissions
        sql_perms = config_data.get("sql_statement_permissions", [])
        allowed, disallowed = unpack_sql_statement_permissions(sql_perms)
        
        return ServerConfig(
            sql_statement_permissions=SQLStatementPermissions(
                allowed=allowed,
                disallowed=disallowed
            )
        )
        
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file not found: {config_file}")
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Error parsing YAML file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Unexpected error loading config: {e}")


def get_login_params() -> Dict[str, List[Any]]:
    """
    Get Snowflake login parameters configuration.

    Returns
    -------
    dict
        Dictionary mapping parameter names to their command line argument definitions
    """
    return {
        "account": [
            "--account",
            "--account-identifier",
            os.getenv("SNOWFLAKE_ACCOUNT"),
            "Your account identifier. The account identifier does not include the snowflakecomputing.com suffix.",
        ],
        "host": ["--host", os.getenv("SNOWFLAKE_HOST"), "Host name."],
        "user": [
            "--user",
            "--username",
            os.getenv("SNOWFLAKE_USER"),
            "Login name for the user.",
        ],
        "password": [
            "--password",
            "--pat",
            os.getenv("SNOWFLAKE_PASSWORD") or os.getenv("SNOWFLAKE_PAT"),
            "Password for the user.",
        ],
        "role": [
            "--role",
            os.getenv("SNOWFLAKE_ROLE"),
            "Name of the role to use.",
        ],
        "warehouse": [
            "--warehouse",
            os.getenv("SNOWFLAKE_WAREHOUSE"),
            "Name of the warehouse to use.",
        ],
        "passcode_in_password": [
            "--passcode-in-password",
            None,
            "False by default. Set this to True if the MFA passcode is embedded in the login password.",
        ],
        "passcode": [
            "--passcode",
            os.getenv("SNOWFLAKE_PASSCODE"),
            "The passcode provided by Duo when using MFA for login.",
        ],
        "private_key": [
            "--private-key",
            os.getenv("SNOWFLAKE_PRIVATE_KEY"),
            "The private key used for authentication.",
        ],
        "private_key_file": [
            "--private-key-file",
            os.getenv("SNOWFLAKE_PRIVATE_KEY_FILE"),
            "Specifies the path to the private key file for the specified user.",
        ],
        "private_key_pwd": [
            "--private-key-pwd",
            os.getenv("SNOWFLAKE_PRIVATE_KEY_PWD"),
            "Specifies the passphrase to decrypt the private key file for the specified user.",
        ],
        "authenticator": [
            "--authenticator",
            None,
            """Authenticator for Snowflake (see documentation for full list of options)""",
        ],
        "connection_name": [
            "--connection-name",
            None,
            "Name of the connection in Snowflake configuration file to use.",
        ],
    }


async def load_tools_config_resource(file_path: str) -> str:
    """
    Load tools configuration from YAML file as JSON string.

    Parameters
    ----------
    file_path : str
        Path to the YAML configuration file

    Returns
    -------
    str
        JSON string representation of the configuration
    """
    with open(file_path, "r") as file:
        tools_config = yaml.safe_load(file)
    return json.dumps(tools_config)