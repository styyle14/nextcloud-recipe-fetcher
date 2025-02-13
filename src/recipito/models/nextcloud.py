"""Nextcloud recipe models."""

import json

from datetime import UTC
from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field

from recipito.utils import convert_characters

from .just_the_recipe import JustTheRecipe
from .just_the_recipe import JustTheRecipeInstructionGroup
from .just_the_recipe import JustTheRecipeNutritionInfo


class NextcloudRecipe(BaseModel):
    """Represents a recipe in Nextcloud format."""

    id: str
    name: str
    description: str = ""
    url: str
    image: str = ""
    prepTime: str
    cookTime: str
    totalTime: str
    recipeCategory: str
    keywords: str = ""
    recipeYield: int
    tool: list[str] = Field(default_factory=list)
    recipeIngredient: list[str]
    recipeInstructions: list[str]
    nutrition: JustTheRecipeNutritionInfo
    context: str = Field(alias="@context", default="http://schema.org")
    type: str = Field(alias="@type", default="Recipe")
    dateModified: datetime
    dateCreated: datetime
    datePublished: datetime | None = None
    printImage: bool = True
    imageUrl: str = "/apps/cookbook/webapp/recipes/{}/image?size=full"

    def model_dump_json(self, **kwargs: Any) -> str:
        """Override JSON serialization to handle datetime."""
        # Extract json.dumps kwargs
        json_kwargs = {"indent": kwargs.pop("indent", 2)}

        # Get model data with remaining kwargs
        data = self.model_dump(by_alias=True, **kwargs)

        # Format datetime fields
        for field in ["dateModified", "dateCreated", "datePublished"]:
            if field in data and data[field] is not None:
                data[field] = data[field].strftime("%Y-%m-%dT%H:%M:%S+0000")

        # Return JSON string
        return json.dumps(data, **json_kwargs)


def convert_to_nextcloud_format(raw_recipe: dict[str, Any], category: str = "Main Course") -> dict[str, Any]:
    """Convert raw recipe JSON to Nextcloud recipes format."""
    recipe = JustTheRecipe(**raw_recipe)
    now = datetime.now(tz=UTC)

    # Convert ingredients with fraction handling
    ingredients = [convert_characters(ingredient.name) for ingredient in recipe.ingredients]

    # Convert instructions to simple text
    instructions: list[str] = []
    for instruction in recipe.instructions:
        if isinstance(instruction, JustTheRecipeInstructionGroup) and instruction.steps:
            for step in instruction.steps:
                text = step.text if step.text is not None else step.name
                instructions.append(convert_characters(text))

    # Create and validate Nextcloud recipe format
    nextcloud_recipe = NextcloudRecipe(
        id=recipe.id,
        name=recipe.name,
        url=recipe.sourceUrl,
        prepTime=str(recipe.prepTime),
        cookTime=str(recipe.cookTime),
        totalTime=str(recipe.totalTime),
        recipeCategory=category,
        recipeYield=recipe.servings,
        recipeIngredient=ingredients,
        recipeInstructions=instructions,
        nutrition=JustTheRecipeNutritionInfo(),
        dateModified=now,
        dateCreated=now,
    )

    return nextcloud_recipe.model_dump(by_alias=True)
