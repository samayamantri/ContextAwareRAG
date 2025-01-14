import pytest
from contextawarerag import DataManager

def test_data_manager_import():
    """Test that DataManager can be imported."""
    assert DataManager is not None

def test_data_manager_instantiation():
    """Test that DataManager can be instantiated."""
    config = {
        'mongodb': {'uri': 'mongodb://localhost:27017', 'database': 'test'},
        'redis': {'host': 'localhost', 'port': 6379},
        'postgres': {
            'host': 'localhost',
            'port': 5432,
            'user': 'test',
            'password': 'test',
            'database': 'test'
        }
    }
    manager = DataManager(config)
    assert manager is not None