# Snowflake MCP Tools Documentation

This package provides a comprehensive set of MCP (Model Context Protocol) tools for managing Snowflake objects, executing SQL queries, and working with Semantic Views. All tools are automatically registered with the MCP server and can be invoked by LLMs through the protocol.

## Tool Categories

- **[Object Management Tools](#object-management-tools)**: Create, modify, delete, and describe Snowflake objects
- **[SQL Execution Tools](#sql-execution-tools)**: Execute arbitrary SQL queries with permission control
- **[Semantic View Tools](#semantic-view-tools)**: Discover, describe, and query Snowflake Semantic Views

---

## Object Management Tools

Object management tools provide full lifecycle management for Snowflake objects using the Snowflake Core API. These tools are automatically generated for all supported object types.

### Supported Object Types

- **`database`** - Snowflake databases
- **`schema`** - Database schemas  
- **`table`** - Data tables
- **`view`** - Views and secure views
- **`warehouse`** - Compute warehouses
- **`computepool`** - Snowpark Container Services compute pools
- **`role`** - Security roles
- **`user`** - User accounts
- **`stage`** - Internal and external stages
- **`imagerepository`** - Container image repositories

### Tool Patterns

For each object type, the following tools are automatically generated:

#### `create_{object_type}`
Creates a new Snowflake object.

**Parameters:**
- `target_object`: Object specification (see object models below)
- `mode`: Creation mode - `"error_if_exists"` (default), `"replace"`, `"if_not_exists"`

**Example:**
```json
{
  "name": "create_table",
  "arguments": {
    "target_object": {
      "name": "sales_data",
      "database_name": "ANALYTICS",
      "schema_name": "PUBLIC", 
      "columns": [
        {"name": "id", "datatype": "NUMBER", "nullable": false},
        {"name": "amount", "datatype": "DECIMAL(10,2)", "nullable": true},
        {"name": "date", "datatype": "DATE", "nullable": false}
      ],
      "kind": "PERMANENT"
    },
    "mode": "error_if_exists"
  }
}
```

#### `drop_{object_type}`  
Drops an existing Snowflake object.

**Parameters:**
- `target_object`: Object identification (minimally requires `name` and location fields)
- `if_exists`: Boolean to suppress errors if object doesn't exist

**Example:**
```json
{
  "name": "drop_table",
  "arguments": {
    "target_object": {
      "name": "old_table",
      "database_name": "ANALYTICS", 
      "schema_name": "PUBLIC"
    },
    "if_exists": true
  }
}
```

#### `describe_{object_type}`
Fetches detailed metadata about an existing object.

**Parameters:**
- `target_object`: Object identification

**Example:**
```json
{
  "name": "describe_warehouse",
  "arguments": {
    "target_object": {
      "name": "COMPUTE_WH"
    }
  }
}
```

#### `list_{object_type}s`
Lists objects of the specified type with optional filtering.

**Parameters:**
- `target_object`: Container specification (database, schema as applicable)
- `like`: Optional pattern filter for object names

**Example:**
```json
{
  "name": "list_tables",
  "arguments": {
    "target_object": {
      "database_name": "ANALYTICS",
      "schema_name": "PUBLIC"
    },
    "like": "sales_%"
  }
}
```

#### `create_or_alter_{object_type}`
Creates a new object or modifies an existing one.

**Parameters:**
- `target_object`: Complete object specification

**Example:**
```json
{
  "name": "create_or_alter_warehouse",
  "arguments": {
    "target_object": {
      "name": "COMPUTE_WH",
      "warehouse_size": "MEDIUM",
      "auto_suspend": 300,
      "auto_resume": "true"
    }
  }
}
```

### Object Models

Each object type has a corresponding Pydantic model defining its properties:

#### SnowflakeTable
```python
{
  "name": str,                           # Required
  "database_name": str,                  # Required
  "schema_name": str,                    # Required  
  "kind": "PERMANENT" | "TRANSIENT",     # Default: "PERMANENT"
  "columns": [SnowflakeTableColumn],     # For creation only
  "data_retention_time_in_days": int,    # 0-89 days
  "comment": str                         # Optional
}
```

#### SnowflakeWarehouse  
```python
{
  "name": str,                                    # Required
  "warehouse_type": "STANDARD" | "SNOWPARK-OPTIMIZED",  # Default: "STANDARD" 
  "warehouse_size": str,                          # X-SMALL to 4X-LARGE
  "auto_suspend": int,                           # Minutes  
  "auto_resume": "true" | "false",
  "initially_suspended": "true" | "false",
  "max_cluster_count": int,
  "min_cluster_count": int,
  "scaling_policy": "STANDARD" | "ECONOMY",
  "statement_timeout_in_seconds": int,
  "comment": str
}
```

#### SnowflakeDatabase
```python
{
  "name": str,                           # Required
  "kind": "PERMANENT" | "TRANSIENT",     # Default: "PERMANENT"
  "data_retention_time_in_days": int,    # 0-89 days
  "comment": str
}
```

*See `src/snowflake_mcp/models/snowflake_objects.py` for complete object model specifications.*

---

## SQL Execution Tools

SQL execution tools allow running arbitrary SQL statements with configurable permission controls.

### `run_snowflake_query`

Executes SQL statements and returns results using dictionary cursors for easy access.

**Parameters:**
- `statement`: SQL query string to execute

**Return Value:**
- List of dictionaries with column names as keys and row values

**Example:**
```json
{
  "name": "run_snowflake_query", 
  "arguments": {
    "statement": "SELECT customer_id, SUM(amount) as total FROM sales WHERE date >= '2024-01-01' GROUP BY customer_id LIMIT 10"
  }
}
```

**Response:**
```json
[
  {"CUSTOMER_ID": 1001, "TOTAL": 15750.50},
  {"CUSTOMER_ID": 1002, "TOTAL": 8920.25},
  {"CUSTOMER_ID": 1003, "TOTAL": 22100.00}
]
```

### SQL Permission Control

SQL execution is controlled by the service configuration file. Statement types are validated using SQLGlot parsing:

**Configuration Example (`services/configuration.yaml`):**
```yaml
sql_statement_permissions:
  - select: true      # Allow SELECT statements
  - show: true        # Allow SHOW commands  
  - describe: true    # Allow DESCRIBE commands
  - use: true         # Allow USE commands
  - create: false     # Deny CREATE statements
  - drop: false       # Deny DROP statements  
  - insert: false     # Deny INSERT statements
  - update: false     # Deny UPDATE statements
  - delete: false     # Deny DELETE statements
  - unknown: false    # Deny unrecognized statement types
```

### Supported Statement Types

The following SQL statement types are recognized and can be controlled:

- **Data Query**: `SELECT`, `WITH`, `SHOW`, `DESCRIBE`, `EXPLAIN`
- **Data Modification**: `INSERT`, `UPDATE`, `DELETE`, `MERGE`  
- **Schema Definition**: `CREATE`, `ALTER`, `DROP`
- **Session Management**: `USE`, `SET`
- **Transaction Control**: `BEGIN`, `COMMIT`, `ROLLBACK`
- **Security**: `GRANT`, `REVOKE`
- **Unknown**: Any unrecognized statement type

---

## Semantic View Tools

Semantic view tools provide discovery, querying, and metadata access for Snowflake Semantic Views.

### `list_semantic_views`

Lists semantic views with flexible scoping options.

**Parameters:**
- `database_name`: Database to search in (optional)
- `schema_name`: Schema to search in (optional) 
- `like`: Pattern filter for view names (optional)
- `starts_with`: Prefix filter for view names (optional)

**Scoping Options:**
- No parameters: Lists all semantic views in account
- `database_name` only: Lists views in database
- `database_name` + `schema_name`: Lists views in specific schema

**Example:**
```json
{
  "name": "list_semantic_views",
  "arguments": {
    "database_name": "ANALYTICS",
    "schema_name": "SEMANTIC",
    "like": "sales"
  }
}
```

### `describe_semantic_view`

Provides detailed metadata about a semantic view including dimensions, metrics, and structure.

**Parameters:**
- `view_name`: Name of the semantic view (required)
- `database_name`: Database name (required)
- `schema_name`: Schema name (required)

**Example:**
```json
{
  "name": "describe_semantic_view",
  "arguments": {
    "view_name": "sales_metrics",
    "database_name": "ANALYTICS", 
    "schema_name": "SEMANTIC"
  }
}
```

### `show_semantic_dimensions`

Lists all dimensions available in a semantic view.

**Parameters:**
- `database_name`: Database name (required)
- `schema_name`: Schema name (required) 
- `view_name`: Semantic view name (required)
- `like`: Pattern filter (optional)
- `starts_with`: Prefix filter (optional)

**Example:**
```json
{
  "name": "show_semantic_dimensions",
  "arguments": {
    "database_name": "ANALYTICS",
    "schema_name": "SEMANTIC", 
    "view_name": "sales_metrics"
  }
}
```

### `show_semantic_metrics`

Lists all metrics available in a semantic view.

**Parameters:**
Same as `show_semantic_dimensions`

### `get_semantic_view_ddl`

Retrieves the DDL (Data Definition Language) for a semantic view.

**Parameters:**
- `view_name`: Semantic view name (required)
- `database_name`: Database name (required)
- `schema_name`: Schema name (required)

**Example:**
```json
{
  "name": "get_semantic_view_ddl",
  "arguments": {
    "view_name": "sales_metrics",
    "database_name": "ANALYTICS",
    "schema_name": "SEMANTIC" 
  }
}
```

### `write_semantic_view_query_tool`

Generates a properly formatted SEMANTIC_VIEW query based on specified dimensions, metrics, and filters.

**Parameters:**
- `database_name`: Database name (required)
- `schema_name`: Schema name (required)
- `view_name`: Semantic view name (required)
- `dimensions`: List of dimension specifications (optional)
- `metrics`: List of metric specifications (optional) 
- `facts`: List of fact specifications (optional)
- `where_clause`: WHERE conditions without the WHERE keyword (optional)
- `order_by`: ORDER BY clause without keywords (optional)
- `limit`: Row limit (optional)

**SemanticExpression Model:**
```python
{
  "table": str,        # Logical table name
  "name": str          # Dimension/metric/fact name
}
```

**Query Rules:**
- Must specify at least one of: dimensions, metrics, or facts
- Cannot use both facts and metrics in the same query
- When using facts + dimensions, all must be from the same logical table

**Example:**
```json
{
  "name": "write_semantic_view_query_tool",
  "arguments": {
    "database_name": "ANALYTICS",
    "schema_name": "SEMANTIC",
    "view_name": "sales_metrics",
    "dimensions": [
      {"table": "time_dim", "name": "year"},
      {"table": "product_dim", "name": "category"}
    ],
    "metrics": [
      {"table": "sales_fact", "name": "total_revenue"},
      {"table": "sales_fact", "name": "avg_order_value"}
    ],
    "where_clause": "year >= 2023",
    "order_by": "total_revenue DESC", 
    "limit": 100
  }
}
```

**Generated Query:**
```sql
SELECT * FROM SEMANTIC_VIEW (
    ANALYTICS.SEMANTIC.sales_metrics
    DIMENSIONS time_dim.year, product_dim.category
    METRICS sales_fact.total_revenue, sales_fact.avg_order_value
) WHERE year >= 2023 ORDER BY total_revenue DESC LIMIT 100
```

### `query_semantic_view`

Executes a semantic view query and returns the results. Uses the same parameters as `write_semantic_view_query_tool` but executes the query and returns data.

**Example:**
```json
{
  "name": "query_semantic_view",
  "arguments": {
    "database_name": "ANALYTICS", 
    "schema_name": "SEMANTIC",
    "view_name": "sales_metrics",
    "dimensions": [{"table": "time_dim", "name": "year"}],
    "metrics": [{"table": "sales_fact", "name": "total_revenue"}],
    "limit": 5
  }
}
```

**Response:**
```json
[
  {"YEAR": 2024, "TOTAL_REVENUE": 1250000.00},
  {"YEAR": 2023, "TOTAL_REVENUE": 980000.00}, 
  {"YEAR": 2022, "TOTAL_REVENUE": 850000.00}
]
```

---

## Error Handling

All tools implement comprehensive error handling through the `SnowflakeException` class:

- **Authentication errors**: Invalid credentials or expired tokens
- **Permission errors**: Insufficient privileges for requested operation
- **Object not found**: Referenced objects don't exist  
- **SQL errors**: Invalid syntax or runtime query errors
- **Configuration errors**: Invalid parameters or missing required fields
- **Connection errors**: Network or service availability issues

Error responses include:
```json
{
  "error": {
    "tool": "tool_name",
    "message": "Detailed error description", 
    "status_code": 500
  }
}
```

---

## Usage Examples

### Creating a Complete Analytics Environment

```json
// 1. Create database
{
  "name": "create_database",
  "arguments": {
    "target_object": {
      "name": "ANALYTICS_DB",
      "kind": "PERMANENT",
      "comment": "Analytics database for sales reporting"
    }
  }
}

// 2. Create schema  
{
  "name": "create_schema",
  "arguments": {
    "target_object": {
      "name": "SALES",
      "database_name": "ANALYTICS_DB",
      "kind": "PERMANENT" 
    }
  }
}

// 3. Create warehouse
{
  "name": "create_warehouse", 
  "arguments": {
    "target_object": {
      "name": "ANALYTICS_WH",
      "warehouse_size": "LARGE",
      "auto_suspend": 300,
      "auto_resume": "true"
    }
  }
}

// 4. Create sales table
{
  "name": "create_table",
  "arguments": {
    "target_object": {
      "name": "sales_transactions",
      "database_name": "ANALYTICS_DB",
      "schema_name": "SALES",
      "columns": [
        {"name": "transaction_id", "datatype": "VARCHAR(50)", "nullable": false},
        {"name": "customer_id", "datatype": "NUMBER", "nullable": false},
        {"name": "product_id", "datatype": "VARCHAR(20)", "nullable": false},
        {"name": "quantity", "datatype": "NUMBER", "nullable": false},
        {"name": "unit_price", "datatype": "DECIMAL(10,2)", "nullable": false},
        {"name": "transaction_date", "datatype": "TIMESTAMP", "nullable": false}
      ]
    }
  }
}
```

### Advanced SQL Analytics  

```json
// Complex analytical query
{
  "name": "run_snowflake_query",
  "arguments": {
    "statement": "WITH monthly_sales AS (SELECT DATE_TRUNC('MONTH', transaction_date) as month, SUM(quantity * unit_price) as revenue FROM ANALYTICS_DB.SALES.sales_transactions WHERE transaction_date >= DATEADD('YEAR', -1, CURRENT_DATE()) GROUP BY 1), growth_rates AS (SELECT month, revenue, LAG(revenue) OVER (ORDER BY month) as prev_month_revenue, ((revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month)) * 100 as growth_rate FROM monthly_sales) SELECT month, revenue, COALESCE(growth_rate, 0) as growth_rate FROM growth_rates ORDER BY month"
  }
}
```

### Semantic View Analytics

```json
// Query semantic view for executive dashboard
{
  "name": "query_semantic_view",
  "arguments": {
    "database_name": "ANALYTICS_DB",
    "schema_name": "SEMANTIC", 
    "view_name": "executive_metrics",
    "dimensions": [
      {"table": "time_dim", "name": "quarter"},
      {"table": "region_dim", "name": "region_name"},
      {"table": "product_dim", "name": "category"}
    ],
    "metrics": [
      {"table": "sales_metrics", "name": "total_revenue"},
      {"table": "sales_metrics", "name": "units_sold"},
      {"table": "customer_metrics", "name": "new_customers"}
    ],
    "where_clause": "quarter IN ('2024-Q1', '2024-Q2', '2024-Q3')",
    "order_by": "quarter, region_name, total_revenue DESC",
    "limit": 50
  }
}
```

---

## Integration Notes

### Permission Configuration
All tools respect the permission settings defined in the service configuration file. Ensure proper permissions are set for your use case:

- **Development**: Enable most operations for flexibility
- **Production**: Restrict to read-only operations for safety
- **Analytics**: Enable SELECT, SHOW, DESCRIBE for data exploration

### Connection Management  
Tools automatically use the connection manager configured at server startup:

- **Object tools**: Use Snowflake Core API through the `root` object
- **SQL tools**: Use raw connection with dictionary cursors  
- **Semantic tools**: Use raw connection for specialized SEMANTIC_VIEW syntax

### Model Validation
All object parameters are validated using Pydantic models before execution:

- Type checking and coercion  
- Required field validation
- Enum value validation
- Range validation for numeric fields
- JSON string parsing support for LLM compatibility

This comprehensive toolset provides full Snowflake management capabilities through the MCP protocol, enabling LLMs to perform complex database operations, analytics, and semantic data exploration.