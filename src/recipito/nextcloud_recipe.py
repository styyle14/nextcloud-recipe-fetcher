from pathlib import Path
import json
import shutil

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
    
    # Save recipe.json
    recipe_path = recipe_dir / "recipe.json"
    recipe_path.write_text(recipe_json) 