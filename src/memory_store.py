import json
import os
import threading
from datetime import datetime
from typing import Any

from .models import Memory, Position


class MemoryStore:
    def __init__(self, storage_path: str = "memories.json"):
        self.storage_path = storage_path
        self.lock = threading.Lock()
        self.root_memory = None
        self._load()

    def _load(self):
        """Load memories from JSON file."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)
                    self.root_memory = Memory.from_dict(data)
            except Exception:
                # If file is corrupted, start fresh
                self._init_root()
        else:
            self._init_root()

    def _init_root(self):
        """Initialize root memory."""
        self.root_memory = Memory(description="root", author="system", content="Root of all memories")
        self._save()

    def _save(self):
        """Save memories to JSON file."""
        with self.lock:
            self._save_without_lock()

    def _save_without_lock(self):
        """Save memories to JSON file without acquiring lock (internal use only)."""
        data = self.root_memory.to_dict()
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def _navigate_to_position(self, position: Position) -> Memory | None:
        """Navigate to a memory at the given position."""
        current = self.root_memory

        for description in position:
            if current is None:
                return None
            child = current.find_child(description)
            if not child:
                return None
            current = child

        return current

    def add_memory(
        self, position: Position, description: str, content: str | None, tags: list[str], author: str
    ) -> dict[str, Any]:
        """Add a new memory at the specified position."""
        with self.lock:
            parent = self._navigate_to_position(position)
            if not parent:
                return {"error": f"Position {position} not found"}

            # Check if memory with same description already exists
            if parent.find_child(description):
                return {"error": f"Memory '{description}' already exists at this position"}

            new_memory = Memory(description=description, content=content, tags=tags, author=author)

            parent.children.append(new_memory)
            self._save_without_lock()

            return {
                "id": new_memory.id,
                "description": new_memory.description,
                "position": position + [description],
                "created_at": new_memory.created_at.isoformat(),
            }

    def read_memory(self, position: Position) -> dict[str, Any]:
        """Read a memory at the specified position."""
        memory = self._navigate_to_position(position)
        if not memory:
            return {"error": f"Memory at position {position} not found"}

        # Update access metadata
        memory.update_access()
        self._save()

        return {
            "id": memory.id,
            "description": memory.description,
            "content": memory.content,
            "tags": memory.tags,
            "author": memory.author,
            "created_at": memory.created_at.isoformat(),
            "updated_at": memory.updated_at.isoformat() if memory.updated_at else None,
            "access_count": memory.access_count,
            "last_accessed": memory.last_accessed.isoformat(),
            "has_children": len(memory.children) > 0,
        }

    def list_children(self, position: Position) -> dict[str, Any]:
        """List children of a memory at the specified position."""
        memory = self._navigate_to_position(position)
        if not memory:
            return {"error": f"Memory at position {position} not found"}

        children = [
            {
                "description": child.description,
                "content": child.content,
                "children_count": len(child.children),
                "tags": child.tags,
            }
            for child in memory.children
        ]

        return {"position": position, "children": children}

    def edit_memory(
        self,
        position: Position,
        description: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Edit a memory at the specified position."""
        with self.lock:
            memory = self._navigate_to_position(position)
            if not memory:
                return {"error": f"Memory at position {position} not found"}

            # Don't allow editing root
            if memory == self.root_memory:
                return {"error": "Cannot edit root memory"}

            # Update fields if provided
            if description is not None:
                # Check if new description conflicts with siblings
                parent_position = position[:-1]
                parent = self._navigate_to_position(parent_position) if parent_position else self.root_memory

                if parent is not None:
                    for sibling in parent.children:
                        if sibling != memory and sibling.description == description:
                            return {"error": f"Memory '{description}' already exists at this level"}

                memory.description = description

            if content is not None:
                memory.content = content

            if tags is not None:
                memory.tags = tags

            memory.updated_at = datetime.now()
            self._save_without_lock()

            return {
                "id": memory.id,
                "description": memory.description,
                "updated_at": memory.updated_at.isoformat(),
            }

    def remove_memory(self, position: Position) -> dict[str, Any]:
        """Remove a memory and all its children."""
        with self.lock:
            if not position:
                return {"error": "Cannot remove root memory"}

            parent_position = position[:-1]
            parent = self._navigate_to_position(parent_position) if parent_position else self.root_memory

            if not parent:
                return {"error": f"Parent position {parent_position} not found"}

            target_description = position[-1]

            # Find and remove the child
            for i, child in enumerate(parent.children):
                if child.description == target_description:
                    removed = parent.children.pop(i)
                    self._save_without_lock()
                    return {
                        "removed": removed.description,
                        "children_removed": self._count_all_children(removed),
                    }

            return {"error": f"Memory '{target_description}' not found at position {parent_position}"}

    def _count_all_children(self, memory: Memory) -> int:
        """Count all descendants of a memory."""
        count = len(memory.children)
        for child in memory.children:
            count += self._count_all_children(child)
        return count
