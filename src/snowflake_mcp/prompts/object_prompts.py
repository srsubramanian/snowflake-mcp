# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Prompt templates for Snowflake object management tools.
"""


def create_object_prompt(object_type: str) -> str:
    """Generate prompt for create object tool."""
    return f"""Create a new Snowflake {object_type} object."""


def drop_object_prompt(object_type: str) -> str:
    """Generate prompt for drop object tool."""
    return f"""Drop a Snowflake {object_type} object."""


def create_or_alter_object_prompt(object_type: str) -> str:
    """Generate prompt for create or alter object tool."""
    return f"""Update a Snowflake {object_type} object if it exists. Otherwise, create a new Snowflake {object_type} object."""


def describe_object_prompt(object_type: str) -> str:
    """Generate prompt for describe object tool."""
    return f"""Describe a Snowflake {object_type} object."""


def list_objects_prompt(object_type: str) -> str:
    """Generate prompt for list objects tool."""
    return f"""List Snowflake {object_type} objects."""