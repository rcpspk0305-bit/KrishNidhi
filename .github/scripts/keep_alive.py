"""
Keep-Alive script for Streamlit Community Cloud apps.

Navigates to the app via headless Chromium, detects if the app has gone to
sleep, clicks the 'Yes, get this app back up!' button if needed, and verifies
that the Streamlit application container is active.
"""
import argparse
import logging
import os
import sys
from typing import List, Optional

# Default target URL
DEFAULT_APP_URL = "https://krishnidhi.streamlit.app/"

# Selectors
SLEEP_BUTTON_SELECTORS = [
    'button:has-text("Yes, get this app back up")',
    'button:has-text("get this app back up")',
    '//button[contains(text(), "Yes, get this app back up")]',
]
APP_CONTAINER_SELECTORS = [
    'div[data-testid="stAppViewContainer"]',
    'div[data-testid="stApp"]',
    '.stApp',
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("streamlit_keep_alive")


def get_target_url(argv: Optional[List[str]] = None) -> str:
    """
    Resolve the target URL by priority:
    1. CLI argument `--url`
    2. Environment variable `STREAMLIT_APP_URL`
    3. DEFAULT_APP_URL
    """
    parser = argparse.ArgumentParser(description="Keep Streamlit app awake.")
    parser.add_argument(
        "--url",
        dest="url",
        default=None,
        help="Target Streamlit application URL",
    )
    args, _ = parser.parse_known_args(argv)

    if args.url:
        return args.url.strip()

    env_url = os.environ.get("STREAMLIT_APP_URL")
    if env_url and env_url.strip():
        return env_url.strip()

    return DEFAULT_APP_URL


def wake_streamlit_app(browser, url: str, timeout_ms: int = 45000) -> bool:
    """
    Load the target page using the provided browser instance, click the wake-up
    button if the app has gone to sleep, and wait for the app container to confirm
    it is active.
    """
    logger.info("Connecting to Streamlit app at: %s", url)
    page = browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    )

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        logger.info("Page loaded initial DOM.")

        # Check for sleep wake-up button
        sleep_button = None
        for selector in SLEEP_BUTTON_SELECTORS:
            btn = page.locator(selector)
            try:
                if btn.is_visible():
                    sleep_button = btn
                    break
            except Exception:
                continue

        if sleep_button:
            logger.info("Detected sleep screen. Clicking 'Yes, get this app back up!'...")
            sleep_button.click()
            logger.info("Wake-up button clicked. Waiting for app to wake...")
        else:
            logger.info("No sleep screen detected. App appears to be active.")

        # Wait for Streamlit container to confirm app is healthy
        container_found = False
        for selector in APP_CONTAINER_SELECTORS:
            try:
                container = page.wait_for_selector(selector, timeout=timeout_ms)
                if container and container.is_visible():
                    container_found = True
                    logger.info("Streamlit container verified active (selector: %s).", selector)
                    break
            except Exception:
                continue

        if not container_found:
            logger.warning(
                "Timed out waiting for Streamlit container, but initial request succeeded."
            )
            return False

        logger.info("Success! App at %s is fully awake.", url)
        return True

    except Exception as exc:
        logger.error("Failed to ping or wake Streamlit app: %s", exc)
        return False
    finally:
        try:
            page.close()
        except Exception:
            pass


def run_keep_alive(url: str, timeout_ms: int = 45000) -> bool:
    """Launch headless browser and perform the keep-alive wake-up sequence."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error(
            "Playwright is not installed. Install it via 'pip install playwright' "
            "and run 'playwright install chromium'."
        )
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
            ],
        )
        try:
            return wake_streamlit_app(browser, url, timeout_ms=timeout_ms)
        finally:
            browser.close()


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint returning 0 for success and 1 for failure."""
    if argv is None:
        argv = sys.argv[1:]

    target_url = get_target_url(argv)
    success = run_keep_alive(target_url)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

