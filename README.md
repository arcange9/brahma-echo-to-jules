<div align="center">
  <img src="assets/Brahma_Lite_Logo.png" alt="Brahma Echo" width="260" />

  <h1>Brahma Echo</h1>

  <p><strong>Open-source Windows desktop AI assistant</strong></p>
  <p>Voice-first automation · contextual desktop intelligence · productivity workflows</p>

  <p>
    <a href="#overview"><img src="https://img.shields.io/badge/experience-open%20source-blue?style=for-the-badge" alt="Open Source" /></a>
    <a href="#getting-started"><img src="https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey?style=for-the-badge" alt="Windows" /></a>
    <a href="#features"><img src="https://img.shields.io/badge/tech-Gemini%20%2B%20OpenRouter-green?style=for-the-badge" alt="Gemini + OpenRouter" /></a>
  </p>

  <p>
    <a href="#quick-start"><img src="https://img.shields.io/badge/Quick%20Start-Install%20%26%20Run-success?style=flat-square" alt="Quick Start" /></a>
    <a href="#project-structure"><img src="https://img.shields.io/badge/Project%20Structure-Clean%20Architecture-lightgrey?style=flat-square" alt="Project Structure" /></a>
    <a href="#community"><img src="https://img.shields.io/badge/Community-Discord-purple?style=flat-square" alt="Community" /></a>
  </p>
</div>

---

## Overview

Brahma Echo is a premium Windows desktop assistant that combines voice and text control with automated workflows, screen-aware intelligence, and rich content generation.

Designed for advanced desktop productivity, Brahma Echo delivers:

- Voice-first command and desktop automation
- Application control, browser workflows, and file handling
- Contextual screen inspection and adaptive task execution
- Presentation, document, and report generation
- Remote control via Discord and Brahma Connect

## Quick Highlights

| Core capability | Why it matters |
|---|---|
| Voice-first assistant | Speak commands naturally and stay hands-free |
| Gemini + OpenRouter | Fast responses with resilient fallback support |
| Screen-aware context | Ask about visible windows and on-screen content |
| Document automation | Create presentations, docs, spreadsheets, and PDFs |
| Plugin-ready | Extend features with lightweight Python plugins |

## Key Benefits

- Wake-word support for “Brahma Echo” and responsive assistant activation
- Gemini 2.5 Flash-powered AI with OpenRouter fallback resilience
- Polished Qt interface with live status displays and workflow cards
- Modular action architecture for clean extensibility and automation
- Secure local configuration with file-based credential storage
- Device pairing and remote routing through Brahma Connect

## Features

### Intelligent Assistant

- Unified voice and typed command handling
- Wake-word listening and responsive assistant activation
- Dynamic screen inspection for context-aware answers
- Automatic briefings with Edge TTS playback
- Gemini-first AI with OpenRouter fallback resilience

### Productivity & Automation

- Open and control Windows apps, windows, files, and system actions
- Browser automation with Playwright-driven workflows
- Contextual automation based on screen content and notifications
- Reminder, meeting assistance, and notification management

### Content & Office Tools

- Generate presentation decks, summaries, and slide content
- Create Word documents and spreadsheets from prompts
- Export polished reports and deliverables as PDF
- Build landing pages and website workspaces locally

### Integrations

- Discord bridge for remote commands and collaboration
- OpenRouter fallback for uninterrupted AI access
- Configurable voice, UI, startup, and notification settings
- Brahma Connect for device discovery and command routing

## Getting Started

### Prerequisites

- Windows 10 or Windows 11
- Python 3.11 or Python 3.12
- Git installed
- Gemini API key
- OpenRouter API key (optional but recommended)

### 1. Clone the repository

```powershell
git clone https://github.com/titechprabhasolutions/Brahma-AI---Lite.git
cd "Brahma AI - Lite"
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
playwright install
```

### 4. Configure API credentials

Create `config/api_keys.json` with your keys:

```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY",
  "openrouter_api_key": "YOUR_OPENROUTER_API_KEY"
}
```

#### Gemini API Key

1. Create a Google Cloud or Gemini account.
2. Enable Gemini API access for your project.
3. Add the generated key to `gemini_api_key`.

#### OpenRouter API Key

1. Register at https://openrouter.ai.
2. Generate an `sk-or-` API key.
3. Add the key to `openrouter_api_key`.

### 5. Optional: Configure Discord integration

If you want Discord remote control, populate `config/discord_bot.json` with your bot credentials and connection settings.

### 6. Launch Brahma Echo

```powershell
python main.py
```

For a cleaner startup experience on Windows:

```powershell
start_brahma.vbs
```

## Configuration

Core configuration files:

- `config/api_keys.json` — Gemini and OpenRouter credentials
- `config/app_settings.json` — voice, UI, startup, and automation preferences
- `config/brahma_connect.json` — device pairing, gateway, and discovery settings
- `config/discord_bot.json` — Discord bridge configuration

## Project Structure

- `main.py` — application startup, AI orchestration, and command routing
- `ui.py` — Qt-based desktop interface and live assistant controls
- `actions/` — modular automation, document, and assistant tools
- `brahma_connect/` — local gateway, pairing, and remote routing
- `config/` — local settings, credentials, and runtime configuration
- `plugins/` — optional plugin extensions
- `tests/` — integration and validation tests

## Plugin System

Extend Brahma Echo with custom Python plugins by adding files to `plugins/`.

Supported hooks:

