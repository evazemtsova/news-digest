import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

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


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def render_post(post: dict) -> str:
    text_html = "<br>".join(escape_html(line) for line in post["text"].splitlines())
    return f"""
    <article class="post">
      <div class="post-meta">{escape_html(post["date"])}</div>
      <div class="post-text">{text_html}</div>
      <a class="post-link" href="{post["link"]}" target="_blank" rel="noopener">
        Open in Telegram →
      </a>
    </article>"""


def generate_html(posts: list) -> str:
    updated = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    posts_html = "\n".join(render_post(p) for p in posts)
    count = len(posts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ExploiteX — News Digest</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #0d1117;
      color: #e6edf3;
      min-height: 100vh;
      padding: 2rem 1rem;
    }}

    header {{
      max-width: 720px;
      margin: 0 auto 2.5rem;
      border-bottom: 1px solid #21262d;
      padding-bottom: 1.25rem;
    }}

    header h1 {{
      font-size: 1.6rem;
      font-weight: 700;
      color: #58a6ff;
      letter-spacing: -0.02em;
    }}

    header p {{
      margin-top: 0.35rem;
      font-size: 0.85rem;
      color: #8b949e;
    }}

    .posts {{
      max-width: 720px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}

    .post {{
      background: #161b22;
      border: 1px solid #21262d;
      border-radius: 10px;
      padding: 1.25rem 1.5rem;
      transition: border-color 0.15s;
    }}

    .post:hover {{
      border-color: #388bfd;
    }}

    .post-meta {{
      font-size: 0.75rem;
      color: #8b949e;
      margin-bottom: 0.65rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .post-text {{
      font-size: 0.95rem;
      line-height: 1.65;
      color: #c9d1d9;
      white-space: pre-wrap;
      word-break: break-word;
    }}

    .post-link {{
      display: inline-block;
      margin-top: 1rem;
      font-size: 0.8rem;
      color: #58a6ff;
      text-decoration: none;
      font-weight: 500;
    }}

    .post-link:hover {{
      text-decoration: underline;
    }}

    footer {{
      max-width: 720px;
      margin: 2.5rem auto 0;
      padding-top: 1.25rem;
      border-top: 1px solid #21262d;
      font-size: 0.78rem;
      color: #6e7681;
      text-align: center;
    }}

    @media (max-width: 480px) {{
      body {{ padding: 1rem 0.75rem; }}
      .post {{ padding: 1rem; }}
      header h1 {{ font-size: 1.3rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>ExploiteX — News Digest</h1>
    <p>Last {count} posts &nbsp;·&nbsp; Updated {updated}</p>
  </header>
  <main class="posts">
{posts_html}
  </main>
  <footer>
    Source: <a href="https://t.me/exploitex" style="color:#58a6ff" target="_blank" rel="noopener">@exploitex</a>
    &nbsp;·&nbsp; auto-updated every 3 hours
  </footer>
</body>
</html>
"""


def main():
    print("Fetching posts from", URL)
    posts = fetch_posts()
    print(f"Got {len(posts)} posts")
    html = generate_html(posts)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html written")


if __name__ == "__main__":
    main()
