import asyncio
import aiohttp
import logging
from bs4 import BeautifulSoup
from contextawarerag import DataManager
from typing import List, Dict, Any
import json
import time
from fake_useragent import UserAgent
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NuSkinScraper:
    def __init__(self):
        self.base_url = "https://www.nuskin.com"
        self.categories = [
            "/us/en/catalog/exfoliators",
            "/us/en/catalog/hair_care",
            "/us/en/catalog/anti-aging",
            "/us/en/catalog/dark_circles_and_puffiness",
            "/us/en/catalog/tru_face"
        ]
        self.rag_manager = None
        self.user_agent = UserAgent()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }

    async def initialize_rag(self):
        """Initialize RAG manager"""
        try:
            config = {
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
            self.rag_manager = DataManager(config)
            await self.rag_manager.initialize()
            logger.info("RAG manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG manager: {e}")
            raise

    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        """Fetch page content with retry logic"""
        retries = 3
        delay = 1
        
        for attempt in range(retries):
            try:
                self.headers['User-Agent'] = self.user_agent.random
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    if response.status == 200:
                        logger.info(f"Successfully fetched {url}")
                        return await response.text()
                    logger.warning(f"Failed to fetch {url}, status: {response.status}")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (attempt + 1))
                    continue
        return ""

    async def parse_product(self, html: str, category: str) -> Dict[str, Any]:
        """Parse product details from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        product = {}
        
        try:
            # Product name
            name_elem = soup.select_one('.product-name, .product-title, h1')
            if name_elem:
                product['name'] = name_elem.text.strip()

            # Price
            price_elem = soup.select_one('.product-price, .price-sales, .price')
            if price_elem:
                price_text = price_elem.text.strip()
                # Extract numbers from price text
                price = ''.join(c for c in price_text if c.isdigit() or c == '.')
                product['price'] = price

            # Description
            desc_elem = soup.select_one('.product-description, .description, .product-details')
            if desc_elem:
                product['description'] = desc_elem.text.strip()

            # Benefits
            benefits = []
            benefit_elems = soup.select('.benefits li, .product-benefits li, .key-benefits li')
            for elem in benefit_elems:
                benefits.append(elem.text.strip())
            product['benefits'] = benefits

            # Ingredients
            ingr_elem = soup.select_one('.ingredients, .ingredient-list')
            if ingr_elem:
                product['ingredients'] = ingr_elem.text.strip()

            # Product ID/SKU
            sku_elem = soup.select_one('[data-product-id], [data-sku]')
            if sku_elem:
                product['id'] = sku_elem.get('data-product-id') or sku_elem.get('data-sku')
            else:
                product['id'] = f"NSK-{random.randint(10000, 99999)}"

            product['category'] = category
            logger.info(f"Successfully parsed product: {product.get('name', 'Unknown')}")
            return product
            
        except Exception as e:
            logger.error(f"Error parsing product: {e}")
            return {}

    async def get_product_urls(self, html: str) -> List[str]:
        """Extract product URLs from category page"""
        soup = BeautifulSoup(html, 'html.parser')
        urls = []
        
        # Try different selectors for product links
        selectors = [
            '.product-tile a[href*="/product/"]',
            '.product-grid a[href*="/product/"]',
            '.product-list a[href*="/product/"]',
            'a[href*="/product/"]'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            if links:
                for link in links:
                    href = link.get('href')
                    if href and '/product/' in href:
                        full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                        urls.append(full_url)
                break
                
        logger.info(f"Found {len(urls)} product URLs")
        return urls

    async def store_product_in_rag(self, product: Dict[str, Any]):
        """Store product in RAG system"""
        try:
            if not product:
                return

            content = f"""
            Product: {product.get('name', 'N/A')}
            Description: {product.get('description', 'N/A')}
            Benefits: {', '.join(product.get('benefits', []))}
            Ingredients: {product.get('ingredients', 'N/A')}
            """

            metadata = {
                "product_id": product.get('id', 'N/A'),
                "category": product.get('category', 'Unknown'),
                "price": product.get('price', '0.00'),
                "url": product.get('url', 'N/A')
            }

            await self.rag_manager.store_rag_content(
                content=content.strip(),
                content_type="product",
                metadata=metadata
            )

            logger.info(f"Stored product: {product.get('name', 'Unknown')}")

        except Exception as e:
            logger.error(f"Error storing product in RAG: {e}")

    async def scrape_products(self, limit: int = 100):
        """Main scraping function"""
        async with aiohttp.ClientSession() as session:
            products_stored = 0
            
            for category in self.categories:
                if products_stored >= limit:
                    break

                category_url = f"{self.base_url}{category}"
                logger.info(f"Scraping category: {category_url}")
                
                # Fetch category page
                category_html = await self.fetch_page(session, category_url)
                if not category_html:
                    continue
                
                # Get product URLs
                product_urls = await self.get_product_urls(category_html)
                
                for url in product_urls:
                    if products_stored >= limit:
                        break

                    # Add delay to avoid rate limiting
                    await asyncio.sleep(random.uniform(1, 2))
                    
                    # Fetch and parse product
                    product_html = await self.fetch_page(session, url)
                    if product_html:
                        product_data = await self.parse_product(product_html, category)
                        if product_data:
                            product_data['url'] = url
                            await self.store_product_in_rag(product_data)
                            products_stored += 1
                            logger.info(f"Progress: {products_stored}/{limit} products stored")

async def main():
    try:
        scraper = NuSkinScraper()
        await scraper.initialize_rag()
        await scraper.scrape_products(limit=100)
        logger.info("Product population completed!")
    except Exception as e:
        logger.error(f"Main execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())