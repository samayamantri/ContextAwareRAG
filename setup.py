from setuptools import setup, find_packages
import os

# Read README.md if it exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="contextawarerag",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Database dependencies
        "asyncpg>=0.29.0",
        "motor>=3.3.2",
        "redis>=5.0.1",
        "pymongo>=4.6.1",
        
        # Web scraping
        "aiohttp>=3.8.1",
        "beautifulsoup4>=4.9.3",
        "fake-useragent>=1.1.1",
        
        # Async support
        "asyncio>=3.4.3",
        
        # Utilities
        "python-dotenv>=0.19.2",
        "pydantic>=2.0.0",
        "tenacity>=8.0.1",
    ],
    extras_require={
        'test': [
            'pytest>=7.4.4',
            'pytest-asyncio>=0.23.5',
            'pytest-docker>=2.0.1',
            'docker>=7.0.0',
        ],
        'dev': [
            'black>=22.3.0',
            'isort>=5.10.1',
            'mypy>=0.981',
            'flake8>=4.0.1',
        ],
        'chat': [
            'openai>=1.0.0',
            'langchain>=0.1.0',
            'tiktoken>=0.5.1',
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A context-aware RAG system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/contextawarerag",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 