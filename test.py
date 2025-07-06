#!/usr/bin/env python3

import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
import time

async def main():
    browser_conf = BrowserConfig(headless=False)
    js="""
(async () => {
    // Find and click the button with the specified name
    const acceptButton = document.querySelector('button');
    if (acceptButton && acceptButton.textContent.includes('Accepter & Fermer: Accepter')) {
        acceptButton.scrollIntoView();
        acceptButton.click();
        await new Promise(r => setTimeout(r, 500)); // Wait for half a second
    }
})();
    """
    config = CrawlerRunConfig(
        js_code=js
    )
    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url="https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14&page=1",
        )
        # print(result.markdown[:300])  # Show the first 300 characters of extracted text
    # crawler = AsyncWebCrawler(config=browser_conf)
    # result = await crawler.arun(
    #     url="https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14&page=1"
    # )
    # time.sleep(1000)

if __name__ == "__main__":
    asyncio.run(main())
