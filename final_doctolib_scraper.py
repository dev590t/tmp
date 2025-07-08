#!/usr/bin/env python3

import asyncio
import json
import csv
import re
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from utils import extract_doctor


@dataclass
class Doctor:
    """Data class to represent a doctor's information"""
    name: str
    distance: Optional[str] = None
    insurance: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'distance': self.distance,
            'insurance': self.insurance
        }


class DoctolibScraper:
    """Professional Doctolib scraper with configurable parameters"""
    
    def __init__(self, base_url: str, max_pages: int = 3):
        """
        Initialize the scraper
        
        Args:
            base_url: The base URL for the search (without page parameter)
            max_pages: Maximum number of pages to scrape
        """
        self.base_url = self._clean_base_url(base_url)
        self.max_pages = max_pages
        self.doctors: List[Doctor] = []
        
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=True
        )
        
        # Extraction schema is now handled in utils.extract_doctor function
        
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
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text by removing HTML tags and extra whitespace"""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def _parse_extracted_data(self, extracted_content: str) -> List[Doctor]:
        """Parse the JSON extracted content into Doctor objects"""
        doctors = []
        
        try:
            # Parse the extracted JSON
            extracted_data = json.loads(extracted_content)
            
            # Handle both list and single object responses
            if isinstance(extracted_data, list):
                data_list = extracted_data
            elif isinstance(extracted_data, dict):
                data_list = [extracted_data]
            else:
                print(f"⚠️ Unexpected data format: {type(extracted_data)}")
                return doctors
            
            for item in data_list:
                if isinstance(item, dict):
                    # Extract and clean the data
                    name = self._clean_text(item.get('name', '')).strip()
                    distance = self._clean_text(item.get('distance', '')).strip() or None
                    insurance = self._clean_text(item.get('insurance', '')).strip() or None
                    
                    # Only create doctor if we have a valid name
                    if name and name != 'Unknown':
                        # Skip non-doctor names
                        skip_terms = ['Notre entreprise', 'Doctolib', 'Questions', 'Recherches', 'Pour les', 'Centre d\'aide', 'Utiliser', 'Mot de passe', 'Prendre et confirmer']
                        if not any(term in name for term in skip_terms):
                            doctor = Doctor(
                                name=name,
                                distance=distance,
                                insurance=insurance
                            )
                            doctors.append(doctor)
            
            # Remove duplicates based on name (keep first occurrence)
            seen_names = set()
            unique_doctors = []
            for doctor in doctors:
                if doctor.name not in seen_names:
                    seen_names.add(doctor.name)
                    unique_doctors.append(doctor)
            
            doctors = unique_doctors
                        
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing extracted JSON: {e}")
            print(f"Raw content: {extracted_content[:200]}...")
        except Exception as e:
            print(f"❌ Error processing extracted data: {e}")
        
        return doctors
    
    async def scrape_page(self, page_number: int) -> List[Doctor]:
        """Scrape a single page for doctor information using utils.extract_doctor"""
        page_url = self._build_page_url(page_number)
        print(f"📄 Scraping page {page_number}: {page_url}")
        
        doctors = []
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            try:
                # Use the utils.extract_doctor function
                extracted_data = await extract_doctor(crawler, page_url, self.js_code)
                
                if extracted_data:
                    print(f"✅ Successfully loaded page {page_number}")
                    
                    # Parse the extracted data
                    doctors = self._parse_extracted_data(json.dumps(extracted_data))
                    print(f"👨‍⚕️ Found {len(doctors)} doctors on page {page_number}")
                    
                    # Debug: Print raw extracted content for first page
                    if page_number == 1:
                        print(f"🔍 Raw extracted content preview: {json.dumps(extracted_data)[:300]}...")
                    
                else:
                    print(f"❌ Failed to extract data from page {page_number}")
                    
            except Exception as e:
                print(f"❌ Error scraping page {page_number}: {e}")
        
        return doctors
    
    async def scrape_all_pages(self) -> List[Doctor]:
        """Scrape all pages up to max_pages"""
        print(f"🚀 Starting to scrape {self.max_pages} pages from Doctolib")
        print(f"🔗 Base URL: {self.base_url}")
        
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
    
    def save_to_json(self, filename: str = "doctolib_doctors.json"):
        """Save scraped doctors to JSON file"""
        data = [doctor.to_dict() for doctor in self.doctors]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(data)} doctors to {filename}")
    
    def save_to_csv(self, filename: str = "doctolib_doctors.csv"):
        """Save scraped doctors to CSV file"""
        if not self.doctors:
            print("⚠️ No doctors to save")
            return
        
        fieldnames = ['name', 'distance', 'insurance']
        
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
        
        print(f"\n{'='*50}")
        print(f"📊 SCRAPING SUMMARY")
        print(f"{'='*50}")
        print(f"Total doctors found: {len(self.doctors)}")
        print(f"Pages scraped: {self.max_pages}")
        
        # Show first few doctors as examples
        print(f"\n📋 First 3 doctors:")
        for i, doctor in enumerate(self.doctors[:3], 1):
            print(f"\n{i}. {doctor.name}")
            if doctor.distance:
                print(f"   Distance: {doctor.distance}")
            if doctor.insurance:
                print(f"   Insurance: {doctor.insurance}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Scrape doctors from Doctolib with configurable parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default 3 pages
  python final_doctolib_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue"
  
  # Scrape 5 pages
  python final_doctolib_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue" --pages 5
  
  # Custom output files
  python final_doctolib_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue" --json gastro_doctors.json --csv gastro_doctors.csv
        """
    )
    
    parser.add_argument(
        '--url', 
        required=True,
        help='Base URL for Doctolib search (page parameter will be added automatically)'
    )
    
    parser.add_argument(
        '--pages', 
        type=int, 
        default=3,
        help='Number of pages to scrape (default: 3)'
    )
    
    parser.add_argument(
        '--json',
        default='doctolib_doctors.json',
        help='Output JSON filename (default: doctolib_doctors.json)'
    )
    
    parser.add_argument(
        '--csv',
        default='doctolib_doctors.csv', 
        help='Output CSV filename (default: doctolib_doctors.csv)'
    )
    
    return parser.parse_args()


