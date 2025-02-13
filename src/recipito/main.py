import typer
from typing import List
from pathlib import Path
import urllib.parse
import json
import requests
from bs4 import BeautifulSoup
from recipito.nextcloud_recipe import save_nextcloud_recipe

app = typer.Typer(help="URL processor application")

def sanitize_filename(title: str) -> str:
    """Convert title to filename-safe format using first 5 words."""
    words = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in title).split()
    return '-'.join(words[:5]).lower()

def get_page_title(url: str) -> str:
    """Fetch the title of a webpage using requests and BeautifulSoup."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.string.strip()
    except Exception as e:
        return f"Error fetching title: {str(e)}"

def get_recipe_content(url: str) -> str:
    """Fetch recipe content from justtherecipe.com."""
    try:
        recipe_url = f"https://www.justtherecipe.com/extractRecipeAtUrl?url={urllib.parse.quote(url)}"
        typer.echo(f"   Fetching from: {recipe_url}")
        response = requests.get(recipe_url)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.RequestException as e:
        return f"Error fetching recipe: {str(e)}"
    except json.JSONDecodeError as e:
        return f"Error parsing recipe JSON: {str(e)}"

@app.command()
def main(
    urls: List[str] = typer.Argument(
        ...,
        help="List of URLs to process",
    )
) -> None:
    """Process a list of URLs and print their titles and recipes."""
    json_dir = Path("output") / "json"
    json_dir.mkdir(parents=True, exist_ok=True)
    
    for i, url in enumerate(urls, 1):
        title = get_page_title(url)
        recipe = get_recipe_content(url)
        
        typer.echo(f"{i}. {url}")
        typer.echo(f"   Title: {title}")
        typer.echo(f"   Recipe extracted: {'Yes' if not recipe.startswith('Error') else 'No'}\n")
        
        if not title.startswith("Error"):
            filename = sanitize_filename(title)
            (json_dir / f"{filename}.json").write_text(recipe)
            save_nextcloud_recipe(filename, recipe)

if __name__ == "__main__":
    app() 