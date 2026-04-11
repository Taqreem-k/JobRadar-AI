import requests
from app.scrapers.base import BaseScraper

class GenericJobScraper(BaseScraper):
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url

    def fetch_data(self) -> list[dict]:
        response = requests.get(self.api_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data from API. Status: {response.status_code}")
            return []

    def run(self):
        raw_list = self.fetch_data()
        
        for item in raw_list:
            try:
                job_url = item.get("url") or item.get("job_url")
                job_title = item.get("title") or item.get("job_title")
                company_name = item.get("company_name") or item.get("company")
                raw_description = item.get("description") or ""

                if not job_url or not job_title:
                    continue

                clean_desc = self.clean_html(raw_description)

                job_data = {
                    "job_url": job_url,
                    "job_title": job_title,
                    "company_name": company_name,
                    "description": clean_desc
                }

                self.save_to_db(job_data)
                
            except Exception as e:
                print(f"Error processing API item: {e}")