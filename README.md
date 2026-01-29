# AI News Aggregator 🤖📰

An automated pipeline that scrapes, summarizes, ranks, and emails the latest AI news daily.

## Key Features
- **Multi-Source Scraping**: Fetches news from OpenAI, Anthropic, and top YouTube channels (with transcript analysis).
- **Intelligent Summarization**: Uses Google Gemini to generate concise technical summaries.
- **Personalized Ranking**: Ranks stories based on your user profile using AI.
- **Automated Delivery**: Sends a clean HTML daily digest email.
- **Fully Automated**: Runs daily at **6:00 AM IST** via GitHub Actions.

## Tech Stack
- **Core**: Python 3.12, Docker, PostgreSQL (Neon DB).
- **AI**: Google Gemini Pro 1.5/Flash, YouTube Transcript API.
- **Deployment**: GitHub Actions (Scheduled Workflow).

## Setup & Configuration

1. **Clone the repo**
2. **Create a `.env` file** with the following secrets:
   ```env
   # Database (Neon Postgres)
   NEON_DATABASE_URL=postgresql://...

   # AI Provider
   GOOGLE_API_KEY=AIza...

   # Email Service (Gmail App Password)
   GMAIL_ID=your_email@gmail.com
   GOOGLE_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

   # Proxies (Webshare)
   WEBSHARE_USERNAME=...
   WEBSHARE_PASSWORD=...
   WEBSHARE_DOMAIN_NAME=...
   WEBSHARE_PORT=...
   ```

## Running Locally

### Option 1: Docker (Recommended)
```bash
docker compose -f docker/docker-compose.yml --env-file .env up --build
```

### Option 2: Python Direct
```bash
pip install -r requirements.txt
python run_pipeline.py
```

## Deployment
The project is configured to auto-deploy using **GitHub Actions**.
1. Push code to `main`.
2. Add all `.env` variables to **GitHub Repo Secrets**.
3. The workflow `.github/workflows/ai_news.yml` runs automatically every day.
