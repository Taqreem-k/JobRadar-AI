import requests
from app.scrapers.base import BaseScraper

class GenericJobScraper(BaseScraper):
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url

    def fetch_data(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            return response.json()[1:] 
        return []

    def run(self):
        raw_jobs = self.fetch_data()
        print(f"📡 Found {len(raw_jobs)} jobs from API. Saving to database...")
        
        for job in raw_jobs[:10]: 
            try:
                job_url = job.get("url")
                title = job.get("position")
                company = job.get("company")
                location = job.get("location", "Remote")
                raw_html = job.get("description", "")
                
                clean_desc = self.clean_html(raw_html)
                
                job_data = {
                    "job_url": job_url,
                    "job_title": title,
                    "company_name": company,
                    "location": location,
                    "raw_text": clean_desc
                }
                
                self.save_to_db(job_data)
            except Exception as e:
                print(f"Skipped a job due to error: {e}")