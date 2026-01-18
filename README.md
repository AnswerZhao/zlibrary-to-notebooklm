# Z-Library to NotebookLM

[English](#english) | [简体中文](#简体中文)

---

<a name="english"></a>
# Z-Library to NotebookLM

> Automatically download books from Z-Library and upload to Google NotebookLM with one command.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-success.svg)](https://claude.ai/claude-code)

## ⚠️ Disclaimer

**For educational, research, and technical demonstration purposes only.** Please comply with local laws and copyright regulations. Use only for resources you have legal access to.

---

## Features

- 🔐 **One-time login** - Save Z-Library session, reuse forever
- 📥 **Smart download** - PDF preferred (preserves formatting), EPUB auto-converted
- 📦 **Auto chunking** - Large files (>350k words) automatically split
- 🤖 **Fully automated** - Complete workflow with single command
- 🎯 **Format adaptive** - Supports PDF, EPUB, and more

## Prerequisites

This skill requires:

- **Python 3.10+** - Required for scripts execution
- **uv** - Modern Python package manager (auto-installs dependencies)

The setup script will automatically verify these requirements.

## Quick Start

### 1. Install the Skill

```bash
# Clone to Claude Skills directory
cd ~/.claude/skills
git clone https://github.com/AnswerZhao/zlibrary-to-notebooklm.git
cd zlibrary-to-notebooklm

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run setup (one-time) - installs Python dependencies and tools
uv run scripts/setup.py

# Complete login (one-time)
uv run scripts/login.py    # Z-Library
notebooklm login           # NotebookLM
```

### 2. Use in Claude Code

Just provide a Z-Library URL:

```
Upload this book to NotebookLM: https://zh.zlib.li/book/12345/...
```

Claude will automatically:
- Check environment and prompt setup if needed
- Download the book (PDF preferred, EPUB converted)
- Upload to NotebookLM
- Return the Notebook ID with follow-up questions

### Example Response

```
Download successful!
Notebook ID: cd5d140c-ca3c-4e30-a3b1-69f32bfbed00

You can now ask:
- "What are the core ideas in this book?"
- "Summarize Chapter 3"
```

## What This Skill Does

```
Z-Library URL → Download → Convert (if needed) → Upload to NotebookLM → Return Notebook ID
```

## File Structure (Optimized)

```
zlibrary-to-notebooklm/
├── SKILL.md                    # Core skill definition (concise)
├── pyproject.toml              # Python dependency management
├── references/
│   └── TROUBLESHOOTING.md      # Detailed troubleshooting (lazy-loaded)
└── scripts/                    # Executable scripts
    ├── upload.py               # Main workflow
    ├── login.py                # Z-Library login
    ├── setup.py                # Dependency installer
    ├── convert_epub.py         # EPUB converter
    ├── config.py               # Configuration
    └── logger.py               # Logging utilities
```

## Optimizations Made

This version is optimized from [zstmfhy/zlibrary-to-notebooklm](https://github.com/zstmfhy/zlibrary-to-notebooklm) with focus on **user experience improvements**:

### 💡 Better User Experience

- ✅ **Simplified setup** - One command (`uv run scripts/setup.py`) handles everything
- ✅ **Auto-detection** - Script checks dependencies and login status automatically
- ✅ **Clear error messages** - Specific fix suggestions instead of cryptic errors
- ✅ **Faster uploads** - Switched to notebooklm-py for more reliable uploads
- ✅ **Reduced token usage** - Progressive disclosure design loads only what's needed

### 🔧 Technical Improvements

- ✅ **Unified dependency management** - `pyproject.toml` + `uv` replaces npm
- ✅ **Removed redundant files** - Deleted auxiliary docs per skill best practices
- ✅ **Streamlined SKILL.md** - 140 lines → 58 lines for faster loading
- ✅ **Environment validation** - Pre-flight checks prevent failed uploads

### 📦 What Changed

| Before | After |
|--------|-------|
| npm notebooklm-cli | Python notebooklm-py |
| requirements.txt | pyproject.toml (uv-managed) |
| README.md, docs/, tests/ | Removed (skill best practices) |
| Manual setup | Auto-setup with one command |
| Cryptic errors | Clear error messages with fixes |

## License

MIT License

---

<a name="简体中文"></a>
# Z-Library 到 NotebookLM

> 一键将 Z-Library 书籍自动下载并上传到 Google NotebookLM

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-success.svg)](https://claude.ai/claude-code)

## ⚠️ 免责声明

**仅供学习、研究和技术演示用途。** 请严格遵守当地法律法规和版权规定，仅用于您拥有合法访问权限的资源。

---

## 特性

- 🔐 **一次登录，永久使用** - 保存 Z-Library 会话状态
- 📥 **智能下载** - 优先 PDF（保留排版），EPUB 自动转换
- 📦 **自动分块** - 大文件（>35万词）自动分割
- 🤖 **全自动化** - 一条命令完成整个流程
- 🎯 **格式自适应** - 支持 PDF、EPUB 等多种格式

## 系统要求

本 Skill 需要：

- **Python 3.10+** - 脚本执行所需
- **uv** - 现代 Python 包管理器（自动安装依赖）

安装脚本会自动验证这些要求。

## 快速开始

### 1. 安装 Skill

```bash
# 克隆到 Claude Skills 目录
cd ~/.claude/skills
git clone https://github.com/AnswerZhao/zlibrary-to-notebooklm.git
cd zlibrary-to-notebooklm

# 安装 uv（如未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 运行安装脚本（仅需一次）- 安装 Python 依赖和工具
uv run scripts/setup.py

# 完成登录（仅需一次）
uv run scripts/login.py    # Z-Library
notebooklm login           # NotebookLM
```

### 2. 在 Claude Code 中使用

只需提供 Z-Library URL：

```
上传这本书到 NotebookLM: https://zh.zlib.li/book/12345/...
```

Claude 将自动：
- 检查环境并在需要时提示设置
- 下载书籍（优先 PDF，EPUB 自动转换）
- 上传到 NotebookLM
- 返回笔记本 ID 和后续问题建议

### 示例响应

```
下载成功！
笔记本 ID: cd5d140c-ca3c-4e30-a3b1-69f32bfbed00

你可以问：
- "这本书的核心观点是什么？"
- "总结第3章"
```

## 工作流程

```
Z-Library URL → 下载 → 转换（如需要）→ 上传到 NotebookLM → 返回笔记本 ID
```

## 文件结构（已优化）

```
zlibrary-to-notebooklm/
├── SKILL.md                    # 技能核心定义（精简）
├── pyproject.toml              # Python 依赖管理
├── references/
│   └── TROUBLESHOOTING.md      # 详细故障排除（按需加载）
└── scripts/                    # 可执行脚本
    ├── upload.py               # 主流程
    ├── login.py                # Z-Library 登录
    ├── setup.py                # 依赖安装器
    ├── convert_epub.py         # EPUB 转换器
    ├── config.py               # 配置
    └── logger.py               # 日志工具
```

## 优化内容

本版本基于 [zstmfhy/zlibrary-to-notebooklm](https://github.com/zstmfhy/zlibrary-to-notebooklm) 进行了优化，**专注于用户体验改善**：

### 💡 更好的用户体验

- ✅ **简化安装** - 一条命令 (`uv run scripts/setup.py`) 完成所有设置
- ✅ **自动检测** - 脚本自动检查依赖和登录状态
- ✅ **清晰的错误提示** - 具体的修复建议，而非晦涩的错误信息
- ✅ **更快的上传** - 切换到 notebooklm-py，上传更稳定
- ✅ **减少 token 消耗** - 渐进式披露设计，只加载需要的内容

### 🔧 技术改进

- ✅ **统一依赖管理** - `pyproject.toml` + `uv` 替代 npm
- ✅ **移除冗余文件** - 遵循 skill 最佳实践删除辅助文档
- ✅ **精简 SKILL.md** - 140 行 → 58 行，加载更快
- ✅ **环境验证** - 预检查防止上传失败

### 📦 主要变化

| 之前 | 之后 |
|------|------|
| npm notebooklm-cli | Python notebooklm-py |
| requirements.txt | pyproject.toml (uv 管理) |
| README.md, docs/, tests/ | 已删除（skill 最佳实践） |
| 手动设置 | 一键自动设置 |
| 晦涩错误 | 清晰的错误提示和修复建议 |

## 许可证

MIT License
