from typing import Dict, List, Any
from contextawarerag import DataManager
import logging

logger = logging.getLogger(__name__)

class ChatRAGIntegration:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'mongodb': {'uri': 'mongodb://localhost:27017', 'database': 'nuskin_rag'},
            'redis': {'host': 'localhost', 'port': 6379},
            'postgres': {
                'host': 'localhost',
                'port': 5432,
                'user': 'test_user',
                'password': 'test_password',
                'database': 'test_db'
            }
        }
        self.rag_manager = None

    async def initialize(self):
        """Initialize RAG manager"""
        self.rag_manager = DataManager(self.config)
        await self.rag_manager.initialize()

    async def search_products(self, query: str, category: str = None) -> List[Dict]:
        """Search products based on query"""
        try:
            search_criteria = {
                "content": {"$regex": query, "$options": "i"}
            }
            if category:
                search_criteria["metadata.category"] = category

            results = []
            async for doc in self.rag_manager.db.rag_content.find(search_criteria).limit(5):
                results.append({
                    "content": doc["content"],
                    "metadata": doc["metadata"]
                })
            return results
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []

    async def get_product_recommendations(self, context: Dict[str, Any]) -> List[Dict]:
        """Get product recommendations based on context"""
        try:
            # Extract relevant information from context
            user_interests = context.get('interests', [])
            previous_purchases = context.get('previous_purchases', [])
            
            # Build search criteria
            search_criteria = {
                "$or": [
                    {"metadata.category": {"$in": user_interests}},
                    {"metadata.product_id": {"$in": previous_purchases}}
                ]
            }
            
            recommendations = []
            async for doc in self.rag_manager.db.rag_content.find(search_criteria).limit(3):
                recommendations.append({
                    "content": doc["content"],
                    "metadata": doc["metadata"]
                })
            return recommendations
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []

    def format_product_response(self, products: List[Dict]) -> str:
        """Format product information for chat response"""
        if not products:
            return "I couldn't find any relevant products."

        response = "Here are some products that might interest you:\n\n"
        for product in products:
            content = product["content"]
            metadata = product["metadata"]
            response += f"🔹 {metadata.get('product_id', 'N/A')}\n"
            response += f"Price: ${metadata.get('price', '0.00')}\n"
            response += f"{content}\n\n"
        return response 