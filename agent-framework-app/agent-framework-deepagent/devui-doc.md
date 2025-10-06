(Files content cropped to 300k characters, download full ingest to see more)
================================================
FILE: python/packages/devui/README.md
================================================
# DevUI - A Sample App for Running Agents and Workflows

A lightweight, standalone sample app interface for running entities (agents/workflows) in the Microsoft Agent Framework supporting **directory-based discovery**, **in-memory entity registration**, and **sample entity gallery**.

> [!IMPORTANT]
> DevUI is a **sample app** to help you get started with the Agent Framework. It is **not** intended for production use. For production, or for features beyond what is provided in this sample app, it is recommended that you build your own custom interface and API server using the Agent Framework SDK.

![DevUI Screenshot](./docs/devuiscreen.png)

## Quick Start

```bash
# Install
pip install agent-framework-devui --pre
```

You can also launch it programmatically

```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from agent_framework.devui import serve

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72°F and sunny"

# Create your agent
agent = ChatAgent(
    name="WeatherAgent",
    chat_client=OpenAIChatClient(),
    tools=[get_weather]
)

# Launch debug UI - that's it!
serve(entities=[agent], auto_open=True)
# → Opens browser to http://localhost:8080
```

In addition, if you have agents/workflows defined in a specific directory structure (see below), you can launch DevUI from the _cli_ to discover and run them.

```bash

# Launch web UI + API server
devui ./agents --port 8080
# → Web UI: http://localhost:8080
# → API: http://localhost:8080/v1/*
```

When DevUI starts with no discovered entities, it displays a **sample entity gallery** with curated examples from the Agent Framework repository to help you get started quickly.

## Directory Structure

For your agents to be discovered by the DevUI, they must be organized in a directory structure like below. Each agent/workflow must have an `__init__.py` that exports the required variable (`agent` or `workflow`).

**Note**: `.env` files are optional but will be automatically loaded if present in the agent/workflow directory or parent entities directory. Use them to store API keys, configuration variables, and other environment-specific settings.

```
agents/
├── weather_agent/
│   ├── __init__.py      # Must export: agent = ChatAgent(...)
│   ├── agent.py
│   └── .env             # Optional: API keys, config vars
├── my_workflow/
│   ├── __init__.py      # Must export: workflow = WorkflowBuilder()...
│   ├── workflow.py
│   └── .env             # Optional: environment variables
└── .env                 # Optional: shared environment variables
```

## Viewing Telemetry (Otel Traces) in DevUI

Agent Framework emits OpenTelemetry (Otel) traces for various operations. You can view these traces in DevUI by enabling tracing when starting the server.

```bash
devui ./agents --tracing framework
```

## OpenAI-Compatible API

For convenience, you can interact with the agents/workflows using the standard OpenAI API format. Just specify the `entity_id` in the `extra_body` field. This can be an `agent_id` or `workflow_id`.

```bash
# Standard OpenAI format
curl -X POST http://localhost:8080/v1/responses \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "model": "agent-framework",
  "input": "Hello world",
  "extra_body": {"entity_id": "weather_agent"}
}

```

## CLI Options

```bash
devui [directory] [options]

Options:
  --port, -p      Port (default: 8080)
  --host          Host (default: 127.0.0.1)
  --headless      API only, no UI
  --config        YAML config file
  --tracing       none|framework|workflow|all
  --reload        Enable auto-reload
```

## Key Endpoints

- `GET /v1/entities` - List discovered agents/workflows
- `GET /v1/entities/{entity_id}/info` - Get detailed entity information
- `POST /v1/entities/add` - Add entity from URL (for gallery samples)
- `DELETE /v1/entities/{entity_id}` - Remove remote entity
- `POST /v1/responses` - Execute agent/workflow (streaming or sync)
- `GET /health` - Health check
- `POST /v1/threads` - Create thread for agent (optional)
- `GET /v1/threads?agent_id={id}` - List threads for agent
- `GET /v1/threads/{thread_id}` - Get thread info
- `DELETE /v1/threads/{thread_id}` - Delete thread
- `GET /v1/threads/{thread_id}/messages` - Get thread messages

## Implementation

- **Discovery**: `agent_framework_devui/_discovery.py`
- **Execution**: `agent_framework_devui/_executor.py`
- **Message Mapping**: `agent_framework_devui/_mapper.py`
- **Session Management**: `agent_framework_devui/_session.py`
- **API Server**: `agent_framework_devui/_server.py`
- **CLI**: `agent_framework_devui/_cli.py`

## Examples

See `samples/` for working agent and workflow implementations.

## License

MIT



================================================
FILE: python/packages/devui/dev.md
================================================
# Testing DevUI - Quick Setup Guide

Here are the step-by-step instructions to test the new DevUI feature:

## 1. Get the Code

```bash
git pull
git checkout victordibia/devui
```

(or use the latest main branch if merged)

## 2. Setup Environment

Navigate to the Python directory and install dependencies:

```bash
cd python
uv sync --dev
source .venv/bin/activate
```

## 3. Configure Environment Variables

Create a `.env` file in the `python/` directory with your API credentials:

```bash
# Copy the example file
cp .env.example .env
```

Then edit `.env` and add your API keys:

```bash
# For OpenAI (minimum required)
OPENAI_API_KEY="your-api-key-here"
OPENAI_CHAT_MODEL_ID="gpt-4o-mini"

# Or for Azure OpenAI
AZURE_OPENAI_ENDPOINT="your-endpoint"
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="your-deployment-name"
```

## 4. Test DevUI

**Option A: In-Memory Mode (Recommended for quick testing)**

```bash
cd packages/devui/samples
python in_memory_mode.py
```

This runs a simple example with predefined agents and opens your browser automatically at http://localhost:8090

**Option B: Directory-Based Discovery**

```bash
cd packages/devui/samples
devui
```

This launches the UI with all example agents/workflows at http://localhost:8080

## 5. What You'll See

- A web interface for testing agents interactively
- Multiple example agents (weather assistant, general assistant, etc.)
- OpenAI-compatible API endpoints for programmatic access

## 6. API Testing (Optional)

You can also test via API calls:

```bash
curl -X POST http://localhost:8080/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agent-framework",
    "input": "What is the weather in Seattle?",
    "extra_body": {"entity_id": "weather_agent"}
  }'
```

## API Mapping

Messages and events from agents/workflows are mapped to OpenAI response types in `agent_framework_devui/_mapper.py`. See the mapping table below:

| Agent Framework Content           | OpenAI Event                              | Type     |
| --------------------------------- | ----------------------------------------- | -------- |
| `TextContent`                     | `ResponseTextDeltaEvent`                  | Official |
| `TextReasoningContent`            | `ResponseReasoningTextDeltaEvent`         | Official |
| `FunctionCallContent`             | `ResponseFunctionCallArgumentsDeltaEvent` | Official |
| `FunctionResultContent`           | `ResponseFunctionResultComplete`          | Custom   |
| `ErrorContent`                    | `ResponseErrorEvent`                      | Official |
| `UsageContent`                    | `ResponseUsageEventComplete`              | Custom   |
| `DataContent`                     | `ResponseTraceEventComplete`              | Custom   |
| `UriContent`                      | `ResponseTraceEventComplete`              | Custom   |
| `HostedFileContent`               | `ResponseTraceEventComplete`              | Custom   |
| `HostedVectorStoreContent`        | `ResponseTraceEventComplete`              | Custom   |
| `FunctionApprovalRequestContent`  | Custom event                              | Custom   |
| `FunctionApprovalResponseContent` | Custom event                              | Custom   |
| `WorkflowEvent`                   | `ResponseWorkflowEventComplete`           | Custom   |

## Frontend Development

To build the frontend:

```bash
cd frontend
yarn install

# Create .env.local with backend URL
echo 'VITE_API_BASE_URL=http://localhost:8000' > .env.local

# Create .env.production (empty for relative URLs)
echo '' > .env.production

# Development
yarn dev

# Build (copies to backend)
yarn build
```

## Troubleshooting

- **Missing API key**: Make sure your `.env` file is in the `python/` directory with valid credentials. Or set environment variables directly in your shell before running DevUI.
- **Import errors**: Run `uv sync --dev` again to ensure all dependencies are installed
- **Port conflicts**: DevUI uses ports 8080 and 8090 by default - close other services using these ports

Let me know if you run into any issues!



================================================
FILE: python/packages/devui/agent_framework_devui/__init__.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Agent Framework DevUI - Debug interface with OpenAI compatible API server."""

import importlib.metadata
import logging
import webbrowser
from typing import Any

from ._server import DevServer
from .models import AgentFrameworkRequest, OpenAIError, OpenAIResponse, ResponseStreamEvent
from .models._discovery_models import DiscoveryResponse, EntityInfo, EnvVarRequirement

logger = logging.getLogger(__name__)

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback for development mode


def serve(
    entities: list[Any] | None = None,
    entities_dir: str | None = None,
    port: int = 8080,
    host: str = "127.0.0.1",
    auto_open: bool = False,
    cors_origins: list[str] | None = None,
    ui_enabled: bool = True,
    tracing_enabled: bool = False,
) -> None:
    """Launch Agent Framework DevUI with simple API.

    Args:
        entities: List of entities for in-memory registration (IDs auto-generated)
        entities_dir: Directory to scan for entities
        port: Port to run server on
        host: Host to bind server to
        auto_open: Whether to automatically open browser
        cors_origins: List of allowed CORS origins
        ui_enabled: Whether to enable the UI
        tracing_enabled: Whether to enable OpenTelemetry tracing
    """
    import re

    import uvicorn

    # Validate host parameter early for security
    if not re.match(r"^(localhost|127\.0\.0\.1|0\.0\.0\.0|[a-zA-Z0-9.-]+)$", host):
        raise ValueError(f"Invalid host: {host}. Must be localhost, IP address, or valid hostname")

    # Validate port parameter
    if not isinstance(port, int) or not (1 <= port <= 65535):
        raise ValueError(f"Invalid port: {port}. Must be integer between 1 and 65535")

    # Configure tracing environment variables if enabled
    if tracing_enabled:
        import os

        # Only set if not already configured by user
        if not os.environ.get("ENABLE_OTEL"):
            os.environ["ENABLE_OTEL"] = "true"
            logger.info("Set ENABLE_OTEL=true for tracing")

        if not os.environ.get("ENABLE_SENSITIVE_DATA"):
            os.environ["ENABLE_SENSITIVE_DATA"] = "true"
            logger.info("Set ENABLE_SENSITIVE_DATA=true for tracing")

        if not os.environ.get("OTLP_ENDPOINT"):
            os.environ["OTLP_ENDPOINT"] = "http://localhost:4317"
            logger.info("Set OTLP_ENDPOINT=http://localhost:4317 for tracing")

    # Create server with direct parameters
    server = DevServer(
        entities_dir=entities_dir, port=port, host=host, cors_origins=cors_origins, ui_enabled=ui_enabled
    )

    # Register in-memory entities if provided
    if entities:
        logger.info(f"Registering {len(entities)} in-memory entities")
        # Store entities for later registration during server startup
        server._pending_entities = entities

    app = server.get_app()

    if auto_open:

        def open_browser() -> None:
            import http.client
            import re
            import time

            # Validate host and port for security
            if not re.match(r"^(localhost|127\.0\.0\.1|0\.0\.0\.0|[a-zA-Z0-9.-]+)$", host):
                logger.warning(f"Invalid host for auto-open: {host}")
                return

            if not isinstance(port, int) or not (1 <= port <= 65535):
                logger.warning(f"Invalid port for auto-open: {port}")
                return

            # Wait for server to be ready by checking health endpoint
            browser_url = f"http://{host}:{port}"

            for _ in range(30):  # 15 second timeout (30 * 0.5s)
                try:
                    # Use http.client for safe connection handling (standard library)
                    conn = http.client.HTTPConnection(host, port, timeout=1)
                    try:
                        conn.request("GET", "/health")
                        response = conn.getresponse()
                        if response.status == 200:
                            webbrowser.open(browser_url)
                            return
                    finally:
                        conn.close()
                except (http.client.HTTPException, OSError, TimeoutError):
                    pass
                time.sleep(0.5)

            # Fallback: open browser anyway after timeout
            webbrowser.open(browser_url)

        import threading

        threading.Thread(target=open_browser, daemon=True).start()

    logger.info(f"Starting Agent Framework DevUI on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


def main() -> None:
    """CLI entry point for devui command."""
    from ._cli import main as cli_main

    cli_main()


# Export main public API
__all__ = [
    "AgentFrameworkRequest",
    "DevServer",
    "DiscoveryResponse",
    "EntityInfo",
    "EnvVarRequirement",
    "OpenAIError",
    "OpenAIResponse",
    "ResponseStreamEvent",
    "main",
    "serve",
]



================================================
FILE: python/packages/devui/agent_framework_devui/_cli.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Command line interface for Agent Framework DevUI."""

import argparse
import logging
import os
import sys

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the server."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(level=getattr(logging, level.upper()), format=log_format, datefmt="%Y-%m-%d %H:%M:%S")


def create_cli_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="devui",
        description="Launch Agent Framework DevUI - Debug interface with OpenAI compatible API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  devui                             # Scan current directory
  devui ./agents                    # Scan specific directory
  devui --port 8000                 # Custom port
  devui --headless                  # API only, no UI
  devui --tracing                   # Enable OpenTelemetry tracing
        """,
    )

    parser.add_argument(
        "directory", nargs="?", default=".", help="Directory to scan for entities (default: current directory)"
    )

    parser.add_argument("--port", "-p", type=int, default=8080, help="Port to run server on (default: 8080)")

    parser.add_argument("--host", default="127.0.0.1", help="Host to bind server to (default: 127.0.0.1)")

    parser.add_argument("--no-open", action="store_true", help="Don't automatically open browser")

    parser.add_argument("--headless", action="store_true", help="Run without UI (API only)")

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    parser.add_argument("--tracing", action="store_true", help="Enable OpenTelemetry tracing for Agent Framework")

    parser.add_argument("--version", action="version", version=f"Agent Framework DevUI {get_version()}")

    return parser


def get_version() -> str:
    """Get the package version."""
    try:
        from . import __version__

        return __version__
    except ImportError:
        return "unknown"


def validate_directory(directory: str) -> str:
    """Validate and normalize the entities directory."""
    if not directory:
        directory = "."

    abs_dir = os.path.abspath(directory)

    if not os.path.exists(abs_dir):
        print(f"❌ Error: Directory '{directory}' does not exist", file=sys.stderr)  # noqa: T201
        sys.exit(1)

    if not os.path.isdir(abs_dir):
        print(f"❌ Error: '{directory}' is not a directory", file=sys.stderr)  # noqa: T201
        sys.exit(1)

    return abs_dir


def print_startup_info(entities_dir: str, host: str, port: int, ui_enabled: bool, reload: bool) -> None:
    """Print startup information."""
    print("🤖 Agent Framework DevUI")  # noqa: T201
    print("=" * 50)  # noqa: T201
    print(f"📁 Entities directory: {entities_dir}")  # noqa: T201
    print(f"🌐 Server URL: http://{host}:{port}")  # noqa: T201
    print(f"🎨 UI enabled: {'Yes' if ui_enabled else 'No'}")  # noqa: T201
    print(f"🔄 Auto-reload: {'Yes' if reload else 'No'}")  # noqa: T201
    print("=" * 50)  # noqa: T201
    print("🔍 Scanning for entities...")  # noqa: T201


def main() -> None:
    """Main CLI entry point."""
    parser = create_cli_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Validate directory
    entities_dir = validate_directory(args.directory)

    # Extract parameters directly from args
    ui_enabled = not args.headless

    # Print startup info
    print_startup_info(entities_dir, args.host, args.port, ui_enabled, args.reload)

    # Import and start server
    try:
        from . import serve

        serve(
            entities_dir=entities_dir,
            port=args.port,
            host=args.host,
            auto_open=not args.no_open,
            ui_enabled=ui_enabled,
            tracing_enabled=args.tracing,
        )

    except KeyboardInterrupt:
        print("\n👋 Shutting down Agent Framework DevUI...")  # noqa: T201
        sys.exit(0)
    except Exception as e:
        logger.exception("Failed to start server")
        print(f"❌ Error: {e}", file=sys.stderr)  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()



================================================
FILE: python/packages/devui/agent_framework_devui/_discovery.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Agent Framework entity discovery implementation."""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import logging
import sys
import uuid
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from .models._discovery_models import EntityInfo

logger = logging.getLogger(__name__)


