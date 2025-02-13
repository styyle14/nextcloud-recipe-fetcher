"""Models for recipe data."""

from typing import Any

from pydantic import BaseModel
from pydantic import Field


class JustTheRecipeStep(BaseModel):
    """Represents a single step in recipe instructions."""

    name: str
    text: str | None = None
    type: str = "step"

    def __init__(self, **data: Any) -> None:
        if "text" not in data and "name" in data:
            data["text"] = data["name"]
        super().__init__(**data)


class JustTheRecipeInstructionGroup(BaseModel):
    """Represents a group of related recipe steps."""

    steps: list[JustTheRecipeStep] | None = None
    name: str
    type: str = "group"

    def __init__(self, **data: Any) -> None:
        if not data.get("steps") and "name" in data:
            data["steps"] = [{"name": data["name"], "type": "step"}]
        super().__init__(**data)


class JustTheRecipeIngredient(BaseModel):
    """Represents a recipe ingredient."""

    name: str


class JustTheRecipeNutritionInfo(BaseModel):
    """Represents nutrition information."""

    type: str = Field(alias="@type", default="NutritionInformation")


class JustTheRecipe(BaseModel):
    """Represents a complete recipe."""

    version: str = "1.0.0"
    id: str
    name: str
    sourceUrl: str
    servings: int
    cookTime: int
    prepTime: int
    totalTime: int
    categories: list[str]
    cuisines: list[str]
    imageUrls: list[str]
    keywords: list[str]
    ingredients: list[JustTheRecipeIngredient]
    instructions: list[JustTheRecipeInstructionGroup | JustTheRecipeStep]
    source: str = "fromUrl"

    def __init__(self, **data: Any) -> None:
        # Convert simple instruction steps to groups if needed
        if "instructions" in data:
            instructions: list[dict[str, Any]] = []
            for instr in data["instructions"]:
                if isinstance(instr, dict) and "steps" not in instr:
                    instruction_dict = instr
                    name_raw: str = instruction_dict.get("name", "")

                    group_data = {
                        "steps": [instruction_dict],
                        "name": name_raw,
                        "type": "group",
                    }
                    instructions.append(group_data)
                else:
                    instructions.append(instr)
            data["instructions"] = instructions
        super().__init__(**data)
