import json
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def extract_doctor(crawler,doctolibPage):
    # 1. Define a simple extraction schema
    schema = {
            'name': 'Gastro-entérologues et hépatologues',
            'baseSelector': '.dl-card-content',
            'fields': [
                {'name': 'name', 'selector': 'h2', 'type': 'text'},
                {'name': 'distance', 'selector': 'span:contains("km")', 'type': 'text'},
                {'name': 'insurance', 'selector': 'p:contains("Conventionné")', 'type': 'text'},
            ]
        }
    # 2. Create the extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    # 3. Set up your crawler config (if needed)
    config = CrawlerRunConfig(
        # e.g., pass js_code or wait_for if the page is dynamic
        # wait_for="css:.crypto-row:nth-child(20)"
        cache_mode = CacheMode.BYPASS,
        extraction_strategy=extraction_strategy,
    )
    # 4. Run the crawl and extraction
    result = await crawler.arun(
        url=doctolibPage,
        config=config
    )
    if not result.success:
        print("Crawl failed:", result.error_message)
        return
    # 5. Parse the extracted JSON
    data = json.loads(result.extracted_content)
    return data
    
