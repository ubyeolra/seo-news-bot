import feedparser
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# RSS URL
RSS_FEED = "http://www.molit.go.kr/dev/board/board_rss.jsp?rss_id=NEWS"

# 블로그 ID (Blogger 대시보드에서 확인 가능)
BLOG_ID = '3721610423718385418'

# Blogger API 인증
def get_credentials():
    with open("credentials.json", "r") as f:
        info = json.load(f)
    return Credentials.from_authorized_user_info(info, ['https://www.googleapis.com/auth/blogger'])

# 포스팅 함수
def post_latest_news():
    creds = get_credentials()
    service = build("blogger", "v3", credentials=creds)
    feed = feedparser.parse(RSS_FEED)
    entry = feed.entries[0]

    title = f"[국토부] {entry.title}"
    content = f"""
    <h2>{entry.title}</h2>
    <p>{entry.summary}</p>
    <p><a href="{entry.link}" target="_blank">[원문 보기]</a></p>
    """

    post = {
        "title": title,
        "content": content
    }

    result = service.posts().insert(blogId=BLOG_ID, body=post).execute()
    print("✅ 업로드 완료:", result["url"])

if __name__ == "__main__":
    post_latest_news()
