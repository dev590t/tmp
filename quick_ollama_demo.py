#!/usr/bin/env python3
"""
Quick demo of Ollama-powered Doctolib scraping
This script demonstrates the key features of the Ollama integration
"""

import asyncio
from ollama_doctolib_scraper import OllamaDoctolibScraper


async def demo_ollama_scraping():
    """
    Demonstrate Ollama-powered scraping with schema generation
    """
    print("🚀 Ollama-Powered Doctolib Scraper Demo")
    print("=" * 50)
    
    # Configuration
    url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
    pages = 2  # Just 2 pages for demo
    model = "llama3.2"  # You can change this to llama3.1, codellama, etc.
    
    print(f"🔧 Configuration:")
    print(f"   URL: {url}")
    print(f"   Pages: {pages}")
    print(f"   Ollama Model: {model}")
    print()
    
    try:
        # Create scraper
        scraper = OllamaDoctolibScraper(url, max_pages=pages, ollama_model=model)
        
        print("🧠 Step 1: Generating extraction schema using Ollama...")
        print("   This analyzes the page structure and creates optimal CSS selectors")
        
        # Generate schema (this is the one-time cost)
        schema = await scraper.generate_extraction_schema()
        
        if schema:
            print("✅ Schema generated successfully!")
            print(f"📋 Schema contains {len(schema.get('fields', []))} extraction fields")
            
            # Save schema for reuse
            scraper.save_schema("demo_schema.json")
            print("💾 Schema saved to demo_schema.json for reuse")
            print()
            
            print("⚡ Step 2: Using schema for fast, LLM-free extractions...")
            
            # Now scrape using the generated schema (fast, no LLM needed)
            doctors = await scraper.scrape_all_pages()
            
            if doctors:
                print(f"🎉 Successfully extracted {len(doctors)} doctors!")
                
                # Show results
                scraper.print_summary()
                
                # Save results
                scraper.save_to_json("demo_doctors.json")
                scraper.save_to_csv("demo_doctors.csv")
                
                print("\n📁 Files created:")
                print("   • demo_doctors.json - Extracted doctor data")
                print("   • demo_doctors.csv - CSV format for Excel")
                print("   • demo_schema.json - Reusable extraction schema")
                
                print("\n🔄 Next time, you can skip schema generation:")
                print("   python ollama_doctolib_scraper.py --load-schema demo_schema.json")
                
            else:
                print("❌ No doctors found - this could be due to website changes")
        
        else:
            print("❌ Schema generation failed")
            print("💡 Try using a different Ollama model or check if Ollama is running")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   • Make sure Ollama is running: ollama serve")
        print("   • Check if model is available: ollama list")
        print("   • Pull model if needed: ollama pull llama3.2")


async def demo_schema_reuse():
    """
    Demonstrate how to reuse a previously generated schema
    """
    print("\n" + "=" * 50)
    print("🔄 Demo: Reusing Previously Generated Schema")
    print("=" * 50)
    
    url = "https://www.doctolib.fr/search?location=75001-paris&speciality=dentiste"
    
    try:
        scraper = OllamaDoctolibScraper(url, max_pages=1)
        
        # Try to load existing schema
        if scraper.load_schema("demo_schema.json"):
            print("✅ Loaded existing schema - no LLM generation needed!")
            print("⚡ This is much faster than generating a new schema")
            
            # Scrape using existing schema
            doctors = await scraper.scrape_all_pages()
            
            if doctors:
                print(f"🎉 Found {len(doctors)} dentists using reused schema!")
                scraper.save_to_json("demo_dentists.json")
            else:
                print("⚠️ No dentists found - schema might need updating for this specialty")
        
        else:
            print("⚠️ No existing schema found - would generate new one")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🧠 Ollama-Powered Doctolib Scraper Demo")
    print("This demo shows the key benefits of using Ollama for schema generation")
    print()
    
    print("⚠️  Prerequisites:")
    print("   • Ollama must be installed and running (ollama serve)")
    print("   • llama3.2 model should be available (ollama pull llama3.2)")
    print("   • Internet connection for accessing Doctolib")
    print()
    
    choice = input("Continue with demo? (y/n): ").lower().strip()
    
    if choice == 'y':
        asyncio.run(demo_ollama_scraping())
        
        # Ask if user wants to see schema reuse demo
        choice2 = input("\nRun schema reuse demo? (y/n): ").lower().strip()
        if choice2 == 'y':
            asyncio.run(demo_schema_reuse())
    
    print("\n✅ Demo completed!")
    print("🔗 For more information, see the README.md file")