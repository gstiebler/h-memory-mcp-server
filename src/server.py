from typing import Optional, List
from fastmcp import FastMCP
from .memory_store import MemoryStore


# Initialize the MCP server
mcp = FastMCP("memory-server")

# Initialize the memory store
store = MemoryStore()


@mcp.tool()
def add_memory(
    position: List[str],
    description: str,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None,
    author: str = "user"
) -> dict:
    """Add a new memory at the specified position.
    
    Args:
        position: List of descriptions representing the path to the parent memory
        description: Short description of the memory
        content: Optional longer text content
        tags: Optional list of tags for categorization
        author: Author of the memory (default: "user")
    
    Returns:
        Dictionary with memory details or error message
    """
    if tags is None:
        tags = []
    
    return store.add_memory(position, description, content, tags, author)


@mcp.tool()
def read_memory(position: List[str]) -> dict:
    """Read a memory at the specified position.
    
    Args:
        position: List of descriptions representing the path to the memory
    
    Returns:
        Dictionary with memory details (excluding children) or error message
    """
    return store.read_memory(position)


@mcp.tool()
def list_children(position: List[str]) -> dict:
    """List all children of a memory at the specified position.
    
    Args:
        position: List of descriptions representing the path to the memory
    
    Returns:
        Dictionary with list of child descriptions or error message
    """
    return store.list_children(position)


@mcp.tool()
def edit_memory(
    position: List[str],
    description: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> dict:
    """Edit a memory at the specified position.
    
    Args:
        position: List of descriptions representing the path to the memory
        description: New description (optional)
        content: New content (optional)
        tags: New tags list (optional)
    
    Returns:
        Dictionary with updated memory info or error message
    """
    return store.edit_memory(position, description, content, tags)


@mcp.tool()
def remove_memory(position: List[str]) -> dict:
    """Remove a memory and all its children at the specified position.
    
    Args:
        position: List of descriptions representing the path to the memory
    
    Returns:
        Dictionary with removal info or error message
    """
    return store.remove_memory(position)


def main():
    """Run the MCP server."""
    import sys
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()