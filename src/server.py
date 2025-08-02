from fastmcp import FastMCP
import typer

from .memory_store import MemoryStore

# Initialize the MCP server
mcp: FastMCP = FastMCP("memory-server")

# Global store variable that will be initialized in main
store: MemoryStore | None = None


@mcp.tool()
def add_memory(
    position: list[str],
    description: str,
    content: str | None = None,
    tags: list[str] | None = None,
    author: str = "user",
) -> dict:
    """Add a new memory at the specified position.

    Args:
        position: List of descriptions representing the hierarchical path to the parent memory.
                 Each element is a memory description, forming a path from root to target.
                 Examples:
                 - [] = Add as child of root memory
                 - ["projects"] = Add as child of the "projects" memory
                 - ["projects", "work"] = Add as child of "work" under "projects"
                 - ["notes", "meeting", "2024"] = Add under "2024" → "meeting" → "notes"
        description: Short description of the memory
        content: Optional longer text content
        tags: Optional list of tags for categorization
        author: Author of the memory (default: "user")

    Returns:
        Dictionary with memory details or error message
    """
    if tags is None:
        tags = []

    if store is None:
        raise RuntimeError("Memory store not initialized")
    return store.add_memory(position, description, content, tags, author)


@mcp.tool()
def read_memory(position: list[str]) -> dict:
    """Read a memory at the specified position.

    Args:
        position: List of descriptions representing the hierarchical path to the memory.
                 Each element is a memory description, forming a path from root to target.
                 Examples:
                 - [] = Read the root memory
                 - ["projects"] = Read the "projects" memory
                 - ["projects", "work"] = Read "work" memory under "projects"
                 - ["notes", "meeting", "2024"] = Read "2024" under "meeting" → "notes"

    Returns:
        Dictionary with memory details (excluding children) or error message
    """
    if store is None:
        raise RuntimeError("Memory store not initialized")
    return store.read_memory(position)


@mcp.tool()
def list_children(position: list[str]) -> dict:
    """List all children of a memory at the specified position.

    Args:
        position: List of descriptions representing the hierarchical path to the memory.
                 Each element is a memory description, forming a path from root to target.
                 Examples:
                 - [] = List children of the root memory
                 - ["projects"] = List children of the "projects" memory
                 - ["projects", "work"] = List children of "work" under "projects"
                 - ["notes", "meeting", "2024"] = List children of "2024" under "meeting" → "notes"

    Returns:
        Dictionary with list of children including description, content, tags, and children_count
    """
    if store is None:
        raise RuntimeError("Memory store not initialized")
    return store.list_children(position)


@mcp.tool()
def edit_memory(
    position: list[str],
    description: str | None = None,
    content: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Edit a memory at the specified position.

    Args:
        position: List of descriptions representing the hierarchical path to the memory.
                 Each element is a memory description, forming a path from root to target.
                 Examples:
                 - [] = Edit the root memory
                 - ["projects"] = Edit the "projects" memory
                 - ["projects", "work"] = Edit "work" memory under "projects"
                 - ["notes", "meeting", "2024"] = Edit "2024" under "meeting" → "notes"
        description: New description (optional)
        content: New content (optional)
        tags: New tags list (optional)

    Returns:
        Dictionary with updated memory info or error message
    """
    if store is None:
        raise RuntimeError("Memory store not initialized")
    return store.edit_memory(position, description, content, tags)


@mcp.tool()
def remove_memory(position: list[str]) -> dict:
    """Remove a memory and all its children at the specified position.

    Args:
        position: List of descriptions representing the hierarchical path to the memory.
                 Each element is a memory description, forming a path from root to target.
                 Examples:
                 - ["projects"] = Remove the "projects" memory and all its children
                 - ["projects", "work"] = Remove "work" under "projects" and all its children
                 - ["notes", "meeting", "2024"] = Remove "2024" under "meeting" → "notes"
                 Note: The root memory (position []) cannot be removed.

    Returns:
        Dictionary with removal info or error message
    """
    if store is None:
        raise RuntimeError("Memory store not initialized")
    return store.remove_memory(position)


def main(
    memory_file: str = typer.Option(
        ..., "--memory-file", "-f", help="Path to the JSON file where memories will be stored"
    ),
):
    """Run the MCP server."""
    global store
    store = MemoryStore(storage_path=memory_file)
    mcp.run(transport="stdio")


def cli_main():
    """Entry point for the CLI."""
    typer.run(main)


if __name__ == "__main__":
    cli_main()
