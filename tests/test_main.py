import json

from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import typer

from recipito.logger import logger
from recipito.main import main


@pytest.fixture
def mock_requests() -> Generator[Mock, None, None]:
    """Fixture to mock requests."""
    logger.info("Setting up mock requests")
    with patch("recipito.main.requests") as mock_req:
        # Mock successful response
        mock_response = Mock()
        mock_response.text = "<html><title>Test Recipe</title></html>"
        mock_response.json.return_value = {
            "version": "1.0.0",
            "id": "test-id",
            "name": "Test Recipe",
            "sourceUrl": "https://example.com/recipe",
            "servings": 4,
            "cookTime": 1800000000,
            "prepTime": 1800000000,
            "totalTime": 3600000000,
            "categories": ["Main Course"],
            "cuisines": ["American"],
            "imageUrls": ["https://example.com/image.jpg"],
            "keywords": ["test"],
            "ingredients": [{"name": "test ingredient"}],
            "instructions": [
                {
                    "steps": [{"text": "test step", "name": "test step", "type": "step"}],
                    "name": "test group",
                    "type": "group",
                },
            ],
            "source": "fromUrl",
        }
        mock_req.get.return_value = mock_response
        yield mock_req
    logger.info("Tearing down mock requests")


def test_main_single_url(tmp_path: Path) -> None:
    """Test processing a single URL."""
    json_dir = tmp_path / "output" / "json"
    json_dir.mkdir(parents=True)

    with patch("recipito.main.Path", return_value=json_dir):
        main(urls=["https://example.com/recipe"], keywords=[])


def test_main_multiple_urls(tmp_path: Path) -> None:
    """Test processing multiple URLs."""
    urls = [
        "https://example.com/recipe1",
        "https://example.com/recipe2",
    ]
    json_dir = tmp_path / "output" / "json"
    json_dir.mkdir(parents=True)

    with patch("recipito.main.Path", return_value=json_dir):
        main(urls=urls, keywords=[])


def test_main_no_urls() -> None:
    """Test handling no URLs."""
    with pytest.raises(typer.Exit):  # Typer raises Exit exception
        main([])


def test_error_handling(mock_requests: Mock, tmp_path: Path) -> None:
    """Test handling request errors."""
    mock_requests.get.side_effect = Exception("Test error")
    json_dir = tmp_path / "output" / "json"
    json_dir.mkdir(parents=True)

    with patch("recipito.main.Path", return_value=json_dir):
        main(urls=["https://example.com/recipe"], keywords=[])  # Pass arguments by name


def test_file_saving(tmp_path: Path) -> None:
    """Test that files are saved correctly."""
    logger.info("Testing file saving functionality")

    # Create base output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)
    logger.debug("Created output directory: %s", output_dir)

    # Create json directory
    json_dir = output_dir / "json"
    json_dir.mkdir(parents=True)

    mock_recipe = {
        "version": "1.0.0",
        "id": "test-id",
        "name": "Test Recipe",
        "sourceUrl": "https://example.com/recipe",
        "servings": 4,
        "cookTime": 1800000000,
        "prepTime": 1800000000,
        "totalTime": 3600000000,
        "categories": ["Main Course"],
        "cuisines": ["American"],
        "imageUrls": ["https://example.com/image.jpg"],
        "keywords": ["test"],
        "ingredients": [{"name": "test ingredient"}],
        "instructions": [
            {
                "steps": [{"text": "test step", "name": "test step", "type": "step"}],
                "name": "test group",
                "type": "group",
            },
        ],
        "source": "fromUrl",
    }

    recipe_title = "Test Recipe"
    sanitized_title = recipe_title  # This matches what sanitize_filename will produce

    with (
        patch("recipito.main.Path", return_value=output_dir),
        patch("recipito.nextcloud_recipe.Path", return_value=output_dir),
        patch("recipito.main.get_page_title", return_value=recipe_title),
        patch("recipito.main.get_recipe_content", return_value=json.dumps(mock_recipe)),
    ):
        main(urls=["https://example.com/recipe"], keywords=[])

        # Check both JSON files were created
        recipe_json = json_dir / f"{sanitized_title}.json"
        nextcloud_json = output_dir / "nextcloud_recipes" / sanitized_title / "recipe.json"

        # Debug output
        logger.debug("Checking for files:")
        logger.debug("Recipe JSON path: %s", recipe_json)
        logger.debug("Nextcloud JSON path: %s", nextcloud_json)
        logger.debug("Recipe JSON exists: %s", recipe_json.exists())
        logger.debug("Nextcloud JSON exists: %s", nextcloud_json.exists())
        logger.debug("Contents of %s:", json_dir)
        for f in json_dir.glob("*"):
            logger.debug("  %s", f)
        logger.debug("Contents of %s:", output_dir)
        for f in output_dir.glob("**/*"):
            logger.debug("  %s", f)

        assert recipe_json.exists(), "Recipe JSON file not created"
        assert nextcloud_json.exists(), "Nextcloud recipe JSON file not created"

    logger.info("File saving test completed")
