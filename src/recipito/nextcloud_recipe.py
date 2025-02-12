from pathlib import Path
import json
import shutil
from datetime import datetime, timezone

def convert_to_nextcloud_format(raw_recipe: dict) -> dict:
    """Convert raw recipe JSON to Nextcloud recipes format."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    
    # Convert time from nanoseconds to "PTxHyMzS" format
    def format_time(ns: int) -> str:
        if not ns:
            return None
        seconds = ns // 1_000_000_000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"PT{hours}H{minutes}M{seconds}S"

    return {
        "id": str(raw_recipe.get("id", ""))[:5],  # Take first 5 chars of UUID
        "name": raw_recipe.get("name", ""),
        "description": "",
        "url": raw_recipe.get("sourceUrl", ""),
        "image": "",
        "prepTime": format_time(raw_recipe.get("prepTime", 0)),
        "cookTime": format_time(raw_recipe.get("cookTime", 0)),
        "totalTime": format_time(raw_recipe.get("totalTime", 0)),
        "recipeCategory": ", ".join(raw_recipe.get("categories", [])),
        "keywords": "",
        "recipeYield": raw_recipe.get("servings", 4),
        "tool": [],
        "recipeIngredient": [
            ingredient["name"] for ingredient in raw_recipe.get("ingredients", [])
        ],
        "recipeInstructions": [
            step["text"] for group in raw_recipe.get("instructions", [])
            for step in group.get("steps", [])
        ],
        "nutrition": {"@type": "NutritionInformation"},
        "@context": "http://schema.org",
        "@type": "Recipe",
        "dateModified": now,
        "dateCreated": now,
        "datePublished": None,
        "printImage": True,
        "imageUrl": "/apps/cookbook/webapp/recipes/{}/image?size=full"
    }

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