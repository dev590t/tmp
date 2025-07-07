#!/usr/bin/env python3
"""
Example demonstrating Ollama-powered schema generation for Doctolib
This script shows how to generate a reusable extraction schema using LLM
"""

import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, LLMConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


async def generate_doctolib_schema():
    """
    Generate an extraction schema for Doctolib using Ollama
    This is a one-time cost that creates a reusable schema
    """
    print("🧠 Generating Doctolib extraction schema using Ollama...")
    
    # Sample Doctolib URL
    url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14&page=1"
    
    browser_config = BrowserConfig(headless=False, verbose=True)
    
    # JavaScript to handle cookie consent
    js_code = """
    (async () => {
        await new Promise(r => setTimeout(r, 2000));
        
        // Handle cookie consent
        const acceptButton = document.querySelector('button:contains("Accepter")');
        if (acceptButton) {
            acceptButton.click();
            await new Promise(r => setTimeout(r, 1000));
        }
        
        await new Promise(r => setTimeout(r, 3000));
    })();
    """
    
    config = CrawlerRunConfig(
        js_code=js_code,
        wait_for="css:body",
        page_timeout=30000,
        delay_before_return_html=5,
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        try:
            # First, get the page content
            print("📄 Loading sample Doctolib page...")
            result = await crawler.arun(url=url, config=config)
            
            if not result.success:
                print(f"❌ Failed to load page: {result.error_message}")
                return None
            
            print("✅ Page loaded successfully")
            print(f"📊 Page content length: {len(result.cleaned_html)} characters")
            
            # Save sample HTML for inspection
            with open("sample_doctolib.html", "w", encoding="utf-8") as f:
                f.write(result.cleaned_html)
            print("💾 Saved sample HTML to sample_doctolib.html")
            
            # Configure Ollama LLM
            llm_config = LLMConfig(
                provider="ollama/llama3.2",  # You can change this to llama3.1, codellama, etc.
                api_token=None  # Not needed for Ollama
            )
            
            print("🔄 Analyzing page structure with Ollama...")
            print("   This may take a moment as Ollama processes the content...")
            
            # Generate schema using Ollama
            schema = JsonCssExtractionStrategy.generate_schema(
                result.cleaned_html,
                llm_config=llm_config,
                instruction="""
                Analyze this Doctolib search results page and create a comprehensive CSS extraction schema.
                
                The page contains a list of doctors/medical practitioners. For each doctor, extract:
                1. name: The doctor's full name (usually in h2 button elements)
                2. specialty: Medical specialty (e.g., "Gastro-entérologue et hépatologue")
                3. address: Complete address including street, postal code, and city
                4. distance: Distance from search location (e.g., "3,2 km")
                5. sector_info: Insurance sector information (e.g., "Conventionné secteur 1")
                6. profile_url: Link to the doctor's profile page if available
                
                Focus only on the main doctor listings. Ignore:
                - Navigation elements
                - Cookie banners
                - Footer content
                - Advertisements
                - Search filters
                
                Create precise CSS selectors that will work reliably for extracting this data.
                """
            )
            
            print("✅ Schema generated successfully!")
            
            # Save the generated schema
            with open("generated_doctolib_schema.json", "w", encoding="utf-8") as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            
            print("💾 Saved schema to generated_doctolib_schema.json")
            print("\n📋 Generated Schema:")
            print(json.dumps(schema, indent=2))
            
            return schema
            
        except Exception as e:
            print(f"❌ Error generating schema: {e}")
            return None


async def test_generated_schema(schema):
    """
    Test the generated schema on a sample page
    """
    if not schema:
        print("❌ No schema to test")
        return
    
    print("\n🧪 Testing generated schema...")
    
    url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14&page=1"
    
    browser_config = BrowserConfig(headless=False, verbose=True)
    
    js_code = """
    (async () => {
        await new Promise(r => setTimeout(r, 2000));
        const acceptButton = document.querySelector('button:contains("Accepter")');
        if (acceptButton) {
            acceptButton.click();
            await new Promise(r => setTimeout(r, 1000));
        }
        await new Promise(r => setTimeout(r, 3000));
    })();
    """
    
    config = CrawlerRunConfig(
        js_code=js_code,
        wait_for="css:body",
        page_timeout=30000,
        delay_before_return_html=5,
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(schema)
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        try:
            result = await crawler.arun(url=url, config=config)
            
            if result.success and result.extracted_content:
                print("✅ Schema test successful!")
                
                # Parse and display results
                try:
                    extracted_data = json.loads(result.extracted_content)
                    
                    if isinstance(extracted_data, list):
                        doctors_count = len(extracted_data)
                        print(f"👨‍⚕️ Extracted {doctors_count} doctors")
                        
                        # Show first few results
                        for i, doctor in enumerate(extracted_data[:3], 1):
                            print(f"\n{i}. Doctor:")
                            for key, value in doctor.items():
                                if value:
                                    print(f"   {key}: {value}")
                    
                    # Save test results
                    with open("schema_test_results.json", "w", encoding="utf-8") as f:
                        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n💾 Saved test results to schema_test_results.json")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing extracted data: {e}")
                    print(f"Raw content: {result.extracted_content[:500]}...")
            
            else:
                print(f"❌ Schema test failed: {result.error_message}")
                
        except Exception as e:
            print(f"❌ Error testing schema: {e}")


async def main():
    """
    Main function to demonstrate schema generation and testing
    """
    print("🚀 Doctolib Schema Generation with Ollama")
    print("=" * 50)
    
    print("\n📋 This example will:")
    print("1. Load a sample Doctolib page")
    print("2. Use Ollama to analyze the page structure")
    print("3. Generate a CSS extraction schema")
    print("4. Test the schema on the same page")
    print("5. Save the schema for reuse")
    
    print("\n⚠️  Prerequisites:")
    print("- Ollama must be installed and running")
    print("- llama3.2 model should be available (or change the model in the code)")
    print("- Internet connection for accessing Doctolib")
    
    input("\nPress Enter to continue...")
    
    try:
        # Step 1: Generate schema
        schema = await generate_doctolib_schema()
        
        if schema:
            # Step 2: Test the schema
            await test_generated_schema(schema)
            
            print("\n✅ Schema generation and testing completed!")
            print("\nFiles created:")
            print("- sample_doctolib.html: Sample page content")
            print("- generated_doctolib_schema.json: Generated extraction schema")
            print("- schema_test_results.json: Test extraction results")
            
            print("\n🔄 You can now use the generated schema in your scraper:")
            print("python ollama_doctolib_scraper.py --load-schema generated_doctolib_schema.json")
        
        else:
            print("❌ Schema generation failed")
    
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())