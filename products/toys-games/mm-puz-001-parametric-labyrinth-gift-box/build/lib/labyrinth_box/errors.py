"""Feature-specific errors that do not import optional dependencies."""


class ImageReliefError(RuntimeError):
    """Base class for actionable image-relief generation failures."""
