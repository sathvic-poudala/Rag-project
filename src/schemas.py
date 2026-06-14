from dataclasses import dataclass, field
from typing import Any

@dataclass
class CustomDocument: 
    """
    A container for a piece of code or documentation.
    Ensures every chunk sent to the vector database has the exact same structure.
    """
    content: str

    metadata: dict[str,Any] = field(default_factory=dict)