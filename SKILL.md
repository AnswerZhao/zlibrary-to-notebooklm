---
name: zlibrary-to-notebooklm
description: Z-Library to NotebookLM automation. Download books from Z-Library URLs (zlib.li, z-lib.org, zh.zlib.li) and upload to Google NotebookLM with automatic PDF/EPUB conversion and chunking for large files. Use when user provides Z-Library link or asks to upload/download books to NotebookLM.
---

# Z-Library to NotebookLM

## Quick Start

First run? Install dependencies:
```bash
cd ~/.claude/skills/zlibrary-to-notebooklm
uv run scripts/setup.py
```

Then upload a book:
```bash
uv run scripts/upload.py "<Z-Library URL>"
```

## Workflow

1. **Check login** - Prompt user to login if needed
   - Z-Library: `uv run scripts/login.py`
   - NotebookLM: `notebooklm login`

2. **Download** - Script auto-downloads (PDF preferred, EPUB converted to Markdown)

3. **Upload** - Creates NotebookLM notebook and uploads content

4. **Return** - Report success with Notebook ID and follow-up questions

## Example Response

```
Download successful!
Notebook ID: 22916611-c68c-4065-a657-99339e126fb4

You can now ask:
- "What are the core ideas in this book?"
- "Summarize Chapter 3"
```

## Troubleshooting

For detailed error handling, see [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md).

Quick fixes:
- **Missing dependencies**: `uv run scripts/setup.py`
- **Z-Library session expired**: `uv run scripts/login.py`
- **NotebookLM login required**: `notebooklm login`

## Legal Notice

Only process content the user has legal access to. If URL appears to be copyrighted commercial content, remind user:

> "Please ensure you have legal access. This tool is for educational and research purposes only."
