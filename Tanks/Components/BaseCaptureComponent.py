from dataclasses import dataclass


@dataclass
class BaseCaptureComponent:
    """
    Component that stores the base capture points of an entity.

    Attributes:
        capturePoints: The current number of capture points.
    """
    capturePoints: int = 0
