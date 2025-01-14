import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pprint import pprint

async def check_rag_data():
    # Connect to MongoDB
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.nuskin_rag
    
    # Get total count
    total_products = await db.rag_content.count_documents({})
    print(f"\nTotal products stored: {total_products}")
    
    # Get products by category
    categories = await db.rag_content.distinct("metadata.category")
    print("\nProducts by category:")
    for category in categories:
        count = await db.rag_content.count_documents({"metadata.category": category})
        print(f"{category}: {count} products")
    
    # Show sample products
    print("\nSample products:")
    async for product in db.rag_content.find().limit(3):
        print("\n---Product---")
        pprint(product)
        
    # Search functionality
    print("\nSearch for specific products:")
    query = {"content": {"$regex": "ageLOC", "$options": "i"}}
    async for product in db.rag_content.find(query).limit(2):
        print("\n---Matching Product---")
        pprint(product)

if __name__ == "__main__":
    asyncio.run(check_rag_data()) 