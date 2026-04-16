import json
import time
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google.genai import types
from app.database.connection import get_db
from app.database.models import RawJobPosting, JobDigest
from app.agents.base import BaseAgent

class JobExtraction(BaseModel):
    estimated_salary: str = Field(description="Extract salary range. if none found, write 'Not Specified'")
    tech_stack: str = Field(description="Comma separated list of programming languages and tools")
    years_of_experience: str = Field(description="Required years of experience")
    brief_summary: str = Field("A strict 2-sentence summary of the role")

class JobDigestAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.system_instruction = "You are an expert technical AI recruiter. Read the following raw job description and extract the exact parameters requested. Do not hallucinate data." 

    def fetch_unprocessed_jobs(self, session: Session, limit: int =10):
        return session.query(RawJobPosting).filter(RawJobPosting.is_processed == False).limit(limit).all()

    def extract_data(self, raw_text: str)-> dict:
        response = self.client.models.generate_content(
            model = self.model_name,
            contents = raw_text,
            config = types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema = JobExtraction,
                temperature= 0.1,
            ),
        )
        return json.loads(response.text)

    def run(self):
        session: Session = next(get_db())
        try:
            jobs = self.fetch_unprocessed_jobs(session)

            for job in jobs:
                print(f"Digesting job: {job.job_title} at {job.company_name}")
                try:
                    extracted_data = self.extract_data(job.raw_text)

                    new_digest = JobDigest(
                        raw_job_id= job.id,
                        estimated_salary= extracted_data.get("estimated_salary"),
                        tech_stack=extracted_data.get("tech_stack"),
                        years_of_experience = extracted_data.get("years_of_experience"),
                        brief_summary = extracted_data.get("brief_summary")
                    )                     
                    session.add(new_digest)

                    job.is_processed = True
                    time.sleep(4)
                
                except Exception as e:
                    print(f"Error extracting data for job ID {job.id}: {e}")
            
            session.commit()
            print("Digest batch complete.")
        finally:
            session.close()