from pathlib import Path
import json
import shutil
from datetime import datetime, timezone
from .models import JustTheRecipe, NextcloudRecipe

def convert_to_nextcloud_format(raw_recipe: dict) -> dict:
    """Convert raw recipe JSON to Nextcloud recipes format."""
    # Validate input recipe format
    recipe = JustTheRecipe(**raw_recipe)
    now = datetime.now(timezone.utc)

    # Convert time from nanoseconds to "PTxHyMzS" format
    def format_time(ns: int) -> str:
        if not ns:
            return None
        seconds = ns // 1_000_000_000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"PT{hours}H{minutes}M{seconds}S"

    # Convert unicode fractions to standard fractions
    def convert_fractions(text: str) -> str:
        fraction_map = {
            '\u00bc': '1/4',
            '\u00bd': '1/2',
            '\u00be': '3/4',
            '\u2153': '1/3',
            '\u2154': '2/3',
            '\u2155': '1/5',
            '\u2156': '2/5',
            '\u2157': '3/5',
            '\u2158': '4/5',
            '\u2159': '1/6',
            '\u215a': '5/6',
            '\u215b': '1/8',
            '\u215c': '3/8',
            '\u215d': '5/8',
            '\u215e': '7/8',
        }
        for unicode_char, fraction in fraction_map.items():
            text = text.replace(unicode_char, fraction)
        return text

    # Convert ingredients with fraction handling
    ingredients = [
        convert_fractions(ingredient.name)
        for ingredient in recipe.ingredients
    ]

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
        recipeInstructions=[
            convert_fractions(step.text)
            for group in recipe.instructions
            for step in group.steps
        ],
        nutrition={"@type": "NutritionInformation"},
        dateModified=now,
        dateCreated=now,
        datePublished=None,
        printImage=True,
        imageUrl="/apps/cookbook/webapp/recipes/{}/image?size=full"
    )

    return nextcloud_recipe.model_dump(by_alias=True)

def save_nextcloud_recipe(title: str, recipe_json: str) -> None:
    """
    Save recipe in Nextcloud recipes format.
    
    Args:
        title: The webpage title to use for directory name
        recipe_json: The JSON string containing recipe data
    """
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
    nextcloud_recipe = convert_to_nextcloud_format(raw_recipe)
    
    # Save recipe.json
    recipe_path = recipe_dir / "recipe.json"
    recipe_path.write_text(json.dumps(nextcloud_recipe, indent=2)) 