# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Schema browser resources for Snowflake MCP Server.

Provides resources for browsing and exploring Snowflake schemas, databases, and objects.
"""

from typing import List, Optional

from snowflake_mcp.core.connection import SnowflakeConnectionManager, execute_query
from snowflake_mcp.core.exceptions import SnowflakeException


class SchemaBrowser:
    """Browse Snowflake database schemas and objects."""
    
    def __init__(self, connection_manager: SnowflakeConnectionManager):
        self.connection_manager = connection_manager

    def list_databases(self, like: Optional[str] = None) -> List[dict]:
        """List all databases in the account."""
        statement = "SHOW DATABASES"
        if like:
            statement += f" LIKE '%{like}%'"
        
        try:
            return execute_query(statement, self.connection_manager)
        except Exception as e:
            raise SnowflakeException(tool="list_databases", message=str(e))

    def list_schemas(self, database: Optional[str] = None, like: Optional[str] = None) -> List[dict]:
        """List schemas in a database or account."""
        statement = "SHOW SCHEMAS"
        
        if database:
            statement += f" IN DATABASE {database}"
        else:
            statement += " IN ACCOUNT"
            
        if like:
            statement += f" LIKE '%{like}%'"
        
        try:
            return execute_query(statement, self.connection_manager)
        except Exception as e:
            raise SnowflakeException(tool="list_schemas", message=str(e))

    def list_tables(
        self, 
        database: Optional[str] = None, 
        schema: Optional[str] = None, 
        like: Optional[str] = None
    ) -> List[dict]:
        """List tables in a schema, database, or account."""
        statement = "SHOW TABLES"
        
        if database and schema:
            statement += f" IN SCHEMA {database}.{schema}"
        elif database:
            statement += f" IN DATABASE {database}"
        else:
            statement += " IN ACCOUNT"
            
        if like:
            statement += f" LIKE '%{like}%'"
        
        try:
            return execute_query(statement, self.connection_manager)
        except Exception as e:
            raise SnowflakeException(tool="list_tables", message=str(e))

    def list_views(
        self, 
        database: Optional[str] = None, 
        schema: Optional[str] = None, 
        like: Optional[str] = None
    ) -> List[dict]:
        """List views in a schema, database, or account."""
        statement = "SHOW VIEWS"
        
        if database and schema:
            statement += f" IN SCHEMA {database}.{schema}"
        elif database:
            statement += f" IN DATABASE {database}"
        else:
            statement += " IN ACCOUNT"
            
        if like:
            statement += f" LIKE '%{like}%'"
        
        try:
            return execute_query(statement, self.connection_manager)
        except Exception as e:
            raise SnowflakeException(tool="list_views", message=str(e))

    def describe_table(self, table_name: str, database: str, schema: str) -> List[dict]:
        """Describe the structure of a table."""
        statement = f"DESCRIBE TABLE {database}.{schema}.{table_name}"
        
        try:
            return execute_query(statement, self.connection_manager)
        except Exception as e:
            raise SnowflakeException(tool="describe_table", message=str(e))

    def get_table_sample(
        self, 
        table_name: str, 
        database: str, 
        schema: str, 
        limit: int = 10
    ) -> List[dict]:
        """Get a sample of data from a table."""
        statement = f"SELECT * FROM {database}.{schema}.{table_name} LIMIT {limit}"
        
        try:
            return execute_query(statement, self.connection_manager)
        except Exception as e:
            raise SnowflakeException(tool="get_table_sample", message=str(e))