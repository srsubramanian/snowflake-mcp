# Snowflake Minimal MCP Server

A minimal implementation of the Snowflake Model Context Protocol (MCP) Server that provides only the core functionality for:

- **Object Management**: Create, alter, drop, describe, and list Snowflake objects (tables, views, warehouses, etc.)
- **SQL Execution**: Execute SQL statements with configurable permissions
- **Semantic View Querying**: Discover and query Snowflake Semantic Views

This implementation **excludes** all Cortex AI features (Cortex Search, Cortex Analyst, etc.) from the original [Snowflake Labs MCP repository](https://github.com/Snowflake-Labs/mcp).

## Features

### Object Management
- Create, alter, and drop Snowflake objects
- List and describe objects with filtering options
- Support for all major Snowflake object types:
  - Tables, Views, Materialized Views
  - Warehouses, Databases, Schemas
  - Functions, Procedures, Streams, Tasks
  - And many more

### SQL Execution
- Execute arbitrary SQL statements
- Configurable statement-type permissions
- Support for SELECT, INSERT, UPDATE, DELETE, DDL statements
- SQL parsing and validation using SQLGlot

### Semantic View Querying
- List semantic views in account, database, or schema
- Describe semantic view structure and metadata
- Show semantic dimensions and metrics
- Generate and execute semantic view queries
- Get semantic view DDL

## Installation

```bash
# Clone this repository
git clone <repository-url>
cd snowflake-mcp

# Install dependencies
pip install -e .
```

## Configuration

Create a YAML configuration file to define SQL statement permissions:

```yaml
# services/configuration.yaml
sql_statement_permissions:
  - select: true
  - show: true  
  - describe: true
  - use: true
  - create: false  # Set to true to allow object creation
  - drop: false    # Set to true to allow object deletion
  - unknown: false # Handle unknown statement types
```

## Usage

### Command Line

```bash
# Using connection parameters
mcp-server-snowflake-minimal \
  --account your_account \
  --user your_username \
  --password your_password \
  --service-config-file services/configuration.yaml

# Using environment variables
export SNOWFLAKE_ACCOUNT=your_account
export SNOWFLAKE_USER=your_username  
export SNOWFLAKE_PASSWORD=your_password
export SERVICE_CONFIG_FILE=services/configuration.yaml

mcp-server-snowflake-minimal
```

### Environment Variables

The server supports all standard Snowflake connection parameters:

- `SNOWFLAKE_ACCOUNT`: Account identifier
- `SNOWFLAKE_USER`: Username
- `SNOWFLAKE_PASSWORD`: Password or Personal Access Token
- `SNOWFLAKE_ROLE`: Role to use
- `SNOWFLAKE_WAREHOUSE`: Default warehouse
- `SNOWFLAKE_HOST`: Host name (optional)
- `SERVICE_CONFIG_FILE`: Path to configuration file

### Authentication Methods

- **External Browser (SSO/SAML)** - ✨ **Recommended for Enterprise**
- Username/password
- Key pair authentication 
- OAuth
- Multi-factor authentication (MFA)
- Native Okta

📚 **See [AUTHENTICATION.md](docs/AUTHENTICATION.md) for detailed setup instructions**

## Available Tools

### Object Management Tools
- `create_<object_type>`: Create Snowflake objects
- `drop_<object_type>`: Drop Snowflake objects  
- `describe_<object_type>`: Get object details
- `list_<object_type>s`: List objects with filtering
- `create_or_alter_<object_type>`: Create or modify objects

### SQL Execution Tools
- `run_snowflake_query`: Execute SQL statements

### Semantic View Tools
- `list_semantic_views`: List semantic views
- `describe_semantic_view`: Get semantic view details
- `show_semantic_dimensions`: Show semantic dimensions
- `show_semantic_metrics`: Show semantic metrics
- `query_semantic_view`: Query semantic views
- `write_semantic_view_query_tool`: Generate semantic view queries
- `get_semantic_view_ddl`: Get semantic view DDL

## Supported Object Types

- Tables (`table`)
- Views (`view`) 
- Materialized Views (`materialized_view`)
- Warehouses (`warehouse`)
- Databases (`database`)
- Schemas (`schema`)
- Functions (`function`)
- Procedures (`procedure`)
- Streams (`stream`)
- Tasks (`task`)
- File Formats (`file_format`)
- Stages (`stage`)
- Pipes (`pipe`)
- Sequences (`sequence`)
- And more...

## Example Usage

```python
# List all tables in a database
list_tables({"database": "MY_DB", "schema": "PUBLIC"})

# Create a new table
create_table({
    "name": "test_table",
    "database": "MY_DB", 
    "schema": "PUBLIC",
    "columns": [
        {"name": "id", "data_type": "NUMBER"},
        {"name": "name", "data_type": "VARCHAR(100)"}
    ]
})

# Execute a SQL query
run_snowflake_query("SELECT * FROM MY_DB.PUBLIC.test_table LIMIT 10")

# Query a semantic view
query_semantic_view(
    database_name="MY_DB",
    schema_name="PUBLIC", 
    view_name="my_semantic_view",
    dimensions=[{"table": "dim_table", "name": "category"}],
    metrics=[{"table": "fact_table", "name": "sales_amount"}]
)
```

## Differences from Original

This minimal implementation differs from the original Snowflake Labs MCP server by:

### Removed Features
- Cortex Search functionality
- Cortex Analyst functionality  
- All AI/ML related tools and services
- Complex response parsing for Cortex APIs
- Cortex-specific authentication and headers

### Retained Core Features
- Object management tools
- SQL execution with permissions
- Semantic view querying
- Connection management
- Authentication (all methods)
- Configuration system
- Error handling

### Dependencies Removed
- `requests` (used for Cortex API calls)
- Cortex-specific imports and modules

## License

Licensed under the Apache License, Version 2.0. See the original [Snowflake Labs MCP repository](https://github.com/Snowflake-Labs/mcp) for the full license terms.