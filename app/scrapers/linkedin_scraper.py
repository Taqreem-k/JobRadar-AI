import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper

class LinkedInScraper(BaseScraper):
    def __init__(self, keyword: str, location: str):
        super().__init__()
        self.keyword = keyword
        self.location = location
        self.target_url = f"https://www.linkedin.com/jobs/search?keywords={keyword}&location={location}"

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            print(f"Navigating to {self.target_url}...")
            page.goto(self.target_url)
            
            try:
                page.wait_for_selector(".jobs-search__results-list", timeout=10000)
            except Exception:
                print("Could not find job results list. Page might have blocked us or changed layout.")
                browser.close()
                return

            soup = BeautifulSoup(page.content(), 'html.parser')
            
            job_cards = soup.find_all('div', class_='base-card') or soup.find_all('li', class_='result-card')
            print(f"Found {len(job_cards)} jobs on the page.")

            for card in job_cards:
                try:
                    # Extract basic info from the card
                    title_tag = card.find('h3', class_='base-search-card__title')
                    company_tag = card.find('h4', class_='base-search-card__subtitle')
                    link_tag = card.find('a', class_='base-card__full-link')
                    location_tag = card.find('span', class_='job-search-card__location')

                    job_title = title_tag.text.strip() if title_tag else "Unknown"
                    company_name = company_tag.text.strip() if company_tag else "Unknown"
                    job_url = link_tag['href'].split('?')[0] if link_tag else None # Clean URL parameters
                    location = location_tag.text.strip() if location_tag else "Unknown"

                    if not job_url:
                        continue

                    print(f"Scraping details: {job_title} @ {company_name}")

                    page.goto(job_url)
                    
                    page.wait_for_selector(".description__text", timeout=5000)
                    
                    desc_element = page.query_selector(".description__text")
                    raw_html = desc_element.inner_html() if desc_element else ""

                    clean_desc = self.clean_html(raw_html)

                    job_data = {
                        "job_url": job_url,
                        "job_title": job_title,
                        "company_name": company_name,
                        "location": location,
                        "raw_text": clean_desc
                    }

                    self.save_to_db(job_data)

                    time.sleep(3)

                except Exception as e:
                    print(f"Error scraping individual job: {e}")
                    continue

            browser.close()