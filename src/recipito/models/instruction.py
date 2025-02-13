"""Models for recipe instructions."""

from typing import Any
from typing import Union

from pydantic import BaseModel


class JustTheRecipeStep(BaseModel):
    """Represents a single step in recipe instructions."""

    name: str
    text: Union[str, None] = None
    type: str = "step"

    def __init__(self, **data: Any) -> None:
        if "text" not in data and "name" in data:
            data["text"] = data["name"]
        super().__init__(**data)


class JustTheRecipeInstructionGroup(BaseModel):
    """Represents a group of related recipe steps."""

    steps: Union[list[JustTheRecipeStep], None] = None
    name: str
    type: str = "group"

    def __init__(self, **data: Any) -> None:
        if not data.get("steps") and "name" in data:
            data["steps"] = [{"name": data["name"], "type": "step"}]
        super().__init__(**data)
