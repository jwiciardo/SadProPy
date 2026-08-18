import warnings

__all__ = ["ValidationError", "warningtext"]

class ValidationError(Exception):
    """Raised when validation fails."""



def warningtext(text):
    """Warning raised when an operation fails but can continue."""
    warnings.warn(text, UserWarning, stacklevel=2)