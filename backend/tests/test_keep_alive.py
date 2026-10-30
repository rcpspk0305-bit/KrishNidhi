"""
Tests for Streamlit keep-alive wake-up automation.
"""
import sys
import os
from unittest.mock import MagicMock, patch
import pytest

# Add .github/scripts to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".github", "scripts")))

try:
    import keep_alive
except ImportError:
    keep_alive = None


def test_import_keep_alive():
    """Verify keep_alive module can be imported."""
    assert keep_alive is not None, "keep_alive module should be importable"


def test_get_target_url_cli_arg():
    """CLI argument should take highest priority."""
    with patch.dict(os.environ, {"STREAMLIT_APP_URL": "https://env.streamlit.app"}):
        url = keep_alive.get_target_url(["--url", "https://custom.streamlit.app"])
        assert url == "https://custom.streamlit.app"


def test_get_target_url_env_var():
    """Environment variable should take precedence over default."""
    with patch.dict(os.environ, {"STREAMLIT_APP_URL": "https://env.streamlit.app"}):
        url = keep_alive.get_target_url([])
        assert url == "https://env.streamlit.app"


def test_get_target_url_default():
    """Default URL should be used if neither CLI nor env var is provided."""
    with patch.dict(os.environ, {}, clear=True):
        url = keep_alive.get_target_url([])
        assert url == keep_alive.DEFAULT_APP_URL
        assert "krishnidhi.streamlit.app" in url


def test_ping_and_wake_already_awake():
    """When app is already awake, it should detect the container without clicking wake button."""
    mock_page = MagicMock()
    # Sleep button not found / not visible
    mock_button = MagicMock()
    mock_button.is_visible.return_value = False
    mock_page.locator.return_value = mock_button

    # Main container is found
    mock_container = MagicMock()
    mock_container.is_visible.return_value = True
    mock_page.wait_for_selector.return_value = mock_container

    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page

    result = keep_alive.wake_streamlit_app(mock_browser, "https://krishnidhi.streamlit.app/", timeout_ms=5000)
    assert result is True
    mock_button.click.assert_not_called()


def test_ping_and_wake_asleep():
    """When app is asleep, it should click the wake button and wait for the container."""
    mock_page = MagicMock()
    mock_button = MagicMock()
    mock_button.is_visible.return_value = True
    mock_page.locator.return_value = mock_button

    mock_container = MagicMock()
    mock_container.is_visible.return_value = True
    mock_page.wait_for_selector.return_value = mock_container

    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page

    result = keep_alive.wake_streamlit_app(mock_browser, "https://krishnidhi.streamlit.app/", timeout_ms=5000)
    assert result is True
    mock_button.click.assert_called_once()


def test_ping_and_wake_failure():
    """When navigation fails or raises an exception, it should return False."""
    mock_page = MagicMock()
    mock_page.goto.side_effect = Exception("Connection timeout")

    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page

    result = keep_alive.wake_streamlit_app(mock_browser, "https://invalid-url.com", timeout_ms=5000)
    assert result is False


def test_main_exit_code_success():
    """main should exit with 0 on success."""
    with patch("keep_alive.run_keep_alive", return_value=True):
        exit_code = keep_alive.main(["--url", "https://krishnidhi.streamlit.app/"])
        assert exit_code == 0


def test_main_exit_code_failure():
    """main should exit with 1 on failure."""
    with patch("keep_alive.run_keep_alive", return_value=False):
        exit_code = keep_alive.main(["--url", "https://krishnidhi.streamlit.app/"])
        assert exit_code == 1

