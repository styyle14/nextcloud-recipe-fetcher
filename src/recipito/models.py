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
    text: str | None = None  # Make text optional
    type: str = "step"

    def __init__(self, **data):
        # If text is not provided, use name as text
        if "text" not in data and "name" in data:
            data["text"] = data["name"]
        super().__init__(**data)


class JustTheRecipeInstructionGroup(BaseModel):
    """Represents a group of related recipe steps."""

    steps: list[JustTheRecipeStep] | None = None  # Make steps optional
    name: str
    type: str = "group"

    def __init__(self, **data):
        # If steps is not provided but we have name/type, create a single step
        if not data.get("steps") and "name" in data:
            data["steps"] = [{"name": data["name"], "type": "step"}]
        super().__init__(**data)


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
    instructions: list[JustTheRecipeInstructionGroup | JustTheRecipeStep]  # Allow either type
    source: str = "fromUrl"

    def __init__(self, **data):
        # Convert simple instruction steps to groups if needed
        if "instructions" in data:
            instructions = []
            for instr in data["instructions"]:
                if isinstance(instr, dict) and "steps" not in instr:
                    # Convert single step to group
                    instructions.append({
                        "steps": [instr],
                        "name": instr.get("name", ""),
                        "type": "group"
                    })
                else:
                    instructions.append(instr)
            data["instructions"] = instructions
        super().__init__(**data)


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
        # Extract json.dumps kwargs
        json_kwargs = {
            "indent": kwargs.pop("indent", 2)
        }
        
        # Get model data with remaining kwargs
        data = self.model_dump(by_alias=True, **kwargs)
        
        # Format datetime fields
        for field in ["dateModified", "dateCreated", "datePublished"]:
            if field in data and data[field] is not None:
                data[field] = data[field].strftime("%Y-%m-%dT%H:%M:%S+0000")
        
        # Return JSON string
        return json.dumps(data, **json_kwargs)
