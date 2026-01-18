#!/usr/bin/env python3
"""
Centralized configuration for zlibrary-to-notebooklm.

All constants, paths, and timeouts are defined here to avoid magic numbers
and hardcoded paths scattered throughout the codebase.
"""
from pathlib import Path

# =============================================================================
# Directory Paths
# =============================================================================
CONFIG_DIR = Path.home() / ".zlibrary"
DOWNLOADS_DIR = Path.home() / "Downloads"
TEMP_DIR = Path("/tmp")

# =============================================================================
# File Paths
# =============================================================================
STORAGE_STATE_FILE = CONFIG_DIR / "storage_state.json"
BROWSER_PROFILE_DIR = CONFIG_DIR / "browser_profile"
CONFIG_FILE = CONFIG_DIR / "config.json"

# =============================================================================
# Timeouts (in seconds)
# =============================================================================
PAGE_LOAD_WAIT = 5
DOWNLOAD_WAIT = 20
CONVERSION_TIMEOUT = 60
FILE_AGE_THRESHOLD = 120  # Consider files downloaded within this time as new
LOGIN_TIMEOUT = 5  # Timeout for login element selectors (seconds -> milliseconds in use)
PAGE_TIMEOUT = 60  # Default page timeout (seconds -> milliseconds in use)

# =============================================================================
# Limits
# =============================================================================
WORD_LIMIT_PER_CHUNK = 350_000  # NotebookLM CLI safe limit
MAX_TITLE_LENGTH = 50  # Maximum title length before truncation
MIN_CHAPTER_CONTENT_LENGTH = 100  # Minimum characters to consider chapter substantial

# =============================================================================
# URLs
# =============================================================================
ZLIBRARY_URL = "https://zh.zlib.li/"

# =============================================================================
# File Permissions
# =============================================================================
DIR_PERMISSIONS = 0o700
FILE_PERMISSIONS = 0o600

# =============================================================================
# Retry Configuration
# =============================================================================
MAX_CONVERSION_WAIT_SECONDS = 60
CONVERSION_CHECK_INTERVAL = 1
PROGRESS_LOG_INTERVAL = 10


def ensure_config_dir() -> Path:
    """Ensure the config directory exists with proper permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.chmod(DIR_PERMISSIONS)
    return CONFIG_DIR


def get_script_dir() -> Path:
    """Get the directory where scripts are located."""
    return Path(__file__).parent
