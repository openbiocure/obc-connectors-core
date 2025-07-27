class ConnectorError(Exception):
    """Base exception class for connector-related errors."""
    
    def __init__(self, message: str, *args, **kwargs):
        """Initialize the connector error.
        
        Args:
            message: Error message describing what went wrong.
            *args: Additional positional arguments for Exception.
            **kwargs: Additional keyword arguments for Exception.
        """
        super().__init__(message, *args)
        self.message = message 