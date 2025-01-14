import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pprint import pprint

async def run_queries():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.nuskin_rag
    
    # 1. Price range analysis
    pipeline = [
        {
            "$group": {
                "_id": "$metadata.category",
                "avg_price": {"$avg": "$metadata.price"},
                "min_price": {"$min": "$metadata.price"},
                "max_price": {"$max": "$metadata.price"}
            }
        }
    ]
    
    print("\nPrice Analysis by Category:")
    async for result in db.rag_content.aggregate(pipeline):
        pprint(result)
    
    # 2. Products without benefits
    print("\nProducts missing benefits:")
    async for product in db.rag_content.find({"benefits": {"$size": 0}}):
        print(f"- {product['metadata']['product_id']}: {product['content'][:100]}...")
    
    # 3. Most common ingredients
    print("\nCommon ingredients:")
    pipeline = [
        {"$group": {
            "_id": "$metadata.ingredients",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    async for result in db.rag_content.aggregate(pipeline):
        pprint(result)

if __name__ == "__main__":
    asyncio.run(run_queries()) 