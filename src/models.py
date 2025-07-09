import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Memory(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    content: str | None = None
    tags: list[str] = Field(default_factory=list)
    author: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None
    access_count: int = 0
    last_accessed: datetime = Field(default_factory=datetime.now)
    children: list["Memory"] = Field(default_factory=list)

    def to_dict(self):
        """Convert memory to dictionary, including children."""
        data = self.model_dump(exclude={"children"})
        data["created_at"] = self.created_at.isoformat()
        data["last_accessed"] = self.last_accessed.isoformat()
        if self.updated_at:
            data["updated_at"] = self.updated_at.isoformat()
        data["children"] = [child.to_dict() for child in self.children]
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Create memory from dictionary, including children."""
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        if data.get("updated_at"):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        children_data = data.pop("children", [])
        memory = cls(**data)
        memory.children = [cls.from_dict(child) for child in children_data]
        return memory

    def find_child(self, description: str) -> Optional["Memory"]:
        """Find a direct child by description."""
        for child in self.children:
            if child.description == description:
                return child
        return None

    def update_access(self):
        """Update access count and last accessed time."""
        self.access_count += 1
        self.last_accessed = datetime.now()


# Enable forward reference resolution
Memory.model_rebuild()


# Type for memory position
Position = list[str]
