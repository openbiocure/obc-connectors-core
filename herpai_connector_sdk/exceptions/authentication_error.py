from .connector_error import ConnectorError

class AuthenticationError(ConnectorError):
    """Exception raised when authentication with a data source fails."""
    
    def __init__(self, message: str = "Authentication failed", *args, **kwargs):
        """Initialize the authentication error.
        
        Args:
            message: Error message describing what went wrong.
            *args: Additional positional arguments for ConnectorError.
            **kwargs: Additional keyword arguments for ConnectorError.
        """
        super().__init__(message, *args, **kwargs) 