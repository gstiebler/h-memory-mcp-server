# Memory MCP Server - Project Context

This document provides context for Claude to understand and work with the Memory MCP Server project.

## Project Overview

This is a Model Context Protocol (MCP) server that implements a hierarchical memory storage system. It allows AI assistants to persistently store and retrieve structured memories organized in a tree-like structure.

## Key Technologies

- **Python 3.12+**: Core language
- **uv**: Package manager for Python (used instead of pip/poetry)
- **FastMCP**: High-level Python library for building MCP servers
- **Pydantic**: Data validation and serialization
- **JSON**: Storage format for memories

## Development Workflow

### Package Management
Always use `uv` for all package operations:
- `uv sync` - Install dependencies
- `uv add <package>` - Add new dependency
- `uv run <command>` - Run commands in the virtual environment
- `uv run main.py` - Run the MCP server

### Running the Server
```bash
uv run main.py
```

### Testing Changes
When testing the server:
1. Run `uv run main.py` in one terminal
2. The server communicates via stdio (standard input/output)
3. Send JSON-RPC messages to test functionality

### Code Style
- Use type hints for all function parameters and returns
- Follow Pydantic models for data structures
- Keep functions focused and single-purpose
- Use descriptive variable names
- Thread safety is important - use locks when modifying shared state

### Code Quality Tools
The project uses automated tools to maintain code quality:

#### Ruff (Linting and Formatting)
```bash
# Check code style issues
uv run ruff check src/ tests/ main.py

# Auto-fix issues
uv run ruff check src/ tests/ main.py --fix

# Format code
uv run ruff format src/ tests/ main.py

# Check if code is formatted correctly
uv run ruff format --check src/ tests/ main.py
```

Ruff is configured in `pyproject.toml` with:
- Line length: 88 characters
- Target Python version: 3.12
- Enabled rules: pycodestyle, pyflakes, isort, flake8-bugbear, flake8-comprehensions, pyupgrade

#### MyPy (Type Checking)
```bash
# Run type checker
uv run mypy src/ tests/ main.py
```

MyPy is configured for strict type checking with:
- Python version: 3.12
- Strict mode enabled
- All type checking flags enabled

#### CI/CD
GitHub Actions automatically run on every push and pull request to ensure:
- Code is properly formatted (ruff format --check)
- No linting issues (ruff check)
- Type annotations are correct (mypy)

**Important**: Always run these checks before committing:
```bash
# Quick check everything
uv run ruff format src/ tests/ main.py && uv run ruff check src/ tests/ main.py && uv run mypy src/ tests/ main.py
```

## Project Structure

```
memory-mcp-server/
├── .github/
│   └── workflows/
│       └── ci.yml        # GitHub Actions CI/CD workflow
├── src/
│   ├── models.py         # Pydantic models for Memory and Position
│   ├── memory_store.py   # Core storage logic with thread-safe operations
│   └── server.py         # MCP server implementation with tool definitions
├── tests/               # Test suite
│   ├── test_models.py    # Tests for data models
│   ├── test_memory_store.py # Tests for storage operations
│   └── test_server.py    # Tests for MCP server functions
├── main.py              # Entry point that runs the server
├── memories.json        # Persistent storage (auto-created)
└── pyproject.toml       # Project config managed by uv
```

## Key Design Decisions

1. **Hierarchical Structure**: Memories are organized in a tree where each memory can have children
2. **Position-Based Navigation**: Uses lists of descriptions as paths (e.g., `["projects", "mcp"]`)
3. **Thread Safety**: All operations use locks to ensure concurrent access safety
4. **Metadata Tracking**: Automatic tracking of access counts and timestamps
5. **JSON Storage**: Human-readable format for easy debugging and manual editing

## Common Tasks

### Adding a New Tool
1. Add the function to `server.py` with `@mcp.tool()` decorator
2. Implement the logic in `memory_store.py`
3. Use proper type hints and docstrings

### Modifying the Memory Model
1. Update the `Memory` class in `models.py`
2. Update `to_dict()` and `from_dict()` methods for serialization
3. Consider backward compatibility with existing storage files

### Testing
Run the comprehensive test suite:
```bash
uv run pytest -v        # Run all tests
uv run pytest -s        # Show print statements
uv run pytest --cov=src # With coverage report
```

### Debugging
- Check `memories.json` for the current state
- Use print statements in the server (they go to stderr)
- The server expects JSON-RPC messages on stdin

## Important Notes

- Always use `uv run` to execute Python code in this project
- The root memory is created automatically and cannot be deleted
- Memory descriptions must be unique within their parent
- All timestamps are stored in ISO format
- The server runs on stdio transport (not HTTP)

## Future Enhancements (Not Implemented Yet)
- Search functionality across all memories
- Move operation to reorganize memories
- Bulk operations for efficiency
- Export/import capabilities
- Validation for circular references
- Query operations like get_path, find_by_date_range