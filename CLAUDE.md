# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv
uv sync

# Activate virtual environment (if needed manually)
source .venv/bin/activate
```

### Running the Application
```bash
# Development server with auto-reload
uv run fastapi dev

# Production server
uv run fastapi run

# Docker development
docker build -t owattayo .
docker run -p 8000:8000 owattayo
```

### Code Quality
```bash
# Format code (configured in devcontainer)
# Python formatting is handled by Ruff automatically on save in VS Code
```

## Architecture Overview

This is a single-file FastAPI application (`main.py`) that provides Claude Code completion notifications through dual channels:

### Core Components

1. **Settings Management** (`Settings` class):
   - Uses pydantic-settings with `.env` file support
   - Key settings: `discord_webhook_url`, `title`, `message_template`

2. **Event Processing** (`StopEvent` model):
   - Handles Claude Code stop events with optional transcript parsing
   - Extracts the last user prompt from JSON Lines transcript files
   - Supports both direct prompt and transcript file inputs

3. **Notification System** (`NotificationManager`):
   - Manages Server-Sent Events (SSE) for browser notifications
   - Maintains list of connected clients via asyncio queues
   - Broadcasts notifications to all connected clients

4. **API Endpoints**:
   - `POST /notify`: Main notification endpoint for Claude Code hooks
   - `GET /notifications`: SSE endpoint for real-time browser notifications
   - `GET /`: Serves static web interface

5. **Static Web Interface** (`static/index.html`):
   - Japanese language UI with modern CSS styling
   - Real-time connection status monitoring
   - Browser notification permission management
   - Notification log display

### Integration with Claude Code

The application integrates with Claude Code's hook system through the "Stop" hook:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command", 
            "command": "curl -X POST http://localhost:8000/notify -H \"Content-Type: application/json\" -d @-"
          }
        ]
      }
    ]
  }
}
```

### Environment Variables

Configure in `.env` file:
- `DISCORD_WEBHOOK_URL`: Discord webhook for notifications (optional)
- `TITLE`: Notification title (default: "Claude Code work completed.")  
- `MESSAGE_TEMPLATE`: Template for notification message (default: "prompt: {prompt}")

### Development Container

The project includes a comprehensive devcontainer setup with:
- Python 3.12 with uv and pre-commit
- Claude Code integration
- Custom firewall and workspace ownership features
- VS Code extensions for Python development (Ruff, YAML)
- Persistent volumes for bash history and Claude config

### Transcript Processing

The application can parse Claude Code transcript files (JSON Lines format) to extract the last user message that triggered the completion, filtering out tool use results to focus on actual user prompts.