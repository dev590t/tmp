#!/usr/bin/env python3

"""
Test script to verify LLM configuration functionality
"""

import asyncio
from llm_doctolib_scraper import LLMDoctolibScraper
from crawl4ai import LLMConfig

async def test_default_groq_config():
    """Test default Groq configuration"""
    print("🧪 Testing default Groq configuration...")
    
    # Test URL
    url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
    
    # Create scraper with default config (should use Groq)
    scraper = LLMDoctolibScraper(url, max_pages=1)
    
    print(f"✅ Default LLM Config:")
    print(f"   Provider: {scraper.llm_config.provider}")
    print(f"   Temperature: {scraper.llm_config.temprature}")
    print(f"   Max Tokens: {scraper.llm_config.max_tokens}")
    
    return scraper

async def test_custom_llm_config():
    """Test custom LLM configuration"""
    print("\n🧪 Testing custom LLM configuration...")
    
    # Test URL
    url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
    
    # Create custom LLM config
    custom_config = LLMConfig(
        provider="groq/meta-llama/llama-4-scout-17b-16e-instruct",
        api_token="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",
        temprature=0.2,
        max_tokens=2000
    )
    
    # Create scraper with custom config
    scraper = LLMDoctolibScraper(url, max_pages=1, llm_config=custom_config)
    
    print(f"✅ Custom LLM Config:")
    print(f"   Provider: {scraper.llm_config.provider}")
    print(f"   Temperature: {scraper.llm_config.temprature}")
    print(f"   Max Tokens: {scraper.llm_config.max_tokens}")
    
    return scraper

async def test_ollama_config():
    """Test Ollama configuration"""
    print("\n🧪 Testing Ollama configuration...")
    
    # Test URL
    url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14"
    
    # Create Ollama LLM config
    ollama_config = LLMConfig(
        provider="ollama/llama3.2",
        api_token=None
    )
    
    # Create scraper with Ollama config
    scraper = LLMDoctolibScraper(url, max_pages=1, llm_config=ollama_config)
    
    print(f"✅ Ollama LLM Config:")
    print(f"   Provider: {scraper.llm_config.provider}")
    print(f"   API Token: {scraper.llm_config.api_token}")
    
    return scraper

async def main():
    """Main test function"""
    print("🚀 Testing LLM Configuration Functionality\n")
    
    try:
        # Test default configuration
        await test_default_groq_config()
        
        # Test custom configuration
        await test_custom_llm_config()
        
        # Test Ollama configuration
        await test_ollama_config()
        
        print("\n✅ All LLM configuration tests passed!")
        print("\n📝 Usage Examples:")
        print("   # Use default Groq config:")
        print("   python llm_doctolib_scraper.py --url 'URL'")
        print("\n   # Use custom Groq model:")
        print("   python llm_doctolib_scraper.py --url 'URL' --llm-model 'meta-llama/llama-3.1-70b-versatile'")
        print("\n   # Use OpenAI:")
        print("   python llm_doctolib_scraper.py --url 'URL' --llm-provider openai --llm-model gpt-4 --llm-api-key YOUR_KEY")
        print("\n   # Use Ollama:")
        print("   python llm_doctolib_scraper.py --url 'URL' --llm-provider ollama --llm-model llama3.2")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())