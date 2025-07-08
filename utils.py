import json
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def extract_doctor(crawler, doctolibPage, js_code=None):
    # 1. Define a simple extraction schema using the validated working selector
    schema = {
            'name': 'Gastro-entérologues et hépatologues',
            'baseSelector': 'div:has(img.w-48):has(h2 button)',
            'fields': [
                {'name': 'name', 'selector': 'h2 button', 'type': 'text'},
                {'name': 'distance', 'selector': 'span:contains("km")', 'type': 'text'},
                {'name': 'insurance', 'selector': 'p:contains("Conventionné")', 'type': 'text'},
            ]
        }
    # 2. Create the extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    # 3. Set up your crawler config (if needed)
    config = CrawlerRunConfig(
        js_code=js_code,
        wait_for="css:body",
        page_timeout=30000,
        delay_before_return_html=5,
        cache_mode=CacheMode.BYPASS,
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
    
