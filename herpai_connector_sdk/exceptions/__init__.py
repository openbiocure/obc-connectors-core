"""Exceptions for the HerpAI Connector SDK."""

class ConnectorError(Exception):
    """Base exception for all connector errors."""
    pass

class AuthenticationError(ConnectorError):
    """Raised when authentication fails."""
    pass

class RateLimitExceeded(ConnectorError):
    """Raised when API rate limit is exceeded."""
    pass

class FetchError(ConnectorError):
    """Raised when fetching data fails."""
    def __init__(self, id: str, message: str):
        self.id = id
        super().__init__(f"Failed to fetch {id}: {message}")

class ParseError(ConnectorError):
    """Raised when parsing response data fails."""
    pass

__all__ = [
    'ConnectorError',
    'AuthenticationError',
    'RateLimitExceeded',
    'FetchError',
    'ParseError'
] 