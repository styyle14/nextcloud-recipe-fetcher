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
    calories: str | None = None
    carbohydrateContent: str | None = None
    cholesterolContent: str | None = None
    fatContent: str | None = None
    fiberContent: str | None = None
    proteinContent: str | None = None
    saturatedFatContent: str | None = None
    servingSize: str | None = None
    sodiumContent: str | None = None
    sugarContent: str | None = None
    transFatContent: str | None = None
    unsaturatedFatContent: str | None = None


class JustTheRecipe(BaseModel):
    """Represents a complete recipe."""

    version: str = "1.0.0"
    id: str
    name: str
    sourceUrl: str
    servings: int
    cookTime: int | None = 0
    prepTime: int | None = 0
    totalTime: int | None = 0
    categories: list[str] = Field(default_factory=list)
    cuisines: list[str] = Field(default_factory=list)
    imageUrls: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
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

    def model_post_init(self, __context: Any) -> None:
        """Calculate total time if not provided."""
        if self.totalTime == 0:
            self.totalTime = (self.prepTime or 0) + (self.cookTime or 0)
