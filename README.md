[README.md](https://github.com/user-attachments/files/26042242/README.md)
# 🤖 Autonomous Job Hunting CRM

> Scrapes 60+ job sources worldwide → AI parses tech stacks → generates personalised cold emails → React dashboard to manage and send leads.

Built by **Parameswar Swain** using Python, Playwright, Groq/Llama AI, FastAPI, and React.

---

## 🚀 What It Does

Most job seekers manually browse Naukri, Indeed, LinkedIn one by one. This tool automates the entire pipeline:

1. **Scrapes** 60+ job sources — Naukri, Indeed, Internshala, Shine, company career pages, ATS portals (Greenhouse, Lever, Workable), Google Jobs, Telegram groups, and more
2. **AI parses** each company's tech stack from their website using Groq/Llama 3.3
3. **Generates** a personalised cold email for each lead based on the company's actual stack
4. **Scores** each lead (0–100) based on tech stack match, contact seniority, and funding stage
5. **Serves** everything through a FastAPI backend and live React dashboard
6. **Sends** approved emails directly via Gmail SMTP

---

## 📸 Screenshots

### CLI Menu
```
╔══════════════════════════════════════════════════════════╗
  🤖  AUTONOMOUS JOB HUNTING & B2B LEAD GEN CRM
      by Parameswar Swain | parameswar.dev
╠══════════════════════════════════════════════════════════╣
  [1] 🏙  Hunt LOCAL  — Odisha Companies (cold email)
  [2] 🌍  Hunt GLOBAL — YC/HN React Startups (Remote)
  [3] 📊  View Stats & Top Leads
  [4] 📤  Export Leads to CSV
  [5] 📬  Send Approved Emails (Gmail SMTP)
  [6] 🌐  Launch Web Dashboard
  [J] 🔍  HIDDEN BBSR Jobs — Beats Naukri/Indeed
  [0] ❌  Exit
╚══════════════════════════════════════════════════════════╝
```

### Sample Lead Output
```
╔══════════════════════════════════════════════════════════╗
  ✅ LEAD  📍 LOCAL
  Company : Razorpay (VC funded)
  Domain  : razorpay.com
  Stack   : JavaScript, Python, Java, Postgres, AWS, Docker
  Contact : Atanu Chowdhury — Associate Director
  Email   : atanu.chowdhury@razorpay.com [99%]
  Score   : 94/100  █████████░
  Subject : Optimizing JavaScript at Scale
  Body    : Your JavaScript stack can benefit from edge caching...
╚══════════════════════════════════════════════════════════╝
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Web Scraping | Python + Playwright (stealth, anti-bot) |
| AI / LLM | Groq API + Llama 3.3 70B |
| Backend API | FastAPI + Uvicorn |
| Frontend | React + Tailwind CSS |
| Database | SQLite (via custom ORM) |
| Email | Gmail SMTP |
| Contact Enrichment | Apollo.io API (optional) |
| Search | Serper.dev / DuckDuckGo (free) |

---

## 📁 Project Structure

```
jobs_hunt/
├── run.py                  ← Interactive CLI (main entry point)
├── api_server.py           ← FastAPI backend + dashboard
├── requirements.txt
├── .env.example            ← Copy to .env and add your keys
├── backend/
│   ├── orchestrator.py     ← Main pipeline (scrape → AI → score → save)
│   ├── scraper.py          ← Playwright stealth scraper
│   ├── ai_brain.py         ← Groq/Llama AI parser + email generator
│   ├── db_manager.py       ← SQLite CRUD layer
│   ├── bbsr_jobs.py        ← Bhubaneswar hidden job hunter
│   ├── naukri_scraper.py   ← Naukri + Internshala scraper
│   ├── smtp_sender.py      ← Gmail SMTP sender
│   ├── exporter.py         ← CSV export
│   └── data_shield.py      ← GDPR auto-purge
├── database/
│   └── schema.sql
└── frontend/
    └── src/app/page.jsx    ← React dashboard
```

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/parameswar6/jobs-hunt-crm.git
cd jobs-hunt-crm
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 3. Configure API keys
```bash
cp .env.example .env
```
Then open `.env` and add:
```
GROQ_API_KEY=your_key_here        # free at console.groq.com
APOLLO_API_KEY=your_key_here      # optional, free at apollo.io
SERPER_API_KEY=your_key_here      # optional, free at serper.dev
SMTP_FROM_EMAIL=you@gmail.com     # optional, for sending emails
SMTP_APP_PASSWORD=xxxx xxxx xxxx  # Gmail App Password
```

### 4. Run
```bash
python run.py
```

### 5. Open dashboard
```bash
# Terminal 1
python api_server.py

# Open browser
http://localhost:8000
```

---

## 🎯 Job Sources Scraped

**Indian Job Boards**
Naukri · Internshala · Shine · TimesJobs · Foundit · Freshersworld · Hirist · Cutshort · Instahyre

**Global Job Boards**
Indeed India · Glassdoor · Wellfound (AngelList)

**Hidden Sources (not on Naukri)**
- ATS portals: Greenhouse, Lever, Workable, Freshteam
- 16 Bhubaneswar company career pages directly
- Google Jobs widget (aggregates everything)
- Google dorks: LinkedIn public, Telegram groups, Google Drive PDFs
- Twitter/X hiring posts

**Direct Company Targets**
Mindfire Solutions · Tatwa Technologies · CSM Technologies · Tekdi · Incobist · LTIMindtree · Tech Mahindra · Capgemini · Razorpay · BrowserStack · Groww · Hasura · smallcase · and more

---

## 📊 How Scoring Works

Each lead is scored 0–100:

| Signal | Points |
|---|---|
| React / Next.js in stack | +12 each |
| TypeScript | +10 |
| Java / Spring Boot (local mode) | +12 each |
| Verified email found | +15–20 |
| CTO / Founder title | +14–15 |
| Director of Engineering | +8 |
| Series A / Seed funding | +9–10 |

Leads below 15 points are automatically skipped.

---

## ✉️ Email Generation

The AI generates a unique cold email for each lead based on:
- Their actual tech stack (not generic)
- The contact's job title
- Funding stage
- A matching proof point from your portfolio

Example output:
> **Subject:** Optimizing React + Node.js at Groww
>
> I noticed Groww's stack relies on React and Node.js — I recently built an autonomous CRM pipeline using Playwright + Groq AI + FastAPI + React that scrapes 60+ job sources end-to-end. I'd love to explore if there's a fit — are you free for a 15-minute call this week?

---

## 🔒 Privacy

- All PII (names, emails) is auto-purged after 14 days with no reply
- GDPR/CCPA compliant audit log
- Run `python run.py` → `[7]` for GDPR dry-run report

---

## 📄 License

MIT — free to use and modify.

---

## 👤 Author

**Parameswar Swain**
 [github.com/parameswar6](https://github.com/parameswar6) · [swainparameswar67@gmail.com](mailto:swainparameswar67@gmail.com)
