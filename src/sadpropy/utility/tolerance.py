from dataclasses import dataclass

@dataclass(frozen=True)
class Tolerance:
    FLOAT = 1e-12                   # Floating-point precision
    LENGTH = 1e-9                   # Coincident points
    DIRECTION = 1e-8                # Local-axis classification
    PARALLEL = 1e-6                 # Parallel vector detection
    ORTHOGONAL = 1e-10              # Rotation matrix validation