import json
import urllib.parse

from pathlib import Path
from typing import Annotated

import requests
import typer

from bs4 import BeautifulSoup

from recipito.logger import logger
from recipito.utils import save_nextcloud_recipe

app = typer.Typer(help="URL processor application")

# Add constant for max filename length
MAX_FILENAME_LENGTH = 100


def sanitize_filename(title: str) -> str:
    """
    Convert title to a valid filename across platforms.

    - Remove invalid filename characters
    - Limit to MAX_FILENAME_LENGTH characters
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

    # Limit length to MAX_FILENAME_LENGTH chars
    if len(clean_title) > MAX_FILENAME_LENGTH:
        clean_title = clean_title[:MAX_FILENAME_LENGTH].rstrip("-")

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
    urls: Annotated[list[str], typer.Argument(help="URLs to scrape")],
    keywords: Annotated[list[str] | None, typer.Option("--keyword", "-k", help="Keywords to filter recipes")] = None,
    category: Annotated[str, typer.Option("--category", "-C", help="Recipe category")] = "Main Course",
) -> None:
    """Scrape recipes from URLs and save them as JSON."""
    if not urls:
        logger.error("No URLs provided")
        raise typer.Exit(code=1)

    # Initialize keywords to empty list if None
    keywords = keywords or []

    logger.info("Processing %d URLs", len(urls))
    if keywords:
        logger.info("Using keywords: %s", ", ".join(keywords))

    output_dir = Path("output")
    json_dir = output_dir / "json"
    json_dir.mkdir(parents=True, exist_ok=True)

    for i, url in enumerate(urls, 1):
        try:
            title = get_page_title(url)
            content = get_recipe_content(url)

            logger.info("URL %d: %s", i, url)
            logger.info("   Title: %s", title)
            logger.info("   Recipe extracted: %s", "Yes" if not content.startswith("Error") else "No")

            if not title.startswith("Error"):
                filename = sanitize_filename(title)
                recipe_path = json_dir / f"{filename}.json"
                recipe_path.write_text(content)
                logger.info("Saved recipe JSON to %s", recipe_path)

                # Save Nextcloud recipe JSON
                save_nextcloud_recipe(filename, content, keywords, category)

        except Exception as e:
            logger.error("Error processing %s: %s", url, e)


if __name__ == "__main__":
    app()
