"""Base recipe models."""

from typing import Any
from typing import Union
from typing import cast

from pydantic import BaseModel
from pydantic import Field

from .instruction import JustTheRecipeInstructionGroup
from .instruction import JustTheRecipeStep
from .just_the_recipe import JustTheRecipeIngredient


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
    instructions: list[Union[JustTheRecipeInstructionGroup, JustTheRecipeStep]]
    source: str = "fromUrl"

    def __init__(self, **data: Any) -> None:
        # Convert simple instruction steps to groups if needed
        if "instructions" in data:
            instructions: list[dict[str, Any]] = []
            for instr in data["instructions"]:
                if isinstance(instr, dict) and "steps" not in instr:
                    instruction_dict = cast(dict[str, Any], instr)
                    name_raw: str = instruction_dict.get("name", "")

                    group_data = {
                        "steps": [instruction_dict],
                        "name": name_raw,
                        "type": "group",
                    }
                    instructions.append(group_data)
                else:
                    typed_instr = cast(dict[str, Any], instr)
                    instructions.append(typed_instr)
            data["instructions"] = instructions
        super().__init__(**data)
