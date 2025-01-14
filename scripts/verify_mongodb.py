import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_mongodb():
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        
        # Verify connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Get database
        db = client.nuskin_rag
        
        # Create indexes if needed
        await db.rag_content.create_index("metadata.product_id")
        await db.rag_content.create_index("metadata.category")
        
        # Print database stats
        stats = await db.command("dbstats")
        logger.info(f"Database stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(verify_mongodb()) 