# ============================================================
# TASKRADAR BOT — COMPLETE SCRIPT
# Version 2.1 | Render Deployment
# Token and Channel ID pre-configured
# ============================================================

import requests
import json
import os
import time
from datetime import datetime

# ============================================================
# YOUR CREDENTIALS — ALREADY CONFIGURED
# ============================================================

BOT_TOKEN = "8996545766:AAFr2eQRMfhki9NSuMV9Bwx4FAJjVSp4kDE"
CHANNEL_ID = "-4296946400"

# ============================================================
# STATE FILE — TRACKS JOBS ALREADY SENT SO NO REPEATS
# ============================================================

STATE_FILE = "seen_jobs.json"

def load_seen_jobs():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return []

def save_seen_jobs(seen):
    with open(STATE_FILE, "w") as f:
        json.dump(seen[-500:], f)

# ============================================================
# SEND ALERT TO TELEGRAM CHANNEL
# ============================================================

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"Telegram response: {response.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")

# ============================================================
# SELF-MONITORING PING
# ============================================================

def send_owner_ping():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": "✅ TaskRadar is alive and running. " + datetime.now().strftime("%d %b %Y %H:%M"),
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Ping error: {e}")

# ============================================================
# KEYWORD FILTER — 10 CATEGORIES
# ============================================================

KEYWORDS = [
    "writing", "copywriting", "content", "blog", "seo",
    "design", "graphic", "logo", "figma", "canva", "ui", "ux",
    "developer", "web", "frontend", "backend", "wordpress", "shopify",
    "video", "editing", "motion", "youtube", "reels",
    "virtual assistant", "admin", "data entry", "scheduling",
    "social media", "instagram", "community manager",
    "marketing", "email marketing", "paid ads", "funnel",
    "data", "excel", "spreadsheet", "research", "analyst",
    "customer support", "live chat", "help desk",
    "ai", "prompt", "chatgpt", "artificial intelligence"
]

