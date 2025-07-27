from .connector_error import ConnectorError

class RateLimitError(ConnectorError):
    """Exception raised when a connector hits its rate limit."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: float = 60.0, *args, **kwargs):
        """Initialize the rate limit error.
        
        Args:
            message: Error message describing what went wrong.
            retry_after: Number of seconds to wait before retrying.
            *args: Additional positional arguments for ConnectorError.
            **kwargs: Additional keyword arguments for ConnectorError.
        """
        super().__init__(message, *args, **kwargs)
        self.retry_after = retry_after 