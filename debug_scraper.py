#!/usr/bin/env python3

import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig


async def debug_doctolib_page():
    """Debug function to examine the actual HTML structure of Doctolib"""
    
    url = "https://www.doctolib.fr/search?location=75012-paris&speciality=gastro-enterologue&availabilitiesBefore=14&page=1"
    
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )
    
    # More comprehensive JavaScript to handle various scenarios
    js_code = """
    (async () => {
        console.log("Starting page interaction...");
        
        // Handle cookie consent - try multiple selectors
        const cookieSelectors = [
            'button[data-testid="accept-all-cookies"]',
            'button:contains("Accepter")',
            'button:contains("Accept")',
            '.cookie-consent button',
            '#cookie-consent button',
            '[data-cy="accept-cookies"]',
            '.gdpr-accept',
            '.cookie-banner button'
        ];
        
        for (const selector of cookieSelectors) {
            try {
                const button = document.querySelector(selector);
                if (button && button.offsetParent !== null) {
                    console.log(`Found cookie button with selector: ${selector}`);
                    button.click();
                    await new Promise(r => setTimeout(r, 1000));
                    break;
                }
            } catch (e) {
                console.log(`Error with selector ${selector}:`, e);
            }
        }
        
        // Wait for content to load
        console.log("Waiting for content to load...");
        await new Promise(r => setTimeout(r, 5000));
        
        // Try to find and log various elements that might contain doctor info
        const possibleSelectors = [
            '.dl-search-result',
            '.search-result',
            '.doctor-card',
            '.practitioner',
            '.listing-item',
            '[data-testid*="doctor"]',
            '[data-testid*="practitioner"]',
            '.result-item',
            '.card',
            'article',
            '.practitioner-result'
        ];
        
        for (const selector of possibleSelectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                console.log(`Found ${elements.length} elements with selector: ${selector}`);
            }
        }
        
        // Log page title and URL for verification
        console.log("Page title:", document.title);
        console.log("Current URL:", window.location.href);
        
        // Check if we're on the right page
        if (document.title.includes("Doctolib")) {
            console.log("✓ We are on Doctolib");
        } else {
            console.log("✗ We might not be on Doctolib");
        }
        
        console.log("Page interaction completed");
    })();
    """
    
    config = CrawlerRunConfig(
        js_code=js_code,
        wait_for="css:body",
        page_timeout=60000,
        delay_before_return_html=5
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        try:
            result = await crawler.arun(url=url, config=config)
            
            if result.success:
                print("✅ Successfully loaded the page")
                print(f"Page title: {result.metadata.get('title', 'Unknown')}")
                print(f"Status code: {result.status_code}")
                
                # Save the HTML for manual inspection
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(result.html)
                print("💾 Saved full HTML to debug_page.html")
                
                with open("debug_cleaned.html", "w", encoding="utf-8") as f:
                    f.write(result.cleaned_html)
                print("💾 Saved cleaned HTML to debug_cleaned.html")
                
                # Try to find doctor-related content with various patterns
                html_content = result.cleaned_html.lower()
                
                print("\n=== CONTENT ANALYSIS ===")
                print(f"HTML length: {len(result.html)} characters")
                print(f"Cleaned HTML length: {len(result.cleaned_html)} characters")
                
                # Look for common doctor-related keywords
                keywords = ['docteur', 'dr.', 'médecin', 'gastro', 'enterologue', 'consultation', 'rendez-vous']
                found_keywords = []
                for keyword in keywords:
                    if keyword in html_content:
                        count = html_content.count(keyword)
                        found_keywords.append(f"{keyword}: {count}")
                
                if found_keywords:
                    print("Found keywords:", ", ".join(found_keywords))
                else:
                    print("❌ No doctor-related keywords found")
                
                # Look for common HTML structures
                patterns = [
                    r'class="[^"]*search[^"]*"',
                    r'class="[^"]*result[^"]*"',
                    r'class="[^"]*doctor[^"]*"',
                    r'class="[^"]*card[^"]*"',
                    r'data-testid="[^"]*"'
                ]
                
                print("\n=== HTML PATTERNS ===")
                for pattern in patterns:
                    matches = re.findall(pattern, result.html, re.IGNORECASE)
                    if matches:
                        unique_matches = list(set(matches))[:5]  # Show first 5 unique matches
                        print(f"Pattern '{pattern}': {len(matches)} matches")
                        print(f"  Examples: {unique_matches}")
                
                # Check for potential blocking or redirects
                if "captcha" in html_content or "robot" in html_content:
                    print("⚠️  Possible bot detection/captcha")
                
                if "javascript" in html_content and "enable" in html_content:
                    print("⚠️  Page might require JavaScript")
                
                # Look for error messages
                error_indicators = ["erreur", "error", "404", "403", "blocked", "access denied"]
                for indicator in error_indicators:
                    if indicator in html_content:
                        print(f"⚠️  Found potential error indicator: {indicator}")
                
            else:
                print(f"❌ Failed to load page: {result.error_message}")
                
        except Exception as e:
            print(f"❌ Error during scraping: {e}")


if __name__ == "__main__":
    asyncio.run(debug_doctolib_page())