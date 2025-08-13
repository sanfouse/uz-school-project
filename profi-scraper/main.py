import asyncio
from src.scraper import Scraper


scraper = Scraper()


if __name__ == "__main__":
    asyncio.run(scraper.run())
