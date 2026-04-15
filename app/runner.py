from app.scrapers.linkedin_scraper import LinkedInScraper
from app.scrapers.generic_job_scraper import GenericJobScraper
from app.agents.job_digest_agent import JobDigestAgent
from app.agents.job_curator_agent import JobCuratorAgent
from app.services.email_service import EmailService

def main():
    print("🚀 Starting Phase 1: Ingestion")
    LinkedInScraper(keyword="Generative AI", location="India").run()
    
    GenericJobScraper(api_url="https://api.example.com/api").run()

    print("🧠 Starting Phase 3: Digestion (Phase 2 is the DB, always running implicitly)")
    JobDigestAgent().run()

    print("🎯 Starting Phase 4: Curation")
    JobCuratorAgent().run()

    print("📬 Starting Phase 5: Delivery")
    EmailService().run()

    print("✅ Daily Job Search Radar Complete!")

if __name__ == "__main__":
    main()