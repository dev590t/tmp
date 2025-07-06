#!/usr/bin/env python3

import asyncio
import argparse
import sys
from urllib.parse import urlparse, parse_qs
from doctolib_scraper import DoctolibScraper


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Scrape doctors from Doctolib with configurable parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default 3 pages
  python configurable_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue"
  
  # Scrape 5 pages
  python configurable_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue" --pages 5
  
  # Custom output files
  python configurable_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue" --json gastro_doctors.json --csv gastro_doctors.csv
        """
    )
    
    parser.add_argument(
        '--url', 
        required=True,
        help='Base URL for Doctolib search (without page parameter)'
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
    
    parser.add_argument(
        '--no-json',
        action='store_true',
        help='Skip JSON output'
    )
    
    parser.add_argument(
        '--no-csv',
        action='store_true',
        help='Skip CSV output'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def validate_url(url: str) -> str:
    """Validate and clean the URL"""
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        if 'doctolib.fr' not in parsed.netloc:
            print("Warning: URL does not appear to be from Doctolib")
        
        # Remove page parameter if present
        if "&page=" in url:
            url = url.split("&page=")[0]
        elif "?page=" in url:
            url = url.split("?page=")[0]
        
        return url
        
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}")


async def main():
    """Main function for configurable scraper"""
    args = parse_arguments()
    
    try:
        # Validate inputs
        base_url = validate_url(args.url)
        
        if args.pages < 1:
            print("Error: Number of pages must be at least 1")
            sys.exit(1)
        
        if args.pages > 20:
            print("Warning: Scraping more than 20 pages may take a very long time")
            response = input("Continue? (y/N): ")
            if response.lower() != 'y':
                sys.exit(0)
        
        # Display configuration
        print("=== SCRAPER CONFIGURATION ===")
        print(f"URL: {base_url}")
        print(f"Pages to scrape: {args.pages}")
        if not args.no_json:
            print(f"JSON output: {args.json}")
        if not args.no_csv:
            print(f"CSV output: {args.csv}")
        print("=" * 30)
        print()
        
        # Create and run scraper
        scraper = DoctolibScraper(base_url, args.pages)
        
        # Scrape all pages
        doctors = await scraper.scrape_all_pages()
        
        if not doctors:
            print("No doctors found. This could be due to:")
            print("- Invalid search parameters")
            print("- Website structure changes")
            print("- Network issues")
            print("- Anti-bot protection")
            sys.exit(1)
        
        # Print summary
        scraper.print_summary()
        
        # Save results
        if not args.no_json:
            scraper.save_to_json(args.json)
        
        if not args.no_csv:
            scraper.save_to_csv(args.csv)
        
        print(f"\n✅ Scraping completed successfully!")
        print(f"Found {len(doctors)} doctors across {args.pages} pages")
        
    except KeyboardInterrupt:
        print("\n❌ Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())