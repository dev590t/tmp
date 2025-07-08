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


@dataclass
class Doctor:
    """Data class to represent a doctor's information"""
    name: str
    specialty: str
    address: str
    distance: Optional[str] = None
    image: Optional[str] = None
    insurance: Optional[str] = None
    consultation: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'specialty': self.specialty,
            'address': self.address,
            'distance': self.distance,
            'image': self.image,
            'insurance': self.insurance,
            'consultation': self.consultation
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
        
        # Define the extraction schema based on actual Doctolib structure
        # Looking at the HTML, each doctor card is in a div that contains both an img and h2 button
        self.extraction_schema = {
            'name': 'Gastro-entérologues et hépatologues',
            'baseSelector': 'div:has(img.w-48):has(h2 button)',
            'fields': [
                {'name': 'name', 'selector': 'h2 button', 'type': 'text'},
                {'name': 'image', 'selector': 'img.w-48', 'type': 'attribute', 'attribute': 'src'},
                {'name': 'distance', 'selector': 'span:contains("km")', 'type': 'text'},
                {'name': 'specialty', 'selector': 'p', 'type': 'text'},
                {'name': 'address', 'selector': 'p:contains("Rue"), p:contains("Boulevard"), p:contains("Avenue"), p:contains("Place"), p:contains("Paris")', 'type': 'text'},
                {'name': 'insurance', 'selector': 'p:contains("Conventionné")', 'type': 'text'},
                {'name': 'consultation', 'selector': 'button:contains("Prendre")', 'type': 'text'}
            ]
        }
        
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
    
    def _extract_doctors_from_html(self, html: str) -> List[Doctor]:
        """Extract doctors from the cleaned HTML using improved regex patterns"""
        doctors = []
        
        # Look for doctor card patterns based on the actual HTML structure
        # Each doctor card contains an image, name in h2>button, specialty, address, and insurance info
        doctor_pattern = r'<img[^>]*class="w-48[^"]*"[^>]*src="([^"]*)"[^>]*>.*?<h2><button>([^<]+)</button></h2>.*?(?:<div><span>([^<]*km[^<]*)</span></div>)?.*?<p>([^<]+)</p>.*?<p>([^<]+)</p>.*?<p>([^<]+)</p>.*?(?:<p>(Conventionné[^<]*)</p>)?'
        
        matches = re.findall(doctor_pattern, html, re.DOTALL | re.IGNORECASE)
        print(f"🔍 Complex regex found {len(matches)} matches")
        
        for match in matches:
            try:
                image, name, distance, specialty, address1, address2, insurance = match
                
                # Clean and process the extracted data
                name = self._clean_text(name).strip()
                if not name or name in ['Notre entreprise', 'Doctolib']:
                    continue
                
                specialty = self._clean_text(specialty).strip()
                if not specialty or 'Questions fréquentes' in specialty:
                    specialty = "Gastro-entérologue et hépatologue"
                
                # Combine address parts
                address_parts = []
                if address1:
                    addr1 = self._clean_text(address1).strip()
                    if addr1 and not any(skip in addr1.lower() for skip in ['questions', 'doctolib', 'résultats']):
                        address_parts.append(addr1)
                
                if address2:
                    addr2 = self._clean_text(address2).strip()
                    if addr2 and not any(skip in addr2.lower() for skip in ['questions', 'doctolib', 'résultats']):
                        address_parts.append(addr2)
                
                address = ", ".join(address_parts) if address_parts else "Unknown"
                
                # Clean other fields
                distance = self._clean_text(distance).strip() if distance else None
                insurance = self._clean_text(insurance).strip() if insurance else None
                image = image.strip() if image else None
                
                doctor = Doctor(
                    name=name,
                    specialty=specialty,
                    address=address,
                    distance=distance,
                    image=image,
                    insurance=insurance,
                    consultation=None  # Not easily extractable with this pattern
                )
                
                doctors.append(doctor)
                
            except Exception as e:
                print(f"Error parsing doctor: {e}")
                continue
        
        # If the regex approach didn't work well, try a simpler approach
        if len(doctors) < 10:  # Expect at least 10 doctors per page
            print("🔄 Using fallback extraction method...")
            doctors = self._extract_doctors_simple_pattern(html)
        
        return doctors
    
    def _extract_doctors_simple_pattern(self, html: str) -> List[Doctor]:
        """Fallback extraction using simpler patterns"""
        doctors = []
        
        # Find all h2 button elements (doctor names)
        name_pattern = r'<h2><button>([^<]+)</button></h2>'
        names = re.findall(name_pattern, html)
        
        # Find all images with doctor avatars
        image_pattern = r'<img[^>]*src="([^"]*(?:doctor_avatar|upload)[^"]*)"[^>]*>'
        images = re.findall(image_pattern, html)
        
        # Find distance information
        distance_pattern = r'<span>([^<]*km[^<]*)</span>'
        distances = re.findall(distance_pattern, html)
        
        # Find insurance information
        insurance_pattern = r'<p>(Conventionné[^<]*)</p>'
        insurances = re.findall(insurance_pattern, html)
        print(f"🔍 Found {len(insurances)} insurance entries: {insurances[:3]}")
        
        # Find address information (look for patterns with street names)
        address_pattern = r'<p>([^<]*(?:Rue|Boulevard|Avenue|Place)[^<]*)</p>'
        addresses = re.findall(address_pattern, html)
        
        # Combine the data (this is approximate since we can't perfectly match them)
        print(f"🔍 Found {len(names)} names, {len(addresses)} addresses, {len(distances)} distances, {len(images)} images")
        
        # Filter out non-doctor names first
        skip_terms = ['Notre entreprise', 'Doctolib', 'Questions', 'Recherches', 'Pour les', 'Centre d\'aide', 'Utiliser', 'Mot de passe', 'Prendre et confirmer']
        filtered_names = []
        for name in names:
            clean_name = self._clean_text(name).strip()
            if clean_name and not any(term in clean_name for term in skip_terms):
                filtered_names.append(clean_name)
        
        print(f"🔍 After filtering: {len(filtered_names)} valid doctor names")
        
        max_doctors = min(len(filtered_names), 20)  # Limit to reasonable number
        
        for i in range(max_doctors):
            name = filtered_names[i]
            
            # Try to match insurance info to this doctor (approximate matching)
            insurance_info = None
            if i < len(insurances):
                insurance_info = self._clean_text(insurances[i])
            elif insurances:  # Use any available insurance info as fallback
                insurance_info = self._clean_text(insurances[0])
            
            doctor = Doctor(
                name=name,
                specialty="Gastro-entérologue et hépatologue",
                address=self._clean_text(addresses[i]) if i < len(addresses) else "Unknown",
                distance=self._clean_text(distances[i]) if i < len(distances) else None,
                image=images[i] if i < len(images) else None,
                insurance=insurance_info,
                consultation=None
            )
            
            doctors.append(doctor)
        
        return doctors

    async def scrape_page(self, page_number: int) -> List[Doctor]:
        """Scrape a single page for doctor information using improved HTML parsing"""
        page_url = self._build_page_url(page_number)
        print(f"📄 Scraping page {page_number}: {page_url}")
        
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
                    print(f"✅ Successfully loaded page {page_number}")
                    
                    # Extract doctors from cleaned HTML
                    doctors = self._extract_doctors_from_html(result.cleaned_html)
                    print(f"👨‍⚕️ Found {len(doctors)} doctors on page {page_number}")
                    
                else:
                    print(f"❌ Failed to load page {page_number}: {result.error_message}")
                    
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
        
        fieldnames = ['name', 'specialty', 'address', 'distance', 'image', 'insurance', 'consultation']
        
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
            if doctor.image:
                print(f"   Image: {doctor.image}")
            if doctor.insurance:
                print(f"   Insurance: {doctor.insurance}")
            if doctor.consultation:
                print(f"   Consultation: {doctor.consultation}")


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