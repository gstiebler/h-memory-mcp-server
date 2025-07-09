import pytest
import os
from src.memory_store import MemoryStore
from src.models import Memory


class TestMemoryStore:
    def test_initialization(self, temp_storage_file):
        """Test store initialization with empty file."""
        store = MemoryStore(temp_storage_file)
        
        assert store.root_memory is not None
        assert store.root_memory.description == "root"
        assert store.root_memory.author == "system"
        assert os.path.exists(temp_storage_file)

    def test_add_memory_to_root(self, temp_storage_file):
        """Test adding a memory to the root."""
        store = MemoryStore(temp_storage_file)
        
        result = store.add_memory(
            position=[],
            description="test",
            content="test content",
            tags=["tag1"],
            author="user"
        )
        
        assert "error" not in result
        assert result["description"] == "test"
        assert result["position"] == ["test"]
        assert "id" in result
        assert "created_at" in result
        
        # Verify it was actually added
        children = store.list_children([])
        assert len(children["children"]) == 1
        assert children["children"][0]["description"] == "test"

    def test_add_memory_nested(self, temp_storage_file):
        """Test adding nested memories."""
        store = MemoryStore(temp_storage_file)
        
        # Add parent
        store.add_memory([], "parent", None, [], "user")
        
        # Add child
        result = store.add_memory(
            position=["parent"],
            description="child",
            content="child content",
            tags=["nested"],
            author="user"
        )
        
        assert "error" not in result
        assert result["position"] == ["parent", "child"]
        
        # Verify structure
        parent_children = store.list_children(["parent"])
        assert len(parent_children["children"]) == 1
        assert parent_children["children"][0]["description"] == "child"

    def test_add_memory_duplicate(self, temp_storage_file):
        """Test adding a duplicate memory fails."""
        store = MemoryStore(temp_storage_file)
        
        store.add_memory([], "test", None, [], "user")
        result = store.add_memory([], "test", None, [], "user")
        
        assert "error" in result
        assert "already exists" in result["error"]

    def test_add_memory_invalid_position(self, temp_storage_file):
        """Test adding memory to non-existent position."""
        store = MemoryStore(temp_storage_file)
        
        result = store.add_memory(["nonexistent"], "test", None, [], "user")
        
        assert "error" in result
        assert "not found" in result["error"]

    def test_read_memory(self, temp_storage_file):
        """Test reading a memory."""
        store = MemoryStore(temp_storage_file)
        
        store.add_memory([], "test", "content", ["tag1", "tag2"], "author1")
        result = store.read_memory(["test"])
        
        assert "error" not in result
        assert result["description"] == "test"
        assert result["content"] == "content"
        assert result["tags"] == ["tag1", "tag2"]
        assert result["author"] == "author1"
        assert result["access_count"] == 1  # Incremented by read
        assert result["has_children"] is False
        assert "id" in result
        assert "created_at" in result
        assert "last_accessed" in result

    def test_read_memory_updates_access(self, temp_storage_file):
        """Test that reading updates access metadata."""
        store = MemoryStore(temp_storage_file)
        
        store.add_memory([], "test", None, [], "user")
        
        # First read
        first_read = store.read_memory(["test"])
        first_count = first_read["access_count"]
        
        # Second read
        second_read = store.read_memory(["test"])
        
        assert second_read["access_count"] == first_count + 1

    def test_read_memory_not_found(self, temp_storage_file):
        """Test reading non-existent memory."""
        store = MemoryStore(temp_storage_file)
        
        result = store.read_memory(["nonexistent"])
        
        assert "error" in result
        assert "not found" in result["error"]

    def test_list_children(self, temp_storage_file):
        """Test listing children."""
        store = MemoryStore(temp_storage_file)
        
        # Add some memories
        store.add_memory([], "parent", None, ["category"], "user")
        store.add_memory(["parent"], "child1", None, ["tag1"], "user")
        store.add_memory(["parent"], "child2", None, ["tag2"], "user")
        store.add_memory(["parent", "child1"], "grandchild", None, [], "user")
        
        # List root children
        root_children = store.list_children([])
        assert len(root_children["children"]) == 1
        assert root_children["children"][0]["description"] == "parent"
        
        # List parent children
        parent_children = store.list_children(["parent"])
        assert len(parent_children["children"]) == 2
        descriptions = [c["description"] for c in parent_children["children"]]
        assert "child1" in descriptions
        assert "child2" in descriptions
        
        # Check has_children flag
        child1_info = next(c for c in parent_children["children"] if c["description"] == "child1")
        assert child1_info["has_children"] is True
        
        child2_info = next(c for c in parent_children["children"] if c["description"] == "child2")
        assert child2_info["has_children"] is False

    def test_edit_memory(self, temp_storage_file):
        """Test editing a memory."""
        store = MemoryStore(temp_storage_file)
        
        store.add_memory([], "original", "original content", ["old"], "user")
        
        result = store.edit_memory(
            ["original"],
            description="updated",
            content="new content",
            tags=["new", "updated"]
        )
        
        assert "error" not in result
        assert result["description"] == "updated"
        assert "updated_at" in result
        
        # Verify changes
        read_result = store.read_memory(["updated"])
        assert read_result["content"] == "new content"
        assert read_result["tags"] == ["new", "updated"]
        assert read_result["updated_at"] is not None

    def test_edit_memory_partial(self, temp_storage_file):
        """Test partial edits (only some fields)."""
        store = MemoryStore(temp_storage_file)
        
        store.add_memory([], "test", "content", ["tag1"], "user")
        
        # Edit only content
        store.edit_memory(["test"], content="new content")
        
        read_result = store.read_memory(["test"])
        assert read_result["description"] == "test"  # Unchanged
        assert read_result["content"] == "new content"  # Changed
        assert read_result["tags"] == ["tag1"]  # Unchanged

    def test_edit_memory_duplicate_description(self, temp_storage_file):
        """Test editing to a description that already exists."""
        store = MemoryStore(temp_storage_file)
        
        store.add_memory([], "memory1", None, [], "user")
        store.add_memory([], "memory2", None, [], "user")
        
        result = store.edit_memory(["memory1"], description="memory2")
        
        assert "error" in result
        assert "already exists" in result["error"]

    def test_edit_root_fails(self, temp_storage_file):
        """Test that editing root memory fails."""
        store = MemoryStore(temp_storage_file)
        
        result = store.edit_memory([], description="new_root")
        
        assert "error" in result
        assert "Cannot edit root" in result["error"]

    def test_remove_memory(self, temp_storage_file):
        """Test removing a memory."""
        store = MemoryStore(temp_storage_file)
        
        store.add_memory([], "to_remove", None, [], "user")
        
        result = store.remove_memory(["to_remove"])
        
        assert "error" not in result
        assert result["removed"] == "to_remove"
        assert result["children_removed"] == 0
        
        # Verify it's gone
        children = store.list_children([])
        assert len(children["children"]) == 0

    def test_remove_memory_with_children(self, temp_storage_file):
        """Test removing a memory with children."""
        store = MemoryStore(temp_storage_file)
        
        store.add_memory([], "parent", None, [], "user")
        store.add_memory(["parent"], "child1", None, [], "user")
        store.add_memory(["parent"], "child2", None, [], "user")
        store.add_memory(["parent", "child1"], "grandchild", None, [], "user")
        
        result = store.remove_memory(["parent"])
        
        assert result["removed"] == "parent"
        assert result["children_removed"] == 3  # 2 children + 1 grandchild
        
        # Verify all are gone
        children = store.list_children([])
        assert len(children["children"]) == 0

    def test_remove_root_fails(self, temp_storage_file):
        """Test that removing root fails."""
        store = MemoryStore(temp_storage_file)
        
        result = store.remove_memory([])
        
        assert "error" in result
        assert "Cannot remove root" in result["error"]

    def test_persistence(self, temp_storage_file):
        """Test that data persists across store instances."""
        # Create first store and add data
        store1 = MemoryStore(temp_storage_file)
        store1.add_memory([], "persistent", "test data", ["tag"], "user")
        
        # Create second store with same file
        store2 = MemoryStore(temp_storage_file)
        
        # Verify data is loaded
        result = store2.read_memory(["persistent"])
        assert result["description"] == "persistent"
        assert result["content"] == "test data"
        assert result["tags"] == ["tag"]

    def test_thread_safety(self, temp_storage_file):
        """Test basic thread safety of operations."""
        import threading
        
        store = MemoryStore(temp_storage_file)
        results = []
        
        def add_memory(index):
            result = store.add_memory([], f"memory{index}", None, [], "user")
            results.append(result)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_memory, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify all succeeded
        assert len(results) == 5
        assert all("error" not in r for r in results)
        
        # Verify all memories exist
        children = store.list_children([])
        assert len(children["children"]) == 5