- `on_brahma_created(brahma)` — called when the assistant instance is initialized
- `on_startup(brahma)` — called after startup when plugins are registered
- `on_text_command(text, source, brahma=None)` — called for each incoming text command; return `True` to indicate the command was handled

## Best Practices

- Keep credentials in `config/api_keys.json` and avoid committing secrets.
- Use the virtual environment for all development and runtime sessions.
- Restart the app after changing config or adding plugins.
- Review `config/app_settings.json` to tune voice, UI, and automation behavior.

## Community & Support

- Discord: https://discord.gg/gEYmJKKtq3

## License

This project is published under a custom source-available license. See `LICENSE` for details.

## Maintainer

- Suryaansh Tiwari

> Preserve attribution and keep credentials secure when building on top of Brahma Echo.


---

## Windows Installer

Brahma Echo can be built into a Windows x64 executable and installer using GitHub Actions.

### Downloads

Download the latest release from the [Releases page](https://github.com/arcange9/brahma-echo-to-jules/releases):

- `Brahma-Echo-Setup.exe` — Full installer (recommended)
- `BrahmaEcho-Portable` — Portable, no install needed
- `BrahmaEcho-Debug` — Console debug build for troubleshooting

### System Requirements

- Windows 10 or Windows 11 (x64)
- Internet connection for AI providers
- Microphone for voice commands (optional but recommended)

### How the Build Works

The GitHub Actions workflow (`.github/workflows/build-windows.yml`) runs on `windows-latest` and:

1. Sets up Python 3.11
2. Installs all dependencies from `requirements.txt`
3. Runs an import audit and tests
4. Builds the executable with PyInstaller using `brahma-echo.spec`
5. Runs a smoke test to verify the executable starts
6. Builds the installer with Inno Setup (`installer/brahma_echo.iss`)
7. Uploads the installer and portable ZIP as artifacts
8. On version tags (`v*`), creates a GitHub Release with download links

### Installation

1. Download `Brahma-Echo-Setup.exe` from the Releases page
2. Run the installer
3. Follow the setup wizard (choose install location, shortcuts)
4. Launch Brahma Echo from the Start Menu or desktop shortcut

### First Run

On first launch, Brahma Echo automatically creates configuration files in:
```
%LOCALAPPDATA%\Brahma Echo\config\
```

Open the settings to configure:
- **Gemini API Key** (required) — Get one at [Google AI Studio](https://aistudio.google.com/apikey)
- **OpenRouter API Key** (optional) — Get one at [OpenRouter](https://openrouter.ai/keys)

### Playwright

Brahma Echo uses Playwright for browser automation features. During installation, you can check "Download Playwright Chromium browser" to set it up automatically.

If you skipped it during installation or prefer manual setup:

1. Open PowerShell as administrator
2. Navigate to the Brahma Echo install directory (typically `C:\Program Files\Brahma Echo\`)
3. Run: `powershell -ExecutionPolicy Bypass -File playwright_setup.ps1`

Or if you have Python installed:
```
pip install playwright
playwright install chromium
```

Note: All other Brahma Echo features work without the Playwright browser. Only browser automation requires it.

### Uninstallation

Uninstall via:
- Settings > Apps > Brahma Echo > Uninstall
- Or the uninstaller in the Start Menu > Brahma Echo > Uninstall Brahma Echo

Uninstalling removes the application but preserves your configuration and memory data in `%LOCALAPPDATA%\Brahma Echo\`.

### Troubleshooting Startup Failures

If Brahma Echo fails to start:

1. **Check the crash log:**
   ```
   %LOCALAPPDATA%\Brahma Echo\logs\crash_log.txt
   ```

2. **Check the application log:**
   ```
   %LOCALAPPDATA%\Brahma Echo\logs\brahma_echo.log
   ```

3. **Run in debug mode:**
   ```
   BrahmaEcho.exe --debug
   ```

4. **Use the Debug Build:**
   Download `BrahmaEchoDebug` from the GitHub Actions artifacts. This version shows a console window with full logging output, making it easier to identify startup issues.

5. **Verify API keys** are configured in `%LOCALAPPDATA%\Brahma Echo\config\api_keys.json`

6. **Check Playwright** browsers are installed if you use browser automation features

### Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `api_keys.json` | `%LOCALAPPDATA%\Brahma Echo\config\` | Gemini and OpenRouter API keys |
| `app_settings.json` | `%LOCALAPPDATA%\Brahma Echo\config\` | App preferences and settings |
| `discord_bot.json` | `%LOCALAPPDATA%\Brahma Echo\config\` | Discord bot configuration |
| `brahma_connect.json` | `%LOCALAPPDATA%\Brahma Echo\config\` | Brahma Connect settings |

### Building from Source

To build Brahma Echo locally:

```bash
# Clone the repository
git clone https://github.com/arcange9/brahma-echo-to-jules.git
cd brahma-echo-to-jules

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
python -m playwright install chromium

# Build the executable
pyinstaller brahma-echo.spec --noconfirm --clean

# Build the installer (requires Inno Setup)
# Install Inno Setup from https://jrsoftware.org/isdl.php
ISCC installer\brahma_echo.iss
```

The executable will be in `dist/BrahmaEcho/` and the installer in `installer/output/`.

To build the debug version (with console output):
```bash
pyinstaller brahma-echo-debug.spec --noconfirm --clean
```

The debug executable will be in `dist/BrahmaEchoDebug/`.
