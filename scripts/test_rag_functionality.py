import asyncio
import logging
from contextawarerag import DataManager
from rich.console import Console
from rich.table import Table
from rich import print as rprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

class RAGTester:
    def __init__(self):
        self.config = {
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
        try:
            self.rag_manager = DataManager(self.config)
            await self.rag_manager.initialize()
            rprint("[green]✓ RAG manager initialized successfully[/green]")
        except Exception as e:
            rprint(f"[red]✗ Failed to initialize RAG manager: {e}[/red]")
            raise

    async def test_database_connection(self):
        """Test database connections"""
        try:
            # Test MongoDB
            await self.rag_manager.db.command("ping")
            rprint("[green]✓ MongoDB connection successful[/green]")
            
            # Count documents
            count = await self.rag_manager.db.rag_content.count_documents({})
            rprint(f"[blue]ℹ Total documents in RAG: {count}[/blue]")
            
            return True
        except Exception as e:
            rprint(f"[red]✗ Database connection failed: {e}[/red]")
            return False

    async def display_sample_products(self):
        """Display sample products from RAG"""
        try:
            table = Table(title="Sample Products from RAG")
            table.add_column("Product ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Category", style="green")
            table.add_column("Price", style="yellow")

            async for doc in self.rag_manager.db.rag_content.find().limit(5):
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                
                # Extract product name from content
                name = next((line.split(": ")[1] for line in content.split("\n") 
                           if line.strip().startswith("Product:")), "N/A")
                
                table.add_row(
                    metadata.get("product_id", "N/A"),
                    name,
                    metadata.get("category", "N/A"),
                    f"${metadata.get('price', '0.00')}"
                )

            console.print(table)
            return True
        except Exception as e:
            rprint(f"[red]✗ Failed to display products: {e}[/red]")
            return False

    async def test_search_functionality(self):
        """Test search functionality"""
        try:
            search_terms = ["anti-aging", "moisturizer", "serum"]
            
            for term in search_terms:
                rprint(f"\n[yellow]Searching for: {term}[/yellow]")
                
                results = await self.rag_manager.db.rag_content.find({
                    "content": {"$regex": term, "$options": "i"}
                }).limit(3).to_list(length=None)
                
                if results:
                    rprint(f"[green]✓ Found {len(results)} results[/green]")
                    for doc in results:
                        rprint(f"[blue]Product ID: {doc['metadata'].get('product_id')}[/blue]")
                        rprint(f"Category: {doc['metadata'].get('category')}")
                        rprint("---")
                else:
                    rprint(f"[yellow]No results found for: {term}[/yellow]")
            
            return True
        except Exception as e:
            rprint(f"[red]✗ Search functionality failed: {e}[/red]")
            return False

    async def test_category_distribution(self):
        """Display category distribution"""
        try:
            pipeline = [
                {"$group": {
                    "_id": "$metadata.category",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            
            table = Table(title="Product Category Distribution")
            table.add_column("Category", style="cyan")
            table.add_column("Count", style="magenta", justify="right")
            
            async for result in self.rag_manager.db.rag_content.aggregate(pipeline):
                table.add_row(
                    str(result["_id"]),
                    str(result["count"])
                )
            
            console.print(table)
            return True
        except Exception as e:
            rprint(f"[red]✗ Failed to get category distribution: {e}[/red]")
            return False

async def main():
    tester = RAGTester()
    
    try:
        # Initialize
        await tester.initialize()
        
        # Run tests
        tests = [
            ("Database Connection", tester.test_database_connection()),
            ("Sample Products", tester.display_sample_products()),
            ("Search Functionality", tester.test_search_functionality()),
            ("Category Distribution", tester.test_category_distribution())
        ]
        
        # Run and collect results
        results = []
        for test_name, test_coro in tests:
            rprint(f"\n[yellow]Running test: {test_name}[/yellow]")
            result = await test_coro
            results.append((test_name, result))
        
        # Display summary
        rprint("\n[bold]Test Summary:[/bold]")
        for test_name, result in results:
            status = "[green]✓ Passed[/green]" if result else "[red]✗ Failed[/red]"
            rprint(f"{test_name}: {status}")
            
    except Exception as e:
        rprint(f"[red]Test execution failed: {e}[/red]")

if __name__ == "__main__":
    # Install rich if not installed
    try:
        import rich
    except ImportError:
        import subprocess
        subprocess.check_call(["pip", "install", "rich"])
        
    asyncio.run(main()) 