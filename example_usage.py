#!/usr/bin/env python3
"""
Example usage of the Doctolib scraper
This script demonstrates how to use the scraper programmatically
"""

import asyncio
from final_doctolib_scraper import DoctolibScraper


async def example_gastroenterologists():
    """Example: Scrape gastroenterologists in Paris 12th"""
    print("=== Example 1: Gastroenterologists in Paris 12th ===")
    
    url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
    scraper = DoctolibScraper(url, max_pages=2)
    
    doctors = await scraper.scrape_all_pages()
    scraper.print_summary()
    
    # Save with custom filenames
    scraper.save_to_json("gastro_paris12.json")
    scraper.save_to_csv("gastro_paris12.csv")
    
    return doctors


async def example_dentists():
    """Example: Scrape dentists in Lyon"""
    print("\n=== Example 2: Dentists in Lyon ===")
    
    url = "https://www.doctolib.fr/search?location=lyon&speciality=dentiste"
    scraper = DoctolibScraper(url, max_pages=1)
    
    doctors = await scraper.scrape_all_pages()
    scraper.print_summary()
    
    # Save with custom filenames
    scraper.save_to_json("dentists_lyon.json")
    scraper.save_to_csv("dentists_lyon.csv")
    
    return doctors


async def example_custom_search():
    """Example: Custom search with data processing"""
    print("\n=== Example 3: Custom search with data processing ===")
    
    url = "https://www.doctolib.fr/search?location=75001-paris&speciality=cardiologue"
    scraper = DoctolibScraper(url, max_pages=1)
    
    doctors = await scraper.scrape_all_pages()
    
    # Process the data
    if doctors:
        print(f"\nData processing example:")
        print(f"Total doctors: {len(doctors)}")
        
        # Group by specialty
        specialties = {}
        for doctor in doctors:
            spec = doctor.specialty
            if spec not in specialties:
                specialties[spec] = []
            specialties[spec].append(doctor)
        
        print(f"Specialties found: {list(specialties.keys())}")
        
        # Find doctors within 5km
        nearby_doctors = [d for d in doctors if d.distance and "km" in d.distance]
        if nearby_doctors:
            print(f"Doctors with distance info: {len(nearby_doctors)}")
            for doctor in nearby_doctors[:3]:
                print(f"  - {doctor.name}: {doctor.distance}")
        
        # Filter by sector
        sector1_doctors = [d for d in doctors if d.sector_info and "secteur 1" in d.sector_info.lower()]
        print(f"Sector 1 doctors: {len(sector1_doctors)}")
    
    return doctors


async def main():
    """Run all examples"""
    print("Doctolib Scraper - Usage Examples")
    print("=" * 50)
    
    try:
        # Example 1: Gastroenterologists
        gastro_doctors = await example_gastroenterologists()
        
        # Example 2: Dentists (commented out to save time)
        # dentist_doctors = await example_dentists()
        
        # Example 3: Custom processing
        # cardio_doctors = await example_custom_search()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("Check the generated JSON and CSV files for results.")
        
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())