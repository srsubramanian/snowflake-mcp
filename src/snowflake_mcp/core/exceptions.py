# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Custom exceptions for Snowflake MCP Server.
"""

from typing import Optional


class SnowflakeException(Exception):
    """
    Custom exception class for Snowflake API errors.

    Provides enhanced error handling for Snowflake operations
    with specific error messages based on HTTP status codes and error types.

    Parameters
    ----------
    tool : str
        Name of the tool that generated the error
    message : str
        Raw error message from the API
    status_code : int, optional
        HTTP status code from the API response, by default None

    Attributes
    ----------
    tool : str
        The service that generated the error
    message : str
        Original error message from the API
    status_code : int|None
        HTTP status code associated with the error
    """

    def __init__(self, tool: str, message, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        self.tool = tool
        super().__init__(message)

    def __str__(self):
        """
        Format error message based on status code and error content.

        Returns
        -------
        str
            Formatted error message with tool name, description, and guidance
        """
        if self.status_code is None:
            return f"{self.tool} Error: An error has occurred.\n\nError Message: {self.message} "
        else:
            if self.status_code == 400:
                if "unknown model" in self.message:
                    return f"{self.tool} Error: Selected model not available or invalid.\n\nError Message: {self.message} "
                else:
                    return f"{self.tool} Error: The resource cannot be found.\n\nError Message: {self.message} "
            elif self.status_code == 401:
                return f"{self.tool} Error: An authorization error occurred.\n\nError Message: {self.message} "
            else:
                return f"{self.tool} Error: An error has occurred.\n\nError Message: {self.message} \n Code: {self.status_code}"


class MissingArgumentsException(Exception):
    """Exception raised when required arguments are missing."""
    
    def __init__(self, missing: list):
        self.missing = missing
        super().__init__(missing)

    def __str__(self):
        from textwrap import dedent
        missing_str = "\n\t\t".join([f"{i}" for i in self.missing])
        message = f"""
        -----------------------------------------------------------------------------------
        Required arguments missing:
        \t{missing_str}
        These values must be specified as command-line arguments or environment variables
        -----------------------------------------------------------------------------------"""
        return dedent(message)


class ConfigurationError(Exception):
    """Exception raised when configuration is invalid."""
    pass


class ConnectionError(SnowflakeException):
    """Exception raised when connection to Snowflake fails."""
    
    def __init__(self, message: str):
        super().__init__("Connection", message)


class AuthenticationError(SnowflakeException):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str):
        super().__init__("Authentication", message, 401)