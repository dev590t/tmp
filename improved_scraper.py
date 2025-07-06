#!/usr/bin/env python3

import asyncio
import json
import csv
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig


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


class ImprovedDoctolibScraper:
    """Improved scraper for Doctolib website"""
    
    def __init__(self, base_url: str, max_pages: int = 3):
        self.base_url = base_url
        self.max_pages = max_pages
        self.doctors: List[Doctor] = []
        
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=True
        )
        
        # JavaScript to handle cookie consent
        self.js_code = """
        (async () => {
            console.log("Handling cookie consent...");
            
            // Wait a bit for page to load
            await new Promise(r => setTimeout(r, 2000));
            
            // Try to find and click accept button
            const acceptSelectors = [
                'button:contains("Accepter")',
                'button[data-testid="accept-all-cookies"]',
                '.cookie-consent button',
                'button:contains("Accept")'
            ];
            
            for (const selector of acceptSelectors) {
                try {
                    const button = document.querySelector(selector);
                    if (button && button.offsetParent !== null) {
                        console.log(`Clicking accept button: ${selector}`);
                        button.click();
                        await new Promise(r => setTimeout(r, 1000));
                        break;
                    }
                } catch (e) {
                    console.log(`Error with selector ${selector}:`, e);
                }
            }
            
            // Wait for content to load
            await new Promise(r => setTimeout(r, 3000));
            console.log("Page interaction completed");
        })();
        """
    
    def _build_page_url(self, page_number: int) -> str:
        """Build URL for a specific page number"""
        if '?' in self.base_url:
            return f"{self.base_url}&page={page_number}"
        else:
            return f"{self.base_url}?page={page_number}"
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _extract_doctors_from_cleaned_html(self, html: str) -> List[Doctor]:
        """Extract doctors from the cleaned HTML based on the actual structure"""
        doctors = []
        
        # Split the HTML by doctor entries
        # Each doctor starts with an h2 containing a button with the name
        doctor_pattern = r'<h2><button>(.*?)</button></h2>(.*?)(?=<h2><button>|$)'
        matches = re.findall(doctor_pattern, html, re.DOTALL | re.IGNORECASE)
        
        for name_match, content_match in matches:
            try:
                name = self._clean_text(name_match)
                if not name:
                    continue
                
                # Extract specialty - usually the first <p> after the name
                specialty_match = re.search(r'<p>(.*?)</p>', content_match)
                specialty = "Unknown"
                if specialty_match:
                    specialty = self._clean_text(specialty_match.group(1))
                
                # Extract address - look for patterns with street names
                address_parts = []
                address_patterns = [
                    r'<p>(\d+.*?(?:Rue|Boulevard|Avenue|Place|Square).*?)</p>',
                    r'<p>(\d{5}\s+[^<]+)</p>'  # Postal code + city
                ]
                
                for pattern in address_patterns:
                    addr_matches = re.findall(pattern, content_match, re.IGNORECASE)
                    address_parts.extend(addr_matches)
                
                address = ", ".join(self._clean_text(part) for part in address_parts) if address_parts else "Unknown"
                
                # Extract distance
                distance_match = re.search(r'<span>([^<]*km[^<]*)</span>', content_match)
                distance = self._clean_text(distance_match.group(1)) if distance_match else None
                
                # Extract sector information
                sector_match = re.search(r'<p>(.*?Conventionné.*?)</p>', content_match, re.IGNORECASE)
                sector_info = self._clean_text(sector_match.group(1)) if sector_match else None
                
                doctor = Doctor(
                    name=name,
                    specialty=specialty,
                    address=address,
                    distance=distance,
                    sector_info=sector_info
                )
                
                doctors.append(doctor)
                
            except Exception as e:
                print(f"Error parsing doctor: {e}")
                continue
        
        return doctors
    
    async def scrape_page(self, page_number: int) -> List[Doctor]:
        """Scrape a single page for doctor information"""
        page_url = self._build_page_url(page_number)
        print(f"Scraping page {page_number}: {page_url}")
        
        config = CrawlerRunConfig(
            js_code=self.js_code,
            wait_for="css:body",
            page_timeout=30000,
            delay_before_return_html=5
        )
        
        doctors = []
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            try:
                result = await crawler.arun(url=page_url, config=config)
                
                if result.success:
                    print(f"Successfully loaded page {page_number}")
                    
                    # Extract doctors from cleaned HTML
                    doctors = self._extract_doctors_from_cleaned_html(result.cleaned_html)
                    print(f"Found {len(doctors)} doctors on page {page_number}")
                    
                    # Save debug info for first page
                    if page_number == 1:
                        with open(f"debug_page_{page_number}.html", "w", encoding="utf-8") as f:
                            f.write(result.cleaned_html)
                        print(f"Saved debug HTML for page {page_number}")
                    
                else:
                    print(f"Failed to load page {page_number}: {result.error_message}")
                    
            except Exception as e:
                print(f"Error scraping page {page_number}: {e}")
        
        return doctors
    
    async def scrape_all_pages(self) -> List[Doctor]:
        """Scrape all pages up to max_pages"""
        print(f"Starting to scrape {self.max_pages} pages from Doctolib")
        
        all_doctors = []
        
        for page_num in range(1, self.max_pages + 1):
            try:
                page_doctors = await self.scrape_page(page_num)
                all_doctors.extend(page_doctors)
                
                # Add delay between pages
                if page_num < self.max_pages:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"Error on page {page_num}: {e}")
                continue
        
        self.doctors = all_doctors
        print(f"Total doctors found: {len(all_doctors)}")
        return all_doctors
    
    def save_to_json(self, filename: str = "doctors.json"):
        """Save scraped doctors to JSON file"""
        data = [doctor.to_dict() for doctor in self.doctors]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} doctors to {filename}")
    
    def save_to_csv(self, filename: str = "doctors.csv"):
        """Save scraped doctors to CSV file"""
        if not self.doctors:
            print("No doctors to save")
            return
        
        fieldnames = ['name', 'specialty', 'address', 'distance', 'sector_info', 'profile_url']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for doctor in self.doctors:
                writer.writerow(doctor.to_dict())
        
        print(f"Saved {len(self.doctors)} doctors to {filename}")
    
    def print_summary(self):
        """Print a summary of scraped doctors"""
        if not self.doctors:
            print("No doctors found")
            return
        
        print(f"\n=== SCRAPING SUMMARY ===")
        print(f"Total doctors found: {len(self.doctors)}")
        print(f"Pages scraped: {self.max_pages}")
        
        # Show first few doctors as examples
        print(f"\nFirst 5 doctors:")
        for i, doctor in enumerate(self.doctors[:5], 1):
            print(f"{i}. {doctor.name}")
            print(f"   Specialty: {doctor.specialty}")
            print(f"   Address: {doctor.address}")
            if doctor.distance:
                print(f"   Distance: {doctor.distance}")
            if doctor.sector_info:
                print(f"   Sector: {doctor.sector_info}")
            print()


async def main():
    """Main function to demonstrate the improved scraper"""
    # Configuration parameters
    BASE_URL = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
    MAX_PAGES = 3
    
    print(f"Initializing improved Doctolib scraper...")
    print(f"Base URL: {BASE_URL}")
    print(f"Max pages: {MAX_PAGES}")
    
    # Create and run scraper
    scraper = ImprovedDoctolibScraper(BASE_URL, MAX_PAGES)
    
    try:
        doctors = await scraper.scrape_all_pages()
        
        # Print summary
        scraper.print_summary()
        
        # Save results
        scraper.save_to_json("improved_doctolib_doctors.json")
        scraper.save_to_csv("improved_doctolib_doctors.csv")
        
    except Exception as e:
        print(f"Error during scraping: {e}")


if __name__ == "__main__":
    asyncio.run(main())