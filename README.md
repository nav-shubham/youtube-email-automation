# YouTube + Email Automation Tools

Collection of Python automation scripts for:

- Email reporting from Gmail
- YouTube video tracking
- Automated YouTube downloads
- Excel report generation

---

# Features

## Email Report Script

- Fetches recent Gmail emails
- Converts timestamps to IST
- Generates Excel report
- Creates direct Gmail links

## YouTube Pipeline

- Tracks latest uploads from subscribed channels
- Uses RSS + YouTube API
- Generates Excel review sheet
- Downloads selected videos automatically

---

# Project Structure

```text
youtube_email/
│
├── downloads/
├── old versions/
├── venv/
│
├── email_report.py
├── youtube_full_pipeline.py
│
├── subscriptions.csv
├── special_channels.csv
│
├── requirements.txt
├── README.md
├── .gitignore
```

---

# Setup

## 1. Create Virtual Environment

```bash
python -m venv venv
```

## 2. Activate Environment

### Windows

```bash
venv\Scripts\activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run Scripts

## Email Report

```bash
python email_report.py
```

## YouTube Pipeline

```bash
python youtube_full_pipeline.py
```

---

# Git Commands

```bash
git init
git add .
git commit -m "Initial commit"
```

---

# Important Notes

- Keep API keys and passwords inside `.env`
- Never upload secrets to GitHub
- Reports and downloads are ignored using `.gitignore`

---

# Tech Stack

- Python
- Pandas
- yt-dlp
- feedparser
- Gmail IMAP
- YouTube Data API
