# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Owattayo is a FastAPI application that receives HTTP requests and notifies. It's primarily designed for notifying about Claude Code work completion. The application provides both Discord webhook notifications and browser-based notifications through Server-Sent Events (SSE).

## Development Commands

### Running the Application
```bash
# Development server
uv run fastapi dev

# Production server
fastapi run --host 0.0.0.0 --port 8000
```

### Docker Operations
```bash
# Build image
docker build -t owattayo .

# Run container
docker run -p 8000:8000 owattayo
```

### Package Management
This project uses `uv` for dependency management:
```bash
# Install dependencies
uv sync

# Add new dependency
uv add package_name

# Update lock file
uv lock
```

## Architecture

### Core Components

**main.py**: Single-file FastAPI application with three main classes:
- `Settings`: Pydantic settings management with environment variables
- `NotificationManager`: Handles Server-Sent Events for browser notifications
- `StopEvent`: Data model for incoming notification requests

### Key Features

**Dual Notification System**:
- Discord webhook notifications via HTTP POST
- Browser notifications via SSE endpoint `/notifications`

**Transcript Processing** (`extract_prompt` function):
- Reads Claude Code transcript files (JSON Lines format)
- Extracts the last user message for notification content
- Handles file I/O errors gracefully

### API Endpoints

- `POST /notify`: Main notification endpoint, accepts optional `StopEvent` payload
- `GET /notifications`: SSE endpoint for real-time browser notifications
- Static file serving from `/static` directory

### Configuration

Environment variables (via `.env` file or system env):
- `DISCORD_WEBHOOK_URL`: Discord webhook URL for notifications
- `TITLE`: Notification title (default: "Claude Code work completed.")
- `MESSAGE_TEMPLATE`: Template string for notification message (default: "prompt: {prompt}")
- `SHOW_PROMPT`: Boolean to include extracted prompt in notifications (default: true)

### Frontend

**static/index.html**: Japanese-language web interface featuring:
- SSE connection status monitoring
- Browser notification permission management
- Real-time notification log display
- Responsive design with teal/cyan color scheme

## File Structure

```
/
├── main.py              # Main FastAPI application
├── pyproject.toml       # Project dependencies and metadata
├── uv.lock             # Dependency lock file
├── Dockerfile          # Multi-stage Docker build
├── static/
│   ├── index.html      # Web interface
│   └── favicon.svg     # Site favicon
└── .devcontainer/      # Development container configuration
```

## Dependencies

Core dependencies:
- **FastAPI**: Web framework with built-in async support
- **Pydantic**: Data validation and settings management
- **sse-starlette**: Server-Sent Events implementation
- **aiofiles**: Async file I/O for transcript reading
- **requests**: HTTP client for Discord webhook calls

## Integration Notes

This application is designed to work with Claude Code's hook system. Configure Claude Code to POST to `/notify` endpoint with transcript path when work completes.