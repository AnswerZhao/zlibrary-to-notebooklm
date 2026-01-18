#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.40.0",
#     "ebooklib>=0.18",
#     "beautifulsoup4>=4.11.0",
#     "lxml>=4.9.0",
# ]
# ///
"""
Z-Library Auto Download and Upload to NotebookLM.

This script automates downloading books from Z-Library and uploading them
to Google NotebookLM for AI-powered reading and analysis.

Usage:
    uv run scripts/upload.py <Z-Library URL>
"""

import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Optional
from urllib.parse import unquote

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERROR: Playwright not installed")
    print("Please run: uv run scripts/setup.py")
    sys.exit(1)

# Import local modules
from config import (
    CONFIG_DIR,
    CONFIG_FILE,
    DOWNLOADS_DIR,
    TEMP_DIR,
    STORAGE_STATE_FILE,
    BROWSER_PROFILE_DIR,
    PAGE_LOAD_WAIT,
    DOWNLOAD_WAIT,
    FILE_AGE_THRESHOLD,
    WORD_LIMIT_PER_CHUNK,
    MAX_TITLE_LENGTH,
    MIN_CHAPTER_CONTENT_LENGTH,
    MAX_CONVERSION_WAIT_SECONDS,
    CONVERSION_CHECK_INTERVAL,
    PROGRESS_LOG_INTERVAL,
    LOGIN_TIMEOUT,
    PAGE_TIMEOUT,
    get_script_dir,
    ensure_config_dir,
)
from logger import get_logger

logger = get_logger(__name__)


def check_environment() -> bool:
    """
    Check if all required dependencies and permissions are available.

    Returns:
        True if environment is ready, False otherwise
    """
    all_ok = True

    # Check Python version
    if sys.version_info < (3, 10):
        print("WARNING: Python 3.10+ is recommended")
        all_ok = False

    # Check notebooklm CLI
    if shutil.which("notebooklm") is None:
        print("ERROR: NotebookLM CLI not found!")
        print("  Please install: uv tool install \"notebooklm-py[browser]\" --with \"httpx[socks]\"")
        print("  Or run: uv run scripts/setup.py")
        all_ok = False
    else:
        # Check if logged in to NotebookLM
        try:
            result = subprocess.run(
                ["notebooklm", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                print("WARNING: NotebookLM login may be required")
                print("  Please run: notebooklm login")
        except Exception:
            pass

    # Playwright is already checked at script import (async_api)
    # Skip redundant check here

    # Check config directory and permissions
    try:
        ensure_config_dir()
        # Check if session file exists
        if not STORAGE_STATE_FILE.exists():
            print("WARNING: Z-Library session not found!")
            print("  Please run: uv run scripts/login.py")
            all_ok = False
    except PermissionError:
        print("ERROR: Cannot write to config directory!")
        print(f"  Config directory: {CONFIG_DIR}")
        all_ok = False

    # Check downloads directory
    if not DOWNLOADS_DIR.exists():
        try:
            DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"ERROR: Cannot write to downloads directory: {DOWNLOADS_DIR}")
            all_ok = False

    # Check temp directory
    if not TEMP_DIR.exists():
        try:
            TEMP_DIR.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"ERROR: Cannot write to temp directory: {TEMP_DIR}")
            all_ok = False

    return all_ok


