"""Models for recipe data structures."""

from typing import Any

from pydantic import BaseModel
from pydantic import Field


class JustTheRecipeItem(BaseModel):
    """Represents a recipe ingredient item's properties."""

    density: float
    state: str


class JustTheRecipeQuantity(BaseModel):
    """Represents a quantity in a recipe."""

    start: int
    end: int
    value: float
    unit: int = 0
    plurality_dependents: list[dict[str, Any]] = Field(default_factory=list)


class JustTheRecipeUnit(BaseModel):
    """Represents a unit of measurement in a recipe."""

    start: int
    end: int
    id: str
    display_type: str
    item: int = 0


class JustTheRecipeIngredient(BaseModel):
    """Represents an ingredient in a recipe."""

    name: str
    items: list[JustTheRecipeItem] = Field(default_factory=list)
    quantities: list[JustTheRecipeQuantity] = Field(default_factory=list)
    units: list[JustTheRecipeUnit] = Field(default_factory=list)
    sizes: list[Any] = Field(default_factory=list)
    type: str = "default"
