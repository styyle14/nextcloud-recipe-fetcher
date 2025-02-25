"""Utility functions for recipe processing."""

import json

from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from PIL import Image
import io

from recipito.logger import logger, console
from recipito.text import convert_characters  # Updated import

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


def convert_to_nextcloud_format(raw_recipe: dict[str, Any], category: str) -> dict[str, Any]:
    """Convert raw recipe JSON to Nextcloud recipes format."""
    logger.info("Converting recipe to Nextcloud format")
    recipe = JustTheRecipe(**raw_recipe)
    now = datetime.now(UTC)

    # Convert time from nanoseconds to "PTxHyMzS" format
    def format_time(ns: int) -> str:
        if not ns:
            return "PT0H0M0S"
        seconds = ns // 1_000_000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"PT{hours}H{minutes}M{seconds}S"

    # Convert instructions to simple text
    instructions: list[str] = []
    for instruction in recipe.instructions:
        if isinstance(instruction, JustTheRecipeStep):
            text = instruction.text or instruction.name
            if text:
                text = text.strip(". ")
                if text and not text.lower().startswith("servings:"):
                    instructions.append(convert_characters(text))

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
        recipeCategory=category,
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


def save_nextcloud_recipe(
    title: str,
    recipe_json: str,
    keywords: list[str],
    category: str = "Main Course",
) -> None:
    """Save recipe in Nextcloud format."""
    logger.info("[bold blue]Converting recipe to Nextcloud format[/]")
    recipe_data = json.loads(recipe_json)
    nextcloud_data = convert_to_nextcloud_format(recipe_data, category)

    # Add keywords if provided
    if keywords:
        nextcloud_data["keywords"] = ", ".join(keywords)

    # Create Nextcloud recipe directory
    output_dir = Path("output")
    recipe_dir = output_dir / "nextcloud_recipes" / title
    recipe_dir.mkdir(parents=True, exist_ok=True)

    # Save recipe.json with custom encoder for datetime
    recipe_path = recipe_dir / "recipe.json"
    recipe_path.write_text(json.dumps(nextcloud_data, indent=2, cls=DateTimeEncoder))

    # Try to download and save the first image
    if recipe_data.get("imageUrls") and recipe_data["imageUrls"]:
        image_url = recipe_data["imageUrls"][0]
        try:
            logger.info("[blue]Downloading image from:[/] %s", image_url)
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # Load image data into PIL Image
            image_data = io.BytesIO(response.content)
            image = Image.open(image_data)

            # Convert to RGB if necessary (e.g., for PNG with transparency)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # Save as JPEG
            image_path = recipe_dir / "full.jpg"
            image.save(image_path, "JPEG", quality=85)
            logger.info("[green]Image saved to:[/] %s", image_path)

            # Update the recipe.json with the image path
            nextcloud_data["image"] = "full.jpg"
            recipe_path.write_text(json.dumps(nextcloud_data, indent=2, cls=DateTimeEncoder))

        except Exception as e:
            logger.error("[red]Failed to download/convert image:[/] %s", e)

    logger.info("[bold green]Recipe saved successfully[/]")
