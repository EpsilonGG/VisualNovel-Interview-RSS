import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from models.item import Item


URL = "https://dengekionline.com/category/interview/page/1"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


DATE_FORMATS = [
    "%Y-%m-%d %H:%M",
]


def parse_date(text: str) -> datetime | None:

    if not text:
        return None

    text = text.strip()

    for fmt in DATE_FORMATS:

        try:

            dt = datetime.strptime(
                text,
                fmt
            )

            return dt.replace(
                tzinfo=timezone.utc
            )

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

    soup = BeautifulSoup(
        response.text,
        "lxml"
    )

    articles = soup.select(
        "li[class*='ArticleList_listItem']"
    )

    items = []

    for article in articles:

        try:

            title_el = article.select_one(
                "[class*='ArticleCard_title']"
            )

            if not title_el:
                continue

            desc_el = article.select_one(
                "[class*='ArticleCard_description']"
            )

            link_el = article.select_one(
                "a[class*='ArticleCard_card']"
            )

            date_el = article.select_one(
                "[class*='ArticleCard_time']"
            )

            img_el = article.select_one(
                "img"
            )

            title = title_el.get_text(
                strip=True
            )

            link = ""

            if link_el:

                link = urljoin(
                    "https://dengekionline.com",
                    link_el.get("href", "")
                )

            description = ""

            if desc_el:

                description = desc_el.get_text(
                    " ",
                    strip=True
                )

            if not description:
                description = title

            pub_date = None

            if date_el:

                raw_date = date_el.get_text(
                    " ",
                    strip=True
                )

                pub_date = parse_date(
                    raw_date
                )

                if pub_date is None:

                    print(
                        "[Dengeki Online] Date parse failed:",
                        repr(raw_date)
                    )

            image_url = ""

            if img_el:

                image_url = (
                    img_el.get("src")
                    or img_el.get("data-src")
                    or img_el.get("data-lazy-src")
                    or ""
                )

                image_url = urljoin(
                    "https://dengekionline.com",
                    image_url
                )

            items.append(
                Item(
                    site="Dengeki Online",
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

            print(
                f"[Dengeki Online] Parse error: {e}"
            )

    return items