class EntityDiscovery:
    """Discovery for Agent Framework entities - agents and workflows."""

    def __init__(self, entities_dir: str | None = None):
        """Initialize entity discovery.

        Args:
            entities_dir: Directory to scan for entities (optional)
        """
        self.entities_dir = entities_dir
        self._entities: dict[str, EntityInfo] = {}
        self._loaded_objects: dict[str, Any] = {}
        self._remote_cache_dir = Path.home() / ".agent_framework_devui" / "remote_cache"

    async def discover_entities(self) -> list[EntityInfo]:
        """Scan for Agent Framework entities.

        Returns:
            List of discovered entities
        """
        if not self.entities_dir:
            logger.info("No Agent Framework entities directory configured")
            return []

        entities_dir = Path(self.entities_dir).resolve()  # noqa: ASYNC240
        await self._scan_entities_directory(entities_dir)

        logger.info(f"Discovered {len(self._entities)} Agent Framework entities")
        return self.list_entities()

    def get_entity_info(self, entity_id: str) -> EntityInfo | None:
        """Get entity metadata.

        Args:
            entity_id: Entity identifier

        Returns:
            Entity information or None if not found
        """
        return self._entities.get(entity_id)

    def get_entity_object(self, entity_id: str) -> Any | None:
        """Get the actual loaded entity object.

        Args:
            entity_id: Entity identifier

        Returns:
            Entity object or None if not found
        """
        return self._loaded_objects.get(entity_id)

    def list_entities(self) -> list[EntityInfo]:
        """List all discovered entities.

        Returns:
            List of all entity information
        """
        return list(self._entities.values())

    def register_entity(self, entity_id: str, entity_info: EntityInfo, entity_object: Any) -> None:
        """Register an entity with both metadata and object.

        Args:
            entity_id: Unique entity identifier
            entity_info: Entity metadata
            entity_object: Actual entity object for execution
        """
        self._entities[entity_id] = entity_info
        self._loaded_objects[entity_id] = entity_object
        logger.debug(f"Registered entity: {entity_id} ({entity_info.type})")

    async def create_entity_info_from_object(
        self, entity_object: Any, entity_type: str | None = None, source: str = "in_memory"
    ) -> EntityInfo:
        """Create EntityInfo from Agent Framework entity object.

        Args:
            entity_object: Agent Framework entity object
            entity_type: Optional entity type override
            source: Source of entity (directory, in_memory, remote)

        Returns:
            EntityInfo with Agent Framework specific metadata
        """
        # Determine entity type if not provided
        if entity_type is None:
            entity_type = "agent"
            # Check if it's a workflow
            if hasattr(entity_object, "get_executors_list") or hasattr(entity_object, "executors"):
                entity_type = "workflow"

        # Extract metadata with improved fallback naming
        name = getattr(entity_object, "name", None)
        if not name:
            # In-memory entities: use ID with entity type prefix since no directory name available
            entity_id_raw = getattr(entity_object, "id", None)
            if entity_id_raw:
                # Truncate UUID to first 8 characters for readability
                short_id = str(entity_id_raw)[:8] if len(str(entity_id_raw)) > 8 else str(entity_id_raw)
                name = f"{entity_type.title()} {short_id}"
            else:
                # Fallback to class name with entity type
                class_name = entity_object.__class__.__name__
                name = f"{entity_type.title()} {class_name}"
        description = getattr(entity_object, "description", "")

        # Generate entity ID using Agent Framework specific naming
        entity_id = self._generate_entity_id(entity_object, entity_type, source)

        # Extract tools/executors using Agent Framework specific logic
        tools_list = await self._extract_tools_from_object(entity_object, entity_type)

        # Extract agent-specific fields (for agents only)
        instructions = None
        model = None
        chat_client_type = None
        context_providers_list = None
        middleware_list = None

        if entity_type == "agent":
            # Try to get instructions
            if hasattr(entity_object, "chat_options") and hasattr(entity_object.chat_options, "instructions"):
                instructions = entity_object.chat_options.instructions

            # Try to get model - check both chat_options and chat_client
            if (
                hasattr(entity_object, "chat_options")
                and hasattr(entity_object.chat_options, "model_id")
                and entity_object.chat_options.model_id
            ):
                model = entity_object.chat_options.model_id
            elif hasattr(entity_object, "chat_client") and hasattr(entity_object.chat_client, "model_id"):
                model = entity_object.chat_client.model_id

            # Try to get chat client type
            if hasattr(entity_object, "chat_client"):
                chat_client_type = entity_object.chat_client.__class__.__name__

            # Try to get context providers
            if (
                hasattr(entity_object, "context_provider")
                and entity_object.context_provider
                and hasattr(entity_object.context_provider, "__class__")
            ):
                context_providers_list = [entity_object.context_provider.__class__.__name__]

            # Try to get middleware
            if hasattr(entity_object, "middleware") and entity_object.middleware:
                middleware_list = []
                for m in entity_object.middleware:
                    # Try multiple ways to get a good name for middleware
                    if hasattr(m, "__name__"):  # Function or callable
                        middleware_list.append(m.__name__)
                    elif hasattr(m, "__class__"):  # Class instance
                        middleware_list.append(m.__class__.__name__)
                    else:
                        middleware_list.append(str(m))

        # Create EntityInfo with Agent Framework specifics
        return EntityInfo(
            id=entity_id,
            name=name,
            description=description,
            type=entity_type,
            framework="agent_framework",
            tools=[str(tool) for tool in (tools_list or [])],
            instructions=instructions,
            model=model,
            chat_client_type=chat_client_type,
            context_providers=context_providers_list,
            middleware=middleware_list,
            executors=tools_list if entity_type == "workflow" else [],
            input_schema={"type": "string"},  # Default schema
            start_executor_id=tools_list[0] if tools_list and entity_type == "workflow" else None,
            metadata={
                "source": "agent_framework_object",
                "class_name": entity_object.__class__.__name__
                if hasattr(entity_object, "__class__")
                else str(type(entity_object)),
                "has_run_stream": hasattr(entity_object, "run_stream"),
            },
        )

    async def _scan_entities_directory(self, entities_dir: Path) -> None:
        """Scan the entities directory for Agent Framework entities.

        Args:
            entities_dir: Directory to scan for entities
        """
        if not entities_dir.exists():  # noqa: ASYNC240
            logger.warning(f"Entities directory not found: {entities_dir}")
            return

        logger.info(f"Scanning {entities_dir} for Agent Framework entities...")

        # Add entities directory to Python path if not already there
        entities_dir_str = str(entities_dir)
        if entities_dir_str not in sys.path:
            sys.path.insert(0, entities_dir_str)

        # Scan for directories and Python files
        for item in entities_dir.iterdir():  # noqa: ASYNC240
            if item.name.startswith(".") or item.name == "__pycache__":
                continue

            if item.is_dir():
                # Directory-based entity
                await self._discover_entities_in_directory(item)
            elif item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
                # Single file entity
                await self._discover_entities_in_file(item)

    async def _discover_entities_in_directory(self, dir_path: Path) -> None:
        """Discover entities in a directory using module import.

        Args:
            dir_path: Directory containing entity
        """
        entity_id = dir_path.name
        logger.debug(f"Scanning directory: {entity_id}")

        try:
            # Load environment variables for this entity first
            self._load_env_for_entity(dir_path)

            # Try different import patterns
            import_patterns = [
                entity_id,  # Direct module import
                f"{entity_id}.agent",  # agent.py submodule
                f"{entity_id}.workflow",  # workflow.py submodule
            ]

            for pattern in import_patterns:
                module = self._load_module_from_pattern(pattern)
                if module:
                    entities_found = await self._find_entities_in_module(module, entity_id, str(dir_path))
                    if entities_found:
                        logger.debug(f"Found {len(entities_found)} entities in {pattern}")
                        break

        except Exception as e:
            logger.warning(f"Error scanning directory {entity_id}: {e}")

    async def _discover_entities_in_file(self, file_path: Path) -> None:
        """Discover entities in a single Python file.

        Args:
            file_path: Python file to scan
        """
        try:
            # Load environment variables for this entity's directory first
            self._load_env_for_entity(file_path.parent)

            # Create module name from file path
            base_name = file_path.stem

            # Load the module directly from file
            module = self._load_module_from_file(file_path, base_name)
            if module:
                entities_found = await self._find_entities_in_module(module, base_name, str(file_path))
                if entities_found:
                    logger.debug(f"Found {len(entities_found)} entities in {file_path.name}")

        except Exception as e:
            logger.warning(f"Error scanning file {file_path}: {e}")

    def _load_env_for_entity(self, entity_path: Path) -> bool:
        """Load .env file for an entity.

        Args:
            entity_path: Path to entity directory

        Returns:
            True if .env was loaded successfully
        """
        # Check for .env in the entity folder first
        env_file = entity_path / ".env"
        if self._load_env_file(env_file):
            return True

        # Check one level up (the entities directory) for safety
        if self.entities_dir:
            entities_dir = Path(self.entities_dir).resolve()
            entities_env = entities_dir / ".env"
            if self._load_env_file(entities_env):
                return True

        return False

    def _load_env_file(self, env_path: Path) -> bool:
        """Load environment variables from .env file.

        Args:
            env_path: Path to .env file

        Returns:
            True if file was loaded successfully
        """
        if env_path.exists():
            load_dotenv(env_path, override=True)
            logger.debug(f"Loaded .env from {env_path}")
            return True
        return False

    def _load_module_from_pattern(self, pattern: str) -> Any | None:
        """Load module using import pattern.

        Args:
            pattern: Import pattern to try

        Returns:
            Loaded module or None if failed
        """
        try:
            # Check if module exists first
            spec = importlib.util.find_spec(pattern)
            if spec is None:
                return None

            module = importlib.import_module(pattern)
            logger.debug(f"Successfully imported {pattern}")
            return module

        except ModuleNotFoundError:
            logger.debug(f"Import pattern {pattern} not found")
            return None
        except Exception as e:
            logger.warning(f"Error importing {pattern}: {e}")
            return None

    def _load_module_from_file(self, file_path: Path, module_name: str) -> Any | None:
        """Load module directly from file path.

        Args:
            file_path: Path to Python file
            module_name: Name to assign to module

        Returns:
            Loaded module or None if failed
        """
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module  # Add to sys.modules for proper imports
            spec.loader.exec_module(module)

            logger.debug(f"Successfully loaded module from {file_path}")
            return module

        except Exception as e:
            logger.warning(f"Error loading module from {file_path}: {e}")
            return None

    async def _find_entities_in_module(self, module: Any, base_id: str, module_path: str) -> list[str]:
        """Find agent and workflow entities in a loaded module.

        Args:
            module: Loaded Python module
            base_id: Base identifier for entities
            module_path: Path to module for metadata

        Returns:
            List of entity IDs that were found and registered
        """
        entities_found = []

        # Look for explicit variable names first
        candidates = [
            ("agent", getattr(module, "agent", None)),
            ("workflow", getattr(module, "workflow", None)),
        ]

        for obj_type, obj in candidates:
            if obj is None:
                continue

            if self._is_valid_entity(obj, obj_type):
                # Pass source as "directory" for directory-discovered entities
                await self._register_entity_from_object(obj, obj_type, module_path, source="directory")
                entities_found.append(obj_type)

        return entities_found

    def _is_valid_entity(self, obj: Any, expected_type: str) -> bool:
        """Check if object is a valid agent or workflow using duck typing.

        Args:
            obj: Object to validate
            expected_type: Expected type ("agent" or "workflow")

        Returns:
            True if object is valid for the expected type
        """
        if expected_type == "agent":
            return self._is_valid_agent(obj)
        if expected_type == "workflow":
            return self._is_valid_workflow(obj)
        return False

    def _is_valid_agent(self, obj: Any) -> bool:
        """Check if object is a valid Agent Framework agent.

        Args:
            obj: Object to validate

        Returns:
            True if object appears to be a valid agent
        """
        try:
            # Try to import AgentProtocol for proper type checking
            try:
                from agent_framework import AgentProtocol

                if isinstance(obj, AgentProtocol):
                    return True
            except ImportError:
                pass

            # Fallback to duck typing for agent protocol
            if hasattr(obj, "run_stream") and hasattr(obj, "id") and hasattr(obj, "name"):
                return True

        except (TypeError, AttributeError):
            pass

        return False

    def _is_valid_workflow(self, obj: Any) -> bool:
        """Check if object is a valid Agent Framework workflow.

        Args:
            obj: Object to validate

        Returns:
            True if object appears to be a valid workflow
        """
        # Check for workflow - must have run_stream method and executors
        return hasattr(obj, "run_stream") and (hasattr(obj, "executors") or hasattr(obj, "get_executors_list"))

    async def _register_entity_from_object(
        self, obj: Any, obj_type: str, module_path: str, source: str = "directory"
    ) -> None:
        """Register an entity from a live object.

        Args:
            obj: Entity object
            obj_type: Type of entity ("agent" or "workflow")
            module_path: Path to module for metadata
            source: Source of entity (directory, in_memory, remote)
        """
        try:
            # Generate entity ID with source information
            entity_id = self._generate_entity_id(obj, obj_type, source)

            # Extract metadata from the live object with improved fallback naming
            name = getattr(obj, "name", None)
            if not name:
                entity_id_raw = getattr(obj, "id", None)
                if entity_id_raw:
                    # Truncate UUID to first 8 characters for readability
                    short_id = str(entity_id_raw)[:8] if len(str(entity_id_raw)) > 8 else str(entity_id_raw)
                    name = f"{obj_type.title()} {short_id}"
                else:
                    name = f"{obj_type.title()} {obj.__class__.__name__}"
            description = getattr(obj, "description", None)
            tools = await self._extract_tools_from_object(obj, obj_type)

            # Create EntityInfo
            tools_union: list[str | dict[str, Any]] | None = None
            if tools:
                tools_union = [tool for tool in tools]

            # Extract agent-specific fields (for agents only)
            instructions = None
            model = None
            chat_client_type = None
            context_providers_list = None
            middleware_list = None

            if obj_type == "agent":
                # Try to get instructions
                if hasattr(obj, "chat_options") and hasattr(obj.chat_options, "instructions"):
                    instructions = obj.chat_options.instructions

                # Try to get model - check both chat_options and chat_client
                if hasattr(obj, "chat_options") and hasattr(obj.chat_options, "model_id") and obj.chat_options.model_id:
                    model = obj.chat_options.model_id
                elif hasattr(obj, "chat_client") and hasattr(obj.chat_client, "model_id"):
                    model = obj.chat_client.model_id

                # Try to get chat client type
                if hasattr(obj, "chat_client"):
                    chat_client_type = obj.chat_client.__class__.__name__

                # Try to get context providers
                if (
                    hasattr(obj, "context_provider")
                    and obj.context_provider
                    and hasattr(obj.context_provider, "__class__")
                ):
                    context_providers_list = [obj.context_provider.__class__.__name__]

                # Try to get middleware
                if hasattr(obj, "middleware") and obj.middleware:
                    middleware_list = []
                    for m in obj.middleware:
                        # Try multiple ways to get a good name for middleware
                        if hasattr(m, "__name__"):  # Function or callable
                            middleware_list.append(m.__name__)
                        elif hasattr(m, "__class__"):  # Class instance
                            middleware_list.append(m.__class__.__name__)
                        else:
                            middleware_list.append(str(m))

            entity_info = EntityInfo(
                id=entity_id,
                type=obj_type,
                name=name,
                framework="agent_framework",
                description=description,
                tools=tools_union,
                instructions=instructions,
                model=model,
                chat_client_type=chat_client_type,
                context_providers=context_providers_list,
                middleware=middleware_list,
                metadata={
                    "module_path": module_path,
                    "entity_type": obj_type,
                    "source": source,
                    "has_run_stream": hasattr(obj, "run_stream"),
                    "class_name": obj.__class__.__name__ if hasattr(obj, "__class__") else str(type(obj)),
                },
            )

            # Register the entity
            self.register_entity(entity_id, entity_info, obj)

        except Exception as e:
            logger.error(f"Error registering entity from {source}: {e}")

    async def _extract_tools_from_object(self, obj: Any, obj_type: str) -> list[str]:
        """Extract tool/executor names from a live object.

        Args:
            obj: Entity object
            obj_type: Type of entity

        Returns:
            List of tool/executor names
        """
        tools = []

        try:
            if obj_type == "agent":
                # For agents, check chat_options.tools first
                chat_options = getattr(obj, "chat_options", None)
                if chat_options and hasattr(chat_options, "tools"):
                    for tool in chat_options.tools:
                        if hasattr(tool, "__name__"):
                            tools.append(tool.__name__)
                        elif hasattr(tool, "name"):
                            tools.append(tool.name)
                        else:
                            tools.append(str(tool))
                else:
                    # Fallback to direct tools attribute
                    agent_tools = getattr(obj, "tools", None)
                    if agent_tools:
                        for tool in agent_tools:
                            if hasattr(tool, "__name__"):
                                tools.append(tool.__name__)
                            elif hasattr(tool, "name"):
                                tools.append(tool.name)
                            else:
                                tools.append(str(tool))

            elif obj_type == "workflow":
                # For workflows, extract executor names
                if hasattr(obj, "get_executors_list"):
                    executor_objects = obj.get_executors_list()
                    tools = [getattr(ex, "id", str(ex)) for ex in executor_objects]
                elif hasattr(obj, "executors"):
                    executors = obj.executors
                    if isinstance(executors, list):
                        tools = [getattr(ex, "id", str(ex)) for ex in executors]
                    elif isinstance(executors, dict):
                        tools = list(executors.keys())

        except Exception as e:
            logger.debug(f"Error extracting tools from {obj_type} {type(obj)}: {e}")

        return tools

    def _generate_entity_id(self, entity: Any, entity_type: str, source: str = "directory") -> str:
        """Generate unique entity ID with UUID suffix for collision resistance.

        Args:
            entity: Entity object
            entity_type: Type of entity (agent, workflow, etc.)
            source: Source of entity (directory, in_memory, remote)

        Returns:
            Unique entity ID with format: {type}_{source}_{name}_{uuid8}
        """
        import re

        # Extract base name with priority: name -> id -> class_name
        if hasattr(entity, "name") and entity.name:
            base_name = str(entity.name).lower().replace(" ", "-").replace("_", "-")
        elif hasattr(entity, "id") and entity.id:
            base_name = str(entity.id).lower().replace(" ", "-").replace("_", "-")
        elif hasattr(entity, "__class__"):
            class_name = entity.__class__.__name__
            # Convert CamelCase to kebab-case
            base_name = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", class_name).lower()
        else:
            base_name = "entity"

        # Generate short UUID (8 chars = 4 billion combinations)
        short_uuid = uuid.uuid4().hex[:8]

        return f"{entity_type}_{source}_{base_name}_{short_uuid}"

    async def fetch_remote_entity(
        self, url: str, metadata: dict[str, Any] | None = None
    ) -> tuple[EntityInfo | None, str | None]:
        """Fetch and register entity from URL.

        Args:
            url: URL to Python file containing entity
            metadata: Additional metadata (source, sampleId, etc.)

        Returns:
            Tuple of (EntityInfo if successful, error_message if failed)
        """
        try:
            normalized_url = self._normalize_url(url)
            logger.info(f"Normalized URL: {normalized_url}")

            content = await self._fetch_url_content(normalized_url)
            if not content:
                error_msg = "Failed to fetch content from URL. The file may not exist or is not accessible."
                logger.warning(error_msg)
                return None, error_msg

            if not self._validate_python_syntax(content):
                error_msg = "Invalid Python syntax in the file. Please check the file contains valid Python code."
                logger.warning(error_msg)
                return None, error_msg

            entity_object = await self._load_entity_from_content(content, url)
            if not entity_object:
                error_msg = (
                    "No valid agent or workflow found in the file. "
                    "Make sure the file contains an 'agent' or 'workflow' variable."
                )
                logger.warning(error_msg)
                return None, error_msg

            entity_info = await self.create_entity_info_from_object(
                entity_object,
                entity_type=None,  # Auto-detect
                source="remote",
            )

            entity_info.source = metadata.get("source", "remote_gallery") if metadata else "remote_gallery"
            entity_info.original_url = url
            if metadata:
                entity_info.metadata.update(metadata)

            self.register_entity(entity_info.id, entity_info, entity_object)

            logger.info(f"Successfully added remote entity: {entity_info.id}")
            return entity_info, None

        except Exception as e:
            error_msg = f"Unexpected error: {e!s}"
            logger.error(f"Error fetching remote entity from {url}: {e}", exc_info=True)
            return None, error_msg

    def _normalize_url(self, url: str) -> str:
        """Convert various Git hosting URLs to raw content URLs."""
        # GitHub: blob -> raw
        if "github.com" in url and "/blob/" in url:
            return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        # GitLab: blob -> raw
        if "gitlab.com" in url and "/-/blob/" in url:
            return url.replace("/-/blob/", "/-/raw/")

        # Bitbucket: src -> raw
        if "bitbucket.org" in url and "/src/" in url:
            return url.replace("/src/", "/raw/")

        return url

    async def _fetch_url_content(self, url: str, max_size_mb: int = 10) -> str | None:
        """Fetch content from URL with size and timeout limits."""
        try:
            timeout = 30.0  # 30 second timeout

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)

                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    return None

                # Check content length
                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > max_size_mb * 1024 * 1024:
                    logger.warning(f"File too large: {content_length} bytes")
                    return None

                # Read with size limit
                content = response.text
                if len(content.encode("utf-8")) > max_size_mb * 1024 * 1024:
                    logger.warning("Content too large after reading")
                    return None

                return content

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _validate_python_syntax(self, content: str) -> bool:
        """Validate that content is valid Python code."""
        try:
            compile(content, "<remote>", "exec")
            return True
        except SyntaxError as e:
            logger.warning(f"Python syntax error: {e}")
            return False

    async def _load_entity_from_content(self, content: str, source_url: str) -> Any | None:
        """Load entity object from Python content string using disk-based import.

        This method caches remote entities to disk and uses importlib for loading,
        making it consistent with local entity discovery and avoiding exec() security warnings.
        """
        try:
            # Create cache directory if it doesn't exist
            self._remote_cache_dir.mkdir(parents=True, exist_ok=True)

            # Generate a unique filename based on URL hash
            url_hash = hashlib.sha256(source_url.encode()).hexdigest()[:16]
            module_name = f"remote_entity_{url_hash}"
            cached_file = self._remote_cache_dir / f"{module_name}.py"

            # Write content to cache file
            cached_file.write_text(content, encoding="utf-8")
            logger.debug(f"Cached remote entity to {cached_file}")

            # Load module from cached file using importlib (same as local scanning)
            module = self._load_module_from_file(cached_file, module_name)
            if not module:
                logger.warning(f"Failed to load module from cached file: {cached_file}")
                return None

            # Look for agent or workflow objects in the loaded module
            for name in dir(module):
                if name.startswith("_"):
                    continue

                obj = getattr(module, name)

                # Check for explicitly named entities first
                if name in ["agent", "workflow"] and self._is_valid_entity(obj, name):
                    return obj

                # Also check if any object looks like an agent/workflow
                if self._is_valid_agent(obj) or self._is_valid_workflow(obj):
                    return obj

            return None

        except Exception as e:
            logger.error(f"Error loading entity from content: {e}")
            return None

    def remove_remote_entity(self, entity_id: str) -> bool:
        """Remove a remote entity by ID."""
        if entity_id in self._entities:
            entity_info = self._entities[entity_id]
            if entity_info.source in ["remote_gallery", "remote"]:
                del self._entities[entity_id]
                if entity_id in self._loaded_objects:
                    del self._loaded_objects[entity_id]
                logger.info(f"Removed remote entity: {entity_id}")
                return True
            logger.warning(f"Cannot remove local entity: {entity_id}")
            return False
        return False



