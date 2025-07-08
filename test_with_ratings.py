#!/usr/bin/env python3

import asyncio
from final_doctolib_scraper import DoctolibScraper

async def test_scraper_with_ratings():
    """Test the updated scraper with Google ratings functionality"""
    print("🧪 Testing Doctolib scraper with Google ratings")
    print("=" * 60)
    
    # Test URL for gastroenterologists in Paris 12th
    url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
    
    # Create scraper instance (limit to 1 page for testing)
    scraper = DoctolibScraper(url, max_pages=1)
    
    print("🔗 Test URL:", url)
    print("📋 Testing with Google ratings integration")
    print()
    
    # Step 1: Scrape doctors from Doctolib
    print("📄 Step 1: Scraping doctors from Doctolib...")
    doctors = await scraper.scrape_all_pages()
    
    if not doctors:
        print("❌ No doctors found. Test failed.")
        return
    
    print(f"✅ Found {len(doctors)} doctors")
    print()
    
    # Step 2: Add Google ratings (using mock for demo)
    print("📄 Step 2: Adding Google ratings (demo mode with mock data)...")
    await scraper.add_google_ratings(use_mock=True)
    print()
    
    # Step 3: Show results
    print("📄 Step 3: Results with ratings:")
    scraper.print_summary()
    
    # Step 4: Save results
    print("\n📄 Step 4: Saving results...")
    scraper.save_to_json("doctors_with_ratings.json")
    scraper.save_to_csv("doctors_with_ratings.csv")
    
    # Step 5: Data quality analysis
    print("\n📊 Data Quality Analysis:")
    print("=" * 30)
    
    total_doctors = len(doctors)
    doctors_with_names = len([d for d in doctors if d.name])
    doctors_with_distance = len([d for d in doctors if d.distance])
    doctors_with_insurance = len([d for d in doctors if d.insurance])
    doctors_with_ratings = len([d for d in doctors if d.rating])
    
    print(f"Total doctors: {total_doctors}")
    print(f"Names: {doctors_with_names}/{total_doctors} ({doctors_with_names/total_doctors*100:.1f}%)")
    print(f"Distance: {doctors_with_distance}/{total_doctors} ({doctors_with_distance/total_doctors*100:.1f}%)")
    print(f"Insurance: {doctors_with_insurance}/{total_doctors} ({doctors_with_insurance/total_doctors*100:.1f}%)")
    print(f"Ratings: {doctors_with_ratings}/{total_doctors} ({doctors_with_ratings/total_doctors*100:.1f}%)")
    
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_scraper_with_ratings())