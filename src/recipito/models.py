import json

from datetime import datetime
from typing import Any
from typing import Optional

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


class JustTheRecipeStep(BaseModel):
    """Represents a single step in recipe instructions."""

    name: str
    text: str
    type: str = "step"


class JustTheRecipeInstructionGroup(BaseModel):
    """Represents a group of related recipe steps."""

    steps: list[JustTheRecipeStep]
    name: str
    type: str = "group"


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
    instructions: list[JustTheRecipeInstructionGroup]
    source: str = "fromUrl"


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
    datePublished: Optional[datetime] = None
    printImage: bool = True
    imageUrl: str = "/apps/cookbook/webapp/recipes/{}/image?size=full"

    def model_dump_json(self, **kwargs: Any) -> str:
        """Override JSON serialization to handle datetime."""
        kwargs.setdefault("indent", 2)
        data = self.model_dump(mode="json", **kwargs)
        for field in ["dateModified", "dateCreated", "datePublished"]:
            if field in data and data[field] is not None:
                data[field] = data[field].strftime("%Y-%m-%dT%H:%M:%S+0000")
        return json.dumps(data, **kwargs)
