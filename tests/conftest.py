import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture(scope="session")
def test_config():
    """Fixture for test configuration"""
    return {
        "test_data_dir": os.path.join(os.path.dirname(__file__), "test_data"),
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup any necessary test environment variables or configurations"""
    # Add any test environment setup here
    yield
    # Add any cleanup code here
