"""Models for recipe data."""

from typing import Any

from pydantic import BaseModel
from pydantic import Field


class JustTheRecipeStep(BaseModel):
    """Represents a single step in recipe instructions."""

    text: str | None = None
    name: str | None = None  # Make name optional
    type: str = "step"

    def model_post_init(self, __context: Any) -> None:
        """Ensure either text or name is present."""
        if self.text is None and self.name is None:
            raise ValueError("Either text or name must be provided")
        if self.text is None:
            self.text = self.name
        if self.name is None:
            self.name = self.text


class JustTheRecipeInstructionGroup(BaseModel):
    """Represents a group of related recipe steps."""

    steps: list[JustTheRecipeStep] | None = None
    name: str | None = None  # Make name optional
    type: str = "group"

    def model_post_init(self, __context: Any) -> None:
        """Convert single step to list if needed."""
        if not self.steps and self.name:
            self.steps = [JustTheRecipeStep(name=self.name, type="step")]


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
    """Represents a recipe from justtherecipe.com."""

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
    instructions: list[dict[str, Any]]  # Raw dictionaries
    source: str = "fromUrl"

    def model_post_init(self, __context: Any) -> None:
        """Calculate total time if not provided and convert instructions."""
        if self.totalTime == 0:
            self.totalTime = (self.prepTime or 0) + (self.cookTime or 0)

        # Convert raw instruction dictionaries to proper objects
        converted_instructions = []
        for instruction in self.instructions:
            if isinstance(instruction, dict):
                if instruction.get("steps"):
                    # It's a group
                    converted_instructions.append(JustTheRecipeInstructionGroup(**instruction))
                else:
                    # It's a single step
                    if "text" in instruction:
                        # Use text as both text and name if name is missing
                        instruction_copy = instruction.copy()
                        if "name" not in instruction_copy:
                            instruction_copy["name"] = instruction_copy["text"]
                        converted_instructions.append(JustTheRecipeStep(**instruction_copy))
            else:
                converted_instructions.append(instruction)
        self.instructions = converted_instructions
