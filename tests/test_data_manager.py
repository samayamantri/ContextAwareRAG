import pytest
from contextawarerag.core.data.data_manager import DataManager

@pytest.fixture
async def data_manager():
    config = {
        'postgres': {
            'host': 'localhost',
            'port': 5432,
            'user': 'test_user',
            'password': 'test_password',
            'database': 'test_db'
        },
        'mongodb': {
            'uri': 'mongodb://localhost:27017',
            'database': 'test_rag_db'
        },
        'redis': {
            'host': 'localhost',
            'port': 6379
        },
        'opensearch': {
            'hosts': ['http://localhost:9200'],
            'auth': ('admin', 'admin')
        }
    }
    
    manager = DataManager(config)
    await manager.initialize()
    return manager

@pytest.mark.asyncio
async def test_store_and_retrieve_content(data_manager):
    # Test data
    content = "Test product description"
    content_type = "product"
    metadata = {
        "unique_id": "TEST001",
        "title": "Test Product",
        "tags": ["test"]
    }
    
    # Store content
    content_id = await data_manager.store_rag_content(
        content=content,
        content_type=content_type,
        metadata=metadata
    )
    
    assert content_id is not None

@pytest.mark.asyncio
async def test_product_operations(data_manager):
    product_id = "TEST_PROD_001"
    
    # Test product data storage
    await data_manager.db.products.insert_one({
        "product_id": product_id,
        "name": "Test Product",
        "price": 99.99,
        "inventory": 100
    })
    
    # Test retrieval
    product = await data_manager.get_product_data(product_id)
    assert product is not None
    assert product["product_id"] == product_id