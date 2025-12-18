"""
pytest configuration for intelligent-automation tests
"""
import sys
import os

# Prevent pytest from discovering the parent __init__.py
# by removing it from sys.modules if already loaded
if 'intelligent-automation' in sys.modules:
    del sys.modules['intelligent-automation']

# Add the parent directory to path before importing test modules
# This avoids the relative import issue with the main package
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)

# Only add if not already in path
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Configure pytest-asyncio to use auto mode
pytest_plugins = ['pytest_asyncio']


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


# Prevent pytest from collecting the parent __init__.py
collect_ignore = ['../__init__.py']
