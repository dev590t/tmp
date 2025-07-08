#!/usr/bin/env python3

import asyncio
from final_doctolib_scraper import DoctolibScraper

async def test_rating_function():
    """Test just the Google rating search function"""
    print("🧪 Testing Google rating search function")
    print("=" * 50)
    
    # Create scraper instance
    url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
    scraper = DoctolibScraper(url, max_pages=1)
    
    # Test with a few doctor names
    test_doctors = [
        "Dr Ariane Chryssostalis",
        "Dr Christian REVOL", 
        "Dr Natanel BENABOU"
    ]
    
    print(f"Testing rating search for {len(test_doctors)} doctors:")
    print()
    
    for i, doctor_name in enumerate(test_doctors, 1):
        print(f"🔍 Test {i}/{len(test_doctors)}: {doctor_name}")
        rating = await scraper.search_google_rating(doctor_name)
        
        if rating:
            print(f"✅ Found rating: {rating}")
        else:
            print(f"❌ No rating found")
        
        print("-" * 40)
        
        # Add delay between searches
        if i < len(test_doctors):
            print("⏳ Waiting 3 seconds...")
            await asyncio.sleep(3)
    
    print("✅ Rating function test completed!")

if __name__ == "__main__":
    asyncio.run(test_rating_function())