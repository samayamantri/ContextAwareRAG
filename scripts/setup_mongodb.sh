#!/bin/bash

# Check if MongoDB is installed
if ! command -v mongod &> /dev/null; then
    echo "MongoDB not found. Installing..."
    brew tap mongodb/brew
    brew install mongodb-community mongodb-database-tools mongosh
fi

# Start MongoDB service
echo "Starting MongoDB service..."
brew services start mongodb-community

# Wait for MongoDB to start
sleep 5

# Check MongoDB status
if brew services list | grep mongodb-community | grep started > /dev/null; then
    echo "MongoDB is running"
else
    echo "MongoDB failed to start"
    exit 1
fi

# Create database and collections
echo "Initializing database..."
mongosh --eval "
    db = db.getSiblingDB('nuskin_rag');
    db.createCollection('rag_content');
    db.rag_content.createIndex({ 'metadata.product_id': 1 });
    db.rag_content.createIndex({ 'metadata.category': 1 });
"

echo "Setup complete!"