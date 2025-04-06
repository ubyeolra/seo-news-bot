import feedparser
import json
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 설정
RSS_FEED = "http://www.molit.go.kr/dev/board/board_rss.jsp?rss_id=NEWS"
BLOG_ID = "3721610423718385418"
POSTED_IDS_FILE = "posted_ids.txt"
MAX_POSTS = 5

# 인증 정보 로드
def get_credentials():
    with open("credentials.json", "r") as f:
        info = json.load(f)
    return Credentials.from_authorized_user_info(info, ['https://www.googleapis.com/auth/blogger'])

# 포스팅된 뉴스 ID 불러오기
def load_posted_ids():
    if not os.path.exists(POSTED_IDS_FILE):
        return set()
    with open(POSTED_IDS_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

# 포스팅된 ID 일괄 저장 (최근 1000개 유지)
def save_posted_ids(ids: set):
    with open(POSTED_IDS_FILE, "w") as f:
        for id in list(ids)[-1000:]:
            f.write(id + '\n')

# 메인 포스팅 로직
def post_latest_news():
    credentials = get_credentials()
    service = build("blogger", "v3", credentials=credentials)

    feed = feedparser.parse(RSS_FEED)
    if feed.bozo:
        print(f"❌ RSS 파싱 오류: {feed.bozo_exception}")
        return

    entries = feed.entries
    if not entries:
        print("❌ 피드에 뉴스가 없습니다.")
        return

    posted_ids = load_posted_ids()
    new_posts_count = 0

    for entry in entries:
        if entry.id in posted_ids:
            print(f"🔁 이미 포스팅됨: {entry.title}")
            continue

        today = datetime.now().strftime("%Y-%m-%d")
        title = f"[국토부] {today} - {entry.title}"

        content = f"""
        <h2>{entry.title}</h2>
        <p>{entry.summary}</p>
        <p><a href="{entry.link}" target="_blank">[원문 보기]</a></p>
        """

        post = {
            "title": title,
            "content": content,
            "labels": ["국토부", "정책뉴스"]
        }

        try:
            result = service.posts().insert(blogId=BLOG_ID, body=post).execute()
            print(f"✅ 포스팅 완료: {result['url']}")
            posted_ids.add(entry.id)
            new_posts_count += 1
        except HttpError as e:
            print(f"❌ 포스팅 실패: {e.status_code if hasattr(e, 'status_code') else 'Unknown'} - {e}")

        if new_posts_count >= MAX_POSTS:
            break

    if new_posts_count > 0:
        save_posted_ids(posted_ids)
    else:
        print("🟡 새로운 뉴스가 없습니다. 오늘은 포스팅하지 않습니다.")

# 실행
if __name__ == "__main__":
    try:
        post_latest_news()
    except Exception as e:
        print("❌ 전체 오류 발생:", e)
