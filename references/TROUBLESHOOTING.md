# Troubleshooting Guide

Detailed error handling for Z-Library to NotebookLM skill.

---

## Installation Issues

### uv not found

**Error:** `command not found: uv`

**Solution:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: brew install uv
```

### Python dependencies missing

**Error:** `ModuleNotFoundError: No module named 'playwright'`

**Solution:**
```bash
cd ~/.claude/skills/zlibrary-to-notebooklm
uv run scripts/setup.py
```

### Playwright browser not found

**Error:** `Executable doesn't exist at ...chromium`

**Solution:**
```bash
uv run playwright install chromium
```

### NotebookLM CLI not found

**Error:** `command not found: notebooklm`

**Solution:**
```bash
uv tool install "notebooklm-py[browser]" --with "httpx[socks]"
uv tool run playwright install chromium
```

---

## Login Issues

### Z-Library session not found

**Error:** `Session state not found`

**Solution:**
```bash
cd ~/.claude/skills/zlibrary-to-notebooklm
uv run scripts/login.py
```

Steps:
1. Browser opens automatically
2. Complete login in browser
3. Return to terminal and press ENTER

### Z-Library session expired

**Symptoms:** Download fails, redirect to login page

**Solution:**
```bash
rm ~/.zlibrary/storage_state.json
cd ~/.claude/skills/zlibrary-to-notebooklm
uv run scripts/login.py
```

### NotebookLM login required

**Error:** `NotebookLM login may be required`

**Solution:**
```bash
notebooklm login
```

Complete Google login in the browser that opens.

---

## Download Issues

### Download link not found

**Error:** `Download link not found`

**Causes:**
- Z-Library page structure changed
- Not logged in
- URL is invalid

**Solution:**
1. Check login status: `ls ~/.zlibrary/storage_state.json`
2. Verify URL works in browser
3. Re-login if needed: `uv run scripts/login.py`

### Download timeout

**Error:** `Download failed` or timeout

**Solution:**
1. Check network connection
2. Retry the download
3. If using VPN, try switching nodes

### Conversion timeout

**Symptoms:** Waits for conversion, then fails

**Solution:**
- This is normal - wait up to 60 seconds
- If consistently failing, try PDF instead of EPUB

---

## Upload Issues

### File too large

**Error:** Upload fails with large file

**Solution:**
The script automatically chunks files >350k words. If still failing:
1. Check file size: `ls -lh ~/Downloads/*.pdf`
2. NotebookLM limit: 200MB per file
3. Manually split if needed

### NotebookLM create failed

**Error:** `Failed to parse notebook ID`

**Solution:**
```bash
# Check if logged in
notebooklm list

# Re-login if needed
notebooklm login
```

### Source add failed

**Error:** `Chunk upload failed`

**Solution:**
1. Check file exists and is readable
2. Verify notebooklm CLI is working: `notebooklm --version`
3. Check notebook ID is valid

---

## Environment Issues

### Cannot write to directory

**Error:** `PermissionError` or `Cannot write to...`

**Solution:**
```bash
# Check permissions
ls -la ~/.zlibrary

# Fix if needed
chmod 700 ~/.zlibrary
chmod 600 ~/.zlibrary/storage_state.json
```

### Downloads directory not found

**Error:** File operations fail in Downloads

**Solution:**
```bash
# Create Downloads directory
mkdir -p ~/Downloads
```

---

## Network Issues

### Cannot reach Z-Library

**Error:** Connection refused or timeout

**Solution:**
1. Check if site is up: `curl -I https://zh.zlib.li`
2. Try alternative domains:
   - https://z-lib.org/
   - https://zlibrary.org/
3. Check VPN/proxy settings

### Slow download

**Solution:**
- Normal for large files
- EPUB conversion takes time on Z-Library servers
- Be patient, script waits automatically

---

## Script Issues

### Script crashes with Python error

**Solution:**
1. Check Python version: `python3 --version` (requires 3.10+)
2. Re-run setup: `uv run scripts/setup.py`
3. Check error details and report if persistent

### Browser crashes during download

**Solution:**
1. Update Playwright: `uv run playwright install chromium --force`
2. Check system resources (memory)
3. Close other browser windows

---

## Quick Reference

| Error | Solution |
|-------|----------|
| `command not found: uv` | Install uv |
| `command not found: notebooklm` | `uv run scripts/setup.py` |
| `Session state not found` | `uv run scripts/login.py` |
| `NotebookLM login required` | `notebooklm login` |
| `Download link not found` | Check URL, re-login |
| Upload failed | `notebooklm list` to check status |
| Permission denied | Check `~/.zlibrary` permissions |
