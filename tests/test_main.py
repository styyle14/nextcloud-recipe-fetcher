from unittest.mock import Mock, patch
import pytest
from typer.testing import CliRunner
from src.main import app

@pytest.fixture
def mock_webdriver():
    """Fixture to mock Selenium WebDriver."""
    with patch('src.main.webdriver.Chrome') as mock_driver:
        # Create mock for WebDriverWait
        mock_wait = Mock()
        mock_element = Mock()
        
        # Setup the chain of mocks to return predetermined titles
        def get_title(url):
            titles = {
                'https://example.com': 'Example Domain',
                'https://google.com': 'Google',
                'https://github.com': "GitHub: Let's build from here"
            }
            return titles.get(url, 'Unknown Title')
        
        # Configure the mocks
        mock_element.get_attribute.side_effect = lambda _: mock_driver.current_url_title
        mock_wait.until.return_value = mock_element
        mock_driver.return_value.get.side_effect = lambda url: setattr(
            mock_driver, 'current_url_title', get_title(url)
        )
        
        # Patch WebDriverWait to return our mock
        with patch('src.main.WebDriverWait', return_value=mock_wait):
            yield mock_driver.return_value

@pytest.fixture
def runner():
    """Fixture for CLI runner."""
    return CliRunner()

def test_main_single_url(runner, mock_webdriver):
    """Test processing a single URL."""
    result = runner.invoke(app, ['https://example.com'])
    assert result.exit_code == 0
    assert '1. https://example.com' in result.stdout
    assert 'Title: Example Domain' in result.stdout

def test_main_multiple_urls(runner, mock_webdriver):
    """Test processing multiple URLs."""
    urls = [
        'https://example.com',
        'https://google.com',
        'https://github.com'
    ]
    
    result = runner.invoke(app, urls)
    
    assert result.exit_code == 0
    assert '1. https://example.com' in result.stdout
    assert 'Title: Example Domain' in result.stdout
    assert '2. https://google.com' in result.stdout
    assert 'Title: Google' in result.stdout
    assert '3. https://github.com' in result.stdout
    assert "Title: GitHub: Let's build from here" in result.stdout

def test_main_no_urls(runner, mock_webdriver):
    """Test calling the program without URLs."""
    result = runner.invoke(app)
    assert result.exit_code != 0  # Should fail without arguments

def test_driver_cleanup(runner, mock_webdriver):
    """Test that the webdriver is properly cleaned up."""
    runner.invoke(app, ['https://example.com'])
    mock_webdriver.quit.assert_called_once()

def test_error_handling(runner, mock_webdriver):
    """Test handling of errors when fetching titles."""
    # Make the driver raise an exception
    mock_webdriver.get.side_effect = Exception("Failed to load page")
    
    result = runner.invoke(app, ['https://example.com'])
    
    assert result.exit_code == 0  # Should not crash
    assert 'Error fetching title' in result.stdout 