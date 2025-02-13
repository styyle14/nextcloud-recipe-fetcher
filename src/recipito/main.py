import json
import urllib.parse

from pathlib import Path

import requests
import typer

from bs4 import BeautifulSoup

from recipito.logger import logger
from recipito.nextcloud_recipe import save_nextcloud_recipe

app = typer.Typer(help="URL processor application")


def sanitize_filename(title: str) -> str:
    """
    Convert title to a valid filename across platforms.
    
    - Remove invalid filename characters
    - Limit to 75 characters
    - Ensure compatibility with Windows, Mac, and Linux
    """
    # Characters not allowed in filenames across platforms
    invalid_chars = '<>:"/\\|?*'
    
    # Replace invalid chars with dash
    clean_title = title
    for char in invalid_chars:
        clean_title = clean_title.replace(char, "-")
        
    # Replace multiple dashes with single dash
    while "--" in clean_title:
        clean_title = clean_title.replace("--", "-")
    
    # Remove leading/trailing dashes and spaces
    clean_title = clean_title.strip("- ")
    
    # Limit length to 75 chars
    if len(clean_title) > 75:
        clean_title = clean_title[:75].rstrip("-")
    
    return clean_title


def get_page_title(url: str) -> str:
    """Fetch the title of a webpage using requests and BeautifulSoup."""
    try:
        logger.info("Fetching page title from: %s", url)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title
        if title is None or title.string is None:
            logger.warning("No title found for URL: %s", url)
            return "Error: No title found"
        return title.string.strip()
    except Exception as e:
        logger.error("Error fetching title: %s", e)
        return f"Error fetching title: {e!s}"


def get_recipe_content(url: str) -> str:
    """Fetch recipe content from justtherecipe.com."""
    try:
        recipe_url = f"https://www.justtherecipe.com/extractRecipeAtUrl?url={urllib.parse.quote(url)}"
        logger.info("Fetching recipe from: %s", recipe_url)
        response = requests.get(recipe_url)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        logger.error("Error fetching recipe: %s", e)
        return f"Error fetching recipe: {e!s}"


@app.command()
def main(
    urls: list[str] = typer.Argument(
        None,  # Use None instead of ... for default
        help="List of URLs to process",
    ),
    keywords: list[str] = typer.Option(
        [],
        "--keyword", "-k",
        help="Keywords to add to the recipe (can be specified multiple times)",
    ),
) -> None:
    """Process a list of URLs and print their titles and recipes."""
    if not urls:
        logger.error("No URLs provided")
        raise typer.Exit(code=1)

    logger.info("Processing %d URLs", len(urls))
    if keywords:
        logger.info("Using keywords: %s", ", ".join(keywords))

    json_dir = Path("output") / "json"
    json_dir.mkdir(parents=True, exist_ok=True)

    for i, url in enumerate(urls, 1):
        title = get_page_title(url)
        recipe = get_recipe_content(url)

        logger.info("URL %d: %s", i, url)
        logger.info("   Title: %s", title)
        logger.info("   Recipe extracted: %s", "Yes" if not recipe.startswith("Error") else "No")

        if not title.startswith("Error"):
            filename = sanitize_filename(title)
            (json_dir / f"{filename}.json").write_text(recipe)
            save_nextcloud_recipe(filename, recipe, keywords)


if __name__ == "__main__":
    app()
