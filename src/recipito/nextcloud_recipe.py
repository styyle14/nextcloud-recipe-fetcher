import json
import shutil
import requests

from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from recipito.logger import logger

from .models import JustTheRecipe
from .models import JustTheRecipeNutritionInfo
from .models import NextcloudRecipe


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""

    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%dT%H:%M:%S+0000")
        return super().default(o)


def convert_to_nextcloud_format(raw_recipe: dict[str, Any]) -> dict[str, Any]:
    """Convert raw recipe JSON to Nextcloud recipes format."""
    logger.info("Converting recipe to Nextcloud format")
    # Validate input recipe format
    recipe = JustTheRecipe(**raw_recipe)
    now = datetime.now(timezone.utc)

    # Convert time from nanoseconds to "PTxHyMzS" format
    def format_time(ns: int) -> str:
        if not ns:
            return "PT0H0M0S"
        seconds = ns // 1_000_000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"PT{hours}H{minutes}M{seconds}S"

    # Convert unicode fractions to standard fractions
    def convert_characters(text: str) -> str:
        """Convert unicode fractions and symbols to standard text."""
        fraction_map = {
            "\u00bc": "1/4",
            "\u00bd": "1/2",
            "\u00be": "3/4",
            "\u2153": "1/3",
            "\u2154": "2/3",
            "\u2155": "1/5",
            "\u2156": "2/5",
            "\u2157": "3/5",
            "\u2158": "4/5",
            "\u2159": "1/6",
            "\u215a": "5/6",
            "\u215b": "1/8",
            "\u215c": "3/8",
            "\u215d": "5/8",
            "\u215e": "7/8",
            "\u00b0": "°",  # Convert unicode degree symbol to standard degree symbol
        }
        for unicode_char, replacement in fraction_map.items():
            text = text.replace(unicode_char, replacement)
        return text

    # Convert ingredients with fraction handling
    ingredients = [convert_characters(ingredient.name) for ingredient in recipe.ingredients]

    # Create and validate Nextcloud recipe format
    nextcloud_recipe = NextcloudRecipe(
        id=str(recipe.id)[:5],
        name=recipe.name,
        description="",
        url=recipe.sourceUrl,
        image="",
        prepTime=format_time(recipe.prepTime),
        cookTime=format_time(recipe.cookTime),
        totalTime=format_time(recipe.totalTime),
        recipeCategory=", ".join(recipe.categories),
        keywords="",
        recipeYield=recipe.servings,
        tool=[],
        recipeIngredient=ingredients,
        recipeInstructions=[convert_characters(step.text) for group in recipe.instructions for step in group.steps],
        nutrition=JustTheRecipeNutritionInfo(),
        dateModified=now,
        dateCreated=now,
        datePublished=None,
        printImage=True,
        imageUrl="/apps/cookbook/webapp/recipes/{}/image?size=full",
    )

    return nextcloud_recipe.model_dump(by_alias=True)


def save_nextcloud_recipe(title: str, recipe_json: str) -> None:
    """
    Save recipe in Nextcloud recipes format.

    Args:
        title: The webpage title to use for directory name
        recipe_json: The JSON string containing recipe data
    """
    logger.info("Saving recipe: %s", title)
    # Create base directory for Nextcloud recipes
    nextcloud_dir = Path("output") / "nextcloud_recipes"
    nextcloud_dir.mkdir(parents=True, exist_ok=True)

    # Create recipe directory using sanitized title
    recipe_dir = nextcloud_dir / title

    # Remove existing directory if it exists
    if recipe_dir.exists():
        shutil.rmtree(recipe_dir)

    recipe_dir.mkdir()

    # Parse raw JSON and convert to Nextcloud format
    raw_recipe = json.loads(recipe_json)
    nextcloud_recipe = NextcloudRecipe(**convert_to_nextcloud_format(raw_recipe))

    # Save recipe.json with custom encoder for datetime
    recipe_path = recipe_dir / "recipe.json"
    recipe_path.write_text(nextcloud_recipe.model_dump_json())

    # Try to download and save the first image
    if raw_recipe.get("imageUrls") and raw_recipe["imageUrls"]:
        image_url = raw_recipe["imageUrls"][0]
        try:
            logger.info("Downloading image from: %s", image_url)
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Save the image as recipe.jpg regardless of original format
            image_path = recipe_dir / "recipe.jpg"
            image_path.write_bytes(response.content)
            logger.info("Image saved to: %s", image_path)
            
            # Update the recipe.json with the image path
            nextcloud_recipe.image = "recipe.jpg"
            recipe_path.write_text(nextcloud_recipe.model_dump_json())
            
        except Exception as e:
            logger.error("Failed to download image: %s", e)

    logger.info("Recipe saved successfully")
