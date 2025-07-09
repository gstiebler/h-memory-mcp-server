import pytest
from datetime import datetime
from src.models import Memory


class TestMemory:
    def test_memory_creation(self):
        """Test basic memory creation."""
        memory = Memory(
            description="test memory",
            content="test content",
            tags=["test", "sample"],
            author="test_user"
        )
        
        assert memory.description == "test memory"
        assert memory.content == "test content"
        assert memory.tags == ["test", "sample"]
        assert memory.author == "test_user"
        assert memory.access_count == 0
        assert len(memory.children) == 0
        assert memory.id is not None
        assert isinstance(memory.created_at, datetime)
        assert isinstance(memory.last_accessed, datetime)
        assert memory.updated_at is None

    def test_memory_creation_with_defaults(self):
        """Test memory creation with minimal required fields."""
        memory = Memory(
            description="minimal",
            author="user"
        )
        
        assert memory.description == "minimal"
        assert memory.content is None
        assert memory.tags == []
        assert memory.author == "user"
        assert memory.access_count == 0

    def test_find_child(self):
        """Test finding a child memory by description."""
        parent = Memory(description="parent", author="user")
        child1 = Memory(description="child1", author="user")
        child2 = Memory(description="child2", author="user")
        
        parent.children.append(child1)
        parent.children.append(child2)
        
        found = parent.find_child("child1")
        assert found == child1
        
        not_found = parent.find_child("nonexistent")
        assert not_found is None

    def test_update_access(self):
        """Test access metadata updates."""
        memory = Memory(description="test", author="user")
        original_count = memory.access_count
        original_time = memory.last_accessed
        
        memory.update_access()
        
        assert memory.access_count == original_count + 1
        assert memory.last_accessed > original_time

    def test_to_dict(self):
        """Test conversion to dictionary."""
        memory = Memory(
            description="test",
            content="content",
            tags=["tag1"],
            author="user"
        )
        child = Memory(description="child", author="user")
        memory.children.append(child)
        
        data = memory.to_dict()
        
        assert data['description'] == "test"
        assert data['content'] == "content"
        assert data['tags'] == ["tag1"]
        assert data['author'] == "user"
        assert data['access_count'] == 0
        assert 'created_at' in data
        assert 'last_accessed' in data
        assert 'id' in data
        assert len(data['children']) == 1
        assert data['children'][0]['description'] == "child"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'id': 'test-id',
            'description': 'test',
            'content': 'content',
            'tags': ['tag1', 'tag2'],
            'author': 'user',
            'created_at': '2025-01-09T10:00:00',
            'last_accessed': '2025-01-09T11:00:00',
            'access_count': 5,
            'children': [
                {
                    'id': 'child-id',
                    'description': 'child',
                    'content': None,
                    'tags': [],
                    'author': 'user',
                    'created_at': '2025-01-09T10:30:00',
                    'last_accessed': '2025-01-09T10:30:00',
                    'access_count': 0,
                    'children': []
                }
            ]
        }
        
        memory = Memory.from_dict(data)
        
        assert memory.id == 'test-id'
        assert memory.description == 'test'
        assert memory.content == 'content'
        assert memory.tags == ['tag1', 'tag2']
        assert memory.author == 'user'
        assert memory.access_count == 5
        assert len(memory.children) == 1
        assert memory.children[0].description == 'child'

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are inverses."""
        original = Memory(
            description="test",
            content="content",
            tags=["tag1", "tag2"],
            author="user"
        )
        original.updated_at = datetime.now()
        
        child = Memory(description="child", author="user")
        original.children.append(child)
        
        # Convert to dict and back
        data = original.to_dict()
        restored = Memory.from_dict(data)
        
        assert restored.description == original.description
        assert restored.content == original.content
        assert restored.tags == original.tags
        assert restored.author == original.author
        assert restored.id == original.id
        assert len(restored.children) == len(original.children)
        assert restored.children[0].description == original.children[0].description