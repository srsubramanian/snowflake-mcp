# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Snowflake connection management for MCP server.
"""

import json
import logging
import os
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional, Tuple

from snowflake.connector import DictCursor, connect
from snowflake.core import Root

from snowflake_mcp.core.environment import get_spcs_container_token, is_running_in_spcs_container
from snowflake_mcp.core.exceptions import AuthenticationError, ConnectionError

logger = logging.getLogger(__name__)

# Used to quantify Snowflake usage
server_name = "snowflake-mcp-minimal"
tag_major_version = 1
tag_minor_version = 0
query_tag = {"origin": "sf_sit", "name": "mcp_server_minimal"}


class SnowflakeConnectionManager:
    """
    Manages Snowflake connections and authentication for the MCP server.
    
    This class handles all Snowflake authentication and connection logic,
    automatically detecting the environment (container vs external) and
    providing appropriate authentication parameters for database connections.
    """

    def __init__(self, connection_params: dict):
        self.connection_params = connection_params
        self.connection: Optional[Any] = None
        self.root: Optional[Root] = None
        self.query_tag = query_tag
        self.tag_major_version = tag_major_version
        self.tag_minor_version = tag_minor_version
        
        # Environment detection for authentication
        self._is_spcs_container = is_running_in_spcs_container()
        
        # Initialize persistent connection
        self.connection = self._get_persistent_connection()
        self.root = Root(self.connection)

    @staticmethod
    def send_initial_query(connection: Any) -> None:
        """Send an initial query to the Snowflake service."""
        with connection.cursor() as cur:
            cur.execute("SELECT 'Snowflake MCP Server Connected'").fetchone()

    def _get_persistent_connection(
        self,
        session_parameters: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Get a persistent Snowflake connection.

        Parameters
        ----------
        session_parameters : dict, optional
            Additional session parameters to add to connection

        Returns
        -------
        connection
            A Snowflake connection object
        """
        try:
            query_tag_params = self.get_query_tag_param()

            if session_parameters is not None:
                if query_tag_params:
                    session_parameters.update(query_tag_params)
            else:
                session_parameters = query_tag_params

            # Get connection parameters based on environment
            if self._is_spcs_container:
                logger.info("Using SPCS container OAuth authentication")
                connection_params = {
                    "host": os.getenv("SNOWFLAKE_HOST"),
                    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
                    "token": get_spcs_container_token(),
                    "authenticator": "oauth",
                }
                connection_params = {
                    k: v for k, v in connection_params.items() if v is not None
                }
            else:
                logger.info("Using external authentication")
                connection_params = self.connection_params.copy()

            # Handle default connection name if no params provided
            if not connection_params:
                connection_params = {
                    "connection_name": os.getenv(
                        "SNOWFLAKE_DEFAULT_CONNECTION_NAME", "default"
                    ),
                }

            connection = connect(
                **connection_params,
                session_parameters=session_parameters,
                client_session_keep_alive=True,
            )
            
            if connection:
                self.send_initial_query(connection)
                return connection
                
        except Exception as e:
            logger.error(f"Error establishing persistent Snowflake connection: {e}")
            raise ConnectionError(f"Failed to establish connection: {e}")

    @contextmanager
    def get_connection(
        self,
        use_dict_cursor: bool = False,
        session_parameters: Optional[Dict[str, Any]] = None,
    ) -> Generator[Tuple[Any, Any], None, None]:
        """
        Get a Snowflake connection with the specified configuration.

        This context manager ensures proper connection handling and cleanup.
        It automatically detects the environment and uses appropriate authentication.

        Parameters
        ----------
        use_dict_cursor : bool, default=False
            Whether to use DictCursor instead of regular cursor
        session_parameters : dict, optional
            Additional session parameters to add to connection such as query tag

        Yields
        ------
        tuple
            A tuple containing (connection, cursor)
        """
        try:
            if self.connection is None:
                # Get connection parameters based on environment
                if self._is_spcs_container:
                    logger.info("Using SPCS container OAuth authentication")
                    connection_params = {
                        "host": os.getenv("SNOWFLAKE_HOST"),
                        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
                        "token": get_spcs_container_token(),
                        "authenticator": "oauth",
                    }
                    connection_params = {
                        k: v for k, v in connection_params.items() if v is not None
                    }
                else:
                    logger.info("Using external authentication")
                    connection_params = self.connection_params.copy()

                self.connection = connect(
                    **connection_params,
                    session_parameters=session_parameters,
                    client_session_keep_alive=False,
                )

            cursor = (
                self.connection.cursor(DictCursor)
                if use_dict_cursor
                else self.connection.cursor()
            )

            try:
                yield self.connection, cursor
            finally:
                cursor.close()

        except Exception as e:
            logger.error(f"Error establishing Snowflake connection: {e}")
            raise ConnectionError(f"Connection failed: {e}")

    def get_query_tag_param(self) -> Optional[Dict[str, Any]]:
        """Get the query tag parameters for the Snowflake service."""
        if self.query_tag is not None:
            query_tag = self.query_tag.copy()
            if (
                self.tag_major_version is not None
                and self.tag_minor_version is not None
            ):
                query_tag["version"] = {
                    "major": self.tag_major_version,
                    "minor": self.tag_minor_version,
                }

            # Set the query tag in default session parameters
            session_parameters = {"QUERY_TAG": json.dumps(query_tag)}
            return session_parameters
        else:
            return None

    def cleanup(self):
        """Clean up connection resources."""
        if self.connection:
            try:
                logger.info("Closing Snowflake connection...")
                self.connection.close()
            except Exception as e:
                logger.error(f"Error closing Snowflake connection: {e}")


def execute_query(statement: str, connection_manager: SnowflakeConnectionManager):
    """Execute a Snowflake query and return the results using Python connector dictionary cursor."""
    with connection_manager.get_connection(
        use_dict_cursor=True,
        session_parameters=connection_manager.get_query_tag_param(),
    ) as (con, cur):
        cur.execute(statement)
        return cur.fetchall()