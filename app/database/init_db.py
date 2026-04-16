from app.database.connection import engine, Base

from app.database.models import Base, RawJobPosting, JobDigest

def init():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init()
