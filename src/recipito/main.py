import typer
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = typer.Typer(help="URL processor application")

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

@app.command()
def main(
    urls: List[str] = typer.Argument(
        ...,
        help="List of URLs to process",
    )
) -> None:
    """Process a list of URLs and print their titles."""
    driver = setup_driver()
    try:
        for i, url in enumerate(urls, 1):
            title = get_page_title(driver, url)
            typer.echo(f"{i}. {url}")
            typer.echo(f"   Title: {title}\n")
    finally:
        driver.quit()

if __name__ == "__main__":
    app() 