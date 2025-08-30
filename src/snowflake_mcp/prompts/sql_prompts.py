# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Prompt templates for SQL execution tools.
"""

query_tool_prompt = """Run a SQL query in Snowflake.
DML and DDL queries are supported.
Tool should only be used if other object tools do not suffice."""