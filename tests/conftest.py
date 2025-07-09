import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_storage_file():
    """Create a temporary file for memory storage."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)