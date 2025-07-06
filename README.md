# Doctolib Scraper

A professional web scraper for extracting doctor information from Doctolib using crawl4ai. This scraper is designed to be configurable, respectful to the website, and easy to use.

## Features

- ✅ **Configurable Parameters**: URL and number of pages can be easily configured
- ✅ **Multiple Output Formats**: Saves data in both JSON and CSV formats
- ✅ **Respectful Scraping**: Includes delays between requests and handles cookie consent
- ✅ **Error Handling**: Robust error handling and logging
- ✅ **Clean Data Extraction**: Properly extracts and cleans doctor information
- ✅ **Command Line Interface**: Easy to use from command line with arguments

## Installation

1. Install the required dependencies:
```bash
pip install crawl4ai
```

2. Install playwright browsers:
```bash
playwright install
playwright install-deps
```

## Usage

### Basic Usage (Default Configuration)

Run with default settings (3 pages of gastroenterologists in Paris 12th):

```bash
python final_doctolib_scraper.py
```

### Command Line Usage

```bash
# Basic usage with custom URL
python final_doctolib_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue"

# Scrape 5 pages
python final_doctolib_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue" --pages 5

# Custom output files
python final_doctolib_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue" --json my_doctors.json --csv my_doctors.csv

# Scrape dentists in Paris 1st
python final_doctolib_scraper.py --url "https://www.doctolib.fr/search?location=75001-paris&speciality=dentiste" --pages 2
```

### Configuration File Usage

You can also use the configuration file approach:

1. Edit `config.json` with your parameters:
```json
{
  "base_url": "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14",
  "max_pages": 3,
  "output": {
    "json_file": "doctolib_doctors.json",
    "csv_file": "doctolib_doctors.csv"
  }
}
```

2. Run the config-based scraper:
```bash
python config_based_scraper.py
```

## Command Line Arguments

- `--url`: Base URL for Doctolib search (required)
- `--pages`: Number of pages to scrape (default: 3)
- `--json`: Output JSON filename (default: doctolib_doctors.json)
- `--csv`: Output CSV filename (default: doctolib_doctors.csv)

## Output Format

The scraper extracts the following information for each doctor:

- **name**: Doctor's name
- **specialty**: Medical specialty
- **address**: Full address
- **distance**: Distance from search location
- **sector_info**: Insurance sector information (e.g., "Conventionné secteur 1")
- **profile_url**: Link to doctor's profile (when available)

### JSON Output Example
```json
[
  {
    "name": "Dr Natanel BENABOU",
    "specialty": "Gastro-entérologue et hépatologue",
    "address": "5 Rue Hippolyte Pinson, 94340 Joinville-le-Pont",
    "distance": "3,2 km",
    "sector_info": "Conventionné secteur 2",
    "profile_url": null
  }
]
```

### CSV Output
The CSV file contains the same data in tabular format, suitable for Excel or data analysis tools.

## How to Build Doctolib URLs

To create search URLs for different specialties and locations:

1. Go to [Doctolib.fr](https://www.doctolib.fr)
2. Search for your desired specialty and location
3. Copy the URL from the results page
4. Remove the `&page=X` parameter if present

Example URLs:
- Gastroenterologists in Paris 12th: `https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue`
- Dentists in Lyon: `https://www.doctolib.fr/search?location=lyon&speciality=dentiste`
- Cardiologists in Marseille: `https://www.doctolib.fr/search?location=marseille&speciality=cardiologue`

## Technical Details

- **Framework**: Built with crawl4ai and Playwright
- **Browser**: Runs in headless mode for efficiency
- **Cookie Handling**: Automatically handles cookie consent dialogs
- **Rate Limiting**: 2-second delay between page requests
- **Error Recovery**: Continues scraping even if individual pages fail

## Limitations and Considerations

- **Respectful Usage**: The scraper includes delays and respects robots.txt
- **Website Changes**: May need updates if Doctolib changes their HTML structure
- **Rate Limiting**: Don't scrape too aggressively to avoid being blocked
- **Legal Compliance**: Ensure your usage complies with Doctolib's terms of service

## Troubleshooting

### Common Issues

1. **No doctors found**: 
   - Check if the URL is correct
   - Verify the search has results on the website
   - Website structure may have changed

2. **Browser errors**:
   - Make sure playwright browsers are installed: `playwright install`
   - Install system dependencies: `playwright install-deps`

3. **Permission errors**:
   - Ensure you have write permissions in the output directory

### Debug Mode

For debugging, you can use the debug scraper:
```bash
python debug_scraper.py
```

This will save the raw HTML content for inspection.

## Files in this Package

- `final_doctolib_scraper.py`: Main scraper with command line interface
- `config_based_scraper.py`: Configuration file-based scraper
- `config.json`: Example configuration file
- `debug_scraper.py`: Debug version for troubleshooting
- `README.md`: This documentation file

## Example Output

When run successfully, you'll see output like:
```
🚀 Starting to scrape 3 pages from Doctolib
📄 Scraping page 1: https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&page=1
✅ Successfully loaded page 1
👨‍⚕️ Found 24 doctors on page 1
...
🎉 Total doctors found: 32
💾 Saved 32 doctors to doctolib_doctors.json
💾 Saved 32 doctors to doctolib_doctors.csv
✅ Scraping completed successfully!
```

## License

This tool is for educational and research purposes. Please respect Doctolib's terms of service and use responsibly.