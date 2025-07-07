#!/usr/bin/env python3

import asyncio
import json
import sys
from pathlib import Path
from doctolib_scraper import DoctolibScraper


def load_config(config_file: str = "config.json") -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"❌ Configuration file '{config_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        sys.exit(1)


def validate_config(config: dict) -> dict:
    """Validate and set defaults for configuration"""
    # Required fields
    if 'base_url' not in config:
        raise ValueError("'base_url' is required in configuration")
    
    # Set defaults
    config.setdefault('max_pages', 3)
    config.setdefault('output', {})
    config['output'].setdefault('json_file', 'doctolib_doctors.json')
    config['output'].setdefault('csv_file', 'doctolib_doctors.csv')
    
    config.setdefault('scraping', {})
    config['scraping'].setdefault('delay_between_pages', 2)
    config['scraping'].setdefault('page_timeout', 30000)
    config['scraping'].setdefault('headless', False)
    
    # Validate values
    if config['max_pages'] < 1:
        raise ValueError("'max_pages' must be at least 1")
    
    if config['scraping']['delay_between_pages'] < 0:
        raise ValueError("'delay_between_pages' must be non-negative")
    
    return config


async def main():
    """Main function for config-based scraper"""
    config_file = "config.json"
    
    # Check if custom config file is provided as argument
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    try:
        # Load and validate configuration
        print(f"📋 Loading configuration from '{config_file}'...")
        config = load_config(config_file)
        config = validate_config(config)
        
        # Display configuration
        print("\n=== CONFIGURATION ===")
        print(f"Base URL: {config['base_url']}")
        print(f"Max pages: {config['max_pages']}")
        print(f"JSON output: {config['output']['json_file']}")
        print(f"CSV output: {config['output']['csv_file']}")
        print(f"Headless mode: {config['scraping']['headless']}")
        print(f"Page timeout: {config['scraping']['page_timeout']}ms")
        print(f"Delay between pages: {config['scraping']['delay_between_pages']}s")
        print("=" * 21)
        print()
        
        # Create scraper with custom configuration
        scraper = DoctolibScraper(config['base_url'], config['max_pages'])
        
        # Update scraper configuration if needed
        scraper.browser_config.headless = config['scraping']['headless']
        
        # Scrape all pages
        print("🚀 Starting scraping process...")
        doctors = await scraper.scrape_all_pages()
        
        if not doctors:
            print("❌ No doctors found. Check your configuration and try again.")
            sys.exit(1)
        
        # Print summary
        scraper.print_summary()
        
        # Save results
        print("💾 Saving results...")
        scraper.save_to_json(config['output']['json_file'])
        scraper.save_to_csv(config['output']['csv_file'])
        
        print(f"\n✅ Scraping completed successfully!")
        print(f"Found {len(doctors)} doctors across {config['max_pages']} pages")
        print(f"Results saved to:")
        print(f"  - {config['output']['json_file']}")
        print(f"  - {config['output']['csv_file']}")
        
    except KeyboardInterrupt:
        print("\n❌ Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())