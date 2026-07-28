import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from models.item import Item


URL = "https://gamebiz.jp/news/tag/17196"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.9",
}


DATE_FORMATS = [
    "%Y.%m.%d %H:%M",
    "%Y.%m.%d",
    "%Y/%m/%d %H:%M",
    "%Y/%m/%d",
]


def parse_date(text: str):
    if not text:
        return None

    text = text.strip()

    match = re.search(
        r"\d{4}[./-]\d{1,2}[./-]\d{1,2}(?:\s+\d{1,2}:\d{2})?",
        text
    )

    if match:
        text = match.group(0)

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass

    return None


def parse():
    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    items = []

    # gamebiz 标签页文章列表
    articles = soup.select("article")

    for article in articles:
        try:
            # title + url
            title_el = article.select_one("h2 a, h3 a, .title a")

            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            link = title_el.get("href", "").strip()

            if not link:
                continue

            if link.startswith("/"):
                link = "https://gamebiz.jp" + link


            # description
            desc_el = article.select_one(
                ".description, .excerpt, p"
            )

            description = (
                desc_el.get_text(strip=True)
                if desc_el
                else title
            )


            # date
            date_el = article.select_one(
                "time, .date, .entry-date"
            )

            pub_date = (
                parse_date(date_el.get_text(strip=True))
                if date_el
                else None
            )


            # image
            image_url = ""

            img_el = article.select_one("img")

            if img_el:
                image_url = (
                    img_el.get("src")
                    or img_el.get("data-src")
                    or ""
                )


            items.append(
                Item(
                    site="GAMEBIZ",
                    category="interview",
                    title=title,
                    link=link,
                    description=description,
                    image_url=image_url,
                    pub_date=pub_date,
                    tags=[]
                )
            )

        except Exception as e:
            print(f"[GAMEBIZ] Parse error: {e}")


    return items