def matches_keywords(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

# ============================================================
# JOB FEED 1 — REMOTIVE
# ============================================================

def fetch_remotive(seen):
    new_jobs = []
    try:
        url = "https://remotive.com/api/remote-jobs?limit=20"
        response = requests.get(url, timeout=15)
        data = response.json()
        jobs = data.get("jobs", [])
        for job in jobs:
            job_id = f"remotive_{job['id']}"
            if job_id not in seen:
                title = job.get("title", "")
                company = job.get("company_name", "")
                link = job.get("url", "")
                category = job.get("category", "")
                if matches_keywords(title) or matches_keywords(category):
                    message = (
                        f"🚨 <b>NEW JOB ALERT</b>\n\n"
                        f"💼 <b>{title}</b>\n"
                        f"🏢 {company}\n"
                        f"📂 {category}\n"
                        f"🌍 Remote\n"
                        f"🔗 <a href='{link}'>Apply Now</a>\n\n"
                        f"⚡ via TaskRadar Pro"
                    )
                    new_jobs.append((job_id, message))
    except Exception as e:
        print(f"Remotive error: {e}")
    return new_jobs

# ============================================================
# JOB FEED 2 — REMOTEOK
# ============================================================

def fetch_remoteok(seen):
    new_jobs = []
    try:
        url = "https://remoteok.com/api"
        headers = {"User-Agent": "Mozilla/5.0 TaskRadar Job Bot"}
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        for job in data[1:21]:
            job_id = f"remoteok_{job.get('id', '')}"
            if job_id not in seen:
                title = job.get("position", "")
                company = job.get("company", "")
                link = job.get("url", "")
                tags = " ".join(job.get("tags", []))
                if matches_keywords(title) or matches_keywords(tags):
                    message = (
                        f"🚨 <b>NEW JOB ALERT</b>\n\n"
                        f"💼 <b>{title}</b>\n"
                        f"🏢 {company}\n"
                        f"📂 {tags[:60]}\n"
                        f"🌍 Remote\n"
                        f"🔗 <a href='{link}'>Apply Now</a>\n\n"
                        f"⚡ via TaskRadar Pro"
                    )
                    new_jobs.append((job_id, message))
    except Exception as e:
        print(f"RemoteOK error: {e}")
    return new_jobs

# ============================================================
# JOB FEED 3 — WE WORK REMOTELY
# ============================================================

def fetch_weworkremotely(seen):
    new_jobs = []
    try:
        import xml.etree.ElementTree as ET
        url = "https://weworkremotely.com/remote-jobs.rss"
        response = requests.get(url, timeout=15)
        root = ET.fromstring(response.content)
        for item in root.findall(".//item")[:20]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            job_id = f"wwr_{link[-30:]}"
            if job_id not in seen:
                if matches_keywords(title):
                    message = (
                        f"🚨 <b>NEW JOB ALERT</b>\n\n"
                        f"💼 <b>{title}</b>\n"
                        f"🏢 We Work Remotely\n"
                        f"🌍 Remote\n"
                        f"🔗 <a href='{link}'>Apply Now</a>\n\n"
                        f"⚡ via TaskRadar Pro"
                    )
                    new_jobs.append((job_id, message))
    except Exception as e:
        print(f"WWR error: {e}")
    return new_jobs

# ============================================================
# JOB FEED 4 — HIMALAYAS
# ============================================================

def fetch_himalayas(seen):
    new_jobs = []
    try:
        url = "https://himalayas.app/jobs/api?limit=20"
        response = requests.get(url, timeout=15)
        data = response.json()
        jobs = data.get("jobs", [])
        for job in jobs:
            job_id = f"himalayas_{job.get('id', '')}"
            if job_id not in seen:
                title = job.get("title", "")
                company = job.get("companyName", "")
                link = job.get("applicationLink", "")
                if matches_keywords(title):
                    message = (
                        f"🚨 <b>NEW JOB ALERT</b>\n\n"
                        f"💼 <b>{title}</b>\n"
                        f"🏢 {company}\n"
                        f"🌍 Remote\n"
                        f"🔗 <a href='{link}'>Apply Now</a>\n\n"
                        f"⚡ via TaskRadar Pro"
                    )
                    new_jobs.append((job_id, message))
    except Exception as e:
        print(f"Himalayas error: {e}")
    return new_jobs

# ============================================================
# JOB FEED 5 — MYJOBMAG
# ============================================================

def fetch_myjobmag(seen):
    new_jobs = []
    try:
        import xml.etree.ElementTree as ET
        url = "https://www.myjobmag.com/rss/jobs"
        response = requests.get(url, timeout=15)
        root = ET.fromstring(response.content)
        for item in root.findall(".//item")[:20]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            job_id = f"myjobmag_{link[-30:]}"
            if job_id not in seen:
                message = (
                    f"🚨 <b>NEW NIGERIA JOB ALERT</b>\n\n"
                    f"💼 <b>{title}</b>\n"
                    f"🏢 MyJobMag Nigeria\n"
                    f"🇳🇬 Nigeria/Remote\n"
                    f"🔗 <a href='{link}'>Apply Now</a>\n\n"
                    f"⚡ via TaskRadar Pro"
                )
                new_jobs.append((job_id, message))
    except Exception as e:
        print(f"MyJobMag error: {e}")
    return new_jobs

# ============================================================
# MAIN LOOP — RUNS EVERY 30 MINUTES FOREVER
# ============================================================

def run():
    print(f"TaskRadar started at {datetime.now().strftime('%d %b %Y %H:%M')}")
    send_owner_ping()

    while True:
        seen = load_seen_jobs()

        all_fetchers = [
            fetch_remotive,
            fetch_remoteok,
            fetch_weworkremotely,
            fetch_himalayas,
            fetch_myjobmag,
        ]

        for fetcher in all_fetchers:
            new_jobs = fetcher(seen)
            for job_id, message in new_jobs:
                send_telegram_alert(message)
                seen.append(job_id)
                time.sleep(2)

        save_seen_jobs(seen)
        print(f"Cycle completed at {datetime.now().strftime('%d %b %Y %H:%M')}. Sleeping 30 minutes.")
        time.sleep(1800)

if __name__ == "__main__":
    run()