class ZLibraryAutoUploader:
    """Z-Library auto download and upload handler."""

    def __init__(self) -> None:
        self.downloads_dir = DOWNLOADS_DIR
        self.temp_dir = TEMP_DIR
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE

    def load_credentials(self) -> Optional[dict]:
        """
        Load Z-Library credentials from config file.

        Returns:
            Dictionary with credentials or None if not found/invalid
        """
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            logger.warning(f"Failed to load credentials: {e}")
            return None

    async def login_to_zlibrary(self, page) -> bool:
        """
        Login to Z-Library using saved credentials.

        Args:
            page: Playwright page object

        Returns:
            True if login successful, False otherwise
        """
        credentials = self.load_credentials()

        if not credentials:
            logger.warning("Z-Library config not found")
            script_dir = get_script_dir()
            logger.info(f"Please run: python3 {script_dir}/login.py")
            return False

        logger.info("Logging in to Z-Library...")
        logger.info(f"Using account: {credentials['email']}")

        timeout_ms = LOGIN_TIMEOUT * 1000

        try:
            # Check for existing login dialog
            modal = await page.query_selector('#zlibrary-modal-auth')
            if modal:
                logger.info("Login dialog detected")
                # Input credentials in dialog
                email_input = await page.wait_for_selector(
                    '#modal-auth input[type="email"], #modal-auth input[name="email"]',
                    timeout=timeout_ms
                )
                await email_input.fill(credentials['email'])

                password_input = await page.wait_for_selector(
                    '#modal-auth input[type="password"], #modal-auth input[name="password"]',
                    timeout=timeout_ms
                )
                await password_input.fill(credentials['password'])

                # Click login
                submit_button = await page.wait_for_selector(
                    '#modal-auth button[type="submit"]',
                    timeout=timeout_ms
                )
                await submit_button.click()
            else:
                # Click login button to open dialog
                login_button = await page.wait_for_selector(
                    'a:has-text("Log in"), a:has-text("Login")',
                    timeout=timeout_ms
                )
                await login_button.click()
                await asyncio.sleep(2)

                # Input email
                email_input = await page.wait_for_selector(
                    'input[type="email"], input[name="email"]',
                    timeout=timeout_ms
                )
                await email_input.fill(credentials['email'])

                # Input password
                password_input = await page.wait_for_selector(
                    'input[type="password"], input[name="password"]',
                    timeout=timeout_ms
                )
                await password_input.fill(credentials['password'])

                # Click submit
                submit_button = await page.wait_for_selector(
                    'button[type="submit"], button:has-text("Log in"), button:has-text("Login")',
                    timeout=timeout_ms
                )
                await submit_button.click()

            # Wait for login to complete
            await asyncio.sleep(PAGE_LOAD_WAIT)

            # Check if login successful
            page_content = await page.content()

            if "logout" in page_content.lower() or "Login" not in page_content:
                logger.success("Login successful")
                return True
            else:
                logger.error("Login may have failed, please check credentials")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def download_from_zlibrary(self, url: str) -> tuple[Optional[Path], Optional[str]]:
        """
        Download book from Z-Library.

        Args:
            url: Z-Library book URL

        Returns:
            Tuple of (file_path, format) or (None, None) on failure
        """
        logger.section("Starting browser automation download")

        # Check for saved session
        storage_state = STORAGE_STATE_FILE

        if not storage_state.exists():
            logger.error("Session state not found")
            script_dir = get_script_dir()
            logger.info(f"Please run: python3 {script_dir}/login.py")
            return (None, None)

        logger.success("Using saved session")

        async with async_playwright() as p:
            # Launch browser with persistent context
            logger.info("Launching browser...")

            browser = await p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_PROFILE_DIR),
                headless=False,
                accept_downloads=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            page = browser.pages[0] if browser.pages else await browser.new_page()
            page.set_default_timeout(PAGE_TIMEOUT * 1000)

            # Setup download handler
            download_path: Optional[Path] = None

            async def handle_download(download) -> None:
                nonlocal download_path
                logger.info("Download started...")
                suggested_filename = download.suggested_filename
                logger.info(f"Filename: {suggested_filename}")
                download_path = self.downloads_dir / suggested_filename
                await download.save_as(download_path)
                logger.success(f"Saved: {download_path}")

            page.on('download', handle_download)

            try:
                # Navigate to book page
                logger.info("Visiting book page...")
                await page.goto(url, wait_until='domcontentloaded', timeout=PAGE_TIMEOUT * 1000)

                logger.info("Waiting for page load...")
                await asyncio.sleep(PAGE_LOAD_WAIT)

                # Step 1: Find download method (prefer PDF, then EPUB)
                logger.info("Step 1: Finding download method...")

                # Check for new UI (three dots menu)
                dots_button = await page.query_selector(
                    'button[aria-label="More options"], button[title="More"], '
                    '.more-options, [class*="dots"], [class*="more"]'
                )

                download_link = None
                downloaded_format: Optional[str] = None

                if dots_button:
                    logger.info("Detected new UI (three dots menu)")
                    await dots_button.click()
                    await asyncio.sleep(2)

                    # Look for PDF option (preferred)
                    logger.info("Looking for PDF option...")
                    pdf_options = await page.query_selector_all(
                        'a:has-text("PDF"), button:has-text("PDF")'
                    )
                    if pdf_options:
                        download_link = pdf_options[0]
                        downloaded_format = 'pdf'
                        logger.success("Found PDF option")
                    else:
                        # Fallback: look for EPUB
                        logger.info("PDF not found, looking for EPUB option...")
                        epub_options = await page.query_selector_all(
                            'a:has-text("EPUB"), button:has-text("EPUB")'
                        )
                        if epub_options:
                            download_link = epub_options[0]
                            downloaded_format = 'epub'
                            logger.success("Found EPUB option")

                else:
                    # Old UI: check convert buttons
                    logger.info("Detected old UI")
                    convert_selector_pdf = 'a[data-convert_to="pdf"]'
                    convert_selector_epub = 'a[data-convert_to="epub"]'

                    # Try PDF first
                    convert_button = await page.query_selector(convert_selector_pdf)

                    if convert_button:
                        logger.info("PDF convert button detected")
                        downloaded_format = 'pdf'
                        await convert_button.evaluate('el => el.click()')
                        logger.success("Clicked PDF convert button")

                        # Wait for conversion
                        logger.info("Waiting for PDF conversion...")
                        for i in range(MAX_CONVERSION_WAIT_SECONDS):
                            await asyncio.sleep(CONVERSION_CHECK_INTERVAL)
                            try:
                                message = await page.query_selector('.message:has-text("convert")')
                                if message:
                                    message_text = await message.inner_text()
                                    if 'pdf' in message_text.lower() and 'complete' in message_text.lower():
                                        logger.success("PDF conversion complete!")
                                        break
                            except Exception:
                                pass
                            if i % PROGRESS_LOG_INTERVAL == 0 and i > 0:
                                logger.progress(i, "Waiting")

                        # Find download link
                        download_link = await page.query_selector(
                            'a[href*="/dl/"][href*="convertedTo=pdf"]'
                        )

                        if not download_link:
                            all_links = await page.query_selector_all('a[href*="/dl/"]')
                            if all_links:
                                download_link = all_links[0]
                                href = await download_link.get_attribute('href')
                                logger.success(f"Found download link: {href}")

                    else:
                        # Fallback: try EPUB
                        convert_button = await page.query_selector(convert_selector_epub)

                        if convert_button:
                            logger.info("EPUB convert button detected")
                            downloaded_format = 'epub'
                            await convert_button.evaluate('el => el.click()')
                            logger.success("Clicked EPUB convert button")

                            # Wait for conversion
                            logger.info("Waiting for EPUB conversion...")
                            for i in range(MAX_CONVERSION_WAIT_SECONDS):
                                await asyncio.sleep(CONVERSION_CHECK_INTERVAL)
                                try:
                                    message = await page.query_selector('.message:has-text("convert")')
                                    if message:
                                        message_text = await message.inner_text()
                                        if 'epub' in message_text.lower() and 'complete' in message_text.lower():
                                            logger.success("EPUB conversion complete!")
                                            break
                                except Exception:
                                    pass
                                if i % PROGRESS_LOG_INTERVAL == 0 and i > 0:
                                    logger.progress(i, "Waiting")

                            # Find download link
                            download_link = await page.query_selector(
                                'a[href*="/dl/"][href*="convertedTo=epub"]'
                            )

                            if not download_link:
                                all_links = await page.query_selector_all('a[href*="/dl/"]')
                                if all_links:
                                    download_link = all_links[0]
                                    href = await download_link.get_attribute('href')
                                    logger.success(f"Found download link: {href}")

                # If still no download link, try direct download
                if not download_link:
                    logger.info("No convert button found, looking for direct download...")

                    selectors = [
                        'a[href*="/dl/"]',
                        'a:has-text("Download")',
                        'button:has-text("Download")',
                    ]

                    for selector in selectors:
                        try:
                            links = await page.query_selector_all(selector)
                            if links:
                                for link in links:
                                    href = await link.get_attribute('href')
                                    if href and '/dl/' in href:
                                        download_link = link
                                        # Detect format from URL
                                        if 'pdf' in href.lower():
                                            downloaded_format = 'pdf'
                                        elif 'epub' in href.lower():
                                            downloaded_format = 'epub'
                                        logger.success(
                                            f"Found download link: {href} (format: {downloaded_format})"
                                        )
                                        break
                                if download_link:
                                    break
                        except Exception:
                            continue

                if not download_link:
                    logger.error("Download link not found")
                    await browser.close()
                    return (None, None)

                # Click download
                logger.info("Step 2: Clicking download link...")

                try:
                    await download_link.evaluate('el => el.click()')
                    logger.success("Click successful")
                except Exception as e:
                    logger.error(f"Click failed: {e}")
                    await browser.close()
                    return (None, None)

                # Wait for download
                logger.info("Step 3: Waiting for download to complete...")
                await asyncio.sleep(DOWNLOAD_WAIT)

                # Check result
                if download_path and download_path.exists():
                    file_size = download_path.stat().st_size / 1024
                    logger.success("Download successful!")
                    logger.info(f"   Format: {downloaded_format.upper() if downloaded_format else 'Unknown'}")
                    logger.info(f"   File: {download_path.name}")
                    logger.info(f"   Path: {download_path}")
                    logger.info(f"   Size: {file_size:.1f} KB")
                    await browser.close()
                    return (download_path, downloaded_format)

                # Fallback: check downloads directory
                logger.info("Checking downloads directory...")

                # Find files based on format
                if downloaded_format == 'pdf':
                    pattern = "*.pdf"
                else:
                    pattern = "*.epub"

                downloaded_files = list(self.downloads_dir.glob(pattern))

                if downloaded_files:
                    latest_file = max(downloaded_files, key=lambda p: p.stat().st_mtime)
                    file_age = time.time() - latest_file.stat().st_mtime

                    if file_age < FILE_AGE_THRESHOLD:
                        file_size = latest_file.stat().st_size / 1024
                        logger.success("Download successful!")
                        logger.info(f"   Format: {downloaded_format.upper() if downloaded_format else 'Unknown'}")
                        logger.info(f"   File: {latest_file.name}")
                        logger.info(f"   Path: {latest_file}")
                        logger.info(f"   Size: {file_size:.1f} KB")
                        await browser.close()
                        return (latest_file, downloaded_format)

                logger.error("Downloaded file not found")
                await browser.close()
                return (None, None)

            except Exception as e:
                logger.error(f"Download failed: {e}")
                traceback.print_exc()
                await browser.close()
                return (None, None)

    def count_words(self, text: str) -> int:
        """
        Count words in text (supports Chinese and English).

        Args:
            text: Text content to count

        Returns:
            Total word count
        """
        # Count Chinese characters
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # Count English words
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        return chinese_chars + english_words

    def split_markdown_file(self, file_path: Path, max_words: int = WORD_LIMIT_PER_CHUNK) -> list[Path]:
        """
        Split large Markdown file into smaller chunks.

        Args:
            file_path: Path to the Markdown file
            max_words: Maximum words per chunk

        Returns:
            List of chunk file paths
        """
        logger.info("File too large, starting split...")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        total_words = self.count_words(content)
        logger.info(f"   Total words: {total_words:,}")
        logger.info(f"   Max per chunk: {max_words:,}")

        # Split by chapters (## or ### headings)
        chapters = re.split(r'\n(?=#{1,3}\s)', content)

        chunks: list[str] = []
        current_chunk = ""
        current_words = 0
        chunk_num = 1

        for chapter in chapters:
            chapter_words = self.count_words(chapter)

            # If single chapter exceeds limit, split further
            if chapter_words > max_words:
                # Save current chunk first
                if current_chunk:
                    chunks.append(current_chunk)
                    chunk_num += 1
                    current_chunk = ""
                    current_words = 0

                # Split large chapter by paragraphs
                paragraphs = chapter.split('\n\n')
                temp_chunk = ""
                temp_words = 0

                for para in paragraphs:
                    para_words = self.count_words(para)
                    if temp_words + para_words > max_words and temp_chunk:
                        chunks.append(temp_chunk)
                        chunk_num += 1
                        temp_chunk = para + "\n\n"
                        temp_words = para_words
                    else:
                        temp_chunk += para + "\n\n"
                        temp_words += para_words

                if temp_chunk:
                    current_chunk = temp_chunk
                    current_words = temp_words

            elif current_words + chapter_words > max_words:
                # Current chunk full, save and start new
                chunks.append(current_chunk)
                chunk_num += 1
                current_chunk = chapter + "\n\n"
                current_words = chapter_words
            else:
                # Add to current chunk
                current_chunk += chapter + "\n\n"
                current_words += chapter_words

        # Save last chunk
        if current_chunk:
            chunks.append(current_chunk)

        # Write chunk files
        chunk_files: list[Path] = []
        stem = file_path.stem
        for i, chunk in enumerate(chunks, 1):
            chunk_file = file_path.parent / f"{stem}_part{i}.md"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            chunk_files.append(chunk_file)
            chunk_words = self.count_words(chunk)
            logger.info(f"   Part {i}/{len(chunks)}: {chunk_words:,} words")

        return chunk_files

    def convert_to_txt(self, file_path: Path, file_format: Optional[str] = None) -> Path | list[Path]:
        """
        Convert file to text format or return directly if PDF.

        Args:
            file_path: Path to the downloaded file
            file_format: Format hint (pdf/epub)

        Returns:
            Path to processed file or list of chunk paths
        """
        logger.section("Processing file")

        file_ext = file_path.suffix.lower()

        # If PDF, use directly (Plan A)
        if file_ext == '.pdf' or file_format == 'pdf':
            logger.success("PDF format detected, using directly")
            logger.info(f"   File: {file_path.name}")
            return file_path

        md_file = self.temp_dir / f"{file_path.stem}.md"

        # If EPUB, convert to Markdown
        if file_ext == '.epub':
            logger.info("EPUB format detected, converting to Markdown...")
            script_dir = get_script_dir()
            convert_script = script_dir / "convert_epub.py"

            # SECURITY FIX: Use list-based subprocess call instead of shell=True
            result = subprocess.run(
                ['python3', str(convert_script), str(file_path), str(md_file)],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"Conversion failed: {result.stderr}")
                return file_path

            logger.success(f"Conversion successful: {md_file}")

            # Check file size, split if too large
            with open(md_file, 'r', encoding='utf-8') as f:
                word_count = self.count_words(f.read())
            logger.info(f"Word count: {word_count:,}")

            if word_count > WORD_LIMIT_PER_CHUNK:
                logger.warning(f"File exceeds {WORD_LIMIT_PER_CHUNK:,} words (NotebookLM CLI limit)")
                return self.split_markdown_file(md_file)
            else:
                return md_file

        else:
            logger.info(f"File format: {file_ext}, using directly")
            return file_path

    def _clean_title(self, title: str) -> str:
        """
        Clean up book title for notebook name.

        Args:
            title: Raw title string

        Returns:
            Cleaned title string
        """
        title = re.sub(r'\[.*?\]', '', title)
        title = re.sub(r'\(.*?\)', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        if len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH] + "..."
        return title

    def upload_to_notebooklm(
        self,
        file_path: Path | list[Path],
        title: Optional[str] = None
    ) -> dict:
        """
        Upload file(s) to NotebookLM.

        Args:
            file_path: Path to file or list of chunk paths
            title: Optional notebook title

        Returns:
            Dictionary with upload result
        """
        logger.section("Uploading to NotebookLM")

        # Handle file list (chunked files)
        if isinstance(file_path, list):
            logger.info(f"Detected {len(file_path)} file chunks")

            # Use first file to determine title
            first_file = file_path[0]
            if not title:
                title = first_file.stem.replace('_part1', '').replace('_', ' ')
                title = self._clean_title(title)

            # Create notebook
            logger.info(f"Creating notebook: {title}")

            # SECURITY FIX: Use list-based subprocess call
            result = subprocess.run(
                ['notebooklm', 'create', title, '--json'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {"success": False, "error": result.stderr}

            try:
                data = json.loads(result.stdout)
                notebook_id = data['notebook']['id']
                logger.success(f"Notebook created (ID: {notebook_id[:8]}...)")
            except (json.JSONDecodeError, KeyError) as e:
                return {"success": False, "error": f"Failed to parse notebook ID: {e}"}

            # Upload all chunks
            source_ids: list[str] = []
            for i, chunk_file in enumerate(file_path, 1):
                logger.info(f"Uploading chunk {i}/{len(file_path)}: {chunk_file.name}")
                result = subprocess.run(
                    ['notebooklm', 'source', 'add',
                     '--notebook', notebook_id,
                     '--type', 'file',
                     str(chunk_file),
                     '--json'],
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    logger.warning(f"Chunk {i} upload failed: {result.stderr}")
                    continue

                try:
                    data = json.loads(result.stdout)
                    source_id = data['source']['id']
                    source_ids.append(source_id)
                    logger.success(f"   Success (ID: {source_id[:8]}...)")
                except (json.JSONDecodeError, KeyError):
                    logger.warning(f"Chunk {i} parse failed")

            return {
                "success": len(source_ids) > 0,
                "notebook_id": notebook_id,
                "source_ids": source_ids,
                "title": title,
                "chunks": len(file_path)
            }

        # Single file upload
        if not title:
            title = file_path.stem.replace('_', ' ')
            title = self._clean_title(title)

        # Create notebook
        logger.info(f"Creating notebook: {title}")

        # SECURITY FIX: Use list-based subprocess call
        result = subprocess.run(
            ['notebooklm', 'create', title, '--json'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {"success": False, "error": result.stderr}

        try:
            data = json.loads(result.stdout)
            notebook_id = data['notebook']['id']
            logger.success(f"Notebook created (ID: {notebook_id[:8]}...)")
        except (json.JSONDecodeError, KeyError) as e:
            return {"success": False, "error": f"Failed to parse notebook ID: {e}"}

        # Upload file
        logger.info("Uploading file...")
        result = subprocess.run(
            ['notebooklm', 'source', 'add',
             '--notebook', notebook_id,
             '--type', 'file',
             str(file_path),
             '--json'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {"success": False, "error": result.stderr}

        try:
            data = json.loads(result.stdout)
            source_id = data['source']['id']
            logger.success(f"Upload successful (ID: {source_id[:8]}...)")

            return {
                "success": True,
                "notebook_id": notebook_id,
                "source_id": source_id,
                "title": title
            }
        except (json.JSONDecodeError, KeyError) as e:
            return {"success": False, "error": f"Failed to parse source ID: {e}"}


async def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Z-Library Auto Download and Upload to NotebookLM")
        print("")
        print("Usage: uv run scripts/upload.py <Z-Library URL>")
        sys.exit(1)

    # Environment check
    if not check_environment():
        print("")
        print("=" * 70)
        print("Environment check failed. Please fix the issues above.")
        print("Run 'uv run scripts/setup.py' to set up all dependencies.")
        print("=" * 70)
        sys.exit(1)

    url = sys.argv[1]
    uploader = ZLibraryAutoUploader()

    # Download
    downloaded_file, file_format = await uploader.download_from_zlibrary(url)

    if not downloaded_file or not downloaded_file.exists():
        logger.section("Download failed, cannot continue")
        sys.exit(1)

    # Convert
    final_file = uploader.convert_to_txt(downloaded_file, file_format)

    # Upload
    result = uploader.upload_to_notebooklm(final_file)

    print("")
    logger.section("")
    if result['success']:
        print("Complete workflow finished!")
        print("=" * 70)
        print(f"Book: {result['title']}")
        print(f"Notebook ID: {result['notebook_id']}")

        # Handle chunked upload result
        if 'chunks' in result:
            print(f"Chunks: {result['chunks']}")
            print(f"Successfully uploaded {len(result['source_ids'])}/{result['chunks']} chunks")
            print("   Source IDs:")
            for sid in result['source_ids']:
                print(f"      - {sid}")
        else:
            print(f"Source ID: {result['source_id']}")

        print("")
        print("Next steps:")
        print(f"   notebooklm ask --notebook {result['notebook_id']} \"What are the key points of this book?\"")
    else:
        print("Upload failed")
        print("=" * 70)
        print(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
