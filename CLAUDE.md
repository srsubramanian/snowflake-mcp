# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Snowflake Minimal MCP Server** - a streamlined implementation of the Model Context Protocol (MCP) for Snowflake. It provides three core capabilities: Object Management (58 auto-generated tools for CRUD operations on Snowflake objects), SQL Execution (with permission-based validation), and Semantic View Querying.

The codebase was extracted from the original Snowflake Labs MCP repository, removing all Cortex AI features to create a minimal, focused implementation.

## Development Commands

```bash
# Install dependencies
pip install -e .

# Install development dependencies  
pip install -e ".[dev]"

# Run the server (requires Snowflake credentials)
snowflake-mcp-minimal --account your_account --user your_user --service-config-file configs/minimal.yaml

# Run with external browser authentication (recommended)
snowflake-mcp-minimal --account your_account --user your_user --authenticator externalbrowser --service-config-file configs/minimal.yaml

# Run tests (if pytest available)
python -m pytest tests/

# Type checking (if pyright available)
pyright src/

# Linting (if ruff available) 
ruff check src/
```

## Architecture Overview

### Core Architecture Pattern

The server follows a **layered architecture** with clear separation of concerns:

1. **Server Layer** (`server.py`): FastMCP server initialization, lifespan management, and tool registration
2. **Connection Management** (`core/connection.py`): Handles all Snowflake authentication methods and connection pooling
3. **Configuration System** (`config/settings.py`): YAML-based configuration with SQL permission management
4. **Tool Layers** (`tools/`): Three distinct tool categories with different connection patterns
5. **Model Layer** (`models/`): Pydantic models for validation and serialization

### Key Architectural Decisions

**Dual Connection Pattern**: The system uses two different connection approaches:
- **Object Management**: Uses Snowflake Core API (`root` object) for type-safe object operations
- **SQL/Semantic Tools**: Uses raw Snowflake connector with dictionary cursors for flexible querying

**Auto-Generated Tool Pattern**: Object management tools are dynamically generated using a factory pattern. For each object type in `SnowflakeClasses`, five tools are created: `create_`, `drop_`, `describe_`, `list_`, and `create_or_alter_`.

**Permission Validation Architecture**: 
- SQL statements are parsed using SQLGlot AST analysis
- Custom mapping layer converts SQLGlot node types to user-friendly config names
- Validation occurs at tool execution time, not server startup

### Critical Integration Points

**Server Initialization** (`server.py:165-175`):
```python
def initialize_tools(snowflake_service: SnowflakeService, server: FastMCP):
    # Object tools use root (Core API)
    initialize_object_manager_tools(server, snowflake_service.connection_manager.root)
    
    # SQL tools use connection manager + config for validation
    initialize_query_manager_tool(server, snowflake_service.connection_manager, snowflake_service.config)
    
    # Semantic tools use raw connection
    initialize_semantic_manager_tools(server, snowflake_service.connection_manager)
```

**Authentication Flow** (`core/connection.py:82-130`): The connection manager automatically detects environment (SPCS container vs. external) and applies appropriate authentication method. It handles parameter cleanup for different auth types (removing `password` for externalbrowser, converting `password` to `token` for OAuth, etc.).

**Configuration Loading** (`config/settings.py:48-82`): YAML configuration is parsed into structured permissions with separate `allowed` and `disallowed` lists. The `unpack_sql_statement_permissions` function converts the user-friendly YAML format into the internal validation format.

## Working with the Codebase

### Adding New Object Types
1. Create Pydantic model in `models/snowflake_objects.py` extending `ObjectMetadata`
2. Implement `get_core_object()` and `get_core_path()` methods
3. Add to `SnowflakeClasses` list - tools are auto-generated

### Modifying SQL Permissions
- Edit configuration files in `configs/` directory
- SQL validation logic is in `tools/sql.py:map_statement_type_to_config()`
- New statement types require mapping from SQLGlot AST nodes to config names

### Authentication Methods
All authentication logic is centralized in `SnowflakeConnectionManager`. The system supports externalbrowser (SSO), username/password, key pair, OAuth, MFA, and Okta. Authentication detection and parameter preparation happens in `_prepare_connection_params()`.

### Error Handling Pattern
All tools use `SnowflakeException` for consistent error responses. Validation errors use `403 Forbidden`, connection errors use `500 Internal Server Error`, and configuration errors use `ConfigurationError`.

### Testing Approach
The codebase includes unit tests in `tests/unit/` focusing on authentication methods and connection parameter preparation. Integration testing requires actual Snowflake credentials.

## Configuration Files

- `configs/minimal.yaml` - Basic read-only permissions (recommended starting point)
- `configs/development.yaml` - Extended permissions for development
- `configs/production.yaml` - Restricted permissions for production
- `services/configuration.yaml` - Legacy configuration format

## Tool Documentation

Comprehensive tool documentation is available in `src/snowflake_mcp/tools/README.md` covering all 58+ available MCP tools with parameters, examples, and usage patterns.