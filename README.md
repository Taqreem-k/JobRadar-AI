# 🎯 Autonomous AI Job Radar

An end-to-end, LLM-powered data pipeline that scrapes job boards, structures messy descriptions, scores roles against a personal candidate profile, and delivers a highly curated daily email digest.

![Python](https://img.shields.io/badge/PYTHON-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/PLAYWRIGHT-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/POSTGRESQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLALCHEMY-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Gemini 2.5 Flash](https://img.shields.io/badge/GEMINI_2.5_FLASH-8E75B2?style=for-the-badge&logo=googlebard&logoColor=white)
![Docker](https://img.shields.io/badge/DOCKER-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## 🏗️ Architecture Overview

The pipeline executes daily in five distinct phases:

1. **Ingestion (Scrapers):** Utilizes `Playwright` for heavy DOM-rendering sites (bypassing basic bot protections) and lightweight `requests` for open APIs (e.g., RemoteOK). Raw HTML is cleaned to Markdown to save API tokens.
2. **Database Foundation:** A localized Dockerized `PostgreSQL` instance manages the state across two tables: `RawJobPosting` and `JobDigest`.
3. **Digestion (AI Extraction):** The `JobDigestAgent` utilizes Gemini 2.5 Flash's Structured Outputs to read raw job descriptions and strictly extract Salary, Tech Stack, Experience, and a 2-sentence summary into a JSON schema.
4. **Curation (AI Scoring):** The `JobCuratorAgent` loads a local `candidate_profile.md` (acting as a strict career strategist) and assigns a `match_score` (1-10) to each digested job based on technical and cultural fit.
5. **Delivery (Orchestration):** The pipeline queries the top 5 highest-scored, un-emailed jobs, compiles them into an HTML template, and fires them off via Gmail SMTP.

![Architecture Flow](asset/architecture.png) 

## 🛠️ Tech Stack

* **Language:** Python 3
* **Package Manager:** `uv`
* **Database:** PostgreSQL (via Docker Compose)
* **ORM:** SQLAlchemy
* **Scraping:** Playwright, BeautifulSoup4, HTML2Text
* **AI:** Google GenAI SDK (Gemini 2.5 Flash)

## ⚙️ Prerequisites

Before running the project locally, ensure you have the following installed:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for the database)
* [`uv`](https://github.com/astral-sh/uv) (for lightning-fast dependency management)
* A [Google Gemini API Key](https://aistudio.google.com/)
* A [Gmail App Password](https://support.google.com/accounts/answer/185833?hl=en)

## 🚀 Local Setup & Installation

**1. Clone the repository and navigate to the project directory:**
```bash
git clone [https://github.com/Taqreem-k/JobRadar-AI.git](https://github.com/Taqreem-k/JobRadar-AI.git)
cd JobRadar-AI
```

**2. Configure Environment Variables:**
Create a `.env` file in the root directory and add the following credentials:

```text
# Database Configuration
DATABASE_URL=postgresql://postgres:supersecretpassword@localhost:5432/job_radar

# API & Email Credentials
GEMINI_API_KEY=your_gemini_api_key_here
SENDER_EMAIL=your_email@gmail.com
EMAIL_APP_PASSWORD=your_16_digit_app_password
RECEIVER_EMAIL=your_email@gmail.com
```

**3. Install Dependencies:**
Use `uv` to install all required packages from the `pyproject.toml` / `uv.lock` file:

```bash
uv sync
```

**4. Start the Database:**
Spin up the local PostgreSQL container in detached mode:

```bash
docker compose up -d
```

**5. Initialize the Tables:**
Run the database setup script to create the tables:

```bash
uv run python -m app.database.init_db
```

**6. Run the Pipeline:**
Execute the master orchestration script to verify all 5 phases run successfully:

```bash
uv run python app/runner.py
```

## ☁️ Deployment (Render)

This project is configured for seamless deployment on Render using Infrastructure as Code (`render.yaml`).

1. Connect your GitHub repository to Render.
2. Go to **Blueprints -> New Blueprint Instance** and select this repo.
3. Render will automatically provision a managed PostgreSQL database and a daily Cron Job scheduled for 8:30 AM EST (13:30 UTC).

**Important:** Add your `GEMINI_API_KEY`, `SENDER_EMAIL`, and `EMAIL_APP_PASSWORD` to the Environment Variables tab in the Render dashboard for the Cron Job service.

---

## 👨‍💻 Author

**Mohammad Taqreem Khan**