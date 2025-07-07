#!/usr/bin/env python3

import asyncio
import json
import csv
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, LLMConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


@dataclass
class Doctor:
    """Data class to represent a doctor's information"""
    name: str
    specialty: str
    address: str
    distance: Optional[str] = None
    sector_info: Optional[str] = None
    profile_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'specialty': self.specialty,
            'address': self.address,
            'distance': self.distance,
            'sector_info': self.sector_info,
            'profile_url': self.profile_url
        }


class LLMDoctolibScraper:
    """Advanced Doctolib scraper using LLM for automatic schema generation"""
    
    def __init__(self, base_url: str, max_pages: int = 3, llm_config: Optional[LLMConfig] = None):
        """
        Initialize the scraper with LLM-powered schema generation
        
        Args:
            base_url: The base URL for the search (without page parameter)
            max_pages: Maximum number of pages to scrape
            llm_config: LLMConfig instance (default: Groq Llama-4-Scout model)
        """
        self.base_url = self._clean_base_url(base_url)
        self.max_pages = max_pages
        self.llm_config = llm_config or self._get_default_llm_config()
        self.doctors: List[Doctor] = []
        self.extraction_schema = None
        
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=True
        )
        
        # JavaScript to handle cookie consent and page interactions
        self.js_code = """
        (async () => {
            console.log("Starting page interaction...");
            
            // Wait for initial page load
            await new Promise(r => setTimeout(r, 2000));
            
            // Handle cookie consent with multiple selectors
            const cookieSelectors = [
                'button:contains("Accepter")',
                'button[data-testid="accept-all-cookies"]',
                '.cookie-consent button',
                'button:contains("Accept")',
                '.gdpr-accept'
            ];
            
            for (const selector of cookieSelectors) {
                try {
                    const button = document.querySelector(selector);
                    if (button && button.offsetParent !== null) {
                        console.log(`Clicking cookie consent: ${selector}`);
                        button.click();
                        await new Promise(r => setTimeout(r, 1000));
                        break;
                    }
                } catch (e) {
                    // Continue to next selector
                }
            }
            
            // Wait for content to fully load
            await new Promise(r => setTimeout(r, 3000));
            
            // Log some debug info
            const doctorElements = document.querySelectorAll('h2 button');
            console.log(`Found ${doctorElements.length} potential doctor elements`);
            
            console.log("Page interaction completed");
        })();
        """
    
    def _get_default_llm_config(self) -> LLMConfig:
        """
        Get default LLM configuration using Groq's Llama-4-Scout model
        """
        return LLMConfig(
            provider="groq/meta-llama/llama-4-scout-17b-16e-instruct",
            api_token="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",
            temprature=0.1,
            max_tokens=4000
        )
    
    def _clean_base_url(self, url: str) -> str:
        """Clean the base URL by removing page parameters"""
        if "&page=" in url:
            return url.split("&page=")[0]
        elif "?page=" in url:
            return url.split("?page=")[0]
        return url
    
    def _build_page_url(self, page_number: int) -> str:
        """Build URL for a specific page number"""
        if '?' in self.base_url:
            return f"{self.base_url}&page={page_number}"
        else:
            return f"{self.base_url}?page={page_number}"
    
    async def generate_extraction_schema(self) -> dict:
        """
        Generate extraction schema using Ollama LLM by analyzing the first page
        This is a one-time cost that creates a reusable schema
        """
        print(f"🧠 Generating extraction schema using LLM: {self.llm_config.provider}")
        
        # First, get a sample page to analyze
        sample_url = self._build_page_url(1)
        
        config = CrawlerRunConfig(
            js_code=self.js_code,
            wait_for="css:body",
            page_timeout=30000,
            delay_before_return_html=5,
            cache_mode=CacheMode.BYPASS
        )
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            try:
                result = await crawler.arun(url=sample_url, config=config)
                
                if not result.success:
                    raise Exception(f"Failed to load sample page: {result.error_message}")
                
                print("✅ Sample page loaded successfully")
                
                print(f"🔄 Analyzing page structure with {self.llm_config.provider}...")
                
                # Generate schema using the sample HTML
                schema = JsonCssExtractionStrategy.generate_schema(
                    result.cleaned_html,
                    llm_config=self.llm_config,
                    instruction="""
                    Analyze this Doctolib search results page and create a CSS extraction schema to extract doctor information.
                    Each doctor entry should include:
                    - name: Doctor's full name
                    - specialty: Medical specialty
                    - address: Full address including street and city
                    - distance: Distance from search location (if available)
                    - sector_info: Insurance sector information (if available)
                    - profile_url: Link to doctor's profile (if available)
                    
                    Focus on the main doctor listings, ignore navigation, ads, and footer content.
                    """
                )
                
                print("✅ Schema generated successfully!")
                print(f"📋 Schema preview: {json.dumps(schema, indent=2)[:500]}...")
                
                self.extraction_schema = schema
                return schema
                
            except Exception as e:
                print(f"❌ Error generating schema: {e}")
                print("🔄 Falling back to manual schema...")
                
                # Fallback to a manually created schema
                fallback_schema = {
                    "name": "doctors",
                    "baseSelector": "div:has(h2 button)",
                    "fields": [
                        {
                            "name": "name",
                            "selector": "h2 button",
                            "type": "text"
                        },
                        {
                            "name": "specialty",
                            "selector": "p",
                            "type": "text"
                        },
                        {
                            "name": "address",
                            "selector": "p:contains('Rue'), p:contains('Boulevard'), p:contains('Avenue')",
                            "type": "text"
                        },
                        {
                            "name": "distance",
                            "selector": "span:contains('km')",
                            "type": "text"
                        },
                        {
                            "name": "sector_info",
                            "selector": "p:contains('Conventionné')",
                            "type": "text"
                        }
                    ]
                }
                
                self.extraction_schema = fallback_schema
                return fallback_schema
    
    async def scrape_page(self, page_number: int) -> List[Doctor]:
        """Scrape a single page using the generated schema"""
        page_url = self._build_page_url(page_number)
        print(f"📄 Scraping page {page_number}: {page_url}")
        
        # Ensure we have a schema
        if not self.extraction_schema:
            await self.generate_extraction_schema()
        
        config = CrawlerRunConfig(
            js_code=self.js_code,
            wait_for="css:body",
            page_timeout=30000,
            delay_before_return_html=5,
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=JsonCssExtractionStrategy(self.extraction_schema)
        )
        
        doctors = []
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            try:
                result = await crawler.arun(url=page_url, config=config)
                
                if result.success and result.extracted_content:
                    print(f"✅ Successfully loaded page {page_number}")
                    
                    # Parse the extracted JSON
                    try:
                        extracted_data = json.loads(result.extracted_content)
                        
                        # Handle both list and single object responses
                        if isinstance(extracted_data, list):
                            data_list = extracted_data
                        elif isinstance(extracted_data, dict):
                            data_list = [extracted_data]
                        else:
                            print(f"⚠️ Unexpected data format: {type(extracted_data)}")
                            data_list = []
                        
                        for item in data_list:
                            if isinstance(item, dict) and item.get('name'):
                                doctor = Doctor(
                                    name=item.get('name', '').strip(),
                                    specialty=item.get('specialty', 'Unknown').strip(),
                                    address=item.get('address', 'Unknown').strip(),
                                    distance=item.get('distance', '').strip() or None,
                                    sector_info=item.get('sector_info', '').strip() or None,
                                    profile_url=item.get('profile_url', '').strip() or None
                                )
                                
                                # Only add if we have a valid name
                                if doctor.name and doctor.name != 'Unknown':
                                    doctors.append(doctor)
                        
                        print(f"👨‍⚕️ Found {len(doctors)} doctors on page {page_number}")
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Error parsing extracted JSON: {e}")
                        print(f"Raw content: {result.extracted_content[:200]}...")
                        
                else:
                    print(f"❌ Failed to load page {page_number}: {result.error_message}")
                    
            except Exception as e:
                print(f"❌ Error scraping page {page_number}: {e}")
        
        return doctors
    
    async def scrape_all_pages(self) -> List[Doctor]:
        """Scrape all pages using the Ollama-generated schema"""
        print(f"🚀 Starting Ollama-powered scraping of {self.max_pages} pages from Doctolib")
        print(f"🔗 Base URL: {self.base_url}")
        print(f"🧠 Using LLM: {self.llm_config.provider}")
        
        # Generate schema first (one-time cost)
        await self.generate_extraction_schema()
        
        all_doctors = []
        
        for page_num in range(1, self.max_pages + 1):
            try:
                page_doctors = await self.scrape_page(page_num)
                all_doctors.extend(page_doctors)
                
                # Add delay between pages to be respectful
                if page_num < self.max_pages:
                    print(f"⏳ Waiting 2 seconds before next page...")
                    await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"❌ Error on page {page_num}: {e}")
                continue
        
        self.doctors = all_doctors
        print(f"🎉 Total doctors found: {len(all_doctors)}")
        return all_doctors
    
    def save_schema(self, filename: str = "doctolib_schema.json"):
        """Save the generated schema for reuse"""
        if self.extraction_schema:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.extraction_schema, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved extraction schema to {filename}")
    
    def load_schema(self, filename: str = "doctolib_schema.json"):
        """Load a previously generated schema"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.extraction_schema = json.load(f)
            print(f"📂 Loaded extraction schema from {filename}")
            return True
        except FileNotFoundError:
            print(f"⚠️ Schema file {filename} not found")
            return False
    
    def save_to_json(self, filename: str = "ollama_doctors.json"):
        """Save scraped doctors to JSON file"""
        data = [doctor.to_dict() for doctor in self.doctors]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(data)} doctors to {filename}")
    
    def save_to_csv(self, filename: str = "ollama_doctors.csv"):
        """Save scraped doctors to CSV file"""
        if not self.doctors:
            print("⚠️ No doctors to save")
            return
        
        fieldnames = ['name', 'specialty', 'address', 'distance', 'sector_info', 'profile_url']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for doctor in self.doctors:
                writer.writerow(doctor.to_dict())
        
        print(f"💾 Saved {len(self.doctors)} doctors to {filename}")
    
    def print_summary(self):
        """Print a summary of scraped doctors"""
        if not self.doctors:
            print("❌ No doctors found")
            return
        
        print(f"\n{'='*60}")
        print(f"📊 OLLAMA-POWERED SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total doctors found: {len(self.doctors)}")
        print(f"Pages scraped: {self.max_pages}")
        print(f"LLM used: {self.llm_config.provider}")
        
        # Count specialties
        specialties = {}
        for doctor in self.doctors:
            spec = doctor.specialty
            specialties[spec] = specialties.get(spec, 0) + 1
        
        print(f"\nSpecialties found:")
        for spec, count in specialties.items():
            print(f"  • {spec}: {count}")
        
        # Show first few doctors as examples
        print(f"\n📋 First 3 doctors:")
        for i, doctor in enumerate(self.doctors[:3], 1):
            print(f"\n{i}. {doctor.name}")
            print(f"   Specialty: {doctor.specialty}")
            print(f"   Address: {doctor.address}")
            if doctor.distance:
                print(f"   Distance: {doctor.distance}")
            if doctor.sector_info:
                print(f"   Sector: {doctor.sector_info}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Scrape doctors from Doctolib using LLM-powered schema generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default Groq settings
  python ollama_doctolib_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue"
  
  # Use different LLM provider and model
  python ollama_doctolib_scraper.py --url "URL" --llm-provider openai --llm-model gpt-4 --llm-api-key YOUR_KEY
  
  # Use Ollama local model
  python ollama_doctolib_scraper.py --url "URL" --llm-provider ollama --llm-model llama3.2
  
  # Load existing schema (skip generation)
  python ollama_doctolib_scraper.py --url "URL" --load-schema doctolib_schema.json
        """
    )
    
    parser.add_argument(
        '--url', 
        required=True,
        help='Base URL for Doctolib search'
    )
    
    parser.add_argument(
        '--pages', 
        type=int, 
        default=3,
        help='Number of pages to scrape (default: 3)'
    )
    
    parser.add_argument(
        '--llm-provider',
        default='groq',
        choices=['groq', 'openai', 'ollama'],
        help='LLM provider to use (default: groq)'
    )
    
    parser.add_argument(
        '--llm-model',
        default='meta-llama/llama-4-scout-17b-16e-instruct',
        help='LLM model to use (default: meta-llama/llama-4-scout-17b-16e-instruct for Groq)'
    )
    
    parser.add_argument(
        '--llm-api-key',
        help='API key for the LLM provider (default: uses built-in Groq key)'
    )
    
    parser.add_argument(
        '--json',
        default='ollama_doctors.json',
        help='Output JSON filename (default: ollama_doctors.json)'
    )
    
    parser.add_argument(
        '--csv',
        default='ollama_doctors.csv', 
        help='Output CSV filename (default: ollama_doctors.csv)'
    )
    
    parser.add_argument(
        '--save-schema',
        default='doctolib_schema.json',
        help='Save generated schema to file (default: doctolib_schema.json)'
    )
    
    parser.add_argument(
        '--load-schema',
        help='Load existing schema from file (skips generation)'
    )
    
    return parser.parse_args()


