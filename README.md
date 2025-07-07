# Doctolib Scraper

A professional web scraper for extracting doctor information from Doctolib using crawl4ai. This scraper is designed to be configurable, respectful to the website, and easy to use.

## 🆕 NEW: Ollama-Powered Schema Generation

The latest version includes **automatic schema generation using Ollama LLM**! This provides:
- **🧠 One-time schema generation** that creates reusable extraction schemas
- **⚡ LLM-free extractions** after initial schema creation
- **🎯 Improved accuracy** through AI-powered page structure analysis
- **💰 No API costs** when using local Ollama models

## Features

### Core Features
- ✅ **Configurable Parameters**: URL and number of pages can be easily configured
- ✅ **Multiple Output Formats**: Saves data in both JSON and CSV formats
- ✅ **Respectful Scraping**: Includes delays between requests and handles cookie consent
- ✅ **Error Handling**: Robust error handling and logging
- ✅ **Clean Data Extraction**: Properly extracts and cleans doctor information
- ✅ **Command Line Interface**: Easy to use from command line with arguments

### AI-Powered Features
- 🧠 **Ollama Integration**: Uses local LLM for intelligent schema generation
- 📋 **Schema Reuse**: Save and reuse generated schemas for fast extractions
- 🔄 **Fallback Support**: Manual schema fallback if LLM generation fails
- 🎯 **Smart Analysis**: AI analyzes page structure to create optimal selectors

## Installation

### Basic Installation

1. Install the required dependencies:
```bash
pip install crawl4ai
```

2. Install playwright browsers:
```bash
playwright install
playwright install-deps
```

### Ollama Installation (for AI-powered schema generation)

3. Install Ollama (for AI-powered features):
```bash
# On macOS
brew install ollama

# On Linux
curl -fsSL https://ollama.ai/install.sh | sh

# On Windows
# Download from https://ollama.ai/download
```

4. Pull a model (recommended: llama3.2):
```bash
ollama pull llama3.2
# or
ollama pull llama3.1
ollama pull codellama
```

5. Start Ollama service:
```bash
ollama serve
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

### 🧠 Ollama-Powered Usage (Recommended)

The new Ollama-powered scraper provides better accuracy through AI-generated schemas:

```bash
# Basic usage with Ollama (generates schema automatically)
python ollama_doctolib_scraper.py --url "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue"

# Use different Ollama model
python ollama_doctolib_scraper.py --url "URL" --model llama3.1 --pages 5

# Load existing schema (skip generation for faster execution)
python ollama_doctolib_scraper.py --url "URL" --load-schema doctolib_schema.json

# Generate and save schema for reuse
python ollama_doctolib_scraper.py --url "URL" --save-schema my_schema.json
```

### Schema Generation Example

To understand how schema generation works:

```bash
# Run the schema generation example
python schema_generator_example.py
```

This will:
1. Load a sample Doctolib page
2. Use Ollama to analyze the page structure
3. Generate a CSS extraction schema
4. Test the schema and save results
5. Save the schema for reuse

## Command Line Arguments

### Standard Scraper (`final_doctolib_scraper.py`)
- `--url`: Base URL for Doctolib search (required)
- `--pages`: Number of pages to scrape (default: 3)
- `--json`: Output JSON filename (default: doctolib_doctors.json)
- `--csv`: Output CSV filename (default: doctolib_doctors.csv)

### Ollama-Powered Scraper (`ollama_doctolib_scraper.py`)
- `--url`: Base URL for Doctolib search (required)
- `--pages`: Number of pages to scrape (default: 3)
- `--model`: Ollama model to use (default: llama3.2)
- `--json`: Output JSON filename (default: ollama_doctors.json)
- `--csv`: Output CSV filename (default: ollama_doctors.csv)
- `--save-schema`: Save generated schema to file (default: doctolib_schema.json)
- `--load-schema`: Load existing schema from file (skips generation)

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

## Available Scrapers

This repository includes multiple scraper implementations:

### 1. 🧠 `ollama_doctolib_scraper.py` (Recommended)
- **AI-powered schema generation** using Ollama
- **Best accuracy** through intelligent page analysis
- **Reusable schemas** for fast subsequent extractions
- **No API costs** (uses local Ollama models)

### 2. 🔧 `final_doctolib_scraper.py` (Standard)
- **Manual CSS selectors** with robust fallbacks
- **No dependencies** on external AI services
- **Proven reliability** with extensive testing
- **Fast execution** (no schema generation overhead)

### 3. ⚙️ `config_based_scraper.py` (Configuration-driven)
- **JSON configuration** for easy parameter management
- **Batch processing** support
- **Template-based** approach

### 4. 🔍 `debug_scraper.py` (Development)
- **Debug mode** with HTML output
- **Troubleshooting** website structure changes
- **Development** and testing tool

### 5. 📚 `schema_generator_example.py` (Educational)
- **Learn** how schema generation works
- **Understand** Ollama integration
- **Test** schema creation process

## Limitations and Considerations

- **Respectful Usage**: The scraper includes delays and respects robots.txt
- **Website Changes**: May need updates if Doctolib changes their HTML structure
- **Rate Limiting**: Don't scrape too aggressively to avoid being blocked
- **Legal Compliance**: Ensure your usage complies with Doctolib's terms of service
- **Ollama Requirement**: AI-powered features require Ollama installation and models

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

4. **Ollama-specific issues**:
   - **Ollama not running**: Make sure `ollama serve` is running
   - **Model not found**: Pull the model with `ollama pull llama3.2`
   - **Schema generation fails**: Try a different model or use `--load-schema` with a manual schema
   - **Connection errors**: Check if Ollama is accessible on localhost:11434

### Debug Mode

For debugging, you can use the debug scraper:
```bash
python debug_scraper.py
```

This will save the raw HTML content for inspection.

For Ollama debugging, use the schema generator example:
```bash
python schema_generator_example.py
```

This will show the schema generation process step by step.

## Files in this Package

### Core Scrapers
- `ollama_doctolib_scraper.py`: 🧠 AI-powered scraper with Ollama schema generation (Recommended)
- `final_doctolib_scraper.py`: 🔧 Standard scraper with manual CSS selectors
- `config_based_scraper.py`: ⚙️ Configuration file-based scraper

### Utilities and Examples
- `schema_generator_example.py`: 📚 Educational example showing schema generation
- `debug_scraper.py`: 🔍 Debug version for troubleshooting
- `example_usage.py`: 📖 Programmatic usage examples

### Configuration and Documentation
- `config.json`: Example configuration file
- `README.md`: This comprehensive documentation
- `pyproject.toml`: Project dependencies

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