================================================
FILE: python/packages/devui/agent_framework_devui/_executor.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Agent Framework executor implementation."""

import json
import logging
import os
import uuid
from collections.abc import AsyncGenerator
from typing import Any, get_origin

from agent_framework import AgentThread

from ._discovery import EntityDiscovery
from ._mapper import MessageMapper
from ._tracing import capture_traces
from .models import AgentFrameworkRequest, OpenAIResponse
from .models._discovery_models import EntityInfo

logger = logging.getLogger(__name__)


class EntityNotFoundError(Exception):
    """Raised when an entity is not found."""

    pass


class AgentFrameworkExecutor:
    """Executor for Agent Framework entities - agents and workflows."""

    def __init__(self, entity_discovery: EntityDiscovery, message_mapper: MessageMapper):
        """Initialize Agent Framework executor.

        Args:
            entity_discovery: Entity discovery instance
            message_mapper: Message mapper instance
        """
        self.entity_discovery = entity_discovery
        self.message_mapper = message_mapper
        self._setup_tracing_provider()
        self._setup_agent_framework_tracing()

        # Minimal thread storage - no metadata needed
        self.thread_storage: dict[str, AgentThread] = {}
        self.agent_threads: dict[str, list[str]] = {}  # agent_id -> thread_ids

    def _setup_tracing_provider(self) -> None:
        """Set up our own TracerProvider so we can add processors."""
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider

            # Only set up if no provider exists yet
            if not hasattr(trace, "_TRACER_PROVIDER") or trace._TRACER_PROVIDER is None:
                resource = Resource.create({
                    "service.name": "agent-framework-server",
                    "service.version": "1.0.0",
                })
                provider = TracerProvider(resource=resource)
                trace.set_tracer_provider(provider)
                logger.info("Set up TracerProvider for server tracing")
            else:
                logger.debug("TracerProvider already exists")

        except ImportError:
            logger.debug("OpenTelemetry not available")
        except Exception as e:
            logger.warning(f"Failed to setup TracerProvider: {e}")

    def _setup_agent_framework_tracing(self) -> None:
        """Set up Agent Framework's built-in tracing."""
        # Configure Agent Framework tracing only if ENABLE_OTEL is set
        if os.environ.get("ENABLE_OTEL"):
            try:
                from agent_framework.observability import setup_observability

                setup_observability(enable_sensitive_data=True)
                logger.info("Enabled Agent Framework observability")
            except Exception as e:
                logger.warning(f"Failed to enable Agent Framework observability: {e}")
        else:
            logger.debug("ENABLE_OTEL not set, skipping observability setup")

    # Thread Management Methods
    def create_thread(self, agent_id: str) -> str:
        """Create new thread for agent."""
        thread_id = f"thread_{uuid.uuid4().hex[:8]}"
        thread = AgentThread()

        self.thread_storage[thread_id] = thread

        if agent_id not in self.agent_threads:
            self.agent_threads[agent_id] = []
        self.agent_threads[agent_id].append(thread_id)

        return thread_id

    def get_thread(self, thread_id: str) -> AgentThread | None:
        """Get AgentThread by ID."""
        return self.thread_storage.get(thread_id)

    def list_threads_for_agent(self, agent_id: str) -> list[str]:
        """List thread IDs for agent."""
        return self.agent_threads.get(agent_id, [])

    def get_agent_for_thread(self, thread_id: str) -> str | None:
        """Find which agent owns this thread."""
        for agent_id, thread_ids in self.agent_threads.items():
            if thread_id in thread_ids:
                return agent_id
        return None

    def delete_thread(self, thread_id: str) -> bool:
        """Delete thread."""
        if thread_id not in self.thread_storage:
            return False

        for _agent_id, thread_ids in self.agent_threads.items():
            if thread_id in thread_ids:
                thread_ids.remove(thread_id)
                break

        del self.thread_storage[thread_id]
        return True

    async def get_thread_messages(self, thread_id: str) -> list[dict[str, Any]]:
        """Get messages from a thread's message store, preserving all content types for UI display."""
        thread = self.get_thread(thread_id)
        if not thread or not thread.message_store:
            return []

        try:
            # Get AgentFramework ChatMessage objects from thread
            af_messages = await thread.message_store.list_messages()

            ui_messages = []
            for i, af_msg in enumerate(af_messages):
                # Extract role value (handle enum)
                role = af_msg.role.value if hasattr(af_msg.role, "value") else str(af_msg.role)

                # Skip tool/function messages - only show user and assistant messages
                if role not in ["user", "assistant"]:
                    continue

                # Extract all user-facing content (text, images, files, etc.)
                display_contents = self._extract_display_contents(af_msg.contents)

                # Skip messages with no displayable content
                if not display_contents:
                    continue

                # Extract usage information if present
                usage_data = None
                for content in af_msg.contents:
                    content_type = getattr(content, "type", None)
                    if content_type == "usage":
                        details = getattr(content, "details", None)
                        if details:
                            usage_data = {
                                "total_tokens": getattr(details, "total_token_count", 0) or 0,
                                "prompt_tokens": getattr(details, "input_token_count", 0) or 0,
                                "completion_tokens": getattr(details, "output_token_count", 0) or 0,
                            }
                        break

                ui_message = {
                    "id": af_msg.message_id or f"restored-{i}",
                    "role": role,
                    "contents": display_contents,
                    "timestamp": __import__("datetime").datetime.now().isoformat(),
                    "author_name": af_msg.author_name,
                    "message_id": af_msg.message_id,
                }

                # Add usage data if available
                if usage_data:
                    ui_message["usage"] = usage_data

                ui_messages.append(ui_message)

            logger.info(f"Restored {len(ui_messages)} display messages for thread {thread_id}")
            return ui_messages

        except Exception as e:
            logger.error(f"Error getting thread messages: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return []

    def _extract_display_contents(self, contents: list[Any]) -> list[dict[str, Any]]:
        """Extract all user-facing content (text, images, files, etc.) from message contents.

        Filters out internal mechanics like function calls/results while preserving
        all content types that should be displayed in the UI.
        """
        display_contents = []

        for content in contents:
            content_type = getattr(content, "type", None)

            # Text content
            if content_type == "text":
                text = getattr(content, "text", "")

                # Handle double-encoded JSON from user messages
                if text.startswith('{"role":'):
                    try:
                        import json

                        parsed = json.loads(text)
                        if parsed.get("contents"):
                            for sub_content in parsed["contents"]:
                                if sub_content.get("type") == "text":
                                    display_contents.append({"type": "text", "text": sub_content.get("text", "")})
                    except Exception:
                        display_contents.append({"type": "text", "text": text})
                else:
                    display_contents.append({"type": "text", "text": text})

            # Data content (images, files, PDFs, etc.)
            elif content_type == "data":
                display_contents.append({
                    "type": "data",
                    "uri": getattr(content, "uri", ""),
                    "media_type": getattr(content, "media_type", None),
                })

            # URI content (external links to images/files)
            elif content_type == "uri":
                display_contents.append({
                    "type": "uri",
                    "uri": getattr(content, "uri", ""),
                    "media_type": getattr(content, "media_type", None),
                })

            # Skip function_call, function_result, and other internal content types

        return display_contents

    async def serialize_thread(self, thread_id: str) -> dict[str, Any] | None:
        """Serialize thread state for persistence."""
        thread = self.get_thread(thread_id)
        if not thread:
            return None

        try:
            # Use AgentThread's built-in serialization
            serialized_state = await thread.serialize()

            # Add our metadata
            agent_id = self.get_agent_for_thread(thread_id)
            serialized_state["metadata"] = {"agent_id": agent_id, "thread_id": thread_id}

            return serialized_state

        except Exception as e:
            logger.error(f"Error serializing thread {thread_id}: {e}")
            return None

    async def deserialize_thread(self, thread_id: str, agent_id: str, serialized_state: dict[str, Any]) -> bool:
        """Deserialize thread state from persistence."""
        try:
            thread = await AgentThread.deserialize(serialized_state)
            # Store the restored thread
            self.thread_storage[thread_id] = thread
            if agent_id not in self.agent_threads:
                self.agent_threads[agent_id] = []
            self.agent_threads[agent_id].append(thread_id)

            return True

        except Exception as e:
            logger.error(f"Error deserializing thread {thread_id}: {e}")
            return False

    async def discover_entities(self) -> list[EntityInfo]:
        """Discover all available entities.

        Returns:
            List of discovered entities
        """
        return await self.entity_discovery.discover_entities()

    def get_entity_info(self, entity_id: str) -> EntityInfo:
        """Get entity information.

        Args:
            entity_id: Entity identifier

        Returns:
            Entity information

        Raises:
            EntityNotFoundError: If entity is not found
        """
        entity_info = self.entity_discovery.get_entity_info(entity_id)
        if entity_info is None:
            raise EntityNotFoundError(f"Entity '{entity_id}' not found")
        return entity_info

    async def execute_streaming(self, request: AgentFrameworkRequest) -> AsyncGenerator[Any, None]:
        """Execute request and stream results in OpenAI format.

        Args:
            request: Request to execute

        Yields:
            OpenAI response stream events
        """
        try:
            entity_id = request.get_entity_id()
            if not entity_id:
                logger.error("No entity_id specified in request")
                return

            # Validate entity exists
            if not self.entity_discovery.get_entity_info(entity_id):
                logger.error(f"Entity '{entity_id}' not found")
                return

            # Execute entity and convert events
            async for raw_event in self.execute_entity(entity_id, request):
                openai_events = await self.message_mapper.convert_event(raw_event, request)
                for event in openai_events:
                    yield event

        except Exception as e:
            logger.exception(f"Error in streaming execution: {e}")
            # Could yield error event here

    async def execute_sync(self, request: AgentFrameworkRequest) -> OpenAIResponse:
        """Execute request synchronously and return complete response.

        Args:
            request: Request to execute

        Returns:
            Final aggregated OpenAI response
        """
        # Collect all streaming events
        events = [event async for event in self.execute_streaming(request)]

        # Aggregate into final response
        return await self.message_mapper.aggregate_to_response(events, request)

    async def execute_entity(self, entity_id: str, request: AgentFrameworkRequest) -> AsyncGenerator[Any, None]:
        """Execute the entity and yield raw Agent Framework events plus trace events.

        Args:
            entity_id: ID of entity to execute
            request: Request to execute

        Yields:
            Raw Agent Framework events and trace events
        """
        try:
            # Get entity info and object
            entity_info = self.get_entity_info(entity_id)
            entity_obj = self.entity_discovery.get_entity_object(entity_id)

            if not entity_obj:
                raise EntityNotFoundError(f"Entity object for '{entity_id}' not found")

            logger.info(f"Executing {entity_info.type}: {entity_id}")

            # Extract session_id from request for trace context
            session_id = getattr(request.extra_body, "session_id", None) if request.extra_body else None

            # Use simplified trace capture
            with capture_traces(session_id=session_id, entity_id=entity_id) as trace_collector:
                if entity_info.type == "agent":
                    async for event in self._execute_agent(entity_obj, request, trace_collector):
                        yield event
                elif entity_info.type == "workflow":
                    async for event in self._execute_workflow(entity_obj, request, trace_collector):
                        yield event
                else:
                    raise ValueError(f"Unsupported entity type: {entity_info.type}")

                # Yield any remaining trace events after execution completes
                for trace_event in trace_collector.get_pending_events():
                    yield trace_event

        except Exception as e:
            logger.exception(f"Error executing entity {entity_id}: {e}")
            # Yield error event
            yield {"type": "error", "message": str(e), "entity_id": entity_id}

    async def _execute_agent(
        self, agent: Any, request: AgentFrameworkRequest, trace_collector: Any
    ) -> AsyncGenerator[Any, None]:
        """Execute Agent Framework agent with trace collection and optional thread support.

        Args:
            agent: Agent object to execute
            request: Request to execute
            trace_collector: Trace collector to get events from

        Yields:
            Agent update events and trace events
        """
        try:
            # Convert input to proper ChatMessage or string
            user_message = self._convert_input_to_chat_message(request.input)

            # Get thread if provided in extra_body
            thread = None
            if request.extra_body and hasattr(request.extra_body, "thread_id") and request.extra_body.thread_id:
                thread_id = request.extra_body.thread_id
                thread = self.get_thread(thread_id)
                if thread:
                    logger.debug(f"Using existing thread: {thread_id}")
                else:
                    logger.warning(f"Thread {thread_id} not found, proceeding without thread")

            if isinstance(user_message, str):
                logger.debug(f"Executing agent with text input: {user_message[:100]}...")
            else:
                logger.debug(f"Executing agent with multimodal ChatMessage: {type(user_message)}")

            # Use Agent Framework's native streaming with optional thread
            if thread:
                async for update in agent.run_stream(user_message, thread=thread):
                    for trace_event in trace_collector.get_pending_events():
                        yield trace_event

                    yield update
            else:
                async for update in agent.run_stream(user_message):
                    for trace_event in trace_collector.get_pending_events():
                        yield trace_event

                    yield update

        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            yield {"type": "error", "message": f"Agent execution error: {e!s}"}

    async def _execute_workflow(
        self, workflow: Any, request: AgentFrameworkRequest, trace_collector: Any
    ) -> AsyncGenerator[Any, None]:
        """Execute Agent Framework workflow with trace collection.

        Args:
            workflow: Workflow object to execute
            request: Request to execute
            trace_collector: Trace collector to get events from

        Yields:
            Workflow events and trace events
        """
        try:
            # Get input data - prefer structured data from extra_body
            input_data: str | list[Any] | dict[str, Any]
            if request.extra_body and hasattr(request.extra_body, "input_data") and request.extra_body.input_data:
                input_data = request.extra_body.input_data
                logger.debug(f"Using structured input_data from extra_body: {type(input_data)}")
            else:
                input_data = request.input
                logger.debug(f"Using input field as fallback: {type(input_data)}")

            # Parse input based on workflow's expected input type
            parsed_input = await self._parse_workflow_input(workflow, input_data)

            logger.debug(f"Executing workflow with parsed input type: {type(parsed_input)}")

            # Use Agent Framework workflow's native streaming
            async for event in workflow.run_stream(parsed_input):
                # Yield any pending trace events first
                for trace_event in trace_collector.get_pending_events():
                    yield trace_event

                # Then yield the workflow event
                yield event

        except Exception as e:
            logger.error(f"Error in workflow execution: {e}")
            yield {"type": "error", "message": f"Workflow execution error: {e!s}"}

    def _convert_input_to_chat_message(self, input_data: Any) -> Any:
        """Convert OpenAI Responses API input to Agent Framework ChatMessage or string.

        Args:
            input_data: OpenAI ResponseInputParam (List[ResponseInputItemParam])

        Returns:
            ChatMessage for multimodal content, or string for simple text
        """
        # Import Agent Framework types
        try:
            from agent_framework import ChatMessage, DataContent, Role, TextContent
        except ImportError:
            # Fallback to string extraction if Agent Framework not available
            return self._extract_user_message_fallback(input_data)

        # Handle simple string input (backward compatibility)
        if isinstance(input_data, str):
            return input_data

        # Handle OpenAI ResponseInputParam (List[ResponseInputItemParam])
        if isinstance(input_data, list):
            return self._convert_openai_input_to_chat_message(input_data, ChatMessage, TextContent, DataContent, Role)

        # Fallback for other formats
        return self._extract_user_message_fallback(input_data)

    def _convert_openai_input_to_chat_message(
        self, input_items: list[Any], ChatMessage: Any, TextContent: Any, DataContent: Any, Role: Any
    ) -> Any:
        """Convert OpenAI ResponseInputParam to Agent Framework ChatMessage.

        Args:
            input_items: List of OpenAI ResponseInputItemParam objects (dicts or objects)
            ChatMessage: ChatMessage class for creating chat messages
            TextContent: TextContent class for text content
            DataContent: DataContent class for data/media content
            Role: Role enum for message roles

        Returns:
            ChatMessage with converted content
        """
        contents = []

        # Process each input item
        for item in input_items:
            # Handle dict format (from JSON)
            if isinstance(item, dict):
                item_type = item.get("type")
                if item_type == "message":
                    # Extract content from OpenAI message
                    message_content = item.get("content", [])

                    # Handle both string content and list content
                    if isinstance(message_content, str):
                        contents.append(TextContent(text=message_content))
                    elif isinstance(message_content, list):
                        for content_item in message_content:
                            # Handle dict content items
                            if isinstance(content_item, dict):
                                content_type = content_item.get("type")

                                if content_type == "input_text":
                                    text = content_item.get("text", "")
                                    contents.append(TextContent(text=text))

                                elif content_type == "input_image":
                                    image_url = content_item.get("image_url", "")
                                    if image_url:
                                        # Extract media type from data URI if possible
                                        # Parse media type from data URL, fallback to image/png
                                        if image_url.startswith("data:"):
                                            try:
                                                # Extract media type from data:image/jpeg;base64,... format
                                                media_type = image_url.split(";")[0].split(":")[1]
                                            except (IndexError, AttributeError):
                                                logger.warning(
                                                    f"Failed to parse media type from data URL: {image_url[:30]}..."
                                                )
                                                media_type = "image/png"
                                        else:
                                            media_type = "image/png"
                                        contents.append(DataContent(uri=image_url, media_type=media_type))

                                elif content_type == "input_file":
                                    # Handle file input
                                    file_data = content_item.get("file_data")
                                    file_url = content_item.get("file_url")
                                    filename = content_item.get("filename", "")

                                    # Determine media type from filename
                                    media_type = "application/octet-stream"  # default
                                    if filename:
                                        if filename.lower().endswith(".pdf"):
                                            media_type = "application/pdf"
                                        elif filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                                            media_type = f"image/{filename.split('.')[-1].lower()}"
                                        elif filename.lower().endswith((
                                            ".wav",
                                            ".mp3",
                                            ".m4a",
                                            ".ogg",
                                            ".flac",
                                            ".aac",
                                        )):
                                            ext = filename.split(".")[-1].lower()
                                            # Normalize extensions to match audio MIME types
                                            media_type = "audio/mp4" if ext == "m4a" else f"audio/{ext}"

                                    # Use file_data or file_url
                                    if file_data:
                                        # Assume file_data is base64, create data URI
                                        data_uri = f"data:{media_type};base64,{file_data}"
                                        contents.append(DataContent(uri=data_uri, media_type=media_type))
                                    elif file_url:
                                        contents.append(DataContent(uri=file_url, media_type=media_type))

            # Handle other OpenAI input item types as needed
            # (tool calls, function results, etc.)

        # If no contents found, create a simple text message
        if not contents:
            contents.append(TextContent(text=""))

        chat_message = ChatMessage(role=Role.USER, contents=contents)

        logger.info(f"Created ChatMessage with {len(contents)} contents:")
        for idx, content in enumerate(contents):
            content_type = content.__class__.__name__
            if hasattr(content, "media_type"):
                logger.info(f"  [{idx}] {content_type} - media_type: {content.media_type}")
            else:
                logger.info(f"  [{idx}] {content_type}")

        return chat_message

    def _extract_user_message_fallback(self, input_data: Any) -> str:
        """Fallback method to extract user message as string.

        Args:
            input_data: Input data in various formats

        Returns:
            Extracted user message string
        """
        if isinstance(input_data, str):
            return input_data
        if isinstance(input_data, dict):
            # Try common field names
            for field in ["message", "text", "input", "content", "query"]:
                if field in input_data:
                    return str(input_data[field])
            # Fallback to JSON string
            return json.dumps(input_data)
        return str(input_data)

    async def _parse_workflow_input(self, workflow: Any, raw_input: Any) -> Any:
        """Parse input based on workflow's expected input type.

        Args:
            workflow: Workflow object
            raw_input: Raw input data

        Returns:
            Parsed input appropriate for the workflow
        """
        try:
            # Handle structured input
            if isinstance(raw_input, dict):
                return self._parse_structured_workflow_input(workflow, raw_input)
            return self._parse_raw_workflow_input(workflow, str(raw_input))

        except Exception as e:
            logger.warning(f"Error parsing workflow input: {e}")
            return raw_input

    def _get_start_executor_message_types(self, workflow: Any) -> tuple[Any | None, list[Any]]:
        """Return start executor and its declared input types."""
        try:
            start_executor = workflow.get_start_executor()
        except Exception as exc:  # pragma: no cover - defensive logging path
            logger.debug(f"Unable to access workflow start executor: {exc}")
            return None, []

        if not start_executor:
            return None, []

        message_types: list[Any] = []

        try:
            input_types = getattr(start_executor, "input_types", None)
        except Exception as exc:  # pragma: no cover - defensive logging path
            logger.debug(f"Failed to read executor input_types: {exc}")
        else:
            if input_types:
                message_types = list(input_types)

        if not message_types and hasattr(start_executor, "_handlers"):
            try:
                handlers = start_executor._handlers
                if isinstance(handlers, dict):
                    message_types = list(handlers.keys())
            except Exception as exc:  # pragma: no cover - defensive logging path
                logger.debug(f"Failed to read executor handlers: {exc}")

        return start_executor, message_types

    def _select_primary_input_type(self, message_types: list[Any]) -> Any | None:
        """Choose the most user-friendly input type for workflow kick-off."""
        if not message_types:
            return None

        preferred = (str, dict)

        for candidate in preferred:
            for message_type in message_types:
                if message_type is candidate:
                    return candidate
                origin = get_origin(message_type)
                if origin is candidate:
                    return candidate

        return message_types[0]

    def _parse_structured_workflow_input(self, workflow: Any, input_data: dict[str, Any]) -> Any:
        """Parse structured input data for workflow execution.

        Args:
            workflow: Workflow object
            input_data: Structured input data

        Returns:
            Parsed input for workflow
        """
        try:
            from ._utils import parse_input_for_type

            # Get the start executor and its input type
            start_executor, message_types = self._get_start_executor_message_types(workflow)
            if not start_executor:
                logger.debug("Cannot determine input type for workflow - using raw dict")
                return input_data

            if not message_types:
                logger.debug("No message types found for start executor - using raw dict")
                return input_data

            # Get the first (primary) input type
            input_type = self._select_primary_input_type(message_types)
            if input_type is None:
                logger.debug("Could not select primary input type for workflow - using raw dict")
                return input_data

            # Use consolidated parsing logic from _utils
            return parse_input_for_type(input_data, input_type)

        except Exception as e:
            logger.warning(f"Error parsing structured workflow input: {e}")
            return input_data

    def _parse_raw_workflow_input(self, workflow: Any, raw_input: str) -> Any:
        """Parse raw input string based on workflow's expected input type.

        Args:
            workflow: Workflow object
            raw_input: Raw input string

        Returns:
            Parsed input for workflow
        """
        try:
            from ._utils import parse_input_for_type

            # Get the start executor and its input type
            start_executor, message_types = self._get_start_executor_message_types(workflow)
            if not start_executor:
                logger.debug("Cannot determine input type for workflow - using raw string")
                return raw_input

            if not message_types:
                logger.debug("No message types found for start executor - using raw string")
                return raw_input

            # Get the first (primary) input type
            input_type = self._select_primary_input_type(message_types)
            if input_type is None:
                logger.debug("Could not select primary input type for workflow - using raw string")
                return raw_input

            # Use consolidated parsing logic from _utils
            return parse_input_for_type(raw_input, input_type)

        except Exception as e:
            logger.debug(f"Error parsing workflow input: {e}")
            return raw_input



================================================
FILE: python/packages/devui/agent_framework_devui/_mapper.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Agent Framework message mapper implementation."""

import json
import logging
import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Any, Union

from .models import (
    AgentFrameworkRequest,
    InputTokensDetails,
    OpenAIResponse,
    OutputTokensDetails,
    ResponseErrorEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionResultComplete,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoningTextDeltaEvent,
    ResponseStreamEvent,
    ResponseTextDeltaEvent,
    ResponseTraceEventComplete,
    ResponseUsage,
    ResponseUsageEventComplete,
    ResponseWorkflowEventComplete,
)

logger = logging.getLogger(__name__)

# Type alias for all possible event types
EventType = Union[
    ResponseStreamEvent,
    ResponseWorkflowEventComplete,
    ResponseFunctionResultComplete,
    ResponseTraceEventComplete,
    ResponseUsageEventComplete,
]


class MessageMapper:
    """Maps Agent Framework messages/responses to OpenAI format."""

    def __init__(self) -> None:
        """Initialize Agent Framework message mapper."""
        self.sequence_counter = 0
        self._conversion_contexts: dict[int, dict[str, Any]] = {}

        # Register content type mappers for all 12 Agent Framework content types
        self.content_mappers = {
            "TextContent": self._map_text_content,
            "TextReasoningContent": self._map_reasoning_content,
            "FunctionCallContent": self._map_function_call_content,
            "FunctionResultContent": self._map_function_result_content,
            "ErrorContent": self._map_error_content,
            "UsageContent": self._map_usage_content,
            "DataContent": self._map_data_content,
            "UriContent": self._map_uri_content,
            "HostedFileContent": self._map_hosted_file_content,
            "HostedVectorStoreContent": self._map_hosted_vector_store_content,
            "FunctionApprovalRequestContent": self._map_approval_request_content,
            "FunctionApprovalResponseContent": self._map_approval_response_content,
        }

    async def convert_event(self, raw_event: Any, request: AgentFrameworkRequest) -> Sequence[Any]:
        """Convert a single Agent Framework event to OpenAI events.

        Args:
            raw_event: Agent Framework event (AgentRunResponseUpdate, WorkflowEvent, etc.)
            request: Original request for context

        Returns:
            List of OpenAI response stream events
        """
        context = self._get_or_create_context(request)

        # Handle error events
        if isinstance(raw_event, dict) and raw_event.get("type") == "error":
            return [await self._create_error_event(raw_event.get("message", "Unknown error"), context)]

        # Handle ResponseTraceEvent objects from our trace collector
        from .models import ResponseTraceEvent

        if isinstance(raw_event, ResponseTraceEvent):
            return [
                ResponseTraceEventComplete(
                    type="response.trace.complete",
                    data=raw_event.data,
                    item_id=context["item_id"],
                    sequence_number=self._next_sequence(context),
                )
            ]

        # Import Agent Framework types for proper isinstance checks
        try:
            from agent_framework import AgentRunResponseUpdate, WorkflowEvent
            from agent_framework._workflows._events import AgentRunUpdateEvent

            # Handle AgentRunUpdateEvent - workflow event wrapping AgentRunResponseUpdate
            # This must be checked BEFORE generic WorkflowEvent check
            if isinstance(raw_event, AgentRunUpdateEvent):
                # Extract the AgentRunResponseUpdate from the event's data attribute
                if raw_event.data and isinstance(raw_event.data, AgentRunResponseUpdate):
                    return await self._convert_agent_update(raw_event.data, context)
                # If no data, treat as generic workflow event
                return await self._convert_workflow_event(raw_event, context)

            # Handle agent updates (AgentRunResponseUpdate) - for direct agent execution
            if isinstance(raw_event, AgentRunResponseUpdate):
                return await self._convert_agent_update(raw_event, context)

            # Handle workflow events (any class that inherits from WorkflowEvent)
            if isinstance(raw_event, WorkflowEvent):
                return await self._convert_workflow_event(raw_event, context)

        except ImportError as e:
            logger.warning(f"Could not import Agent Framework types: {e}")
            # Fallback to attribute-based detection
            if hasattr(raw_event, "contents"):
                return await self._convert_agent_update(raw_event, context)
            if hasattr(raw_event, "__class__") and "Event" in raw_event.__class__.__name__:
                return await self._convert_workflow_event(raw_event, context)

        # Unknown event type
        return [await self._create_unknown_event(raw_event, context)]

    async def aggregate_to_response(self, events: Sequence[Any], request: AgentFrameworkRequest) -> OpenAIResponse:
        """Aggregate streaming events into final OpenAI response.

        Args:
            events: List of OpenAI stream events
            request: Original request for context

        Returns:
            Final aggregated OpenAI response
        """
        try:
            # Extract text content from events
            content_parts = []

            for event in events:
                # Extract delta text from ResponseTextDeltaEvent
                if hasattr(event, "delta") and hasattr(event, "type") and event.type == "response.output_text.delta":
                    content_parts.append(event.delta)

            # Combine content
            full_content = "".join(content_parts)

            # Create proper OpenAI Response
            response_output_text = ResponseOutputText(type="output_text", text=full_content, annotations=[])

            response_output_message = ResponseOutputMessage(
                type="message",
                role="assistant",
                content=[response_output_text],
                id=f"msg_{uuid.uuid4().hex[:8]}",
                status="completed",
            )

            # Create usage object
            input_token_count = len(str(request.input)) // 4 if request.input else 0
            output_token_count = len(full_content) // 4

            usage = ResponseUsage(
                input_tokens=input_token_count,
                output_tokens=output_token_count,
                total_tokens=input_token_count + output_token_count,
                input_tokens_details=InputTokensDetails(cached_tokens=0),
                output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
            )

            return OpenAIResponse(
                id=f"resp_{uuid.uuid4().hex[:12]}",
                object="response",
                created_at=datetime.now().timestamp(),
                model=request.model,
                output=[response_output_message],
                usage=usage,
                parallel_tool_calls=False,
                tool_choice="none",
                tools=[],
            )

        except Exception as e:
            logger.exception(f"Error aggregating response: {e}")
            return await self._create_error_response(str(e), request)

    def _get_or_create_context(self, request: AgentFrameworkRequest) -> dict[str, Any]:
        """Get or create conversion context for this request.

        Args:
            request: Request to get context for

        Returns:
            Conversion context dictionary
        """
        request_key = id(request)
        if request_key not in self._conversion_contexts:
            self._conversion_contexts[request_key] = {
                "sequence_counter": 0,
                "item_id": f"msg_{uuid.uuid4().hex[:8]}",
                "content_index": 0,
                "output_index": 0,
            }
        return self._conversion_contexts[request_key]

    def _next_sequence(self, context: dict[str, Any]) -> int:
        """Get next sequence number for events.

        Args:
            context: Conversion context

        Returns:
            Next sequence number
        """
        context["sequence_counter"] += 1
        return int(context["sequence_counter"])

    async def _convert_agent_update(self, update: Any, context: dict[str, Any]) -> Sequence[Any]:
        """Convert AgentRunResponseUpdate to OpenAI events using comprehensive content mapping.

        Args:
            update: Agent run response update
            context: Conversion context

        Returns:
            List of OpenAI response stream events
        """
        events: list[Any] = []

        try:
            # Handle different update types
            if not hasattr(update, "contents") or not update.contents:
                return events

            for content in update.contents:
                content_type = content.__class__.__name__

                if content_type in self.content_mappers:
                    mapped_events = await self.content_mappers[content_type](content, context)
                    if isinstance(mapped_events, list):
                        events.extend(mapped_events)
                    else:
                        events.append(mapped_events)
                else:
                    # Graceful fallback for unknown content types
                    events.append(await self._create_unknown_content_event(content, context))

                context["content_index"] += 1

        except Exception as e:
            logger.warning(f"Error converting agent update: {e}")
            events.append(await self._create_error_event(str(e), context))

        return events

    async def _convert_workflow_event(self, event: Any, context: dict[str, Any]) -> Sequence[Any]:
        """Convert workflow event to structured OpenAI events.

        Args:
            event: Workflow event
            context: Conversion context

        Returns:
            List of OpenAI response stream events
        """
        try:
            # Get event data and serialize if it's a SerializationMixin
            event_data = getattr(event, "data", None)
            if event_data is not None and hasattr(event_data, "to_dict"):
                # SerializationMixin objects - convert to dict for JSON serialization
                try:
                    event_data = event_data.to_dict()
                except Exception as e:
                    logger.debug(f"Failed to serialize event data with to_dict(): {e}")
                    event_data = str(event_data)

            # Create structured workflow event
            workflow_event = ResponseWorkflowEventComplete(
                type="response.workflow_event.complete",
                data={
                    "event_type": event.__class__.__name__,
                    "data": event_data,
                    "executor_id": getattr(event, "executor_id", None),
                    "timestamp": datetime.now().isoformat(),
                },
                executor_id=getattr(event, "executor_id", None),
                item_id=context["item_id"],
                output_index=context["output_index"],
                sequence_number=self._next_sequence(context),
            )

            return [workflow_event]

        except Exception as e:
            logger.warning(f"Error converting workflow event: {e}")
            return [await self._create_error_event(str(e), context)]

    # Content type mappers - implementing our comprehensive mapping plan

    async def _map_text_content(self, content: Any, context: dict[str, Any]) -> ResponseTextDeltaEvent:
        """Map TextContent to ResponseTextDeltaEvent."""
        return self._create_text_delta_event(content.text, context)

    async def _map_reasoning_content(self, content: Any, context: dict[str, Any]) -> ResponseReasoningTextDeltaEvent:
        """Map TextReasoningContent to ResponseReasoningTextDeltaEvent."""
        return ResponseReasoningTextDeltaEvent(
            type="response.reasoning_text.delta",
            delta=content.text,
            item_id=context["item_id"],
            output_index=context["output_index"],
            content_index=context["content_index"],
            sequence_number=self._next_sequence(context),
        )

    async def _map_function_call_content(
        self, content: Any, context: dict[str, Any]
    ) -> list[ResponseFunctionCallArgumentsDeltaEvent]:
        """Map FunctionCallContent to ResponseFunctionCallArgumentsDeltaEvent(s)."""
        events = []

        # For streaming, need to chunk the arguments JSON
        args_str = json.dumps(content.arguments) if hasattr(content, "arguments") and content.arguments else "{}"

        # Chunk the JSON string for streaming
        for chunk in self._chunk_json_string(args_str):
            events.append(
                ResponseFunctionCallArgumentsDeltaEvent(
                    type="response.function_call_arguments.delta",
                    delta=chunk,
                    item_id=context["item_id"],
                    output_index=context["output_index"],
                    sequence_number=self._next_sequence(context),
                )
            )

        return events

    async def _map_function_result_content(
        self, content: Any, context: dict[str, Any]
    ) -> ResponseFunctionResultComplete:
        """Map FunctionResultContent to structured event."""
        return ResponseFunctionResultComplete(
            type="response.function_result.complete",
            data={
                "call_id": getattr(content, "call_id", f"call_{uuid.uuid4().hex[:8]}"),
                "result": getattr(content, "result", None),
                "status": "completed" if not getattr(content, "exception", None) else "failed",
                "exception": str(getattr(content, "exception", None)) if getattr(content, "exception", None) else None,
                "timestamp": datetime.now().isoformat(),
            },
            call_id=getattr(content, "call_id", f"call_{uuid.uuid4().hex[:8]}"),
            item_id=context["item_id"],
            output_index=context["output_index"],
            sequence_number=self._next_sequence(context),
        )

    async def _map_error_content(self, content: Any, context: dict[str, Any]) -> ResponseErrorEvent:
        """Map ErrorContent to ResponseErrorEvent."""
        return ResponseErrorEvent(
            type="error",
            message=getattr(content, "message", "Unknown error"),
            code=getattr(content, "error_code", None),
            param=None,
            sequence_number=self._next_sequence(context),
        )

    async def _map_usage_content(self, content: Any, context: dict[str, Any]) -> ResponseUsageEventComplete:
        """Map UsageContent to structured usage event."""
        # Store usage data in context for aggregation
        if "usage_data" not in context:
            context["usage_data"] = []
        context["usage_data"].append(content)

        # Extract usage from UsageContent.details (UsageDetails object)
        details = getattr(content, "details", None)
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0

        if details:
            total_tokens = getattr(details, "total_token_count", 0) or 0
            prompt_tokens = getattr(details, "input_token_count", 0) or 0
            completion_tokens = getattr(details, "output_token_count", 0) or 0

        return ResponseUsageEventComplete(
            type="response.usage.complete",
            data={
                "usage_data": details.to_dict() if details and hasattr(details, "to_dict") else {},
                "total_tokens": total_tokens,
                "completion_tokens": completion_tokens,
                "prompt_tokens": prompt_tokens,
                "timestamp": datetime.now().isoformat(),
            },
            item_id=context["item_id"],
            output_index=context["output_index"],
            sequence_number=self._next_sequence(context),
        )

    async def _map_data_content(self, content: Any, context: dict[str, Any]) -> ResponseTraceEventComplete:
        """Map DataContent to structured trace event."""
        return ResponseTraceEventComplete(
            type="response.trace.complete",
            data={
                "content_type": "data",
                "data": getattr(content, "data", None),
                "mime_type": getattr(content, "mime_type", "application/octet-stream"),
                "size_bytes": len(str(getattr(content, "data", ""))) if getattr(content, "data", None) else 0,
                "timestamp": datetime.now().isoformat(),
            },
            item_id=context["item_id"],
            output_index=context["output_index"],
            sequence_number=self._next_sequence(context),
        )

    async def _map_uri_content(self, content: Any, context: dict[str, Any]) -> ResponseTraceEventComplete:
        """Map UriContent to structured trace event."""
        return ResponseTraceEventComplete(
            type="response.trace.complete",
            data={
                "content_type": "uri",
                "uri": getattr(content, "uri", ""),
                "mime_type": getattr(content, "mime_type", "text/plain"),
                "timestamp": datetime.now().isoformat(),
            },
            item_id=context["item_id"],
            output_index=context["output_index"],
            sequence_number=self._next_sequence(context),
        )

    async def _map_hosted_file_content(self, content: Any, context: dict[str, Any]) -> ResponseTraceEventComplete:
        """Map HostedFileContent to structured trace event."""
        return ResponseTraceEventComplete(
            type="response.trace.complete",
            data={
                "content_type": "hosted_file",
                "file_id": getattr(content, "file_id", "unknown"),
                "timestamp": datetime.now().isoformat(),
            },
            item_id=context["item_id"],
            output_index=context["output_index"],
            sequence_number=self._next_sequence(context),
        )

    async def _map_hosted_vector_store_content(
        self, content: Any, context: dict[str, Any]
    ) -> ResponseTraceEventComplete:
        """Map HostedVectorStoreContent to structured trace event."""
        return ResponseTraceEventComplete(
            type="response.trace.complete",
            data={
                "content_type": "hosted_vector_store",
                "vector_store_id": getattr(content, "vector_store_id", "unknown"),
                "timestamp": datetime.now().isoformat(),
            },
            item_id=context["item_id"],
            output_index=context["output_index"],
            sequence_number=self._next_sequence(context),
        )

    async def _map_approval_request_content(self, content: Any, context: dict[str, Any]) -> dict[str, Any]:
        """Map FunctionApprovalRequestContent to custom event."""
        return {
            "type": "response.function_approval.requested",
            "request_id": getattr(content, "id", "unknown"),
            "function_call": {
                "id": getattr(content.function_call, "call_id", "") if hasattr(content, "function_call") else "",
                "name": getattr(content.function_call, "name", "") if hasattr(content, "function_call") else "",
                "arguments": getattr(content.function_call, "arguments", {})
                if hasattr(content, "function_call")
                else {},
            },
            "item_id": context["item_id"],
            "output_index": context["output_index"],
            "sequence_number": self._next_sequence(context),
        }

    async def _map_approval_response_content(self, content: Any, context: dict[str, Any]) -> dict[str, Any]:
        """Map FunctionApprovalResponseContent to custom event."""
        return {
            "type": "response.function_approval.responded",
            "request_id": getattr(content, "request_id", "unknown"),
            "approved": getattr(content, "approved", False),
            "item_id": context["item_id"],
            "output_index": context["output_index"],
            "sequence_number": self._next_sequence(context),
        }

    # Helper methods

    def _create_text_delta_event(self, text: str, context: dict[str, Any]) -> ResponseTextDeltaEvent:
        """Create a ResponseTextDeltaEvent."""
        return ResponseTextDeltaEvent(
            type="response.output_text.delta",
            item_id=context["item_id"],
            output_index=context["output_index"],
            content_index=context["content_index"],
            delta=text,
            sequence_number=self._next_sequence(context),
            logprobs=[],
        )

    async def _create_error_event(self, message: str, context: dict[str, Any]) -> ResponseErrorEvent:
        """Create a ResponseErrorEvent."""
        return ResponseErrorEvent(
            type="error", message=message, code=None, param=None, sequence_number=self._next_sequence(context)
        )

    async def _create_unknown_event(self, event_data: Any, context: dict[str, Any]) -> ResponseStreamEvent:
        """Create event for unknown event types."""
        text = f"Unknown event: {event_data!s}\\n"
        return self._create_text_delta_event(text, context)

    async def _create_unknown_content_event(self, content: Any, context: dict[str, Any]) -> ResponseStreamEvent:
        """Create event for unknown content types."""
        content_type = content.__class__.__name__
        text = f"⚠️ Unknown content type: {content_type}\\n"
        return self._create_text_delta_event(text, context)

    def _chunk_json_string(self, json_str: str, chunk_size: int = 50) -> list[str]:
        """Chunk JSON string for streaming."""
        return [json_str[i : i + chunk_size] for i in range(0, len(json_str), chunk_size)]

    async def _create_error_response(self, error_message: str, request: AgentFrameworkRequest) -> OpenAIResponse:
        """Create error response."""
        error_text = f"Error: {error_message}"

        response_output_text = ResponseOutputText(type="output_text", text=error_text, annotations=[])

        response_output_message = ResponseOutputMessage(
            type="message",
            role="assistant",
            content=[response_output_text],
            id=f"msg_{uuid.uuid4().hex[:8]}",
            status="completed",
        )

        usage = ResponseUsage(
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            input_tokens_details=InputTokensDetails(cached_tokens=0),
            output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
        )

        return OpenAIResponse(
            id=f"resp_{uuid.uuid4().hex[:12]}",
            object="response",
            created_at=datetime.now().timestamp(),
            model=request.model,
            output=[response_output_message],
            usage=usage,
            parallel_tool_calls=False,
            tool_choice="none",
            tools=[],
        )



================================================
FILE: python/packages/devui/agent_framework_devui/_server.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""FastAPI server implementation."""

import inspect
import json
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, get_origin

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from ._discovery import EntityDiscovery
from ._executor import AgentFrameworkExecutor
from ._mapper import MessageMapper
from .models import AgentFrameworkRequest, OpenAIError
from .models._discovery_models import DiscoveryResponse, EntityInfo

logger = logging.getLogger(__name__)


def _extract_executor_message_types(executor: Any) -> list[Any]:
    """Return declared input types for the given executor."""
    message_types: list[Any] = []

    try:
        input_types = getattr(executor, "input_types", None)
    except Exception as exc:  # pragma: no cover - defensive logging path
        logger.debug(f"Failed to access executor input_types: {exc}")
    else:
        if input_types:
            message_types = list(input_types)

    if not message_types and hasattr(executor, "_handlers"):
        try:
            handlers = executor._handlers
            if isinstance(handlers, dict):
                message_types = list(handlers.keys())
        except Exception as exc:  # pragma: no cover - defensive logging path
            logger.debug(f"Failed to read executor handlers: {exc}")

    return message_types


def _select_primary_input_type(message_types: list[Any]) -> Any | None:
    """Choose the most user-friendly input type for rendering workflow inputs."""
    if not message_types:
        return None

    preferred = (str, dict)

    for candidate in preferred:
        for message_type in message_types:
            if message_type is candidate:
                return candidate
            origin = get_origin(message_type)
            if origin is candidate:
                return candidate

    return message_types[0]


class DevServer:
    """Development Server - OpenAI compatible API server for debugging agents."""

    def __init__(
        self,
        entities_dir: str | None = None,
        port: int = 8080,
        host: str = "127.0.0.1",
        cors_origins: list[str] | None = None,
        ui_enabled: bool = True,
    ) -> None:
        """Initialize the development server.

        Args:
            entities_dir: Directory to scan for entities
            port: Port to run server on
            host: Host to bind server to
            cors_origins: List of allowed CORS origins
            ui_enabled: Whether to enable the UI
        """
        self.entities_dir = entities_dir
        self.port = port
        self.host = host
        self.cors_origins = cors_origins or ["*"]
        self.ui_enabled = ui_enabled
        self.executor: AgentFrameworkExecutor | None = None
        self._app: FastAPI | None = None
        self._pending_entities: list[Any] | None = None

    async def _ensure_executor(self) -> AgentFrameworkExecutor:
        """Ensure executor is initialized."""
        if self.executor is None:
            logger.info("Initializing Agent Framework executor...")

            # Create components directly
            entity_discovery = EntityDiscovery(self.entities_dir)
            message_mapper = MessageMapper()
            self.executor = AgentFrameworkExecutor(entity_discovery, message_mapper)

            # Discover entities from directory
            discovered_entities = await self.executor.discover_entities()
            logger.info(f"Discovered {len(discovered_entities)} entities from directory")

            # Register any pending in-memory entities
            if self._pending_entities:
                discovery = self.executor.entity_discovery
                for entity in self._pending_entities:
                    try:
                        entity_info = await discovery.create_entity_info_from_object(entity, source="in-memory")
                        discovery.register_entity(entity_info.id, entity_info, entity)
                        logger.info(f"Registered in-memory entity: {entity_info.id}")
                    except Exception as e:
                        logger.error(f"Failed to register in-memory entity: {e}")
                self._pending_entities = None  # Clear after registration

            # Get the final entity count after all registration
            all_entities = self.executor.entity_discovery.list_entities()
            logger.info(f"Total entities available: {len(all_entities)}")

        return self.executor

    async def _cleanup_entities(self) -> None:
        """Cleanup entity resources (close clients, credentials, etc.)."""
        if not self.executor:
            return

        logger.info("Cleaning up entity resources...")
        entities = self.executor.entity_discovery.list_entities()
        closed_count = 0

        for entity_info in entities:
            try:
                entity_obj = self.executor.entity_discovery.get_entity_object(entity_info.id)
                if entity_obj and hasattr(entity_obj, "chat_client"):
                    client = entity_obj.chat_client
                    if hasattr(client, "close") and callable(client.close):
                        if inspect.iscoroutinefunction(client.close):
                            await client.close()
                        else:
                            client.close()
                        closed_count += 1
                        logger.debug(f"Closed client for entity: {entity_info.id}")
            except Exception as e:
                logger.warning(f"Error closing entity {entity_info.id}: {e}")

        if closed_count > 0:
            logger.info(f"Closed {closed_count} entity client(s)")

    def create_app(self) -> FastAPI:
        """Create the FastAPI application."""

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            # Startup
            logger.info("Starting Agent Framework Server")
            await self._ensure_executor()
            yield
            # Shutdown
            logger.info("Shutting down Agent Framework Server")

            # Cleanup entity resources (e.g., close credentials, clients)
            if self.executor:
                await self._cleanup_entities()

        app = FastAPI(
            title="Agent Framework Server",
            description="OpenAI-compatible API server for Agent Framework and other AI frameworks",
            version="1.0.0",
            lifespan=lifespan,
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._register_routes(app)
        self._mount_ui(app)

        return app

    def _register_routes(self, app: FastAPI) -> None:
        """Register API routes."""

        @app.get("/health")
        async def health_check() -> dict[str, Any]:
            """Health check endpoint."""
            executor = await self._ensure_executor()
            # Use list_entities() to avoid re-discovering and re-registering entities
            entities = executor.entity_discovery.list_entities()

            return {"status": "healthy", "entities_count": len(entities), "framework": "agent_framework"}

        @app.get("/v1/entities", response_model=DiscoveryResponse)
        async def discover_entities() -> DiscoveryResponse:
            """List all registered entities."""
            try:
                executor = await self._ensure_executor()
                # Use list_entities() instead of discover_entities() to get already-registered entities
                entities = executor.entity_discovery.list_entities()
                return DiscoveryResponse(entities=entities)
            except Exception as e:
                logger.error(f"Error listing entities: {e}")
                raise HTTPException(status_code=500, detail=f"Entity listing failed: {e!s}") from e

        @app.get("/v1/entities/{entity_id}/info", response_model=EntityInfo)
        async def get_entity_info(entity_id: str) -> EntityInfo:
            """Get detailed information about a specific entity."""
            try:
                executor = await self._ensure_executor()
                entity_info = executor.get_entity_info(entity_id)

                if not entity_info:
                    raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

                # For workflows, populate additional detailed information
                if entity_info.type == "workflow":
                    entity_obj = executor.entity_discovery.get_entity_object(entity_id)
                    if entity_obj:
                        # Get workflow structure
                        workflow_dump = None
                        if hasattr(entity_obj, "to_dict") and callable(getattr(entity_obj, "to_dict", None)):
                            try:
                                workflow_dump = entity_obj.to_dict()  # type: ignore[attr-defined]
                            except Exception:
                                workflow_dump = None
                        elif hasattr(entity_obj, "to_json") and callable(getattr(entity_obj, "to_json", None)):
                            try:
                                raw_dump = entity_obj.to_json()  # type: ignore[attr-defined]
                            except Exception:
                                workflow_dump = None
                            else:
                                if isinstance(raw_dump, (bytes, bytearray)):
                                    try:
                                        raw_dump = raw_dump.decode()
                                    except Exception:
                                        raw_dump = raw_dump.decode(errors="replace")
                                if isinstance(raw_dump, str):
                                    try:
                                        parsed_dump = json.loads(raw_dump)
                                    except Exception:
                                        workflow_dump = raw_dump
                                    else:
                                        workflow_dump = parsed_dump if isinstance(parsed_dump, dict) else raw_dump
                                else:
                                    workflow_dump = raw_dump
                        elif hasattr(entity_obj, "__dict__"):
                            workflow_dump = {k: v for k, v in entity_obj.__dict__.items() if not k.startswith("_")}

                        # Get input schema information
                        input_schema = {}
                        input_type_name = "Unknown"
                        start_executor_id = ""

                        try:
                            from ._utils import generate_input_schema

                            start_executor = entity_obj.get_start_executor()
                        except Exception as e:
                            logger.debug(f"Could not extract input info for workflow {entity_id}: {e}")
                        else:
                            if start_executor:
                                start_executor_id = getattr(start_executor, "executor_id", "") or getattr(
                                    start_executor, "id", ""
                                )

                                message_types = _extract_executor_message_types(start_executor)
                                input_type = _select_primary_input_type(message_types)

                                if input_type:
                                    input_type_name = getattr(input_type, "__name__", str(input_type))

                                    # Generate schema using comprehensive schema generation
                                    input_schema = generate_input_schema(input_type)

                        if not input_schema:
                            input_schema = {"type": "string"}
                            if input_type_name == "Unknown":
                                input_type_name = "string"

                        # Get executor list
                        executor_list = []
                        if hasattr(entity_obj, "executors") and entity_obj.executors:
                            executor_list = [getattr(ex, "executor_id", str(ex)) for ex in entity_obj.executors]

                        # Create copy of entity info and populate workflow-specific fields
                        update_payload: dict[str, Any] = {
                            "workflow_dump": workflow_dump,
                            "input_schema": input_schema,
                            "input_type_name": input_type_name,
                            "start_executor_id": start_executor_id,
                        }
                        if executor_list:
                            update_payload["executors"] = executor_list
                        return entity_info.model_copy(update=update_payload)

                # For non-workflow entities, return as-is
                return entity_info

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting entity info for {entity_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to get entity info: {e!s}") from e

        @app.post("/v1/entities/add")
        async def add_entity(request: dict[str, Any]) -> dict[str, Any]:
            """Add entity from URL."""
            try:
                url = request.get("url")
                metadata = request.get("metadata", {})

                if not url:
                    raise HTTPException(status_code=400, detail="URL is required")

                logger.info(f"Attempting to add entity from URL: {url}")
                executor = await self._ensure_executor()
                entity_info, error_msg = await executor.entity_discovery.fetch_remote_entity(url, metadata)

                if not entity_info:
                    # Sanitize error message - only return safe, user-friendly errors
                    logger.error(f"Failed to fetch or validate entity from {url}: {error_msg}")
                    safe_error = error_msg if error_msg else "Failed to fetch or validate entity"
                    raise HTTPException(status_code=400, detail=safe_error)

                logger.info(f"Successfully added entity: {entity_info.id}")
                return {"success": True, "entity": entity_info.model_dump()}

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error adding entity: {e}", exc_info=True)
                # Don't expose internal error details to client
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred while adding the entity"
                ) from e

        @app.delete("/v1/entities/{entity_id}")
        async def remove_entity(entity_id: str) -> dict[str, Any]:
            """Remove entity by ID."""
            try:
                executor = await self._ensure_executor()

                # Cleanup entity resources before removal
                try:
                    entity_obj = executor.entity_discovery.get_entity_object(entity_id)
                    if entity_obj and hasattr(entity_obj, "chat_client"):
                        client = entity_obj.chat_client
                        if hasattr(client, "close") and callable(client.close):
                            if inspect.iscoroutinefunction(client.close):
                                await client.close()
                            else:
                                client.close()
                            logger.info(f"Closed client for entity: {entity_id}")
                except Exception as e:
                    logger.warning(f"Error closing entity {entity_id} during removal: {e}")

                # Remove entity from registry
                success = executor.entity_discovery.remove_remote_entity(entity_id)

                if success:
                    return {"success": True}
                raise HTTPException(status_code=404, detail="Entity not found or cannot be removed")

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error removing entity {entity_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to remove entity: {e!s}") from e

        @app.post("/v1/responses")
        async def create_response(request: AgentFrameworkRequest, raw_request: Request) -> Any:
            """OpenAI Responses API endpoint."""
            try:
                raw_body = await raw_request.body()
                logger.info(f"Raw request body: {raw_body.decode()}")
                logger.info(f"Parsed request: model={request.model}, extra_body={request.extra_body}")

                # Get entity_id using the new method
                entity_id = request.get_entity_id()
                logger.info(f"Extracted entity_id: {entity_id}")

                if not entity_id:
                    error = OpenAIError.create(f"Missing entity_id. Request extra_body: {request.extra_body}")
                    return JSONResponse(status_code=400, content=error.to_dict())

                # Get executor and validate entity exists
                executor = await self._ensure_executor()
                try:
                    entity_info = executor.get_entity_info(entity_id)
                    logger.info(f"Found entity: {entity_info.name} ({entity_info.type})")
                except Exception:
                    error = OpenAIError.create(f"Entity not found: {entity_id}")
                    return JSONResponse(status_code=404, content=error.to_dict())

                # Execute request
                if request.stream:
                    return StreamingResponse(
                        self._stream_execution(executor, request),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                            "Access-Control-Allow-Origin": "*",
                        },
                    )
                return await executor.execute_sync(request)

            except Exception as e:
                logger.error(f"Error executing request: {e}")
                error = OpenAIError.create(f"Execution failed: {e!s}")
                return JSONResponse(status_code=500, content=error.to_dict())

        @app.post("/v1/threads")
        async def create_thread(request_data: dict[str, Any]) -> dict[str, Any]:
            """Create a new thread for an agent."""
            try:
                agent_id = request_data.get("agent_id")
                if not agent_id:
                    raise HTTPException(status_code=400, detail="agent_id is required")

                executor = await self._ensure_executor()
                thread_id = executor.create_thread(agent_id)

                return {
                    "id": thread_id,
                    "object": "thread",
                    "created_at": int(__import__("time").time()),
                    "metadata": {"agent_id": agent_id},
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error creating thread: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to create thread: {e!s}") from e

        @app.get("/v1/threads")
        async def list_threads(agent_id: str) -> dict[str, Any]:
            """List threads for an agent."""
            try:
                executor = await self._ensure_executor()
                thread_ids = executor.list_threads_for_agent(agent_id)

                # Convert thread IDs to thread objects
                threads = []
                for thread_id in thread_ids:
                    threads.append({"id": thread_id, "object": "thread", "agent_id": agent_id})

                return {"object": "list", "data": threads}
            except Exception as e:
                logger.error(f"Error listing threads: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to list threads: {e!s}") from e

        @app.get("/v1/threads/{thread_id}")
        async def get_thread(thread_id: str) -> dict[str, Any]:
            """Get thread information."""
            try:
                executor = await self._ensure_executor()

                # Check if thread exists
                thread = executor.get_thread(thread_id)
                if not thread:
                    raise HTTPException(status_code=404, detail="Thread not found")

                # Get the agent that owns this thread
                agent_id = executor.get_agent_for_thread(thread_id)

                return {"id": thread_id, "object": "thread", "agent_id": agent_id}
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting thread {thread_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to get thread: {e!s}") from e

        @app.delete("/v1/threads/{thread_id}")
        async def delete_thread(thread_id: str) -> dict[str, Any]:
            """Delete a thread."""
            try:
                executor = await self._ensure_executor()
                success = executor.delete_thread(thread_id)

                if not success:
                    raise HTTPException(status_code=404, detail="Thread not found")

                return {"id": thread_id, "object": "thread.deleted", "deleted": True}
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error deleting thread {thread_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to delete thread: {e!s}") from e

        @app.get("/v1/threads/{thread_id}/messages")
        async def get_thread_messages(thread_id: str) -> dict[str, Any]:
            """Get messages from a thread."""
            try:
                executor = await self._ensure_executor()

                # Check if thread exists
                thread = executor.get_thread(thread_id)
                if not thread:
                    raise HTTPException(status_code=404, detail="Thread not found")

                # Get messages from thread
                messages = await executor.get_thread_messages(thread_id)

                return {"object": "list", "data": messages, "thread_id": thread_id}
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting messages for thread {thread_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to get thread messages: {e!s}") from e

    async def _stream_execution(
        self, executor: AgentFrameworkExecutor, request: AgentFrameworkRequest
    ) -> AsyncGenerator[str, None]:
        """Stream execution directly through executor."""
        try:
            # Direct call to executor - simple and clean
            async for event in executor.execute_streaming(request):
                # IMPORTANT: Check model_dump_json FIRST because to_json() can have newlines (pretty-printing)
                # which breaks SSE format. model_dump_json() returns single-line JSON.
                if hasattr(event, "model_dump_json"):
                    payload = event.model_dump_json()  # type: ignore[attr-defined]
                elif hasattr(event, "to_json") and callable(getattr(event, "to_json", None)):
                    payload = event.to_json()  # type: ignore[attr-defined]
                    # Strip newlines from pretty-printed JSON for SSE compatibility
                    payload = payload.replace("\n", "").replace("\r", "")
                elif isinstance(event, dict):
                    # Handle plain dict events (e.g., error events from executor)
                    payload = json.dumps(event)
                elif hasattr(event, "to_dict") and callable(getattr(event, "to_dict", None)):
                    payload = json.dumps(event.to_dict())  # type: ignore[attr-defined]
                else:
                    payload = json.dumps(str(event))
                yield f"data: {payload}\n\n"

            # Send final done event
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Error in streaming execution: {e}")
            error_event = {"id": "error", "object": "error", "error": {"message": str(e), "type": "execution_error"}}
            yield f"data: {json.dumps(error_event)}\n\n"

    def _mount_ui(self, app: FastAPI) -> None:
        """Mount the UI as static files."""
        from pathlib import Path

        ui_dir = Path(__file__).parent / "ui"
        if ui_dir.exists() and ui_dir.is_dir() and self.ui_enabled:
            app.mount("/", StaticFiles(directory=str(ui_dir), html=True), name="ui")

    def register_entities(self, entities: list[Any]) -> None:
        """Register entities to be discovered when server starts.

        Args:
            entities: List of entity objects to register
        """
        if self._pending_entities is None:
            self._pending_entities = []
        self._pending_entities.extend(entities)

    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        if self._app is None:
            self._app = self.create_app()
        return self._app



================================================
FILE: python/packages/devui/agent_framework_devui/_session.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Session management for agent execution tracking."""

import logging
import uuid
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Type aliases for better readability
SessionData = dict[str, Any]
RequestRecord = dict[str, Any]
SessionSummary = dict[str, Any]


class SessionManager:
    """Manages execution sessions for tracking requests and context."""

    def __init__(self) -> None:
        """Initialize the session manager."""
        self.sessions: dict[str, SessionData] = {}

    def create_session(self, session_id: str | None = None) -> str:
        """Create a new execution session.

        Args:
            session_id: Optional session ID, if not provided a new one is generated

        Returns:
            Session ID
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now(),
            "requests": [],
            "context": {},
            "active": True,
        }

        logger.debug(f"Created session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> SessionData | None:
        """Get session information.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        return self.sessions.get(session_id)

    def close_session(self, session_id: str) -> None:
        """Close and cleanup a session.

        Args:
            session_id: Session ID to close
        """
        if session_id in self.sessions:
            self.sessions[session_id]["active"] = False
            logger.debug(f"Closed session: {session_id}")

    def add_request_record(
        self, session_id: str, entity_id: str, executor_name: str, request_input: Any, model: str
    ) -> str:
        """Add a request record to a session.

        Args:
            session_id: Session ID
            entity_id: ID of the entity being executed
            executor_name: Name of the executor
            request_input: Input for the request
            model: Model name

        Returns:
            Request ID
        """
        session = self.get_session(session_id)
        if not session:
            return ""

        request_record: RequestRecord = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(),
            "entity_id": entity_id,
            "executor": executor_name,
            "input": request_input,
            "model": model,
            "stream": True,
        }
        session["requests"].append(request_record)
        return str(request_record["id"])

    def update_request_record(self, session_id: str, request_id: str, updates: dict[str, Any]) -> None:
        """Update a request record in a session.

        Args:
            session_id: Session ID
            request_id: Request ID to update
            updates: Dictionary of updates to apply
        """
        session = self.get_session(session_id)
        if not session:
            return

        for request in session["requests"]:
            if request["id"] == request_id:
                request.update(updates)
                break

    def get_session_history(self, session_id: str) -> SessionSummary | None:
        """Get session execution history.

        Args:
            session_id: Session ID

        Returns:
            Session history or None if not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": session_id,
            "created_at": session["created_at"].isoformat(),
            "active": session["active"],
            "request_count": len(session["requests"]),
            "requests": [
                {
                    "id": req["id"],
                    "timestamp": req["timestamp"].isoformat(),
                    "entity_id": req["entity_id"],
                    "executor": req["executor"],
                    "model": req["model"],
                    "input_length": len(str(req["input"])) if req["input"] else 0,
                    "execution_time": req.get("execution_time"),
                    "status": req.get("status", "unknown"),
                }
                for req in session["requests"]
            ],
        }

    def get_active_sessions(self) -> list[SessionSummary]:
        """Get list of active sessions.

        Returns:
            List of active session summaries
        """
        active_sessions = []

        for session_id, session in self.sessions.items():
            if session["active"]:
                active_sessions.append({
                    "session_id": session_id,
                    "created_at": session["created_at"].isoformat(),
                    "request_count": len(session["requests"]),
                    "last_activity": (
                        session["requests"][-1]["timestamp"].isoformat()
                        if session["requests"]
                        else session["created_at"].isoformat()
                    ),
                })

        return active_sessions

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """Cleanup old sessions to prevent memory leaks.

        Args:
            max_age_hours: Maximum age of sessions to keep in hours
        """
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            if session["created_at"].timestamp() < cutoff_time:
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            logger.debug(f"Cleaned up old session: {session_id}")

        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")



================================================
FILE: python/packages/devui/agent_framework_devui/_tracing.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Simplified tracing integration for Agent Framework Server."""

import logging
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from .models import ResponseTraceEvent

logger = logging.getLogger(__name__)


class SimpleTraceCollector(SpanExporter):
    """Simple trace collector that captures spans for direct yielding."""

    def __init__(self, session_id: str | None = None, entity_id: str | None = None) -> None:
        """Initialize trace collector.

        Args:
            session_id: Session identifier for context
            entity_id: Entity identifier for context
        """
        self.session_id = session_id
        self.entity_id = entity_id
        self.collected_events: list[ResponseTraceEvent] = []

    def export(self, spans: Sequence[Any]) -> SpanExportResult:
        """Collect spans as trace events.

        Args:
            spans: Sequence of OpenTelemetry spans

        Returns:
            SpanExportResult indicating success
        """
        logger.debug(f"SimpleTraceCollector received {len(spans)} spans")

        try:
            for span in spans:
                trace_event = self._convert_span_to_trace_event(span)
                if trace_event:
                    self.collected_events.append(trace_event)
                    logger.debug(f"Collected trace event: {span.name}")

            return SpanExportResult.SUCCESS

        except Exception as e:
            logger.error(f"Error collecting trace spans: {e}")
            return SpanExportResult.FAILURE

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush spans (no-op for simple collection)."""
        return True

    def get_pending_events(self) -> list[ResponseTraceEvent]:
        """Get and clear pending trace events.

        Returns:
            List of collected trace events, clearing the internal list
        """
        events = self.collected_events.copy()
        self.collected_events.clear()
        return events

    def _convert_span_to_trace_event(self, span: Any) -> ResponseTraceEvent | None:
        """Convert OpenTelemetry span to ResponseTraceEvent.

        Args:
            span: OpenTelemetry span

        Returns:
            ResponseTraceEvent or None if conversion fails
        """
        try:
            start_time = span.start_time / 1_000_000_000  # Convert from nanoseconds
            end_time = span.end_time / 1_000_000_000 if span.end_time else None
            duration_ms = ((end_time - start_time) * 1000) if end_time else None

            # Build trace data
            trace_data = {
                "type": "trace_span",
                "span_id": str(span.context.span_id),
                "trace_id": str(span.context.trace_id),
                "parent_span_id": str(span.parent.span_id) if span.parent else None,
                "operation_name": span.name,
                "start_time": start_time,
                "end_time": end_time,
                "duration_ms": duration_ms,
                "attributes": dict(span.attributes) if span.attributes else {},
                "status": str(span.status.status_code) if hasattr(span, "status") else "OK",
                "session_id": self.session_id,
                "entity_id": self.entity_id,
            }

            # Add events if available
            if hasattr(span, "events") and span.events:
                trace_data["events"] = [
                    {
                        "name": event.name,
                        "timestamp": event.timestamp / 1_000_000_000,
                        "attributes": dict(event.attributes) if event.attributes else {},
                    }
                    for event in span.events
                ]

            # Add error information if span failed
            if hasattr(span, "status") and span.status.status_code.name == "ERROR":
                trace_data["error"] = span.status.description or "Unknown error"

            return ResponseTraceEvent(type="trace_event", data=trace_data, timestamp=datetime.now().isoformat())

        except Exception as e:
            logger.warning(f"Failed to convert span {getattr(span, 'name', 'unknown')}: {e}")
            return None


@contextmanager
def capture_traces(
    session_id: str | None = None, entity_id: str | None = None
) -> Generator[SimpleTraceCollector, None, None]:
    """Context manager to capture traces during execution.

    Args:
        session_id: Session identifier for context
        entity_id: Entity identifier for context

    Yields:
        SimpleTraceCollector instance to get trace events from
    """
    collector = SimpleTraceCollector(session_id, entity_id)

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor

        # Get current tracer provider and add our collector
        provider = trace.get_tracer_provider()
        processor = SimpleSpanProcessor(collector)

        # Check if this is a real TracerProvider (not the default NoOpTracerProvider)
        if isinstance(provider, TracerProvider):
            provider.add_span_processor(processor)
            logger.debug(f"Added trace collector to TracerProvider for session: {session_id}, entity: {entity_id}")

            try:
                yield collector
            finally:
                # Clean up - shutdown processor
                try:
                    processor.shutdown()
                except Exception as e:
                    logger.debug(f"Error shutting down processor: {e}")
        else:
            logger.warning(f"No real TracerProvider available, got: {type(provider)}")
            yield collector

    except ImportError:
        logger.debug("OpenTelemetry not available")
        yield collector
    except Exception as e:
        logger.error(f"Error setting up trace capture: {e}")
        yield collector



================================================
FILE: python/packages/devui/agent_framework_devui/_utils.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Utility functions for DevUI."""

import inspect
import json
import logging
from dataclasses import fields, is_dataclass
from typing import Any, get_args, get_origin

logger = logging.getLogger(__name__)

# ============================================================================
# Type System Utilities
# ============================================================================


def is_serialization_mixin(cls: type) -> bool:
    """Check if class is a SerializationMixin subclass.

    Args:
        cls: Class to check

    Returns:
        True if class is a SerializationMixin subclass
    """
    try:
        from agent_framework._serialization import SerializationMixin

        return isinstance(cls, type) and issubclass(cls, SerializationMixin)
    except ImportError:
        return False


def _type_to_schema(type_hint: Any, field_name: str) -> dict[str, Any]:
    """Convert a type hint to JSON schema.

    Args:
        type_hint: Type hint to convert
        field_name: Name of the field (for documentation)

    Returns:
        JSON schema dict
    """
    type_str = str(type_hint)

    # Handle None/Optional
    if type_hint is type(None):
        return {"type": "null"}

    # Handle basic types
    if type_hint is str or "str" in type_str:
        return {"type": "string"}
    if type_hint is int or "int" in type_str:
        return {"type": "integer"}
    if type_hint is float or "float" in type_str:
        return {"type": "number"}
    if type_hint is bool or "bool" in type_str:
        return {"type": "boolean"}

    # Handle Literal types (for enum-like values)
    if "Literal" in type_str:
        origin = get_origin(type_hint)
        if origin is not None:
            args = get_args(type_hint)
            if args:
                return {"type": "string", "enum": list(args)}

    # Handle Union/Optional
    if "Union" in type_str or "Optional" in type_str:
        origin = get_origin(type_hint)
        if origin is not None:
            args = get_args(type_hint)
            # Filter out None type
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                return _type_to_schema(non_none_args[0], field_name)
            # Multiple types - pick first non-None
            if non_none_args:
                return _type_to_schema(non_none_args[0], field_name)

    # Handle collections
    if "list" in type_str or "List" in type_str or "Sequence" in type_str:
        origin = get_origin(type_hint)
        if origin is not None:
            args = get_args(type_hint)
            if args:
                items_schema = _type_to_schema(args[0], field_name)
                return {"type": "array", "items": items_schema}
        return {"type": "array"}

    if "dict" in type_str or "Dict" in type_str or "Mapping" in type_str:
        return {"type": "object"}

    # Default fallback
    return {"type": "string", "description": f"Type: {type_hint}"}


def generate_schema_from_serialization_mixin(cls: type[Any]) -> dict[str, Any]:
    """Generate JSON schema from SerializationMixin class.

    Introspects the __init__ signature to extract parameter types and defaults.

    Args:
        cls: SerializationMixin subclass

    Returns:
        JSON schema dict
    """
    sig = inspect.signature(cls)

    # Get type hints
    try:
        from typing import get_type_hints

        type_hints = get_type_hints(cls)
    except Exception:
        type_hints = {}

    properties: dict[str, Any] = {}
    required: list[str] = []

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "kwargs"):
            continue

        # Get type annotation
        param_type = type_hints.get(param_name, str)

        # Generate schema for this parameter
        param_schema = _type_to_schema(param_type, param_name)
        properties[param_name] = param_schema

        # Check if required (no default value, not VAR_KEYWORD)
        if param.default == inspect.Parameter.empty and param.kind != inspect.Parameter.VAR_KEYWORD:
            required.append(param_name)

    schema: dict[str, Any] = {"type": "object", "properties": properties}

    if required:
        schema["required"] = required

    return schema


def generate_schema_from_dataclass(cls: type[Any]) -> dict[str, Any]:
    """Generate JSON schema from dataclass.

    Args:
        cls: Dataclass type

    Returns:
        JSON schema dict
    """
    if not is_dataclass(cls):
        return {"type": "object"}

    properties: dict[str, Any] = {}
    required: list[str] = []

    for field in fields(cls):
        # Generate schema for field type
        field_schema = _type_to_schema(field.type, field.name)
        properties[field.name] = field_schema

        # Check if required (no default value)
        if field.default == field.default_factory:  # No default
            required.append(field.name)

    schema: dict[str, Any] = {"type": "object", "properties": properties}

    if required:
        schema["required"] = required

    return schema


def generate_input_schema(input_type: type) -> dict[str, Any]:
    """Generate JSON schema for workflow input type.

    Supports multiple input types in priority order:
    1. Built-in types (str, dict, int, etc.)
    2. Pydantic models (via model_json_schema)
    3. SerializationMixin classes (via __init__ introspection)
    4. Dataclasses (via fields introspection)
    5. Fallback to string

    Args:
        input_type: Input type to generate schema for

    Returns:
        JSON schema dict
    """
    # 1. Built-in types
    if input_type is str:
        return {"type": "string"}
    if input_type is dict:
        return {"type": "object"}
    if input_type is int:
        return {"type": "integer"}
    if input_type is float:
        return {"type": "number"}
    if input_type is bool:
        return {"type": "boolean"}

    # 2. Pydantic models (legacy support)
    if hasattr(input_type, "model_json_schema"):
        return input_type.model_json_schema()  # type: ignore

    # 3. SerializationMixin classes (ChatMessage, etc.)
    if is_serialization_mixin(input_type):
        return generate_schema_from_serialization_mixin(input_type)

    # 4. Dataclasses
    if is_dataclass(input_type):
        return generate_schema_from_dataclass(input_type)

    # 5. Fallback to string
    type_name = getattr(input_type, "__name__", str(input_type))
    return {"type": "string", "description": f"Input type: {type_name}"}


# ============================================================================
# Input Parsing Utilities
# ============================================================================


def parse_input_for_type(input_data: Any, target_type: type) -> Any:
    """Parse input data to match the target type.

    Handles conversion from raw input (string, dict) to the expected type:
    - Built-in types: direct conversion
    - Pydantic models: use model_validate or model_validate_json
    - SerializationMixin: use from_dict or construct from string
    - Dataclasses: construct from dict

    Args:
        input_data: Raw input data (string, dict, or already correct type)
        target_type: Expected type for the input

    Returns:
        Parsed input matching target_type, or original input if parsing fails
    """
    # If already correct type, return as-is
    if isinstance(input_data, target_type):
        return input_data

    # Handle string input
    if isinstance(input_data, str):
        return _parse_string_input(input_data, target_type)

    # Handle dict input
    if isinstance(input_data, dict):
        return _parse_dict_input(input_data, target_type)

    # Fallback: return original
    return input_data


def _parse_string_input(input_str: str, target_type: type) -> Any:
    """Parse string input to target type.

    Args:
        input_str: Input string
        target_type: Target type

    Returns:
        Parsed input or original string
    """
    # Built-in types
    if target_type is str:
        return input_str
    if target_type is int:
        try:
            return int(input_str)
        except ValueError:
            return input_str
    elif target_type is float:
        try:
            return float(input_str)
        except ValueError:
            return input_str
    elif target_type is bool:
        return input_str.lower() in ("true", "1", "yes")

    # Pydantic models
    if hasattr(target_type, "model_validate_json"):
        try:
            # Try parsing as JSON first
            if input_str.strip().startswith("{"):
                return target_type.model_validate_json(input_str)  # type: ignore

            # Try common field names with the string value
            common_fields = ["text", "message", "content", "input", "data"]
            for field in common_fields:
                try:
                    return target_type(**{field: input_str})  # type: ignore
                except Exception as e:
                    logger.debug(f"Failed to parse string input with field '{field}': {e}")
                    continue
        except Exception as e:
            logger.debug(f"Failed to parse string as Pydantic model: {e}")

    # SerializationMixin (like ChatMessage)
    if is_serialization_mixin(target_type):
        try:
            # Try parsing as JSON dict first
            if input_str.strip().startswith("{"):
                data = json.loads(input_str)
                if hasattr(target_type, "from_dict"):
                    return target_type.from_dict(data)  # type: ignore
                return target_type(**data)  # type: ignore

            # For ChatMessage specifically: create from text
            # Try common field patterns
            common_fields = ["text", "message", "content"]
            sig = inspect.signature(target_type)
            params = list(sig.parameters.keys())

            # If it has 'text' param, use it
            if "text" in params:
                try:
                    return target_type(role="user", text=input_str)  # type: ignore
                except Exception as e:
                    logger.debug(f"Failed to create SerializationMixin with text field: {e}")

            # Try other common fields
            for field in common_fields:
                if field in params:
                    try:
                        return target_type(**{field: input_str})  # type: ignore
                    except Exception as e:
                        logger.debug(f"Failed to create SerializationMixin with field '{field}': {e}")
                        continue
        except Exception as e:
            logger.debug(f"Failed to parse string as SerializationMixin: {e}")

    # Dataclasses
    if is_dataclass(target_type):
        try:
            # Try parsing as JSON
            if input_str.strip().startswith("{"):
                data = json.loads(input_str)
                return target_type(**data)  # type: ignore

            # Try common field names
            common_fields = ["text", "message", "content", "input", "data"]
            for field in common_fields:
                try:
                    return target_type(**{field: input_str})  # type: ignore
                except Exception as e:
                    logger.debug(f"Failed to create dataclass with field '{field}': {e}")
                    continue
        except Exception as e:
            logger.debug(f"Failed to parse string as dataclass: {e}")

    # Fallback: return original string
    return input_str


def _parse_dict_input(input_dict: dict[str, Any], target_type: type) -> Any:
    """Parse dict input to target type.

    Args:
        input_dict: Input dictionary
        target_type: Target type

    Returns:
        Parsed input or original dict
    """
    # Handle primitive types - extract from common field names
    if target_type in (str, int, float, bool):
        try:
            # If it's already the right type, return as-is
            if isinstance(input_dict, target_type):
                return input_dict

            # Try "input" field first (common for workflow inputs)
            if "input" in input_dict:
                return target_type(input_dict["input"])  # type: ignore

            # If single-key dict, extract the value
            if len(input_dict) == 1:
                value = next(iter(input_dict.values()))
                return target_type(value)  # type: ignore

            # Otherwise, return as-is
            return input_dict
        except (ValueError, TypeError) as e:
            logger.debug(f"Failed to convert dict to {target_type}: {e}")
            return input_dict

    # If target is dict, return as-is
    if target_type is dict:
        return input_dict

    # Pydantic models
    if hasattr(target_type, "model_validate"):
        try:
            return target_type.model_validate(input_dict)  # type: ignore
        except Exception as e:
            logger.debug(f"Failed to validate dict as Pydantic model: {e}")

    # SerializationMixin
    if is_serialization_mixin(target_type):
        try:
            if hasattr(target_type, "from_dict"):
                return target_type.from_dict(input_dict)  # type: ignore
            return target_type(**input_dict)  # type: ignore
        except Exception as e:
            logger.debug(f"Failed to parse dict as SerializationMixin: {e}")

    # Dataclasses
    if is_dataclass(target_type):
        try:
            return target_type(**input_dict)  # type: ignore
        except Exception as e:
            logger.debug(f"Failed to parse dict as dataclass: {e}")

    # Fallback: return original dict
    return input_dict



================================================
FILE: python/packages/devui/agent_framework_devui/models/__init__.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Agent Framework DevUI Models - OpenAI-compatible types and custom extensions."""

# Import discovery models
# Import all OpenAI types directly from the openai package
from openai.types.responses import (
    Response,
    ResponseErrorEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseInputParam,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoningTextDeltaEvent,
    ResponseStreamEvent,
    ResponseTextDeltaEvent,
    ResponseUsage,
    ToolParam,
)
from openai.types.responses.response_usage import InputTokensDetails, OutputTokensDetails
from openai.types.shared import Metadata, ResponsesModel

from ._discovery_models import DiscoveryResponse, EntityInfo
from ._openai_custom import (
    AgentFrameworkRequest,
    OpenAIError,
    ResponseFunctionResultComplete,
    ResponseFunctionResultDelta,
    ResponseTraceEvent,
    ResponseTraceEventComplete,
    ResponseTraceEventDelta,
    ResponseUsageEventComplete,
    ResponseUsageEventDelta,
    ResponseWorkflowEventComplete,
    ResponseWorkflowEventDelta,
)

# Type alias for compatibility
OpenAIResponse = Response

# Export all types for easy importing
__all__ = [
    "AgentFrameworkRequest",
    "DiscoveryResponse",
    "EntityInfo",
    "InputTokensDetails",
    "Metadata",
    "OpenAIError",
    "OpenAIResponse",
    "OutputTokensDetails",
    "Response",
    "ResponseErrorEvent",
    "ResponseFunctionCallArgumentsDeltaEvent",
    "ResponseFunctionResultComplete",
    "ResponseFunctionResultDelta",
    "ResponseInputParam",
    "ResponseOutputMessage",
    "ResponseOutputText",
    "ResponseReasoningTextDeltaEvent",
    "ResponseStreamEvent",
    "ResponseTextDeltaEvent",
    "ResponseTraceEvent",
    "ResponseTraceEventComplete",
    "ResponseTraceEventDelta",
    "ResponseUsage",
    "ResponseUsageEventComplete",
    "ResponseUsageEventDelta",
    "ResponseWorkflowEventComplete",
    "ResponseWorkflowEventDelta",
    "ResponsesModel",
    "ToolParam",
]



================================================
FILE: python/packages/devui/agent_framework_devui/models/_discovery_models.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Discovery API models for entity information."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EnvVarRequirement(BaseModel):
    """Environment variable requirement for an entity."""

    name: str
    description: str
    required: bool = True
    example: str | None = None


class EntityInfo(BaseModel):
    """Entity information for discovery and detailed views."""

    # Always present (core entity data)
    id: str
    type: str  # "agent", "workflow"
    name: str
    description: str | None = None
    framework: str
    tools: list[str | dict[str, Any]] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Source information
    source: str = "directory"  # "directory", "in_memory", "remote_gallery"
    original_url: str | None = None

    # Environment variable requirements
    required_env_vars: list[EnvVarRequirement] | None = None

    # Agent-specific fields (optional, populated when available)
    instructions: str | None = None
    model: str | None = None
    chat_client_type: str | None = None
    context_providers: list[str] | None = None
    middleware: list[str] | None = None

    # Workflow-specific fields (populated only for detailed info requests)
    executors: list[str] | None = None
    workflow_dump: dict[str, Any] | None = None
    input_schema: dict[str, Any] | None = None
    input_type_name: str | None = None
    start_executor_id: str | None = None


class DiscoveryResponse(BaseModel):
    """Response model for entity discovery."""

    entities: list[EntityInfo] = Field(default_factory=list)



================================================
FILE: python/packages/devui/agent_framework_devui/models/_openai_custom.py
================================================
# Copyright (c) Microsoft. All rights reserved.

"""Custom OpenAI-compatible event types for Agent Framework extensions.

These are custom event types that extend beyond the standard OpenAI Responses API
to support Agent Framework specific features like workflows, traces, and function results.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

# Custom Agent Framework OpenAI event types for structured data


class ResponseWorkflowEventDelta(BaseModel):
    """Structured workflow event with completion tracking."""

    type: Literal["response.workflow_event.delta"] = "response.workflow_event.delta"
    delta: dict[str, Any]
    executor_id: str | None = None
    is_complete: bool = False  # Track if this is the final part
    item_id: str
    output_index: int = 0
    sequence_number: int


class ResponseWorkflowEventComplete(BaseModel):
    """Complete workflow event data."""

    type: Literal["response.workflow_event.complete"] = "response.workflow_event.complete"
    data: dict[str, Any]  # Complete event data, not delta
    executor_id: str | None = None
    item_id: str
    output_index: int = 0
    sequence_number: int


class ResponseFunctionResultDelta(BaseModel):
    """Structured function result with completion tracking."""

    type: Literal["response.function_result.delta"] = "response.function_result.delta"
    delta: dict[str, Any]
    call_id: str
    is_complete: bool = False
    item_id: str
    output_index: int = 0
    sequence_number: int


class ResponseFunctionResultComplete(BaseModel):
    """Complete function result data."""

    type: Literal["response.function_result.complete"] = "response.function_result.complete"
    data: dict[str, Any]  # Complete function result data, not delta
    call_id: str
    item_id: str
    output_index: int = 0
    sequence_number: int


class ResponseTraceEventDelta(BaseModel):
    """Structured trace event with completion tracking."""

    type: Literal["response.trace.delta"] = "response.trace.delta"
    delta: dict[str, Any]
    span_id: str | None = None
    is_complete: bool = False
    item_id: str
    output_index: int = 0
    sequence_number: int


class ResponseTraceEventComplete(BaseModel):
    """Complete trace event data."""

    type: Literal["response.trace.complete"] = "response.trace.complete"
    data: dict[str, Any]  # Complete trace data, not delta
    span_id: str | None = None
    item_id: str
    output_index: int = 0
    sequence_number: int


class ResponseUsageEventDelta(BaseModel):
    """Structured usage event with completion tracking."""

    type: Literal["response.usage.delta"] = "response.usage.delta"
    delta: dict[str, Any]
    is_complete: bool = False
    item_id: str
    output_index: int = 0
    sequence_number: int


class ResponseUsageEventComplete(BaseModel):
    """Complete usage event data."""

    type: Literal["response.usage.complete"] = "response.usage.complete"
    data: dict[str, Any]  # Complete usage data, not delta
    item_id: str
    output_index: int = 0
    sequence_number: int


# Agent Framework extension fields
class AgentFrameworkExtraBody(BaseModel):
    """Agent Framework specific routing fields for OpenAI requests."""

    entity_id: str
    thread_id: str | None = None
    input_data: dict[str, Any] | None = None

    model_config = ConfigDict(extra="allow")


# Agent Framework Request Model - Extending real OpenAI types
class AgentFrameworkRequest(BaseModel):
    """OpenAI ResponseCreateParams with Agent Framework extensions.

    This properly extends the real OpenAI API request format while adding
    our custom routing fields in extra_body.
    """

    # All OpenAI fields from ResponseCreateParams
    model: str
    input: str | list[Any]  # ResponseInputParam
    stream: bool | None = False

    # Common OpenAI optional fields
    instructions: str | None = None
    metadata: dict[str, Any] | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    tools: list[dict[str, Any]] | None = None

    # Agent Framework extension - strongly typed
    extra_body: AgentFrameworkExtraBody | None = None

    entity_id: str | None = None  # Allow entity_id as top-level field

    model_config = ConfigDict(extra="allow")

    def get_entity_id(self) -> str | None:
        """Get entity_id from either top-level field or extra_body."""
        # Priority 1: Top-level entity_id field
        if self.entity_id:
            return self.entity_id

        # Priority 2: entity_id in extra_body
        if self.extra_body and hasattr(self.extra_body, "entity_id"):
            return self.extra_body.entity_id

        return None

    def to_openai_params(self) -> dict[str, Any]:
        """Convert to dict for OpenAI client compatibility."""
        data = self.model_dump(exclude={"extra_body", "entity_id"}, exclude_none=True)
        if self.extra_body:
            # Don't merge extra_body into main params to keep them separate
            data["extra_body"] = self.extra_body
        return data


# Error handling
class ResponseTraceEvent(BaseModel):
    """Trace event for execution tracing."""

    type: Literal["trace_event"] = "trace_event"
    data: dict[str, Any]
    timestamp: str


class OpenAIError(BaseModel):
    """OpenAI standard error response model."""

    error: dict[str, Any]

    @classmethod
    def create(cls, message: str, type: str = "invalid_request_error", code: str | None = None) -> OpenAIError:
        """Create a standard OpenAI error response."""
        error_data = {"message": message, "type": type, "code": code}
        return cls(error=error_data)

    def to_dict(self) -> dict[str, Any]:
        """Return the error payload as a plain mapping."""
        return {"error": dict(self.error)}

    def to_json(self) -> str:
        """Return the error payload serialized to JSON."""
        return self.model_dump_json()


# Export all custom types
__all__ = [
    "AgentFrameworkRequest",
    "OpenAIError",
    "ResponseFunctionResultComplete",
    "ResponseFunctionResultDelta",
    "ResponseTraceEvent",
    "ResponseTraceEventComplete",
    "ResponseTraceEventDelta",
    "ResponseUsageEventComplete",
    "ResponseUsageEventDelta",
    "ResponseWorkflowEventComplete",
    "ResponseWorkflowEventDelta",
]



================================================
FILE: python/packages/devui/agent_framework_devui/ui/index.html
================================================
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/agentframework.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Agent Framework Dev UI</title>
    <script type="module" crossorigin src="/assets/index-D0SfShuZ.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index-WsCIE0bH.css">
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>



================================================
FILE: python/packages/devui/frontend/README.md
================================================
# DevUI Frontend

## Build Instructions

```bash
cd frontend
yarn install

# Create .env.local with backend URL
echo 'VITE_API_BASE_URL=http://localhost:8000' > .env.local

# Create .env.production (empty for relative URLs)
echo '' > .env.production

# Development
yarn dev

# Build (copies to backend)
yarn build
```

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      ...tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      ...tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      ...tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```



================================================
FILE: python/packages/devui/frontend/components.json
================================================
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/index.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "iconLibrary": "lucide"
}


================================================
FILE: python/packages/devui/frontend/eslint.config.js
================================================
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { globalIgnores } from 'eslint/config'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
  },
])



================================================
FILE: python/packages/devui/frontend/index.html
================================================
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/agentframework.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Agent Framework Dev UI</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>



================================================
FILE: python/packages/devui/frontend/package.json
================================================
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@radix-ui/react-checkbox": "^1.3.3",
    "@radix-ui/react-dropdown-menu": "^2.1.16",
    "@radix-ui/react-label": "^2.1.7",
    "@radix-ui/react-scroll-area": "^1.2.10",
    "@radix-ui/react-select": "^2.2.6",
    "@radix-ui/react-slot": "^1.2.3",
    "@radix-ui/react-tabs": "^1.1.13",
    "@tailwindcss/vite": "^4.1.12",
    "@xyflow/react": "^12.8.4",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "lucide-react": "^0.540.0",
    "next-themes": "^0.4.6",
    "react": "^19.1.1",
    "react-dom": "^19.1.1",
    "tailwind-merge": "^3.3.1",
    "tailwindcss": "^4.1.12"
  },
  "devDependencies": {
    "@eslint/js": "^9.33.0",
    "@types/node": "^24.3.0",
    "@types/react": "^19.1.10",
    "@types/react-dom": "^19.1.7",
    "@vitejs/plugin-react": "^5.0.0",
    "eslint": "^9.33.0",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.20",
    "globals": "^16.3.0",
    "tw-animate-css": "^1.3.7",
    "typescript": "~5.8.3",
    "typescript-eslint": "^8.39.1",
    "vite": "^7.1.5"
  }
}



================================================
FILE: python/packages/devui/frontend/tsconfig.app.json
================================================
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    },

    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",

    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "erasableSyntaxOnly": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["src"]
}



================================================
FILE: python/packages/devui/frontend/tsconfig.json
================================================
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ],
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}



================================================
FILE: python/packages/devui/frontend/tsconfig.node.json
================================================
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",
    "target": "ES2023",
    "lib": ["ES2023"],
    "module": "ESNext",
    "skipLibCheck": true,

    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,

    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "erasableSyntaxOnly": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["vite.config.ts"]
}



================================================
FILE: python/packages/devui/frontend/vite.config.ts
================================================
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "../agent_framework_devui/ui",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        // Minimize to just 2 files: main app + CSS
        manualChunks: undefined,
        // Ensure everything goes into a single JS file
        inlineDynamicImports: true,
      },
    },
  },
  // Ensure proper tree-shaking
  optimizeDeps: {
    include: ["lucide-react", "@xyflow/react"],
  },
  // Enable aggressive tree-shaking
  esbuild: {
    treeShaking: true,
  },
});



================================================
FILE: python/packages/devui/frontend/src/App.css
================================================
#root {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.react:hover {
  filter: drop-shadow(0 0 2em #61dafbaa);
}

@keyframes logo-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: no-preference) {
  a:nth-of-type(2) .logo {
    animation: logo-spin infinite 20s linear;
  }
}

.card {
  padding: 2em;
}

.read-the-docs {
  color: #888;
}



================================================
FILE: python/packages/devui/frontend/src/App.tsx
================================================
/**
 * DevUI App - Minimal orchestrator for agent/workflow interactions
 * Features: Entity selection, layout management, debug coordination
 */

import { useState, useEffect, useCallback } from "react";
import { AppHeader } from "@/components/shared/app-header";
import { DebugPanel } from "@/components/shared/debug-panel";
import { SettingsModal } from "@/components/shared/settings-modal";
import { GalleryView } from "@/components/gallery";
import { AgentView } from "@/components/agent/agent-view";
import { WorkflowView } from "@/components/workflow/workflow-view";
import { LoadingState } from "@/components/ui/loading-state";
import { Toast } from "@/components/ui/toast";
import { apiClient } from "@/services/api";
import { PanelRightOpen, ChevronDown, ServerOff } from "lucide-react";
import type { SampleEntity } from "@/data/gallery";
import type {
  AgentInfo,
  WorkflowInfo,
  AppState,
  ExtendedResponseStreamEvent,
} from "@/types";
import { Button } from "./components/ui/button";

export default function App() {
  const [appState, setAppState] = useState<AppState>({
    agents: [],
    workflows: [],
    isLoading: true,
  });

  const [debugEvents, setDebugEvents] = useState<ExtendedResponseStreamEvent[]>(
    []
  );
  const [showDebugPanel, setShowDebugPanel] = useState(() => {
    const saved = localStorage.getItem("showDebugPanel");
    return saved !== null ? saved === "true" : true;
  });
  const [debugPanelWidth, setDebugPanelWidth] = useState(() => {
    const savedWidth = localStorage.getItem("debugPanelWidth");
    return savedWidth ? parseInt(savedWidth, 10) : 320;
  });
  const [isResizing, setIsResizing] = useState(false);
  const [showAboutModal, setShowAboutModal] = useState(false);
  const [showGallery, setShowGallery] = useState(false);
  const [addingEntityId, setAddingEntityId] = useState<string | null>(null);
  const [errorEntityId, setErrorEntityId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showEntityNotFoundToast, setShowEntityNotFoundToast] = useState(false);

  // Initialize app - load agents and workflows
  useEffect(() => {
    const loadData = async () => {
      try {
        const [agents, workflows] = await Promise.all([
          apiClient.getAgents(),
          apiClient.getWorkflows(),
        ]);

        // Check if there's an entity_id in the URL
        const urlParams = new URLSearchParams(window.location.search);
        const entityId = urlParams.get("entity_id");

        let selectedAgent: AgentInfo | WorkflowInfo | undefined;

        // Try to find entity from URL parameter first
        if (entityId) {
          selectedAgent =
            agents.find((a) => a.id === entityId) ||
            workflows.find((w) => w.id === entityId);

          // If entity not found but was requested, show notification
          if (!selectedAgent) {
            setShowEntityNotFoundToast(true);
          }
        }

        // Fallback to first available entity if URL entity not found
        if (!selectedAgent) {
          selectedAgent =
            agents.length > 0
              ? agents[0]
              : workflows.length > 0
              ? workflows[0]
              : undefined;

          // Update URL to match actual selected entity (or clear if none)
          if (selectedAgent) {
            const url = new URL(window.location.href);
            url.searchParams.set("entity_id", selectedAgent.id);
            window.history.replaceState({}, "", url);
          } else {
            // Clear entity_id if no entities available
            const url = new URL(window.location.href);
            url.searchParams.delete("entity_id");
            window.history.replaceState({}, "", url);
          }
        }

        setAppState((prev) => ({
          ...prev,
          agents,
          workflows,
          selectedAgent,
          isLoading: false,
        }));
      } catch (error) {
        console.error("Failed to load agents/workflows:", error);
        setAppState((prev) => ({
          ...prev,
          error: error instanceof Error ? error.message : "Failed to load data",
          isLoading: false,
        }));
      }
    };

    loadData();
  }, []);

  // Save debug panel state to localStorage
  useEffect(() => {
    localStorage.setItem("showDebugPanel", showDebugPanel.toString());
  }, [showDebugPanel]);

  useEffect(() => {
    localStorage.setItem("debugPanelWidth", debugPanelWidth.toString());
  }, [debugPanelWidth]);

  // Handle resize drag
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      setIsResizing(true);

      const startX = e.clientX;
      const startWidth = debugPanelWidth;

      const handleMouseMove = (e: MouseEvent) => {
        const deltaX = startX - e.clientX; // Subtract because we're dragging from right
        const newWidth = Math.max(
          200,
          Math.min(window.innerWidth * 0.5, startWidth + deltaX)
        );
        setDebugPanelWidth(newWidth);
      };

      const handleMouseUp = () => {
        setIsResizing(false);
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
      };

      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    },
    [debugPanelWidth]
  );

  // Handle entity selection
  const handleEntitySelect = useCallback((item: AgentInfo | WorkflowInfo) => {
    setAppState((prev) => ({
      ...prev,
      selectedAgent: item,
      currentThread: undefined,
    }));

    // Update URL with selected entity ID
    const url = new URL(window.location.href);
    url.searchParams.set("entity_id", item.id);
    window.history.pushState({}, "", url);

    // Clear debug events when switching entities
    setDebugEvents([]);
  }, []);

  // Handle debug events from active view
  const handleDebugEvent = useCallback(
    (event: ExtendedResponseStreamEvent | "clear") => {
      if (event === "clear") {
        setDebugEvents([]);
      } else {
        setDebugEvents((prev) => [...prev, event]);
      }
    },
    []
  );

  // Handle adding sample entity
  const handleAddSample = useCallback(async (sample: SampleEntity) => {
    setAddingEntityId(sample.id);
    setErrorEntityId(null);
    setErrorMessage(null);

    try {
      // Call backend to fetch and add entity
      const newEntity = await apiClient.addEntity(sample.url, {
        source: "remote_gallery",
        originalUrl: sample.url,
        sampleId: sample.id,
      });

      // Convert backend entity to frontend format
      const convertedEntity = {
        id: newEntity.id,
        name: newEntity.name,
        description: newEntity.description,
        type: newEntity.type,
        source:
          (newEntity.source as "directory" | "in_memory" | "remote_gallery") ||
          "remote_gallery",
        has_env: false,
        module_path: undefined,
      };

      // Update app state
      if (newEntity.type === "agent") {
        const agentEntity = {
          ...convertedEntity,
          tools: (newEntity.tools || []).map((tool) =>
            typeof tool === "string" ? tool : JSON.stringify(tool)
          ),
        } as AgentInfo;

        setAppState((prev) => ({
          ...prev,
          agents: [...prev.agents, agentEntity],
          selectedAgent: agentEntity,
        }));

        // Update URL with new entity
        const url = new URL(window.location.href);
        url.searchParams.set("entity_id", agentEntity.id);
        window.history.pushState({}, "", url);
      } else {
        const workflowEntity = {
          ...convertedEntity,
          executors: (newEntity.tools || []).map((tool) =>
            typeof tool === "string" ? tool : JSON.stringify(tool)
          ),
          input_schema: { type: "string" },
          input_type_name: "Input",
          start_executor_id:
            newEntity.tools && newEntity.tools.length > 0
              ? typeof newEntity.tools[0] === "string"
                ? newEntity.tools[0]
                : JSON.stringify(newEntity.tools[0])
              : "unknown",
        } as WorkflowInfo;

        setAppState((prev) => ({
          ...prev,
          workflows: [...prev.workflows, workflowEntity],
          selectedAgent: workflowEntity,
        }));

        // Update URL with new entity
        const url = new URL(window.location.href);
        url.searchParams.set("entity_id", workflowEntity.id);
        window.history.pushState({}, "", url);
      }

      // Close gallery and clear debug events
      setShowGallery(false);
      setDebugEvents([]);
    } catch (error) {
      const errMsg =
        error instanceof Error ? error.message : "Failed to add sample entity";
      console.error("Failed to add sample entity:", errMsg);
      setErrorEntityId(sample.id);
      setErrorMessage(errMsg);
    } finally {
      setAddingEntityId(null);
    }
  }, []);

  const handleClearError = useCallback(() => {
    setErrorEntityId(null);
    setErrorMessage(null);
  }, []);

  // Handle removing entity
  const handleRemoveEntity = useCallback(
    async (entityId: string) => {
      try {
        await apiClient.removeEntity(entityId);

        // Update app state
        setAppState((prev) => ({
          ...prev,
          agents: prev.agents.filter((a) => a.id !== entityId),
          workflows: prev.workflows.filter((w) => w.id !== entityId),
          selectedAgent:
            prev.selectedAgent?.id === entityId
              ? undefined
              : prev.selectedAgent,
        }));

        // Update URL - clear entity_id if we removed the selected entity
        if (appState.selectedAgent?.id === entityId) {
          const url = new URL(window.location.href);
          url.searchParams.delete("entity_id");
          window.history.pushState({}, "", url);
          setDebugEvents([]);
        }
      } catch (error) {
        console.error("Failed to remove entity:", error);
      }
    },
    [appState.selectedAgent?.id]
  );

  // Show loading state while initializing
  if (appState.isLoading) {
    return (
      <div className="h-screen flex flex-col bg-background">
        {/* Top Bar - Skeleton */}
        <header className="flex h-14 items-center gap-4 border-b px-4">
          <div className="w-64 h-9 bg-muted animate-pulse rounded-md" />
          <div className="flex items-center gap-2 ml-auto">
            <div className="w-8 h-8 bg-muted animate-pulse rounded-md" />
            <div className="w-8 h-8 bg-muted animate-pulse rounded-md" />
          </div>
        </header>

        {/* Loading Content */}
        <LoadingState
          message="Initializing DevUI..."
          description="Loading agents and workflows from your configuration"
          fullPage={true}
        />
      </div>
    );
  }

  // Show error state if loading failed
  if (appState.error) {
    return (
      <div className="h-screen flex flex-col bg-background">
        <AppHeader
          agents={[]}
          workflows={[]}
          selectedItem={undefined}
          onSelect={() => {}}
          onRemove={handleRemoveEntity}
          isLoading={false}
          onSettingsClick={() => setShowAboutModal(true)}
        />

        {/* Error Content */}
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center space-y-6 max-w-2xl">
            {/* Icon */}
            <div className="flex justify-center">
              <div className="rounded-full bg-muted p-4 animate-pulse">
                <ServerOff className="h-12 w-12 text-muted-foreground" />
              </div>
            </div>

            {/* Heading */}
            <div className="space-y-2">
              <h2 className="text-2xl font-semibold text-foreground">
                Can't Connect to Backend
              </h2>
              <p className="text-muted-foreground text-base">
                No worries! Just start the DevUI backend server and you'll be
                good to go.
              </p>
            </div>

            {/* Command Instructions */}
            <div className="space-y-3">
              <div className="text-left bg-muted/50 rounded-lg p-4 space-y-3">
                <p className="text-sm font-medium text-foreground">
                  Start the backend:
                </p>
                <code className="block bg-background px-3 py-2 rounded border text-sm font-mono text-foreground">
                  devui ./agents --port 8080
                </code>
                <p className="text-xs text-muted-foreground">
                  Or launch programmatically with{" "}
                  <code className="text-xs">serve(entities=[agent])</code>
                </p>
              </div>

              <p className="text-xs text-muted-foreground">
                Default:{" "}
                <span className="font-mono">http://localhost:8080</span>
              </p>
            </div>

            {/* Error Details (Collapsible) */}
            {appState.error && (
              <details className="text-left group">
                <summary className="text-sm text-muted-foreground cursor-pointer hover:text-foreground flex items-center gap-2">
                  <ChevronDown className="h-4 w-4 transition-transform group-open:rotate-180" />
                  Error details
                </summary>
                <p className="mt-2 text-xs text-muted-foreground font-mono bg-muted/30 p-3 rounded border">
                  {appState.error}
                </p>
              </details>
            )}

            {/* Retry Button */}
            <Button
              onClick={() => window.location.reload()}
              variant="default"
              className="mt-2"
            >
              Retry Connection
            </Button>
          </div>
        </div>

        {/* Settings Modal */}
        <SettingsModal open={showAboutModal} onOpenChange={setShowAboutModal} />
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-background max-h-screen">
      <AppHeader
        agents={appState.agents}
        workflows={appState.workflows}
        selectedItem={appState.selectedAgent}
        onSelect={handleEntitySelect}
        onRemove={handleRemoveEntity}
        onBrowseGallery={() => setShowGallery(true)}
        isLoading={appState.isLoading}
        onSettingsClick={() => setShowAboutModal(true)}
      />

      {/* Main Content - Split Panel or Gallery */}
      <div className="flex flex-1 overflow-hidden">
        {showGallery ? (
          // Show gallery full screen (w-full ensures it takes entire width)
          <div className="flex-1 w-full">
            <GalleryView
              variant="route"
              onAdd={handleAddSample}
              addingEntityId={addingEntityId}
              errorEntityId={errorEntityId}
              errorMessage={errorMessage}
              onClearError={handleClearError}
              onClose={() => setShowGallery(false)}
              hasExistingEntities={
                appState.agents.length > 0 || appState.workflows.length > 0
              }
            />
          </div>
        ) : appState.agents.length === 0 && appState.workflows.length === 0 ? (
          // Empty state - show gallery inline (full width, no debug panel)
          <GalleryView
            variant="inline"
            onAdd={handleAddSample}
            addingEntityId={addingEntityId}
            errorEntityId={errorEntityId}
            errorMessage={errorMessage}
            onClearError={handleClearError}
          />
        ) : (
          <>
            {/* Left Panel - Main View */}
            <div className="flex-1 min-w-0">
              {appState.selectedAgent ? (
                appState.selectedAgent.type === "agent" ? (
                  <AgentView
                    selectedAgent={appState.selectedAgent as AgentInfo}
                    onDebugEvent={handleDebugEvent}
                  />
                ) : (
                  <WorkflowView
                    selectedWorkflow={appState.selectedAgent as WorkflowInfo}
                    onDebugEvent={handleDebugEvent}
                  />
                )
              ) : (
                <div className="flex-1 flex items-center justify-center text-muted-foreground">
                  Select an agent or workflow to get started.
                </div>
              )}
            </div>

            {showDebugPanel ? (
              <>
                {/* Resize Handle */}
                <div
                  className={`w-1 cursor-col-resize flex-shrink-0 relative group transition-colors duration-200 ease-in-out ${
                    isResizing ? "bg-primary/40" : "bg-border hover:bg-primary/20"
                  }`}
                  onMouseDown={handleMouseDown}
                >
                  <div className="absolute inset-y-0 -left-2 -right-2 flex items-center justify-center">
                    <div
                      className={`h-12 w-1 rounded-full transition-all duration-200 ease-in-out ${
                        isResizing
                          ? "bg-primary shadow-lg shadow-primary/25"
                          : "bg-primary/30 group-hover:bg-primary group-hover:shadow-md group-hover:shadow-primary/20"
                      }`}
                    ></div>
                  </div>
                </div>

                {/* Right Panel - Debug */}
                <div
                  className="flex-shrink-0"
                  style={{ width: `${debugPanelWidth}px` }}
                >
                  <DebugPanel
                    events={debugEvents}
                    isStreaming={false} // Each view manages its own streaming state
                    onClose={() => setShowDebugPanel(false)}
                  />
                </div>
              </>
            ) : (
              /* Button to reopen when closed */
              <div className="flex-shrink-0">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowDebugPanel(true)}
                  className="h-full w-10 rounded-none border-l"
                  title="Show debug panel"
                >
                  <PanelRightOpen className="h-4 w-4" />
                </Button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Settings Modal */}
      <SettingsModal open={showAboutModal} onOpenChange={setShowAboutModal} />

      {/* Toast Notification */}
      {showEntityNotFoundToast && (
        <Toast
          message="Entity not found. Showing first available entity instead."
          type="info"
          onClose={() => setShowEntityNotFoundToast(false)}
        />
      )}
    </div>
  );
}



================================================
FILE: python/packages/devui/frontend/src/index.css
================================================
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

@theme inline {
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);
}

:root {
  --radius: 0.625rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.48 0.18 290);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --chart-1: oklch(0.646 0.222 41.116);
  --chart-2: oklch(0.6 0.118 184.704);
  --chart-3: oklch(0.398 0.07 227.392);
  --chart-4: oklch(0.828 0.189 84.429);
  --chart-5: oklch(0.769 0.188 70.08);
  --sidebar: oklch(0.985 0 0);
  --sidebar-foreground: oklch(0.145 0 0);
  --sidebar-primary: oklch(0.205 0 0);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.97 0 0);
  --sidebar-accent-foreground: oklch(0.205 0 0);
  --sidebar-border: oklch(0.922 0 0);
  --sidebar-ring: oklch(0.708 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.62 0.20 290);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);
  --chart-1: oklch(0.488 0.243 264.376);
  --chart-2: oklch(0.696 0.17 162.48);
  --chart-3: oklch(0.769 0.188 70.08);
  --chart-4: oklch(0.627 0.265 303.9);
  --chart-5: oklch(0.645 0.246 16.439);
  --sidebar: oklch(0.205 0 0);
  --sidebar-foreground: oklch(0.985 0 0);
  --sidebar-primary: oklch(0.488 0.243 264.376);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.269 0 0);
  --sidebar-accent-foreground: oklch(0.985 0 0);
  --sidebar-border: oklch(1 0 0 / 10%);
  --sidebar-ring: oklch(0.556 0 0);
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}

/* Mermaid diagram styles removed - visualization coming soon */

/* Style workflow completion/error states */
.workflow-chat-view .border-green-200 {
  @apply border-emerald-200;
}

.workflow-chat-view .bg-green-50 {
  @apply bg-emerald-50;
}

.workflow-chat-view .bg-green-100 {
  @apply bg-emerald-100;
}

.workflow-chat-view .text-green-600 {
  @apply text-emerald-600;
}

.workflow-chat-view .text-green-700 {
  @apply text-emerald-700;
}

.workflow-chat-view .text-green-800 {
  @apply text-emerald-800;
}



================================================
FILE: python/packages/devui/frontend/src/main.tsx
================================================
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ThemeProvider } from "./components/theme-provider"

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      <App />
    </ThemeProvider>
  </StrictMode>,
)



================================================
FILE: python/packages/devui/frontend/src/vite-env.d.ts
================================================
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}



================================================
FILE: python/packages/devui/frontend/src/components/mode-toggle.tsx
================================================
"use client"

import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function ModeToggle() {
  const { setTheme } = useTheme()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}


================================================
FILE: python/packages/devui/frontend/src/components/theme-provider.tsx
================================================
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"

interface ThemeProviderProps {
  children: React.ReactNode
  attribute?: "class" | "data-theme" | "data-mode"
  defaultTheme?: string
  enableSystem?: boolean
  disableTransitionOnChange?: boolean
}

export function ThemeProvider({
  children,
  attribute = "class",
  defaultTheme = "dark",
  enableSystem = true,
  disableTransitionOnChange = true,
  ...props
}: ThemeProviderProps) {
  return (
    <NextThemesProvider
      attribute={attribute}
      defaultTheme={defaultTheme}
      enableSystem={enableSystem}
      disableTransitionOnChange={disableTransitionOnChange}
      {...props}
    >
      {children}
    </NextThemesProvider>
  )
}


================================================
FILE: python/packages/devui/frontend/src/components/agent/agent-view.tsx
================================================
/**
 * AgentView - Complete agent interaction interface
 * Features: Chat interface, message streaming, thread management
 */

import { useState, useCallback, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileUpload } from "@/components/ui/file-upload";
import {
  AttachmentGallery,
  type AttachmentItem,
} from "@/components/ui/attachment-gallery";
import { MessageRenderer } from "@/components/message_renderer";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { AgentDetailsModal } from "@/components/shared/agent-details-modal";
import {
  SendHorizontal,
  User,
  Bot,
  Plus,
  AlertCircle,
  Paperclip,
  Info,
  Trash2,
  FileText,
} from "lucide-react";
import { apiClient } from "@/services/api";
import type {
  AgentInfo,
  ChatMessage,
  RunAgentRequest,
  ThreadInfo,
  ExtendedResponseStreamEvent,
} from "@/types";

interface ChatState {
  messages: ChatMessage[];
  isStreaming: boolean;
}

type DebugEventHandler = (event: ExtendedResponseStreamEvent | "clear") => void;

interface AgentViewProps {
  selectedAgent: AgentInfo;
  onDebugEvent: DebugEventHandler;
}

interface MessageBubbleProps {
  message: ChatMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isError = message.error;
  const Icon = isUser ? User : isError ? AlertCircle : Bot;

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border ${
          isUser
            ? "bg-primary text-primary-foreground"
            : isError
            ? "bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-400 border-orange-200 dark:border-orange-800"
            : "bg-muted"
        }`}
      >
        <Icon className="h-4 w-4" />
      </div>

      <div
        className={`flex flex-col space-y-1 ${
          isUser ? "items-end" : "items-start"
        } max-w-[80%]`}
      >
        <div
          className={`rounded px-3 py-2 text-sm break-all ${
            isUser
              ? "bg-primary text-primary-foreground"
              : isError
              ? "bg-orange-50 dark:bg-orange-950/50 text-orange-800 dark:text-orange-200 border border-orange-200 dark:border-orange-800"
              : "bg-muted"
          }`}
        >
          {isError && (
            <div className="flex items-start gap-2 mb-2">
              <AlertCircle className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
              <span className="font-medium text-sm">
                Unable to process request
              </span>
            </div>
          )}
          <div className={isError ? "text-xs leading-relaxed break-all" : ""}>
            <MessageRenderer
              contents={message.contents}
              isStreaming={message.streaming}
            />
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono">
          <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
          {!isUser && message.usage && (
            <>
              <span>•</span>
              <span className="text-[11px]">
                {message.usage.total_tokens >= 1000
                  ? `${(message.usage.total_tokens / 1000).toFixed(2)}k`
                  : message.usage.total_tokens}{" "}
                tokens
                {message.usage.prompt_tokens > 0 && (
                  <span className="opacity-70">
                    {" "}
                    (
                    {message.usage.prompt_tokens >= 1000
                      ? `${(message.usage.prompt_tokens / 1000).toFixed(1)}k`
                      : message.usage.prompt_tokens}{" "}
                    in,{" "}
                    {message.usage.completion_tokens >= 1000
                      ? `${(message.usage.completion_tokens / 1000).toFixed(1)}k`
                      : message.usage.completion_tokens}{" "}
                    out)
                  </span>
                )}
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-muted">
        <Bot className="h-4 w-4" />
      </div>
      <div className="flex items-center space-x-1 rounded bg-muted px-3 py-2">
        <div className="flex space-x-1">
          <div className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.3s]" />
          <div className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.15s]" />
          <div className="h-2 w-2 animate-bounce rounded-full bg-current" />
        </div>
      </div>
    </div>
  );
}

export function AgentView({ selectedAgent, onDebugEvent }: AgentViewProps) {
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    isStreaming: false,
  });
  const [currentThread, setCurrentThread] = useState<ThreadInfo | undefined>(
    undefined
  );
  const [availableThreads, setAvailableThreads] = useState<ThreadInfo[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [attachments, setAttachments] = useState<AttachmentItem[]>([]);
  const [loadingThreads, setLoadingThreads] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);
  const [pasteNotification, setPasteNotification] = useState<string | null>(
    null
  );
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [threadUsage, setThreadUsage] = useState<{
    total_tokens: number;
    message_count: number;
  }>({ total_tokens: 0, message_count: 0 });

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const accumulatedText = useRef<string>("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const currentMessageUsage = useRef<{
    total_tokens: number;
    prompt_tokens: number;
    completion_tokens: number;
  } | null>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatState.messages, chatState.isStreaming]);

  // Load threads when agent changes
  useEffect(() => {
    const loadThreads = async () => {
      if (!selectedAgent) return;

      setLoadingThreads(true);
      try {
        const threads = await apiClient.getThreads(selectedAgent.id);
        setAvailableThreads(threads);

        // Auto-select the most recent thread if available
        if (threads.length > 0) {
          const mostRecentThread = threads[0]; // Assuming threads are sorted by creation date (newest first)
          setCurrentThread(mostRecentThread);

          // Load messages for the selected thread
          try {
            const threadMessages = await apiClient.getThreadMessages(
              mostRecentThread.id
            );
            setChatState({
              messages: threadMessages,
              isStreaming: false,
            });
          } catch (error) {
            console.error("Failed to load thread messages:", error);
            setChatState({
              messages: [],
              isStreaming: false,
            });
          }
        }
      } catch (error) {
        console.error("Failed to load threads:", error);
        setAvailableThreads([]);
      } finally {
        setLoadingThreads(false);
      }
    };

    // Clear chat when agent changes
    setChatState({
      messages: [],
      isStreaming: false,
    });
    setCurrentThread(undefined);
    accumulatedText.current = "";

    loadThreads();
  }, [selectedAgent]);

  // Handle file uploads
  const handleFilesSelected = async (files: File[]) => {
    const newAttachments: AttachmentItem[] = [];

    for (const file of files) {
      const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const type = getFileType(file);

      let preview: string | undefined;
      if (type === "image") {
        preview = await readFileAsDataURL(file);
      }

      newAttachments.push({
        id,
        file,
        preview,
        type,
      });
    }

    setAttachments((prev) => [...prev, ...newAttachments]);
  };

  const handleRemoveAttachment = (id: string) => {
    setAttachments((prev) => prev.filter((att) => att.id !== id));
  };

  // Drag and drop handlers
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter((prev) => prev + 1);
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const newCounter = dragCounter - 1;
    setDragCounter(newCounter);
    if (newCounter === 0) {
      setIsDragOver(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    setDragCounter(0);

    if (isSubmitting || chatState.isStreaming) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      await handleFilesSelected(files);
    }
  };

  // Paste handler
  const handlePaste = async (e: React.ClipboardEvent) => {
    const items = Array.from(e.clipboardData.items);
    const files: File[] = [];
    let hasProcessedText = false;
    const TEXT_THRESHOLD = 8000; // Convert to file if text is larger than this

    for (const item of items) {
      // Handle pasted images (screenshots)
      if (item.type.startsWith("image/")) {
        e.preventDefault();
        const blob = item.getAsFile();
        if (blob) {
          const timestamp = Date.now();
          files.push(
            new File([blob], `screenshot-${timestamp}.png`, { type: blob.type })
          );
        }
      }
      // Handle text - only process first text item (browsers often duplicate)
      else if (item.type === "text/plain" && !hasProcessedText) {
        hasProcessedText = true;

        // We need to check the text synchronously to decide whether to prevent default
        // Unfortunately, getAsString is async, so we'll prevent default for all text
        // and then decide whether to actually create a file or manually insert the text
        e.preventDefault();

        await new Promise<void>((resolve) => {
          item.getAsString((text) => {
            // Check if text should be converted to file
            const lineCount = (text.match(/\n/g) || []).length;
            const shouldConvert =
              text.length > TEXT_THRESHOLD ||
              lineCount > 50 || // Many lines suggests logs/data
              /^\s*[{[][\s\S]*[}\]]\s*$/.test(text) || // JSON-like
              /^<\?xml|^<html|^<!DOCTYPE/i.test(text); // XML/HTML

            if (shouldConvert) {
              // Create file for large/complex text
              const extension = detectFileExtension(text);
              const timestamp = Date.now();
              const blob = new Blob([text], { type: "text/plain" });
              files.push(
                new File([blob], `pasted-text-${timestamp}${extension}`, {
                  type: "text/plain",
                })
              );
            } else {
              // For small text, manually insert into textarea since we prevented default
              const textarea = textareaRef.current;
              if (textarea) {
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                const currentValue = textarea.value;
                const newValue = currentValue.slice(0, start) + text + currentValue.slice(end);
                setInputValue(newValue);

                // Restore cursor position after the inserted text
                setTimeout(() => {
                  textarea.selectionStart = textarea.selectionEnd = start + text.length;
                  textarea.focus();
                }, 0);
              }
            }
            resolve();
          });
        });
      }
    }

    // Process collected files
    if (files.length > 0) {
      await handleFilesSelected(files);

      // Show notification with appropriate icon
      const message =
        files.length === 1
          ? files[0].name.includes("screenshot")
            ? "Screenshot added as attachment"
            : "Large text converted to file"
          : `${files.length} files added`;

      setPasteNotification(message);
      setTimeout(() => setPasteNotification(null), 3000);
    }
  };

  // Detect file extension from content
  const detectFileExtension = (text: string): string => {
    const trimmed = text.trim();
    const lines = trimmed.split('\n');

    // JSON detection
    if (/^{[\s\S]*}$|^\[[\s\S]*\]$/.test(trimmed)) return ".json";

    // XML/HTML detection
    if (/^<\?xml|^<html|^<!DOCTYPE/i.test(trimmed)) return ".html";

    // Markdown detection (code blocks)
    if (/^```/.test(trimmed)) return ".md";

    // TSV detection (tabs with multiple lines)
    if (/\t/.test(text) && lines.length > 1) return ".tsv";

    // CSV detection (more strict) - need multiple lines with consistent comma patterns
    if (lines.length > 2) {
      const commaLines = lines.filter(line => line.includes(','));
      const semicolonLines = lines.filter(line => line.includes(';'));

      // If >50% of lines have commas and it looks tabular
      if (commaLines.length > lines.length * 0.5) {
        const avgCommas = commaLines.reduce((sum, line) => sum + (line.match(/,/g) || []).length, 0) / commaLines.length;
        if (avgCommas >= 2) return ".csv";
      }

      // If >50% of lines have semicolons and it looks tabular
      if (semicolonLines.length > lines.length * 0.5) {
        const avgSemicolons = semicolonLines.reduce((sum, line) => sum + (line.match(/;/g) || []).length, 0) / semicolonLines.length;
        if (avgSemicolons >= 2) return ".csv";
      }
    }

    return ".txt";
  };

  // Helper functions
  const getFileType = (file: File): AttachmentItem["type"] => {
    if (file.type.startsWith("image/")) return "image";
    if (file.type === "application/pdf") return "pdf";
    if (file.type.startsWith("audio/")) return "audio";
    return "other";
  };

  const readFileAsDataURL = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  // Handle new thread creation
  const handleNewThread = useCallback(async () => {
    if (!selectedAgent) return;

    try {
      const newThread = await apiClient.createThread(selectedAgent.id);
      setCurrentThread(newThread);
      setAvailableThreads((prev) => [newThread, ...prev]);
      setChatState({
        messages: [],
        isStreaming: false,
      });
      setThreadUsage({ total_tokens: 0, message_count: 0 });
      accumulatedText.current = "";
    } catch (error) {
      console.error("Failed to create thread:", error);
    }
  }, [selectedAgent]);

  // Handle thread deletion
  const handleDeleteThread = useCallback(
    async (threadId: string, e?: React.MouseEvent) => {
      // Prevent event from bubbling to SelectItem
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }

      // Confirm deletion
      if (!confirm("Delete this thread? This cannot be undone.")) {
        return;
      }

      try {
        const success = await apiClient.deleteThread(threadId);
        if (success) {
          // Remove thread from available threads
          const updatedThreads = availableThreads.filter((t) => t.id !== threadId);
          setAvailableThreads(updatedThreads);

          // If deleted thread was selected, switch to another thread or clear chat
          if (currentThread?.id === threadId) {
            if (updatedThreads.length > 0) {
              // Select the most recent remaining thread
              const nextThread = updatedThreads[0];
              setCurrentThread(nextThread);

              // Load messages for the next thread
              try {
                const threadMessages = await apiClient.getThreadMessages(nextThread.id);
                setChatState({
                  messages: threadMessages,
                  isStreaming: false,
                });
              } catch (error) {
                console.error("Failed to load thread messages:", error);
                setChatState({
                  messages: [],
                  isStreaming: false,
                });
              }
            } else {
              // No threads left, clear everything
              setCurrentThread(undefined);
              setChatState({
                messages: [],
                isStreaming: false,
              });
              setThreadUsage({ total_tokens: 0, message_count: 0 });
              accumulatedText.current = "";
            }
          }

          // Clear debug panel
          onDebugEvent("clear");
        }
      } catch (error) {
        console.error("Failed to delete thread:", error);
        alert("Failed to delete thread. Please try again.");
      }
    },
    [availableThreads, currentThread, onDebugEvent]
  );

  // Handle thread selection
  const handleThreadSelect = useCallback(
    async (threadId: string) => {
      const thread = availableThreads.find((t) => t.id === threadId);
      if (!thread) return;

      setCurrentThread(thread);

      // Clear debug panel when switching threads
      onDebugEvent("clear");

      try {
        // Load thread messages from backend
        const threadMessages = await apiClient.getThreadMessages(threadId);

        setChatState({
          messages: threadMessages,
          isStreaming: false,
        });

        // Calculate cumulative usage for this thread
        const totalTokens = threadMessages.reduce(
          (sum, msg) => sum + (msg.usage?.total_tokens || 0),
          0
        );
        const messageCount = threadMessages.filter(
          (msg) => msg.role === "assistant" && msg.usage
        ).length;
        setThreadUsage({ total_tokens: totalTokens, message_count: messageCount });

        console.log(
          `Restored ${threadMessages.length} messages for thread ${threadId}`
        );
      } catch (error) {
        console.error("Failed to load thread messages:", error);
        // Fallback to clearing messages
        setChatState({
          messages: [],
          isStreaming: false,
        });
      }

      accumulatedText.current = "";
    },
    [availableThreads]
  );

  // Handle message sending
  const handleSendMessage = useCallback(
    async (request: RunAgentRequest) => {
      if (!selectedAgent) return;

      // Extract text and attachments from OpenAI format for UI display
      let displayText = "";
      const attachmentContents: import("@/types/agent-framework").Contents[] =
        [];

      // Parse OpenAI ResponseInputParam to extract display content
      for (const inputItem of request.input) {
        if (inputItem.type === "message" && Array.isArray(inputItem.content)) {
          for (const contentItem of inputItem.content) {
            if (contentItem.type === "input_text") {
              displayText += contentItem.text + " ";
            } else if (contentItem.type === "input_image") {
              attachmentContents.push({
                type: "data",
                uri: contentItem.image_url || "",
                media_type: "image/png", // Default, should extract from data URI
              } as import("@/types/agent-framework").DataContent);
            } else if (contentItem.type === "input_file") {
              const dataUri = `data:application/octet-stream;base64,${contentItem.file_data}`;
              // Determine media type from filename
              const filename = (contentItem as import("@/types/agent-framework").ResponseInputFileParam).filename || "";
              let mediaType = "application/octet-stream";

              if (filename.endsWith(".pdf")) mediaType = "application/pdf";
              else if (filename.endsWith(".txt")) mediaType = "text/plain";
              else if (filename.endsWith(".json")) mediaType = "application/json";
              else if (filename.endsWith(".csv")) mediaType = "text/csv";
              else if (filename.endsWith(".html")) mediaType = "text/html";
              else if (filename.endsWith(".md")) mediaType = "text/markdown";

              attachmentContents.push({
                type: "data",
                uri: dataUri,
                media_type: mediaType,
              } as import("@/types/agent-framework").DataContent);
            }
          }
        }
      }

      const userMessageContents: import("@/types/agent-framework").Contents[] =
        [
          ...(displayText.trim()
            ? [
                {
                  type: "text",
                  text: displayText.trim(),
                } as import("@/types/agent-framework").TextContent,
              ]
            : []),
          ...attachmentContents,
        ];

      // Add user message to UI state
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        contents: userMessageContents,
        timestamp: new Date().toISOString(),
      };

      setChatState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isStreaming: true,
      }));

      // Create assistant message placeholder
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        contents: [],
        timestamp: new Date().toISOString(),
        streaming: true,
      };

      setChatState((prev) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
      }));

      try {
        // If no thread selected, create one automatically
        let threadToUse = currentThread;
        if (!threadToUse) {
          try {
            threadToUse = await apiClient.createThread(selectedAgent.id);
            setCurrentThread(threadToUse);
            setAvailableThreads((prev) => [threadToUse!, ...prev]);
          } catch (error) {
            console.error("Failed to create thread:", error);
          }
        }

        const apiRequest = {
          input: request.input,
          thread_id: threadToUse?.id,
        };

        // Clear text accumulator for new response
        accumulatedText.current = "";

        // Clear debug panel events for new agent run
        onDebugEvent("clear");

        // Use OpenAI-compatible API streaming - direct event handling
        const streamGenerator = apiClient.streamAgentExecutionOpenAI(
          selectedAgent.id,
          apiRequest
        );

        for await (const openAIEvent of streamGenerator) {
          // Pass all events to debug panel
          onDebugEvent(openAIEvent);

          // Handle usage events
          if (openAIEvent.type === "response.usage.complete") {
            const usageEvent = openAIEvent as import("@/types").ResponseUsageEventComplete;
            console.log("📊 Usage event received:", usageEvent.data);
            if (usageEvent.data) {
              currentMessageUsage.current = {
                total_tokens: usageEvent.data.total_tokens || 0,
                prompt_tokens: usageEvent.data.prompt_tokens || 0,
                completion_tokens: usageEvent.data.completion_tokens || 0,
              };
              console.log("📊 Set usage:", currentMessageUsage.current);
            }
          }

          // Handle error events from the stream
          if (openAIEvent.type === "error") {
            const errorEvent = openAIEvent as ExtendedResponseStreamEvent & {
              message?: string;
            };
            const errorMessage = errorEvent.message || "An error occurred";

            // Update assistant message with error and stop streaming
            setChatState((prev) => ({
              ...prev,
              isStreaming: false,
              messages: prev.messages.map((msg) =>
                msg.id === assistantMessage.id
                  ? {
                      ...msg,
                      contents: [
                        {
                          type: "text",
                          text: errorMessage,
                        },
                      ],
                      streaming: false,
                      error: true, // Add error flag for styling
                    }
                  : msg
              ),
            }));
            return; // Exit stream processing early on error
          }

          // Handle text delta events for chat
          if (
            openAIEvent.type === "response.output_text.delta" &&
            "delta" in openAIEvent &&
            openAIEvent.delta
          ) {
            accumulatedText.current += openAIEvent.delta;

            // Update assistant message with accumulated content
            setChatState((prev) => ({
              ...prev,
              messages: prev.messages.map((msg) =>
                msg.id === assistantMessage.id
                  ? {
                      ...msg,
                      contents: [
                        {
                          type: "text",
                          text: accumulatedText.current,
                        },
                      ],
                    }
                  : msg
              ),
            }));
          }

          // Handle completion/error by detecting when streaming stops
          // (Server will close the stream when done, so we'll exit the loop naturally)
        }

        // Stream ended - mark as complete and attach usage
        const finalUsage = currentMessageUsage.current;
        console.log("📊 Stream ended, attaching usage to message:", finalUsage);

        setChatState((prev) => ({
          ...prev,
          isStreaming: false,
          messages: prev.messages.map((msg) =>
            msg.id === assistantMessage.id
              ? {
                  ...msg,
                  streaming: false,
                  usage: finalUsage || undefined,
                }
              : msg
          ),
        }));

        // Update thread-level usage stats
        if (finalUsage) {
          setThreadUsage((prev) => ({
            total_tokens: prev.total_tokens + finalUsage.total_tokens,
            message_count: prev.message_count + 1,
          }));
          console.log("📊 Updated thread usage");
        }

        // Reset usage for next message
        currentMessageUsage.current = null;
      } catch (error) {
        console.error("Streaming error:", error);
        setChatState((prev) => ({
          ...prev,
          isStreaming: false,
          messages: prev.messages.map((msg) =>
            msg.id === assistantMessage.id
              ? {
                  ...msg,
                  contents: [
                    {
                      type: "text",
                      text: `Error: ${
                        error instanceof Error
                          ? error.message
                          : "Failed to get response"
                      }`,
                    },
                  ],
                  streaming: false,
                }
              : msg
          ),
        }));
      }
    },
    [selectedAgent, currentThread, onDebugEvent]
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (
      (!inputValue.trim() && attachments.length === 0) ||
      isSubmitting ||
      !selectedAgent
    )
      return;

    setIsSubmitting(true);
    const messageText = inputValue.trim();
    setInputValue("");

    try {
      // Create OpenAI Responses API format
      if (attachments.length > 0 || messageText) {
        const content: import("@/types/agent-framework").ResponseInputContent[] =
          [];

        // Add text content if present - EXACT OpenAI ResponseInputTextParam
        if (messageText) {
          content.push({
            text: messageText,
            type: "input_text",
          } as import("@/types/agent-framework").ResponseInputTextParam);
        }

        // Add attachments using EXACT OpenAI types
        for (const attachment of attachments) {
          const dataUri = await readFileAsDataURL(attachment.file);

          if (attachment.file.type.startsWith("image/")) {
            // EXACT OpenAI ResponseInputImageParam
            content.push({
              detail: "auto",
              type: "input_image",
              image_url: dataUri,
            } as import("@/types/agent-framework").ResponseInputImageParam);
          } else if (
            attachment.file.type === "text/plain" &&
            (attachment.file.name.includes("pasted-text-") ||
             attachment.file.name.endsWith(".txt") ||
             attachment.file.name.endsWith(".csv") ||
             attachment.file.name.endsWith(".json") ||
             attachment.file.name.endsWith(".html") ||
             attachment.file.name.endsWith(".md") ||
             attachment.file.name.endsWith(".tsv"))
          ) {
            // Convert all text files (from pasted large text) back to input_text
            const text = await attachment.file.text();
            content.push({
              text: text,
              type: "input_text",
            } as import("@/types/agent-framework").ResponseInputTextParam);
          } else {
            // EXACT OpenAI ResponseInputFileParam for other files
            const base64Data = dataUri.split(",")[1]; // Extract base64 part
            content.push({
              type: "input_file",
              file_data: base64Data,
              file_url: dataUri, // Use data URI as the URL
              filename: attachment.file.name,
            } as import("@/types/agent-framework").ResponseInputFileParam);
          }
        }

        const openaiInput: import("@/types/agent-framework").ResponseInputParam =
          [
            {
              type: "message",
              role: "user",
              content,
            },
          ];

        // Use pure OpenAI format
        await handleSendMessage({
          input: openaiInput,
          thread_id: currentThread?.id,
        });
      } else {
        // Simple text message using OpenAI format
        const openaiInput: import("@/types/agent-framework").ResponseInputParam =
          [
            {
              type: "message",
              role: "user",
              content: [
                {
                  text: messageText,
                  type: "input_text",
                } as import("@/types/agent-framework").ResponseInputTextParam,
              ],
            },
          ];

        await handleSendMessage({
          input: openaiInput,
          thread_id: currentThread?.id,
        });
      }

      // Clear attachments after sending
      setAttachments([]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const canSendMessage =
    selectedAgent &&
    !isSubmitting &&
    !chatState.isStreaming &&
    (inputValue.trim() || attachments.length > 0);

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      {/* Header */}
      <div className="border-b pb-2  p-4 flex-shrink-0">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 min-w-0">
            <h2 className="font-semibold text-sm truncate">
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4 flex-shrink-0" />
                <span className="truncate">Chat with {selectedAgent.name || selectedAgent.id}</span>
              </div>
            </h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setDetailsModalOpen(true)}
              className="h-6 w-6 p-0 flex-shrink-0"
              title="View agent details"
            >
              <Info className="h-4 w-4" />
            </Button>
          </div>

          {/* Thread Controls */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 flex-shrink-0">
            <Select
              value={currentThread?.id || ""}
              onValueChange={handleThreadSelect}
              disabled={loadingThreads || isSubmitting}
            >
              <SelectTrigger className="w-full sm:w-64">
                <SelectValue
                  placeholder={
                    loadingThreads
                      ? "Loading..."
                      : availableThreads.length === 0
                      ? "No threads"
                      : currentThread
                      ? `Thread ${currentThread.id.slice(-8)}`
                      : "Select thread"
                  }
                >
                  {currentThread && (
                    <div className="flex items-center gap-2 text-xs">
                      <span>Thread {currentThread.id.slice(-8)}</span>
                      {threadUsage.total_tokens > 0 && (
                        <>
                          <span className="text-muted-foreground">•</span>
                          <span className="text-muted-foreground">
                            {threadUsage.total_tokens >= 1000
                              ? `${(threadUsage.total_tokens / 1000).toFixed(1)}k`
                              : threadUsage.total_tokens}{" "}
                            tokens
                          </span>
                        </>
                      )}
                    </div>
                  )}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {availableThreads.map((thread) => (
                  <SelectItem key={thread.id} value={thread.id}>
                    <div className="flex items-center justify-between w-full">
                      <span>Thread {thread.id.slice(-8)}</span>
                      {thread.created_at && (
                        <span className="text-xs text-muted-foreground ml-3">
                          {new Date(thread.created_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              size="icon"
              onClick={() => currentThread && handleDeleteThread(currentThread.id)}
              disabled={!currentThread || isSubmitting}
              title={currentThread ? `Delete Thread ${currentThread.id.slice(-8)}` : "No thread selected"}
            >
              <Trash2 className="h-4 w-4" />
            </Button>

            <Button
              variant="outline"
              size="lg"
              onClick={handleNewThread}
              disabled={!selectedAgent || isSubmitting}
              className="whitespace-nowrap"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Thread
            </Button>
          </div>
        </div>

        {selectedAgent.description && (
          <p className="text-sm text-muted-foreground">
            {selectedAgent.description}
          </p>
        )}
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4 h-0" ref={scrollAreaRef}>
        <div className="space-y-4">
          {chatState.messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-center">
              <div className="text-muted-foreground text-sm">
                Start a conversation with{" "}
                {selectedAgent.name || selectedAgent.id}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Type a message below to begin
              </div>
            </div>
          ) : (
            chatState.messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))
          )}

          {chatState.isStreaming && !isSubmitting && <TypingIndicator />}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t flex-shrink-0">
        <div
          className={`p-4 relative transition-all duration-300 ease-in-out ${
            isDragOver ? "bg-blue-50 dark:bg-blue-950/20" : ""
          }`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {/* Drag overlay */}
          {isDragOver && (
            <div className="absolute inset-2 border-2 border-dashed border-blue-400 dark:border-blue-500 rounded-lg bg-blue-50/80 dark:bg-blue-950/40 backdrop-blur-sm flex items-center justify-center transition-all duration-200 ease-in-out z-10">
              <div className="text-center">
                <div className="text-blue-600 dark:text-blue-400 text-sm font-medium mb-1">
                  Drop files here
                </div>
                <div className="text-blue-500 dark:text-blue-500 text-xs">
                  Images, PDFs, and other files
                </div>
              </div>
            </div>
          )}

          {/* Attachment gallery */}
          {attachments.length > 0 && (
            <div className="mb-3">
              <AttachmentGallery
                attachments={attachments}
                onRemoveAttachment={handleRemoveAttachment}
              />
            </div>
          )}

          {/* Paste notification */}
          {pasteNotification && (
            <div
              className="absolute bottom-24 left-1/2 -translate-x-1/2 z-20
                          bg-blue-500 text-white px-4 py-2 rounded-full text-sm
                          animate-in slide-in-from-bottom-2 fade-in duration-200
                          flex items-center gap-2 shadow-lg"
            >
              {pasteNotification.includes("screenshot") ? (
                <Paperclip className="h-3 w-3" />
              ) : (
                <FileText className="h-3 w-3" />
              )}
              {pasteNotification}
            </div>
          )}

          {/* Input form */}
          <form onSubmit={handleSubmit} className="flex gap-2 items-end">
            <Textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onPaste={handlePaste}
              onKeyDown={(e) => {
                // Submit on Enter (without shift)
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder={`Message ${
                selectedAgent.name || selectedAgent.id
              }... (Shift+Enter for new line)`}
              disabled={isSubmitting || chatState.isStreaming}
              className="flex-1 min-h-[40px] max-h-[200px] resize-none"
              style={{ fieldSizing: "content" } as React.CSSProperties}
            />
            <FileUpload
              onFilesSelected={handleFilesSelected}
              disabled={isSubmitting || chatState.isStreaming}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!canSendMessage}
              className="shrink-0 h-10"
            >
              {isSubmitting ? (
                <LoadingSpinner size="sm" />
              ) : (
                <SendHorizontal className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </div>

      {/* Agent Details Modal */}
      <AgentDetailsModal
        agent={selectedAgent}
        open={detailsModalOpen}
        onOpenChange={setDetailsModalOpen}
      />
    </div>
  );
}



================================================
FILE: python/packages/devui/frontend/src/components/gallery/gallery-view.tsx
================================================
/**
 * GalleryView - Consolidated gallery component with card and grid logic
 * Supports inline (empty state) and modal variants
 */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Bot,
  Workflow,
  Plus,
  Loader2,
  User,
  TriangleAlert,
  AlertCircle,
  X,
  Key,
  ChevronDown,
  ArrowLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  SAMPLE_ENTITIES,
  type SampleEntity,
  getDifficultyColor,
} from "@/data/gallery";

interface GalleryViewProps {
  onAdd: (sample: SampleEntity) => Promise<void>;
  addingEntityId?: string | null;
  errorEntityId?: string | null;
  errorMessage?: string | null;
  onClearError?: (sampleId: string) => void;
  onClose?: () => void;
  variant?: "inline" | "route" | "modal";
  hasExistingEntities?: boolean;
}

// Internal: Sample Entity Card Component
function SampleEntityCard({
  sample,
  onAdd,
  isAdding = false,
  hasError = false,
  errorMessage,
  onClearError,
}: {
  sample: SampleEntity;
  onAdd: (sample: SampleEntity) => Promise<void>;
  isAdding?: boolean;
  hasError?: boolean;
  errorMessage?: string | null;
  onClearError?: (sampleId: string) => void;
}) {
  const [isLoading, setIsLoading] = useState(false);

  const handleAdd = async () => {
    if (isLoading || isAdding) return;

    setIsLoading(true);
    try {
      await onAdd(sample);
    } finally {
      setIsLoading(false);
    }
  };

  const TypeIcon = sample.type === "workflow" ? Workflow : Bot;
  const isDisabled = isLoading || isAdding;

  return (
    <Card
      className={cn(
        "hover:shadow-md transition-shadow duration-200 h-full flex flex-col overflow-hidden w-full",
        hasError && "border-destructive"
      )}
    >
      <CardHeader className="pb-3 min-w-0">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            <TypeIcon className="h-5 w-5" />
            <Badge variant="secondary" className="text-xs">
              {sample.type}
            </Badge>
          </div>
          <Badge
            variant="outline"
            className={cn(
              "text-xs border",
              getDifficultyColor(sample.difficulty)
            )}
          >
            {sample.difficulty}
          </Badge>
        </div>

        <CardTitle className="text-lg leading-tight">{sample.name}</CardTitle>
        <CardDescription className="text-sm line-clamp-3">
          {sample.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-0 flex-1 min-w-0 overflow-hidden">
        {/* Error Banner */}
        {hasError && errorMessage && (
          <div className="mb-3 p-3 bg-destructive/10 border border-destructive/20 rounded-md">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-destructive flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-destructive font-medium mb-1">
                  Failed to add
                </p>
                <p className="text-xs text-muted-foreground">{errorMessage}</p>
              </div>
              {onClearError && (
                <button
                  onClick={() => onClearError(sample.id)}
                  className="text-muted-foreground hover:text-foreground"
                  aria-label="Dismiss error"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
          </div>
        )}

        <div className="space-y-3 min-w-0">
          {/* Tags */}
          <div className="flex flex-wrap gap-1">
            {sample.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
            {sample.tags.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{sample.tags.length - 3}
              </Badge>
            )}
          </div>

          {/* Environment Variables Required - Collapsible */}
          {sample.requiredEnvVars && sample.requiredEnvVars.length > 0 && (
            <details className="group min-w-0 max-w-full overflow-hidden">
              <summary className="cursor-pointer list-none p-2 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-md hover:bg-amber-100 dark:hover:bg-amber-950/30 transition-colors flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <Key className="h-3.5 w-3.5 text-amber-600 dark:text-amber-500 flex-shrink-0" />
                  <span className="text-xs font-medium text-amber-900 dark:text-amber-100 truncate">
                    Requires {sample.requiredEnvVars.length} env var
                    {sample.requiredEnvVars.length > 1 ? "s" : ""}
                  </span>
                </div>
                <ChevronDown className="h-3 w-3 text-amber-600 dark:text-amber-500 flex-shrink-0 group-open:rotate-180 transition-transform" />
              </summary>
              <div className="mt-2 p-2 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-md space-y-2 min-w-0 max-w-full overflow-hidden">
                {sample.requiredEnvVars.map((envVar) => (
                  <div key={envVar.name} className="text-xs min-w-0 max-w-full overflow-hidden">
                    <div className="font-mono font-medium text-amber-900 dark:text-amber-100 break-words">
                      {envVar.name}
                    </div>
                    <div className="text-amber-700 dark:text-amber-300 mt-0.5 break-words">
                      {envVar.description}
                    </div>
                    {envVar.example && (
                      <div className="font-mono text-amber-600 dark:text-amber-400 mt-0.5 break-all">
                        {envVar.example}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </details>
          )}

          {/* Features */}
          <div className="space-y-2">
            <div className="text-xs font-medium text-muted-foreground">
              Key Features:
            </div>
            <ul className="text-xs space-y-1">
              {sample.features.slice(0, 3).map((feature) => (
                <li key={feature} className="flex items-center gap-1">
                  <div className="w-1 h-1 rounded-full bg-current opacity-50" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>

      <CardFooter className="pt-3 flex-col gap-3">
        {/* Metadata */}
        <div className="w-full flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <User className="h-3 w-3" />
            <span>{sample.author}</span>
          </div>
        </div>

        {/* Add Button - Full width on its own line */}
        <Button
          onClick={handleAdd}
          disabled={isDisabled}
          className="w-full"
          size="sm"
          variant={hasError ? "outline" : "default"}
        >
          {isDisabled ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Adding...
            </>
          ) : hasError ? (
            <>
              <Plus className="h-4 w-4 mr-2" />
              Retry
            </>
          ) : (
            <>
              <Plus className="h-4 w-4 mr-2" />
              Add Sample
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}

// Internal: Sample Entity Grid Component
function SampleEntityGrid({
  samples,
  onAdd,
  addingEntityId,
  errorEntityId,
  errorMessage,
  onClearError,
}: {
  samples: SampleEntity[];
  onAdd: (sample: SampleEntity) => Promise<void>;
  addingEntityId?: string | null;
  errorEntityId?: string | null;
  errorMessage?: string | null;
  onClearError?: (sampleId: string) => void;
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {samples.map((sample) => (
        <div key={sample.id} className="min-w-0">
          <SampleEntityCard
            sample={sample}
            onAdd={onAdd}
            isAdding={addingEntityId === sample.id}
            hasError={errorEntityId === sample.id}
            errorMessage={errorMessage}
            onClearError={onClearError}
          />
        </div>
      ))}
    </div>
  );
}

// Main: Gallery View Component
export function GalleryView({
  onAdd,
  addingEntityId,
  errorEntityId,
  errorMessage,
  onClearError,
  onClose,
  variant = "inline",
  hasExistingEntities = false,
}: GalleryViewProps) {
  // Inline variant - for empty state in main app
  if (variant === "inline") {
    return (
      <div className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Info Banner */}
          <div className="mb-8 p-4 bg-muted/50 border border-border rounded-lg">
            <div className="flex items-start gap-3">
              <TriangleAlert className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold mb-1">
                  No agents or workflows configured yet!
                </h3>
                <p className="text-sm text-muted-foreground mb-2">
                  You can configure agents or workflows by running{" "}
                  <code className="px-1.5 py-0.5 bg-background rounded text-xs">
                    devui
                  </code>{" "}
                  in a directory containing them.
                </p>
                <p className="text-sm text-muted-foreground">
                  You can also import any of the sample agents and workflows
                  below to get started quickly.
                </p>
              </div>
            </div>
          </div>

          {/* Sample Gallery */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4">Sample Gallery</h3>
            <SampleEntityGrid
              samples={SAMPLE_ENTITIES}
              onAdd={onAdd}
              addingEntityId={addingEntityId}
              errorEntityId={errorEntityId}
              errorMessage={errorMessage}
              onClearError={onClearError}
            />
          </div>

          {/* Footer */}
          <div className="text-center mt-12 pt-8 border-t">
            <p className="text-sm text-muted-foreground">
              Want to create your own agents or workflows? Check out the{" "}
              <a
                href="https://github.com/microsoft/agent-framework"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                documentation
              </a>
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Route variant - for /gallery page
  if (variant === "route") {
    return (
      <div className="h-full overflow-auto">
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Header */}
          <div className="mb-8">
            {hasExistingEntities && (
              <div className="mb-4">
                <Button variant="ghost" onClick={onClose} className="gap-2">
                  <ArrowLeft className="h-4 w-4" />
                  Back
                </Button>
              </div>
            )}

            <div className="text-center">
              <h2 className="text-2xl font-semibold mb-2">Sample Gallery</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Browse and add sample agents and workflows to learn the Agent
                Framework. These are curated examples ranging from beginner to
                advanced.
              </p>
            </div>
          </div>

          {/* Sample Gallery */}
          <SampleEntityGrid
            samples={SAMPLE_ENTITIES}
            onAdd={onAdd}
            addingEntityId={addingEntityId}
            errorEntityId={errorEntityId}
            errorMessage={errorMessage}
            onClearError={onClearError}
          />

          {/* Footer */}
          <div className="text-center mt-12 pt-8 border-t">
            <p className="text-sm text-muted-foreground">
              Want to create your own agents or workflows? Check out the{" "}
              <a
                href="https://github.com/microsoft/agent-framework"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                documentation
              </a>
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Modal variant - for dropdown trigger (simplified, just the grid)
  return (
    <SampleEntityGrid
      samples={SAMPLE_ENTITIES}
      onAdd={onAdd}
      addingEntityId={addingEntityId}
      errorEntityId={errorEntityId}
      errorMessage={errorMessage}
      onClearError={onClearError}
    />
  );
}



================================================
FILE: python/packages/devui/frontend/src/components/gallery/index.ts
================================================
/**
 * Gallery component exports
 */

export { GalleryView } from './gallery-view';


================================================
FILE: python/packages/devui/frontend/src/components/message_renderer/ContentRenderer.tsx
================================================
/**
 * ContentRenderer - Renders individual content items based on type
 */

import { useState } from "react";
import {
  Download,
  FileText,
  AlertCircle,
  Code,
  ChevronDown,
  ChevronUp,
  Music,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import type { RenderProps } from "./types";
import {
  isTextContent,
  isFunctionCallContent,
  isFunctionResultContent,
} from "@/types/agent-framework";

function TextContentRenderer({ content, isStreaming, className }: RenderProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!isTextContent(content)) return null;

  const text = content.text;
  const TRUNCATE_LENGTH = 1600;
  const shouldTruncate = text.length > TRUNCATE_LENGTH && !isStreaming;
  const displayText =
    shouldTruncate && !isExpanded
      ? text.slice(0, TRUNCATE_LENGTH) + "..."
      : text;

  return (
    <div className={`whitespace-pre-wrap break-words ${className || ""}`}>
      <div
        className={
          isExpanded && shouldTruncate ? "max-h-96 overflow-y-auto" : ""
        }
      >
        {displayText}
      </div>
      {isStreaming && (
        <span className="ml-1 inline-block h-2 w-2 animate-pulse rounded-full bg-current" />
      )}
      {shouldTruncate && (
        <div className="flex justify-end mt-1">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="inline-flex items-center gap-1 text-xs
                       bg-background/80 hover:bg-background border border-border/50 hover:border-border
                       text-muted-foreground hover:text-foreground
                       transition-colors cursor-pointer px-2 py-1 rounded"
          >
            {isExpanded ? (
              <>
                less <ChevronUp className="h-3 w-3" />
              </>
            ) : (
              <>
                {(text.length - TRUNCATE_LENGTH).toLocaleString()} more{" "}
                <ChevronDown className="h-3 w-3" />
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}

function DataContentRenderer({ content, className }: RenderProps) {
  const [imageError, setImageError] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  if (content.type !== "data") return null;

  // Extract data URI and media type (updated for new field names)
  const dataUri = typeof content.uri === "string" ? content.uri : "";
  const mediaTypeMatch = dataUri.match(/^data:([^;]+)/);
  const mediaType = content.media_type || mediaTypeMatch?.[1] || "unknown";

  const isImage = mediaType.startsWith("image/");
  const isPdf = mediaType === "application/pdf";
  const isAudio = mediaType.startsWith("audio/");

  if (isImage && !imageError) {
    return (
      <div className={`my-2 ${className || ""}`}>
        <img
          src={dataUri}
          alt="Uploaded image"
          className={`rounded-lg border max-w-full transition-all cursor-pointer ${
            isExpanded ? "max-h-none" : "max-h-64"
          }`}
          onClick={() => setIsExpanded(!isExpanded)}
          onError={() => setImageError(true)}
        />
        <div className="text-xs text-muted-foreground mt-1">
          {mediaType} • Click to {isExpanded ? "collapse" : "expand"}
        </div>
      </div>
    );
  }

  if (isAudio) {
    return (
      <div className={`my-2 p-3 border rounded-lg bg-purple-50 dark:bg-purple-950/20 ${className || ""}`}>
        <div className="flex items-center gap-2 mb-2">
          <Music className="h-4 w-4 text-purple-500" />
          <span className="text-sm font-medium text-purple-800 dark:text-purple-300">Audio File</span>
          <span className="text-xs text-muted-foreground">({mediaType})</span>
        </div>
        <audio controls className="w-full max-w-md">
          <source src={dataUri} type={mediaType} />
          Your browser does not support the audio element.
        </audio>
      </div>
    );
  }

  // Fallback for non-images/non-audio or failed images
  return (
    <div className={`my-2 p-3 border rounded-lg bg-muted ${className || ""}`}>
      <div className="flex items-center gap-2">
        {isPdf ? (
          <FileText className="h-4 w-4 text-red-500" />
        ) : (
          <Download className="h-4 w-4" />
        )}
        <span className="text-sm font-medium">
          {isPdf ? "PDF Document" : "File Attachment"}
        </span>
        <span className="text-xs text-muted-foreground">({mediaType})</span>
      </div>
      <Button
        variant="outline"
        size="sm"
        className="mt-2"
        onClick={() => {
          const link = document.createElement("a");
          link.href = dataUri;
          link.download = `attachment.${mediaType.split("/")[1] || "bin"}`;
          link.click();
        }}
      >
        <Download className="h-3 w-3 mr-1" />
        Download
      </Button>
    </div>
  );
}

function FunctionCallRenderer({ content, className }: RenderProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!isFunctionCallContent(content)) return null;

  let parsedArgs;
  try {
    parsedArgs =
      typeof content.arguments === "string"
        ? JSON.parse(content.arguments)
        : content.arguments;
  } catch {
    parsedArgs = content.arguments;
  }

  return (
    <div className={`my-2 p-3 border rounded-lg bg-blue-50 ${className || ""}`}>
      <div
        className="flex items-center gap-2 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Code className="h-4 w-4 text-blue-600" />
        <span className="text-sm font-medium text-blue-800">
          Function Call: {content.name}
        </span>
        <span className="text-xs text-blue-600">{isExpanded ? "▼" : "▶"}</span>
      </div>
      {isExpanded && (
        <div className="mt-2 text-xs font-mono bg-white p-2 rounded border">
          <div className="text-blue-600 mb-1">Arguments:</div>
          <pre className="whitespace-pre-wrap">
            {JSON.stringify(parsedArgs, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

function FunctionResultRenderer({ content, className }: RenderProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!isFunctionResultContent(content)) return null;

  return (
    <div
      className={`my-2 p-3 border rounded-lg bg-green-50 ${className || ""}`}
    >
      <div
        className="flex items-center gap-2 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Code className="h-4 w-4 text-green-600" />
        <span className="text-sm font-medium text-green-800">
          Function Result
        </span>
        <span className="text-xs text-green-600">{isExpanded ? "▼" : "▶"}</span>
      </div>
      {isExpanded && (
        <div className="mt-2 text-xs font-mono bg-white p-2 rounded border">
          <pre className="whitespace-pre-wrap">
            {typeof content.result === "string"
              ? content.result
              : JSON.stringify(content.result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

function ErrorContentRenderer({ content, className }: RenderProps) {
  if (content.type !== "error") return null;

  return (
    <div className={`my-2 p-3 border rounded-lg bg-red-50 ${className || ""}`}>
      <div className="flex items-center gap-2">
        <AlertCircle className="h-4 w-4 text-red-500" />
        <span className="text-sm font-medium text-red-800">Error</span>
        {content.error_code && (
          <span className="text-xs text-red-600">({content.error_code})</span>
        )}
      </div>
      <div className="mt-1 text-sm text-red-700">{content.error}</div>
    </div>
  );
}

function UriContentRenderer({ content, className }: RenderProps) {
  const [imageError, setImageError] = useState(false);

  if (content.type !== "uri") return null;

  const isImage = content.media_type?.startsWith("image/");

  if (isImage && !imageError) {
    return (
      <div className={`my-2 ${className || ""}`}>
        <img
          src={content.uri}
          alt="Referenced image"
          className="rounded-lg border max-w-full max-h-64"
          onError={() => setImageError(true)}
        />
        <div className="text-xs text-muted-foreground mt-1">
          <a
            href={content.uri}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:underline"
          >
            {content.uri}
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className={`my-2 p-3 border rounded-lg bg-muted ${className || ""}`}>
      <div className="flex items-center gap-2">
        <FileText className="h-4 w-4" />
        <a
          href={content.uri}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium hover:underline"
        >
          {content.media_type || "External Link"}
        </a>
      </div>
      <div className="text-xs text-muted-foreground mt-1 break-all">
        {content.uri}
      </div>
    </div>
  );
}

export function ContentRenderer({
  content,
  isStreaming,
  className,
}: RenderProps) {
  switch (content.type) {
    case "text":
      return (
        <TextContentRenderer
          content={content}
          isStreaming={isStreaming}
          className={className}
        />
      );
    case "data":
      return <DataContentRenderer content={content} className={className} />;
    case "uri":
      return <UriContentRenderer content={content} className={className} />;
    case "function_call":
      return <FunctionCallRenderer content={content} className={className} />;
    case "function_result":
      return <FunctionResultRenderer content={content} className={className} />;
    case "error":
      return <ErrorContentRenderer content={content} className={className} />;
    default:
      // Fallback for unsupported content types
      return (
        <div
          className={`my-2 p-2 bg-gray-100 rounded text-xs ${className || ""}`}
        >
          <div>Unsupported content type: {content.type}</div>
          <pre className="mt-1 text-xs whitespace-pre-wrap">
            {JSON.stringify(content, null, 2)}
          </pre>
        </div>
      );
  }
}



================================================
FILE: python/packages/devui/frontend/src/components/message_renderer/index.ts
================================================
/**
 * Message Renderer - Exports
 */

export { MessageRenderer } from "./MessageRenderer";
export { ContentRenderer } from "./ContentRenderer";
export { StreamingRenderer } from "./StreamingRenderer";
export type { MessageRendererProps, RenderProps, MessageRenderState } from "./types";


================================================
FILE: python/packages/devui/frontend/src/components/message_renderer/MessageRenderer.tsx
================================================
/**
 * MessageRenderer - Main orchestrator for rendering message contents
 */

import { StreamingRenderer } from "./StreamingRenderer";
import { ContentRenderer } from "./ContentRenderer";
import type { MessageRendererProps } from "./types";

export function MessageRenderer({
  contents,
  isStreaming = false,
  className,
}: MessageRendererProps) {
  // If not streaming, render each content item individually
  if (!isStreaming) {
    return (
      <div className={className}>
        {contents.map((content, index) => (
          <ContentRenderer
            key={index}
            content={content}
            isStreaming={false}
            className={index > 0 ? "mt-2" : ""}
          />
        ))}
      </div>
    );
  }

  // For streaming, use the streaming renderer for smart accumulation
  return (
    <StreamingRenderer
      contents={contents}
      isStreaming={isStreaming}
      className={className}
    />
  );
}


================================================
FILE: python/packages/devui/frontend/src/components/message_renderer/StreamingRenderer.tsx
================================================
/**
 * StreamingRenderer - Handles accumulation and display of streaming content
 */

import { useState, useEffect } from "react";
import { ContentRenderer } from "./ContentRenderer";
import type { Contents, MessageRenderState } from "./types";
import { isTextContent } from "@/types/agent-framework";

interface StreamingRendererProps {
  contents: Contents[];
  isStreaming?: boolean;
  className?: string;
}

export function StreamingRenderer({
  contents,
  isStreaming = false,
  className,
}: StreamingRendererProps) {
  const [renderState, setRenderState] = useState<MessageRenderState>({
    textAccumulator: "",
    dataContentItems: [],
    functionCalls: [],
    errors: [],
    isComplete: !isStreaming,
  });

  useEffect(() => {
    // Process and accumulate content
    let textAccumulator = "";
    const dataContentItems: Contents[] = [];
    const functionCalls: Contents[] = [];
    const errors: Contents[] = [];

    contents.forEach((content) => {
      if (isTextContent(content)) {
        textAccumulator += content.text;
      } else if (content.type === "data") {
        // Only show data content when streaming is complete or item is complete
        if (!isStreaming) {
          dataContentItems.push(content);
        }
      } else if (content.type === "function_call") {
        functionCalls.push(content);
      } else if (content.type === "error") {
        errors.push(content);
      } else {
        // Other content types (uri, function_result, etc.)
        dataContentItems.push(content);
      }
    });

    setRenderState({
      textAccumulator,
      dataContentItems,
      functionCalls,
      errors,
      isComplete: !isStreaming,
    });
  }, [contents, isStreaming]);

  const hasTextContent = renderState.textAccumulator.length > 0;
  const hasOtherContent =
    renderState.dataContentItems.length > 0 ||
    renderState.functionCalls.length > 0 ||
    renderState.errors.length > 0;

  return (
    <div className={className}>
      {/* Render accumulated text with streaming indicator */}
      {hasTextContent && (
        <div className="whitespace-pre-wrap break-words">
          {renderState.textAccumulator}
          {isStreaming && hasTextContent && (
            <span className="ml-1 inline-block h-2 w-2 animate-pulse rounded-full bg-current" />
          )}
        </div>
      )}

      {/* Render other content types when complete or non-data items immediately */}
      {hasOtherContent && (
        <div className="mt-2 space-y-2">
          {renderState.errors.map((content, index) => (
            <ContentRenderer key={`error-${index}`} content={content} />
          ))}

          {renderState.functionCalls.map((content, index) => (
            <ContentRenderer key={`function-${index}`} content={content} />
          ))}

          {renderState.dataContentItems.map((content, index) => (
            <ContentRenderer
              key={`data-${index}`}
              content={content}
              isStreaming={isStreaming}
            />
          ))}
        </div>
      )}

      {/* Show loading indicator when streaming and no text content yet */}
      {isStreaming && !hasTextContent && !hasOtherContent && (
        <div className="flex items-center space-x-1">
          <div className="flex space-x-1">
            <div className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.3s]" />
            <div className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.15s]" />
            <div className="h-2 w-2 animate-bounce rounded-full bg-current" />
          </div>
        </div>
      )}
    </div>
  );
}


================================================
FILE: python/packages/devui/frontend/src/components/message_renderer/types.ts
================================================
/**
 * Types for message rendering components
 */

// Re-export and extend types from agent-framework
import type {
  Contents,
  TextContent,
  DataContent,
  UriContent,
  FunctionCallContent,
  FunctionResultContent,
  ErrorContent,
  AgentRunResponseUpdate,
} from "@/types/agent-framework";

export type {
  Contents,
  TextContent,
  DataContent,
  UriContent,
  FunctionCallContent,
  FunctionResultContent,
  ErrorContent,
  AgentRunResponseUpdate,
};

// UI-specific types for message rendering
export interface MessageRenderState {
  // Track accumulated content during streaming
  textAccumulator: string;
  dataContentItems: Contents[];
  functionCalls: Contents[];
  errors: Contents[];
  isComplete: boolean;
}

export interface RenderProps {
  content: Contents;
  isStreaming?: boolean;
  className?: string;
}

export interface MessageRendererProps {
  contents: Contents[];
  isStreaming?: boolean;
  className?: string;
}


================================================
FILE: python/packages/devui/frontend/src/components/shared/about-modal.tsx
================================================
/**
 * About DevUI Modal - Shows information about the DevUI sample app
 */

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ExternalLink } from "lucide-react";

interface AboutModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AboutModal({ open, onOpenChange }: AboutModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader className="p-6 pb-4">
          <DialogTitle>About DevUI</DialogTitle>
        </DialogHeader>

        <DialogClose onClose={() => onOpenChange(false)} />

        <div className="px-6 pb-6 space-y-4">
          <p className="text-sm text-muted-foreground">
            DevUI is a sample app for getting started with Agent Framework.
          </p>

          <div className="flex justify-center pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                window.open(
                  "https://github.com/microsoft/agent-framework",
                  "_blank"
                )
              }
              className="text-xs"
            >
              <ExternalLink className="h-3 w-3 mr-1" />
              Learn More about Agent Framework
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}



================================================
FILE: python/packages/devui/frontend/src/components/shared/agent-details-modal.tsx
================================================
/**
 * AgentDetailsModal - Responsive grid-based modal for displaying agent metadata
 */

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Bot,
  Package,
  FileText,
  FolderOpen,
  Database,
  Globe,
  CheckCircle,
  XCircle,
} from "lucide-react";
import type { AgentInfo } from "@/types";

interface AgentDetailsModalProps {
  agent: AgentInfo;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface DetailCardProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

function DetailCard({ title, icon, children, className = "" }: DetailCardProps) {
  return (
    <div className={`border rounded-lg p-4 bg-card ${className}`}>
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      </div>
      <div className="text-sm text-muted-foreground">{children}</div>
    </div>
  );
}

export function AgentDetailsModal({
  agent,
  open,
  onOpenChange,
}: AgentDetailsModalProps) {
  const sourceIcon =
    agent.source === "directory" ? (
      <FolderOpen className="h-4 w-4 text-muted-foreground" />
    ) : agent.source === "in_memory" ? (
      <Database className="h-4 w-4 text-muted-foreground" />
    ) : (
      <Globe className="h-4 w-4 text-muted-foreground" />
    );

  const sourceLabel =
    agent.source === "directory"
      ? "Local"
      : agent.source === "in_memory"
      ? "In-Memory"
      : "Gallery";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader className="px-6 pt-6 flex-shrink-0">
          <DialogTitle>Agent Details</DialogTitle>
          <DialogClose onClose={() => onOpenChange(false)} />
        </DialogHeader>

        <div className="px-6 pb-6 overflow-y-auto flex-1">
          {/* Header Section */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <Bot className="h-6 w-6 text-primary" />
              <h2 className="text-xl font-semibold text-foreground">
                {agent.name || agent.id}
              </h2>
            </div>
            {agent.description && (
              <p className="text-muted-foreground">{agent.description}</p>
            )}
          </div>

          <div className="h-px bg-border mb-6" />

          {/* Grid Layout for Metadata */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {/* Model & Client */}
            {(agent.model || agent.chat_client_type) && (
              <DetailCard
                title="Model & Client"
                icon={<Bot className="h-4 w-4 text-muted-foreground" />}
              >
                <div className="space-y-1">
                  {agent.model && (
                    <div className="font-mono text-foreground">{agent.model}</div>
                  )}
                  {agent.chat_client_type && (
                    <div className="text-xs">({agent.chat_client_type})</div>
                  )}
                </div>
              </DetailCard>
            )}

            {/* Source */}
            <DetailCard title="Source" icon={sourceIcon}>
              <div className="space-y-1">
                <div className="text-foreground">{sourceLabel}</div>
                {agent.module_path && (
                  <div className="font-mono text-xs break-all">
                    {agent.module_path}
                  </div>
                )}
              </div>
            </DetailCard>

            {/* Environment */}
            <DetailCard
              title="Environment"
              icon={
                agent.has_env ? (
                  <XCircle className="h-4 w-4 text-orange-500" />
                ) : (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                )
              }
              className="md:col-span-2"
            >
              <div
                className={
                  agent.has_env ? "text-orange-600 dark:text-orange-400" : "text-green-600 dark:text-green-400"
                }
              >
                {agent.has_env
                  ? "Requires environment variables"
                  : "No environment variables required"}
              </div>
            </DetailCard>
          </div>

          {/* Full Width Sections */}
          {agent.instructions && (
            <DetailCard
              title="Instructions"
              icon={<FileText className="h-4 w-4 text-muted-foreground" />}
              className="mb-4"
            >
              <div className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                {agent.instructions}
              </div>
            </DetailCard>
          )}

          {/* Tools and Middleware Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Tools */}
            <DetailCard
              title={`Tools (${agent.tools.length})`}
              icon={<Package className="h-4 w-4 text-muted-foreground" />}
            >
              {agent.tools.length > 0 ? (
                <ul className="space-y-1">
                  {agent.tools.map((tool, index) => (
                    <li key={index} className="font-mono text-xs text-foreground">
                      • {tool}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-muted-foreground">No tools configured</div>
              )}
            </DetailCard>

            {/* Middleware */}
            {agent.middleware && agent.middleware.length > 0 && (
              <DetailCard
                title={`Middleware (${agent.middleware.length})`}
                icon={<Package className="h-4 w-4 text-muted-foreground" />}
              >
                <ul className="space-y-1">
                  {agent.middleware.map((mw, index) => (
                    <li key={index} className="font-mono text-xs text-foreground">
                      • {mw}
                    </li>
                  ))}
                </ul>
              </DetailCard>
            )}

            {/* Context Providers */}
            {agent.context_providers && agent.context_providers.length > 0 && (
              <DetailCard
                title={`Context Providers (${agent.context_providers.length})`}
                icon={<Database className="h-4 w-4 text-muted-foreground" />}
                className={!agent.middleware || agent.middleware.length === 0 ? "md:col-start-2" : ""}
              >
                <ul className="space-y-1">
                  {agent.context_providers.map((cp, index) => (
                    <li key={index} className="font-mono text-xs text-foreground">
                      • {cp}
                    </li>
                  ))}
                </ul>
              </DetailCard>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}



================================================
FILE: python/packages/devui/frontend/src/components/shared/app-header.tsx
================================================
/**
 * AppHeader - Global application header
 * Features: Entity selection, global settings, theme toggle
 */

import { Button } from "@/components/ui/button";
import { EntitySelector } from "@/components/shared/entity-selector";
import { ModeToggle } from "@/components/mode-toggle";
import { Settings } from "lucide-react";
import type { AgentInfo, WorkflowInfo } from "@/types";

interface AppHeaderProps {
  agents: AgentInfo[];
  workflows: WorkflowInfo[];
  selectedItem?: AgentInfo | WorkflowInfo;
  onSelect: (item: AgentInfo | WorkflowInfo) => void;
  onRemove?: (entityId: string) => void;
  onBrowseGallery?: () => void;
  isLoading?: boolean;
  onSettingsClick?: () => void;
}

export function AppHeader({
  agents,
  workflows,
  selectedItem,
  onSelect,
  onRemove,
  onBrowseGallery,
  isLoading = false,
  onSettingsClick,
}: AppHeaderProps) {
  return (
    <header className="flex h-14 items-center gap-4 border-b px-4">
      <div className="flex items-center gap-2 font-semibold">
        <svg
          width="24"
          height="24"
          viewBox="0 0 805 805"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="flex-shrink-0"
        >
          <path
            d="M402.488 119.713C439.197 119.713 468.955 149.472 468.955 186.18C468.955 192.086 471.708 197.849 476.915 200.635L546.702 237.977C555.862 242.879 566.95 240.96 576.092 236.023C585.476 230.955 596.218 228.078 607.632 228.078C644.341 228.078 674.098 257.836 674.099 294.545C674.099 316.95 663.013 336.765 646.028 348.806C637.861 354.595 631.412 363.24 631.412 373.251V430.818C631.412 440.83 637.861 449.475 646.028 455.264C663.013 467.305 674.099 487.121 674.099 509.526C674.099 546.235 644.341 575.994 607.632 575.994C598.598 575.994 589.985 574.191 582.133 570.926C573.644 567.397 563.91 566.393 555.804 570.731L469.581 616.867C469.193 617.074 468.955 617.479 468.955 617.919C468.955 654.628 439.197 684.386 402.488 684.386C365.779 684.386 336.021 654.628 336.021 617.919C336.021 616.802 335.423 615.765 334.439 615.238L249.895 570C241.61 565.567 231.646 566.713 223.034 570.472C214.898 574.024 205.914 575.994 196.47 575.994C159.761 575.994 130.002 546.235 130.002 509.526C130.002 486.66 141.549 466.49 159.13 454.531C167.604 448.766 174.349 439.975 174.349 429.726V372.538C174.349 362.289 167.604 353.498 159.13 347.734C141.549 335.774 130.002 315.604 130.002 292.738C130.002 256.029 159.761 226.271 196.47 226.271C208.223 226.271 219.263 229.322 228.843 234.674C238.065 239.827 249.351 241.894 258.666 236.91L328.655 199.459C333.448 196.895 336.021 191.616 336.021 186.18C336.021 149.471 365.779 119.713 402.488 119.713ZM475.716 394.444C471.337 396.787 468.955 401.586 468.955 406.552C468.955 429.68 457.142 450.048 439.221 461.954C430.571 467.7 423.653 476.574 423.653 486.959V537.511C423.653 547.896 430.746 556.851 439.379 562.622C449 569.053 461.434 572.052 471.637 566.592L527.264 536.826C536.887 531.677 541.164 520.44 541.164 509.526C541.164 485.968 553.42 465.272 571.904 453.468C580.846 447.757 588.054 438.749 588.054 428.139V371.427C588.054 363.494 582.671 356.676 575.716 352.862C569.342 349.366 561.663 348.454 555.253 351.884L475.716 394.444ZM247.992 349.841C241.997 346.633 234.806 347.465 228.873 350.785C222.524 354.337 217.706 360.639 217.706 367.915V429.162C217.706 439.537 224.611 448.404 233.248 454.152C251.144 466.062 262.937 486.417 262.937 509.526C262.937 519.654 267.026 529.991 275.955 534.769L334.852 566.284C344.582 571.49 356.362 568.81 365.528 562.667C373.735 557.166 380.296 548.643 380.296 538.764V486.305C380.296 476.067 373.564 467.282 365.103 461.516C347.548 449.552 336.021 429.398 336.021 406.552C336.021 400.967 333.389 395.536 328.465 392.902L247.992 349.841ZM270.019 280.008C265.421 282.469 262.936 287.522 262.937 292.738C262.937 293.308 262.929 293.876 262.915 294.443C262.615 306.354 266.961 318.871 277.466 324.492L334.017 354.751C344.13 360.163 356.442 357.269 366.027 350.969C376.495 344.088 389.024 340.085 402.488 340.085C416.203 340.085 428.947 344.239 439.532 351.357C449.163 357.834 461.63 360.861 471.864 355.385L526.625 326.083C537.106 320.474 541.458 307.999 541.182 296.115C541.17 295.593 541.164 295.069 541.164 294.545C541.164 288.551 538.376 282.696 533.091 279.868L463.562 242.664C454.384 237.753 443.274 239.688 434.123 244.65C424.716 249.75 413.941 252.647 402.488 252.647C390.83 252.647 379.873 249.646 370.348 244.373C361.148 239.281 349.917 237.256 340.646 242.217L270.019 280.008Z"
            fill="url(#paint0_linear_510_1294)"
          />
          <defs>
            <linearGradient
              id="paint0_linear_510_1294"
              x1="255.628"
              y1="-34.3245"
              x2="618.483"
              y2="632.032"
              gradientUnits="userSpaceOnUse"
            >
              <stop stopColor="#D59FFF" />
              <stop offset="1" stopColor="#8562C5" />
            </linearGradient>
          </defs>
        </svg>
        Dev UI
      </div>
      <EntitySelector
        agents={agents}
        workflows={workflows}
        selectedItem={selectedItem}
        onSelect={onSelect}
        onRemove={onRemove}
        onBrowseGallery={onBrowseGallery}
        isLoading={isLoading}
      />

      <div className="flex items-center gap-2 ml-auto">
        <ModeToggle />
        <Button variant="ghost" size="sm" onClick={onSettingsClick}>
          <Settings className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}



================================================
FILE: python/packages/devui/frontend/src/components/shared/debug-panel.tsx
================================================
/**
 * DebugPanel - Tabbed interface for OpenAI events, traces, and tool information
 * Features: Real-time event streaming, trace visualization, tool call details
 */

import { useRef, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Activity,
  Search,
  Wrench,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Zap,
  MessageSquare,
  ChevronRight,
  ChevronDown,
  Info,
  PanelRightClose,
} from "lucide-react";
import type { ExtendedResponseStreamEvent } from "@/types";

// Type definitions for event data structures
interface EventDataBase {
  call_id?: string;
  executor_id?: string;
  timestamp?: string;
  [key: string]: unknown;
}

interface FunctionResultData extends EventDataBase {
  result?: unknown;
  status?: "completed" | "failed";
  exception?: string;
}

interface FunctionCallData extends EventDataBase {
  name?: string;
  arguments?: string | object;
  function?: unknown;
  tool_calls?: unknown[];
}

interface WorkflowEventData extends EventDataBase {
  event_type?: string;
  data?: Record<string, unknown>;
}

interface TraceEventData extends EventDataBase {
  operation_name?: string;
  duration_ms?: number;
  status?: string;
  attributes?: Record<string, unknown>;
  span_id?: string;
  trace_id?: string;
  parent_span_id?: string | null;
  start_time?: number;
  end_time?: number;
  entity_id?: string;
  session_id?: string | null;
}

interface DebugPanelProps {
  events: ExtendedResponseStreamEvent[];
  isStreaming?: boolean;
  onClose?: () => void;
}

// Helper function to accumulate OpenAI events into meaningful units
function processEventsForDisplay(
  events: ExtendedResponseStreamEvent[]
): ExtendedResponseStreamEvent[] {
  const processedEvents: ExtendedResponseStreamEvent[] = [];
  const functionCalls = new Map<
    string,
    {
      name?: string;
      arguments: string;
      callId: string;
      timestamp: string;
    }
  >();
  const callIdToName = new Map<string, string>(); // Track call_id -> function name mappings
  let accumulatedText = "";
  const lastFunctionCallId: string | null = null; // Track the most recent function call

  for (const event of events) {
    // Always show completion, error, workflow events, and function results
    if (
      event.type === "response.done" ||
      event.type === "error" ||
      event.type === "response.workflow_event.complete" ||
      event.type === "response.trace_event.complete" ||
      event.type === "response.trace.complete" ||
      event.type === "response.function_result.complete"
    ) {
      // Flush any accumulated text before showing these events
      if (accumulatedText.trim()) {
        processedEvents.push({
          type: "response.output_text.delta",
          delta: accumulatedText.trim(),
        } as ExtendedResponseStreamEvent);
        accumulatedText = "";
      }

      // Extract function names from trace events
      if (
        (event.type === "response.trace_event.complete" ||
          event.type === "response.trace.complete") &&
        "data" in event
      ) {
        const traceData = event.data as TraceEventData;
        if (
          traceData.attributes &&
          traceData.attributes["gen_ai.output.messages"] &&
          typeof traceData.attributes["gen_ai.output.messages"] === "string"
        ) {
          try {
            const messages = JSON.parse(
              traceData.attributes["gen_ai.output.messages"] as string
            );
            for (const msg of messages) {
              if (msg.parts) {
                for (const part of msg.parts) {
                  if (part.type === "tool_call" && part.name && part.id) {
                    // Store the call_id -> function name mapping
                    callIdToName.set(part.id, part.name);
                  }
                }
              }
            }
          } catch {
            // Ignore parsing errors
          }
        }
      }

      // For function results, ensure we have the corresponding function call
      if (
        event.type === "response.function_result.complete" &&
        "data" in event
      ) {
        const resultData = event.data as FunctionResultData;
        const callId = resultData.call_id;

        // Only create function call event if we have actual argument data
        if (callId && functionCalls.has(callId)) {
          const call = functionCalls.get(callId)!;
          const functionName =
            callIdToName.get(callId) || call.name || "unknown";

          processedEvents.push({
            type: "response.function_call.complete",
            data: {
              name: functionName,
              arguments: call.arguments,
              call_id: call.callId,
            },
          } as ExtendedResponseStreamEvent);
          functionCalls.delete(callId);
        }
      }

      processedEvents.push(event);
      continue;
    }

    // Handle function call start events
    if (event.type === "response.function_call.delta" && "data" in event) {
      const callData = event.data as FunctionCallData;
      const callId = callData.call_id || `call_${Date.now()}`;

      // Initialize or update the function call
      if (!functionCalls.has(callId)) {
        functionCalls.set(callId, {
          name: callData.name || undefined,
          arguments: "",
          callId,
          timestamp: new Date().toISOString(),
        });
      }

      // Update name if provided
      if (callData.name && callData.name.trim()) {
        functionCalls.get(callId)!.name = callData.name.trim();
      }
      continue;
    }

    // Handle function call complete events that come directly (not generated by us)
    if (event.type === "response.function_call.complete" && "data" in event) {
      