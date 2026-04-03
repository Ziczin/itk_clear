class BaseAppError(Exception):
    """Base application exception with configurable message and default fallback."""

    default_message = "Application error occurred"

    def __init__(self, message: str = ""):
        full_message = (
            f"{self.default_message}"
            if not message
            else f"{self.default_message}: {message}"
        )
        super().__init__(full_message)
