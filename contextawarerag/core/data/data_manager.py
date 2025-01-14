from typing import Dict, List, Optional, Any
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
import logging

logger = logging.getLogger(__name__)

class DataManagerError(Exception):
    pass

class DataManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pg_pool = None
        self.mongo_client = None
        self.redis_client = None
        self.db = None

    async def initialize(self):
        try:
            # MongoDB connection
            self.mongo_client = AsyncIOMotorClient(
                self.config['mongodb']['uri'],
                serverSelectionTimeoutMS=5000
            )
            self.db = self.mongo_client[self.config['mongodb']['database']]
            await self.mongo_client.admin.command('ping')
            
            # Redis connection
            self.redis_client = Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                socket_timeout=5
            )
            self.redis_client.ping()
            
            # PostgreSQL connection
            self.pg_pool = await asyncpg.create_pool(
                **self.config['postgres'],
                min_size=5,
                max_size=20
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize connections: {e}")
            raise DataManagerError(f"Initialization failed: {str(e)}")

    async def store_rag_content(
        self,
        content: str,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Store content for RAG with metadata"""
        document = {
            "content": content,
            "content_type": content_type,
            "metadata": metadata
        }
        result = await self.db.rag_content.insert_one(document)
        return str(result.inserted_id)

    async def get_product_data(self, product_id: str) -> Dict:
        """Get product data"""
        product = await self.db.products.find_one(
            {"product_id": product_id},
            {'_id': 0}
        )
        return product if product else {}