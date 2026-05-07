import pandas as pd
from datetime import datetime, timedelta
import pytz
import feedparser
import requests
import yt_dlp
import os
from dotenv import load_dotenv
import os
load_dotenv()
# =========================
# CONFIG
# =========================




API_KEY = os.getenv("YOUTUBE_API_KEY")

HOURS_LOOKBACK = 36

MODE = "video"
RESOLUTION = "1080"

utc = pytz.utc
ist = pytz.timezone('Asia/Kolkata')


# =========================
# LOAD CHANNELS
# =========================
def load_normal_channels():
    df = pd.read_csv("subscriptions.csv")
    return df.iloc[:, 0].dropna().tolist()

def load_special_channels():
    df = pd.read_csv("special_channels.csv")
    return df.iloc[:, 0].dropna().tolist()


# =========================
# TIME CONVERSION
# =========================
def convert_to_ist(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc.localize(utc_time)
    ist_time = utc_time.astimezone(ist)
    return ist_time.date(), ist_time.strftime("%H:%M:%S")


# =========================
# RSS FETCH
# =========================
def get_rss_videos(channel_id):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(url)

    videos = []
    cutoff = datetime.utcnow() - timedelta(hours=HOURS_LOOKBACK)

    for entry in feed.entries:
        published = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%S%z")
        published_naive = published.replace(tzinfo=None)

        if published_naive >= cutoff:
            date_ist, time_ist = convert_to_ist(entry.published.replace("+00:00","Z"))

            videos.append({
                "Channel": entry.author,
                "Title": entry.title,
                "Video URL": entry.link,
                "Date (IST)": date_ist,
                "Time (IST)": time_ist,
                "Source": "RSS"
            })

    return videos


# =========================
# API FETCH
# =========================
def get_api_videos(channel_id):
    videos = []
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat("T") + "Z"

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "key": API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "publishedAfter": yesterday,
        "maxResults": 50
    }

    response = requests.get(url, params=params)
    data = response.json()

    for item in data.get("items", []):
        if item["id"]["kind"] == "youtube#video":
            video_id = item["id"]["videoId"]

            date_ist, time_ist = convert_to_ist(item["snippet"]["publishedAt"])

            videos.append({
                "Channel": item["snippet"]["channelTitle"],
                "Title": item["snippet"]["title"],
                "Video URL": f"https://www.youtube.com/watch?v={video_id}",
                "Date (IST)": date_ist,
                "Time (IST)": time_ist,
                "Source": "API"
            })

    return videos


# =========================
# STEP 1: CREATE REPORT
# =========================
def create_report():
    all_videos = []

    print("Fetching RSS...")
    for ch in load_normal_channels():
        try:
            all_videos.extend(get_rss_videos(ch))
        except:
            pass

    print("Fetching API...")
    for ch in load_special_channels():
        try:
            all_videos.extend(get_api_videos(ch))
        except:
            pass

    df = pd.DataFrame(all_videos)
    df = df.sort_values(by=["Date (IST)", "Time (IST)"], ascending=False)

    # REVIEW COLUMNS
    df["Download?"] = ""
    df["Category"] = ""
    df["Priority"] = ""

    file_path = "YouTube_Report.xlsx"
    df.to_excel(file_path, index=False)

    print("Report created")

    # OPEN EXCEL
    os.startfile(file_path)

    return file_path


# =========================
# STEP 2: WAIT FOR USER
# =========================
def wait_for_user():
    input("\n👉 Mark 'Yes' in Download column, SAVE Excel, then press ENTER...")


# =========================
# STEP 3: DOWNLOAD VIDEOS
# =========================
def download_videos(file_path):
    df = pd.read_excel(file_path)

    selected = df[df["Download?"].astype(str).str.lower() == "yes"]
    urls = selected["Video URL"].dropna().tolist()

    print(f"Downloading {len(urls)} videos...")

    # DATE FOLDER
    today = datetime.now().strftime("%Y-%m-%d")
    outtmpl_path = f"downloads/{today}/%(uploader)s/%(title)s.%(ext)s"

    # FORMAT
    if MODE == "audio":
        format_option = "bestaudio[ext=m4a]/bestaudio"
    else:
        format_option = f'bestvideo[height<={RESOLUTION}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'

    ydl_opts = {
        'format': format_option,
        'outtmpl': outtmpl_path,
        'merge_output_format': 'mp4',
        'writesubtitles': False,
        'writeautomaticsub': False,
        'ignoreerrors': True,
        'no_warnings': True,
        'restrictfilenames': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)


# =========================
# MAIN PIPELINE
# =========================
def main():
    file_path = create_report()
    wait_for_user()
    download_videos(file_path)


if __name__ == "__main__":
    main()
