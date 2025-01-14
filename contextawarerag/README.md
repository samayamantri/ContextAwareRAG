# ContextAwareRAG

A high-performance context-aware Retrieval Augmented Generation (RAG) system designed for e-commerce and commission-based applications.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Integration Guide](#integration-guide)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Features

### Core Capabilities
- **Context Management**
  - Multi-turn conversation handling
  - User context persistence
  - Session management
  - Context window optimization

### Data Integration
- **Multi-Database Support**
  - MongoDB for document storage
  - Redis for caching
  - PostgreSQL for transactional data
  - Vector store integration

### Domain-Specific Features
- **E-commerce**
  - Product information retrieval
  - Inventory tracking
  - Order management
  - Price updates

- **Commission System**
  - Real-time commission calculation
  - Performance tracking
  - Multi-tier commission structures
  - Payment scheduling

## Installation
Create virtual environment
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
Install package
pip install -e ".[test]"
Start required services
docker-compose up -d

## Quick Start
python
from contextawarerag import DataManager
Initialize
config = {
'mongodb': {'uri': 'mongodb://localhost:27017', 'database': 'rag_db'},
'redis': {'host': 'localhost', 'port': 6379},
'postgres': {
'host': 'localhost',
'port': 5432,
'user': 'test_user',
'password': 'test_password',
'database': 'test_db'
}
}
async def main():
# Create manager instance
manager = DataManager(config)
await manager.initialize()
# Store content
content_id = await manager.store_rag_content(
content="Product description",
content_type="product",
metadata={"category": "electronics"}
)
# Retrieve product data
product = await manager.get_product_data("PROD123")

## Architecture

### Component Overview
ContextAwareRAG/Readme.md
ContextAwareRAG/
├── core/
│ ├── data/ # Data management
│ ├── vectorstore/ # Vector operations
│ ├── cache/ # Caching layer
│ └── processing/ # Data processing
├── models/ # ML models
│ ├── embeddings/ # Embedding models
│ ├── classifiers/ # Classification models
│ └── generators/ # Text generation models
├── api/ # API endpoints
│ ├── rest/ # REST API
│ └── graphql/ # GraphQL API
├── services/ # Business logic
│ ├── commission/ # Commission calculation
│ ├── products/ # Product management
│ └── users/ # User management
└── utils/ # Utility functions
    ├── logging/ # Logging utilities
    ├── config/ # Configuration management
    └── testing/ # Testing utilities

## Integration Guide

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- MongoDB
- Redis
- PostgreSQL

### Basic Integration

1. Install the package:


