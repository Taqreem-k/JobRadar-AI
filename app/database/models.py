from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from app.database.connection import Base
from datetime import datetime, timezone

class RawJobPosting(Base):
    __tablename__ = "raw_job_posting"

    id = Column(Integer, primary_key=True)
    job_url = Column(String, unique=True, index= True)
    job_title = Column(String)
    company_name = Column(String)
    location = Column(String)
    raw_text = Column(Text)
    scraped_at = Column(DateTime,default=datetime.now(timezone.utc))
    is_processed = Column(Boolean, default=False)

class JobDigest(Base):
    __tablename__ ="job_digest"

    id = Column(Integer, primary_key=True)
    raw_job_id = Column(Integer, ForeignKey(RawJobPosting.id))
    estimated_salary = Column(String)
    tech_stack = Column(String)
    years_of_experience = Column(String)
    brief_summary = Column(Text)
    match_score = Column(Integer, nullable=True)
    is_emailed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))