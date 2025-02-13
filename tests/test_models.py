"""Tests for recipe models."""

from datetime import UTC
from datetime import datetime

from recipito.models import JustTheRecipe
from recipito.models import JustTheRecipeInstructionGroup
from recipito.models import JustTheRecipeNutritionInfo
from recipito.models import JustTheRecipeStep
from recipito.models import NextcloudRecipe


def test_recipe_step_initialization() -> None:
    """Test JustTheRecipeStep initialization."""
    step = JustTheRecipeStep(name="Test Step")
    assert step.name == "Test Step"
    assert step.text == "Test Step"  # Should copy name to text
    assert step.type == "step"


def test_instruction_group_initialization() -> None:
    """Test JustTheRecipeInstructionGroup initialization."""
    group = JustTheRecipeInstructionGroup(name="Test Group")
    assert group.name == "Test Group"
    assert group.type == "group"
    assert group.steps is not None  # Check steps is not None first
    assert len(group.steps) == 1
    assert group.steps[0].name == "Test Group"


def test_recipe_conversion() -> None:
    """Test recipe conversion logic."""
    recipe_data = {
        "id": "test-id",
        "name": "Test Recipe",
        "sourceUrl": "https://example.com",
        "servings": 4,
        "cookTime": 1800000000,
        "prepTime": 1800000000,
        "totalTime": 3600000000,
        "categories": ["Main Course"],
        "cuisines": ["American"],
        "imageUrls": ["https://example.com/image.jpg"],
        "keywords": ["test"],
        "ingredients": [{"name": "test ingredient"}],
        "instructions": [{"name": "test step", "type": "step"}],
        "source": "fromUrl",
    }

    recipe = JustTheRecipe(**recipe_data)
    assert recipe.name == "Test Recipe"
    assert len(recipe.instructions) == 1
    assert isinstance(recipe.instructions[0], JustTheRecipeInstructionGroup)


def test_nextcloud_recipe_serialization() -> None:
    """Test NextcloudRecipe JSON serialization."""
    now = datetime.now(UTC)
    recipe = NextcloudRecipe(
        id="test",
        name="Test Recipe",
        url="https://example.com",
        prepTime="PT30M",
        cookTime="PT30M",
        totalTime="PT1H",
        recipeCategory="Main Course",
        recipeYield=4,
        recipeIngredient=["test ingredient"],
        recipeInstructions=["test step"],
        dateModified=now,
        dateCreated=now,
        nutrition=JustTheRecipeNutritionInfo(),  # Add required nutrition field
    )

    json_data = recipe.model_dump_json()
    assert "test" in json_data
    assert "Test Recipe" in json_data
    assert now.strftime("%Y-%m-%dT%H:%M:%S+0000") in json_data
