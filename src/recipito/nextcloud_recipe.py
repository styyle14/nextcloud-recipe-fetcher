import json
import shutil

from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any
from typing import Optional

import requests

from recipito.logger import logger

from .models import JustTheRecipe
from .models import JustTheRecipeInstructionGroup
from .models import JustTheRecipeNutritionInfo
from .models import JustTheRecipeStep
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

    # Safely handle instructions with type checking
    instructions: list[str] = []
    for group in recipe.instructions:
        if isinstance(group, JustTheRecipeInstructionGroup) and group.steps:
            for step in group.steps:
                if step.text:
                    instructions.append(convert_characters(step.text))
        elif isinstance(group, JustTheRecipeStep) and group.text:
            instructions.append(convert_characters(group.text))

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
        recipeInstructions=instructions,
        nutrition=JustTheRecipeNutritionInfo(),
        dateModified=now,
        dateCreated=now,
        datePublished=None,
        printImage=True,
        imageUrl="/apps/cookbook/webapp/recipes/{}/image?size=full",
    )

    return nextcloud_recipe.model_dump(by_alias=True)


def save_nextcloud_recipe(title: str, recipe_json: str, keywords: Optional[list[str]] = None) -> None:
    """
    Save recipe in Nextcloud recipes format.

    Args:
        title: The webpage title to use for directory name
        recipe_json: The JSON string containing recipe data
        keywords: Optional list of keywords to add to the recipe
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
    nextcloud_data = convert_to_nextcloud_format(raw_recipe)

    # Add keywords if provided
    if keywords:
        nextcloud_data["keywords"] = ", ".join(keywords)

    nextcloud_recipe = NextcloudRecipe(**nextcloud_data)

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

            # Determine image extension from Content-Type or URL
            content_type = response.headers.get("Content-Type", "")
            if "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            elif "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"
            else:
                # Fallback to extension from URL
                url_ext = image_url.split(".")[-1].lower()
                if url_ext in ["jpg", "jpeg", "png", "webp"]:
                    ext = f".{url_ext}"
                else:
                    logger.warning("Unknown image type: %s, defaulting to .jpg", content_type)
                    ext = ".jpg"

            # Save the image as full.<ext>
            image_path = recipe_dir / f"full{ext}"
            image_path.write_bytes(response.content)
            logger.info("Image saved to: %s", image_path)

            # Update the recipe.json with the image path
            nextcloud_recipe.image = f"full{ext}"
            recipe_path.write_text(nextcloud_recipe.model_dump_json())

        except Exception as e:
            logger.error("Failed to download image: %s", e)

    logger.info("Recipe saved successfully")