async def main():
    """Main function"""
    # If run directly, use default parameters
    if len(__import__('sys').argv) == 1:
        # Default configuration
        BASE_URL = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
        MAX_PAGES = 3
        JSON_FILE = "doctolib_doctors.json"
        CSV_FILE = "doctolib_doctors.csv"
        
        print("🔧 Using default configuration:")
        print(f"   URL: {BASE_URL}")
        print(f"   Pages: {MAX_PAGES}")
        
    else:
        # Parse command line arguments
        args = parse_arguments()
        BASE_URL = args.url
        MAX_PAGES = args.pages
        JSON_FILE = args.json
        CSV_FILE = args.csv
        
        print("🔧 Using command line configuration:")
        print(f"   URL: {BASE_URL}")
        print(f"   Pages: {MAX_PAGES}")
    
    try:
        # Create and run scraper
        scraper = DoctolibScraper(BASE_URL, MAX_PAGES)
        
        # Scrape all pages
        doctors = await scraper.scrape_all_pages()
        
        if not doctors:
            print("❌ No doctors found. This could be due to:")
            print("   • Invalid search parameters")
            print("   • Website structure changes")
            print("   • Network issues")
            print("   • Anti-bot protection")
            return
        
        # Print summary
        scraper.print_summary()
        
        # Save results
        scraper.save_to_json(JSON_FILE)
        scraper.save_to_csv(CSV_FILE)
        
        print(f"\n✅ Scraping completed successfully!")
        print(f"📊 Found {len(doctors)} doctors across {MAX_PAGES} pages")
        print(f"📁 Results saved to:")
        print(f"   • {JSON_FILE}")
        print(f"   • {CSV_FILE}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())