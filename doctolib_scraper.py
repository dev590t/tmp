#!/usr/bin/env python3

import asyncio
import json
import csv
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse, parse_qs
import re
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


@dataclass
class Doctor:
    """Data class to represent a doctor's information"""
    name: str
    specialty: str
    address: str
    phone: Optional[str] = None
    rating: Optional[str] = None
    availability: Optional[str] = None
    profile_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'specialty': self.specialty,
            'address': self.address,
            'phone': self.phone,
            'rating': self.rating,
            'availability': self.availability,
            'profile_url': self.profile_url
        }


class DoctolibScraper:
    """Scraper for Doctolib website to extract doctor information"""
    
    def __init__(self, base_url: str, max_pages: int = 3):
        """
        Initialize the scraper
        
        Args:
            base_url: The base URL for the search (without page parameter)
            max_pages: Maximum number of pages to scrape
        """
        self.base_url = base_url
        self.max_pages = max_pages
        self.doctors: List[Doctor] = []
        
        # Configure browser for headless operation
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=True
        )
        
        # JavaScript to handle cookie consent and page interactions
        self.js_code = """
        (async () => {
            // Handle cookie consent if present
            const acceptButton = document.querySelector('button[data-testid="accept-all-cookies"]');
            if (acceptButton) {
                acceptButton.click();
                await new Promise(r => setTimeout(r, 1000));
            }
            
            // Alternative cookie consent selectors
            const altAcceptButton = document.querySelector('button:contains("Accepter")');
            if (altAcceptButton) {
                altAcceptButton.click();
                await new Promise(r => setTimeout(r, 1000));
            }
            
            // Wait for content to load
            await new Promise(r => setTimeout(r, 2000));
        })();
        """
        
        # CSS extraction strategy for doctor information based on actual HTML structure
        self.extraction_schema = {
            "name": "doctors",
            "baseSelector": "div:has(h2 button)",  # Each doctor card contains an h2 with a button
            "fields": [
                {
                    "name": "name",
                    "selector": "h2 button",
                    "type": "text"
                },
                {
                    "name": "specialty", 
                    "selector": "h2 + div p, div:has(h2) + div p",
                    "type": "text"
                },
                {
                    "name": "address",
                    "selector": "p:contains('Rue'), p:contains('Boulevard'), p:contains('Avenue'), p:contains('Place')",
                    "type": "text"
                },
                {
                    "name": "distance",
                    "selector": "span:contains('km')",
                    "type": "text"
                },
                {
                    "name": "sector_info",
                    "selector": "p:contains('Conventionné'), p:contains('secteur')",
                    "type": "text"
                },
                {
                    "name": "profile_url",
                    "selector": "h2 button",
                    "type": "attribute",
                    "attribute": "onclick"
                }
            ]
        }
    
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
    
    def _extract_doctors_from_html(self, html: str, page_url: str) -> List[Doctor]:
        """Extract doctor information from HTML using regex patterns as fallback"""
        doctors = []
        
        # Based on the actual HTML structure, look for doctor cards
        # Each doctor has an h2 with a button containing the name
        doctor_name_pattern = r'<h2><button[^>]*>(.*?)</button></h2>'
        name_matches = re.findall(doctor_name_pattern, html, re.DOTALL | re.IGNORECASE)
        
        # Find all doctor sections by looking for the pattern around names
        # The structure is: div > div > div > h2 > button (name)
        doctor_section_pattern = r'<div[^>]*><div[^>]*><div[^>]*><div[^>]*><h2><button[^>]*>(.*?)</button></h2>.*?</div></div></div></div>'
        
        section_matches = re.findall(doctor_section_pattern, html, re.DOTALL | re.IGNORECASE)
        
        for section in section_matches:
            doctor = self._parse_doctor_section(section, page_url)
            if doctor and doctor.name:
                doctors.append(doctor)
        
        # If the section pattern doesn't work, try a simpler approach
        if not doctors and name_matches:
            # Extract information around each name
            for name in name_matches:
                clean_name = self._clean_text(re.sub(r'<[^>]+>', '', name))
                if clean_name:
                    # Try to find the context around this name
                    name_context_pattern = f'<h2><button[^>]*>{re.escape(name)}</button></h2>(.*?)(?=<h2><button|$)'
                    context_match = re.search(name_context_pattern, html, re.DOTALL | re.IGNORECASE)
                    
                    if context_match:
                        context = context_match.group(1)
                        doctor = self._parse_doctor_context(clean_name, context, page_url)
                        if doctor:
                            doctors.append(doctor)
        
        return doctors
    
    def _parse_doctor_section(self, section_html: str, page_url: str) -> Optional[Doctor]:
        """Parse a doctor section from the HTML"""
        try:
            # Extract name from the section
            name = self._clean_text(re.sub(r'<[^>]+>', '', section_html))
            if not name:
                return None
            
            # This is a simplified version - in practice, you'd extract more details
            return Doctor(
                name=name,
                specialty="Gastro-entérologue et hépatologue",
                address="Unknown"
            )
        except Exception as e:
            print(f"Error parsing doctor section: {e}")
            return None
    
    def _parse_doctor_context(self, name: str, context_html: str, page_url: str) -> Optional[Doctor]:
        """Parse doctor information from name and surrounding context"""
        try:
            # Extract specialty
            specialty_patterns = [
                r'<p>(.*?gastro.*?)</p>',
                r'<p>(.*?entérologue.*?)</p>',
                r'<p>(.*?Centre de santé.*?)</p>'
            ]
            specialty = "Unknown"
            for pattern in specialty_patterns:
                match = re.search(pattern, context_html, re.IGNORECASE)
                if match:
                    specialty = self._clean_text(re.sub(r'<[^>]+>', '', match.group(1)))
                    break
            
            # Extract address
            address_patterns = [
                r'<p>(\d+.*?(?:Rue|Boulevard|Avenue|Place).*?)</p>',
                r'<p>(.*?(?:Rue|Boulevard|Avenue|Place).*?)</p>'
            ]
            address = "Unknown"
            for pattern in address_patterns:
                match = re.search(pattern, context_html, re.IGNORECASE)
                if match:
                    address = self._clean_text(re.sub(r'<[^>]+>', '', match.group(1)))
                    break
            
            # Extract distance if available
            distance_match = re.search(r'<span>([^<]*km[^<]*)</span>', context_html)
            distance = distance_match.group(1) if distance_match else None
            
            # Extract sector information
            sector_match = re.search(r'<p>(.*?Conventionné.*?)</p>', context_html, re.IGNORECASE)
            sector_info = sector_match.group(1) if sector_match else None
            
            return Doctor(
                name=name,
                specialty=specialty,
                address=address,
                phone=distance,  # Using phone field for distance temporarily
                rating=sector_info  # Using rating field for sector info temporarily
            )
            
        except Exception as e:
            print(f"Error parsing doctor context: {e}")
            return None
    
    def _parse_doctor_card(self, card_html: str, page_url: str) -> Optional[Doctor]:
        """Parse individual doctor card HTML"""
        try:
            # Extract name
            name_patterns = [
                r'<h3[^>]*>(.*?)</h3>',
                r'class="[^"]*name[^"]*"[^>]*>(.*?)<',
                r'data-testid="[^"]*name[^"]*"[^>]*>(.*?)<'
            ]
            name = ""
            for pattern in name_patterns:
                match = re.search(pattern, card_html, re.IGNORECASE)
                if match:
                    name = self._clean_text(re.sub(r'<[^>]+>', '', match.group(1)))
                    break
            
            # Extract specialty
            specialty_patterns = [
                r'class="[^"]*specialty[^"]*"[^>]*>(.*?)<',
                r'class="[^"]*subtitle[^"]*"[^>]*>(.*?)<'
            ]
            specialty = ""
            for pattern in specialty_patterns:
                match = re.search(pattern, card_html, re.IGNORECASE)
                if match:
                    specialty = self._clean_text(re.sub(r'<[^>]+>', '', match.group(1)))
                    break
            
            # Extract address
            address_patterns = [
                r'class="[^"]*address[^"]*"[^>]*>(.*?)<',
                r'class="[^"]*location[^"]*"[^>]*>(.*?)<'
            ]
            address = ""
            for pattern in address_patterns:
                match = re.search(pattern, card_html, re.IGNORECASE)
                if match:
                    address = self._clean_text(re.sub(r'<[^>]+>', '', match.group(1)))
                    break
            
            # Extract profile URL
            profile_url = ""
            url_match = re.search(r'href="([^"]*)"', card_html)
            if url_match:
                profile_url = urljoin(page_url, url_match.group(1))
            
            if name:  # Only create doctor if we have at least a name
                return Doctor(
                    name=name,
                    specialty=specialty or "Unknown",
                    address=address or "Unknown",
                    profile_url=profile_url
                )
        except Exception as e:
            print(f"Error parsing doctor card: {e}")
        
        return None
    
    async def scrape_page(self, page_number: int) -> List[Doctor]:
        """Scrape a single page for doctor information"""
        page_url = self._build_page_url(page_number)
        print(f"Scraping page {page_number}: {page_url}")
        
        config = CrawlerRunConfig(
            js_code=self.js_code,
            wait_for="css:body",
            page_timeout=30000,
            delay_before_return_html=3
        )
        
        doctors = []
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            try:
                result = await crawler.arun(url=page_url, config=config)
                
                if result.success:
                    print(f"Successfully loaded page {page_number}")
                    
                    # Try CSS extraction first
                    extraction_strategy = JsonCssExtractionStrategy(self.extraction_schema)
                    config_with_extraction = CrawlerRunConfig(
                        extraction_strategy=extraction_strategy,
                        js_only=True,
                        session_id=f"doctolib_page_{page_number}"
                    )
                    
                    extracted_result = await crawler.arun(url=page_url, config=config_with_extraction)
                    
                    if extracted_result.success and extracted_result.extracted_content:
                        try:
                            extracted_data = json.loads(extracted_result.extracted_content)
                            if isinstance(extracted_data, list):
                                for item in extracted_data:
                                    if isinstance(item, dict) and item.get('name'):
                                        doctor = Doctor(
                                            name=self._clean_text(item.get('name', '')),
                                            specialty=self._clean_text(item.get('specialty', 'Unknown')),
                                            address=self._clean_text(item.get('address', 'Unknown')),
                                            phone=self._clean_text(item.get('phone', '')),
                                            rating=self._clean_text(item.get('rating', '')),
                                            availability=self._clean_text(item.get('availability', '')),
                                            profile_url=item.get('profile_url', '')
                                        )
                                        if doctor.profile_url and not doctor.profile_url.startswith('http'):
                                            doctor.profile_url = urljoin(page_url, doctor.profile_url)
                                        doctors.append(doctor)
                        except json.JSONDecodeError:
                            print("Failed to parse extracted JSON, falling back to HTML parsing")
                    
                    # Fallback to HTML parsing if CSS extraction failed
                    if not doctors:
                        print("Using HTML parsing fallback")
                        doctors = self._extract_doctors_from_html(result.cleaned_html, page_url)
                    
                    print(f"Found {len(doctors)} doctors on page {page_number}")
                    
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
                
                # Add delay between pages to be respectful
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
        
        fieldnames = ['name', 'specialty', 'address', 'phone', 'rating', 'availability', 'profile_url']
        
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
        print(f"\nFirst 3 doctors:")
        for i, doctor in enumerate(self.doctors[:3], 1):
            print(f"{i}. {doctor.name}")
            print(f"   Specialty: {doctor.specialty}")
            print(f"   Address: {doctor.address}")
            if doctor.profile_url:
                print(f"   URL: {doctor.profile_url}")
            print()


async def main():
    """Main function to demonstrate the scraper"""
    # Configuration parameters
    BASE_URL = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14&page=1"
    MAX_PAGES = 3
    
    # Remove page parameter from base URL if present
    if "&page=" in BASE_URL:
        BASE_URL = BASE_URL.split("&page=")[0]
    elif "?page=" in BASE_URL:
        BASE_URL = BASE_URL.split("?page=")[0]
    
    print(f"Initializing Doctolib scraper...")
    print(f"Base URL: {BASE_URL}")
    print(f"Max pages: {MAX_PAGES}")
    
    # Create and run scraper
    scraper = DoctolibScraper(BASE_URL, MAX_PAGES)
    
    try:
        doctors = await scraper.scrape_all_pages()
        
        # Print summary
        scraper.print_summary()
        
        # Save results
        scraper.save_to_json("doctolib_doctors.json")
        scraper.save_to_csv("doctolib_doctors.csv")
        
    except Exception as e:
        print(f"Error during scraping: {e}")


if __name__ == "__main__":
    asyncio.run(main())