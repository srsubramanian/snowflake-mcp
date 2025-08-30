# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Main Snowflake MCP Server implementation.
"""

import argparse
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from snowflake_mcp.config.settings import (
    ServerConfig,
    get_login_params,
    load_config_from_file,
    load_tools_config_resource,
)
from snowflake_mcp.core.connection import SnowflakeConnectionManager
from snowflake_mcp.core.exceptions import ConfigurationError
from snowflake_mcp.tools.objects import initialize_object_manager_tools
from snowflake_mcp.tools.sql import initialize_query_manager_tool
from snowflake_mcp.tools.semantic import initialize_semantic_manager_tools

logger = logging.getLogger(__name__)


class SnowflakeService:
    """
    Snowflake service for the MCP server.
    
    Manages configuration, connection, and tool initialization.
    """

    def __init__(
        self,
        service_config_file: str,
        transport: str,
        connection_params: dict,
    ):
        self.service_config_file = str(Path(service_config_file).expanduser().resolve())
        self.config_path_uri = Path(self.service_config_file).as_uri()
        self.transport = transport
        
        # Load configuration
        self.config = load_config_from_file(self.service_config_file)
        
        # Initialize connection manager
        self.connection_manager = SnowflakeConnectionManager(connection_params)

    def cleanup(self):
        """Clean up service resources."""
        if self.connection_manager:
            self.connection_manager.cleanup()


def get_var(var_name: str, env_var_name: str, args) -> Optional[str]:
    """
    Retrieve variable value from command line arguments or environment variables.
    """
    if getattr(args, var_name):
        return getattr(args, var_name)
    if env_var_name in os.environ:
        return os.environ[env_var_name]
    return None


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Snowflake MCP Server")

    login_params = get_login_params()

    for value in login_params.values():
        parser.add_argument(
            *value[:-2], required=False, default=value[-2], help=value[-1]
        )

    parser.add_argument(
        "--service-config-file",
        required=False,
        help="Path to service specification file",
    )
    parser.add_argument(
        "--transport",
        required=False,
        choices=["stdio", "sse", "streamable-http"],
        help="Transport for the MCP server",
        default="stdio",
    )

    return parser.parse_args()


def create_lifespan(args):
    """Create a lifespan function with captured arguments."""

    @asynccontextmanager
    async def create_snowflake_service(
        server: FastMCP,
    ) -> AsyncIterator[SnowflakeService]:
        """
        Create main entry point for the Snowflake MCP server package.
        """
        connection_params = {
            key: getattr(args, key)
            for key in get_login_params().keys()
            if getattr(args, key) is not None
        }
        
        service_config_file = get_var(
            "service_config_file", "SERVICE_CONFIG_FILE", args
        )
        
        if not service_config_file:
            raise ConfigurationError(
                "Service configuration file must be specified via --service-config-file or SERVICE_CONFIG_FILE environment variable"
            )

        snowflake_service = None
        try:
            snowflake_service = SnowflakeService(
                service_config_file=service_config_file,
                transport=args.transport,
                connection_params=connection_params,
            )

            # Initialize tools and resources
            logger.info("Initializing tools and resources...")
            initialize_tools(snowflake_service, server)
            initialize_resources(snowflake_service, server)

            yield snowflake_service
            
        except Exception as e:
            logger.error(f"Error creating Snowflake service: {e}")
            raise

        finally:
            if snowflake_service is not None:
                snowflake_service.cleanup()

    return create_snowflake_service


def initialize_resources(snowflake_service: SnowflakeService, server: FastMCP):
    """Initialize MCP resources."""
    @server.resource(snowflake_service.config_path_uri)
    async def get_tools_config():
        """
        Tools Specification Configuration.

        Provides access to the YAML tools configuration file as JSON.
        """
        tools_config = await load_tools_config_resource(
            snowflake_service.service_config_file
        )
        return tools_config


def initialize_tools(snowflake_service: SnowflakeService, server: FastMCP):
    """Initialize MCP tools."""
    if snowflake_service is not None:
        # Add tools for object manager
        initialize_object_manager_tools(server, snowflake_service.connection_manager.root)

        # Add tools for query manager
        initialize_query_manager_tool(server, snowflake_service.connection_manager)

        # Add tools for semantic manager
        initialize_semantic_manager_tools(server, snowflake_service.connection_manager)


def main():
    """Main entry point for the Snowflake MCP Server."""
    args = parse_arguments()

    # Create server with lifespan that has access to args
    server = FastMCP("Snowflake MCP Server", lifespan=create_lifespan(args))

    try:
        logger.info("Starting Snowflake MCP Server...")

        if args.transport and args.transport in [
            "sse",
            "streamable-http",
        ]:
            logger.info(f"Starting server with transport: {args.transport}")
            server.run(transport=args.transport, host="0.0.0.0", port=9000)
        else:
            logger.info(f"Starting server with transport: {args.transport or 'stdio'}")
            server.run(transport=args.transport or "stdio")

    except Exception as e:
        logger.error(f"Error starting MCP server: {e}")
        raise


if __name__ == "__main__":
    main()