"""Custom exceptions for the OpenBioCure Connector SDK."""


class ConnectorError(Exception):
    """Base exception for connector-related errors."""

    pass


class AuthenticationError(ConnectorError):
    """Exception raised for authentication failures."""

    def __init__(self, message="Authentication failed", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class RateLimitExceeded(ConnectorError):
    """Exception raised when rate limits are exceeded."""

    def __init__(self, message="Rate limit exceeded", retry_after=None, *args, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, *args, **kwargs)


class FetchError(ConnectorError):
    """Exception raised when document fetching fails."""

    def __init__(self, document_id, message="Failed to fetch document", *args, **kwargs):
        self.document_id = document_id
        super().__init__(f"{message}: {document_id}", *args, **kwargs)


class ParseError(ConnectorError):
    """Exception raised when document parsing fails."""

    def __init__(self, document_id, message="Failed to parse document", *args, **kwargs):
        self.document_id = document_id
        super().__init__(f"{message}: {document_id}", *args, **kwargs)
