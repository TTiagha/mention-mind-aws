import os
import sys
from pathlib import Path
from typing import Dict, Generator

import pytest

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path.absolute()))


@pytest.fixture(scope="session")
def test_config() -> Dict[str, str]:
    """Fixture for test configuration"""
    return {
        "test_data_dir": os.path.join(os.path.dirname(__file__), "test_data"),
    }


@pytest.fixture(autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """Setup any necessary test environment variables or configurations"""
    # Add any test environment setup here
    yield
    # Add any cleanup code here
