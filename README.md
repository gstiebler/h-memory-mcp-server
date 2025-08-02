# Memory MCP Server

A hierarchical memory storage system built as an MCP (Model Context Protocol) server. This server allows AI assistants to store, retrieve, and organize memories in a tree-like structure with metadata tracking.

## Features

- **Hierarchical Organization**: Memories are organized in a tree structure, where each memory can have child memories
- **Position-Based Navigation**: Access memories using a path-like position system (e.g., `["projects", "mcp", "features"]`)
- **Rich Metadata**: Each memory includes:
  - Unique ID
  - Description (short identifier)
  - Content (optional detailed text)
  - Tags for categorization
  - Author information
  - Creation and update timestamps
  - Access tracking (count and last accessed time)
- **Persistent Storage**: Memories are stored in a JSON file for persistence across sessions
- **Thread-Safe Operations**: All operations are thread-safe for concurrent access

## Installation

This project uses `uv` for Python package management.

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd memory-mcp-server
```

2. Install dependencies with uv:
```bash
uv sync
```

## Usage

### Running the Server

To run the MCP server:

```bash
uv run -m src.server
```

### Integrating with Claude

1. Copy the `claude_mcp_config.json` to your Claude configuration directory
2. Update the `cwd` path in the configuration to match your installation path
3. Restart Claude to load the new MCP server

### Available Operations

#### Add Memory
Add a new memory at a specified position:
```
add_memory(position=["projects"], description="mcp", content="MCP development notes", tags=["development"], author="user")
```

#### Read Memory
Read a memory's details (without children):
```
read_memory(position=["projects", "mcp"])
```

#### List Children
List all child memories at a position:
```
list_children(position=["projects"])
```

#### Edit Memory
Update a memory's properties:
```
edit_memory(position=["projects", "mcp"], content="Updated MCP notes", tags=["development", "protocol"])
```

#### Remove Memory
Remove a memory and all its children:
```
remove_memory(position=["projects", "mcp"])
```

## Development

### Using Mise for Task Management

This project includes a `mise.toml` configuration file that provides convenient tasks for common development operations:

```bash
# Install mise (if not already installed)
# See https://mise.jdx.dev for installation instructions

# Run all checks (format, lint, type check)
mise run check

# Run all tests
mise run test

# Run tests with coverage
mise run test-cov

# Auto-fix formatting and linting issues
mise run fix

# Run all checks and tests
mise run all

# Run individual tasks
mise run format      # Format code with ruff
mise run lint        # Run ruff linter
mise run mypy        # Run type checker

# Development server
mise run dev         # Run the MCP server

# Clean generated files
mise run clean
```

### Code Quality

The project uses automated tools to maintain code quality:

#### Linting with Ruff

```bash
# Run ruff linter
uv run ruff check

# Auto-fix issues
uv run ruff check --fix

# Format code
uv run ruff format
```

#### Type Checking with MyPy

```bash
# Run type checker
uv run mypy src/ tests/
```

#### Continuous Integration

The project includes GitHub Actions that automatically run on every push and pull request:
- Code formatting check (ruff format)
- Linting (ruff check)
- Type checking (mypy)

### Running Tests

The project includes comprehensive tests for all components:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_models.py

# Run with coverage report
uv run pytest --cov=src

# Run tests and show print statements
uv run pytest -s
```

The test suite includes:
- **Model tests**: Data structure validation and serialization
- **Storage tests**: CRUD operations, persistence, and thread safety
- **Server tests**: MCP tool function behavior and integration

Test files are located in the `tests/` directory:
- `test_models.py` - Tests for the Memory data model
- `test_memory_store.py` - Tests for storage operations
- `test_server.py` - Tests for MCP server functions

### Development Mode

To run in development mode with auto-reload:

```bash
uv run --reload -m src.server
```

## Storage Format

Memories are stored in `memories.json` with the following structure:

```json
{
  "id": "uuid",
  "description": "root",
  "content": "Root of all memories",
  "tags": [],
  "author": "system",
  "created_at": "2025-01-09T10:00:00",
  "access_count": 0,
  "last_accessed": "2025-01-09T10:00:00",
  "children": [
    {
      "id": "uuid",
      "description": "projects",
      "content": null,
      "tags": ["category"],
      "author": "user",
      "created_at": "2025-01-09T10:05:00",
      "access_count": 5,
      "last_accessed": "2025-01-09T11:00:00",
      "children": []
    }
  ]
}
```

## License

MIT License