import asyncio
from playwright.async_api import async_playwright
import argparse
import random
import json
import time
import os
import re
from urllib.parse import urlparse, urljoin

async def scrape(base_url, out_folder, headless=True, proxy=None, max_pages=50, delay_min=1, delay_max=3):
    async with async_playwright() as p:
        launch_args = {"headless": headless}
        if proxy:
            launch_args["proxy"] = {"server": proxy}

        browser = await p.chromium.launch(**launch_args)

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/118.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768}
        )

        page = await context.new_page()

        # Extract university base URL and college name
        university_base = extract_university_base(base_url)
        college_name = extract_college_name(base_url)
        
        print(f"University base URL: {university_base}")
        print(f"College name: {college_name}")
        
        # Create main college folder only
        college_folder = os.path.join(out_folder, college_name)
        os.makedirs(college_folder, exist_ok=True)
        print(f"Main folder: {college_folder}")

        visited = set()
        to_visit = [base_url]
        scraped_count = 0

        while to_visit and scraped_count < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)

            try:
                print(f"[{scraped_count+1}/{max_pages}] Visiting: {url}")
                await page.goto(url, wait_until="networkidle", timeout=60000)

                # Scroll to trigger lazy-loaded content
                await page.mouse.wheel(0, 2000)
                await page.wait_for_timeout(2000)

                # Extract text content
                text = await page.inner_text("body")
                
                # Get page title
                title = await page.title()

                # Get filename with category prefix
                filename = generate_filename(url, university_base)
                filepath = os.path.join(college_folder, filename)
                category = detect_category(url)

                # Prepare data
                page_data = {
                    "url": url,
                    "title": title,
                    "content": text,
                    "category": category,
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                # Save to JSON file in main folder
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(page_data, f, indent=2, ensure_ascii=False)
                
                print(f"   Saved to: {filename}")
                scraped_count += 1

                # Collect links for further crawling - only university-specific pages
                links = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
                for link in links:
                    if link and is_university_page(link, university_base):
                        if link not in visited and link not in to_visit:
                            to_visit.append(link)
                            link_category = detect_category(link)
                            print(f"   Found {link_category} page: {link}")

                # Random delay to avoid detection
                time.sleep(random.uniform(delay_min, delay_max))

            except Exception as e:
                print(f"Error while processing {url}: {e}")

        print(f"\n✅ Crawling finished. Pages scraped: {scraped_count}")
        print(f"All files saved in: {college_folder}")

        await browser.close()

def detect_category(url):
    """Detect the category of the page from URL"""
    url_lower = url.lower()
    
    # Define category patterns
    if any(word in url_lower for word in ["admission", "apply", "application", "entrance", "eligibility"]):
        return "admission"
    elif any(word in url_lower for word in ["cutoff", "cut-off", "ranking", "rank", "jee", "neet", "gate"]):
        return "cutoff"
    elif any(word in url_lower for word in ["placement", "career", "job", "company", "recruit", "salary"]):
        return "placements"
    elif any(word in url_lower for word in ["hostel", "accommodation", "residence", "boarding"]):
        return "hostel"
    elif any(word in url_lower for word in ["fee", "cost", "tuition", "expense", "payment"]):
        return "fees"
    elif any(word in url_lower for word in ["scholarship", "financial-aid", "grant", "stipend"]):
        return "scholarship"
    elif any(word in url_lower for word in ["faculty", "professor", "teacher", "staff", "dean"]):
        return "faculty"
    elif any(word in url_lower for word in ["department", "school", "division", "branch"]):
        return "departments"
    elif any(word in url_lower for word in ["infrastructure", "facility", "campus", "lab", "library"]):
        return "infrastructure"
    elif any(word in url_lower for word in ["ranking", "nirf", "rating"]):
        return "ranking"
    elif any(word in url_lower for word in ["review", "feedback", "opinion"]):
        return "reviews"
    elif any(word in url_lower for word in ["gallery", "photo", "image"]):
        return "gallery"
    elif any(word in url_lower for word in ["course", "program", "degree", "btech","engineering", "mtech", "mba", "bsc", "msc"]):
        return "courses"
    else:
        return "profile"

def generate_filename(url, university_base):
    """Generate a descriptive filename with category prefix"""
    category = detect_category(url)
    
    # Extract meaningful part from URL
    if url.startswith(university_base):
        page_path = url[len(university_base):].strip("/")
    else:
        parsed_url = urlparse(url)
        page_path = parsed_url.path.strip("/")
    
    if not page_path:
        return f"{category}_main.json"
    
    # Clean the path and make it descriptive
    clean_path = re.sub(r"[^a-zA-Z0-9-_/]", "_", page_path)
    clean_path = clean_path.replace("/", "_").strip("_")
    
    # Limit length
    if len(clean_path) > 60:
        clean_path = clean_path[:60]
    
    # Add category prefix for better organization
    if clean_path and category not in clean_path:
        filename = f"{category}_{clean_path}.json"
    else:
        filename = f"{clean_path}.json" if clean_path else f"{category}_page.json"
    
    return filename

def extract_university_base(base_url):
    """Extract the university base URL pattern for collegedunia"""
    if "/university/" in base_url:
        parts = base_url.split("/university/")
        if len(parts) >= 2:
            university_part = parts[1].split("/")[0]
            return f"{parts[0]}/university/{university_part}"
    return base_url.rstrip("/")

def extract_college_name(base_url):
    """Extract college name from collegedunia URL for folder naming"""
    if "/university/" in base_url:
        parts = base_url.split("/university/")
        if len(parts) >= 2:
            university_part = parts[1].split("/")[0]
            # Remove the ID prefix and clean up the name
            if "-" in university_part:
                # Remove ID (numbers) and clean the name
                college_name = re.sub(r'^\d+-', '', university_part)
                college_name = college_name.replace("-", "_")
                return college_name
    return "unknown_college"

def is_university_page(link, university_base):
    """Check if the link belongs to the specific university on collegedunia"""
    if not link or not link.startswith("http"):
        return False
    
    # Must contain collegedunia.com and reference the same university
    if "collegedunia.com" in link:
        # Extract university ID from both URLs
        base_id = extract_university_id(university_base)
        link_id = extract_university_id(link)
        return base_id and link_id and base_id == link_id
    
    return False

def extract_university_id(url):
    """Extract university ID from collegedunia URL"""
    if "/university/" in url:
        parts = url.split("/university/")
        if len(parts) >= 2:
            university_part = parts[1].split("/")[0]
            # Extract just the ID part (numbers at the beginning)
            id_match = re.match(r'^(\d+)', university_part)
            if id_match:
                return id_match.group(1)
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Base URL to start scraping")
    parser.add_argument("--out", default="scraped_data", help="Output folder for college data")
    parser.add_argument("--headless", default=True, type=bool, help="Run headless or not")
    parser.add_argument("--proxy", default=None, help="Proxy server (http://user:pass@ip:port)")
    parser.add_argument("--max-pages", default=50, type=int, help="Maximum pages to scrape")
    parser.add_argument("--delay-min", default=1, type=float, help="Minimum delay between requests")
    parser.add_argument("--delay-max", default=3, type=float, help="Maximum delay between requests")

    args = parser.parse_args()

    asyncio.run(scrape(
        base_url=args.base,
        out_folder=args.out,
        headless=args.headless,
        proxy=args.proxy,
        max_pages=args.max_pages,
        delay_min=args.delay_min,
        delay_max=args.delay_max
    ))
