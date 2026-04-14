import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import JobDigest, RawJobPosting
from app.config import SENDER_EMAIL, EMAIL_APP_PASSWORD, RECEIVER_EMAIL

class EmailService:
    def __init__(self):
        self.sender_email = SENDER_EMAIL
        self.password = EMAIL_APP_PASSWORD
        self.receiver_email = RECEIVER_EMAIL

    def fetch_top_jobs(self, session: Session, limit: int = 5):
        return session.query(JobDigest, RawJobPosting)\
            .join(RawJobPosting, JobDigest.raw_job_id == RawJobPosting.id)\
            .filter(JobDigest.is_emailed == False)\
            .filter(JobDigest.match_score.isnot(None))\
            .order_by(JobDigest.match_score.desc())\
            .limit(limit).all()

    def generate_html(self, jobs: list) -> str:
        html = """
        <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; padding: 20px; color: #333; }
                .card { background-color: #ffffff; padding: 20px; margin-bottom: 20px; border-radius: 8px; border-left: 5px solid #2ecc71; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
                .title { font-size: 22px; font-weight: bold; margin-bottom: 5px; color: #2c3e50; }
                .company { font-size: 16px; margin-bottom: 15px; color: #7f8c8d; }
                .score { font-weight: bold; color: #2ecc71; font-size: 18px; }
                .details { margin-bottom: 15px; line-height: 1.6; }
                .btn { display: inline-block; padding: 10px 15px; color: #ffffff; background-color: #3498db; text-decoration: none; border-radius: 5px; font-weight: bold; }
                .btn:hover { background-color: #2980b9; }
            </style>
        </head>
        <body>
            <h2 style="color: #2c3e50;">Job Radar AI: Daily Matches</h2>
        """

        for digest, raw_job in jobs:
            html += f"""
            <div class="card">
                <div class="title">{raw_job.job_title}</div>
                <div class="company">{raw_job.company_name}</div>
                <div class="details">
                    <span class="score">Match Score: {digest.match_score}/10</span><br>
                    <strong>Estimated Salary:</strong> {digest.estimated_salary}<br>
                    <strong>Tech Stack:</strong> {digest.tech_stack}
                </div>
                <a href="{raw_job.job_url}" class="btn">View Original Posting</a>
            </div>
            """

        html += """
        </body>
        </html>
        """
        return html

    def send_email(self, html_content: str):
        message = MIMEMultipart("alternative")
        message["Subject"] = "Job Radar AI: Your Top Matches for Today"
        message["From"] = self.sender_email
        message["To"] = self.receiver_email

        part = MIMEText(html_content, "html")
        message.attach(part)

        context = ssl.create_default_context()
        
        try:
            print("Connecting to SMTP server...")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

    def run(self):
        session: Session = next(get_db())
        try:
            print("Fetching top jobs...")
            jobs = self.fetch_top_jobs(session)
            
            if not jobs:
                print("No new jobs to email.")
                return

            print(f"Found {len(jobs)} high-value jobs. Generating HTML...")
            html_content = self.generate_html(jobs)
            
            self.send_email(html_content)
            
            for digest, raw_job in jobs:
                digest.is_emailed = True
            
            session.commit()
            print("Delivery phase complete.")
        except Exception as e:
            print(f"Error in EmailService run loop: {e}")
        finally:
            session.close()