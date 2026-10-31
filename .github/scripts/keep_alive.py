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
    'text="Yes, get this app back up!"',
    '//button[contains(text(), "Yes, get this app back up")]',
]
APP_CONTAINER_SELECTORS = [
    'div[data-testid="stAppViewContainer"]',
    'div[data-testid="stApp"]',
    '.stApp',
    'iframe[title*="streamlit" i]',
    'iframe',
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


def find_sleep_button(page):
    """Search for the sleep reactivation button in the main page and child frames."""
    for selector in SLEEP_BUTTON_SELECTORS:
        try:
            loc = page.locator(selector).first
            if loc.is_visible():
                return loc
        except Exception:
            pass

        frames = getattr(page, "frames", [])
        for frame in frames:
            try:
                loc = frame.locator(selector).first
                if loc.is_visible():
                    return loc
            except Exception:
                pass
    return None


def verify_active_container(page, timeout_ms: int = 5000) -> bool:
    """Verify presence of Streamlit container or embedded iframe in page or frames."""
    for selector in APP_CONTAINER_SELECTORS:
        try:
            container = page.wait_for_selector(selector, timeout=timeout_ms)
            if container and container.is_visible():
                logger.info("Streamlit container verified active (selector: %s).", selector)
                return True
        except Exception:
            pass

        frames = getattr(page, "frames", [])
        for frame in frames:
            try:
                container = frame.wait_for_selector(selector, timeout=2000)
                if container and container.is_visible():
                    logger.info("Streamlit container verified in frame (selector: %s).", selector)
                    return True
            except Exception:
                pass
    return False


def wake_streamlit_app(browser, url: str, timeout_ms: int = 30000) -> bool:
    """
    Load the target page using the provided browser instance, click the wake-up
    button if the app has gone to sleep, and confirm the application is awake.
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
        response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        logger.info("Page loaded initial DOM.")

        # Give client-side JS/React a short window to hydrate
        try:
            wait_for_load = getattr(page, "wait_for_load_state", None)
            if callable(wait_for_load):
                wait_for_load("networkidle", timeout=6000)
        except Exception:
            pass

        # Check for sleep wake-up button across page and frames
        sleep_button = find_sleep_button(page)

        if sleep_button:
            logger.info("Detected sleep screen. Clicking 'Yes, get this app back up!'...")
            sleep_button.click()
            logger.info("Wake-up button clicked. Waiting for app to wake...")
            try:
                wait_timeout = getattr(page, "wait_for_timeout", None)
                if callable(wait_timeout):
                    wait_timeout(5000)
            except Exception:
                pass

            container_awake = verify_active_container(page, timeout_ms=timeout_ms)
            if container_awake:
                logger.info("Success! App at %s was woken up successfully.", url)
                return True
            logger.warning("Wake button clicked, but active container confirmation timed out.")
            return True
        else:
            logger.info("No sleep screen detected.")

        # Check if container or iframe is present
        container_found = verify_active_container(page, timeout_ms=5000)
        if container_found:
            logger.info("Success! App at %s is fully awake and verified.", url)
            return True

        # If no sleep button was found and response was HTTP 200, app is awake
        status = getattr(response, "status", None) if response is not None else 200
        if status and status < 400:
            logger.info("App responded with HTTP status %s and no sleep prompt; app is awake.", status)
            return True

        logger.warning("App did not return a valid active state or 2xx status.")
        return False

    except Exception as exc:
        logger.error("Failed to ping or wake Streamlit app: %s", exc)
        return False
    finally:
        try:
            page.close()
        except Exception:
            pass


def run_keep_alive(url: str, timeout_ms: int = 30000) -> bool:
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

