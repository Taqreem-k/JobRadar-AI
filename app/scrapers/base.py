import html2text
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import RawJobPosting

class BaseScraper:
    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True

    def clean_html(self, raw_html: str) -> str:
        return self.html_converter.handle(raw_html)
    
    def save_to_db(self,job_data: dict):
        session: Session = next(get_db())

        try:
            existing_job = session.query(RawJobPosting).filter(RawJobPosting.job_url == job_data["job_url"]).first()

            if existing_job:
                print("Job already exists")
            
            else:
                new_job = RawJobPosting(**job_data)
                session.add(new_job)
                session.commit()
        
        finally:
            session.close()