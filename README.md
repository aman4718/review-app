---
title: ChatGPT India Review Pulse
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.45.0
app_file: app.py
pinned: false
---

# ChatGPT India — App Review Insights Analyser

Automated weekly pipeline: Play Store reviews → BERTopic clusters → Groq LLM pulse → Email via Resend.

---

## Project Structure

```
reviewer-app/
├── scraper.js               # Phase 1: Play Store scraper (Node.js)
├── cluster.py               # Phase 2: BERTopic clustering (5 themes)
├── analyse.py               # Phase 3: Groq LLM analysis → pulse.json
├── report.py                # Phase 4: Jinja2 report renderer
├── emailer.py               # Phase 5: Email via Resend API
├── app.py                   # Streamlit dashboard (interactive UI)
├── main.py                  # Orchestrator: runs all 5 phases
├── requirements.txt         # Python dependencies
├── package.json             # Node.js dependencies
├── .env.example             # Environment variable template
├── templates/
│   ├── pulse.md.j2          # Markdown report template
│   └── pulse.html.j2        # HTML email template
├── data/                    # Pipeline intermediate files (git-ignored)
│   ├── raw_reviews.csv
│   ├── clustered_reviews.csv
│   └── pulse.json
├── output/                  # Final reports (git-ignored)
│   ├── weekly_pulse.md
│   └── weekly_pulse.html
└── .github/workflows/
    └── weekly.yml           # GitHub Actions: runs every Monday 07:00 IST
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd reviewer-app

# Node dependencies (scraper)
npm install

# Python dependencies
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
GROQ_API_KEY=gsk_your_groq_key_here
RESEND_API_KEY=re_your_resend_key_here
RECIPIENT_EMAIL=your_email@gmail.com
```

### 3. Get your API keys

| Key | Where to get |
|-----|-------------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — free, no card |
| `RESEND_API_KEY` | [resend.com](https://resend.com) — free, 3000 emails/month |
| `RECIPIENT_EMAIL` | Your email address where you want to receive reports |

---

## Streamlit Dashboard

Launch the interactive dashboard to run the pipeline and explore insights in your browser:

```bash
python -m streamlit run app.py
```

Opens at **http://localhost:8501** — no extra config needed.

The dashboard has four tabs:
- **Run Pipeline** — trigger all 5 phases (or individual phases) with live log output
- **Insights** — executive summary, theme breakdown, sentiment badges, quotes & actions
- **Raw Data** — rating distribution chart + searchable review tables
- **Report** — download HTML/Markdown report or preview it inline

---

## Run

### Run full pipeline (all 5 phases)
```bash
python main.py
```

### Run a single phase
```bash
python main.py --phase scrape    # Phase 1: Fetch reviews
python main.py --phase cluster   # Phase 2: Cluster into 5 themes
python main.py --phase analyse   # Phase 3: LLM analysis
python main.py --phase report    # Phase 4: Generate HTML/MD report
python main.py --phase email     # Phase 5: Send email
```

### Run scraper only (Node)
```bash
node scraper.js
```

---

## Re-run for a new week

Just run again — it always fetches the latest 200 reviews:
```bash
python main.py
```

---

## Theme Legend

Themes are auto-generated each week by KMeans + LLM labelling.
Typical themes for ChatGPT India:
- Voice UX issues
- Language / Hinglish support
- Paywall & subscription friction
- Response quality
- App performance & crashes

---

## GitHub Actions (Automated Weekly Email)

### Setup secrets in GitHub

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `GROQ_API_KEY` | Your Groq API key |
| `RESEND_API_KEY` | Your Resend API key |
| `RECIPIENT_EMAIL` | Destination email address |

### Schedule

Pipeline runs automatically every **Monday at 07:00 IST** (01:30 UTC).

Manual trigger: **Actions tab** → **Weekly Review Pulse** → **Run workflow**

---

## Pipeline Flow

```
Play Store (com.openai.chatgpt, India)
    ↓ google-play-scraper
raw_reviews.csv  [date, rating, title, review_text, platform]
    ↓ sentence-transformers + KMeans
clustered_reviews.csv  [+theme_id, +theme_label]
    ↓ Groq llama3-8b-8192
pulse.json  [top_themes, quotes, action_items, executive_summary]
    ↓ Jinja2
weekly_pulse.md + weekly_pulse.html
    ↓ Resend API
Email Inbox — every Monday 07:00 IST
```

---

Milestone 2 | ChatGPT Voice for India | AI PM Cohort 2026
