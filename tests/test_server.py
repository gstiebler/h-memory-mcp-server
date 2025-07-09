import pytest
from unittest.mock import patch
from src.server import mcp
from src.memory_store import MemoryStore


class TestServerFunctions:
    """Test the MCP server tool functions."""

    @pytest.fixture(autouse=True)
    def setup(self, temp_storage_file):
        """Setup test with a fresh memory store."""
        # Replace the global store with a test store
        test_store = MemoryStore(temp_storage_file)

        # Patch the store in the server module
        with patch("src.server.store", test_store):
            yield test_store

    def get_tool_function(self, tool_name):
        """Get the actual function from the MCP tool."""
        tools = mcp._tool_manager._tools
        for tool in tools.values():
            if tool.name == tool_name:
                return tool.fn
        raise ValueError(f"Tool {tool_name} not found")

    def test_add_memory_tool(self):
        """Test the add_memory tool function."""
        add_memory = self.get_tool_function("add_memory")

        # First add parent
        result = add_memory([], "test", author="user")
        assert isinstance(result, dict)
        assert "error" not in result

        # Then add child
        result = add_memory(
            position=["test"],
            description="child",
            content="test content",
            tags=["tag1", "tag2"],
            author="test_user",
        )

        assert isinstance(result, dict)
        assert "error" not in result
        assert result["description"] == "child"
        assert result["position"] == ["test", "child"]

    def test_add_memory_defaults(self):
        """Test add_memory with default values."""
        add_memory = self.get_tool_function("add_memory")

        result = add_memory(position=[], description="test")

        assert isinstance(result, dict)
        assert "error" not in result
        assert result["description"] == "test"

    def test_read_memory_tool(self):
        """Test the read_memory tool function."""
        add_memory = self.get_tool_function("add_memory")
        read_memory = self.get_tool_function("read_memory")

        # Add a memory first
        add_memory([], "test", content="content", author="user")

        # Read it
        result = read_memory(["test"])

        assert isinstance(result, dict)
        assert "error" not in result
        assert result["description"] == "test"
        assert result["content"] == "content"

    def test_list_children_tool(self):
        """Test the list_children tool function."""
        add_memory = self.get_tool_function("add_memory")
        list_children = self.get_tool_function("list_children")

        # Add some memories
        add_memory([], "parent", author="user")
        add_memory(["parent"], "child1", author="user")
        add_memory(["parent"], "child2", author="user")

        # List children
        result = list_children(["parent"])

        assert isinstance(result, dict)
        assert "error" not in result
        assert len(result["children"]) == 2

    def test_edit_memory_tool(self):
        """Test the edit_memory tool function."""
        add_memory = self.get_tool_function("add_memory")
        edit_memory = self.get_tool_function("edit_memory")
        read_memory = self.get_tool_function("read_memory")

        # Add a memory
        add_memory([], "test", content="old", tags=["old"], author="user")

        # Edit it
        result = edit_memory(position=["test"], content="new content", tags=["new", "updated"])

        assert isinstance(result, dict)
        assert "error" not in result

        # Verify changes
        read_result = read_memory(["test"])
        assert read_result["content"] == "new content"
        assert read_result["tags"] == ["new", "updated"]

    def test_remove_memory_tool(self):
        """Test the remove_memory tool function."""
        add_memory = self.get_tool_function("add_memory")
        remove_memory = self.get_tool_function("remove_memory")

        # Add a memory
        add_memory([], "to_remove", author="user")

        # Remove it
        result = remove_memory(["to_remove"])

        assert isinstance(result, dict)
        assert "error" not in result
        assert result["removed"] == "to_remove"


class TestMCPIntegration:
    """Test MCP server integration aspects."""

    def test_tools_registered(self):
        """Verify all expected tools are registered with MCP."""
        tools = mcp._tool_manager._tools
        tool_names = [tool.name for tool in tools.values()]

        expected_tools = ["add_memory", "read_memory", "list_children", "edit_memory", "remove_memory"]

        for expected in expected_tools:
            assert expected in tool_names, f"Tool {expected} not found in MCP server"

    def test_tool_metadata(self):
        """Verify tool metadata is properly set."""
        tools = mcp._tool_manager._tools
        for tool in tools.values():
            # Check that each tool has a name and description
            assert tool.name
            assert tool.description

            # Check specific tools have expected metadata
            if tool.name == "add_memory":
                assert "Add a new memory" in tool.description
                assert "position" in tool.description.lower()
            elif tool.name == "read_memory":
                assert "Read a memory" in tool.description
            elif tool.name == "list_children":
                assert "List all children" in tool.description
            elif tool.name == "edit_memory":
                assert "Edit a memory" in tool.description
            elif tool.name == "remove_memory":
                assert "Remove a memory" in tool.description

    def test_server_name(self):
        """Verify the server has the correct name."""
        assert mcp.name == "memory-server"
