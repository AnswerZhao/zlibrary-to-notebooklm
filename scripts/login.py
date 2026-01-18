#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.40.0",
# ]
# ///
"""
Z-Library Login - One-time login, save session state.

Similar to how `notebooklm login` works.

Usage:
    uv run scripts/login.py
"""

import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed")
    print("Please run: pip install playwright")
    sys.exit(1)

# Import local modules
from config import (
    CONFIG_DIR,
    STORAGE_STATE_FILE,
    BROWSER_PROFILE_DIR,
    ZLIBRARY_URL,
    DIR_PERMISSIONS,
    FILE_PERMISSIONS,
    ensure_config_dir,
    get_script_dir,
)
from logger import get_logger

logger = get_logger(__name__)


def zlibrary_login() -> None:
    """Login to Z-Library and save session."""

    config_dir = ensure_config_dir()
    storage_state = STORAGE_STATE_FILE

    logger.section("Z-Library Login")
    print("")
    print("Instructions:")
    print("  1. Browser will automatically open and visit Z-Library")
    print("  2. Please complete login manually (if needed)")
    print("  3. After successful login, return to terminal and press ENTER")
    print("  4. Session state will be saved, no need to login again")
    print("")

    with sync_playwright() as p:
        logger.info("Launching browser...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE_DIR),
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            logger.info("Visiting Z-Library...")
            page.goto(ZLIBRARY_URL, wait_until='domcontentloaded', timeout=30000)

            print("")
            logger.section("Action Steps")
            print("1. Complete login in the browser (if not logged in)")
            print("2. Wait until you see the Z-Library homepage")
            print("3. Return to terminal and press ENTER to continue")
            print("=" * 70)
            print("")

            input("Login completed? Press ENTER to save session... ")

            # Save session state
            browser.storage_state(path=str(storage_state))
            storage_state.chmod(FILE_PERMISSIONS)

            print("")
            logger.success("Session saved!")
            print(f"Location: {storage_state}")
            print("")
            print("You can now run the automation script:")
            script_dir = get_script_dir()
            print(f"   python3 {script_dir}/upload.py <Z-Library URL>")
            print("")

        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            browser.close()


def main() -> None:
    """Main entry point."""
    zlibrary_login()


if __name__ == "__main__":
    main()
