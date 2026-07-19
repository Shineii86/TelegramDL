# 🤝 Contributing to TelegramDL

Thanks for your interest in contributing! Here's how you can help.

---

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [How to Contribute](#-how-to-contribute)
- [Coding Guidelines](#-coding-guidelines)
- [Commit Messages](#-commit-messages)
- [Pull Request Process](#-pull-request-process)
- [Resources](#-resources)
- [Community](#-community)

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version | Link |
|------|---------|------|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| Git | Latest | [git-scm.com](https://git-scm.com/) |
| MongoDB | 6.0+ | [mongodb.com](https://www.mongodb.com/try/download/community) |
| FFmpeg | Latest | [ffmpeg.org](https://ffmpeg.org/download.html) |

### Fork & Clone

```bash
# 1. Fork the repository on GitHub
# https://github.com/Shineii86/TelegramDL/fork

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/TelegramDL.git
cd TelegramDL

# 3. Add upstream remote
git remote add upstream https://github.com/Shineii86/TelegramDL.git

# 4. Create a feature branch
git checkout -b feature/your-feature-name
```

---

## 🛠️ Development Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install dev dependencies
pip install pytest pytest-asyncio black flake8 mypy

# 4. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 5. Run the bot
python3 bot.py
```

### Project Structure

```
TelegramDL/
├── bot.py                  # Main entry point
├── config.py               # Configuration
├── app.py                  # Flask server
├── plugins/                # Bot commands
│   ├── start.py           # /start, /help, /login
│   ├── generate.py        # Core download logic
│   ├── backup.py          # Backup command
│   ├── broadcast.py       # Admin broadcast
│   ├── ytdl.py            # yt-dlp commands
│   ├── custom_bot.py      # Custom bot per user
│   └── settings.py        # User settings
├── database/               # Database layer
│   └── db.py              # MongoDB (Motor)
└── utils/                  # Utilities
    ├── ui.py              # UI components
    ├── progress.py        # Progress bar
    ├── splitter.py        # File splitting
    ├── ytdl.py            # yt-dlp wrapper
    └── audio_metadata.py  # Audio metadata
```

---

## 📝 How to Contribute

### 🐛 Report Bugs

1. Check [existing issues](https://github.com/Shineii86/TelegramDL/issues)
2. If not found, [create a new issue](https://github.com/Shineii86/TelegramDL/issues/new?template=bug_report.yml)
3. Include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Error logs
   - Your environment (platform, Python version)

### 💡 Suggest Features

1. Check [existing discussions](https://github.com/Shineii86/TelegramDL/issues)
2. [Create a feature request](https://github.com/Shineii86/TelegramDL/issues/new?template=feature_request.yml)
3. Include:
   - Problem statement
   - Proposed solution
   - Alternatives considered

### 🔀 Submit Code

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📐 Coding Guidelines

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use `black` for formatting
- Use `flake8` for linting
- Use type hints where possible

```python
# Good
async def download_file(
    client: Client,
    message_id: int,
    chat_id: int
) -> Optional[str]:
    """Download a file from Telegram."""
    try:
        file = await client.get_messages(chat_id, message_id)
        return await client.download_media(file)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None
```

### File Naming

- Use `snake_case` for files and functions
- Use `PascalCase` for classes
- Use `UPPER_CASE` for constants

```python
# Files
progress.py
audio_metadata.py

# Functions
def download_file()
async def handle_callback()

# Classes
class DownloadProgress
class UserManager

# Constants
MAX_FILE_SIZE = 2048
DEFAULT_WAITING_TIME = 10
```

### Async/Await

- Use `async/await` for all Telegram operations
- Never block the event loop
- Use `asyncio.gather()` for parallel operations

```python
# Good
async def process_messages(messages):
    tasks = [handle_message(msg) for msg in messages]
    await asyncio.gather(*tasks)

# Bad
def process_messages(messages):
    for msg in messages:
        handle_message(msg)  # Blocking!
```

### Error Handling

- Always handle exceptions
- Log errors with context
- Provide user-friendly error messages

```python
try:
    file = await client.download_media(message)
except FloodWaitError as e:
    await asyncio.sleep(e.value)
    file = await client.download_media(message)
except Exception as e:
    logger.error(f"Download failed: {e}")
    await message.reply("❌ Download failed. Please try again.")
```

---

## 💬 Commit Messages

### Format

```
<type>: <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting (no code change) |
| `refactor` | Code restructuring |
| `test` | Adding tests |
| `chore` | Build process/tooling |

### Examples

```bash
# Feature
git commit -m "feat: add file splitting for large files"

# Bug fix
git commit -m "fix: handle FloodWaitError in batch download"

# Documentation
git commit -m "docs: update README with deployment guide"

# Refactor
git commit -m "refactor: extract progress bar to utils"
```

---

## 🔀 Pull Request Process

### 1. Before Submitting

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: your feature description"

# Push to your fork
git push origin feature/your-feature
```

### 2. PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
- [ ] All tests pass

### 3. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested on Google Colab
- [ ] Tested on Docker
- [ ] Manual testing

## Related Issues
Fixes #
```

---

## 📚 Resources

### 🔧 Official Documentation

| Resource | Link | Description |
|----------|------|-------------|
| Python Docs | [docs.python.org](https://docs.python.org/3/) | Official Python documentation |
| Telegram API | [core.telegram.org](https://core.telegram.org/api) | Telegram Bot API |
| Kurigram | [github.com/KurimuzonAkuma/kurigram](https://github.com/KurimuzonAkuma/kurigram) | Pyrogram fork |
| Pyrogram | [docs.pyrogram.org](https://docs.pyrogram.org/) | Pyrogram documentation |
| MongoDB | [docs.mongodb.com](https://docs.mongodb.com/) | MongoDB documentation |
| Motor | [motor.readthedocs.io](https://motor.readthedocs.io/) | Async MongoDB driver |
| yt-dlp | [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | Video downloader |
| Flask | [flask.palletsprojects.com](https://flask.palletsprojects.com/) | Web framework |

### 📖 Tutorials & Guides

| Resource | Link | Description |
|----------|------|-------------|
| Python Async | [docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html) | Async programming guide |
| Git Basics | [git-scm.com/book](https://git-scm.com/book) | Git documentation |
| PEP 8 | [peps.python.org/pep-0008](https://peps.python.org/pep-0008/) | Python style guide |
| Conventional Commits | [conventionalcommits.org](https://www.conventionalcommits.org/) | Commit message format |
| GitHub Flow | [docs.github.com/en/get-started](https://docs.github.com/en/get-started/using-github/github-flow) | Git workflow |

### 🛠️ Development Tools

| Tool | Link | Purpose |
|------|------|---------|
| VS Code | [code.visualstudio.com](https://code.visualstudio.com/) | Code editor |
| Python Extension | [marketplace.visualstudio.com](https://marketplace.visualstudio.com/items?itemName=ms-python.python) | Python support |
| Black | [github.com/psf/black](https://github.com/psf/black) | Code formatter |
| Flake8 | [flake8.pycqa.org](https://flake8.pycqa.org/) | Linter |
| MyPy | [mypy-lang.org](https://mypy-lang.org/) | Type checker |
| Pytest | [docs.pytest.org](https://docs.pytest.org/) | Testing framework |

### 📺 Video Tutorials

| Topic | Link | Description |
|-------|------|-------------|
| Python Basics | [youtube.com/watch?v=rfscVS0vtbw](https://www.youtube.com/watch?v=rfscVS0vtbw) | Python for beginners |
| Async Python | [youtube.com/watch?v=93YK-zYq2Cs](https://www.youtube.com/watch?v=93YK-zYq2Cs) | Async programming |
| Git Tutorial | [youtube.com/watch?v=HVsySz-h9r4](https://www.youtube.com/watch?v=HVsySz-h9r4) | Git & GitHub |
| Telegram Bots | [core.telegram.org/bots](https://core.telegram.org/bots/tutorial) | Official bot tutorial |
| MongoDB Basics | [youtube.com/watch?v=-OOmMSshOyM](https://www.youtube.com/watch?v=-OOmMSshOyM) | MongoDB tutorial |

### 📦 Useful Libraries

| Library | Link | Purpose |
|---------|------|---------|
| aiofiles | [github.com/Tinche/aiofiles](https://github.com/Tinche/aiofiles) | Async file operations |
| mutagen | [github.com/quodlibet/mutagen](https://github.com/quodlibet/mutagen) | Audio metadata |
| nest-asyncio | [github.com/erdewit/nest_asyncio](https://github.com/erdewit/nest_asyncio) | Nested async support |
| tgcrypto | [github.com/pyrogram/tgcrypto](https://github.com/pyrogram/tgcrypto) | Telegram crypto |

### 🔗 Community Resources

| Resource | Link | Description |
|----------|------|-------------|
| Telegram Group | [t.me/Shineii86](https://t.me/Shineii86) | Developer contact |
| GitHub Discussions | [github.com/Shineii86/TelegramDL/discussions](https://github.com/Shineii86/TelegramDL/discussions) | Community discussions |
| Stack Overflow | [stackoverflow.com](https://stackoverflow.com/questions/tagged/python) | Q&A |
| Reddit | [r/Python](https://www.reddit.com/r/Python/) | Python community |
| Discord | [discord.gg/python](https://discord.gg/python) | Python Discord |

---

## 👥 Community

### Communication Channels

| Channel | Link | Purpose |
|---------|------|---------|
| Issues | [GitHub Issues](https://github.com/Shineii86/TelegramDL/issues) | Bug reports, features |
| Discussions | [GitHub Discussions](https://github.com/Shineii86/TelegramDL/discussions) | General discussion |
| Telegram | [t.me/Shineii86](https://t.me/Shineii86) | Direct contact |

### Code of Conduct

- Be respectful and inclusive
- Help newcomers
- Focus on constructive feedback
- No harassment or discrimination

---

## ❓ Questions?

If you have questions:

1. Check the [README](README.md)
2. Search [existing issues](https://github.com/Shineii86/TelegramDL/issues)
3. Ask in [Discussions](https://github.com/Shineii86/TelegramDL/discussions)
4. Contact on [Telegram](https://t.me/Shineii86)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

<div align="center">

**Thank you for contributing!** 🎉

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Shineii86/TelegramDL)

</div>
