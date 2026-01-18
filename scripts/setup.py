#!/usr/bin/env python3
"""
Setup script for zlibrary-to-notebooklm.

This script installs external tools that cannot be managed by Python packages:
- NotebookLM CLI (notebooklm-py) - via uv tool
- Playwright browser - via playwright install

Python dependencies are automatically managed by uv via pyproject.toml.

Usage:
    uv run scripts/setup.py
"""

import shutil
import subprocess
import sys
from pathlib import Path


def check_uv() -> bool:
    """Check if uv is installed."""
    return shutil.which("uv") is not None


def check_python_version() -> bool:
    """Check if Python version is 3.10+."""
    return sys.version_info >= (3, 10)


def check_playwright_browser() -> bool:
    """Check if Playwright Chromium browser is installed."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser_path = p.chromium.executable_path
            return Path(browser_path).exists()
    except Exception:
        return False


def install_playwright_browser() -> bool:
    """Install Playwright Chromium browser."""
    print("=" * 70)
    print("Installing Playwright Chromium browser...")
    print("=" * 70)
    print("")

    try:
        result = subprocess.run(
            ["playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            text=True
        )
        print("  Playwright Chromium installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Failed to install browser: {e}")
        if e.stderr:
            print(f"  Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("  playwright command not found. Run: uv run playwright install chromium")
        return False


def check_notebooklm_cli() -> bool:
    """Check if NotebookLM CLI (notebooklm-py) is installed."""
    try:
        result = subprocess.run(
            ["notebooklm", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_notebooklm_cli() -> bool:
    """Install NotebookLM CLI (notebooklm-py) using uv tool."""
    print("=" * 70)
    print("Installing NotebookLM CLI (notebooklm-py)...")
    print("=" * 70)
    print("")

    try:
        # Install notebooklm-py with browser support
        print("  Running: uv tool install notebooklm-py[browser] --with httpx[socks]")
        result = subprocess.run(
            ["uv", "tool", "install", "notebooklm-py[browser]", "--with", "httpx[socks]"],
            check=True,
            capture_output=True,
            text=True
        )

        # Install Chromium for Playwright (via uv tool run)
        print("  Running: uv tool run playwright install chromium")
        result = subprocess.run(
            ["uv", "tool", "run", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            text=True
        )

        print("  NotebookLM CLI installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Failed to install NotebookLM CLI:")
        print(f"    Return code: {e.returncode}")
        if e.stderr:
            print(f"    Error: {e.stderr.strip()}")
        if e.stdout:
            print(f"    Output: {e.stdout.strip()}")
        return False
    except FileNotFoundError:
        print("  ERROR: uv not found!")
        print("  Please install uv first:")
        print("    curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("    # or: brew install uv")
        return False


def ensure_config_directory() -> Path:
    """Ensure config directory exists with proper permissions."""
    config_dir = Path.home() / ".zlibrary"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_dir.chmod(0o700)

    # Ensure downloads directory exists and is writable
    downloads_dir = Path.home() / "Downloads"
    if not downloads_dir.exists():
        downloads_dir.mkdir(parents=True, exist_ok=True)

    return config_dir


def main() -> None:
    """Main setup routine."""
    print("")
    print("=" * 70)
    print("Z-Library to NotebookLM - Setup")
    print("=" * 70)
    print("")

    all_success = True

    # Check Python version
    print("Checking Python version...")
    print(f"  Current: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    if check_python_version():
        print("  OK (3.10+)")
    else:
        print("  WARNING: Python 3.10+ is recommended")
        all_success = False
    print("")

    # Check uv
    print("Checking uv package manager...")
    if check_uv():
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        print(f"  OK: {result.stdout.strip()}")
    else:
        print("  ERROR: uv not found!")
        print("  Please install uv first:")
        print("    curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("    # or: brew install uv")
        all_success = False
    print("")

    # Check Python dependencies (managed by uv via pyproject.toml)
    print("Checking Python dependencies...")
    print("  (Python dependencies are auto-installed by uv on first run)")
    print("")

    # Step 1: Check/Install Playwright browser
    print("Step 1: Checking Playwright browser...")
    if check_playwright_browser():
        print("  Already installed")
    else:
        print("  Not found, installing...")
        if not install_playwright_browser():
            print("  Failed. Try manually: uv run playwright install chromium")
            all_success = False
    print("")

    # Step 2: Check/Install NotebookLM CLI
    print("Step 2: Checking NotebookLM CLI (notebooklm-py)...")
    if check_notebooklm_cli():
        result = subprocess.run(
            ["notebooklm", "--version"],
            capture_output=True,
            text=True
        )
        print(f"  Already installed: {result.stdout.strip()}")
    else:
        print("  Not found, installing...")
        if not install_notebooklm_cli():
            print("  Failed. Try manually:")
            print("    uv tool install \"notebooklm-py[browser]\" --with \"httpx[socks]\"")
            all_success = False
    print("")

    # Step 3: Create config directory
    print("Step 3: Creating config directories...")
    config_dir = ensure_config_directory()
    print(f"  Config directory: {config_dir}")
    print(f"  Downloads directory: {Path.home() / 'Downloads'}")
    print("")

    # Summary
    print("=" * 70)
    if all_success:
        print("Setup complete! All dependencies installed.")
    else:
        print("Setup completed with warnings. Please fix the errors above.")
    print("=" * 70)
    print("")
    print("Next steps:")
    print("  1. Login to Z-Library (one-time):")
    print("     uv run scripts/login.py")
    print("")
    print("  2. Login to NotebookLM (one-time):")
    print("     notebooklm login")
    print("")
    print("  3. Upload a book:")
    print("     uv run scripts/upload.py <Z-Library URL>")
    print("")


if __name__ == "__main__":
    main()
