import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json
import os

URL = "https://t.me/s/exploitex"
MAX_POSTS = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_posts():
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    posts = []
    for msg in soup.select(".tgme_widget_message"):
        # text
        text_el = msg.select_one(".tgme_widget_message_text")
        text = text_el.get_text("\n", strip=True) if text_el else ""
        if not text:
            continue

        # date / link
        time_el = msg.select_one(".tgme_widget_message_date time")
        date_str = ""
        if time_el and time_el.get("datetime"):
            try:
                dt = datetime.fromisoformat(time_el["datetime"])
                date_str = dt.astimezone(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
            except ValueError:
                date_str = time_el.get("datetime", "")

        link_el = msg.select_one(".tgme_widget_message_date")
        link = link_el.get("href", URL) if link_el else URL

        posts.append({"text": text, "date": date_str, "link": link})

    # most-recent first, cap at MAX_POSTS
    return list(reversed(posts))[:MAX_POSTS]


def load_existing_posts():
    if not os.path.exists("posts.json"):
        return []
    try:
        with open("posts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_posts_to_json(posts):
    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


def main():
    print("Fetching posts from", URL)
    new_posts = fetch_posts()
    print(f"Got {len(new_posts)} new posts from source")
    
    existing_posts = load_existing_posts()
    existing_links = {post["link"] for post in existing_posts}
    
    unique_new_posts = [post for post in new_posts if post["link"] not in existing_links]
    print(f"Found {len(unique_new_posts)} new unique posts")
    
    if unique_new_posts:
        all_posts = unique_new_posts + existing_posts
        save_posts_to_json(all_posts)
        print(f"Updated posts.json with {len(all_posts)} total posts")
    else:
        print("No new posts to add")


if __name__ == "__main__":
    main()
