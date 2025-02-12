import typer
from typing import List

app = typer.Typer(help="URL processor application")

@app.command()
def main(
    urls: List[str] = typer.Argument(
        ...,
        help="List of URLs to process",
    )
) -> None:
    """Process a list of URLs and print them."""
    for i, url in enumerate(urls, 1):
        typer.echo(f"{i}. {url}")

if __name__ == "__main__":
    app()