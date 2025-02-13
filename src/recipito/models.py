from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class RecipeItem(BaseModel):
    """Represents a recipe ingredient item's properties."""
    density: float
    state: str

class RecipeQuantity(BaseModel):
    """Represents a quantity in a recipe."""
    start: int
    end: int
    value: float
    unit: int = 0
    plurality_dependents: List[Dict[str, str]] = Field(default_factory=list)

class RecipeUnit(BaseModel):
    """Represents a unit of measurement in a recipe."""
    start: int
    end: int
    id: str
    display_type: str
    item: int = 0

class RecipeIngredient(BaseModel):
    """Represents an ingredient in a recipe."""
    name: str
    items: List[RecipeItem] = Field(default_factory=list)
    quantities: List[RecipeQuantity] = Field(default_factory=list)
    units: List[RecipeUnit] = Field(default_factory=list)
    sizes: List[Any] = Field(default_factory=list)
    type: str = "default"

class RecipeStep(BaseModel):
    """Represents a single step in recipe instructions."""
    name: str
    text: str
    type: str = "step"

class RecipeInstructionGroup(BaseModel):
    """Represents a group of related recipe steps."""
    steps: List[RecipeStep]
    name: str
    type: str = "group"

class NutritionInfo(BaseModel):
    """Represents nutrition information."""
    type: str = Field(alias="@type", default="NutritionInformation")

class Recipe(BaseModel):
    """Represents a complete recipe."""
    version: str = "1.0.0"
    id: str
    name: str
    sourceUrl: str
    servings: int
    cookTime: int
    prepTime: int
    totalTime: int
    categories: List[str]
    cuisines: List[str]
    imageUrls: List[str]
    keywords: List[str]
    ingredients: List[RecipeIngredient]
    instructions: List[RecipeInstructionGroup]
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
    tool: List[str] = Field(default_factory=list)
    recipeIngredient: List[str]
    recipeInstructions: List[str]
    nutrition: NutritionInfo
    context: str = Field(alias="@context", default="http://schema.org")
    type: str = Field(alias="@type", default="Recipe")
    dateModified: datetime
    dateCreated: datetime
    datePublished: Optional[datetime] = None
    printImage: bool = True
    imageUrl: str = "/apps/cookbook/webapp/recipes/{}/image?size=full"

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S+0000")
        } 