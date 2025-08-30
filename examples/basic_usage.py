#!/usr/bin/env python3
"""
Basic usage example for Snowflake MCP Server.

This example demonstrates how to use the Snowflake MCP server
with various operations like querying data, managing objects,
and working with semantic views.
"""

import asyncio
import os
from pathlib import Path

# This would be used if running the server programmatically
# For normal usage, you'd run the server via CLI and connect with an MCP client

def main():
    print("=== Snowflake MCP Server - Basic Usage Example ===\n")
    
    print("1. Server Configuration:")
    print("   - Set up your Snowflake credentials as environment variables")
    print("   - Create a configuration file (see configs/minimal.yaml)")
    print("   - Run the server with: uv run snowflake-mcp-minimal\n")
    
    print("2. Available Tools:")
    print("   Object Management:")
    print("   - create_table, create_view, create_database, etc.")
    print("   - drop_table, drop_view, drop_database, etc.")
    print("   - describe_table, describe_view, etc.")
    print("   - list_tables, list_views, list_databases, etc.")
    print()
    
    print("   SQL Execution:")
    print("   - run_snowflake_query")
    print()
    
    print("   Semantic Views:")
    print("   - list_semantic_views")
    print("   - describe_semantic_view")
    print("   - query_semantic_view")
    print("   - show_semantic_dimensions")
    print("   - show_semantic_metrics")
    print()
    
    print("3. Example Operations:")
    print("   # List all databases")
    print("   run_snowflake_query('SHOW DATABASES')")
    print()
    
    print("   # Create a simple table")
    print("   create_table({")
    print("       'name': 'my_table',")
    print("       'database': 'MY_DB',")
    print("       'schema': 'PUBLIC',")
    print("       'columns': [")
    print("           {'name': 'id', 'data_type': 'NUMBER'},")
    print("           {'name': 'name', 'data_type': 'VARCHAR(100)'}]")
    print("   })")
    print()
    
    print("   # Query semantic view")
    print("   query_semantic_view(")
    print("       database_name='MY_DB',")
    print("       schema_name='PUBLIC',")
    print("       view_name='sales_semantic_view',")
    print("       dimensions=[{'table': 'dim_date', 'name': 'year'}],")
    print("       metrics=[{'table': 'fact_sales', 'name': 'total_sales'}]")
    print("   )")
    print()
    
    print("4. Configuration Example:")
    config_path = Path(__file__).parent.parent / "configs" / "minimal.yaml"
    print(f"   See: {config_path}")
    print()
    
    print("5. Claude Desktop Integration:")
    print("   Add to your Claude Desktop configuration:")
    print('   {')
    print('     "mcpServers": {')
    print('       "snowflake": {')
    print('         "command": "uv",')
    print('         "args": [')
    print('           "--directory", "/path/to/your/project",')
    print('           "run", "snowflake-mcp-minimal",')
    print('           "--service-config-file", "configs/minimal.yaml"')
    print('         ]')
    print('       }')
    print('     }')
    print('   }')


if __name__ == "__main__":
    main()