from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

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
    plurality_dependents: List[Dict[str, str]] = Field(default_factory=list)

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
    items: List[JustTheRecipeItem] = Field(default_factory=list)
    quantities: List[JustTheRecipeQuantity] = Field(default_factory=list)
    units: List[JustTheRecipeUnit] = Field(default_factory=list)
    sizes: List[Any] = Field(default_factory=list)
    type: str = "default"

class JustTheRecipeStep(BaseModel):
    """Represents a single step in recipe instructions."""
    name: str
    text: str
    type: str = "step"

class JustTheRecipeInstructionGroup(BaseModel):
    """Represents a group of related recipe steps."""
    steps: List[JustTheRecipeStep]
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
    categories: List[str]
    cuisines: List[str]
    imageUrls: List[str]
    keywords: List[str]
    ingredients: List[JustTheRecipeIngredient]
    instructions: List[JustTheRecipeInstructionGroup]
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
    nutrition: JustTheRecipeNutritionInfo
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