async def main():
    """Main function"""
    # If run directly, use default parameters
    if len(__import__('sys').argv) == 1:
        # Default configuration
        BASE_URL = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
        MAX_PAGES = 3
        JSON_FILE = "llm_doctors.json"
        CSV_FILE = "llm_doctors.csv"
        SCHEMA_FILE = "doctolib_schema.json"
        LOAD_SCHEMA = None
        LLM_CONFIG = None  # Use default Groq config
        
        print("🔧 Using default configuration:")
        print(f"   URL: {BASE_URL}")
        print(f"   Pages: {MAX_PAGES}")
        print(f"   LLM: Groq meta-llama/llama-4-scout-17b-16e-instruct (default)")
        
    else:
        # Parse command line arguments
        args = parse_arguments()
        BASE_URL = args.url
        MAX_PAGES = args.pages
        JSON_FILE = args.json
        CSV_FILE = args.csv
        SCHEMA_FILE = args.save_schema
        LOAD_SCHEMA = args.load_schema
        
        # Create LLM config from arguments
        api_key = args.llm_api_key
        if not api_key and args.llm_provider == 'groq':
            api_key = "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"
        
        if args.llm_provider == 'ollama':
            LLM_CONFIG = LLMConfig(
                provider=f"ollama/{args.llm_model}",
                api_token=None
            )
        else:
            LLM_CONFIG = LLMConfig(
                provider=f"{args.llm_provider}/{args.llm_model}",
                api_token=api_key,
                temprature=0.1,
                max_tokens=4000
            )
        
        print("🔧 Using command line configuration:")
        print(f"   URL: {BASE_URL}")
        print(f"   Pages: {MAX_PAGES}")
        print(f"   LLM: {args.llm_provider} {args.llm_model}")
    
    try:
        # Create scraper
        scraper = LLMDoctolibScraper(BASE_URL, MAX_PAGES, LLM_CONFIG)
        
        # Load existing schema if specified
        if LOAD_SCHEMA:
            if scraper.load_schema(LOAD_SCHEMA):
                print("✅ Using existing schema (skipping generation)")
            else:
                print("⚠️ Could not load schema, will generate new one")
        
        # Scrape all pages
        doctors = await scraper.scrape_all_pages()
        
        if not doctors:
            print("❌ No doctors found. This could be due to:")
            print("   • Invalid search parameters")
            print("   • Website structure changes")
            print("   • Network issues")
            print("   • Ollama model issues")
            return
        
        # Print summary
        scraper.print_summary()
        
        # Save results
        scraper.save_to_json(JSON_FILE)
        scraper.save_to_csv(CSV_FILE)
        
        # Save schema for reuse
        if not LOAD_SCHEMA:  # Only save if we generated a new one
            scraper.save_schema(SCHEMA_FILE)
        
        print(f"\n✅ Ollama-powered scraping completed successfully!")
        print(f"📊 Found {len(doctors)} doctors across {MAX_PAGES} pages")
        print(f"📁 Results saved to:")
        print(f"   • {JSON_FILE}")
        print(f"   • {CSV_FILE}")
        if not LOAD_SCHEMA:
            print(f"   • {SCHEMA_FILE} (reusable schema)")
        
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())