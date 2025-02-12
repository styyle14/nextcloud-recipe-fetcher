import typer
from typing import List
from pathlib import Path
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests

app = typer.Typer(help="URL processor application")

def sanitize_filename(title: str) -> str:
    """Convert title to filename-safe format using first 5 words."""
    # Remove special characters and split into words
    words = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in title).split()
    # Take first 5 words and join with dashes
    return '-'.join(words[:5]).lower()

def setup_driver():
    """Setup and return a Chrome webdriver with headless mode."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def get_page_title(driver: webdriver.Chrome, url: str) -> str:
    """Fetch the title of a webpage."""
    try:
        driver.get(url)
        title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "title"))
        ).get_attribute("textContent")
        return title.strip()
    except Exception as e:
        return f"Error fetching title: {str(e)}"

def get_recipe_content(driver: webdriver.Chrome, url: str) -> str:
    """Fetch recipe content from justtherecipe.com."""
    try:
        recipe_url = f"https://www.justtherecipe.com/extractRecipeAtUrl?url={urllib.parse.quote(url)}"
        typer.echo(f"   Fetching from: {recipe_url}")
        response = requests.get(recipe_url)
        response.raise_for_status()  # Raise exception for bad status codes
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
    # Create output/json directory
    json_dir = Path("output") / "json"
    json_dir.mkdir(parents=True, exist_ok=True)
    
    driver = setup_driver()
    try:
        for i, url in enumerate(urls, 1):
            title = get_page_title(driver, url)
            recipe = get_recipe_content(driver, url)
            
            typer.echo(f"{i}. {url}")
            typer.echo(f"   Title: {title}")
            typer.echo(f"   Recipe extracted: {'Yes' if not recipe.startswith('Error') else 'No'}\n")
            
            if not title.startswith("Error"):
                filename = sanitize_filename(title)
                (json_dir / f"{filename}.json").write_text(recipe)
    finally:
        driver.quit()

if __name__ == "__main__":
    app() 