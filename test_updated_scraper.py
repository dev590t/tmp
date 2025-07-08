#!/usr/bin/env python3
"""
Test script for the updated final_doctolib_scraper.py with JsonCssExtractionStrategy
"""

import asyncio
import json
from final_doctolib_scraper import DoctolibScraper

async def test_scraper():
    """Test the updated scraper with a small sample"""
    print("🧪 Testing updated Doctolib scraper with JsonCssExtractionStrategy")
    print("=" * 60)
    
    # Test URL - gastroenterologists in Paris 12th
    test_url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
    
    # Create scraper with only 1 page for testing
    scraper = DoctolibScraper(test_url, max_pages=1)
    
    print(f"🔗 Test URL: {test_url}")
    print(f"📋 Schema: {json.dumps(scraper.extraction_schema, indent=2)}")
    
    try:
        # Test scraping
        doctors = await scraper.scrape_all_pages()
        
        if doctors:
            print(f"\n✅ Test successful! Found {len(doctors)} doctors")
            
            # Print detailed results
            scraper.print_summary()
            
            # Save test results
            scraper.save_to_json("test_doctors.json")
            scraper.save_to_csv("test_doctors.csv")
            
            # Analyze data quality
            print(f"\n📊 DATA QUALITY ANALYSIS")
            print("=" * 40)
            
            total_doctors = len(doctors)
            doctors_with_name = sum(1 for d in doctors if d.name and d.name != "Unknown")
            doctors_with_specialty = sum(1 for d in doctors if d.specialty and d.specialty != "Unknown")
            doctors_with_address = sum(1 for d in doctors if d.address and d.address != "Unknown")
            doctors_with_distance = sum(1 for d in doctors if d.distance)
            doctors_with_image = sum(1 for d in doctors if d.image)
            doctors_with_insurance = sum(1 for d in doctors if d.insurance)
            doctors_with_consultation = sum(1 for d in doctors if d.consultation)
            
            print(f"Total doctors: {total_doctors}")
            print(f"With name: {doctors_with_name}/{total_doctors} ({doctors_with_name/total_doctors*100:.1f}%)")
            print(f"With specialty: {doctors_with_specialty}/{total_doctors} ({doctors_with_specialty/total_doctors*100:.1f}%)")
            print(f"With address: {doctors_with_address}/{total_doctors} ({doctors_with_address/total_doctors*100:.1f}%)")
            print(f"With distance: {doctors_with_distance}/{total_doctors} ({doctors_with_distance/total_doctors*100:.1f}%)")
            print(f"With image: {doctors_with_image}/{total_doctors} ({doctors_with_image/total_doctors*100:.1f}%)")
            print(f"With insurance: {doctors_with_insurance}/{total_doctors} ({doctors_with_insurance/total_doctors*100:.1f}%)")
            print(f"With consultation: {doctors_with_consultation}/{total_doctors} ({doctors_with_consultation/total_doctors*100:.1f}%)")
            
            # Show sample data
            print(f"\n📋 SAMPLE DATA (first 2 doctors):")
            print("=" * 40)
            for i, doctor in enumerate(doctors[:2], 1):
                print(f"\nDoctor {i}:")
                print(f"  Name: {doctor.name}")
                print(f"  Specialty: {doctor.specialty}")
                print(f"  Address: {doctor.address}")
                print(f"  Distance: {doctor.distance}")
                print(f"  Image: {doctor.image}")
                print(f"  Insurance: {doctor.insurance}")
                print(f"  Consultation: {doctor.consultation}")
            
        else:
            print("❌ Test failed - no doctors found")
            print("This could be due to:")
            print("- Incorrect CSS selectors in the schema")
            print("- Website structure changes")
            print("- Anti-bot protection")
            print("- Network issues")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraper())