db = db.getSiblingDB('nuskin_rag');

// Create collections
db.createCollection('rag_content');

// Create indexes
db.rag_content.createIndex({ "metadata.product_id": 1 });
db.rag_content.createIndex({ "metadata.category": 1 });

// Set up initial metadata
db.rag_content.insertOne({
    "content": "Test content",
    "content_type": "test",
    "metadata": {
        "test": true,
        "timestamp": new Date()
    }
}); 