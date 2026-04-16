import os
import json
import time
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google.genai import types
from app.database.connection import get_db
from app.database.models import JobDigest, RawJobPosting
from app.agents.base import BaseAgent

class JobScoring(BaseModel):
    match_score: int = Field(description="Score from 1 to 10 including how perfectly this job aligns with the candidate's profile")

class JobCuratorAgent(BaseAgent):
    def __init__(self, profile_path: str = "app/profiles/candidate_profile.md"):
        super().__init__()

        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                self.profile_text = f.read()

        else:
            self.profile_text = "No profile provided."
            print(f"Warning: Profile file not found at {profile_path}")

        self.system_instruction = "You are a ruthless career strategist. Compare the jobs detals to the candidate's profile. Score the fit from 1 to 10. Be highly critical regarding tech stack and location mismatches. Only award 9s or 10s for the perfect matches."

    def fetch_unscored_jobs(self, session: Session, limit: int=10):
        return session.query(JobDigest, RawJobPosting)\
        .join(RawJobPosting, JobDigest.raw_job_id == RawJobPosting.id)\
        .filter(JobDigest.match_score.is_(None))\
        .limit(limit).all()
    
    def score_job(self, job_details: str)-> dict:
        prompt = f"Candidate Profile:\n{self.profile_text}\n\nJob Details:\n{job_details}"

        response = self.client.models.generate_content(
            model = self.model_name,
            contents = prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type = "application/json",
                response_schema=JobScoring,
                temperature=0.4,
            ),
        )
        return json.loads(response.text)
    
    def run(self):
        session: Session = next(get_db())
        try:
            unscored_records = self.fetch_unscored_jobs(session)

            for digest, raw_job in unscored_records:
                job_string = f"""
                Title: {raw_job.job_title}
                Company: {raw_job.company_name}
                Tech Stack: {digest.tech_stack}
                Salary: {digest.estimated_salary}
                Experience Required: {digest.years_of_experience}
                Summary: {digest.brief_summary}
                """

                try:
                    extracted_data = self.score_job(job_string)

                    digest.match_score = extracted_data.get("match_score")
                    print(f"Scored {raw_job.job_title} at {raw_job.company_name}: {digest.match_score}/10")
                    time.sleep(4)

                except Exception as e:
                    print(f"Error scoring job ID {digest.id}: {e}")

            session.commit()
            print("Curation batch complete.")
        finally:
            session.close()